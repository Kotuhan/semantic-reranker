# Claude Code Configuration

This directory contains the multi-agent workflow configuration for the project.

## Directory Structure

```
.claude/
├── CLAUDE.md              # This file
├── settings.json          # Permission allow/deny lists (committed)
├── settings.local.json    # Local overrides (committed, but user-specific)
├── .mcp.json              # MCP server connections
├── agents/                # Agent role definitions (11 agents)
├── commands/              # Slash commands (/build-check, /lint-fix, etc.)
│   ├── tm/                # TaskMaster CLI commands
│   └── workflow/          # Workflow step commands
└── skills/                # Reusable skill definitions (8 skills)
```

## Agents

| Agent | File | Role |
|-------|------|------|
| director | `agents/director.md` | Workflow orchestrator - determines next stage, invokes agents |
| system-architect | `agents/system-architect.md` | Architecture governance (arch-context, arch-review, arch-update) |
| product-owner | `agents/product-owner.md` | Requirements analysis, acceptance criteria |
| team-lead | `agents/team-lead.md` | Technical design, implementation steps |
| qa-engineer | `agents/qa-engineer.md` | Test planning and verification |
| backend-developer | `agents/backend-developer.md` | NestJS/Prisma implementation |
| frontend-developer | `agents/frontend-developer.md` | Next.js/React implementation |
| nestjs-architect | `agents/nestjs-architect.md` | NestJS-specific architecture patterns |
| researcher | `agents/researcher.md` | Knowledge base management, web research |
| context-updater | `agents/context-updater.md` | Post-task CLAUDE.md updates |
| claude-best-practices | `agents/claude-best-practices.md` | CLAUDE.md optimization reviewer |

## Commands

| Command | File | What it does |
|---------|------|--------------|
| `/build-check` | `commands/build-check.md` | Runs `pnpm build`, verifies artifacts |
| `/lint-fix` | `commands/lint-fix.md` | Runs `pnpm format` + `pnpm lint` |
| `/test-all` | `commands/test-all.md` | Runs `pnpm test`, per-app breakdown |
| `/db-migrate` | `commands/db-migrate.md` | Prisma migration workflow (multi-step) |
| `/research` | `commands/research.md` | Spawns researcher agent |
| `/director` | `commands/director.md` | Invokes director for task orchestration |
| `/doer` | `commands/doer.md` | Implementation agent |

## Skills

| Skill | Directory | Purpose |
|-------|-----------|---------|
| task-workflow | `skills/task-workflow/` | Task directory setup, validation scripts, subtask creation |
| system-architect | `skills/system-architect/` | Architecture review skill |
| research | `skills/research/` | Research skill with Context7 integration |
| po-analysis | `skills/po-analysis/` | Product Owner analysis templates |
| qa-planning | `skills/qa-planning/` | QA test planning templates |
| technical-design | `skills/technical-design/` | TL design templates |
| frontend-developer | `skills/frontend-developer/` | Frontend patterns and templates |

## Conventions

### Agent File Structure

All agent files follow this structure:
1. Role description (who the agent is)
2. Operating modes or responsibilities
3. Decision logic / workflow rules
4. Output format templates
5. DO / DO NOT rules

### Workflow Source of Truth

- **workflow-history.md** is the source of truth for task stage (NOT tasks.json)
- If workflow-history is empty but task.md has content, treat as "legacy" content
- Every stage transition MUST be logged in workflow-history

### Mandatory Post-Implementation Sequence

After implementation completes, these stages are MANDATORY and AUTOMATIC (no user prompting):
```
implementation -> qa-verification -> context-update -> arch-update -> po-summary -> git-commit -> done
```

### Permission Updates

When adding new tools or integrations:
- Add tool permissions to `settings.json` (allow list)
- Never add destructive commands (`rm -rf`, `sudo`, `chmod 777`)
- MCP tool connections go in `.mcp.json`

## DO NOT

- Edit `decisions/_template.md` in `architecture/` (it is immutable)
- Skip workflow-history updates when transitioning stages
- Trust tasks.json stage over workflow-history
- Assume task.md content is validated if workflow-history is empty
- Ask user "should I continue?" during the mandatory post-implementation sequence
