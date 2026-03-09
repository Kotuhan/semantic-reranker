"""Evaluation script for the semantic re-ranker.

Compares re-ranked results against ideal rankings using NDCG@10 and Precision@5.
Also shows keyword baseline for comparison.
"""

import math
import sys

from rich.console import Console
from rich.table import Table

sys.path.insert(0, "src")

from reranker import Reranker
from reranker.models import IdealRanking
from reranker.utils import load_ideal_rankings, load_keyword_results, load_reports


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


def main() -> None:
    console = Console()

    console.print("\n[bold]Semantic Re-Ranker Evaluation[/bold]")
    console.print("Model: cross-encoder/ms-marco-MiniLM-L-6-v2\n")

    # Load data
    try:
        reports = load_reports()
        queries = load_keyword_results()
        ideal_rankings = load_ideal_rankings()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    # Initialize re-ranker
    console.print("Loading model...")
    try:
        reranker = Reranker()
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print("[green]Model loaded.[/green]\n")

    # Build results table
    table = Table(title="Re-Ranker Evaluation Results")
    table.add_column("Query", width=45)
    table.add_column("NDCG@10\n(semantic)", justify="right", width=12)
    table.add_column("NDCG@10\n(keyword)", justify="right", width=12)
    table.add_column("Precision@5", justify="right", width=12)

    ndcg_scores: list[float] = []
    ndcg_baseline_scores: list[float] = []
    precision_scores: list[float] = []

    for query_data, ideal_data in zip(queries, ideal_rankings):
        candidates = [r.report_id for r in query_data.results]
        ideal_ids = {entry.report_id for entry in ideal_data.top_10}

        # Semantic re-ranking
        results = reranker.rerank(query_data.query, candidates, reports)
        reranked_ids = [r.report_id for r in results]

        # Keyword baseline (original order, take top 10)
        keyword_ids = candidates[:10]

        # Compute metrics
        ndcg = compute_ndcg(reranked_ids, ideal_data.top_10)
        ndcg_baseline = compute_ndcg(keyword_ids, ideal_data.top_10)
        precision = compute_precision(reranked_ids, ideal_ids)

        ndcg_scores.append(ndcg)
        ndcg_baseline_scores.append(ndcg_baseline)
        precision_scores.append(precision)

        # Color NDCG based on improvement
        ndcg_style = "green" if ndcg > ndcg_baseline else "red"

        table.add_row(
            query_data.query[:45],
            f"[{ndcg_style}]{ndcg:.4f}[/{ndcg_style}]",
            f"{ndcg_baseline:.4f}",
            f"{precision:.4f}",
        )

    # Average row
    avg_ndcg = sum(ndcg_scores) / len(ndcg_scores)
    avg_baseline = sum(ndcg_baseline_scores) / len(ndcg_baseline_scores)
    avg_precision = sum(precision_scores) / len(precision_scores)

    table.add_section()
    table.add_row(
        "[bold]Average[/bold]",
        f"[bold green]{avg_ndcg:.4f}[/bold green]",
        f"[bold]{avg_baseline:.4f}[/bold]",
        f"[bold]{avg_precision:.4f}[/bold]",
    )

    console.print(table)

    # Summary
    improvement = avg_ndcg - avg_baseline
    console.print(f"\nNDCG@10 improvement over keyword baseline: [bold green]+{improvement:.4f}[/bold green]")
    console.print()


if __name__ == "__main__":
    main()
