# Test All

Run all tests across the monorepo.

## Steps

1. Run all tests:
```bash
pnpm test
```

2. For more verbose output, run tests per app:
```bash
pnpm test:api
pnpm test:web
```

3. To run tests in watch mode during development:
```bash
cd apps/api && pnpm test:watch
```

4. To run with coverage:
```bash
cd apps/api && pnpm test:cov
```

5. Report test results and any failures

## E2E Tests

For API integration tests:
```bash
cd apps/api && pnpm test:e2e
```

Note: E2E tests require Docker services to be running:
```bash
docker compose up -d
```
