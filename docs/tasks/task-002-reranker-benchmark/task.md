---
id: task-002
title: Benchmark different re-ranking approaches
status: done
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

### Changes Made

1. **Extracted metrics** -- Moved `compute_ndcg` and `compute_precision` from `evaluate.py` to new `src/reranker/metrics.py`. Updated `evaluate.py` imports.

2. **Created `benchmark.py`** -- 15 experiments across 5 groups:
   - Text Composition (4): title-only, title+desc, title+desc+loc [baseline], title+desc+loc+subcats
   - Subcategory Scoring (4): category bonus beta=0.5/1.0/2.0, weighted subcat enrichment
   - Models (2): MiniLM-L-12-v2, bge-reranker-base
   - Best Combinations (2): bge-reranker-base+subcats, MiniLM-L-12+subcats
   - Hybrid Scoring (3): alpha=0.7/0.8/0.9

3. **Applied best configuration** -- Winner: `BAAI/bge-reranker-base` + subcategories in text
   - Updated `DEFAULT_MODEL` in `reranker.py` to `BAAI/bge-reranker-base`
   - Updated `get_report_text()` in `utils.py` to include flattened subcategories
   - Updated model name in `main.py` and `evaluate.py` headers

### Benchmark Results Summary

| Experiment | NDCG@10 | P@5 | dNDCG |
|---|---|---|---|
| title only | 0.6445 | 0.6800 | -0.0462 |
| title + desc | 0.6739 | 0.6800 | -0.0168 |
| title + desc + loc [BASELINE] | 0.6908 | 0.6800 | +0.0000 |
| title + desc + loc + subcats | 0.7403 | 0.7200 | +0.0495 |
| category bonus beta=0.5 | 0.6957 | 0.6800 | +0.0049 |
| category bonus beta=1.0 | 0.6961 | 0.7200 | +0.0053 |
| category bonus beta=2.0 | 0.6922 | 0.6800 | +0.0014 |
| weighted subcat enrichment | 0.7158 | 0.6800 | +0.0250 |
| MiniLM-L-12-v2 | 0.7401 | 0.6800 | +0.0494 |
| bge-reranker-base | 0.7452 | 0.7200 | +0.0545 |
| **bge-reranker-base + subcats** | **0.8283** | **0.8000** | **+0.1376** |
| MiniLM-L-12 + subcats | 0.7618 | 0.8000 | +0.0710 |
| hybrid alpha=0.7 | 0.5739 | 0.5600 | -0.1169 |
| hybrid alpha=0.8 | 0.5972 | 0.6400 | -0.0935 |
| hybrid alpha=0.9 | 0.6419 | 0.6800 | -0.0488 |

### Key Findings

1. **Winner: bge-reranker-base + subcategories** -- NDCG@10=0.8283 (+19.9% over baseline), P@5=0.8000 (+17.6%)
2. **Subcategories as text is very effective** -- adding flattened subcategories improves every model
3. **bge-reranker-base outperforms MiniLM models** -- even without subcats, it beats MiniLM-L-12-v2
4. **Hybrid scoring hurts** -- keyword score interpolation degrades results at all alpha values
5. **Category bonus is marginal** -- additive bonus provides <1% improvement
6. **Latency is acceptable** -- bge-reranker-base at ~1.1s per query, well within 2-3s budget

---

## QA Notes (QA)

**Verdict**: APPROVED

All acceptance criteria verified:
- Benchmark table shows all experiments with NDCG@10, P@5, delta vs baseline
- Text composition variants: 4 tested (title-only through title+desc+loc+subcats)
- Subcategory scoring: 4 variants tested (category bonus x3 + weighted enrichment)
- Models: 3 tested (MiniLM-L-6, MiniLM-L-12, bge-reranker-base)
- Hybrid scoring: 3 alpha values tested (0.7, 0.8, 0.9)
- Best configuration highlighted and applied as new default
- No regressions in evaluate.py or main.py

See `insights/qa-plan.md` for full verification details.
