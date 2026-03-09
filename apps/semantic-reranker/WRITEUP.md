# Technical Write-Up: Semantic Re-Ranker

## Approach

I use a **cross-encoder** architecture (`BAAI/bge-reranker-base`) to re-rank the keyword engine's top-20 results. Unlike bi-encoders that encode query and document independently, a cross-encoder jointly processes the `[query, document]` pair through a single transformer pass, producing a relevance score. This joint attention mechanism allows the model to capture fine-grained semantic relationships — critically, it can bridge vocabulary gaps like "vehicle bomb" ↔ "VBIED" and "homemade explosives" ↔ "TATP".

Document text is composed as `title + description + location (country, city) + flattened subcategories`. Title and description provide semantic content, location helps geo-scoped queries, and subcategories (Target, Organization, Attack, Component, Explosive, Operating) provide structured domain terminology that the model can match against query terms.

**Why this model:** I benchmarked three cross-encoders (MiniLM-L-6, MiniLM-L-12, bge-reranker-base) across multiple text compositions. bge-reranker-base delivered the best NDCG@10 (0.83 vs 0.69 for MiniLM-L-6) while staying within the CPU latency budget (~1.1s for 20 candidates). It runs fully offline after initial download.

## Architecture

```
User Query → Elasticsearch (BM25) → Top-20 Candidates → Cross-Encoder Re-Ranker → Top-10 Results
```

**Production integration:** For Codex's scale (~12 concurrent users, hundreds of daily queries), I recommend embedding the `Reranker` class directly into the search service as a module — no separate microservice needed. This avoids HTTP overhead and infrastructure complexity. If the re-ranker becomes shared across multiple products, extracting it into a microservice with a REST API would then make sense.

## Trade-offs

- **Latency vs. quality:** Cross-encoders are slower than bi-encoders per pair (~0.1s for 20 pairs vs. ~0.01s), but far more accurate for re-ranking. With only 20 candidates, this is acceptable. bge-reranker-base is ~3x slower than MiniLM-L-6 but the quality gain (+19.9% NDCG) justifies it.
- **CPU-only:** No GPU required. bge-reranker-base processes 20 pairs in ~1.1s on modern CPUs, well within the 2-3s budget.
- **Cold start:** First run downloads the model (~350MB). Subsequent runs use the local HuggingFace cache. Model loading takes ~2s, amortized across all queries in a session.
- **General vs. domain-specific:** The model is trained on general search data, not intelligence reports. Including subcategories as text partially bridges this gap. Evaluation shows NDCG@10 of 0.83 (3.8x over keyword baseline).

## Benchmark: Theories Tested

I built a benchmark harness (`benchmark.py`) to systematically compare approaches. Here are the theories I tested and what I found:

1. **"More text = better understanding"** — Does adding location and subcategories to document text help the model? **Yes.** Adding location gave a small boost for geo-queries. Adding flattened subcategories (e.g., "Target: Military. Attack: Vehicle-Borne IED. Explosive: Ammonium Nitrate") gave a significant +5-14% NDCG lift across all models — the structured domain terminology gives the model vocabulary it wouldn't otherwise see.

2. **"A bigger model scores better"** — Does MiniLM-L-12 (12 layers) beat MiniLM-L-6 (6 layers)? And does bge-reranker-base beat both? **Partially.** L-12 offered marginal improvement over L-6. bge-reranker-base was the clear winner — a different architecture and training approach mattered more than just adding layers.

3. **"Hybrid scoring combines the best of both worlds"** — Does blending keyword scores with semantic scores (`α * semantic + (1-α) * keyword`) improve results? **No.** Hybrid scoring degraded results at every alpha value tested (0.7, 0.8, 0.9). The keyword scores added noise rather than signal — the semantic model already captures what keywords measure, plus more.

4. **"Structured metadata matching helps"** — Does adding a category-match bonus (counting subcategory overlaps between query terms and report tags) improve scoring? **Barely.** Less than 1% improvement — not worth the added complexity. The cross-encoder already picks up on these associations through the flattened text.

5. **"Repeating important fields amplifies their signal"** — Does duplicating high-value subcategory axes (Explosive, Attack) in the document text boost relevance? **No meaningful effect.** The cross-encoder's attention mechanism doesn't benefit from repetition the way a bag-of-words model would.

## What I'd Do With More Time

1. **Query expansion** — Add a synonym layer for intelligence terminology (VBIED → vehicle bomb, PBIED → person-borne IED, TATP → homemade explosive). This addresses the recall limitation: the re-ranker can only reorder what the keyword engine returns.
2. **Domain fine-tuning** — Fine-tune MiniLM on intelligence report pairs to improve understanding of specialist terminology. Even 1,000 labeled pairs would likely boost NDCG@10 significantly.
3. **Dense retrieval first stage** — Replace or augment Elasticsearch with a bi-encoder over the full corpus to improve recall at the retrieval stage.
4. **Expand candidate pool** — Request top-50 from the keyword engine instead of top-20 to give the re-ranker more candidates to promote.
