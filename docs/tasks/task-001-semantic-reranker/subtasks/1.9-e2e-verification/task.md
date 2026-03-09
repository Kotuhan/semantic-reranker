# Subtask 1.9: End-to-End Verification

## Parent Task
task-001-semantic-reranker

## Description
Run both scripts and verify all acceptance criteria from PO analysis. Check specific report rankings, latency, error handling, and code quality.

## Acceptance Criteria

* Given `python main.py`
  When run
  Then outputs all 5 queries with 10 results each, no errors

* Given `python evaluate.py`
  When run
  Then outputs NDCG@10 and Precision@5 table for all 5 queries plus averages

* Given query "vehicle bomb attacks in the Middle East"
  When re-ranked
  Then RPT-001 and RPT-006 appear in top 5

* Given query "homemade explosives from household chemicals"
  When re-ranked
  Then RPT-023, RPT-009, RPT-002 appear in top 5

* Given any query
  When processed
  Then latency < 3 seconds on CPU

* Given main.py and reranker.py imports
  When reviewed
  Then ideal_rankings.json is NOT referenced

* Given the codebase
  When reviewed
  Then error handling exists for missing files, invalid inputs, model loading failures

## Verification Steps
- Run main.py and evaluate.py end-to-end
- Spot-check specific report rankings
- Measure latency
- Review imports for ideal_rankings.json isolation
- Review error handling

## Files to Create/Modify
- None (verification only)
