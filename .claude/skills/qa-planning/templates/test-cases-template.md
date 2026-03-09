# Test Cases Template

## Test Case Format

```markdown
### TC-{task-id}-{number}: {Test Case Name}

**Priority:** Critical / High / Medium / Low
**Type:** Unit / Integration / E2E / Manual
**Automated:** Yes / No / Planned

**Preconditions:**
- {Required state before test}
- {User must be logged in, etc.}

**Test Data:**
- {Specific values to use}
- {Test user credentials if needed}

**Steps:**
1. {First action}
2. {Second action}
3. {Continue...}

**Expected Result:**
- {What should happen}
- {Specific UI changes}
- {Data changes}

**Actual Result:** _To be filled during execution_
**Status:** Pending / Pass / Fail / Blocked
**Notes:** _Any observations_
```

---

## Test Cases by Acceptance Criterion

### AC-1: {First Acceptance Criterion}

#### TC-{task-id}-001: Happy Path
**Priority:** Critical
**Type:** E2E

**Preconditions:**
- User is logged in
- User has remaining usage in trial

**Test Data:**
- Input: "Sample test input" (typical user input)

**Steps:**
1. Navigate to the feature page
2. Enter data into the input field
3. Click the "Submit" button

**Expected Result:**
- Result appears within 3 seconds
- Original input preserved above
- Usage count decremented

**Actual Result:** _____________
**Status:** Pending

---

#### TC-{task-id}-002: Empty Input Validation
**Priority:** Medium
**Type:** Unit

**Preconditions:**
- User is on the feature page

**Test Data:**
- Input: "" (empty string)

**Steps:**
1. Leave input field empty
2. Click "Submit" button

**Expected Result:**
- Validation error shown
- "Please enter a value" displayed
- No API call made

**Actual Result:** _____________
**Status:** Pending

---

#### TC-{task-id}-003: Maximum Length Input
**Priority:** Medium
**Type:** Integration

**Preconditions:**
- User is logged in

**Test Data:**
- Message: 2001 characters (exceeds limit)

**Steps:**
1. Paste message exceeding 2000 characters
2. Attempt to submit

**Expected Result:**
- Validation error shown
- Character count displays overflow amount
- Submit button disabled

**Actual Result:** _____________
**Status:** Pending

---

## Test Coverage Matrix

| Acceptance Criterion | Test Case(s) | Type | Priority | Automated |
|---------------------|--------------|------|----------|-----------|
| AC-1 | TC-001, TC-002, TC-003 | E2E, Unit, Integration | Critical, Medium, Medium | No, Yes, Yes |
| AC-2 | | | | |
| AC-3 | | | | |

## Edge Cases

| Scenario | Test Case | Priority |
|----------|-----------|----------|
| Network timeout | TC-xxx | High |
| Concurrent requests | TC-xxx | Medium |
| Session expiry | TC-xxx | High |
| Rate limiting | TC-xxx | Medium |

## Negative Tests

| Scenario | Test Case | Expected Behavior |
|----------|-----------|-------------------|
| Invalid input | TC-xxx | Validation error |
| Unauthorized | TC-xxx | 401 response |
| Server error | TC-xxx | Graceful error message |
