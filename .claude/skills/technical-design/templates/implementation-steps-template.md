# Implementation Steps Template

## Guidelines

Each step should be:
- **Atomic**: Completable independently
- **Ordered**: Dependencies are respected
- **Verifiable**: Has clear done criteria
- **Reasonable**: Can be done in a focused session

## Step Format

```markdown
### Step {N}: {Title}

**Description:**
{What needs to be done}

**Files to Create:**
- `path/to/new-file.ts`

**Files to Modify:**
- `path/to/existing-file.ts`

**Changes:**
{Specific changes to make}

**Verification:**
- [ ] {How to verify this step is complete}
- [ ] {Additional verification if needed}

**Dependencies:**
- Requires Step {X} to be complete
- Requires {external dependency}
```

---

## Implementation Steps

### Step 1: Database/Schema Changes (if applicable)

**Description:**
Set up database models and run migrations.

**Files to Create:**
- None (schema in existing file)

**Files to Modify:**
- `apps/api/prisma/schema.prisma`

**Changes:**
```prisma
// Add model here
```

**Verification:**
- [ ] `pnpm db:migrate` runs successfully
- [ ] Model visible in `pnpm db:studio`
- [ ] No errors in Prisma Client generation

---

### Step 2: Backend Service Layer

**Description:**
Implement business logic in service.

**Files to Create:**
- `apps/api/src/modules/{name}/{name}.service.ts`

**Files to Modify:**
- `apps/api/src/modules/{name}/{name}.module.ts`

**Changes:**
- Implement service methods
- Add to module providers

**Verification:**
- [ ] Service compiles without errors
- [ ] Unit tests pass: `pnpm test {name}.service`

---

### Step 3: Backend DTOs & Validation

**Description:**
Create request/response DTOs with validation.

**Files to Create:**
- `apps/api/src/modules/{name}/dto/create-{name}.dto.ts`
- `apps/api/src/modules/{name}/dto/update-{name}.dto.ts`

**Changes:**
- Add class-validator decorators
- Export from dto/index.ts

**Verification:**
- [ ] DTOs compile without errors
- [ ] Validation decorators are correct

---

### Step 4: Backend Controller & Routes

**Description:**
Expose API endpoints.

**Files to Create:**
- `apps/api/src/modules/{name}/{name}.controller.ts`

**Files to Modify:**
- `apps/api/src/modules/{name}/{name}.module.ts`

**Changes:**
- Implement controller methods
- Add guards if needed
- Add to module controllers

**Verification:**
- [ ] Endpoints respond correctly (test with curl/Postman)
- [ ] Auth guards work as expected
- [ ] DTOs validate input

---

### Step 5: Test Factory (if new entity)

**Description:**
Add test factory for new entity.

**Files to Create:**
- `apps/api/src/test-utils/factories/{name}.factory.ts`

**Files to Modify:**
- `apps/api/src/test-utils/factories/index.ts`

**Changes:**
- Implement factory with sensible defaults
- Export from index

**Verification:**
- [ ] Factory creates valid entities
- [ ] Used in at least one test

---

### Step 6: Backend Integration Tests

**Description:**
Write e2e tests for API endpoints.

**Files to Create:**
- `apps/api/test/{name}.e2e-spec.ts`

**Changes:**
- Test happy path
- Test error cases
- Test auth requirements

**Verification:**
- [ ] All tests pass: `pnpm test:e2e`
- [ ] Tests use cleanupDb() properly

---

### Step 7: Frontend Types & API Client

**Description:**
Add types and API methods.

**Files to Create:**
- `apps/web/src/types/{name}.ts`

**Files to Modify:**
- `apps/web/src/lib/api-client.ts`

**Changes:**
- Define TypeScript interfaces
- Add API methods

**Verification:**
- [ ] Types compile without errors
- [ ] API methods match backend contract

---

### Step 8: Frontend Components

**Description:**
Build UI components.

**Files to Create:**
- `apps/web/src/components/{name}/{name}.tsx`

**Changes:**
- Implement component with proper types
- Use Tailwind CSS for styling
- Handle loading/error states

**Verification:**
- [ ] Component renders without errors
- [ ] Responsive on mobile
- [ ] Accessible (keyboard nav, screen reader)

---

### Step 9: Frontend Integration

**Description:**
Connect components to pages and state.

**Files to Modify:**
- `apps/web/src/app/(app)/{page}/page.tsx`

**Changes:**
- Import and use new components
- Connect to Zustand store if needed
- Add React Query hooks

**Verification:**
- [ ] Feature works end-to-end
- [ ] State updates correctly
- [ ] No console errors

---

### Step 10: Final Verification

**Description:**
Run all checks and verify the feature.

**Verification:**
- [ ] `pnpm lint` passes
- [ ] `pnpm test` passes
- [ ] `pnpm build` succeeds
- [ ] Feature works in dev environment
- [ ] Acceptance criteria met (check with PO insights)
- [ ] Record test results in task file

---

## Notes

<!-- Any additional implementation notes -->
