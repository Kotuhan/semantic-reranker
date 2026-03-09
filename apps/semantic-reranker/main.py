"""Demo entry point for the semantic re-ranker.

Loads data, runs re-ranking on all queries, and displays results
using rich-formatted console tables.
"""

import sys
import time

from rich.console import Console
from rich.table import Table

sys.path.insert(0, "src")

from reranker import Reranker
from reranker.utils import load_keyword_results, load_reports


def main() -> None:
    console = Console()

    console.print("\n[bold]Semantic Re-Ranker Demo[/bold]")
    console.print("Model: cross-encoder/ms-marco-MiniLM-L-6-v2\n")

    # Load data
    try:
        reports = load_reports()
        queries = load_keyword_results()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(f"Loaded {len(reports)} reports, {len(queries)} queries\n")

    # Initialize re-ranker
    console.print("Loading model...")
    try:
        reranker = Reranker()
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print("[green]Model loaded.[/green]\n")

    # Process each query
    for i, query in enumerate(queries, 1):
        candidates = [r.report_id for r in query.results]

        start = time.time()
        results = reranker.rerank(query.query, candidates, reports)
        elapsed = time.time() - start

        table = Table(
            title=f"Query {i}: {query.query}",
            caption=f"Re-ranked in {elapsed:.2f}s",
        )
        table.add_column("Rank", style="bold", width=5)
        table.add_column("Report ID", width=10)
        table.add_column("Title", width=55)
        table.add_column("Score", justify="right", width=8)
        table.add_column("Was", justify="right", width=5)

        for rank, result in enumerate(results, 1):
            report = reports[result.report_id]
            table.add_row(
                str(rank),
                result.report_id,
                report.title[:55],
                f"{result.score:.4f}",
                f"#{result.original_rank}",
            )

        console.print(table)
        console.print()


if __name__ == "__main__":
    main()
