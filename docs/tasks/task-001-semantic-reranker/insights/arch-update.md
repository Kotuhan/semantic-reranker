# Architecture Update: task-001
Generated: 2026-03-09

## Impact Assessment

This is the first project added to the monorepo. It introduces a new standalone Python application under `apps/semantic-reranker/` that is architecturally isolated from the Node.js/TypeScript monorepo toolchain. Three implicit architectural decisions were identified and documented as retroactive ADRs.

Key architectural impact:
- Establishes precedent that `apps/` can contain non-Node.js projects without Turborepo/pnpm integration
- Introduces Python + sentence-transformers + Pydantic as a technology stack component
- No cross-component interactions, no API contracts, no shared state with other modules

## Updates Made

- `architecture/overview.md`: Populated all sections (previously empty template). Added Semantic Re-Ranker as the first system component, documented tech stack, module inventory, security architecture (none), and known limitations.
- `architecture/CLAUDE.md`: Updated next available ADR number from 0001 to 0004.

## Retroactive ADRs Created

- **ADR-0001**: Standalone Python App for Semantic Re-Ranker -- documents the decision to keep the Python project outside the monorepo toolchain (no Turborepo/pnpm integration), with consequences for `pnpm dev/build/test` not including it.
- **ADR-0002**: Cross-Encoder Model for Semantic Re-Ranking -- documents the choice of `cross-encoder/ms-marco-MiniLM-L-6-v2` via sentence-transformers over bi-encoder or raw transformers alternatives, with performance characteristics (3.1x NDCG improvement, ~0.3s latency).
- **ADR-0003**: Document Text Composition for Cross-Encoder Scoring -- documents the decision to concatenate title + description + location (excluding subcategories) as the document text for scoring, with rationale for each field inclusion/exclusion.

## Recommendations

- **Future Python projects**: If additional Python apps are added to `apps/`, consider establishing a standardized pattern (e.g., pyproject.toml, shared linting config) rather than ad-hoc sys.path manipulation. ADR-0001 should be revisited at that point.
- **Monorepo Python integration**: If the project grows beyond a standalone assignment into a production service, consider adding Turborepo task wrappers or a separate Python workspace manager (e.g., uv, poetry) to bring it under unified `pnpm` commands.
- **Model versioning**: The current requirements.txt uses minimum version pins (`>=`). For reproducibility in production, consider pinning exact versions or using a lockfile.
