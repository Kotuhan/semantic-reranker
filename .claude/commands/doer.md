# DOER - Implementation Agent

Execute implementation plans with minimal context: $ARGUMENTS

## Purpose

The DOER agent implements code changes from a plan.md file. It starts with minimal context and only reads files as needed for modification, keeping token usage low.

## Instructions

### Step 1: Determine Target

If `$ARGUMENTS` is provided:
- Use it as the task folder path (e.g., "task-001" or "docs/tasks/task-001-esphome-setup")

If no arguments:
- Read `.taskmaster/tasks/tasks.json`
- Find task with stage "dev-planning" (ready for implementation)
- If no task at dev-planning stage, report and stop

### Step 2: Validate Prerequisites

1. Check that `{folder}/plan.md` exists
2. Verify plan.md has file-by-file implementation structure
3. If missing or incomplete, report what's needed and stop

### Step 3: Minimal Context Load

**CRITICAL: Start with minimal context**

1. Read ONLY `{folder}/plan.md`
2. Do NOT read:
   - task.md (unless plan.md explicitly references it)
   - insights/*.md files
   - research/*.md files
   - PRD.md
   - CLAUDE.md files
3. Parse the plan to understand:
   - Files to create
   - Files to modify
   - Order of changes
   - Verification steps

### Step 4: Execute Plan

For each file in the plan:

1. **Before modifying**: Read only that specific file
2. **Make changes**: Follow plan.md exactly
3. **Verify**: Run any file-specific verification from the plan
4. **Track**: Note the file in your summary

Implementation rules:
- Follow the plan exactly - do not improvise
- If plan is unclear on a detail, ask the user immediately
- If a file doesn't exist but should be modified, ask the user
- Create parent directories as needed for new files
- Use existing code patterns when the plan references them

### Step 5: Run Verification (MANDATORY BUILD GATE)

**CRITICAL: This step is MANDATORY regardless of what the plan specifies.**

Always run ALL of these commands and verify they pass:

```bash
pnpm lint          # Must pass with 0 errors
pnpm test          # All tests must pass
pnpm build         # Both API and Web must compile
```

Additionally, execute any plan-specific verification steps (e.g., validate configuration files).

**HARD GATE**: If `pnpm build` fails, you MUST:
1. Analyze the build error
2. Fix the issue
3. Re-run `pnpm build` until it passes
4. Only then proceed to Step 6

Do NOT skip this step. Do NOT proceed if build fails. Do NOT mark implementation as complete with a broken build.

### Step 6: Report Summary

Provide implementation summary:

```
## Implementation Complete

### Files Created
- path/to/new/file.ts
- path/to/another/file.yaml

### Files Modified
- path/to/existing/file.ts (lines 10-25)
- path/to/config.yaml (added new section)

### Files Read (for context)
- plan.md
- path/to/existing/file.ts (before modification)

### Verification Results
- Build: PASS/FAIL
- Lint: PASS/FAIL
- Tests: PASS/FAIL (if applicable)

### Issues Encountered
- (any problems or deviations from plan)
```

### Step 7: Update Stage (if successful)

If implementation succeeded:
1. Update task stage to "implementation" in `.taskmaster/tasks/tasks.json`
2. Append to `{folder}/insights/workflow-history.md`:
   ```
   ## {date} {time} - Implementation
   - Agent: doer
   - Result: completed
   - Summary: Implemented {N} files per plan.md
   - Next: qa-verification
   - Files read: {list}
   - Files created: {list}
   - Files modified: {list}
   - Verification: {results}
   ```

## Error Handling

### Plan Unclear
If the plan doesn't specify something clearly:
- Ask the user immediately
- Do not guess or improvise
- Document the clarification in the summary

### File Conflicts
If a file exists but plan says to create:
- Ask user: overwrite, merge, or skip?
- Document decision in summary

### Verification Failures
If verification fails:
- Report the failure with full error output
- Attempt to fix the issue (up to 3 attempts)
- If fixed: re-run verification and proceed
- If cannot fix after 3 attempts: Do NOT update stage to "implementation", report to user
- **NEVER** proceed with a broken build - this is a hard gate

## Example Usage

```
/doer                           # Auto-detect task at dev-planning stage
/doer task-001                  # Implement task-001
/doer docs/tasks/task-001-esphome-setup  # Full path
```

## Context Efficiency

This agent is designed for minimal context usage:

| What | Read? |
|------|-------|
| plan.md | Yes (always) |
| Files being modified | Yes (just before modification) |
| task.md | No (unless plan references) |
| insights/*.md | No |
| research/*.md | No |
| PRD.md | No |
| Other codebase files | Only if plan explicitly requires |

This keeps the agent focused and token-efficient while still having all information needed to implement correctly.
