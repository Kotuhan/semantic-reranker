"""Data loading utilities for the semantic re-ranker."""

import json
from pathlib import Path

from .models import QueryIdealRanking, QueryResults, Report


def load_reports(path: str | Path = "data/reports.json") -> dict[str, Report]:
    """Load reports.json and return a dict keyed by report ID."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Reports file not found: {path}")

    with open(path) as f:
        data = json.load(f)

    return {r["id"]: Report(**r) for r in data}


def load_keyword_results(
    path: str | Path = "data/keyword_results.json",
) -> list[QueryResults]:
    """Load keyword_results.json and return list of QueryResults."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Keyword results file not found: {path}")

    with open(path) as f:
        data = json.load(f)

    return [QueryResults(**q) for q in data["queries"]]


def load_ideal_rankings(
    path: str | Path = "data/ideal_rankings.json",
) -> list[QueryIdealRanking]:
    """Load ideal_rankings.json and return list of QueryIdealRanking."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Ideal rankings file not found: {path}")

    with open(path) as f:
        data = json.load(f)

    return [QueryIdealRanking(**q) for q in data["ideal_rankings"]]


def get_report_text(report: Report) -> str:
    """Build document text for cross-encoder scoring.

    Combines title, description, and location for semantic matching.
    Country/city included to support geo-queries (e.g., "Middle East").
    """
    return f"{report.title}. {report.description} Location: {report.country}, {report.city}."
