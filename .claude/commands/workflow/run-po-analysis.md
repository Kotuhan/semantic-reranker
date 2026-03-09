# Run PO Analysis

Run Product Owner analysis for a task: $ARGUMENTS

## Steps

1. **Parse Task ID**
   - Extract task ID from arguments
   - Verify task directory exists at `docs/tasks/{task-id}/`

2. **Check Prerequisites**
   - Verify task.md exists
   - Check if PO analysis already exists in insights

3. **Invoke PO Agent**
   - Use the Task tool with `subagent_type: "product-owner"`
   - The PO Agent will:
     - Read task context and any PRD documentation
     - Fill Problem Statement, Success Criteria, Acceptance Criteria
     - Define Out of Scope and Open Questions
     - Save output to `docs/tasks/{task-id}/insights/po-agent.md`

4. **Validate Output**
   - Run validation script to check completeness
   - Report any missing sections

5. **Report Results**
   - Show summary of PO analysis
   - Recommend moving to grooming phase (TL Agent)

## Example Usage

```
/workflow/run-po-analysis TASK-001
```

This will generate PO analysis for TASK-001 and save it to the insights directory.
