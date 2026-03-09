# Run QA Planning

Run QA Engineer test planning for a task: $ARGUMENTS

## Steps

1. **Parse Task ID**
   - Extract task ID from arguments
   - Verify task directory exists at `docs/tasks/{task-id}/`

2. **Check Prerequisites**
   - Verify PO analysis exists (for acceptance criteria)
   - Verify TL design exists (for technical context)
   - If missing, recommend running previous agents first

3. **Invoke QA Agent**
   - Use the Task tool with `subagent_type: "qa-engineer"`
   - The QA Agent will:
     - Read PO acceptance criteria and TL technical notes
     - Derive test cases from acceptance criteria
     - Create coverage matrix and regression plan
     - Define Definition of Done checklist
     - Save output to `docs/tasks/{task-id}/insights/qa-agent.md`

4. **Validate Output**
   - Run validation script to check completeness
   - Report any missing sections

5. **Report Results**
   - Show summary of test planning
   - Show test case count and coverage
   - Recommend moving to development phase

## Example Usage

```
/workflow/run-qa-planning TASK-001
```

This will generate QA test plan for TASK-001 based on PO and TL insights.
