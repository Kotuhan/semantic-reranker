---
name: task-workflow
description: Automates multi-agent task workflow orchestration. Prepares task directories, validates agent outputs, and coordinates handoffs between roles.
---

# Task Workflow Skill

Automates the development workflow by orchestrating agents and validating outputs.

## Usage

### Prepare New Task
Initialize task directory structure from template:
```bash
bash .claude/skills/task-workflow/scripts/prepare-task.sh {task-id}
```

### Validate Agent Insights
Check that all required sections are filled:
```bash
bash .claude/skills/task-workflow/scripts/validate-insights.sh {task-id} {agent-name}
```

### Run Full Workflow
Execute all agents in sequence for a task:
1. Invoke Director to assess current state
2. Director delegates to appropriate role agent
3. Each agent saves output to insights directory
4. Director validates and recommends next step

## Scripts

### prepare-task.sh
Creates task directory structure:
```
docs/tasks/{task-id}/
├── task.md           # Copy of _template.md
├── plan.md           # Empty implementation plan
└── insights/         # Agent outputs directory
```

### prepare-subtask.sh
Creates subtask directory structure under a parent task:
```bash
bash .claude/skills/task-workflow/scripts/prepare-subtask.sh {parent-folder} {subtask-id} {slug}
# Example:
bash .claude/skills/task-workflow/scripts/prepare-subtask.sh task-020-custom-web-ui 020.1 scaffolding
```

Creates:
```
docs/tasks/{parent-folder}/subtasks/{subtask-id}-{slug}/
├── task.md                    # From subtask template (lightweight)
├── plan.md                    # Empty (filled during dev-planning)
└── insights/
    └── workflow-history.md    # Empty (tracks subtask stages)
```

### validate-insights.sh
Validates agent output completeness:
- PO Agent: Problem, Success Criteria, Acceptance Criteria, Out of Scope
- TL Agent: Technical Notes, Implementation Steps
- QA Agent: Test Cases, Coverage Matrix
- Developer Agents: Files Modified, Tests Added, Verification

## Subtask Workflow Pattern

Large tasks can be decomposed into subtasks after TL design. Each subtask follows a simplified workflow.

### When to Decompose
The Director recommends decomposition based on:
- **Step count**: >= 5 steps always, >= 3 steps with high complexity
- **Complexity factors**: New module creation (HIGH), multiple tech domains (HIGH), external integrations (MEDIUM), config-only changes (LOW)

### Subtask Lifecycle
```
Parent:  backlog → arch-context? → po → tl → arch-review → decomposed → (wait) → parent-qa → context-update → arch-update → po-summary → git-commit → done
Subtask: dev-planning → implementation → qa-verification → context-update → git-commit → done
```

**Note**: Subtasks skip all architect stages (arch-context, arch-review, arch-update). The System Architect governs at the parent task level only.

### Workflow Diagram (Mermaid)

Visual diagrams live in [docs/workflow.md](../../../docs/workflow.md).

**MANDATORY**: When ANY workflow stage, sequence, or agent assignment changes:
1. Update `docs/workflow.md` Mermaid diagrams to reflect the change
2. Update the Quick Reference section at the bottom of `docs/workflow.md`
3. Present the updated diagram to the user for review and approval before committing
4. This is a blocking gate — workflow changes MUST NOT be committed without diagram review

### Key Rules
- Parent provides "what/why" (PO + TL). Subtasks provide "how" (DEV + code).
- Subtasks share parent's `research/` directory.
- Each subtask is independently committable.
- Git commit per subtask: `{Verb} {description} (task-{parentId}.{N})`
- When all subtasks done → parent-level integrated QA → context-update → arch-update → po-summary → done.
- arch-review is a mandatory hard gate after TL design (max 2 rejections before user escalation).
- PO Summary creates `insights/summary.md` and updates `docs/README.md`.

## Integration

This skill integrates with:
- Task Master for status management
- Director agent for orchestration
- System Architect agent for arch-context, arch-review, and arch-update stages
- Role-specific agents for analysis
