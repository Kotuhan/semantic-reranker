# Architecture Documentation

Living architecture reference for the project. This directory is the primary knowledge base for the System Architect agent.

## Directory Structure

| Subdirectory | Purpose | Naming Convention |
|---|---|---|
| `decisions/` | MADR Architecture Decision Records | `adr-NNNN-slug.md` (4-digit, sequential) |
| `contracts/` | API contracts, event schemas, protocol specs | `{domain}-{type}.md` |
| `diagrams/` | Mermaid system architecture diagrams | `{scope}-{view}.md` |
| `roadmap/` | Migration and evolution plans | `{feature-slug}.md` |
| `runbooks/` | Operational procedures for failure recovery | `{scenario-slug}.md` |

## Key Files

| File | Description |
|---|---|
| `overview.md` | Living system state: components, tech stack, module inventory, security architecture, known limitations |
| `system-design.md` | System design: C4 diagrams, sequence diagrams, state machines, crosscutting concerns |
| `decisions/_template.md` | MADR template for new ADRs (immutable) |

## Instructions for System Architect Agent

1. **Read this file first** when entering any arch-* mode (arch-context, arch-review, arch-update)
2. **Check existing ADRs** in `decisions/` before creating new ones to avoid duplicates
3. **Use `decisions/_template.md`** for all new ADRs. Never modify the template itself.
4. **Keep `overview.md` current** as the single source of truth for architecture state
5. **Verify contracts match implementation** when reviewing changes that affect API boundaries
6. **Use Mermaid syntax** for all diagrams (renders natively on GitHub)
7. **Cross-reference ADRs** bidirectionally when one supersedes another

## ADR Numbering

- Format: `adr-NNNN-slug.md` (4-digit zero-padded)
- Start: 0001
- Next available: 0001
- Sequential only. Never reuse numbers, even for rejected/superseded ADRs.
- Slug: lowercase, hyphens, verb-noun structure preferred (e.g., `use-madr-format`, `adopt-stripe-billing`)

## Relationship to Root CLAUDE.md

This `architecture/` directory **supplements** the root `CLAUDE.md`. It does not replace it.

- `CLAUDE.md`: Quick reference for developers (commands, setup, key parameters)
- `architecture/`: Deep reference for architectural decisions, contracts, and system design

When architectural information changes, update both:
1. `architecture/overview.md` (detailed, living document)
2. Root `CLAUDE.md` relevant section (summary for developers)
