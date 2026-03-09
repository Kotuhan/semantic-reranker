# Project Tasks

This file is the **single source of truth** for all project tasks.
Each task is a folder containing `task.md` and `insights/`.

---

## Task Structure

```
docs/tasks/
├── _template/              # Template for new tasks
│   ├── task.md
│   └── plan.md
├── task-NNN-slug/
│   ├── task.md             # Task definition (PO, TL, DEV, QA sections)
│   └── insights/           # Agent analysis files
│       ├── po-analysis.md  # Product Owner analysis
│       ├── tl-design.md    # Tech Lead design notes
│       └── qa-plan.md      # QA test planning
```

---

## Task Index

| ID | Name | Status | Dependencies | Folder |
|----|------|--------|--------------|--------|
| <!-- Add tasks here --> |

---

## Dependency Graph

```mermaid
graph TD
    %% Add task dependencies here
```

**Legend:** done | in-progress | pending/backlog

---

## Rules

- One task = one folder
- Task definition in `task.md`
- Agent insights go in `insights/` folder
- Task Master tracks status in `.taskmaster/tasks/tasks.json`
- This index should be updated when tasks change status
- New tasks use `_template/` as starting point

---

## Completed Tasks

| ID | Date | Summary |
|----|------|---------|
| <!-- Completed tasks logged here --> |

---

End of Tasks Index
