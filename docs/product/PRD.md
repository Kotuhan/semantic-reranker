# PRD: Semantic Re-Ranker for Intelligence Report Search
> Take-home assignment — Codex

---

## 1. Context

Codex is a platform that indexes and searches intelligence reports covering terrorism, IEDs, and explosive threats. The current keyword-based engine (BM25/Elasticsearch) suffers from **vocabulary mismatch** — it cannot match semantically equivalent terms like "vehicle bomb" ↔ "VBIED", "homemade explosives" ↔ "TATP", "suicide attack" ↔ "PBIED".

### Users
- Intelligence analysts
- EOD Technicians
- Non-technical users, freeform text search

### Production constraints (confirmed with client)
| Parameter | Value |
|-----------|-------|
| Acceptable latency | 2–3 seconds per search |
| Daily query volume | Hundreds, ~12 simultaneous |
| GPU in production | ❌ CPU only |
| External API budget | ❌ None |
| Offline requirement | ✅ Hard requirement (both exercise and production) |

---

## 2. Problem Statement

The keyword engine returns top-20 candidates but ranks them poorly due to vocabulary gaps. A semantic re-ranker must **re-order** these 20 candidates so the most semantically relevant reports appear at the top.

> **Important constraint:** The re-ranker only works with what the keyword engine returns. If a relevant document is not in the top-20, the re-ranker cannot surface it. This is a known limitation — see [Section 8: Future Work](#8-future-work).

---

## 3. Deliverables

### 3.1 Re-Ranking Implementation
- Python class `Reranker` with method `rerank(query: str, candidates: list[str]) -> list[str]`
- Accepts a search query and list of 20 candidate report IDs
- Returns re-ranked list of top-10 most relevant report IDs
- Entry point: `main.py` for demo run

### 3.2 Evaluation Script
- File: `evaluate.py`
- Runs re-ranker against all 5 queries from `keyword_results.json`
- Compares output to `ideal_rankings.json`
- Reports per-query and average scores
- Output: rich-formatted table in console

Metrics:
- **NDCG@10** — primary metric
- **Precision@5** — secondary metric

### 3.3 Write-Up
- File: `WRITEUP.md`
- Max 1 page
- Sections: Approach, Architecture, Trade-offs, What I'd do with more time

---

## 4. Technical Approach

### Model Selection
**`cross-encoder/ms-marco-MiniLM-L-6-v2`**

| Criteria | Decision |
|----------|----------|
| CPU only in production | ✅ MiniLM is lightweight enough |
| Offline hard requirement | ✅ Fully self-hosted, no API calls |
| Latency budget 2–3s | ✅ Cross-encoder on 20 docs fits comfortably |
| Semantic understanding | ✅ Cross-encoder sees query + doc together |

### Why Cross-Encoder over alternatives

| Approach | Verdict | Reason |
|----------|---------|--------|
| Bi-encoder | ❌ Skipped | Less accurate, query and doc don't interact |
| Cross-encoder | ✅ **Selected** | Best quality for re-ranking small candidate set |
| Bi→Cross pipeline | ❌ Not needed | First stage already done by Elasticsearch |
| LLM-based (Cohere, GPT) | ❌ Eliminated | No API budget, no GPU |

### How it works
```
user query
    ↓
Elasticsearch/BM25  →  top-20 candidates
                              ↓
                    cross-encoder scores each
                    [query + doc] → relevance score
                              ↓
                         top-10 re-ranked
                              ↓
                           user sees results
```

---

## 5. Architecture

### Integration options (both discussed in WRITEUP.md)

**Option A — Module inside monolith:**
```
search service → imports Reranker class directly → returns results
```
- ✅ Less latency (no HTTP roundtrip)
- ✅ Less infrastructure
- ❌ Cannot scale re-ranker independently

**Option B — Microservice:**
```
search service → HTTP → re-ranker service → response
```
- ✅ Independent scaling and deployment
- ❌ Adds latency and operational complexity
- ❌ Overkill for ~12 concurrent users

> **Decision for write-up:** Present both options with trade-offs. Given the load (~12 concurrent), monolith module is the pragmatic choice. Microservice makes sense if the re-ranker becomes a shared service across multiple products.

### Code architecture
```
assignment-semantic-reranker/
├── data/
│   ├── reports.json
│   ├── keyword_results.json
│   └── ideal_rankings.json        # self-evaluation only, not in runtime path
├── src/
│   └── reranker/
│       ├── __init__.py
│       ├── reranker.py            # Reranker class — core logic
│       ├── models.py              # Pydantic data models
│       └── utils.py               # data loading, helpers
├── evaluate.py                    # evaluation script
├── main.py                        # demo entry point
├── WRITEUP.md
├── requirements.txt
└── README.md
```

---

## 6. Evaluation Design

### Metrics
| Metric | Description |
|--------|-------------|
| NDCG@10 | Primary — measures ranking quality across top-10 |
| Precision@5 | Secondary — measures accuracy in top-5 |

### Relevance scoring
**Graded relevance** based on position in `ideal_rankings.json`:
```
position 1  → score 10
position 2  → score 9
...
position 10 → score 1
not in list → score 0
```

### Output format
Rich-formatted console table:

```
┌─────────────────────────┬──────────┬───────────────┐
│ Query                   │ NDCG@10  │ Precision@5   │
├─────────────────────────┼──────────┼───────────────┤
│ vehicle bomb            │ 0.87     │ 0.80          │
│ homemade explosives     │ 0.79     │ 0.60          │
│ ...                     │ ...      │ ...           │
├─────────────────────────┼──────────┼───────────────┤
│ Average                 │ 0.83     │ 0.72          │
└─────────────────────────┴──────────┴───────────────┘
```

---

## 7. Assumptions & Decisions Log

| # | Assumption | Rationale |
|---|------------|-----------|
| 1 | Graded relevance for NDCG | Position in ideal_rankings implies importance, binary would hide ranking errors |
| 2 | `ideal_rankings.json` not in runtime path | As specified in assignment — self-evaluation only |
| 3 | Cross-encoder as single-stage re-ranker | CPU-only, offline constraints eliminate all other options |
| 4 | No fine-tuning on test data | Assignment explicitly forbids overfitting to 5 queries |
| 5 | Monolith module preferred over microservice | Load (~12 concurrent) doesn't justify microservice overhead |

---

## 8. Future Work (for WRITEUP.md)

### Query Expansion
Addresses **recall failure** — the fundamental limitation of re-ranking:
> If a relevant document is not in the keyword engine's top-20, the re-ranker cannot surface it.

Solutions:
- Synonym dictionary for intelligence terminology (VBIED, PBIED, TATP etc.)
- LLM query rewriting: *"expand this query using terms common in intelligence reports"*
- HyDE (Hypothetical Document Embedding)

### Domain Fine-Tuning
GPU available for pretraining (confirmed). Could fine-tune `ms-marco-MiniLM` on intelligence domain data to improve understanding of specialist terminology.

### Dense Retrieval (Bi-Encoder) for First Stage
Replace or augment Elasticsearch with a bi-encoder over the full 19k corpus. Improves recall at the retrieval stage, not just re-ranking quality.

### Expand Candidate Pool
Request top-50 instead of top-20 from keyword engine. More candidates = better recall for re-ranker, small latency cost.

---

## 9. Constraints Checklist

| Requirement | Status |
|-------------|--------|
| Python 3.10+ | ✅ |
| Works offline | ✅ |
| No training on test data | ✅ |
| requirements.txt included | ✅ |
| Setup and run instructions in README | ✅ |
| ideal_rankings.json not in runtime path | ✅ |
| NDCG@10 reported | ✅ |
| Precision@5 reported | ✅ |
| Average scores reported | ✅ |
| Write-up max 1 page | ✅ |

---

## 10. Out of Scope

- FastAPI wrapper (mentioned as optional future improvement in WRITEUP.md)
- Fine-tuning implementation (mentioned in WRITEUP.md as future work)
- Query expansion (mentioned in WRITEUP.md as future work)
- Saving evaluation results to file
