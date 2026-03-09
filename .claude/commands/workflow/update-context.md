# Update Context After Task

Analyze changes from completed task and update CLAUDE.md files: $ARGUMENTS

## Steps

1. **Parse Arguments**
   - Optional: Task ID (e.g., `TASK-001`)
   - Optional: Commit range (e.g., `HEAD~5..HEAD` or `abc123..def456`)
   - If no arguments, analyze uncommitted changes + last 3 commits

2. **Gather Change Context**
   - If Task ID provided, check `docs/tasks/{task-id}/` for context
   - Run `git diff` to understand what changed
   - Identify modified directories and files

3. **Invoke Context Updater Agent**
   - Use the Task tool with `subagent_type: "context-updater"`
   - Pass the commit range or task reference
   - The agent will:
     - Analyze the diff for new patterns
     - Identify which CLAUDE.md files need updates
     - Generate specific content to add/modify/remove
     - Recommend new deep CLAUDE.md files if needed

4. **Review and Apply**
   - Present the recommended updates to user
   - Allow user to approve/reject each update
   - Apply approved changes to CLAUDE.md files

## Example Usage

```
# After completing a task
/workflow/update-context TASK-005

# After a series of commits
/workflow/update-context HEAD~5

# Analyze current uncommitted changes
/workflow/update-context
```

## When to Use

**REQUIRED**: This is a mandatory step in the workflow after QA verification passes.

- After marking a task as `done` (mandatory per Director workflow)
- After merging a PR
- When you've made significant changes and want to capture learnings

## Workflow Integration

This is the FINAL step in the task lifecycle:
```
development → review (QA) → done → context update (YOU ARE HERE)
```

Only after context update is the task truly complete.

## Integration

This command pairs with:
- `/workflow/invoke-director` - for task orchestration
- `best-practices-reviewer` agent - for full codebase context audit
