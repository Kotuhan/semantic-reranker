# Semantic Re-Ranker

Standalone Python app that re-ranks keyword search results using a cross-encoder model (`BAAI/bge-reranker-base`). Not integrated with the monorepo toolchain (no pnpm/turborepo).

## Quick Reference

```bash
cd apps/semantic-reranker
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py        # Demo: re-ranks all 5 queries, shows rich tables
python evaluate.py    # Metrics: NDCG@10, Precision@5 per query + averages
python benchmark.py   # Compare all re-ranking approaches (15 experiments)
```

## Project Structure

```
apps/semantic-reranker/
  data/
    reports.json              # 30 intelligence reports (read by main.py + evaluate.py)
    keyword_results.json      # 5 queries x 20 keyword results
    ideal_rankings.json       # Ground truth (evaluate.py ONLY -- never import elsewhere)
  src/reranker/
    __init__.py               # Exports Reranker class
    reranker.py               # Reranker class -- core scoring logic
    models.py                 # Pydantic models (Report, KeywordResult, RerankedResult, etc.)
    utils.py                  # Data loaders + get_report_text()
    metrics.py                # compute_ndcg(), compute_precision() -- shared by evaluate.py and benchmark.py
  main.py                     # Demo entry point (rich tables)
  evaluate.py                 # Evaluation script (NDCG@10, Precision@5)
  benchmark.py                # Benchmark: compares 15 experiments across text/model/scoring variants
  requirements.txt            # sentence-transformers, torch, pydantic, rich
  WRITEUP.md                  # Technical write-up (Approach, Architecture, Trade-offs, Future)
  README.md                   # Setup and run instructions
```

## Architecture Decisions

- **Model**: `BAAI/bge-reranker-base` -- selected via benchmark (task-002). Outperforms MiniLM-L-6-v2 (+7.9% NDCG) and MiniLM-L-12-v2 (+0.7% NDCG). Latency ~1.1s per query on CPU, within 2-3s budget.
- **Document text for scoring**: `title + ". " + description + " Location: " + country + ", " + city + "." + " Categories: " + flattened_subcategories` -- benchmark showed subcategories as text improves NDCG by +5-14% across all models. Previous decision to exclude subcategories was reversed based on data.
- **Model loading**: Loaded once in `Reranker.__init__()`, reused across calls. First run downloads ~350MB to HuggingFace cache; subsequent runs are offline.
- **Batch scoring**: All query-document pairs scored in a single `model.predict()` call per query (not one-by-one).
- **Graded relevance for NDCG**: ideal rank 1 = score 10, rank 2 = 9, ..., rank 10 = 1, absent = 0.
- **`sys.path.insert(0, "src")`**: Used in `main.py`, `evaluate.py`, and `benchmark.py` to import from `src/reranker/`. Scripts must be run from the `apps/semantic-reranker/` directory.
- **Metrics extracted to `metrics.py`**: `compute_ndcg` and `compute_precision` shared between `evaluate.py` and `benchmark.py`.

## Patterns

- **Pydantic models** for all data structures (Report, KeywordResult, QueryResults, RerankedResult, etc.)
- **Typed function signatures** with `-> return_type` on all functions
- **`rich` library** for all console output (tables with columns, colored text)
- **Error handling**: `FileNotFoundError` with descriptive messages for missing data files, `RuntimeError` wrapping model load failures, warning logs for invalid report IDs (skip gracefully)
- **Data loaders** return typed objects: `load_reports() -> dict[str, Report]`, `load_keyword_results() -> list[QueryResults]`
- **Benchmark experiments as dataclasses** -- each experiment is a config with name, model, text composer, score modifier

## DO NOT

- Import or reference `ideal_rankings.json` from `main.py` or `reranker.py` -- it is evaluation-only data, accessed exclusively by `evaluate.py` and `benchmark.py`
- Call `model.predict()` one pair at a time -- always batch all pairs for a query
- Assume scripts work from any directory -- they use relative paths to `data/` and `sys.path.insert(0, "src")`
- Use hybrid scoring (keyword+semantic interpolation) -- benchmark proved it degrades results at all alpha values
- Use category match bonus as additive score modifier -- benchmark showed <1% improvement, not worth the complexity

## Known Limitations

- **General-domain model**: `bge-reranker-base` is trained on general web/search data, not intelligence domain. Domain fine-tuning would further improve results.
- **CPU-only**: No GPU path. Latency ~1.1s per query (20 candidates) -- acceptable for ~12 concurrent users but would need GPU at scale.

## Performance Baseline

| Metric | Value |
|--------|-------|
| Avg NDCG@10 (semantic) | 0.8283 |
| Avg NDCG@10 (keyword baseline) | 0.2196 |
| Improvement | 3.8x |
| Avg Precision@5 | 0.8000 |
| Latency per query (20 candidates) | ~1.1s on CPU |

### Benchmark History (task-002)

| Configuration | NDCG@10 | P@5 |
|---|---|---|
| MiniLM-L-6 + title/desc/loc (original) | 0.6908 | 0.6800 |
| bge-reranker-base + title/desc/loc/subcats (current) | 0.8283 | 0.8000 |
| Improvement | +19.9% | +17.6% |
