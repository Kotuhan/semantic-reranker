"""Core semantic re-ranker using cross-encoder model."""

import logging
from typing import Optional

from sentence_transformers import CrossEncoder

from .models import RerankedResult, Report
from .utils import get_report_text

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    """Semantic re-ranker using a cross-encoder model.

    Scores query-document pairs jointly and re-ranks by semantic relevance.
    Model is loaded once at init and reused across calls.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        """Load the cross-encoder model.

        Args:
            model_name: HuggingFace model identifier. Downloaded on first run,
                cached locally for subsequent offline use.

        Raises:
            RuntimeError: If model loading fails.
        """
        try:
            self.model = CrossEncoder(model_name)
            logger.info("Loaded model: %s", model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load model '{model_name}': {e}") from e

    def rerank(
        self,
        query: str,
        candidates: list[str],
        reports: dict[str, Report],
        top_k: int = 10,
    ) -> list[RerankedResult]:
        """Re-rank candidate reports by semantic relevance to the query.

        Args:
            query: Search query string.
            candidates: List of report IDs (from keyword engine top-20).
            reports: Dict of all reports keyed by ID.
            top_k: Number of top results to return.

        Returns:
            List of RerankedResult sorted by descending relevance score.
        """
        if not candidates:
            return []

        # Build (query, document_text) pairs, tracking original rank
        pairs: list[tuple[str, str]] = []
        valid_candidates: list[tuple[str, int]] = []  # (report_id, original_rank)

        for rank, report_id in enumerate(candidates, start=1):
            report = reports.get(report_id)
            if report is None:
                logger.warning("Report ID '%s' not found in reports, skipping", report_id)
                continue
            pairs.append((query, get_report_text(report)))
            valid_candidates.append((report_id, rank))

        if not pairs:
            return []

        # Score all pairs in a single batch
        scores = self.model.predict(pairs)

        # Combine scores with candidate info and sort
        scored = [
            RerankedResult(
                report_id=report_id,
                score=float(score),
                original_rank=original_rank,
            )
            for (report_id, original_rank), score in zip(valid_candidates, scores)
        ]
        scored.sort(key=lambda r: r.score, reverse=True)

        return scored[:top_k]
