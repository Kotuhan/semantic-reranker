# PO Analysis: task-001
Generated: 2026-03-09

## Problem Statement

Intelligence analysts, EOD technicians, and non-technical users searching the Codex platform for threat intelligence cannot find the most relevant reports because the keyword search engine fails on vocabulary mismatch. Queries using natural language (e.g., "vehicle bomb") do not match domain-specific terminology in reports (e.g., "VBIED", "car-borne IED"), causing the most relevant results to be buried at ranks 14-20 instead of appearing at the top.

**Evidence from the data:** Across all 5 test queries, the keyword engine consistently ranks the most semantically relevant reports near the bottom of its top-20 results. For example:
- Query "vehicle bomb attacks in the Middle East": RPT-001 (VBIED attack in Mosul -- the ideal #1 result) is ranked #14 by keywords. RPT-006 (car-borne IED in Yemen -- ideal #2) is ranked #15.
- Query "homemade explosives from household chemicals": RPT-023 (TATP synthesis from nail polish remover, hair bleach -- ideal #1) is ranked #17 by keywords.
- Query "remote-controlled detonation methods": RPT-004 (RCIED with cell phone trigger -- ideal #1) is ranked #15 by keywords.

This pattern repeats for all 5 queries. Users are seeing irrelevant results first and missing critical intelligence.

**Why this matters now:** This is a take-home assignment for Codex. The deliverable demonstrates that a lightweight, CPU-only, offline cross-encoder re-ranker can solve the vocabulary mismatch problem for their production search system.

**If we do nothing:** The assignment is not submitted. No impact on existing production, but the opportunity to demonstrate the solution is lost.

## Success Criteria

1. The re-ranker produces NDCG@10 scores that demonstrate meaningful improvement over keyword-only ranking across all 5 queries.
2. The evaluate.py script runs end-to-end and produces a formatted table showing per-query NDCG@10 and Precision@5, plus averages.
3. The main.py demo runs successfully on a fresh Python 3.10+ environment after `pip install -r requirements.txt`, with no network access required after initial model download.
4. All three deliverables are present and complete: main.py, evaluate.py, WRITEUP.md.
5. The re-ranker processes each query's 20 candidates and returns a top-10 ranked list within 2-3 seconds on CPU.
6. Code is clean, readable, and well-structured with appropriate abstractions (per the 25% code quality evaluation weight).

## Acceptance Criteria

* Given a fresh Python 3.10+ virtual environment and the requirements.txt file
  When the user runs `pip install -r requirements.txt`
  Then all dependencies install successfully with no errors

* Given the installed environment and data files in data/
  When the user runs `python main.py`
  Then the script outputs a demo re-ranking for at least one query, showing the re-ordered top-10 report IDs with relevance scores

* Given the installed environment and data files in data/
  When the user runs `python evaluate.py`
  Then the script outputs a formatted table with NDCG@10 and Precision@5 for each of the 5 queries plus average scores

* Given the query "vehicle bomb attacks in the Middle East" and the 20 keyword results from keyword_results.json
  When the re-ranker processes this query
  Then RPT-001 (VBIED Mosul) and RPT-006 (car-borne IED Yemen) appear in the top 5 re-ranked results (they are ranked 14 and 15 by keywords but are the ideal #1 and #2)

* Given the query "homemade explosives from household chemicals" and the 20 keyword results
  When the re-ranker processes this query
  Then RPT-023 (TATP synthesis manual), RPT-009 (HMTD lab), and RPT-002 (TATP precursors) appear in the top 5 re-ranked results (they are ranked 17, 16, and 15 by keywords but are the ideal #1, #2, and #3)

* Given any of the 5 queries and their 20 candidates
  When the re-ranker processes the query on CPU
  Then processing completes within 3 seconds

* Given the Reranker class
  When instantiated and called with `rerank(query: str, candidates: list[str]) -> list[str]`
  Then it returns a list of exactly 10 report IDs ordered by semantic relevance

* Given the code repository
  When reviewed for production readiness
  Then the code includes error handling for missing data files, invalid inputs, and model loading failures

* Given the WRITEUP.md file
  When reviewed
  Then it covers all four required sections (Approach, Architecture, Trade-offs, What I'd do with more time) and does not exceed 1 page

* Given the evaluate.py script
  When it accesses data files
  Then ideal_rankings.json is only used by evaluate.py for scoring, never imported or referenced by main.py or the Reranker class

## Out of Scope

- FastAPI or any HTTP service wrapper (mentioned as future work in PRD)
- Fine-tuning the cross-encoder model on domain data (future work)
- Query expansion or synonym dictionaries (future work)
- GPU support or GPU-optimized inference paths
- Dense retrieval / bi-encoder first-stage replacement for Elasticsearch
- Expanding the candidate pool beyond top-20
- Saving evaluation results to file (console output only)
- Integration with actual Elasticsearch or any live search system
- UI or frontend for displaying results
- Docker containerization or deployment scripts
- CI/CD pipeline configuration
- Unit tests beyond the evaluation script (nice-to-have but not a deliverable)
- Handling queries not in the provided dataset (the 5 queries are the test set)
- Monorepo integration concerns (turborepo, pnpm) -- this is a standalone Python project living under apps/semantic-reranker/

## Open Questions

All open questions have been resolved from the PRD and assignment documentation. The PRD provides clear answers on:
- Model choice: cross-encoder/ms-marco-MiniLM-L-6-v2 (confirmed)
- Architecture: monolith module preferred (confirmed)
- Metrics: NDCG@10 primary, Precision@5 secondary (confirmed)
- Relevance scoring: graded by position in ideal_rankings (confirmed)
- Constraints: CPU-only, offline, Python 3.10+ (confirmed)
- Output format: rich-formatted console table (confirmed)
- Code structure: specified in PRD Section 5 (confirmed)

No open questions require user decision at this time.

## Recommendations

### For TL/DEV
- **Data characteristics:** The 30 reports have rich text in both `title` and `description` fields. The `description` field (2-4 sentences) is the primary semantic content. Consider concatenating title + description as the document text for cross-encoder scoring.
- **Subcategories field:** Reports also contain structured `subcategories` with taxonomy tags. Consider whether to include these in the text passed to the cross-encoder (they could help with domain terminology matching, but may also add noise).
- **Relevance scoring for NDCG:** The PRD specifies graded relevance: position 1 = score 10, position 2 = score 9, ..., position 10 = score 1, not in ideal list = score 0. This must be implemented exactly in evaluate.py.
- **Model caching:** The cross-encoder model will be downloaded on first run. Consider documenting this in the README and handling the case where the model cache directory is not writable.
- **Rich library:** The PRD specifies "rich-formatted console table" for evaluation output. The `rich` Python library is the standard choice for this.

### For QA
- The strongest signal of re-ranker quality is whether it promotes the "buried" relevant results. For each query, the keyword engine puts the most relevant reports at ranks 14-20, while the ideal ranking wants them at ranks 1-5. This inversion is the core test case.
- Verify that ideal_rankings.json is never imported by main.py or the Reranker class -- only by evaluate.py.
- Verify latency on CPU is within the 2-3 second budget per query.
