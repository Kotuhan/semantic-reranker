# Run QA Verification

Verify implementation against QA test plan after development is complete: $ARGUMENTS

## When to Use

After the backend-developer or frontend-developer agent completes implementation, use this command to:
1. Verify the implementation meets acceptance criteria
2. Run through the QA test cases
3. Update test results in the task file
4. Approve or reject the implementation

## Steps

1. **Parse Arguments**
   - Extract task ID from arguments (e.g., `BE-002`)
   - Locate task file in `docs/tasks/` structure

2. **Gather Context**
   - Read the QA insights: `docs/tasks/{epic}/tasks/{task-id}/BE-{id}/insights/qa-agent.md`
   - Read the task file with acceptance criteria
   - Review the implementation log from DEV section

3. **Invoke QA Agent for Verification**
   - Use the Task tool with `subagent_type: "qa-engineer"`
   - Pass the task ID and request **verification mode** (not planning mode)
   - The QA Agent will:
     - Review each test case against actual implementation
     - Run verification commands (`pnpm test`, `pnpm lint`, `pnpm build`)
     - Check test coverage meets threshold
     - Verify each acceptance criterion has passing tests
     - Document any issues found

4. **Update Task File**
   - Fill in "Test Results" section with PASS/FAIL
   - Document any issues found
   - Update "Definition of Done" checklist

5. **Report Results**
   - If all tests pass: recommend moving task to `done`
   - If tests fail: return task to development with specific issues

## Example Usage

```
/workflow/run-qa-verification BE-002
```

## Verification Checklist (QA Agent fills this)

- [ ] All unit tests pass
- [ ] All E2E tests pass
- [ ] Test coverage > 85% for new code
- [ ] `pnpm lint` passes
- [ ] `pnpm build` passes
- [ ] All acceptance criteria verified
- [ ] No critical bugs open

## Output

Updates the task file's QA Notes section with:
- Test case results (PASS/FAIL for each)
- Issues found (if any)
- Final verdict: APPROVED or NEEDS_WORK
