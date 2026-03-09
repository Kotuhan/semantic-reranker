---
status: superseded-in-place
date: 2026-03-09
triggered-by: task-001
updated-by: task-002
---

# ADR-0003: Document Text Composition for Cross-Encoder Scoring

## Context and Problem Statement

The cross-encoder scores (query, document_text) pairs. Each intelligence report has multiple fields: title, description, type, country, city, event_date, and subcategories. We needed to decide which fields to concatenate into the document text passed to the model.

## Decision Drivers

- Cross-encoder input length is limited by model context window (512 tokens)
- Title and description contain the richest natural language content
- Some queries are geo-specific (e.g., "Middle East") requiring location awareness
- Subcategories are structured taxonomy tags but contain domain-relevant terms (e.g., "Vehicle-Borne IED", "Ammonium Nitrate")

## Considered Options

- Title + description only
- Title + description + country + city (as location suffix)
- Title + description + location + subcategories (all fields)
- Title + description + location + weighted subcategories (repeat high-value axes)

## Decision Outcome

**Updated (task-002):** Chosen option: "Title + description + location + flattened subcategories", implemented as `title + ". " + description + " Location: " + country + ", " + city + "." + " Categories: " + comma-joined subcategory values + "."`.

Benchmark results showed subcategories significantly improve scoring across all models:

| Text Composition | NDCG@10 (bge-reranker-base) |
|---|---|
| title + desc + loc (original) | 0.7452 |
| title + desc + loc + subcats | 0.8283 (+11.1%) |

The original decision to exclude subcategories was based on the assumption they would add noise. Empirical testing proved the opposite -- subcategory terms like "Vehicle-Borne IED", "Ammonium Nitrate", "Military/Security Forces" provide strong domain-specific signals that help the cross-encoder bridge vocabulary gaps.

### Consequences

- Good, because subcategories provide +11.1% NDCG improvement with bge-reranker-base
- Good, because geo-queries still work (location suffix retained)
- Good, because approach is consistent across all models (helps MiniLM variants too)
- Neutral, because input is longer but still within 512-token context window for all reports tested

## More Information

- Implemented in `apps/semantic-reranker/src/reranker/utils.py` function `get_report_text()`
- Benchmark data: `apps/semantic-reranker/benchmark.py` experiments #3 vs #4 and #10 vs #11
- Subcategory keys in data: Target, Organization, Attack, Component, Explosive, Operating
