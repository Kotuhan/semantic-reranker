"""Evaluation metrics for the semantic re-ranker."""

import math

from .models import IdealRanking


def compute_ndcg(
    ranked_ids: list[str],
    ideal_ranking: list[IdealRanking],
    k: int = 10,
) -> float:
    """Compute NDCG@k with graded relevance.

    Relevance scores: ideal rank 1 = 10, rank 2 = 9, ..., rank 10 = 1, absent = 0.
    """
    # Build relevance map from ideal rankings
    relevance_map: dict[str, int] = {}
    for entry in ideal_ranking:
        relevance_map[entry.report_id] = 11 - entry.rank  # rank 1 -> 10, rank 10 -> 1

    # DCG@k
    dcg = 0.0
    for i, report_id in enumerate(ranked_ids[:k], start=1):
        rel = relevance_map.get(report_id, 0)
        dcg += rel / math.log2(i + 1)

    # IDCG@k — perfect ranking of available relevance scores
    ideal_scores = sorted(relevance_map.values(), reverse=True)[:k]
    idcg = sum(rel / math.log2(i + 1) for i, rel in enumerate(ideal_scores, start=1))

    if idcg == 0:
        return 0.0

    return dcg / idcg


def compute_precision(
    ranked_ids: list[str],
    ideal_ids: set[str],
    k: int = 5,
) -> float:
    """Compute Precision@k.

    Fraction of top-k results that appear in the ideal top-10.
    """
    if k == 0:
        return 0.0
    hits = sum(1 for rid in ranked_ids[:k] if rid in ideal_ids)
    return hits / k
