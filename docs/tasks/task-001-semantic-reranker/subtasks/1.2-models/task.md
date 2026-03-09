# Subtask 1.2: Pydantic Data Models

## Parent Task
task-001-semantic-reranker

## Description
Create `src/reranker/models.py` with Pydantic models: Report, KeywordResult, QueryResults, IdealRanking, QueryIdealRanking, RerankedResult. These provide type-safe data contracts for all JSON data and re-ranking output.

## Acceptance Criteria

* Given `models.py`
  When Report model is instantiated from a reports.json entry
  Then it validates successfully with fields: id, title, description, type, country, city, event_date, subcategories

* Given `models.py`
  When KeywordResult and QueryResults are instantiated from keyword_results.json
  Then they validate successfully with all fields

* Given `models.py`
  When RerankedResult is instantiated
  Then it has fields: report_id, score, original_rank

## Verification Steps
- All models instantiate from JSON data without validation errors
- Field types match the JSON schema

## Files to Create/Modify
- `apps/semantic-reranker/src/reranker/models.py`
