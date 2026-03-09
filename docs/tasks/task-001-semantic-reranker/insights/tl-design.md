# Technical Design: task-001
Generated: 2026-03-09

## Overview

Build a standalone Python package within `apps/semantic-reranker/` that implements a cross-encoder re-ranker using `cross-encoder/ms-marco-MiniLM-L-6-v2`. The project takes keyword search results (20 candidates per query) and re-ranks them by semantic relevance, returning the top 10. Three deliverables: `main.py` (demo), `evaluate.py` (metrics), and `WRITEUP.md` (analysis). No monorepo integration beyond living in `apps/`.

## Technical Notes

- **Affected modules:** None existing. New standalone Python project in `apps/semantic-reranker/`.
- **New modules to create:**
  - `apps/semantic-reranker/src/reranker/` -- Python package with core re-ranking logic
  - `apps/semantic-reranker/main.py` -- demo entry point
  - `apps/semantic-reranker/evaluate.py` -- evaluation script
  - `apps/semantic-reranker/WRITEUP.md` -- technical write-up
  - `apps/semantic-reranker/README.md` -- setup and run instructions
  - `apps/semantic-reranker/requirements.txt` -- dependencies
- **DB schema change required?** No.
- **Architectural considerations:**
  - The `Reranker` class must be stateless beyond model loading (model loaded once at init, reused across calls)
  - Document text for scoring = `title + ". " + description + " Location: " + country + ", " + city + "."` (title/description for semantic content, country/city appended for geo-queries like "Middle East")
  - Subcategories are structured taxonomy tags, not natural language. Including them would add noise to the cross-encoder input -- exclude from scoring text.
  - Data files (`reports.json`, `keyword_results.json`) are copied into `apps/semantic-reranker/data/`. `ideal_rankings.json` is also copied but only accessed by `evaluate.py`, never by `Reranker` or `main.py`.
  - Model is downloaded on first run to HuggingFace cache (`~/.cache/huggingface/`). Subsequent runs work offline.
  - The `rich` library provides the formatted console table output.
  - Graded relevance for NDCG: position 1 in ideal = score 10, position 2 = 9, ..., position 10 = 1, absent = 0.
- **Known risks or trade-offs:**
  - **Low risk:** Model download on first run requires network. README must document this clearly.
  - **Low risk:** Cross-encoder performance varies by hardware. The 2-3 second latency budget is comfortable for 20 candidates on modern CPUs but should be verified.
  - **Low risk:** The model is general-domain (MS MARCO), not tuned for intelligence/IED terminology. The cross-encoder's semantic understanding should still bridge vocabulary gaps (VBIED <-> vehicle bomb) based on contextual co-occurrence in pretraining data, but NDCG scores may not be perfect.
- **Test plan:** No unit tests. `evaluate.py` serves as the verification script, reporting NDCG@10 and Precision@5 per query.

## Architecture Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| Concatenate `title + description + location` as document text | Title/description are the richest natural-language fields. Country/city appended as "Location: X, Y" to help geo-queries (e.g., "Middle East" matching "Iraq, Mosul"). | Include subcategories (rejected: structured tags, add noise). Exclude location (rejected after user review: hurts geo-queries). |
| Use `sentence-transformers` `CrossEncoder` class | Standard, well-maintained wrapper for HuggingFace cross-encoders. Handles tokenization, batching, and scoring. | Raw `transformers` AutoModelForSequenceClassification (more boilerplate, no benefit) |
| Pydantic models for data structures | Type safety, validation, clear data contracts. Matches PRD's code architecture spec. | Plain dicts (fragile), dataclasses (less validation) |
| `rich` for console output | PRD specifies "rich-formatted console table". `rich` is the standard Python library for this. | `tabulate` (less formatting control), plain print (doesn't meet spec) |
| Copy data files into app directory | Self-contained project. Evaluators can clone and run without navigating monorepo. | Symlink to original data (fragile, platform-dependent) |
| No `__main__.py` or CLI framework | Two simple entry points (`main.py`, `evaluate.py`). `argparse`/`click` would be overengineering. | Click CLI (overkill for 2 scripts) |

## Implementation Steps

### Step 1 -- Project scaffolding and data files

Create the directory structure and copy data files.

- Files to create:
  - `apps/semantic-reranker/` directory tree
  - `apps/semantic-reranker/data/reports.json` (copy from `docs/product/assignment-semantic-reranker/data/`)
  - `apps/semantic-reranker/data/keyword_results.json` (copy)
  - `apps/semantic-reranker/data/ideal_rankings.json` (copy)
  - `apps/semantic-reranker/src/__init__.py` (empty)
  - `apps/semantic-reranker/src/reranker/__init__.py` (exports `Reranker` class)
  - `apps/semantic-reranker/requirements.txt`
- Verification: Directory structure matches PRD Section 5 layout. `requirements.txt` contains `sentence-transformers`, `torch`, `rich`, `pydantic`. All three data files present and valid JSON.

### Step 2 -- Pydantic data models

Define typed data models for reports, keyword results, and ideal rankings.

- Files to create/modify:
  - `apps/semantic-reranker/src/reranker/models.py`
- Models:
  - `Report` -- id, title, description, type, country, city, event_date, subcategories
  - `KeywordResult` -- rank, report_id, keyword_score, match_reason
  - `QueryResults` -- query, description, results (list of KeywordResult)
  - `IdealRanking` -- rank, report_id, rationale
  - `QueryIdealRanking` -- query, top_10 (list of IdealRanking)
  - `RerankedResult` -- report_id, score, original_rank
- Verification: Models can be instantiated from the JSON data files without validation errors.

### Step 3 -- Data loading utilities

Implement helper functions to load and parse the JSON data files.

- Files to create/modify:
  - `apps/semantic-reranker/src/reranker/utils.py`
- Functions:
  - `load_reports(path) -> dict[str, Report]` -- loads reports.json, returns dict keyed by report ID
  - `load_keyword_results(path) -> list[QueryResults]` -- loads keyword_results.json
  - `load_ideal_rankings(path) -> list[QueryIdealRanking]` -- loads ideal_rankings.json
  - `get_report_text(report: Report) -> str` -- returns `f"{report.title}. {report.description} Location: {report.country}, {report.city}."` (country/city for geo-relevance)
- Verification: Each loader function returns correctly typed objects. `get_report_text` produces expected concatenation.

### Step 4 -- Reranker class (core logic)

Implement the `Reranker` class with `rerank()` method.

- Files to create/modify:
  - `apps/semantic-reranker/src/reranker/reranker.py`
- Class design:
  - `__init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2")` -- loads CrossEncoder model
  - `rerank(self, query: str, candidates: list[str], reports: dict[str, Report], top_k: int = 10) -> list[RerankedResult]`
    - For each candidate ID, look up report, get text via `get_report_text`
    - Build list of `(query, report_text)` pairs
    - Score all pairs with cross-encoder in a single batch call (`model.predict()`)
    - Sort by score descending
    - Return top_k `RerankedResult` objects
  - Error handling: validate candidate IDs exist in reports dict, handle empty candidates list, catch model loading failures
- Update `apps/semantic-reranker/src/reranker/__init__.py` to export `Reranker`
- Verification: Instantiate `Reranker`, call `rerank()` with first query from keyword_results.json. Verify it returns exactly 10 results, all valid report IDs, sorted by descending score.

### Step 5 -- main.py (demo entry point)

Create the demo script that shows the re-ranker in action.

- Files to create:
  - `apps/semantic-reranker/main.py`
- Behavior:
  - Load reports and keyword results
  - Instantiate `Reranker`
  - For each of the 5 queries: run `rerank()`, print query, print re-ranked top-10 with rank, report ID, title, and relevance score
  - Use `rich` for formatted console output (table per query)
  - Print timing per query to demonstrate latency
- Verification: `python main.py` runs without errors, produces formatted output for all 5 queries, each showing 10 results with scores.

### Step 6 -- evaluate.py (metrics and evaluation)

Implement the evaluation script with NDCG@10 and Precision@5.

- Files to create:
  - `apps/semantic-reranker/evaluate.py`
- Metric implementations:
  - `compute_ndcg(reranked_ids: list[str], ideal_ranking: list[IdealRanking], k: int = 10) -> float`
    - Graded relevance: ideal rank 1 = score 10, rank 2 = 9, ..., rank 10 = 1, absent = 0
    - DCG@k = sum of relevance_i / log2(i+1) for i in 1..k
    - IDCG@k = DCG of the ideal ordering (scores [10, 9, 8, ..., 1] in perfect order)
    - NDCG@k = DCG / IDCG
  - `compute_precision(reranked_ids: list[str], ideal_ids: set[str], k: int = 5) -> float`
    - Precision@5 = count of top-5 reranked IDs that appear in ideal top-10 / 5
- Output: `rich` table with columns: Query, NDCG@10, Precision@5. Final row: Average.
- Also show keyword baseline NDCG@10 for comparison (run the same NDCG computation on the original keyword ranking).
- Verification: `python evaluate.py` runs without errors, produces formatted table with numeric scores for all 5 queries plus averages.

### Step 7 -- WRITEUP.md

Create the technical write-up covering all four required sections.

- Files to create:
  - `apps/semantic-reranker/WRITEUP.md`
- Sections:
  - **Approach:** Cross-encoder re-ranking with ms-marco-MiniLM-L-6-v2. Why cross-encoder over bi-encoder. Why this model (lightweight, CPU-friendly, offline).
  - **Architecture:** Two integration options (monolith module vs. microservice). Recommend monolith for ~12 concurrent users. Diagram of search pipeline.
  - **Trade-offs:** Latency vs. quality (cross-encoder is slower but more accurate than bi-encoder, acceptable for 20 candidates). CPU-only constraint. Cold-start (first model load). No fine-tuning.
  - **What I'd do with more time:** Query expansion (synonyms, HyDE), domain fine-tuning, dense retrieval first stage, expand candidate pool to 50.
- Verification: Document exists, covers all 4 sections, does not exceed ~1 page.

### Step 8 -- README.md

Create setup and run instructions.

- Files to create:
  - `apps/semantic-reranker/README.md`
- Content:
  - Project description
  - Prerequisites (Python 3.10+)
  - Setup instructions (venv, pip install)
  - First run note (model download requires internet, ~80MB, subsequent runs offline)
  - Run instructions (`python main.py`, `python evaluate.py`)
  - Project structure overview
- Verification: Following README instructions on a fresh environment results in successful execution.

### Step 9 -- End-to-end verification

Run both scripts and verify all acceptance criteria.

- Run `python main.py` -- confirm output for all 5 queries, 10 results each
- Run `python evaluate.py` -- confirm NDCG@10 and Precision@5 table
- Verify RPT-001 and RPT-006 appear in top 5 for "vehicle bomb" query
- Verify RPT-023, RPT-009, RPT-002 appear in top 5 for "homemade explosives" query
- Verify latency < 3 seconds per query on CPU
- Verify `ideal_rankings.json` is not imported by `main.py` or `reranker.py`
- Verify code has error handling for missing files, invalid inputs, model loading failures
- Verification: All acceptance criteria from PO analysis pass.

## Complexity Assessment

- **Estimated effort:** 1 day (3-5 hours of implementation)
- **Risk level:** Low
  - Well-defined scope with clear deliverables
  - Standard libraries (sentence-transformers, rich, pydantic)
  - No external dependencies, no database, no API
  - The cross-encoder model is proven for this exact use case (re-ranking)
- **Dependencies:** None external. Python ecosystem packages only.

## Key File Structure

```
apps/semantic-reranker/
├── data/
│   ├── reports.json              # 30 intelligence reports
│   ├── keyword_results.json      # 5 queries x 20 keyword results
│   └── ideal_rankings.json       # ground truth (evaluate.py only)
├── src/
│   ├── __init__.py
│   └── reranker/
│       ├── __init__.py           # exports Reranker
│       ├── reranker.py           # Reranker class (core logic)
│       ├── models.py             # Pydantic data models
│       └── utils.py              # data loading helpers
├── main.py                       # demo entry point
├── evaluate.py                   # evaluation script
├── WRITEUP.md                    # technical write-up
├── README.md                     # setup and run instructions
└── requirements.txt              # Python dependencies
```

## Requirements.txt Content

```
sentence-transformers>=2.2.0
torch>=2.0.0
pydantic>=2.0.0
rich>=13.0.0
```

Note: `torch` is pulled in by `sentence-transformers` but listing it explicitly ensures CPU-only install works. Consider pinning `torch` with CPU-only index URL in README instructions if needed: `pip install torch --index-url https://download.pytorch.org/whl/cpu`.

## Test Strategy

- **No unit tests** (per PO scope -- "unit tests beyond evaluate.py" is out of scope)
- **evaluate.py is the test:** Reports NDCG@10 and Precision@5 per query and averages
- **Manual verification:** Run `main.py`, check output makes sense, check specific report IDs appear in expected positions
- **Latency check:** Time each query in `main.py` output, verify < 3 seconds

## Open Technical Questions

None. All technical decisions are resolved by the PRD and PO analysis:
- Model choice, metrics, relevance scoring, output format, constraints, and code structure are all specified.
- Document text composition (title + description + location) refined after user review to include country/city for geo-query support.
- No ambiguity remains in the implementation path.
