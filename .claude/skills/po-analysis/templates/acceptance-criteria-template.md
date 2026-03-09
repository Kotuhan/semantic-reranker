# Acceptance Criteria Template

## Format: Given/When/Then

Each acceptance criterion should follow this structure:

```
* Given [precondition/context]
  When [action performed]
  Then [expected result]
```

## Guidelines

### Preconditions (Given)
- State the initial context clearly
- Include user state (logged in, on specific page, etc.)
- Include data state (existing records, settings, etc.)

### Actions (When)
- Describe the specific user action
- Be precise about what is clicked, entered, or triggered
- Include any parameters or inputs

### Expected Results (Then)
- Describe observable outcomes
- Include what the user should see/experience
- Include any data changes that should occur
- Be specific about timing if relevant

## Acceptance Criteria Checklist

For each criterion, verify:
- [ ] Is it testable by QA?
- [ ] Is it independent of implementation?
- [ ] Is it specific enough to verify?
- [ ] Does it have clear pass/fail criteria?

---

## Examples

### Example 1: Feature Criterion
```
* Given a logged-in user on the Dashboard page
  When they fill out the form and click "Submit"
  Then the processed result appears within 3 seconds
  And the original input is preserved above the result
```

### Example 2: Error Handling
```
* Given a user with no internet connection
  When they attempt to submit a form
  Then an offline indicator is shown
  And cached data (if any) is still accessible
```

### Example 3: Data Validation
```
* Given a user entering a message longer than 2000 characters
  When they attempt to submit
  Then a validation error is shown
  And the character count displays how many characters exceed the limit
```

### Example 4: State Transition
```
* Given a user on the free trial
  When they reach the usage limit
  Then an upgrade modal appears
  And the usage counter resets after subscription
```

---

## Anti-patterns to Avoid

**Too Vague:**
```
* When the user submits
  Then it should work correctly
```

**Implementation-Specific:**
```
* When the POST /api/items endpoint is called
  Then the database record is created with status 'completed'
```

**Untestable:**
```
* The output should be good quality
```
