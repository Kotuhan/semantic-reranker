# Semantic Re-Ranker — Approach & Findings

## Where I Started

When I first read the assignment, I didn't jump straight to code. The problem statement was clear — vocabulary mismatch between queries and intelligence reports — but I had several open questions that would fundamentally change the architecture before writing a single line.

So I asked.

The answers shaped everything:

- **Users are intelligence analysts and EOD technicians** — non-technical, freeform search, tolerant of 2–3 second latency
- **~12 concurrent users, hundreds of queries per day** — low load, no need for complex scaling
- **CPU only in production** — eliminates large models and GPU-dependent approaches
- **No external API budget** — Cohere Rerank, OpenAI — off the table
- **Offline is a hard production requirement** — not just an exercise constraint

This ruled out three of the four standard approaches immediately. LLM-based reranking (Cohere, GPT) — gone. Large cross-encoders — gone. Hybrid cloud/local fallback — unnecessary complexity.

What remained: a lightweight cross-encoder, fully self-hosted, CPU-friendly, offline by design.

---

## The Architecture Decision

Before choosing a model, I thought about where this sits in the pipeline:

```
User query → Elasticsearch/BM25 → top-20 candidates → re-ranker → top-10
```

The re-ranker doesn't need to search — that's already done. It only needs to re-order 20 documents. This is important because cross-encoders are too slow to run against an entire corpus, but 20 documents at 2–3 seconds is perfectly acceptable.

I also considered whether this should be a microservice or a module inside the existing search service. Given the load (~12 concurrent users), a microservice adds latency and operational overhead with no real benefit. A module is the pragmatic choice — with the caveat that a microservice makes sense if the re-ranker eventually becomes a shared component across multiple products.

The core abstraction is simple: a `Reranker` class with a `rerank(query, candidates)` method. Clean, testable, importable by both `evaluate.py` and any future HTTP wrapper.

---

## The Benchmarking Approach

I didn't want to just pick a model and submit. I wanted to understand *why* things work — and what doesn't.

I structured 15 experiments across 5 hypothesis categories:

**Text Composition** — How much context should I feed the model?
**Model Selection** — Does architecture matter more than size?
**Subcategory Scoring** — Can structured metadata boost relevance signals?
**Hybrid Scoring** — Does blending keyword + semantic scores help?
**Best Combinations** — What happens when I combine winning components?

Each experiment had a theory, a prediction, and a verdict.

---

## What I Found

### The biggest win: subcategories as text

Adding flattened subcategory tags (Target, Organization, Attack, Component, Explosive) to the document text gave a consistent **+5–14% NDCG lift** across all models. The taxonomy that the reports already had was essentially a free semantic signal — I just needed to include it in the input text.

### Architecture beats parameter count

`bge-reranker-base` outperformed `MiniLM-L-12` despite similar size. Cross-encoder architecture designed specifically for re-ranking matters more than just having more layers. This pushed me toward BGE as the primary model.

### The counterintuitive finding: hybrid scoring made things worse

I hypothesized that blending the keyword engine's BM25 scores with semantic scores would combine the best of both worlds. It didn't. At every alpha value tested (0.7, 0.8, 0.9), hybrid scoring degraded results — sometimes significantly.

The reason: the keyword scores weren't adding signal, they were adding noise. The cross-encoder already captures lexical overlap as part of its attention mechanism. Reintroducing raw BM25 scores pulled the ranking back toward keyword matching — exactly the problem we were trying to solve.

**Verdict: rejected.**

### The weak spot: geographic queries

Q1 ("vehicle bomb attacks in the Middle East") was the hardest query across every configuration, including the best one (NDCG: 0.62 vs. 0.91 for other queries). Geographic specificity in freeform queries is a known limitation — the model has no special handling for location disambiguation. This would be the first thing I'd address with more time.

---

## Final Configuration

**Model:** `BAAI/bge-reranker-base`
**Document text:** title + description + location + flattened subcategories
**Latency:** ~1.07 seconds for 20 documents on CPU
**NDCG@10:** 0.8283 (+19.9% over baseline)
**Precision@5:** 0.80

---

## What I'd Do With More Time

**Query expansion to fix recall failures.** The re-ranker can only work with what the keyword engine returns. If a relevant document doesn't appear in the top-20 at all, re-ranking can't surface it. The right fix is upstream: expand queries using intelligence domain synonyms ("vehicle bomb" → "VBIED, car-borne IED, CBIED") or LLM-based query rewriting. This addresses the root cause rather than optimizing the re-ranking step.

**Domain fine-tuning.** GPU is available for pretraining. Fine-tuning `bge-reranker-base` on intelligence report pairs with human relevance judgments would likely push NDCG significantly beyond 0.83 — the model currently has no exposure to this domain's specific terminology.

**Expand the candidate pool.** Requesting top-50 instead of top-20 from Elasticsearch costs little at retrieval time but meaningfully improves recall. More candidates means fewer relevant documents missed before re-ranking even begins.

---

## On the Benchmark Report

The full results — all 15 experiments, per-query heatmap, quality vs. latency scatter, and theory verdicts — are available at:

**[https://kotuhan.github.io/semantic-reranker/report.html](https://kotuhan.github.io/semantic-reranker/report.html)**