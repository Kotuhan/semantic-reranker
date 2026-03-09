# Architecture Update: task-003-docker-reranker
Generated: 2026-03-09

## Impact Assessment

This task introduced Docker containerization as a new deployment mechanism for the semantic re-ranker. While the application code itself was unchanged, several architectural decisions were made implicitly during implementation:

1. **Dockerfile placement at repo root** -- a project-level convention for how Docker builds interact with the monorepo structure
2. **CPU-only PyTorch enforcement in Docker** -- reinforces the CPU-only constraint from ADR-0002, now codified in the Dockerfile's `--index-url` flag
3. **CLI-tool-not-service pattern** -- the Docker container runs scripts and exits, with no ports, volumes, or persistent state, preserving the security architecture (no network services)
4. **Entrypoint with CMD override** -- establishes a pattern for running different scripts in the same container

These decisions collectively form a Docker containerization pattern that warrants an ADR for future reference.

## Updates Made

- `architecture/decisions/adr-0004-docker-containerization-for-semantic-reranker.md`: Created new ADR documenting the Docker containerization pattern, base image choice, CPU-only PyTorch enforcement, Dockerfile placement at repo root, entrypoint design, and the decision to not use volumes or ports
- `architecture/overview.md`: Added Docker container as a system component in the components table; added Docker deployment subsection under Semantic Re-Ranker; added Docker/Docker Compose to the tech stack table; added Dockerfile, docker-compose.yml, and entrypoint.sh to the module inventory; updated security architecture section to note Docker container exposes no ports
- `architecture/CLAUDE.md`: Updated next available ADR number from 0004 to 0005

## Retroactive ADRs Created

- ADR-0004: Docker Containerization for Semantic Re-Ranker -- documents the containerization pattern including Dockerfile-at-root convention, CPU-only PyTorch, entrypoint override pattern, and the decision to keep the container as a CLI tool (no service, no volumes, no ports)

## Recommendations

- **Model cache volume**: If container startup time becomes a concern (model download is ~350MB per fresh start), consider adding a named Docker volume for the HuggingFace cache directory (`~/.cache/huggingface/`). The TL design originally included this but it was not implemented in the final docker-compose.yml. This is acceptable for demo/evaluation use but would need revisiting for frequent usage.
- **Multi-app Docker**: If future apps are Dockerized, consider whether each gets its own Dockerfile at repo root or whether a `docker/` directory convention should be established. ADR-0004 sets the precedent of root-level Dockerfile for now.
- **Python version alignment**: The Dockerfile uses Python 3.12-slim while `architecture/overview.md` documents "Python 3.10+". Both are correct (3.12 satisfies 3.10+), but if the minimum version is effectively 3.12 now due to Docker, this should be clarified when relevant.
