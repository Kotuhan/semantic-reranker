# QA Verification — task-002: Benchmark Re-Ranking Approaches

**Date**: 2026-03-09
**Verdict**: APPROVED

## Test Results

### 1. Benchmark Script Runs Successfully
- **PASS** -- `python benchmark.py` runs all 15 experiments and produces a comparison table
- Output includes NDCG@10, Precision@5, and delta vs baseline for every experiment

### 2. Text Composition Variants
- **PASS** -- 4 variants tested: title-only (0.6445), title+desc (0.6739), title+desc+loc (0.6908), title+desc+loc+subcats (0.7403)

### 3. Subcategory Scoring Variants
- **PASS** -- 4 variants tested: category bonus beta=0.5/1.0/2.0, weighted text enrichment

### 4. Multiple Models
- **PASS** -- 3 models tested: MiniLM-L-6-v2 (baseline), MiniLM-L-12-v2 (0.7401), bge-reranker-base (0.7452)

### 5. Hybrid Scoring
- **PASS** -- 3 alpha values tested: 0.7, 0.8, 0.9

### 6. Best Configuration Highlighted
- **PASS** -- "Best configuration: bge-reranker-base + subcats" displayed with green bold

### 7. Best Configuration Applied as Default
- **PASS** -- `DEFAULT_MODEL` updated to `BAAI/bge-reranker-base`, `get_report_text()` includes subcategories
- Verified: `evaluate.py` with new defaults produces NDCG@10=0.8283, matching benchmark result

### 8. Metrics Extraction Refactor
- **PASS** -- `compute_ndcg` and `compute_precision` extracted to `src/reranker/metrics.py`
- Verified: `evaluate.py` still produces correct results after refactor (baseline was 0.6908 before model/text change)
- Verified: metric functions pass unit assertions (perfect ranking=1.0, precision calculation correct)

### 9. No Regressions
- **PASS** -- `evaluate.py` works correctly with new defaults
- **PASS** -- `main.py` works correctly with new defaults

## Notes

- No `pnpm lint/test/build` applicable -- this is a standalone Python app not in the monorepo toolchain
- No unit test framework configured for this app (evaluation scripts serve as verification)
