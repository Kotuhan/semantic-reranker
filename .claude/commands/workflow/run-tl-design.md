# Run TL Technical Design

Run Team Lead technical design for a task: $ARGUMENTS

## Steps

1. **Parse Task ID**
   - Extract task ID from arguments
   - Verify task directory exists at `docs/tasks/{task-id}/`

2. **Check Prerequisites**
   - Verify PO analysis exists at `docs/tasks/{task-id}/insights/po-agent.md`
   - If missing, recommend running PO analysis first

3. **Invoke TL Agent**
   - Use the Task tool with `subagent_type: "team-lead"`
   - The TL Agent will:
     - Read PO analysis and acceptance criteria
     - Explore the codebase for existing patterns
     - Create Technical Notes and Implementation Steps
     - Define test strategy and risk assessment
     - Save output to `docs/tasks/{task-id}/insights/tl-agent.md`

4. **Validate Output**
   - Run validation script to check completeness
   - Report any missing sections

5. **Report Results**
   - Show summary of technical design
   - Show implementation steps overview
   - Recommend next steps (QA planning or development)

## Example Usage

```
/workflow/run-tl-design TASK-001
```

This will generate technical design for TASK-001 based on PO requirements.
