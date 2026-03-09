# Subtask 1.6: evaluate.py (Metrics and Evaluation)

## Parent Task
task-001-semantic-reranker

## Description
Create `evaluate.py` implementing NDCG@10 (graded relevance) and Precision@5 (binary). Shows keyword baseline NDCG@10 for comparison. Rich table output with per-query and average scores.

## Acceptance Criteria

* Given installed dependencies and data files
  When `python evaluate.py` is run
  Then it outputs a rich-formatted table with NDCG@10 and Precision@5 for each of 5 queries plus averages

* Given the NDCG calculation
  When ideal rank 1 = score 10, rank 2 = 9, ..., rank 10 = 1, absent = 0
  Then NDCG@10 = DCG / IDCG computed correctly

* Given the table output
  When reviewed
  Then it also shows keyword baseline NDCG@10 for comparison

* Given evaluate.py
  When it accesses data files
  Then ideal_rankings.json is loaded ONLY by evaluate.py, never by Reranker

## Verification Steps
- `python evaluate.py` produces formatted table with numeric scores
- All 5 queries have scores plus averages row
- Keyword baseline column present for comparison

## Files to Create/Modify
- `apps/semantic-reranker/evaluate.py`
