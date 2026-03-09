# Subtask 1.4: Reranker Class (Core Logic)

## Parent Task
task-001-semantic-reranker

## Description
Create `src/reranker/reranker.py` with the `Reranker` class. Uses `sentence-transformers` `CrossEncoder` with `cross-encoder/ms-marco-MiniLM-L-6-v2`. Method `rerank(query, candidates, reports, top_k=10)` scores each query-document pair and returns top-k results sorted by relevance.

## Acceptance Criteria

* Given a Reranker instance
  When `rerank()` is called with a query, 20 candidate IDs, and reports dict
  Then it returns exactly 10 RerankedResult objects sorted by descending score

* Given candidate IDs that don't exist in reports
  When `rerank()` is called
  Then invalid IDs are skipped with a warning, not a crash

* Given an empty candidates list
  When `rerank()` is called
  Then it returns an empty list

* Given the model
  When loaded
  Then it uses CrossEncoder from sentence-transformers (not raw transformers)

## Verification Steps
- Instantiate Reranker, call rerank() on first query from keyword_results.json
- Verify returns exactly 10 results, all valid report IDs, sorted by descending score
- Update `src/reranker/__init__.py` to export Reranker

## Files to Create/Modify
- `apps/semantic-reranker/src/reranker/reranker.py`
- `apps/semantic-reranker/src/reranker/__init__.py` (update exports)
