# Semantic Re-Ranker

Standalone Python app that re-ranks keyword search results using a cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`). Not integrated with the monorepo toolchain (no pnpm/turborepo).

## Quick Reference

```bash
cd apps/semantic-reranker
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py        # Demo: re-ranks all 5 queries, shows rich tables
python evaluate.py    # Metrics: NDCG@10, Precision@5 per query + averages
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
  main.py                     # Demo entry point (rich tables)
  evaluate.py                 # Evaluation script (NDCG@10, Precision@5)
  requirements.txt            # sentence-transformers, torch, pydantic, rich
  WRITEUP.md                  # Technical write-up (Approach, Architecture, Trade-offs, Future)
  README.md                   # Setup and run instructions
```

## Architecture Decisions

- **Document text for scoring**: `title + ". " + description + " Location: " + country + ", " + city + "."` -- country/city appended to support geo-queries (e.g., "Middle East"). Subcategories excluded (structured tags add noise to cross-encoder).
- **Model loading**: Loaded once in `Reranker.__init__()`, reused across calls. First run downloads ~80MB to HuggingFace cache; subsequent runs are offline.
- **Batch scoring**: All query-document pairs scored in a single `model.predict()` call per query (not one-by-one).
- **Graded relevance for NDCG**: ideal rank 1 = score 10, rank 2 = 9, ..., rank 10 = 1, absent = 0.
- **`sys.path.insert(0, "src")`**: Used in `main.py` and `evaluate.py` to import from `src/reranker/`. Scripts must be run from the `apps/semantic-reranker/` directory.

## Patterns

- **Pydantic models** for all data structures (Report, KeywordResult, QueryResults, RerankedResult, etc.)
- **Typed function signatures** with `-> return_type` on all functions
- **`rich` library** for all console output (tables with columns, colored text)
- **Error handling**: `FileNotFoundError` with descriptive messages for missing data files, `RuntimeError` wrapping model load failures, warning logs for invalid report IDs (skip gracefully)
- **Data loaders** return typed objects: `load_reports() -> dict[str, Report]`, `load_keyword_results() -> list[QueryResults]`

## DO NOT

- Import or reference `ideal_rankings.json` from `main.py` or `reranker.py` -- it is evaluation-only data, accessed exclusively by `evaluate.py`
- Include subcategories in document text for scoring -- they are structured taxonomy tags, not natural language
- Call `model.predict()` one pair at a time -- always batch all pairs for a query
- Assume scripts work from any directory -- they use relative paths to `data/` and `sys.path.insert(0, "src")`

## Known Limitations

- **General-domain model**: `ms-marco-MiniLM-L-6-v2` is trained on web search data, not intelligence domain. Some domain-specific vocabulary gaps remain (e.g., TATP synthesis not strongly matched to "homemade explosives"). Domain fine-tuning would address this.
- **CPU-only**: No GPU path. Latency is well under budget (~0.3s per 20 candidates) but would matter at scale.

## Performance Baseline

| Metric | Value |
|--------|-------|
| Avg NDCG@10 (semantic) | 0.6908 |
| Avg NDCG@10 (keyword baseline) | 0.2196 |
| Improvement | 3.1x |
| Avg Precision@5 | 0.6800 |
| Latency per query (20 candidates) | < 0.31s on CPU |
