---
status: accepted
date: 2026-03-09
triggered-by: task-001
---

# ADR-0002: Cross-Encoder Model for Semantic Re-Ranking

## Context and Problem Statement

The semantic re-ranker needs to re-score keyword search results by semantic relevance. The model must run on CPU, work offline after initial download, and process 20 candidates per query within 2-3 seconds. We needed to choose a scoring approach and specific model.

## Decision Drivers

- CPU-only inference required (no GPU)
- Latency budget of 2-3 seconds for 20 candidates per query
- Must bridge vocabulary mismatch (e.g., "vehicle bomb" vs. "VBIED")
- Offline operation after initial model download
- Lightweight enough for a take-home assignment

## Considered Options

- Cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) via sentence-transformers
- Bi-encoder with cosine similarity (faster but less accurate for re-ranking)
- Raw `transformers` AutoModelForSequenceClassification (same model, more boilerplate)

## Decision Outcome

Chosen option: "Cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) via sentence-transformers", because cross-encoders jointly attend to query-document pairs producing higher quality relevance scores than bi-encoders, the MiniLM-L-6 variant is small enough for CPU (~80MB), and the sentence-transformers CrossEncoder wrapper handles tokenization, batching, and scoring with minimal code.

### Consequences

- Good, because cross-encoder produces 3.1x NDCG improvement over keyword baseline
- Good, because latency is well under budget (~0.3s per query for 20 candidates on CPU)
- Good, because sentence-transformers provides a clean API (single `model.predict()` call)
- Bad, because the model is general-domain (MS MARCO web search), not tuned for intelligence/IED terminology -- some edge cases remain
- Bad, because cross-encoders do not scale to large candidate pools (O(n) inference per query) -- acceptable for 20 candidates but would need bi-encoder first stage at scale

## More Information

- Model is downloaded on first run to `~/.cache/huggingface/` (~80MB)
- Document text composition: `title + ". " + description + " Location: " + country + ", " + city + "."`
- Subcategories excluded from scoring text (structured taxonomy tags add noise to the cross-encoder)
