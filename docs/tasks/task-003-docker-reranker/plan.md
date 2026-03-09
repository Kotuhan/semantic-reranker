# Implementation Plan: task-003 -- Dockerize Semantic Re-Ranker
Generated: 2026-03-09

## Overview

Create 4 new files at the repo root and app level to containerize the existing `apps/semantic-reranker/` Python application. Update `README.md` with Docker instructions. No changes to existing Python source code.

## Files to Create/Modify

| # | File | Action | Purpose |
|---|------|--------|---------|
| 1 | `.dockerignore` (repo root) | CREATE | Minimize build context |
| 2 | `Dockerfile` (repo root) | CREATE | Image definition |
| 3 | `apps/semantic-reranker/entrypoint.sh` | CREATE | Default run orchestration |
| 4 | `docker-compose.yml` (repo root) | CREATE | Service + volume definition |
| 5 | `apps/semantic-reranker/README.md` | MODIFY | Add Docker usage section |

---

## Step 1: Create `.dockerignore` at repo root

**File:** `/Users/user/dev/assignment/.dockerignore`

**Content:**
```
# Version control
.git/
.gitignore

# Node / Turborepo
node_modules/
.turbo/
packages/
pnpm-lock.yaml
pnpm-workspace.yaml
turbo.json
package.json
tsconfig.json

# Documentation and config
architecture/
docs/
knowledgebase/
.claude/
.taskmaster/

# Python artifacts
venv/
__pycache__/
*.pyc
.cache/

# App-specific artifacts to exclude
apps/semantic-reranker/venv/
apps/semantic-reranker/__pycache__/
apps/semantic-reranker/.cache/
apps/semantic-reranker/report.html
apps/semantic-reranker/benchmark_results.json

# Root-level files not needed
*.md
!apps/semantic-reranker/**/*.md
report.html
```

**Rationale:** The build context must include `apps/semantic-reranker/` source, data, scripts, and `requirements.txt`. Everything else (node_modules, docs, .git, venv, architecture) is excluded to keep the context small (<5MB). Note the negation pattern `!apps/semantic-reranker/**/*.md` is included in case any MD files inside the app are ever needed, but in practice the COPY instructions are selective so this is a safety net.

**Verification:** After creating, run `docker build -t test-context .` and observe the "Sending build context to Docker daemon" size is small.

---

## Step 2: Create `Dockerfile` at repo root

**File:** `/Users/user/dev/assignment/Dockerfile`

**Content:**
```dockerfile
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/.cache/huggingface

WORKDIR /app

# Copy and install dependencies first (layer caching)
# Using CPU-only torch index as primary, PyPI as fallback for other packages
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
COPY apps/semantic-reranker/generate_report.py .
COPY apps/semantic-reranker/entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
```

**Key design decisions:**

1. **`python:3.12-slim` base** -- Stable, multi-arch (ARM + x86_64), slim variant avoids unnecessary OS packages.

2. **`--index-url https://download.pytorch.org/whl/cpu` as primary** -- This is the CPU-only PyTorch index. Packages not found here (sentence-transformers, pydantic, rich) fall through to `--extra-index-url https://pypi.org/simple/`. This saves ~1.5GB by avoiding CUDA libraries.

3. **Layer caching strategy** -- `requirements.txt` is copied and installed before source code. Code changes do not invalidate the dependency layer (pip install takes ~2-3 minutes).

4. **WORKDIR `/app`** -- All scripts use `sys.path.insert(0, "src")` and relative paths to `data/`. Setting WORKDIR to `/app` and copying the app contents there means these paths resolve correctly without any code changes.

5. **`HF_HOME=/app/.cache/huggingface`** -- The HuggingFace library respects this env var for model cache location. This path will be volume-mounted in docker-compose for persistence.

6. **`generate_report.py` included** -- While not part of the default entrypoint, it should be available for `docker-compose run` override.

7. **No `COPY apps/semantic-reranker/WRITEUP.md`** etc. -- Only files needed at runtime are copied. Documentation stays out of the image.

**Verification:** `docker build -t semantic-reranker .` succeeds. `docker images semantic-reranker` shows size < 3GB.

---

## Step 3: Create `apps/semantic-reranker/entrypoint.sh`

**File:** `/Users/user/dev/assignment/apps/semantic-reranker/entrypoint.sh`

**Content:**
```bash
#!/bin/bash
set -e

# If arguments are passed, execute them instead of the default sequence.
# This enables: docker-compose run reranker python benchmark.py
if [ $# -gt 0 ]; then
    exec "$@"
fi

# Default: run demo then evaluation
echo "=== Running Re-Ranker Demo ==="
python main.py

echo ""
echo "=== Running Evaluation ==="
python evaluate.py
```

**Key design decisions:**

1. **`set -e`** -- Exit on first error. If `main.py` fails, `evaluate.py` does not run.

2. **`exec "$@"` override pattern** -- When arguments are passed (e.g., `docker-compose run reranker python benchmark.py`), the entrypoint hands off execution entirely to the provided command. This supports:
   - `docker-compose run reranker python benchmark.py` -- run benchmark
   - `docker-compose run reranker python main.py` -- run demo only
   - `docker-compose run reranker python evaluate.py` -- run evaluation only
   - `docker-compose run reranker bash` -- interactive shell for debugging

3. **Echo separators** -- Visible markers between main.py and evaluate.py output since both produce rich tables.

**Verification:** `bash -n apps/semantic-reranker/entrypoint.sh` passes (syntax check). File must be committed with execute permission (`chmod +x`).

---

## Step 4: Create `docker-compose.yml` at repo root

**File:** `/Users/user/dev/assignment/docker-compose.yml`

**Content:**
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

**Key design decisions:**

1. **Named volume `hf-cache`** -- Persists the HuggingFace model cache across container rebuilds and image changes. The model (~350MB for default, ~1GB+ if benchmark runs 3 models) downloads once and is reused.

2. **No `version` key** -- Modern Docker Compose (v2+) does not require the `version` field. It is deprecated.

3. **No port mappings** -- This is a CLI tool, not a server. No ports needed.

4. **No `restart` policy** -- Run-to-completion semantics. Container runs the scripts and exits.

5. **`environment` section** -- Reinforces `HF_HOME` even though it is also set in the Dockerfile. Explicit in compose for visibility and override capability.

6. **No `container_name`** -- Allows docker-compose to manage naming (enables `docker-compose run` to create parallel instances).

**Verification:** `docker-compose config` validates without errors.

---

## Step 5: Update `apps/semantic-reranker/README.md`

**File:** `/Users/user/dev/assignment/apps/semantic-reranker/README.md`

**Change:** Add a "Docker" section after the existing "Setup" section (before "Usage"). Insert the following block after the closing `>` note about model download (line 23) and before `## Usage` (line 25):

**Content to insert:**
```markdown

## Docker (Recommended)

Run everything with a single command -- no Python setup required:

```bash
# From the repository root:
docker-compose up --build
```

This builds the image, installs dependencies, and runs both `main.py` (demo) and `evaluate.py` (metrics).

### Run individual scripts

```bash
docker-compose run reranker python main.py         # Demo only
docker-compose run reranker python evaluate.py      # Evaluation only
docker-compose run reranker python benchmark.py     # Full benchmark (~10 min)
docker-compose run reranker python generate_report.py  # Generate HTML report
```

### Notes

- **First run** downloads the cross-encoder model (~350MB). Subsequent runs use a cached Docker volume and work offline.
- **Image size** is ~2-3GB (CPU-only PyTorch, no CUDA).
- The `Dockerfile` and `docker-compose.yml` are at the **repository root**, not inside `apps/semantic-reranker/`.
- To reset the model cache: `docker-compose down -v`

```

**Verification:** README renders correctly in a Markdown viewer. Commands listed are accurate.

---

## Verification Plan

### Build verification
```bash
# Syntax check entrypoint
bash -n apps/semantic-reranker/entrypoint.sh

# Validate docker-compose
docker-compose config

# Build image
docker-compose build

# Check image size
docker images | grep reranker
# Expected: < 3GB
```

### Functional verification
```bash
# Run default (main.py + evaluate.py)
docker-compose up

# Expected output:
# 1. "=== Running Re-Ranker Demo ===" followed by 5 rich tables
# 2. "=== Running Evaluation ===" followed by NDCG/Precision table
# 3. Container exits with code 0

# Run individual scripts
docker-compose run reranker python main.py
docker-compose run reranker python evaluate.py
docker-compose run reranker python benchmark.py
```

### Cache verification
```bash
# Second run should NOT show model download messages
docker-compose up

# Offline verification (disconnect network, run again)
# Model loads from volume cache
```

### Clean rebuild verification
```bash
docker-compose down -v
docker-compose up --build
# Full rebuild from scratch -- must succeed
```

### Monorepo build verification
```bash
# Docker files should not break existing monorepo tooling
pnpm lint
pnpm test
pnpm build
```

Note: `pnpm lint/test/build` applies to the monorepo (NestJS etc.), not the Python app. The Python app is standalone and not managed by pnpm. These commands should still pass since we are only adding new files (Dockerfile, docker-compose.yml, .dockerignore, entrypoint.sh) and modifying README.md -- none of which affect the monorepo build.

---

## Potential Issues

1. **pip install with dual index URLs** -- If a package exists in both the CPU torch index and PyPI, the CPU index version wins (it is `--index-url`, not `--extra-index-url`). For `torch` and `sentence-transformers` this is correct behavior. For `pydantic` and `rich`, they will not be found in the torch index and will fall through to PyPI via `--extra-index-url`.

2. **ARM vs x86** -- `python:3.12-slim` has multi-arch manifests. PyTorch CPU wheels are available for both `linux/amd64` and `linux/arm64`. No platform-specific issues expected.

3. **`benchmark_results.json` output** -- `benchmark.py` writes `benchmark_results.json` to the current directory inside the container. Since the container filesystem is ephemeral, this file is lost when the container stops. This is acceptable -- the user sees the output in the terminal. If persistence is needed, a bind mount can be added later.

4. **File permissions for `entrypoint.sh`** -- The `RUN chmod +x entrypoint.sh` in the Dockerfile handles this inside the image. However, the file should also be committed with execute permission in git: `git add --chmod=+x apps/semantic-reranker/entrypoint.sh`.
