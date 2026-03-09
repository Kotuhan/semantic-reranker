# Subtask 1.1: Project Scaffolding and Data Files

## Parent Task
task-001-semantic-reranker

## Description
Create the `apps/semantic-reranker/` directory tree, copy 3 data JSON files from `docs/product/assignment-semantic-reranker/data/`, create `requirements.txt` with dependencies (sentence-transformers, torch, pydantic, rich), and create empty `__init__.py` files.

## Acceptance Criteria

* Given the monorepo root
  When the subtask is complete
  Then `apps/semantic-reranker/` directory exists with `src/reranker/`, `data/` subdirectories

* Given `apps/semantic-reranker/data/`
  When listing files
  Then `reports.json`, `keyword_results.json`, `ideal_rankings.json` are present and valid JSON

* Given `apps/semantic-reranker/requirements.txt`
  When read
  Then it contains `sentence-transformers`, `torch`, `pydantic`, `rich` with version constraints

* Given `apps/semantic-reranker/src/` and `apps/semantic-reranker/src/reranker/`
  When listing files
  Then both contain `__init__.py`

## Verification Steps
- Directory structure matches PRD Section 5 layout
- All 3 data files present and valid JSON
- `requirements.txt` present with correct dependencies
- `__init__.py` files exist

## Files to Create/Modify
- `apps/semantic-reranker/data/reports.json` (copy)
- `apps/semantic-reranker/data/keyword_results.json` (copy)
- `apps/semantic-reranker/data/ideal_rankings.json` (copy)
- `apps/semantic-reranker/src/__init__.py`
- `apps/semantic-reranker/src/reranker/__init__.py`
- `apps/semantic-reranker/requirements.txt`
