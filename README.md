# Project Template

Monorepo template with multi-agent Claude Code workflow.

## What's Included

- **Multi-agent workflow**: 11 specialized agents (Director, PO, TL, Architect, QA, Dev, Researcher, etc.)
- **46+ TaskMaster commands**: Project management via Claude Code slash commands
- **8 reusable skills**: Task workflow, research, QA planning, technical design, etc.
- **Architecture framework**: ADR templates, contract specs, diagram conventions
- **Knowledge base**: Persistent research repository with staleness tracking

## Tech Stack

- **Monorepo**: Turborepo + pnpm workspaces
- **Config**: Shared ESLint, TypeScript, Prettier configs

## Prerequisites

- Node.js 22+
- pnpm 9+

## Getting Started

### 1. Install dependencies

```bash
pnpm install
```

### 2. Start developing

```bash
pnpm dev
```

## Commands

| Command | Description |
|---------|-------------|
| `pnpm dev` | Run all apps in dev mode |
| `pnpm build` | Build all apps |
| `pnpm lint` | Lint all apps |
| `pnpm test` | Run all tests |
| `pnpm format` | Format all files |
| `pnpm format:check` | Check formatting |
| `pnpm clean` | Clean all build outputs |

## Project Structure

```
├── apps/                # Application packages (add your apps here)
├── packages/
│   └── config/          # Shared ESLint, TS configs
├── architecture/        # ADRs, contracts, diagrams
├── docs/                # Tasks, workflow docs
├── knowledgebase/       # Research repository
├── .claude/             # Multi-agent workflow config
│   ├── agents/          # 11 agent definitions
│   ├── commands/        # Slash commands
│   └── skills/          # Reusable skills
└── .taskmaster/         # Task Master AI integration
```

## Multi-Agent Workflow

Use `/director` to orchestrate development tasks through the full lifecycle:

```
backlog -> arch-context -> PO analysis -> TL design -> arch-review -> implementation -> QA -> context-update -> commit -> done
```

See [docs/workflow.md](docs/workflow.md) for detailed Mermaid diagrams.

## License

Private - All rights reserved
