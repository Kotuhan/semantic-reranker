---
status: accepted
date: 2026-03-09
triggered-by: task-001
---

# ADR-0003: Document Text Composition for Cross-Encoder Scoring

## Context and Problem Statement

The cross-encoder scores (query, document_text) pairs. Each intelligence report has multiple fields: title, description, type, country, city, event_date, and subcategories. We needed to decide which fields to concatenate into the document text passed to the model.

## Decision Drivers

- Cross-encoder input length is limited by model context window (512 tokens for MiniLM)
- Title and description contain the richest natural language content
- Some queries are geo-specific (e.g., "Middle East") requiring location awareness
- Subcategories are structured taxonomy tags, not natural language prose

## Considered Options

- Title + description only
- Title + description + country + city (as location suffix)
- Title + description + subcategories + location (all fields)

## Decision Outcome

Chosen option: "Title + description + country + city (as location suffix)", implemented as `f"{report.title}. {report.description} Location: {report.country}, {report.city}."`. This includes the semantic-rich fields plus location context for geo-queries, while excluding subcategories that would add noise.

### Consequences

- Good, because geo-queries like "vehicle bomb attacks in the Middle East" correctly match reports in Iraq, Yemen, etc.
- Good, because subcategory exclusion avoids polluting semantic signal with taxonomy codes
- Bad, because some niche queries might benefit from subcategory terms -- but empirical results show strong NDCG without them

## More Information

- Implemented in `apps/semantic-reranker/src/reranker/utils.py` function `get_report_text()`
- The location is appended as a natural-language suffix ("Location: Iraq, Mosul.") so the cross-encoder can process it semantically rather than as raw metadata
