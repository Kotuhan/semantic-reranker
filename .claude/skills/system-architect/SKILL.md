---
name: system-architect
description: Architectural governance for the project. Reviews designs against ADRs and contracts, provides pre-PO context, and maintains architecture docs.
---

# System Architect Skill

Provides architectural governance through the system-architect agent. Three modes cover the full task lifecycle: pre-PO context, post-TL review gate, and post-task architecture maintenance.

## CRITICAL: How to Execute This Skill

**When this skill is invoked, you MUST spawn the system-architect agent via Task tool.**

```yaml
# arch-context mode (default)
Task(
  subagent_type: "system-architect",
  prompt: "Run in arch-context mode for task in {folder}.
    1. Read architecture/CLAUDE.md and architecture/overview.md
    2. Read relevant ADRs and contracts
    3. Read task.md for scope
    4. Write insights/arch-context.md with constraints, existing decisions, integration points
    Return summary of files read and written."
)

# arch-review mode
Task(
  subagent_type: "system-architect",
  prompt: "Run in arch-review mode for task in {folder}. Iteration: {1|2}.
    1. Read architecture/CLAUDE.md, overview.md, all ADRs, relevant contracts
    2. Read insights/tl-design.md and insights/po-analysis.md
    3. Validate design against ADRs, contracts, conventions
    4. Write insights/arch-review.md with APPROVED or REJECTED verdict
    If REJECTED: cite specific references, provide constraints, suggest alternatives.
    Return summary of files read and written."
)

# arch-update mode
Task(
  subagent_type: "system-architect",
  prompt: "Run in arch-update mode for task in {folder}.
    1. Read architecture/CLAUDE.md and all architecture/ files
    2. Read insights/workflow-history.md, plan.md
    3. Assess architectural impact
    4. Update architecture/ files if needed
    5. Create retroactive ADRs for implicit decisions
    6. Write insights/arch-update.md
    Return summary of files read, written, and updated."
)
```

**DO NOT:**
- Use this skill without spawning the system-architect agent
- Bypass the architecture/ directory reading step
- Create ADRs without checking existing ones for duplicates

## Usage

### Direct Invocation
```
/architect <task-id>              # Default: arch-context mode
/architect review <task-id>       # arch-review mode (post-TL gate)
/architect update <task-id>       # arch-update mode (post-task)
```

### Examples
```bash
# Pre-PO architectural context for a cross-component task
/architect task-010

# Review TL design against architecture (mandatory gate)
/architect review task-008

# Update architecture docs after task completion
/architect update task-009
```

## Modes

| Mode | When Used | Trigger | Output |
|------|-----------|---------|--------|
| arch-context | Before PO analysis | Director (optional, cross-component tasks) | `insights/arch-context.md` |
| arch-review | After TL design | Director (mandatory, all tasks) | `insights/arch-review.md` |
| arch-update | After context-update | Director (mandatory, all tasks) | `insights/arch-update.md` |

## Templates

- **ADR template**: `architecture/decisions/_template.md` (MADR format with Triggered-By field)
- **Output formats**: Defined in the system-architect agent definition

## Integration

| Consumer | How |
|----------|-----|
| **Director Agent** | Invokes automatically at arch-context, arch-review, arch-update stages |
| **User** | Manual invocation via `/architect` |
| **Team Lead Agent** | Receives arch-review feedback when design is rejected |

### Architecture Knowledge Base

The agent reads from and writes to `architecture/`:
- `decisions/` — ADRs (MADR format)
- `contracts/` — Event schemas, API contracts
- `diagrams/` — Mermaid architecture diagrams
- `roadmap/` — Migration and evolution plans
- `runbooks/` — Operational recovery procedures
- `overview.md` — Living system state document
