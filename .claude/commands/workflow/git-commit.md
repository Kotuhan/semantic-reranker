# Git Commit Task Changes

Commit all changes from a completed task: $ARGUMENTS

## Purpose

Automatically stage and commit task-related files with a structured commit message. This is a mandatory workflow stage that runs after context-update and before marking a task as done.

## Instructions

### Step 1: Determine Target Task

If `$ARGUMENTS` is provided:
- Use it as the task ID (e.g., "8" or "task-008")
- Look up the task in `.taskmaster/tasks/tasks.json`

If no arguments:
- Read `.taskmaster/tasks/tasks.json`
- Find task at stage `context-update` (ready for commit)
- If no task at that stage, report and stop

### Step 2: Gather Task Context

1. Read the task entry from `.taskmaster/tasks/tasks.json` to get `folder` and `title`
2. Determine if this is a **subtask** or **parent/standard task**:
   - **Subtask ID format**: `{parentId}.{N}` (e.g., `20.1`, `20.2`)
   - **Subtask folder**: `docs/tasks/{parent-folder}/subtasks/{subtaskId}-{slug}/`
   - **Standard task folder**: `docs/tasks/{folder}/`
3. Read the appropriate `insights/workflow-history.md`:
   - For subtask: `docs/tasks/{parent-folder}/subtasks/{subtaskId}-{slug}/insights/workflow-history.md`
   - For standard/parent task: `docs/tasks/{folder}/insights/workflow-history.md`
4. Extract from workflow-history:
   - All "Files Created" and "Files Modified" paths from each stage entry
   - The "Task Complete" summary (if exists) or the latest stage summaries
   - Task/subtask title for commit message

### Step 3: Identify Files to Commit

Run `git status` to see all changed files. Then categorize:

**ALWAYS include (if changed):**
- `docs/tasks/{folder}/**` — all task artifacts (task.md, plan.md, insights/, research/)
- `.taskmaster/tasks/tasks.json` — task status updates
- Files explicitly listed in workflow-history "Files Created" / "Files Modified" entries

**Include if changed (documentation updates):**
- `CLAUDE.md` (root)
- `*/CLAUDE.md` (module-level, e.g., `homeassistant/CLAUDE.md`, `notifications/CLAUDE.md`)

**Include if changed (implementation files):**
- Any source/config files listed in workflow-history entries
- Example: `homeassistant/config/automations.yaml`, `notifications/src/**/*.ts`

**NEVER include (runtime/generated files):**
- `*.db`, `*.db-shm`, `*.db-wal` (databases)
- `*.log`, `*.log.*` (log files)
- `.storage/` (HA internal storage)
- `.ha_run.lock` (HA lock file)
- `node_modules/`, `.venv/`, `__pycache__/`
- `.env` (secrets)

### Step 4: Generate Commit Message

Build a commit message using this format:

```
{Action verb} {short description} ({task-id})

{2-3 line summary of what was implemented/changed}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**Action verb** selection:
- New feature/automation → "Implement"
- Bug fix → "Fix"
- Documentation only → "Document"
- Refactoring → "Refactor"
- Configuration → "Configure"

**Examples:**

Standard task:
```
Implement load control automation (task-008)

Add HA automations to turn off boiler and heater plugs during grid
outages and restore them when power returns with SOC threshold checks.
Includes 4 automations, 3 input entities, and event integration.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Subtask:
```
Scaffold Next.js project with glassmorphism design system (task-020.1)

Create web-ui/ directory with Next.js 15, Tailwind CSS, glassmorphism
styles, Docker multi-stage build, and docker-compose integration.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### Step 5: Update Workflow History (BEFORE committing)

Append a "Git Commit" entry to `docs/tasks/{folder}/insights/workflow-history.md`:

```markdown
---

## {YYYY-MM-DD} {HH:MM} - Git Commit

- **Agent**: director (git-commit)
- **Result**: completed
- **Summary**: Committed {N} files for {task-id}
- **Files committed**: {list of staged files}
- **Commit message**: {first line of commit message}
- **Next stage**: done
```

**IMPORTANT**: Write this entry BEFORE running `git commit` so it's included in the commit.

### Step 5b: Update Task Stage to Done (BEFORE committing)

Update `.taskmaster/tasks/tasks.json` **before** staging files so the updated status is included in the commit:
- Set task `stage` to `"done"`
- Set task `status` to `"done"`

For subtasks: update the subtask entry inside the parent task's `subtasks` array (both `stage` and `status` fields).

This prevents stale statuses when the git-commit runs as the final action in a session with no director turn after it.

### Step 6: Stage and Commit

1. Stage identified files using `git add` with explicit file paths:
   ```bash
   git add path/to/file1 path/to/file2 ...
   ```
   - **NEVER** use `git add -A` or `git add .`
   - Stage files individually by name

2. Verify staged files with `git diff --cached --stat`

3. Commit using HEREDOC format:
   ```bash
   git commit -m "$(cat <<'EOF'
   Commit message here.

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
   EOF
   )"
   ```

4. Verify with `git log --oneline -1`

### Step 7: Report Results

```
## Git Commit Complete

- **Commit**: {hash} {first line}
- **Files committed**: {count}
- **Task**: {task-id} - {title}

### Staged Files
- {list of committed files}

### Not Staged (excluded)
- {runtime/unrelated files that were skipped}
```

### Step 8: Verify Task Stage

Verify that `.taskmaster/tasks/tasks.json` was updated in Step 5b (stage and status set to `"done"`).
If not already updated (e.g., Step 5b was skipped), update now:
- Set task `stage` to `"done"`
- Set task `status` to `"done"`

**Note**: Step 5b handles this before the commit so tasks.json is included. This step is a safety net.

## Error Handling

### No Changed Files
If `git status` shows no task-related changes:
- Report "No changes to commit for {task-id}"
- Skip commit, proceed to done stage
- This can happen if changes were already committed manually

### Commit Fails
If `git commit` fails (e.g., pre-commit hook):
- Report the error
- Do NOT update stage
- Let user decide how to proceed

### Mixed Changes
If working directory has changes from multiple tasks:
- Only stage files related to the target task
- Report which files were excluded and why
- Other task changes remain unstaged

## Example Usage

```
/workflow/git-commit              # Auto-detect task at context-update stage
/workflow/git-commit 8            # Commit task-008 changes
/workflow/git-commit task-008     # Same, with prefix
```

## Integration

This command is part of the mandatory completion sequence:
```
implementation → qa-verification → context-update → po-summary → git-commit → done
```

The Director automatically invokes this after po-summary completes (with user approval).