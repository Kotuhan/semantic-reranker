# TL Design — task-002: Benchmark Re-Ranking Approaches

**Date**: 2026-03-09
**Estimated Effort**: 0.5 days (small, self-contained)
**Complexity**: Low-medium (variations on existing patterns, no new architecture)

## Technical Analysis

### Current State (from task-001)
- `Reranker` class in `src/reranker/reranker.py` uses `cross-encoder/ms-marco-MiniLM-L-6-v2`
- `get_report_text()` in `utils.py` composes: `title + description + Location: country, city`
- `evaluate.py` computes NDCG@10 and Precision@5 using `rich` tables
- Baseline NDCG@10: 0.6908, Precision@5: 0.6800
- Reports have `subcategories` dict with keys: Target, Organization, Attack, Component, Explosive, Operating

### Design Approach

Create a single `benchmark.py` script that defines experiment configurations declaratively, runs each through the existing evaluation pipeline, and produces a comparison table. Reuse existing `compute_ndcg`, `compute_precision` from `evaluate.py` by extracting them (or importing).

### Key Design Decisions

1. **Single file `benchmark.py`** -- all experiment logic in one script, following the pattern of `evaluate.py` and `main.py`
2. **Experiment as dataclass** -- each experiment is a config (name, model, text_composer, score_modifier)
3. **Text composers as functions** -- `(Report) -> str` callables for each text variant
4. **Score modifiers as functions** -- optional `(float, Report, str) -> float` for hybrid/category scoring
5. **Reuse evaluation functions** -- extract `compute_ndcg` and `compute_precision` into `utils.py` or import from `evaluate.py`

### Architecture

```
benchmark.py
  |
  |- defines Experiment dataclass (name, model_name, text_fn, score_fn, params)
  |- defines text composition functions:
  |    - title_only(report) -> str
  |    - title_desc(report) -> str
  |    - title_desc_loc(report) -> str  (current baseline)
  |    - title_desc_loc_subcats(report) -> str
  |    - title_desc_loc_weighted_subcats(report) -> str
  |
  |- defines score modifier functions:
  |    - category_bonus(score, report, query, beta) -> float
  |    - hybrid_alpha(semantic_score, keyword_score, alpha) -> float
  |
  |- builds experiment list (~15-20 experiments)
  |- for each experiment:
  |    - loads model (caches per model_name to avoid reloads)
  |    - runs all 5 queries
  |    - computes NDCG@10, Precision@5
  |    - stores results
  |
  |- outputs rich table with all experiments, delta vs baseline
  |- highlights best configuration
```

### Experiment Matrix

**Text compositions (4 variants, using baseline model):**
1. title only
2. title + description
3. title + description + location (BASELINE)
4. title + description + location + subcategories (flattened)

**Subcategory approaches (using baseline model, baseline text):**
5. category match bonus beta=0.5
6. category match bonus beta=1.0
7. category match bonus beta=2.0
8. weighted text enrichment (repeat Attack/Explosive subcats in text)

**Models (using baseline text composition):**
9. cross-encoder/ms-marco-MiniLM-L-12-v2
10. BAAI/bge-reranker-base

**Hybrid scoring (using baseline model+text):**
11. alpha=0.7 (semantic*0.7 + keyword*0.3)
12. alpha=0.8
13. alpha=0.9

Total: ~13 core experiments. Fast to run (5 queries x 20 candidates each).

### Category Match Bonus Implementation

For each report-query pair, count how many subcategory values match query terms:
```python
def count_category_matches(report: Report, query: str) -> int:
    query_lower = query.lower()
    count = 0
    for values in report.subcategories.values():
        for val in values:
            if val.lower() in query_lower or query_lower in val.lower():
                count += 1
    return count

final_score = semantic_score + beta * match_count
```

### Hybrid Scoring Implementation

Normalize keyword scores (rank-based or raw keyword_score from data), then:
```python
final_score = alpha * semantic_score + (1 - alpha) * normalized_keyword_score
```

Need to normalize both score types to [0,1] range via min-max within each query.

### Weighted Text Enrichment

Repeat high-value subcategory axes (Attack, Explosive, Target) in document text:
```python
def title_desc_loc_weighted_subcats(report: Report) -> str:
    base = f"{report.title}. {report.description} Location: {report.country}, {report.city}."
    # Append high-value subcategories with repetition for emphasis
    high_value_keys = ["Attack", "Explosive", "Target"]
    enrichment = []
    for key in high_value_keys:
        if key in report.subcategories:
            enrichment.extend(report.subcategories[key] * 2)  # repeat for weight
    if enrichment:
        base += " " + " ".join(enrichment)
    return base
```

### Model Caching

Models are large (~80-350MB). Cache loaded models by name:
```python
_model_cache: dict[str, CrossEncoder] = {}
def get_model(name: str) -> CrossEncoder:
    if name not in _model_cache:
        _model_cache[name] = CrossEncoder(name)
    return _model_cache[name]
```

### Output Format

Rich table with columns: Experiment | NDCG@10 | P@5 | Delta NDCG | Delta P@5 | Notes
- Delta computed vs baseline (experiment #3: title+desc+loc with MiniLM-L-6-v2)
- Best row highlighted with green bold
- Summary section at bottom with winner announcement

## Implementation Steps

1. **Extract evaluation functions** -- Move `compute_ndcg` and `compute_precision` from `evaluate.py` to `src/reranker/utils.py` (or a new `src/reranker/metrics.py`). Update `evaluate.py` imports. This avoids code duplication.

2. **Create `benchmark.py`** -- Main benchmark script with:
   - Experiment dataclass/TypedDict definition
   - All text composition functions
   - Category match bonus function
   - Hybrid scoring function
   - Experiment list definition
   - Model caching
   - Main loop: iterate experiments, compute metrics, collect results
   - Rich table output with delta vs baseline and best-config highlight

3. **Test run** -- Execute `benchmark.py` and verify all experiments produce valid results

4. **Update best config** -- Based on results, update `get_report_text()` and/or `Reranker` defaults if a better config is found (acceptance criteria: "best configuration applied as new default")

5. **Update CLAUDE.md** -- Update `apps/semantic-reranker/CLAUDE.md` with benchmark results and new baseline if changed

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| bge-reranker-base not downloaded | Low | Script will auto-download on first run; add clear error message |
| Score normalization edge cases | Low | Handle zero-range case (all same score) |
| Slow execution | Low | Only 5 queries x 20 candidates, even 3 models should be < 30s total |

## Test Strategy

- Run benchmark.py, verify table shows all expected experiments
- Verify baseline experiment matches existing evaluate.py output (NDCG@10 = 0.6908)
- Verify delta column is correct (experiment NDCG minus baseline NDCG)
- Verify best config is highlighted
- No unit tests needed -- this is a one-shot analysis script, verified by running it

## Open Questions

None -- user resolved all questions ("test everything").
