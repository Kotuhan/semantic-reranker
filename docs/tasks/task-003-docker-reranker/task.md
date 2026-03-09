---
id: task-003
title: Dockerize Semantic Re-Ranker
status: backlog
priority: high
dependencies: [task-001]
created_at: 2026-03-09
---

# Dockerize Semantic Re-Ranker

## Problem (PO)

Running the semantic re-ranker requires manual environment setup: creating a Python virtual environment, installing dependencies, ensuring the correct Python version, and running scripts from the correct working directory. This is fragile and non-reproducible across machines due to OS differences, Python version mismatches, and system library conflicts (especially for torch/sentence-transformers).

As a reviewer evaluating this project, I want to clone the repo and run a single command to see the re-ranker in action, without debugging Python environment issues.

**Why now:** This is a take-home assignment -- a clean `docker-compose up` experience signals production-readiness to evaluators. The heavy ML dependencies (torch ~2GB) are notoriously sensitive to environment. The offline requirement from the PRD is naturally satisfied by Docker with cached model volumes.

**If we do nothing:** Reviewers must manually set up Python 3.10+ venv, install requirements (which may fail), and remember to run scripts from the correct directory. Friction reduces confidence in the solution.

## Success Criteria (PO)

1. A reviewer runs the full demo (`main.py`) with a single `docker-compose up` command and sees re-ranked results in the terminal.
2. Running `evaluate.py` and `benchmark.py` inside the container is straightforward (single docker-compose command).
3. The HuggingFace model (~350MB) is cached in a Docker volume so subsequent runs skip the download and work offline.
4. The Docker image builds successfully on both ARM (Apple Silicon) and x86_64 architectures.
5. Container startup to first output (with cached model) takes no longer than 30 seconds.

## Acceptance Criteria (PO)

* Given a fresh clone of the repository with Docker installed
  When the user runs `docker-compose up` (or the documented build+run command)
  Then the container builds, installs dependencies, and executes `main.py` producing re-ranked results in the terminal

* Given the container has run once and the HuggingFace model is cached in a volume
  When the user runs the container again without internet access
  Then the re-ranker executes successfully using the cached model

* Given the Docker setup is complete
  When the user runs `evaluate.py` via the documented command (e.g., `docker-compose run reranker python evaluate.py`)
  Then the evaluation produces NDCG@10 and Precision@5 metrics matching the known baseline (Avg NDCG@10 ~0.8283)

* Given the Docker setup is complete
  When the user runs `benchmark.py` via the documented command
  Then the benchmark produces the comparison table with all 15 experiments

* Given the Dockerfile and docker-compose.yml are present
  When `docker-compose build` is run
  Then the image builds without errors and the final image size is under 3GB

* Given the data files (reports.json, keyword_results.json, ideal_rankings.json) exist in the repository
  When the container starts
  Then all data files are accessible inside the container at the expected paths

* Given the Docker setup uses a volume for HuggingFace cache
  When the user rebuilds the image (code changes only, not requirements)
  Then the model cache volume is preserved and the model does not re-download

## Out of Scope (PO)

- **GPU support**: CPU-only per PRD constraints. No NVIDIA/CUDA Docker configuration.
- **FastAPI or HTTP server**: This task containerizes existing CLI scripts, not a web service.
- **Aggressive image size optimization**: Reasonable size expected (<3GB), but no multi-stage build to minimize below 2GB.
- **CI/CD pipeline**: No GitHub Actions or automated Docker build pipeline.
- **Kubernetes/Helm**: No container orchestration beyond docker-compose.
- **Health checks or readiness probes**: Not needed for CLI-mode execution.
- **Model baking into image**: Model downloads on first run and caches via volume.
- **Windows container support**: Linux containers only.

## Open Questions (PO)

* ~~What should `docker-compose up` run by default?~~ **RESOLVED**: Both `main.py` then `evaluate.py` sequentially.
* ~~Should the Dockerfile live at `apps/semantic-reranker/Dockerfile` or at the repository root?~~ **RESOLVED**: Repository root.
* ~~Python version for base image?~~ **RESOLVED**: Python 3.12 (stable, broad Docker support).

---

## Technical Notes (TL)

- **Affected modules:** `apps/semantic-reranker/` (no code changes -- Docker wraps existing scripts)
- **New files to create:**
  - `Dockerfile` (repo root) -- Python 3.12-slim, CPU-only torch, layer-cached deps
  - `docker-compose.yml` (repo root) -- service definition with named volume for HF cache
  - `.dockerignore` (repo root) -- exclude venv, node_modules, .git, docs, etc.
  - `apps/semantic-reranker/entrypoint.sh` -- runs main.py then evaluate.py; supports CMD override
- **DB schema change required?** No
- **Architectural considerations:**
  - Dockerfile at repo root; build context `.`; COPY paths reference `apps/semantic-reranker/`
  - WORKDIR `/app` -- scripts' `sys.path.insert(0, "src")` and relative `data/` paths resolve correctly
  - torch CPU-only via `--index-url https://download.pytorch.org/whl/cpu` (saves ~1.5GB)
  - Layer caching: COPY requirements.txt first, pip install, then COPY source
  - `HF_HOME=/app/.cache/huggingface` env var + named Docker volume for model persistence
  - `PYTHONUNBUFFERED=1` for real-time output in docker-compose
  - entrypoint.sh pattern: if args passed, `exec "$@"` (override); otherwise default sequence
- **Known risks or trade-offs:**
  - ARM/x86 compatibility (Low): python:3.12-slim and torch CPU wheels are multi-arch
  - Image size (Low): CPU-only torch keeps image under 3GB
  - First-run model download (Low): ~350MB on first run, cached via volume thereafter
  - benchmark.py downloads 3 models (Info): not part of default entrypoint, run separately
- **Test plan:** Manual verification (docker-compose build + run). No unit tests for Docker config.

## Implementation Steps (TL)

1. **Create `.dockerignore` at repo root**
   - Files: `.dockerignore`
   - Exclude: `node_modules/`, `.git/`, `venv/`, `__pycache__/`, `.turbo/`, `packages/`, `architecture/`, `docs/`, `knowledgebase/`, `.claude/`, `.taskmaster/`, `report.html`, `apps/semantic-reranker/venv/`, `apps/semantic-reranker/__pycache__/`, `apps/semantic-reranker/.cache/`
   - Verification: build context is small (only app source + data)

2. **Create `Dockerfile` at repo root**
   - Files: `Dockerfile`
   - Base: `python:3.12-slim`; env vars `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `HF_HOME=/app/.cache/huggingface`
   - WORKDIR `/app`; COPY requirements.txt first, pip install with CPU-only torch index, then COPY src/, data/, scripts, entrypoint.sh
   - Verification: `docker build -t semantic-reranker .` succeeds; image < 3GB

3. **Create `apps/semantic-reranker/entrypoint.sh`**
   - Files: `apps/semantic-reranker/entrypoint.sh`
   - If args passed: `exec "$@"` (allows override); else: run `python main.py && python evaluate.py`
   - Verification: `bash -n entrypoint.sh` passes

4. **Create `docker-compose.yml` at repo root**
   - Files: `docker-compose.yml`
   - Service `reranker` with build context `.`, named volume `hf-cache` mounted at `/app/.cache/huggingface`
   - Verification: `docker-compose config` validates

5. **End-to-end verification**
   - `docker-compose build` succeeds
   - `docker-compose up` runs main.py + evaluate.py with expected output
   - `docker-compose run reranker python benchmark.py` works
   - Second run uses cached model (no download)
   - Image size < 3GB

6. **Update `apps/semantic-reranker/README.md` with Docker section**
   - Add Docker usage instructions after existing Setup section
   - Document: `docker-compose up`, `docker-compose run reranker python benchmark.py`, volume caching
   - Verification: README is accurate and renders correctly

7. **Clean verification**
   - `docker-compose down -v` + rebuild from scratch
   - Both main.py and evaluate.py produce expected output
   - Container exits with code 0

---

## Implementation Log (DEV)

<!-- To be filled during implementation -->

---

## QA Notes (QA)

<!-- To be filled by QA agent -->
