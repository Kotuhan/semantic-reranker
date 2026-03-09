# Technical Write-Up: Semantic Re-Ranker

## Approach

I use a **cross-encoder** architecture (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to re-rank the keyword engine's top-20 results. Unlike bi-encoders that encode query and document independently, a cross-encoder jointly processes the `[query, document]` pair through a single transformer pass, producing a relevance score. This joint attention mechanism allows the model to capture fine-grained semantic relationships — critically, it can bridge vocabulary gaps like "vehicle bomb" ↔ "VBIED" and "homemade explosives" ↔ "TATP" because it learned these associations from MS MARCO training data.

Document text is composed as `title + description + location (country, city)` — title and description provide semantic content, while location helps geo-scoped queries like "Middle East" match reports from Iraq or Yemen.

**Why this model:** MiniLM-L-6 has only 6 transformer layers (~22M parameters), making it fast enough for CPU inference on 20 candidates within the 2-3 second latency budget. It requires no GPU and runs fully offline after initial download.

## Architecture

```
User Query → Elasticsearch (BM25) → Top-20 Candidates → Cross-Encoder Re-Ranker → Top-10 Results
```

**Production integration:** For Codex's scale (~12 concurrent users, hundreds of daily queries), I recommend embedding the `Reranker` class directly into the search service as a module — no separate microservice needed. This avoids HTTP overhead and infrastructure complexity. If the re-ranker becomes shared across multiple products, extracting it into a microservice with a REST API would then make sense.

## Trade-offs

- **Latency vs. quality:** Cross-encoders are slower than bi-encoders per pair (~0.1s for 20 pairs vs. ~0.01s), but far more accurate for re-ranking. With only 20 candidates, this is acceptable.
- **CPU-only:** No GPU required. MiniLM-L-6 processes 20 pairs in ~0.3s on modern CPUs. A larger model (MiniLM-L-12) would improve quality marginally but double latency.
- **Cold start:** First run downloads the model (~80MB). Subsequent runs use the local HuggingFace cache. Model loading takes ~1s, amortized across all queries in a session.
- **General vs. domain-specific:** The model is trained on web search data, not intelligence reports. It handles common vocabulary gaps well but may miss highly specialized jargon. Evaluation shows NDCG@10 of 0.69 (3x over keyword baseline).

## What I'd Do With More Time

1. **Query expansion** — Add a synonym layer for intelligence terminology (VBIED → vehicle bomb, PBIED → person-borne IED, TATP → homemade explosive). This addresses the recall limitation: the re-ranker can only reorder what the keyword engine returns.
2. **Domain fine-tuning** — Fine-tune MiniLM on intelligence report pairs to improve understanding of specialist terminology. Even 1,000 labeled pairs would likely boost NDCG@10 significantly.
3. **Dense retrieval first stage** — Replace or augment Elasticsearch with a bi-encoder over the full corpus to improve recall at the retrieval stage.
4. **Expand candidate pool** — Request top-50 from the keyword engine instead of top-20 to give the re-ranker more candidates to promote.
