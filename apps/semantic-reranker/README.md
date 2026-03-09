# Semantic Re-Ranker for Intelligence Report Search

A semantic re-ranking system that improves keyword search results using a cross-encoder transformer model. Takes the keyword engine's top-20 results and re-orders them by semantic relevance, returning the top 10.

## Prerequisites

- Python 3.10+
- Internet connection for first run (model download, ~80MB)

## Setup

```bash
cd apps/semantic-reranker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

> **Note:** The first run downloads the cross-encoder model (~80MB) from HuggingFace. Subsequent runs work fully offline using the cached model at `~/.cache/huggingface/`.

## Docker (Recommended)

Run everything with a single command -- no Python setup required:

```bash
# From the repository root:
docker-compose up --build
```

This builds the image, installs dependencies, and runs both `main.py` (demo) and `evaluate.py` (metrics).

### Run individual scripts

```bash
docker-compose run reranker python main.py            # Demo only
docker-compose run reranker python evaluate.py         # Evaluation only
docker-compose run reranker python benchmark.py        # Full benchmark (~10 min)
docker-compose run reranker python generate_report.py  # Generate HTML report
```

### Notes

- Each run downloads the cross-encoder model (~80MB) from HuggingFace. Requires internet.
- **Image size** is ~1.7GB (CPU-only PyTorch, no CUDA).
- The `Dockerfile` and `docker-compose.yml` are at the **repository root**, not inside `apps/semantic-reranker/`.

## Usage

### Demo — Re-rank all queries

```bash
python main.py
```

Shows re-ranked top-10 results for all 5 test queries with relevance scores and timing.

### Evaluation — Measure ranking quality

```bash
python evaluate.py
```

Compares re-ranked results against ideal rankings, reporting NDCG@10 and Precision@5 per query with keyword baseline comparison.

## Project Structure

```
apps/semantic-reranker/
├── data/
│   ├── reports.json              # 30 intelligence reports
│   ├── keyword_results.json      # 5 queries × 20 keyword results
│   └── ideal_rankings.json       # Ground truth (evaluation only)
├── src/
│   └── reranker/
│       ├── __init__.py           # Package exports
│       ├── reranker.py           # Reranker class (core logic)
│       ├── models.py             # Pydantic data models
│       └── utils.py              # Data loading helpers
├── main.py                       # Demo entry point
├── evaluate.py                   # Evaluation script
├── WRITEUP.md                    # Technical approach documentation
├── README.md                     # This file
└── requirements.txt              # Python dependencies
```

## Model

**`cross-encoder/ms-marco-MiniLM-L-6-v2`** — A lightweight cross-encoder (6 layers, ~22M parameters) trained on MS MARCO passage ranking. Scores query-document pairs jointly for semantic relevance. CPU-friendly, offline-capable after initial download.
