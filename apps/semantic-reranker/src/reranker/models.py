"""Pydantic data models for the semantic re-ranker."""

from pydantic import BaseModel


class Report(BaseModel):
    """Intelligence report from reports.json."""

    id: str
    title: str
    description: str
    type: str
    country: str
    city: str
    event_date: str
    subcategories: dict[str, list[str]]


class KeywordResult(BaseModel):
    """Single keyword search result."""

    rank: int
    report_id: str
    keyword_score: float
    match_reason: str


class QueryResults(BaseModel):
    """A query with its keyword search results."""

    query: str
    description: str
    results: list[KeywordResult]


class IdealRanking(BaseModel):
    """Single entry in ideal top-10 ranking."""

    rank: int
    report_id: str
    rationale: str


class QueryIdealRanking(BaseModel):
    """A query with its ideal top-10 ranking."""

    query: str
    top_10: list[IdealRanking]


class RerankedResult(BaseModel):
    """Single result after semantic re-ranking."""

    report_id: str
    score: float
    original_rank: int
