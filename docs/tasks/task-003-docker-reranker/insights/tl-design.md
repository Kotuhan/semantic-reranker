# Technical Design: task-003
Generated: 2026-03-09

## Overview

Dockerize the semantic re-ranker by adding a Dockerfile at the repository root and a docker-compose.yml that runs main.py followed by evaluate.py. The build uses Python 3.12-slim with CPU-only torch, layer-cached dependency installation, and a named Docker volume for the HuggingFace model cache. An entrypoint shell script orchestrates the sequential execution of both Python scripts.

## Technical Notes

- **Affected modules:** `apps/semantic-reranker/` (no code changes -- Docker wraps existing scripts)
- **New files to create:**
  - `Dockerfile` (repo root)
  - `docker-compose.yml` (repo root)
  - `.dockerignore` (repo root)
  - `apps/semantic-reranker/entrypoint.sh` (shell script to run main.py then evaluate.py)
- **DB schema change required?** No
- **Architectural considerations:**
  - Dockerfile at repo root with build context `.` -- COPY paths reference `apps/semantic-reranker/`
  - WORKDIR set to `/app` inside the container, which maps to `apps/semantic-reranker/` contents
  - Scripts use `sys.path.insert(0, "src")` and relative paths to `data/` -- WORKDIR must be the app directory for these to resolve
  - torch CPU-only variant via `--index-url https://download.pytorch.org/whl/cpu` saves ~1.5GB
  - Layer caching: COPY requirements.txt first, pip install, then COPY source -- code changes don't invalidate the dependency layer
  - HF_HOME env var points to `/root/.cache/huggingface` (or `/app/.cache/huggingface`) mounted as a named volume
  - entrypoint.sh runs `python main.py && python evaluate.py` by default, but CMD can be overridden for individual scripts
- **Known risks or trade-offs:**
  - **ARM/x86 compatibility (Low):** `python:3.12-slim` has multi-arch images. torch CPU wheel is available for both. sentence-transformers pulls platform-appropriate wheels.
  - **Image size (Low):** CPU-only torch keeps image under 3GB. No multi-stage build needed per scope.
  - **First-run model download (Low):** ~350MB download on first run. Volume caching means subsequent runs are instant and work offline.
  - **benchmark.py downloads 3 models (Info):** The benchmark script loads 3 different models (~1GB total). Running it via docker-compose is supported but documented separately since it takes longer and downloads more.
- **Test plan:** Manual verification only (Docker build + run). No unit tests for Docker configuration. Verification via docker-compose up and checking output matches expected metrics.

## Architecture Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| Dockerfile at repo root | User decision (resolved). Gives visibility for reviewers who clone the repo. Build context includes `apps/semantic-reranker/`. | App-level Dockerfile (rejected -- less visible) |
| Shell entrypoint script | Clean separation of orchestration from Dockerfile CMD. Easy to override for individual scripts. | Inline `CMD ["sh", "-c", "python main.py && python evaluate.py"]` (less maintainable, harder to override) |
| CPU-only torch via `--index-url` | Saves ~1.5GB image size. PRD mandates CPU-only. | Default torch with CUDA (wasteful, larger image) |
| Named volume for HF cache | Persists across container rebuilds. Works offline after first download. Standard Docker pattern. | Bind mount (couples to host path), bake model into image (huge image, violates out-of-scope) |
| `docker-compose run` for benchmark | benchmark.py downloads 3 extra models and takes ~10min. Should not be part of default `docker-compose up`. | Include in default entrypoint (too slow for reviewers) |
| No multi-stage build | Out of scope per PO. Single-stage keeps Dockerfile simple. Image under 3GB is acceptable. | Multi-stage (complexity not justified for CLI tool) |

## Implementation Steps

### Step 1 -- Create .dockerignore at repo root

- **Files:** `/Users/user/dev/assignment/.dockerignore`
- **Details:** Exclude directories that should not be in the Docker build context: `node_modules/`, `.git/`, `venv/`, `__pycache__/`, `.turbo/`, `packages/`, `architecture/`, `docs/`, `knowledgebase/`, `.claude/`, `*.md` (root-level), `pnpm-lock.yaml`, `.taskmaster/`, `report.html`, `apps/semantic-reranker/venv/`, `apps/semantic-reranker/__pycache__/`, `apps/semantic-reranker/.cache/`. Keep `apps/semantic-reranker/` source, data, and requirements.txt.
- **Verification:** Run `docker build --no-cache -f Dockerfile -t test-context .` from repo root and confirm build context is small (< 5MB excluding base image pulls).

### Step 2 -- Create Dockerfile at repo root

- **Files:** `/Users/user/dev/assignment/Dockerfile`
- **Details:**
  ```
  FROM python:3.12-slim

  # Set environment variables
  ENV PYTHONDONTWRITEBYTECODE=1
  ENV PYTHONUNBUFFERED=1
  ENV HF_HOME=/app/.cache/huggingface

  WORKDIR /app

  # Copy and install dependencies first (layer caching)
  COPY apps/semantic-reranker/requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt \
      --index-url https://download.pytorch.org/whl/cpu \
      --extra-index-url https://pypi.org/simple/

  # Copy application source and data
  COPY apps/semantic-reranker/src/ src/
  COPY apps/semantic-reranker/data/ data/
  COPY apps/semantic-reranker/main.py .
  COPY apps/semantic-reranker/evaluate.py .
  COPY apps/semantic-reranker/benchmark.py .
  COPY apps/semantic-reranker/entrypoint.sh .
  RUN chmod +x entrypoint.sh

  ENTRYPOINT ["./entrypoint.sh"]
  ```
  Key points:
  - `--index-url` for CPU-only torch as primary, `--extra-index-url` for other packages from PyPI
  - WORKDIR `/app` so `sys.path.insert(0, "src")` and `data/` relative paths resolve correctly
  - HF_HOME points to a path inside the container that will be volume-mounted
  - PYTHONUNBUFFERED=1 ensures real-time output in `docker-compose up`
- **Verification:** `docker build -t semantic-reranker .` from repo root succeeds without errors. Check image size with `docker images semantic-reranker` (should be < 3GB).

### Step 3 -- Create entrypoint.sh

- **Files:** `/Users/user/dev/assignment/apps/semantic-reranker/entrypoint.sh`
- **Details:**
  ```bash
  #!/bin/bash
  set -e

  # If arguments are passed, run them instead of the default
  if [ $# -gt 0 ]; then
      exec "$@"
  fi

  # Default: run main.py then evaluate.py
  echo "=== Running Re-Ranker Demo ==="
  python main.py

  echo ""
  echo "=== Running Evaluation ==="
  python evaluate.py
  ```
  The `if [ $# -gt 0 ]` pattern allows overriding via:
  - `docker-compose run reranker python benchmark.py`
  - `docker-compose run reranker python main.py`
  - `docker-compose run reranker bash` (interactive shell)
- **Verification:** `chmod +x entrypoint.sh` and confirm the script is syntactically valid with `bash -n entrypoint.sh`.

### Step 4 -- Create docker-compose.yml at repo root

- **Files:** `/Users/user/dev/assignment/docker-compose.yml`
- **Details:**
  ```yaml
  services:
    reranker:
      build:
        context: .
        dockerfile: Dockerfile
      volumes:
        - hf-cache:/app/.cache/huggingface
      environment:
        - HF_HOME=/app/.cache/huggingface

  volumes:
    hf-cache:
  ```
  Key points:
  - Named volume `hf-cache` persists the HuggingFace model cache across container rebuilds
  - No port mappings needed (CLI tool, not a server)
  - No restart policy (run-to-completion)
  - `environment` section reinforces HF_HOME (also set in Dockerfile, but explicit in compose for clarity)
- **Verification:** `docker-compose config` validates the compose file syntax.

### Step 5 -- Build and run end-to-end verification

- **Files:** No new files. Verification step.
- **Details:**
  1. `docker-compose build` -- image builds without errors
  2. `docker-compose up` -- runs main.py then evaluate.py, produces expected output
  3. Verify NDCG@10 output matches baseline (~0.8283 or close, depending on model used by default Reranker)
  4. `docker-compose run reranker python evaluate.py` -- runs evaluate.py alone
  5. `docker-compose run reranker python benchmark.py` -- runs benchmark (optional, takes ~10min)
  6. Check image size: `docker images` shows < 3GB
  7. Second run: `docker-compose up` again -- model loads from cache (no download), faster startup
- **Verification:** All commands above produce expected output. Container exits cleanly with code 0.

### Step 6 -- Update README.md with Docker instructions

- **Files:** `/Users/user/dev/assignment/apps/semantic-reranker/README.md`
- **Details:** Add a "Docker" section after the existing "Setup" section:
  - `docker-compose up` -- builds and runs demo + evaluation
  - `docker-compose run reranker python benchmark.py` -- runs benchmark
  - `docker-compose run reranker python main.py` -- runs demo only
  - Note about first-run model download and volume caching
  - Note that docker-compose.yml is at the repo root
- **Verification:** README renders correctly, commands are accurate.

### Step 7 -- Verification: full clean test

- **Files:** No new files.
- **Details:**
  1. Remove existing images/volumes: `docker-compose down -v && docker rmi semantic-reranker` (if exists)
  2. `docker-compose up --build` -- full rebuild from scratch
  3. Confirm main.py output (re-ranked tables)
  4. Confirm evaluate.py output (NDCG@10, Precision@5 table)
  5. Confirm container exits with code 0
  6. Run again without `--build` -- verify model is cached (no download messages)
- **Verification:** Both runs succeed. Second run is faster (cached model).

## Complexity Assessment

- **Estimated effort:** 0.5 days (2-4 hours)
- **Risk level:** Low
- **Dependencies:** Docker and docker-compose installed on the machine. No code changes to the Python app itself.
- **Step count:** 7 steps (5 implementation + 2 verification)

This is a straightforward infrastructure task. The main subtlety is the pip install command for CPU-only torch (correct index URLs) and ensuring WORKDIR aligns with the scripts' relative path assumptions. No code changes to the existing Python application are needed.

## Test Strategy

- **Unit tests:** None. Docker configuration is not unit-testable.
- **Integration tests:** Manual docker-compose build + run cycle (Steps 5 and 7).
- **Verification checks:**
  1. Image builds without errors
  2. Image size < 3GB
  3. `docker-compose up` produces expected main.py + evaluate.py output
  4. `docker-compose run reranker python benchmark.py` works
  5. Named volume preserves model cache across runs
  6. Second run works without internet (model cached)
  7. Entrypoint override works (`docker-compose run reranker python main.py`)

## Open Technical Questions

None. All questions from PO analysis have been resolved by the user. No new technical questions discovered during design.
