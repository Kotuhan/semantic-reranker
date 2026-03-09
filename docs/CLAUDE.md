# Documentation Directory

Central documentation for the project.

## Directory Structure

```
docs/
├── CLAUDE.md                  # This file
├── tasks/                     # Task management (see below)
│   ├── README.md              # Task index with dependency graph (source of truth)
│   └── _template/             # Template for new tasks
├── workflow.md                # Workflow stages and Mermaid diagrams
└── workflow.mmd               # Mermaid source file
```

## Task Conventions

### Task Folder Format

Every task follows this structure:
```
task-NNN-slug/
├── task.md                    # Task definition (PO, TL, DEV, QA sections)
└── insights/                  # Agent analysis files (always present)
    ├── workflow-history.md    # Stage transitions (source of truth for status)
    ├── arch-context.md        # Architect context analysis
    ├── po-analysis.md         # Product Owner analysis
    ├── tl-design.md           # Tech Lead design
    ├── arch-review.md         # Architecture review result
    ├── qa-plan.md             # QA test plan and verification
    └── dev-notes.md           # Developer implementation notes
```

### Insight File Naming Convention

| File | Agent | Content |
|------|-------|---------|
| `workflow-history.md` | director | Stage transitions, source of truth for task stage |
| `arch-context.md` | system-architect | Architecture analysis before PO |
| `po-analysis.md` | product-owner | Requirements analysis, acceptance criteria |
| `tl-design.md` | team-lead | Technical design, implementation steps |
| `arch-review.md` | system-architect | Architecture review (approve/reject) |
| `qa-plan.md` | qa-engineer | Test planning and verification results |
| `dev-notes.md` | developer | Implementation notes, decisions during coding |
| `summary.md` | product-owner | Post-completion summary (PO Summary stage) |

### Task Numbering

Tasks are numbered sequentially starting from task-001.

### Empty Insights Directories

Every task folder has an `insights/` directory, even if no insight files exist yet. Use `.gitkeep` for empty insights directories to maintain structural consistency.

## DO NOT

- Use old insight naming (`po-agent.md`, `tl-agent.md`, `qa-agent.md`) -- use `po-analysis.md`, `tl-design.md`, `qa-plan.md`
- Trust `tasks.json` stage over `workflow-history.md` -- workflow-history is the source of truth
