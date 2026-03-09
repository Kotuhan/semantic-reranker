# PO Analysis — task-002: Benchmark Re-Ranking Approaches

**Date**: 2026-03-09
**Status**: APPROVED (pre-filled by user, validated by director)

## Summary

User provided complete PO sections during initial discussion. All open questions were resolved: "test everything" -- all models, all text compositions, all subcategory approaches, all hybrid scoring variants.

## Validated Sections

### Problem Statement
Task-001 delivered a working re-ranker with one fixed config. Need systematic comparison of alternatives.

### Success Criteria
- Single `benchmark.py` command produces comparison table
- Clear winner identified with data
- Best configuration applied as new default

### Acceptance Criteria (7 scenarios)
1. Benchmark table with NDCG@10, Precision@5, delta vs baseline
2. Text composition variants: title-only, title+desc, title+desc+loc, title+desc+loc+subcategories
3. Subcategory scoring: category match bonus (beta=0.5,1.0,2.0), weighted text enrichment
4. Models: MiniLM-L-6-v2 (baseline), MiniLM-L-12-v2, bge-reranker-base
5. Hybrid scoring: alpha=0.7, 0.8, 0.9
6. Best config highlighted in results

### Out of Scope
Domain fine-tuning, query expansion, dense retrieval, GPU inference, changing evaluation metrics.

## Open Questions Resolution
All resolved by user: "test everything" -- no outstanding questions.
