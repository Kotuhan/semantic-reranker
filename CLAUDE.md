# CLAUDE.md

## Communication

<!-- Define your language preferences here -->
<!-- Example: User writes in Ukrainian, Claude responds in English. -->
User writes in Ukrainian, Claude responds in English.
## Project Overview

<!-- Describe your project here -->

## Tech Stack

<!-- List your technology choices -->
- **Monorepo**: Turborepo + pnpm workspaces

## Project Structure

```
apps/                # Application packages (add your apps here)
packages/config/     # Shared ESLint, TS configs
architecture/        # Architecture docs (ADRs, contracts, diagrams, roadmap, runbooks)
docs/                # Documentation, tasks (see docs/CLAUDE.md)
knowledgebase/       # Central research repository (managed by Researcher agent)
.claude/             # Claude Code configuration
.taskmaster/         # Task Master AI integration
```

## Module Documentation

| Directory        | CLAUDE.md                                            | Description                              |
| ---------------- | ---------------------------------------------------- | ---------------------------------------- |
| `knowledgebase/` | [knowledgebase/CLAUDE.md](knowledgebase/CLAUDE.md)   | Research repository, technical docs      |
| `docs/`          | [docs/CLAUDE.md](docs/CLAUDE.md)                     | Tasks, workflow docs                     |
| `architecture/`  | [architecture/CLAUDE.md](architecture/CLAUDE.md)     | ADRs, contracts, diagrams, roadmap       |
| `.claude/`       | [.claude/CLAUDE.md](.claude/CLAUDE.md)               | Agent, command, skill definitions        |

## Commands

```bash
pnpm dev          # Run all apps
pnpm build        # Build all apps
pnpm lint         # Lint all apps
pnpm test         # Run all tests
pnpm format       # Format all files
```

## Verification Requirements

Before completing any implementation:
1. State how you will verify the implementation
2. Run `pnpm lint` and `pnpm test`
3. Run `pnpm build` to ensure no build errors

## DO NOT

- Use `any` type - use proper types or `unknown`
- Skip error handling
- Store secrets in code
- Create components > 200 lines
- Use WebSearch/WebFetch directly - always use `/research` skill instead
- Change workflow stages/sequences without updating `docs/workflow.md` Mermaid diagrams and getting user review
- Auto-resolve open questions — ALL open questions (from PO or TL phases) must be presented to the user for decision via `AskUserQuestion`. The workflow must pause until the user answers

## Established Patterns

<!-- Add project-specific patterns here as they emerge from development -->
<!-- The context-updater agent will populate this section as you build -->

## Agent Rules

### Research Policy (MANDATORY FOR ALL AGENTS)

**ALL research and web searches MUST go through the `researcher` agent.**

This rule applies to:
- Main Claude Code session
- ALL sub-agents spawned via Task tool (Explore, Plan, backend-developer, etc.)
- ANY agent that needs external information

#### How to Do Research

```yaml
# CORRECT: Spawn researcher agent
Task(
  subagent_type: "researcher",
  prompt: "Research topic XYZ"
)

# ALSO CORRECT: Use /research skill (which spawns researcher agent)
/research topic XYZ
```

```yaml
# WRONG: Direct tool usage (NEVER DO THIS)
WebSearch("topic XYZ")
WebFetch("https://example.com/...")
```

#### Why This Matters

1. **Knowledge base indexing** - Researcher updates `knowledgebase/CLAUDE.md` index
2. **Deduplication** - Researcher checks existing research first
3. **Persistence** - Findings saved for future sessions
4. **Staleness tracking** - Research has expiration dates

#### Researcher Agent Responsibilities

The researcher agent (spawned via Task tool) will:
1. Check `knowledgebase/CLAUDE.md` index for existing research
2. Use WebSearch/WebFetch if new research needed
3. Create file in `knowledgebase/{domain}/{topic-slug}.md`
4. Update the index in `knowledgebase/CLAUDE.md`
5. Return summary to calling agent

## Multi-Agent Workflow

Use `/workflow/invoke-director TASK-ID` to orchestrate development tasks. See `.claude/agents/` for available agents.

## Available Commands

- `/build-check` - Build all apps and verify success
- `/lint-fix` - Run formatters and linters
- `/test-all` - Run all tests across monorepo
- `/research <topic> [--task <id>]` - Find or conduct research on technical topics

## Task Master Integration

Use Task Master for project management:

- `task-master list` - Show all tasks
- `task-master next` - Get next task
- `task-master show <id>` - View task details

### Subtask Workflow (Decomposition)

Large or complex tasks can be decomposed into subtasks after TL design. The Director recommends decomposition based on step count and complexity.

**Parent task lifecycle:**
```
backlog -> arch-context? -> po -> tl -> arch-review -> decomposed -> (subtasks execute) -> parent-qa -> context-update -> arch-update -> po-summary -> git-commit -> done
```

**Subtask lifecycle (simplified -- skips PO/TL):**
```
dev-planning -> implementation -> qa-verification -> context-update -> git-commit -> done
```

**Visual workflow**: See [docs/workflow.md](docs/workflow.md) for Mermaid diagrams.

**Directory structure:**
```
docs/tasks/task-{id}-{slug}/
  task.md, insights/, research/     # Parent artifacts
  subtasks/
    {id}.1-{slug}/
      task.md, plan.md
      insights/workflow-history.md
    {id}.2-{slug}/ ...
```

**Key rules:**
- Parent provides "what/why" (PO + TL). Subtasks provide "how" (DEV + code).
- Subtasks share parent's `research/` directory.
- Each subtask is independently committable.
- When all subtasks done -> parent-level integrated QA -> context-update -> arch-update -> po-summary -> done.
- Subtasks skip all architect stages (arch-context, arch-review, arch-update) -- architect governs parent-level only.
- arch-review is a mandatory hard gate after TL design (max 2 rejections before user escalation).
- PO Summary creates `insights/summary.md` and updates `docs/README.md`.

**Decomposition criteria** (Director recommends when ANY of):
- Steps >= 5 (regardless of complexity)
- Steps >= 3 AND high complexity (new module, multiple tech domains, external integrations)
- TL design estimates total effort > 2 days

## Implementation Status

Managed via TaskMaster. Use `task-master list` to see current tasks and their statuses.
