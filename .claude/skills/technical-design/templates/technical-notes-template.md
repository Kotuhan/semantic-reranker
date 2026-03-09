# Technical Notes Template

## Affected Modules

List all modules that will be modified or interact with this feature:

**Backend (apps/api/):**
- [ ] `src/modules/auth/` - Authentication changes
- [ ] `src/modules/users/` - User management
- [ ] `src/modules/{feature}/` - Feature modules
- [ ] Other: _________________

**Frontend (apps/web/):**
- [ ] `src/app/` - Pages/routes
- [ ] `src/components/` - UI components
- [ ] `src/hooks/` - Custom hooks
- [ ] `src/stores/` - Zustand stores
- [ ] `src/lib/` - Utilities
- [ ] Other: _________________

**Shared (packages/shared/):**
- [ ] `src/types/` - TypeScript types
- [ ] `src/constants/` - Constants
- [ ] `src/enums/` - Enums
- [ ] Other: _________________

## New Modules/Entities

List any new modules or entities to create:

| Name | Type | Location | Purpose |
|------|------|----------|---------|
| | Module | | |
| | Entity | | |
| | Service | | |
| | Component | | |

## Database Schema Changes

**Schema change required?** Yes / No

If yes:

### Migration Plan
```prisma
// Add new models/fields here
```

### Migration Verification
1. Run `pnpm db:migrate` with name: `{migration_name}`
2. Verify in Prisma Studio: `pnpm db:studio`
3. Check: _________________

### Rollback Plan
<!-- How to revert if needed -->

## Architectural Considerations

### Patterns to Use
- [ ] Repository pattern
- [ ] Service layer
- [ ] Event-driven
- [ ] Caching strategy
- [ ] Other: _________________

### Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| | | |

### Dependencies
- External services: _________________
- Internal modules: _________________
- Third-party packages: _________________

## Known Risks & Trade-offs

| Risk | Severity | Mitigation |
|------|----------|------------|
| | High/Medium/Low | |

## Test Plan

### Unit Tests (Required)
- [ ] Service methods
- [ ] Utility functions
- [ ] Validation logic

### Integration Tests (If applicable)
- [ ] API endpoints
- [ ] Database operations
- [ ] External service calls

### E2E Tests (If critical path)
- [ ] User flow: _________________

### Test Data Requirements
<!-- Factories, fixtures, mocks needed -->
