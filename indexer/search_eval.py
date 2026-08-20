from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class SearchCase:
    query: str
    relevant_ids: tuple[str, ...]


def evaluate_search(
    search_fn: Callable[[str, int], list[dict]],
    cases: list[SearchCase],
) -> dict[str, float]:
    if not cases:
        return {"recall_at_5": 0.0, "mrr_at_10": 0.0, "ndcg_at_10": 0.0}
    recalls = []
    reciprocal_ranks = []
    ndcgs = []
    for case in cases:
        results = search_fn(case.query, 10)
        ids = [str(result.get("id", "")) for result in results]
        relevant = set(case.relevant_ids)
        recalls.append(len(relevant & set(ids[:5])) / max(1, len(relevant)))
        first_rank = next((rank for rank, component_id in enumerate(ids[:10], 1) if component_id in relevant), None)
        reciprocal_ranks.append(1.0 / first_rank if first_rank else 0.0)
        dcg = sum(1.0 / math.log2(rank + 1) for rank, component_id in enumerate(ids[:10], 1) if component_id in relevant)
        ideal_hits = min(len(relevant), 10)
        ideal = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
        ndcgs.append(dcg / ideal if ideal else 0.0)
    return {
        "recall_at_5": round(sum(recalls) / len(recalls), 6),
        "mrr_at_10": round(sum(reciprocal_ranks) / len(reciprocal_ranks), 6),
        "ndcg_at_10": round(sum(ndcgs) / len(ndcgs), 6),
    }


__all__ = ["SearchCase", "evaluate_search"]
