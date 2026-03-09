# Invoke Director Agent

Orchestrate the development workflow for a task: $ARGUMENTS

## Steps

1. **Parse Task ID**
   - Extract task ID from arguments
   - If no ID provided, list available tasks in `docs/tasks/`

2. **Verify Task Exists**
   - Check if `docs/tasks/{task-id}/` directory exists
   - If not, offer to run `prepare-task.sh` to create it

3. **Invoke Director Agent**
   - Use the Task tool with `subagent_type: "director"`
   - Pass the task ID and request workflow assessment
   - The Director will:
     - Read the task file and existing insights
     - Determine current phase in lifecycle
     - Recommend which agent should act next
     - Validate prerequisites for next phase

4. **Report Results**
   - Show the Director's assessment
   - Display recommended next action
   - Offer to invoke the recommended agent

## Example Usage

```
/workflow/invoke-director TASK-001
```

This will assess TASK-001's current state and recommend the next workflow step.
