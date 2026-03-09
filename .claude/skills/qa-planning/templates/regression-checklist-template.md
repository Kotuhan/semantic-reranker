# Regression Checklist Template

## Impact Analysis

### Directly Affected Areas

| Area | Reason | Risk Level |
|------|--------|------------|
| | Changes to X | High |
| | Uses shared Y | Medium |
| | Depends on Z | Low |

### Potentially Affected Areas

| Area | Reason | Risk Level |
|------|--------|------------|
| | Shares database with X | Medium |
| | Uses same API endpoint | Low |

---

## Regression Test Suite

### Critical Path Tests (Must Pass)

- [ ] **Auth Flow**: Login, logout, session persistence
- [ ] **Core Feature A**: Primary feature workflow
- [ ] **Core Feature B**: Secondary feature workflow
- [ ] **Billing**: Subscription status check (if applicable)
- [ ] **Onboarding**: New user flow

### Feature-Specific Tests

Based on impact analysis, run these additional tests:

#### Backend
- [ ] `apps/api/test/auth.e2e-spec.ts`
- [ ] `apps/api/test/{feature-a}.e2e-spec.ts`
- [ ] `apps/api/test/{feature-b}.e2e-spec.ts`
- [ ] `apps/api/test/{affected-module}.e2e-spec.ts`

#### Frontend
- [ ] `apps/web/tests/e2e/auth.spec.ts`
- [ ] `apps/web/tests/e2e/{feature-a}.spec.ts`
- [ ] `apps/web/tests/e2e/{feature-b}.spec.ts`

### Performance Checks

- [ ] API response times within SLA
- [ ] No memory leaks in long-running sessions
- [ ] Database query performance unchanged

---

## Execution Tracking

### Pre-Release Checklist

| Check | Status | Notes |
|-------|--------|-------|
| All unit tests pass | | |
| All integration tests pass | | |
| Critical path E2E pass | | |
| No new console errors | | |
| No new accessibility issues | | |
| Performance metrics unchanged | | |

### Test Execution Log

| Date | Tester | Environment | Tests Run | Pass | Fail | Blocked |
|------|--------|-------------|-----------|------|------|---------|
| | | staging | | | | |

---

## Definition of Done

- [ ] All test cases executed
- [ ] All critical/high priority tests pass
- [ ] No P0/P1 bugs open
- [ ] Regression suite passes (> 95%)
- [ ] Performance within acceptable range
- [ ] Code coverage meets threshold (if applicable)
- [ ] Accessibility checks pass
- [ ] Cross-browser verification (Chrome, Safari, Firefox)
- [ ] Mobile responsiveness verified

---

## Issues Found

| ID | Severity | Description | Status | Assigned |
|----|----------|-------------|--------|----------|
| | P0/P1/P2/P3 | | Open/Fixed/Won't Fix | |

---

## Sign-off

| Role | Name | Date | Approved |
|------|------|------|----------|
| QA | | | [ ] |
| Dev | | | [ ] |
| PO | | | [ ] |
