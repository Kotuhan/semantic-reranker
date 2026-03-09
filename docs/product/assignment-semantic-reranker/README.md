# Take-Home Assignment: Semantic Re-Ranker for Intelligence Report Search

## Background

You're joining the engineering team at Codex, a platform that indexes and searches a large corpus of intelligence reports covering terrorism, IEDs, explosive threats, and related security topics. Our current search engine uses keyword-based matching (BM25-style) to retrieve and rank results.

**The problem:** Keyword search frequently misses highly relevant reports due to vocabulary mismatch. For example:

- A query for "vehicle bomb" won't rank reports about "VBIEDs" or "car-borne IEDs" highly
- A query for "homemade explosives" won't surface reports about "TATP" or "HMTD" synthesis
- A query for "suicide attacks" won't match "self-detonation" or "PBIED" terminology

**Your task:** Build a semantic re-ranker that takes the keyword engine's top-20 results for a given query and re-orders them so that the most semantically relevant reports appear at the top.

## What You're Given

### `data/reports.json`

30 synthetic intelligence reports, each with:

- `id` — Unique report identifier (e.g., `RPT-001`)
- `title` — Report headline
- `description` — 2-4 sentence summary of the report content
- `type` — Report source type (`mobius`, `tgalert`, `hydra`, `info_item`, `al-khemia`)
- `country`, `city` — Geographic location
- `event_date` — Date of the event
- `subcategories` — Structured taxonomy tags (Target, Organization, Attack, Component, Explosive, Operating)

### `data/keyword_results.json`

5 search queries, each with 20 results pre-ranked by a simulated keyword engine. Each result includes:

- `rank` — Current keyword-based ranking (1-20)
- `report_id` — Reference to a report in `reports.json`
- `keyword_score` — Simulated BM25-style relevance score
- `match_reason` — Explanation of why the keyword engine ranked it here

### `data/ideal_rankings.json`

Ground-truth "ideal" top-10 rankings for each query, with rationales. **Use this for self-evaluation only** — your re-ranker should work without access to these labels.

## Deliverables

### 1. Re-Ranking Implementation

Build a Python service/script that:

- Accepts a search query and a list of candidate report IDs (the keyword engine's top-20)
- Returns a re-ranked list of the top-10 most relevant reports
- Uses semantic understanding to bridge vocabulary gaps between queries and report content

### 2. Evaluation Script

Write a script that:

- Runs your re-ranker against all 5 queries
- Compares your output to `ideal_rankings.json`
- Reports **NDCG@10** (Normalized Discounted Cumulative Gain) and **Precision@5** for each query
- Reports average scores across all queries

### 3. Brief Write-Up (max 1 page)

A short document covering:

- **Approach:** What model/technique did you use and why?
- **Architecture:** How would this integrate into a production search pipeline?
- **Trade-offs:** Latency vs. quality, cost considerations, cold-start handling
- **What you'd do with more time:** Potential improvements, fine-tuning strategies, etc.

## Constraints & Guidelines

- **Language:** Python 3.10+
- **Dependencies:** Use any open-source libraries/models. If using an external API (e.g., OpenAI, Cohere), include a fallback that works offline with a local model.
- **Time budget:** ~3-5 hours. We value thoughtful design over exhaustive optimization.
- **No training on the test data.** Your re-ranker should generalize — don't overfit to these 5 queries.
- Include a `requirements.txt` or `pyproject.toml` with all dependencies.
- Include clear setup and run instructions.

## Evaluation Criteria

We'll evaluate your submission on:

| Criteria                 | Weight | Description                                                              |
| ------------------------ | ------ | ------------------------------------------------------------------------ |
| **Ranking Quality**      | 30%    | How well does your re-ranker surface relevant results? (NDCG@10 scores)  |
| **Code Quality**         | 25%    | Clean, readable, well-structured code with appropriate abstractions      |
| **Approach & Reasoning** | 25%    | Sound technical choices, understanding of the problem space              |
| **Production Readiness** | 20%    | Error handling, configuration, documentation, scalability considerations |

## Getting Started

```bash
# Clone and enter the directory
cd assignment-semantic-reranker

# Set up your environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies (yours)
pip install -r requirements.txt

# Run your re-ranker
python reranker.py

# Run evaluation
python evaluate.py
```

## Submission

- Push your solution to a Git repository (GitHub, GitLab, etc.)
- Include all source files, your write-up, and the evaluation output
- Do **not** include the `data/ideal_rankings.json` in your solution's runtime path — it's for self-evaluation only
- Send us the repository link

## Questions?

If anything is unclear, email us. We'd rather you ask than make wrong assumptions.

---

**Good luck!** We're excited to see your approach.
