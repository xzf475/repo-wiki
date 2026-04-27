from __future__ import annotations
from pathlib import Path
from indexer.config import VectorStoreConfig


def _get_client(persist_dir: str):
    import chromadb
    return chromadb.PersistentClient(path=persist_dir)


def _get_or_create_collection(client, name: str, dim: int = 1024):
    import chromadb
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine", "hnsw:M": 16, "hnsw:construction_ef": 100},
    )


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

    if branch:
        existing = collection.get(where={"branch": branch}, include=["ids"])
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])

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
    collection = _get_or_create_collection(client, cfg.collection_name)

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
    collection = _get_or_create_collection(client, cfg.collection_name)

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
    collection = _get_or_create_collection(client, cfg.collection_name)

    ids_to_delete = []
    for file_path in removed_files:
        where_clause = {"file": file_path}
        if branch:
            where_clause = {"$and": [{"file": file_path}, {"branch": branch}]}
        results = collection.get(
            where=where_clause,
            include=["ids"],
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


def _build_meta(node, branch: str = "") -> dict:
    meta: dict = {
        "type": node.type,
        "file": node.file,
        "line_start": node.line_start,
        "line_end": node.line_end,
    }
    if branch:
        meta["branch"] = branch
    if node.calls:
        meta["calls"] = json_dumps_compact(node.calls)
    if node.called_by:
        meta["called_by"] = json_dumps_compact(node.called_by)
    if node.imports:
        meta["imports"] = json_dumps_compact(node.imports)
    return meta


def json_dumps_compact(obj) -> str:
    import json
    return json.dumps(obj, separators=(",", ":"))
