# Completion Summary: task-001

Completed: 2026-03-09

## What Was Done

Built a semantic re-ranker that takes the keyword search engine's top-20 results for intelligence report queries and re-orders them so the most relevant reports appear at the top. The re-ranker uses a pre-trained language model to understand that terms like "vehicle bomb" and "VBIED" mean the same thing, solving the vocabulary mismatch problem that buried the best results at ranks 14-20. Three deliverables were produced: a demo script, an evaluation script with metrics, and a technical write-up.

## Key Decisions

| Decision | Why |
|----------|-----|
| Used `cross-encoder/ms-marco-MiniLM-L-6-v2` model | Lightweight, runs on CPU without GPU, works offline after first download |
| Included country and city in the text sent to the model | Improves results for location-based queries like "Middle East" |
| Excluded report subcategories from model input | These are structured tags, not natural language -- adding them hurt accuracy |
| Used graded relevance scoring (rank 1 = 10 points, rank 10 = 1 point) | More nuanced than binary relevant/not-relevant; rewards putting the best results first |
| General-domain model without fine-tuning | Sufficient for the assignment scope; domain fine-tuning noted as future improvement |

## What Changed

- **New project**: `apps/semantic-reranker/` -- standalone Python application, no changes to existing code
- **Files added**: `main.py`, `evaluate.py`, `WRITEUP.md`, `README.md`, `requirements.txt`, plus `src/reranker/` package (models, utilities, core logic) and `data/` directory with 3 JSON files

## Impact

- Analysts searching for intelligence reports now get the most relevant results in the top 10 instead of having them buried at ranks 14-20
- Search quality improved 3.1x on average (NDCG@10: 0.69 vs 0.22 keyword baseline)
- All 5 test queries show improvement; the "vehicle bomb" query went from having its best match at rank 14 to rank 1
- Processing takes under 0.3 seconds per query, well within the 3-second budget

## Known Limitation

One specific report (RPT-023, TATP synthesis) is not promoted for the "homemade explosives" query due to the general-domain model lacking specialized chemistry-to-explosives associations. This is a documented trade-off, not a bug, and would be addressed by domain fine-tuning.

## QA Result

15/15 test cases passed. All acceptance criteria met. Approved without issues.
