# Architecture Review — task-002: Benchmark Re-Ranking Approaches

**Date**: 2026-03-09
**Reviewer**: system-architect
**Verdict**: APPROVED

## Scope Assessment

This task adds a `benchmark.py` script to the existing `apps/semantic-reranker/` standalone Python app. No new architectural components, no new dependencies beyond what's already in requirements.txt (sentence-transformers already supports all three target models), no API surface changes.

## Review Points

### 1. Consistency with Existing Architecture
**PASS** -- Follows the same pattern as `evaluate.py` and `main.py`: standalone script, `sys.path.insert(0, "src")`, rich table output, reuses existing data loaders and models.

### 2. ADR Compliance
- ADR-0001 (standalone Python app): No change, benchmark.py stays within the same app
- ADR-0002 (cross-encoder model): Benchmark tests alternative models but does not change the architecture pattern (still cross-encoder re-ranking)
- ADR-0003 (document text composition): Benchmark tests alternatives but any change to default composition would be a conscious decision based on data

### 3. Refactoring: Extract Metrics to utils.py
**APPROVED** -- Moving `compute_ndcg` and `compute_precision` from `evaluate.py` to `src/reranker/metrics.py` (or `utils.py`) is a clean improvement. Both `evaluate.py` and `benchmark.py` need these functions. No behavioral change.

### 4. Model Caching
**APPROVED** -- Simple dict-based cache for loaded models within a single script run. No persistence concerns.

### 5. Risk: Changing Default Configuration
The TL design includes "update best config as new default" if benchmark identifies a winner. This is acceptable -- it should be done by updating `get_report_text()` and/or `DEFAULT_MODEL` constant, with the benchmark results as justification. If the winning model changes, ADR-0002 and ADR-0003 should be updated to reflect the new decision.

## Conditions

- If the benchmark identifies a new best model (not MiniLM-L-6-v2), update ADR-0002 with the new choice and rationale.
- If the benchmark identifies a new best text composition, update ADR-0003.
- Update `apps/semantic-reranker/CLAUDE.md` performance baseline section with new numbers.

## Decomposition Assessment

**No decomposition needed.** This is a 5-step task with low complexity:
- All within a single Python file (benchmark.py) + minor refactor of evaluate.py
- Single tech domain (Python, sentence-transformers)
- No external integrations
- Estimated effort: < 0.5 days

Proceed directly to implementation.
