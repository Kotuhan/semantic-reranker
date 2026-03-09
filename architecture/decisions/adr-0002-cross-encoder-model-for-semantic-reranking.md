---
status: superseded-in-place
date: 2026-03-09
triggered-by: task-001
updated-by: task-002
---

# ADR-0002: Cross-Encoder Model for Semantic Re-Ranking

## Context and Problem Statement

The semantic re-ranker needs to re-score keyword search results by semantic relevance. The model must run on CPU, work offline after initial download, and process 20 candidates per query within 2-3 seconds. We needed to choose a scoring approach and specific model.

## Decision Drivers

- CPU-only inference required (no GPU)
- Latency budget of 2-3 seconds for 20 candidates per query
- Must bridge vocabulary mismatch (e.g., "vehicle bomb" vs. "VBIED")
- Offline operation after initial model download

## Considered Options

- Cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) via sentence-transformers
- Cross-encoder (`cross-encoder/ms-marco-MiniLM-L-12-v2`) via sentence-transformers
- Cross-encoder (`BAAI/bge-reranker-base`) via sentence-transformers
- Bi-encoder with cosine similarity (faster but less accurate for re-ranking)

## Decision Outcome

**Updated (task-002):** Chosen option: "Cross-encoder (`BAAI/bge-reranker-base`) via sentence-transformers", selected after systematic benchmark of 15 experiments. bge-reranker-base outperforms both MiniLM variants:

| Model | NDCG@10 | P@5 | Latency |
|---|---|---|---|
| MiniLM-L-6-v2 (original) | 0.6908 | 0.6800 | ~0.3s |
| MiniLM-L-12-v2 | 0.7401 | 0.6800 | ~0.3s |
| bge-reranker-base | 0.7452 | 0.7200 | ~1.1s |
| bge-reranker-base + subcats | 0.8283 | 0.8000 | ~1.1s |

### Consequences

- Good, because bge-reranker-base produces 3.8x NDCG improvement over keyword baseline (up from 3.1x)
- Good, because latency (~1.1s) is still well within 2-3s budget
- Good, because sentence-transformers CrossEncoder API is identical across all three models
- Bad, because the model is larger (~350MB vs ~80MB for MiniLM-L-6)
- Bad, because the model is general-domain, not tuned for intelligence/IED terminology
- Bad, because cross-encoders do not scale to large candidate pools (O(n) inference per query)

## More Information

- Model is downloaded on first run to `~/.cache/huggingface/` (~350MB)
- Document text composition: `title + description + location + flattened subcategories` (see ADR-0003)
- Benchmark data: `apps/semantic-reranker/benchmark.py` (15 experiments, reproducible)
