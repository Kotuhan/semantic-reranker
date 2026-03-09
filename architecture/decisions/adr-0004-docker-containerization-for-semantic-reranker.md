---
status: accepted
date: 2026-03-09
triggered-by: task-003
---

# ADR-0004: Docker Containerization for Semantic Re-Ranker

## Context and Problem Statement

The semantic re-ranker requires Python 3.12, PyTorch, sentence-transformers, and a ~350MB HuggingFace model. Setting up this environment manually is error-prone for reviewers evaluating the project. We needed a way to provide a reproducible, zero-configuration execution environment.

## Decision Drivers

- Reviewers should be able to run the app with a single command, without Python/venv setup
- The app is CPU-only and has no network service requirements (per ADR-0002)
- The monorepo contains non-Python artifacts that should not bloat the Docker image
- PyTorch's CPU-only variant is significantly smaller than the default GPU-capable package

## Considered Options

- Dockerfile inside `apps/semantic-reranker/` with local build context
- Dockerfile at repo root with selective COPY from `apps/semantic-reranker/`
- No Docker -- rely on venv setup instructions only

## Decision Outcome

Chosen option: "Dockerfile at repo root with selective COPY", because the monorepo structure requires the build context to be the repo root to access `apps/semantic-reranker/`, and placing the Dockerfile at root makes `docker-compose build` work without custom context overrides. A `.dockerignore` excludes all non-reranker files (Node.js, docs, architecture, etc.) to keep the build context small.

Key implementation details:
- **Base image**: `python:3.12-slim` (minimal Debian with Python)
- **CPU-only PyTorch**: Installed via `--index-url https://download.pytorch.org/whl/cpu` to avoid ~2GB GPU libraries
- **Layer caching**: `requirements.txt` copied and installed before application code, so dependency layer is cached across code changes
- **Entrypoint pattern**: `entrypoint.sh` runs `main.py` + `evaluate.py` by default, but supports CMD override for running arbitrary commands (e.g., `docker-compose run reranker python benchmark.py`)
- **No volumes or ports**: The app is a CLI tool, not a service. No persistent state needed beyond the HuggingFace model cache (downloaded fresh per container)

### Consequences

- Good, because reviewers can run `docker-compose up` with no local Python setup
- Good, because CPU-only torch keeps image at ~1.7GB instead of ~3.5GB+ with GPU libraries
- Good, because `.dockerignore` prevents monorepo bloat in Docker context
- Good, because entrypoint CMD override pattern allows running any script (main, evaluate, benchmark)
- Bad, because HuggingFace model (~350MB) is downloaded on every fresh container start (no volume mount for cache)
- Bad, because Dockerfile at repo root is not co-located with the app it builds, which may confuse contributors
- Neutral, the existing venv-based workflow (ADR-0001) remains fully functional alongside Docker

## More Information

- Files: `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `apps/semantic-reranker/entrypoint.sh`
- Docker Compose is minimal (build-only, no volumes, no ports, no networks)
- Related: ADR-0001 (standalone Python app pattern -- Docker adds a deployment option without changing the app structure)
- Related: ADR-0002 (CPU-only inference -- enforced in Dockerfile via PyTorch CPU index URL)
