# Architecture Overview

<!-- This is a living document. Update as the system evolves. -->

## System Components

| Component | Location | Type | Tech Stack | Status |
|-----------|----------|------|------------|--------|
| Semantic Re-Ranker | `apps/semantic-reranker/` | Standalone Python app | Python 3.10+, sentence-transformers, Pydantic, rich | Implemented (task-001) |

### Semantic Re-Ranker

A standalone Python application that re-ranks keyword search results using a cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-6-v2`). Takes 20 keyword candidates per query and returns a top-10 list ordered by semantic relevance. Not integrated with the monorepo toolchain (Turborepo/pnpm).

**Key characteristics:**
- CPU-only inference, offline after initial model download (~80MB)
- Latency: ~0.3s per query for 20 candidates
- NDCG@10 improvement: 3.1x over keyword baseline
- Self-contained with own virtualenv and requirements.txt

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Monorepo | Turborepo + pnpm workspaces | Node.js/TypeScript projects |
| ML/Re-ranking | Python 3.10+, sentence-transformers, PyTorch | Standalone, not in monorepo toolchain |
| Data validation | Pydantic v2 | Used in semantic-reranker |
| Console output | rich | Used in semantic-reranker |

## Module Inventory

| Module | Path | Responsibility | Depends On | ADR |
|--------|------|---------------|------------|-----|
| reranker (package) | `apps/semantic-reranker/src/reranker/` | Cross-encoder scoring, data models, data loading | sentence-transformers, Pydantic | ADR-0001, ADR-0002, ADR-0003 |
| main.py | `apps/semantic-reranker/main.py` | Demo entry point -- re-ranks all 5 queries, rich table output | reranker package | -- |
| evaluate.py | `apps/semantic-reranker/evaluate.py` | NDCG@10 and Precision@5 evaluation against ground truth | reranker package, ideal_rankings.json | -- |

## Security Architecture

No authentication, authorization, or network services. The semantic re-ranker is a local CLI tool processing static JSON data files.

## Known Limitations

- **No monorepo integration for Python apps**: `apps/semantic-reranker/` is not included in `pnpm dev/build/test/lint` commands. Must be run separately with its own Python virtualenv. (per ADR-0001)
- **General-domain model**: The cross-encoder is trained on MS MARCO web search data, not intelligence domain terminology. Some vocabulary gaps remain for highly specialized terms. Domain fine-tuning would address this. (per ADR-0002)
- **Relative path dependency**: Scripts must be run from `apps/semantic-reranker/` directory due to `sys.path.insert(0, "src")` and relative data paths.
- **No unit test framework**: Evaluation script (`evaluate.py`) serves as the verification mechanism. No pytest or unittest integration.
