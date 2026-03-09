# Build Check

Build all apps and packages and verify success.

## Steps

1. Run the full build:
```bash
pnpm build
```

2. Check for any build errors in the output

3. Verify build artifacts exist:
- `apps/web/.next/` directory exists
- `apps/api/dist/` directory exists
- `packages/shared/dist/` directory exists
- `packages/ui/dist/` directory exists

4. Report any errors found
