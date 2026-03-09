---
id: task-001
title: Implement Semantic Re-Ranker for Intelligence Reports
status: backlog
priority: high
dependencies: []
created_at: 2026-03-09
---

# Implement Semantic Re-Ranker for Intelligence Reports

## Problem (PO)

Intelligence analysts, EOD technicians, and non-technical users searching the Codex platform cannot find the most relevant intelligence reports because the keyword search engine fails on vocabulary mismatch. Queries using natural language (e.g., "vehicle bomb") do not match domain-specific terminology in reports (e.g., "VBIED", "car-borne IED"), causing the most relevant results to be buried at ranks 14-20 instead of appearing at the top.

Evidence from the provided data: across all 5 test queries, the keyword engine consistently ranks the most semantically relevant reports near the bottom of its top-20. For example, RPT-001 (VBIED attack in Mosul -- the ideal #1 result for "vehicle bomb attacks") is ranked #14 by keywords. RPT-023 (TATP synthesis manual -- ideal #1 for "homemade explosives") is ranked #17.

**Task:** Build a Python semantic re-ranker using `cross-encoder/ms-marco-MiniLM-L-6-v2` that takes the keyword engine's top-20 results and re-orders them so the most semantically relevant reports appear in the top-10. This is a take-home assignment for Codex with three deliverables: `main.py`, `evaluate.py`, and `WRITEUP.md`.

## Success Criteria (PO)

1. Re-ranker produces NDCG@10 scores demonstrating meaningful improvement over keyword-only ranking across all 5 queries
2. `evaluate.py` runs end-to-end and outputs a rich-formatted table with per-query NDCG@10, Precision@5, and averages
3. `main.py` runs successfully on a fresh Python 3.10+ environment after `pip install -r requirements.txt`, with no network access required after initial model download
4. All three deliverables present and complete: `main.py`, `evaluate.py`, `WRITEUP.md`
5. Re-ranker processes 20 candidates per query and returns top-10 within 2-3 seconds on CPU
6. Code is clean, readable, well-structured with appropriate abstractions (25% of evaluation weight)
7. Production readiness: error handling, configuration, documentation (20% of evaluation weight)

## Acceptance Criteria (PO)

* Given a fresh Python 3.10+ virtual environment and requirements.txt
  When the user runs `pip install -r requirements.txt`
  Then all dependencies install successfully with no errors

* Given the installed environment and data files in data/
  When the user runs `python main.py`
  Then the script outputs a demo re-ranking for at least one query, showing re-ordered top-10 report IDs with relevance scores

* Given the installed environment and data files in data/
  When the user runs `python evaluate.py`
  Then the script outputs a rich-formatted table with NDCG@10 and Precision@5 for each of the 5 queries plus average scores

* Given query "vehicle bomb attacks in the Middle East" and its 20 keyword results
  When the re-ranker processes this query
  Then RPT-001 (VBIED Mosul) and RPT-006 (car-borne IED Yemen) appear in the top 5 results (keyword ranks 14 and 15; ideal ranks 1 and 2)

* Given query "homemade explosives from household chemicals" and its 20 keyword results
  When the re-ranker processes this query
  Then RPT-023 (TATP synthesis), RPT-009 (HMTD lab), and RPT-002 (TATP precursors) appear in the top 5 results (keyword ranks 17, 16, 15; ideal ranks 1, 2, 3)

* Given any of the 5 queries and their 20 candidates
  When the re-ranker processes the query on CPU
  Then processing completes within 3 seconds

* Given the Reranker class
  When called with `rerank(query: str, candidates: list[str]) -> list[str]`
  Then it returns a list of exactly 10 report IDs ordered by semantic relevance

* Given the code repository
  When reviewed for production readiness
  Then the code includes error handling for missing data files, invalid inputs, and model loading failures

* Given WRITEUP.md
  When reviewed
  Then it covers Approach, Architecture, Trade-offs, and What I'd do with more time, and does not exceed 1 page

* Given evaluate.py
  When it accesses data files
  Then ideal_rankings.json is only used by evaluate.py for scoring, never imported by main.py or Reranker class

## Out of Scope (PO)

- FastAPI or any HTTP service wrapper
- Fine-tuning the cross-encoder model on domain data
- Query expansion or synonym dictionaries
- GPU support or GPU-optimized inference paths
- Dense retrieval / bi-encoder first-stage replacement
- Expanding candidate pool beyond top-20
- Saving evaluation results to file (console output only)
- Integration with actual Elasticsearch or any live search system
- UI or frontend for displaying results
- Docker containerization or deployment scripts
- CI/CD pipeline configuration
- Unit tests beyond the evaluation script
- Monorepo integration concerns (turborepo, pnpm) -- standalone Python project

## Open Questions (PO)

No open questions. The PRD and assignment README provide clear answers on all key decisions:
- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2` (PRD Section 4)
- Metrics: NDCG@10 primary, Precision@5 secondary (PRD Section 6)
- Relevance scoring: graded by position (rank 1 = score 10, ..., rank 10 = score 1, absent = 0) (PRD Section 6)
- Constraints: CPU-only, offline, Python 3.10+ (PRD Section 1, assignment constraints)
- Output: rich-formatted console table (PRD Section 6)
- Code structure: specified in PRD Section 5
- Architecture: monolith module preferred for ~12 concurrent users (PRD Section 5)

---

## Technical Notes (TL)

- **Affected modules:** None existing. New standalone Python project in `apps/semantic-reranker/`.
- **New modules/entities to create:**
  - `apps/semantic-reranker/src/reranker/` -- Python package (reranker.py, models.py, utils.py)
  - `apps/semantic-reranker/main.py` -- demo entry point
  - `apps/semantic-reranker/evaluate.py` -- evaluation script
  - `apps/semantic-reranker/data/` -- copied data files (reports.json, keyword_results.json, ideal_rankings.json)
  - `apps/semantic-reranker/WRITEUP.md`, `README.md`, `requirements.txt`
- **DB schema change required?** No.
- **Architectural considerations:**
  - `Reranker` class loads model once at init, scores query-document pairs via `CrossEncoder.predict()`
  - Document text = `title + ". " + description` (concatenation of two richest fields; subcategories excluded as structured tags add noise)
  - Graded relevance for NDCG: ideal rank 1 = score 10, rank 2 = 9, ..., rank 10 = 1, absent = 0
  - Model downloaded on first run to HuggingFace cache; subsequent runs fully offline
  - `rich` library for formatted console tables
  - `ideal_rankings.json` only accessed by `evaluate.py`, never by `Reranker` or `main.py`
- **Known risks:**
  - Low: First-run model download (~80MB) requires internet. Document in README.
  - Low: CPU latency varies by hardware. Budget is 2-3s for 20 candidates, comfortable on modern CPUs.
- **Test plan:** No unit tests (out of scope per PO). `evaluate.py` serves as verification (NDCG@10, Precision@5).

## Implementation Steps (TL)

1. **Project scaffolding and data files**
   - Files: create `apps/semantic-reranker/` directory tree, copy 3 data JSON files from `docs/product/assignment-semantic-reranker/data/`, create `requirements.txt` (sentence-transformers, torch, pydantic, rich), create empty `__init__.py` files
   - Verification: directory structure matches PRD Section 5, all data files valid JSON, requirements.txt present

2. **Pydantic data models**
   - Files: create `src/reranker/models.py` with Report, KeywordResult, QueryResults, IdealRanking, QueryIdealRanking, RerankedResult models
   - Verification: models instantiate from JSON data without validation errors

3. **Data loading utilities**
   - Files: create `src/reranker/utils.py` with `load_reports()`, `load_keyword_results()`, `load_ideal_rankings()`, `get_report_text()`
   - Verification: each loader returns correctly typed objects from data files

4. **Reranker class (core logic)**
   - Files: create `src/reranker/reranker.py` with `Reranker` class, update `src/reranker/__init__.py` to export it
   - Method: `rerank(query, candidates, reports, top_k=10)` -- looks up report text, batch-scores with cross-encoder, sorts by score, returns top_k RerankedResult list
   - Error handling: validate candidate IDs exist, handle empty candidates, catch model loading failures
   - Verification: call rerank() on first query, returns exactly 10 valid report IDs sorted by descending score

5. **main.py (demo entry point)**
   - Files: create `apps/semantic-reranker/main.py`
   - Loads data, instantiates Reranker, runs all 5 queries, prints rich-formatted tables with rank/report ID/title/score, prints timing per query
   - Verification: `python main.py` produces formatted output for all 5 queries, 10 results each

6. **evaluate.py (metrics and evaluation)**
   - Files: create `apps/semantic-reranker/evaluate.py`
   - Implements NDCG@10 (graded relevance) and Precision@5 (binary: in ideal top-10 or not)
   - Shows keyword baseline NDCG@10 for comparison
   - Rich table output: Query, NDCG@10, Precision@5, plus Average row
   - Verification: `python evaluate.py` produces table with numeric scores for all 5 queries plus averages

7. **WRITEUP.md**
   - Files: create `apps/semantic-reranker/WRITEUP.md`
   - Sections: Approach, Architecture, Trade-offs, What I'd do with more time
   - Verification: all 4 sections present, does not exceed ~1 page

8. **README.md**
   - Files: create `apps/semantic-reranker/README.md`
   - Content: prerequisites, setup (venv + pip install), first-run model download note, run instructions, project structure
   - Verification: following instructions on fresh env leads to successful execution

9. **End-to-end verification**
   - Run `python main.py` and `python evaluate.py`
   - Verify RPT-001, RPT-006 in top 5 for "vehicle bomb" query
   - Verify RPT-023, RPT-009, RPT-002 in top 5 for "homemade explosives" query
   - Verify latency < 3s per query on CPU
   - Verify `ideal_rankings.json` not imported by main.py or reranker.py
   - Verify error handling for missing files and invalid inputs

---

## Implementation Log (DEV)

_To be filled during implementation_

---

## QA Notes (QA)

_To be filled by QA agent_
