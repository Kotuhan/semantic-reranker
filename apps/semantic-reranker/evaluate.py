"""Evaluation script for the semantic re-ranker.

Compares re-ranked results against ideal rankings using NDCG@10 and Precision@5.
Also shows keyword baseline for comparison.
"""

import sys

from rich.console import Console
from rich.table import Table

sys.path.insert(0, "src")

from reranker import Reranker
from reranker.metrics import compute_ndcg, compute_precision
from reranker.utils import load_ideal_rankings, load_keyword_results, load_reports


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
