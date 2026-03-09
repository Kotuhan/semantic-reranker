# Prepare Task for Development

Prepare a task for development by gathering all insights: $ARGUMENTS

## Steps

1. **Parse Task ID**
   - Extract task ID from arguments
   - Verify task directory exists at `docs/tasks/{task-id}/`

2. **Validate All Prerequisites**
   - Check PO analysis: `docs/tasks/{task-id}/insights/po-agent.md`
   - Check TL design: `docs/tasks/{task-id}/insights/tl-agent.md`
   - Check QA plan: `docs/tasks/{task-id}/insights/qa-agent.md`
   - Run full validation: `bash .claude/skills/task-workflow/scripts/validate-insights.sh {task-id}`

3. **Generate Development Summary**
   - Compile implementation steps from TL design
   - Include acceptance criteria from PO
   - Include test cases from QA
   - Create development checklist

4. **Determine Scope**
   - Analyze if task is FE-only, BE-only, or Full-Stack
   - Recommend which Developer agent(s) to invoke for guidance

5. **Invoke Developer Agents (Optional)**
   - If requested, invoke FE Developer and/or BE Developer agents
   - They will provide implementation guidance based on TL steps
   - Save to `docs/tasks/{task-id}/insights/fe-dev.md` and/or `be-dev.md`

6. **Update Task Status**
   - If using Task Master, update status to `in-progress`
   - Update task.md status in frontmatter

7. **Report Results**
   - Show complete development context
   - Display implementation steps
   - Show test cases for verification
   - Provide command to start implementation

## Example Usage

```
/workflow/prepare-for-dev TASK-001
```

This will validate all prerequisites and prepare TASK-001 for development.

## Output Format

```markdown
# Development Ready: TASK-001

## Summary
{From PO analysis}

## Implementation Steps
1. {Step from TL design}
2. ...

## Test Cases to Satisfy
- TC-001: {test case}
- TC-002: {test case}

## Definition of Done
- [ ] All steps implemented
- [ ] All tests pass
- [ ] Code reviewed
- [ ] QA verified

## Ready to Implement!
```
