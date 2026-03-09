---
id: task-002
title: Benchmark different re-ranking approaches
status: backlog
priority: high
dependencies: [task-001]
created_at: 2026-03-09
---

# Benchmark different re-ranking approaches

## Problem (PO)

Task-001 delivered a working re-ranker with one fixed configuration (MiniLM-L-6, title+desc+location). We don't know if this is the best approach — there may be easy wins from different text compositions, models, or scoring strategies. We need a systematic way to compare alternatives and pick the best one.

## Success Criteria (PO)

* A single `benchmark.py` command produces a comparison table of all experiments
* Clear winner identified with data backing the decision
* Best configuration applied as the new default

## Acceptance Criteria (PO)

* Given the benchmark script exists
  When `python benchmark.py` is run
  Then a table shows NDCG@10, Precision@5, and delta vs baseline for each experiment

* Given multiple text composition variants are defined
  When benchmark runs
  Then at least these variants are compared:
    - title only
    - title + description (no location)
    - title + description + location (current baseline)
    - title + description + location + subcategories (flattened as text)

* Given subcategory-based scoring variants are defined
  When benchmark runs
  Then at least these variants are compared:
    - category match bonus: `final = semantic + β * category_match_count` (β=0.5, 1.0, 2.0)
    - weighted text enrichment: repeat high-value subcategory axes (Explosive, Attack) in document text

* Given multiple models are defined
  When benchmark runs
  Then at least these models are compared:
    - `cross-encoder/ms-marco-MiniLM-L-6-v2` (current)
    - `cross-encoder/ms-marco-MiniLM-L-12-v2`
    - `BAAI/bge-reranker-base`

* Given hybrid scoring is implemented
  When benchmark runs
  Then at least α=0.7, 0.8, 0.9 are compared

* Given all experiments complete
  When results are displayed
  Then the best configuration is highlighted

## Out of Scope (PO)

* Domain fine-tuning (needs labeled data, separate effort)
* Query expansion / synonym dictionaries (separate task)
* Dense retrieval / bi-encoder first stage
* GPU inference
* Changing the evaluation metrics themselves

## Open Questions (PO)

_Resolved: test all models including bge-reranker-base, test all subcategory approaches._

---

## Technical Notes (TL)

_To be filled by TL agent_

## Implementation Steps (TL)

_To be filled by TL agent_

---

## Implementation Log (DEV)

_Pending_

---

## QA Notes (QA)

_Pending_
