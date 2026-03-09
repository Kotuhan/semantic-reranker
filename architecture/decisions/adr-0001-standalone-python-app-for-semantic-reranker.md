---
status: accepted
date: 2026-03-09
triggered-by: task-001
---

# ADR-0001: Standalone Python App for Semantic Re-Ranker

## Context and Problem Statement

The first project added to the monorepo is a Python-based semantic re-ranker for intelligence reports. The monorepo is configured with Turborepo + pnpm workspaces (targeting Node.js/TypeScript). We needed to decide how to integrate a Python project into this structure.

## Decision Drivers

- The re-ranker is a take-home assignment deliverable that must be self-contained and runnable independently
- The monorepo toolchain (Turborepo, pnpm) has no native Python support
- Evaluators will clone and run the project without understanding the monorepo
- No other components exist yet that the re-ranker needs to interact with

## Considered Options

- Standalone Python project under `apps/` with no monorepo integration
- Python project with Turborepo task wrappers (e.g., pnpm scripts calling Python)
- Separate repository outside the monorepo

## Decision Outcome

Chosen option: "Standalone Python project under `apps/` with no monorepo integration", because the project has no dependencies on other monorepo packages, evaluators need a self-contained artifact, and adding Turborepo wrappers for a single Python project adds complexity with no benefit.

### Consequences

- Good, because the project is fully self-contained with its own venv, requirements.txt, and run instructions
- Good, because evaluators can navigate directly to `apps/semantic-reranker/` without monorepo knowledge
- Bad, because `pnpm dev`, `pnpm build`, `pnpm test` do not include this project -- it must be run separately
- Neutral, sets a precedent that `apps/` can contain non-Node.js projects without monorepo integration

## More Information

- Scripts must be run from `apps/semantic-reranker/` directory due to relative path usage
- Uses `sys.path.insert(0, "src")` for imports rather than a Python package manager (no pyproject.toml, no setuptools)
