# Subtask 1.5: main.py (Demo Entry Point)

## Parent Task
task-001-semantic-reranker

## Description
Create `main.py` that loads data, instantiates Reranker, runs all 5 queries, and prints rich-formatted tables with rank, report ID, title, and relevance score. Also prints timing per query.

## Acceptance Criteria

* Given installed dependencies and data files
  When `python main.py` is run
  Then it outputs formatted results for all 5 queries, 10 results each

* Given the output
  When reviewed
  Then each result shows rank, report ID, title, and semantic relevance score

* Given each query
  When timed
  Then processing completes within 3 seconds on CPU

* Given the imports in main.py
  When reviewed
  Then ideal_rankings.json is NOT imported or referenced

## Verification Steps
- `python main.py` produces formatted output for all 5 queries
- Each query shows 10 results with scores
- Timing displayed per query

## Files to Create/Modify
- `apps/semantic-reranker/main.py`
