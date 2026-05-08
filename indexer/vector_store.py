from __future__ import annotations
import json
import logging
import threading
from pathlib import Path
from indexer.config import VectorStoreConfig

logger = logging.getLogger(__name__)

_client_cache: dict[str, object] = {}
_client_lock = threading.Lock()


def _get_client(persist_dir: str):
    with _client_lock:
        if persist_dir not in _client_cache:
            import chromadb
            _client_cache[persist_dir] = chromadb.PersistentClient(path=persist_dir)
        return _client_cache[persist_dir]


def evict_client(persist_dir: str):
    with _client_lock:
        _client_cache.pop(persist_dir, None)


def _get_or_create_collection(client, name: str, dim: int | None = 1024):
    import chromadb
    if dim is not None:
        collection = client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine", "hnsw:M": 16, "hnsw:construction_ef": 100, "dim": dim},
        )
        existing_dim = collection.metadata.get("dim") if collection.metadata else None
        if existing_dim and existing_dim != dim:
            raise ValueError(
                f"Collection '{name}' exists with dim={existing_dim}, but config requests dim={dim}. "
                f"Delete the collection or update embedding.dimensions."
            )
    else:
        try:
            collection = client.get_collection(name=name)
        except Exception as e:
            logger.warning("Collection '%s' not found, creating with default dim: %s", name, e)
            collection = client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine", "hnsw:M": 16, "hnsw:construction_ef": 100, "dim": 1024},
            )
    return collection


def upsert_nodes(
    nodes: list,
    vectors: dict[str, list[float]],
    descriptions: dict[str, str],
    cfg: VectorStoreConfig,
    repo_root: Path,
    dim: int = 1024,
    branch: str = "",
):
    persist_path = str(repo_root / cfg.persist_dir)
    client = _get_client(persist_path)
    collection = _get_or_create_collection(client, cfg.collection_name, dim=dim)

    files_in_batch = list({n.file for n in nodes})
    old_ids = set()

    chunk_size = 20
    for ci in range(0, len(files_in_batch), chunk_size):
        chunk = files_in_batch[ci:ci + chunk_size]
        try:
            if branch:
                where = {"$or": [{"$and": [{"file": f}, {"branch": branch}]} for f in chunk]} if len(chunk) > 1 else {"$and": [{"file": chunk[0]}, {"branch": branch}]}
            else:
                where = {"$or": [{"file": f} for f in chunk]} if len(chunk) > 1 else {"file": chunk[0]}
            all_existing = collection.get(where=where)
            if all_existing and all_existing["ids"]:
                old_ids.update(all_existing["ids"])
        except Exception as e:
            logger.debug("Batch query failed for %d files, falling back: %s", len(chunk), e)
            for f in chunk:
                try:
                    existing_for_file = collection.get(
                        where={"$and": [{"file": f}, {"branch": branch}]},
                    )
                    if existing_for_file and existing_for_file["ids"]:
                        old_ids.update(existing_for_file["ids"])
                except Exception as e2:
                    logger.debug("Failed to query existing vectors for %s: %s", f, e2)

    valid = [(n, vectors[n.id]) for n in nodes if n.id in vectors and vectors[n.id] is not None]
    if not valid:
        return 0

    ids = [n.id for n, _ in valid]
    embeddings = [vec for _, vec in valid]
    documents = [_build_doc(n, descriptions) for n, _ in valid]
    metadatas = [_build_meta(n, branch) for n, _ in valid]

    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
            documents=documents[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
        )

    all_new_ids = {n.id for n, _ in valid}
    stale_ids = old_ids - all_new_ids
    if stale_ids:
        collection.delete(ids=list(stale_ids))

    return len(ids)


def search(
    query_vector: list[float],
    cfg: VectorStoreConfig,
    repo_root: Path,
    top_k: int = 10,
    where: dict | None = None,
) -> list[dict]:
    persist_path = str(repo_root / cfg.persist_dir)
    client = _get_client(persist_path)
    collection = _get_or_create_collection(client, cfg.collection_name, dim=None)

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    if results and results["ids"] and results["ids"][0]:
        for i, id_ in enumerate(results["ids"][0]):
            hits.append({
                "id": id_,
                "document": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0.0,
            })
    return hits


def get_by_ids(
    ids: list[str],
    cfg: VectorStoreConfig,
    repo_root: Path,
) -> list[dict]:
    persist_path = str(repo_root / cfg.persist_dir)
    client = _get_client(persist_path)
    collection = _get_or_create_collection(client, cfg.collection_name, dim=None)

    results = collection.get(
        ids=ids,
        include=["documents", "metadatas"],
    )

    hits = []
    if results and results["ids"]:
        for i, id_ in enumerate(results["ids"]):
            hits.append({
                "id": id_,
                "document": results["documents"][i] if results["documents"] else "",
                "metadata": results["metadatas"][i] if results["metadatas"] else {},
            })
    return hits


def delete_by_files(
    removed_files: list[str],
    cfg: VectorStoreConfig,
    repo_root: Path,
    branch: str = "",
) -> int:
    persist_path = str(repo_root / cfg.persist_dir)
    if not Path(persist_path).exists():
        return 0
    client = _get_client(persist_path)
    collection = _get_or_create_collection(client, cfg.collection_name, dim=None)

    ids_to_delete = []
    for file_path in removed_files:
        where_clause = {"file": file_path}
        if branch:
            where_clause = {"$and": [{"file": file_path}, {"branch": branch}]}
        results = collection.get(
            where=where_clause,
        )
        if results and results["ids"]:
            ids_to_delete.extend(results["ids"])

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
    return len(ids_to_delete)


def _build_doc(node, descriptions: dict[str, str]) -> str:
    desc = descriptions.get(node.id, "")
    parts = [f"[{node.type}] {node.id}"]
    if desc:
        parts.append(desc)
    if node.docstring:
        parts.append(node.docstring)
    return " | ".join(parts)


def _truncate_list(obj: list, max_json_len: int = 4000) -> str:
    s = json_dumps_compact(obj)
    if len(s) <= max_json_len:
        return s
    while len(obj) > 1:
        obj = obj[:len(obj) // 2]
        s = json_dumps_compact(obj)
        if len(s) <= max_json_len:
            return s
    s = json_dumps_compact(obj[:1])
    if len(s) > max_json_len:
        logger.warning("Metadata field truncated: single element exceeds max_json_len=%d", max_json_len)
        return "[]"
    return s


def _build_meta(node, branch: str = "") -> dict:
    meta: dict = {
        "type": node.type,
        "file": node.file,
        "line_start": node.line_start,
        "line_end": node.line_end,
    }
    meta["branch"] = branch
    if node.calls:
        meta["calls"] = _truncate_list(node.calls)
    if node.called_by:
        meta["called_by"] = _truncate_list(node.called_by)
    if node.imports:
        meta["imports"] = _truncate_list(node.imports)
    return meta


def json_dumps_compact(obj) -> str:
    return json.dumps(obj, separators=(",", ":"))
