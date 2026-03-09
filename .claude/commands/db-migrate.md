# Database Migration

Create and run a Prisma migration for schema changes.

## Steps

1. Ensure Docker is running with Postgres:
```bash
docker compose up -d
```

2. Review the current schema changes in `apps/api/prisma/schema.prisma`

3. Create a new migration with a descriptive name:
```bash
pnpm db:migrate
```
When prompted, enter a migration name (e.g., "add_user_preferences")

4. Verify the migration was created in `apps/api/prisma/migrations/`

5. Check the generated SQL is correct

6. If needed, regenerate Prisma client:
```bash
cd apps/api && pnpm prisma generate
```

## Notes

- For quick schema iteration during development, use `pnpm db:push` instead
- Always create proper migrations before deploying to production
