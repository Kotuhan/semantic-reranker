# Subtask 1.3: Data Loading Utilities

## Parent Task
task-001-semantic-reranker

## Description
Create `src/reranker/utils.py` with helper functions: `load_reports()`, `load_keyword_results()`, `load_ideal_rankings()`, `get_report_text()`. Each loads the corresponding JSON file and returns typed Pydantic objects.

## Acceptance Criteria

* Given `utils.py` and valid data files
  When `load_reports()` is called
  Then it returns `dict[str, Report]` keyed by report ID

* Given `utils.py` and valid data files
  When `load_keyword_results()` is called
  Then it returns `list[QueryResults]`

* Given a Report object
  When `get_report_text(report)` is called
  Then it returns `"{title}. {description}"` (period separator for sentence boundary)

## Verification Steps
- Each loader returns correctly typed objects from data files
- `get_report_text` produces expected concatenation
- Error handling for missing files

## Files to Create/Modify
- `apps/semantic-reranker/src/reranker/utils.py`
