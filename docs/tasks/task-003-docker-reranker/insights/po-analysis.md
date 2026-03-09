# PO Analysis: task-003
Generated: 2026-03-09

## Problem Statement

Today, running the semantic re-ranker requires manual environment setup: creating a Python virtual environment, installing dependencies, ensuring the correct Python version, and running scripts from the correct working directory. This process is fragile and non-reproducible -- it works on the developer's machine but may fail on a colleague's due to OS differences, Python version mismatches, or missing system libraries (especially for torch/sentence-transformers).

From a user perspective: "As a developer or reviewer evaluating this project, I want to clone the repo and run a single command to see the re-ranker in action, without spending time debugging Python environment issues."

This matters now because:
- The project is a take-home assignment that will be reviewed by evaluators. First impressions matter -- a clean `docker-compose up` experience signals production-readiness.
- The re-ranker depends on heavy ML libraries (torch ~2GB, sentence-transformers) that are notoriously sensitive to OS and Python version.
- The offline requirement from the PRD means the container must work without internet access after initial model download -- Docker with cached volumes achieves this cleanly.

If we do nothing: reviewers must manually set up a Python 3.10+ venv, install requirements (which may fail on their system), and remember to run scripts from the correct directory. Any friction reduces confidence in the solution.

## Success Criteria

1. A reviewer can run the full demo (`main.py`) with a single `docker-compose up` command (or equivalent one-liner) and see re-ranked results in the terminal.
2. Running `evaluate.py` and `benchmark.py` inside the container is straightforward (single docker-compose command or documented `docker exec` / `docker-compose run` command).
3. The HuggingFace model (~350MB) is cached in a Docker volume so subsequent runs skip the download and work offline.
4. The Docker image builds successfully on both ARM (Apple Silicon) and x86_64 architectures.
5. Container startup to first output (with cached model) takes no longer than 30 seconds.

## Acceptance Criteria

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
  Then the image builds without errors and the final image size is under 3GB (CPU-only torch, no GPU libraries)

* Given the data files (reports.json, keyword_results.json, ideal_rankings.json) exist in the repository
  When the container starts
  Then all data files are accessible inside the container at the expected paths

* Given the Docker setup uses a volume for HuggingFace cache
  When the user rebuilds the image (code changes only, not requirements)
  Then the model cache volume is preserved and the model does not re-download

## Out of Scope

- **GPU support**: The re-ranker is CPU-only per PRD constraints. No NVIDIA/CUDA Docker configuration.
- **FastAPI or HTTP server**: This task containerizes the existing CLI scripts, not a web service. API wrapping is future work per the PRD.
- **Multi-stage production image optimization**: A reasonable image size is expected, but aggressive multi-stage builds to minimize image size below 2GB are not required.
- **CI/CD pipeline integration**: No GitHub Actions or automated build pipeline for the Docker image.
- **Kubernetes manifests or Helm charts**: Container orchestration beyond docker-compose is not included.
- **Health checks or readiness probes**: Not needed for CLI-mode execution.
- **Custom model baking into the image**: The model should be downloaded on first run and cached via volume, not embedded in the Docker image itself.
- **Windows container support**: Linux containers only (works on Windows via Docker Desktop/WSL2, but no Windows-native containers).

## Open Questions

* Should the default `docker-compose up` command run `main.py`, `evaluate.py`, or both? --> Owner: PO (user decision)
* Should the Dockerfile live at `apps/semantic-reranker/Dockerfile` or at the repository root? The app is standalone, so app-level placement seems natural, but root placement may be preferred for visibility. --> Owner: PO (user decision)
* Is Python 3.14 (matching the current venv) required, or should we target a more widely available base image like Python 3.11 or 3.12? The current venv shows Python 3.14 which may have limited Docker base image availability. --> Owner: TL (technical decision, but flagged for awareness)

## Recommendations

- Use `python:3.11-slim` or `python:3.12-slim` as the base image for broad compatibility and smaller size. Python 3.14 is very new and official slim images may not be stable.
- Install `torch` CPU-only variant (`--index-url https://download.pytorch.org/whl/cpu`) to avoid pulling in CUDA libraries and save ~1.5GB of image size.
- Set `TRANSFORMERS_CACHE` / `HF_HOME` environment variable in the Dockerfile pointing to a path that can be mounted as a Docker volume.
- Set `WORKDIR` to `/app` in the container, matching the requirement that scripts run from the app directory.
- Use `.dockerignore` to exclude `venv/`, `__pycache__/`, and `.git/` from the build context.
- The `docker-compose.yml` should define a named volume for the HuggingFace cache and mount `data/` from the host (or copy it into the image).
