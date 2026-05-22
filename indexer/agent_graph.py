from __future__ import annotations

from indexer.retrieval import (
    _extract_graphql_operations,
    _extract_http_paths,
    _limit_list,
    _looks_like_client_symbol,
    _repo_nodes_for_graph,
)

def cross_repo_graph(repos: dict[str, dict], max_results: int = 200) -> dict:
    max_results = max(1, min(max_results, 1000))
    repo_nodes = {name: _repo_nodes_for_graph(info) for name, info in repos.items()}
    edges = []
    for from_repo, nodes in repo_nodes.items():
        for node in nodes:
            paths = _extract_http_paths(node.get("document", "")) if _looks_like_client_symbol(node) else []
            operations = _extract_graphql_operations(node.get("document", ""))
            for to_repo, targets in repo_nodes.items():
                if from_repo == to_repo:
                    continue
                for target in targets:
                    hay = " ".join([target.get("id", ""), target.get("document", "")]).lower()
                    for path in paths:
                        if path.lower() in hay:
                            edges.append({
                                "from_repo": from_repo,
                                "from": node.get("id"),
                                "to_repo": to_repo,
                                "to": target.get("id"),
                                "kind": "http_path",
                                "path": path,
                            })
                    for op in operations:
                        if op.lower() in hay:
                            edges.append({
                                "from_repo": from_repo,
                                "from": node.get("id"),
                                "to_repo": to_repo,
                                "to": target.get("id"),
                                "kind": "graphql_operation",
                                "operation": op,
                            })
    return {"edges": _limit_list(edges, max_results), "total": len(edges)}

__all__ = ['cross_repo_graph']
