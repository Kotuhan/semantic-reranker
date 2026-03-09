"""Benchmark script for comparing re-ranking approaches.

Runs multiple experiments varying text composition, models, subcategory scoring,
and hybrid scoring. Outputs a comparison table with NDCG@10, Precision@5, and
delta vs baseline.

Usage:
    python benchmark.py
"""

import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional

from rich.console import Console
from rich.table import Table
from sentence_transformers import CrossEncoder

sys.path.insert(0, "src")

from reranker.metrics import compute_ndcg, compute_precision
from reranker.models import KeywordResult, Report
from reranker.utils import load_ideal_rankings, load_keyword_results, load_reports

# ---------------------------------------------------------------------------
# Text composition functions: (Report) -> str
# ---------------------------------------------------------------------------


def text_title_only(report: Report) -> str:
    """Title only."""
    return report.title


def text_title_desc(report: Report) -> str:
    """Title + description."""
    return f"{report.title}. {report.description}"


def text_title_desc_loc(report: Report) -> str:
    """Title + description + location (current baseline)."""
    return f"{report.title}. {report.description} Location: {report.country}, {report.city}."


def text_title_desc_loc_subcats(report: Report) -> str:
    """Title + description + location + all subcategories flattened."""
    base = text_title_desc_loc(report)
    all_values: list[str] = []
    for values in report.subcategories.values():
        all_values.extend(values)
    if all_values:
        base += " Categories: " + ", ".join(all_values) + "."
    return base


def text_title_desc_loc_weighted_subcats(report: Report) -> str:
    """Title + description + location + high-value subcategories repeated for emphasis."""
    base = text_title_desc_loc(report)
    high_value_keys = ["Attack", "Explosive", "Target"]
    enrichment: list[str] = []
    for key in high_value_keys:
        if key in report.subcategories:
            # Repeat each value twice for emphasis
            enrichment.extend(report.subcategories[key] * 2)
    if enrichment:
        base += " " + " ".join(enrichment)
    return base


# Type aliases
TextComposer = Callable[[Report], str]


# ---------------------------------------------------------------------------
# Score modifier functions
# ---------------------------------------------------------------------------


def count_category_matches(report: Report, query: str) -> int:
    """Count subcategory values that overlap with query terms."""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    count = 0
    for values in report.subcategories.values():
        for val in values:
            val_lower = val.lower()
            # Check if any query word appears in the subcategory value or vice versa
            val_words = set(val_lower.replace("-", " ").split())
            if query_words & val_words or val_lower in query_lower or query_lower in val_lower:
                count += 1
    return count


def normalize_scores(scores: list[float]) -> list[float]:
    """Min-max normalize scores to [0, 1] range."""
    if not scores:
        return []
    min_s = min(scores)
    max_s = max(scores)
    if max_s == min_s:
        return [0.5] * len(scores)
    return [(s - min_s) / (max_s - min_s) for s in scores]


# ---------------------------------------------------------------------------
# Experiment definition
# ---------------------------------------------------------------------------


@dataclass
class Experiment:
    """A single benchmark experiment configuration."""

    name: str
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    text_fn: TextComposer = text_title_desc_loc
    category_bonus_beta: Optional[float] = None  # None = no category bonus
    hybrid_alpha: Optional[float] = None  # None = no hybrid scoring
    group: str = ""  # For table grouping


@dataclass
class ExperimentResult:
    """Results from running an experiment."""

    name: str
    group: str
    avg_ndcg: float
    avg_precision: float
    elapsed_seconds: float
    per_query_ndcg: list[float] = field(default_factory=list)
    per_query_precision: list[float] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Model cache
# ---------------------------------------------------------------------------

_model_cache: dict[str, CrossEncoder] = {}


def get_model(name: str, console: Console) -> CrossEncoder:
    """Load a cross-encoder model, caching for reuse."""
    if name not in _model_cache:
        console.print(f"  Loading model: {name}...")
        _model_cache[name] = CrossEncoder(name)
        console.print(f"  [green]Model loaded.[/green]")
    return _model_cache[name]


# ---------------------------------------------------------------------------
# Run a single experiment
# ---------------------------------------------------------------------------


def run_experiment(
    experiment: Experiment,
    reports: dict[str, Report],
    queries: list,  # list[QueryResults]
    ideal_rankings: list,  # list[QueryIdealRanking]
    console: Console,
) -> ExperimentResult:
    """Run a single experiment across all queries and compute metrics."""
    model = get_model(experiment.model_name, console)

    ndcg_scores: list[float] = []
    precision_scores: list[float] = []

    start = time.perf_counter()

    for query_data, ideal_data in zip(queries, ideal_rankings):
        candidates = [r.report_id for r in query_data.results]
        keyword_scores_raw = [r.keyword_score for r in query_data.results]
        ideal_ids = {entry.report_id for entry in ideal_data.top_10}

        # Build pairs using the experiment's text composer
        pairs: list[tuple[str, str]] = []
        valid_candidates: list[tuple[str, int, float]] = []  # (id, rank, kw_score)

        for rank, result in enumerate(query_data.results, start=1):
            report = reports.get(result.report_id)
            if report is None:
                continue
            text = experiment.text_fn(report)
            pairs.append((query_data.query, text))
            valid_candidates.append((result.report_id, rank, result.keyword_score))

        if not pairs:
            continue

        # Score all pairs
        raw_scores = model.predict(pairs)
        semantic_scores = [float(s) for s in raw_scores]

        # Apply score modifiers
        final_scores: list[float] = []

        if experiment.hybrid_alpha is not None:
            # Hybrid: alpha * semantic + (1-alpha) * keyword
            norm_semantic = normalize_scores(semantic_scores)
            kw_scores = [vc[2] for vc in valid_candidates]
            norm_keyword = normalize_scores(kw_scores)
            alpha = experiment.hybrid_alpha
            for ns, nk in zip(norm_semantic, norm_keyword):
                final_scores.append(alpha * ns + (1 - alpha) * nk)
        elif experiment.category_bonus_beta is not None:
            # Category match bonus
            beta = experiment.category_bonus_beta
            for i, (report_id, _rank, _kw) in enumerate(valid_candidates):
                report = reports[report_id]
                matches = count_category_matches(report, query_data.query)
                final_scores.append(semantic_scores[i] + beta * matches)
        else:
            final_scores = semantic_scores

        # Sort by final score descending
        scored = sorted(
            zip([vc[0] for vc in valid_candidates], final_scores),
            key=lambda x: x[1],
            reverse=True,
        )
        reranked_ids = [s[0] for s in scored[:10]]

        # Compute metrics
        ndcg = compute_ndcg(reranked_ids, ideal_data.top_10)
        precision = compute_precision(reranked_ids, ideal_ids)
        ndcg_scores.append(ndcg)
        precision_scores.append(precision)

    elapsed = time.perf_counter() - start

    avg_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0
    avg_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0

    return ExperimentResult(
        name=experiment.name,
        group=experiment.group,
        avg_ndcg=avg_ndcg,
        avg_precision=avg_precision,
        elapsed_seconds=elapsed,
        per_query_ndcg=ndcg_scores,
        per_query_precision=precision_scores,
    )


# ---------------------------------------------------------------------------
# Experiment definitions
# ---------------------------------------------------------------------------

EXPERIMENTS: list[Experiment] = [
    # --- Text composition variants (baseline model) ---
    Experiment(
        name="title only",
        text_fn=text_title_only,
        group="Text Composition",
    ),
    Experiment(
        name="title + desc",
        text_fn=text_title_desc,
        group="Text Composition",
    ),
    Experiment(
        name="title + desc + loc [BASELINE]",
        text_fn=text_title_desc_loc,
        group="Text Composition",
    ),
    Experiment(
        name="title + desc + loc + subcats",
        text_fn=text_title_desc_loc_subcats,
        group="Text Composition",
    ),
    # --- Subcategory scoring approaches (baseline model + text) ---
    Experiment(
        name="category bonus beta=0.5",
        category_bonus_beta=0.5,
        group="Subcategory Scoring",
    ),
    Experiment(
        name="category bonus beta=1.0",
        category_bonus_beta=1.0,
        group="Subcategory Scoring",
    ),
    Experiment(
        name="category bonus beta=2.0",
        category_bonus_beta=2.0,
        group="Subcategory Scoring",
    ),
    Experiment(
        name="weighted subcat enrichment",
        text_fn=text_title_desc_loc_weighted_subcats,
        group="Subcategory Scoring",
    ),
    # --- Alternative models (baseline text) ---
    Experiment(
        name="MiniLM-L-12-v2",
        model_name="cross-encoder/ms-marco-MiniLM-L-12-v2",
        group="Models",
    ),
    Experiment(
        name="bge-reranker-base",
        model_name="BAAI/bge-reranker-base",
        group="Models",
    ),
    # --- Best combinations (cross-category) ---
    Experiment(
        name="bge-reranker-base + subcats",
        model_name="BAAI/bge-reranker-base",
        text_fn=text_title_desc_loc_subcats,
        group="Best Combinations",
    ),
    Experiment(
        name="MiniLM-L-12 + subcats",
        model_name="cross-encoder/ms-marco-MiniLM-L-12-v2",
        text_fn=text_title_desc_loc_subcats,
        group="Best Combinations",
    ),
    # --- Hybrid scoring (baseline model + text) ---
    Experiment(
        name="hybrid alpha=0.7",
        hybrid_alpha=0.7,
        group="Hybrid Scoring",
    ),
    Experiment(
        name="hybrid alpha=0.8",
        hybrid_alpha=0.8,
        group="Hybrid Scoring",
    ),
    Experiment(
        name="hybrid alpha=0.9",
        hybrid_alpha=0.9,
        group="Hybrid Scoring",
    ),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    console = Console()

    console.print("\n[bold]Re-Ranker Benchmark: Comparing Approaches[/bold]\n")

    # Load data
    try:
        reports = load_reports()
        queries = load_keyword_results()
        ideal_rankings = load_ideal_rankings()
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    console.print(f"Loaded {len(reports)} reports, {len(queries)} queries.\n")

    # Find baseline index
    baseline_idx: Optional[int] = None
    for i, exp in enumerate(EXPERIMENTS):
        if "BASELINE" in exp.name:
            baseline_idx = i
            break

    # Run all experiments
    results: list[ExperimentResult] = []
    for i, experiment in enumerate(EXPERIMENTS):
        console.print(f"[{i + 1}/{len(EXPERIMENTS)}] Running: {experiment.name}")
        result = run_experiment(experiment, reports, queries, ideal_rankings, console)
        results.append(result)
        console.print(
            f"  NDCG@10={result.avg_ndcg:.4f}  P@5={result.avg_precision:.4f}  "
            f"({result.elapsed_seconds:.2f}s)\n"
        )

    # Get baseline values
    baseline_ndcg = results[baseline_idx].avg_ndcg if baseline_idx is not None else 0.0
    baseline_precision = results[baseline_idx].avg_precision if baseline_idx is not None else 0.0

    # Find best result
    best_idx = max(range(len(results)), key=lambda i: results[i].avg_ndcg)

    # Build comparison table
    table = Table(title="\nBenchmark Results: All Experiments vs Baseline")
    table.add_column("#", justify="right", width=3)
    table.add_column("Experiment", width=35)
    table.add_column("NDCG@10", justify="right", width=10)
    table.add_column("P@5", justify="right", width=10)
    table.add_column("dNDCG", justify="right", width=10)
    table.add_column("dP@5", justify="right", width=10)
    table.add_column("Time", justify="right", width=8)

    current_group = ""
    for i, result in enumerate(results):
        # Add section separator for new groups
        if result.group != current_group:
            if current_group:
                table.add_section()
            current_group = result.group

        delta_ndcg = result.avg_ndcg - baseline_ndcg
        delta_precision = result.avg_precision - baseline_precision

        # Color coding
        if i == best_idx:
            name_str = f"[bold green]{result.name}[/bold green]"
            ndcg_str = f"[bold green]{result.avg_ndcg:.4f}[/bold green]"
            p5_str = f"[bold green]{result.avg_precision:.4f}[/bold green]"
        elif "BASELINE" in result.name:
            name_str = f"[bold]{result.name}[/bold]"
            ndcg_str = f"[bold]{result.avg_ndcg:.4f}[/bold]"
            p5_str = f"[bold]{result.avg_precision:.4f}[/bold]"
        else:
            name_str = result.name
            ndcg_str = f"{result.avg_ndcg:.4f}"
            p5_str = f"{result.avg_precision:.4f}"

        # Delta coloring
        delta_ndcg_style = "green" if delta_ndcg > 0.001 else ("red" if delta_ndcg < -0.001 else "dim")
        delta_p5_style = "green" if delta_precision > 0.001 else ("red" if delta_precision < -0.001 else "dim")

        delta_ndcg_str = f"[{delta_ndcg_style}]{delta_ndcg:+.4f}[/{delta_ndcg_style}]"
        delta_p5_str = f"[{delta_p5_style}]{delta_precision:+.4f}[/{delta_p5_style}]"

        table.add_row(
            str(i + 1),
            name_str,
            ndcg_str,
            p5_str,
            delta_ndcg_str,
            delta_p5_str,
            f"{result.elapsed_seconds:.2f}s",
        )

    console.print(table)

    # Summary
    best = results[best_idx]
    console.print(f"\n[bold green]Best configuration: {best.name}[/bold green]")
    console.print(f"  NDCG@10: {best.avg_ndcg:.4f} (delta vs baseline: {best.avg_ndcg - baseline_ndcg:+.4f})")
    console.print(f"  P@5:     {best.avg_precision:.4f} (delta vs baseline: {best.avg_precision - baseline_precision:+.4f})")
    console.print()

    # Save results to JSON
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "baseline": results[baseline_idx].name if baseline_idx is not None else None,
        "best": best.name,
        "experiments": [
            {
                "name": r.name,
                "group": r.group,
                "ndcg10": round(r.avg_ndcg, 4),
                "precision5": round(r.avg_precision, 4),
                "delta_ndcg": round(r.avg_ndcg - baseline_ndcg, 4),
                "delta_precision": round(r.avg_precision - baseline_precision, 4),
                "elapsed_seconds": round(r.elapsed_seconds, 2),
                "per_query_ndcg": [round(v, 4) for v in r.per_query_ndcg],
                "per_query_precision": [round(v, 4) for v in r.per_query_precision],
            }
            for r in results
        ],
        "queries": [q.query for q in queries],
    }
    out_path = "benchmark_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    console.print(f"Results saved to [bold]{out_path}[/bold]")


if __name__ == "__main__":
    main()
