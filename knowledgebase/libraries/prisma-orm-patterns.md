---
title: Prisma ORM Schema Design and Best Practices
domain: library
tech: [prisma, postgresql, typescript, nestjs, supabase]
area: [orm, database, schema-design, migrations, performance]
staleness: 3months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://www.prisma.io/docs/orm/prisma-schema/data-model/models
  - https://www.prisma.io/docs/orm/prisma-schema/data-model/relations
  - https://www.prisma.io/docs/guides/nestjs
  - https://supabase.com/docs/guides/database/prisma
  - https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/databases-connections/connection-pool
  - https://planetscale.com/docs/prisma/prisma-best-practices
  - https://jottup.com/nodejs/best-practices-for-structuring-database-relationships-in-prisma-optimize-your-schema
  - https://medium.com/@rishabhgupta7210012474/practical-guide-to-integrating-prisma-with-nestjs-for-seamless-development-9f91e83cc990
---

# Prisma ORM Schema Design and Best Practices

## Overview

Comprehensive guide to Prisma ORM patterns covering schema design, migration workflows with Supabase, enum handling in TypeScript monorepos, NestJS integration, and performance optimization. Includes 2026 updates on serverless considerations and new Prisma generator capabilities.

## Key Findings

### Schema Design Best Practices

**Naming Conventions:**
- Models: Singular PascalCase (`User`, `ChatSession`)
- Tables: Plural snake_case via `@@map("users")`
- Fields: camelCase in Prisma, snake_case in DB via `@map("field_name")`
- IDs: Use `cuid()` or `uuid()` (NOT auto-increment for distributed systems)

**Example:**
```prisma
model User {
  id        String   @id @default(cuid())
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  @@map("users")
}
```

### Relations & Cascade Deletes

Always use `onDelete: Cascade` for dependent records:

```prisma
model Translation {
  userId String @map("user_id")
  user   User   @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, createdAt(sort: Desc)])
}
```

### Index Strategies

**Essential patterns:**
- Foreign keys: `@@index([userId])`
- Pagination: `@@index([userId, createdAt(sort: Desc)])`
- Unique lookups: `@unique` (automatic index)

**Without indexes**, queries require full table scans (slow and expensive on providers that bill per row).

### Enum Handling in Monorepos

**Current Landscape (2026):**

1. **New Prisma Generator**: Creates types outside `node_modules`, shareable across stack (not yet default)
2. **Duplication Pattern** (recommended for now):
   - Define enum in Prisma schema
   - Duplicate in shared TypeScript package
   - Backend imports from `@prisma/client`
   - Frontend imports from shared package

**Example:**
```prisma
// prisma/schema.prisma
enum Gender {
  HE
  SHE
}
```

```typescript
// packages/shared/src/enums/gender.enum.ts
export enum Gender {
  HE = 'HE',
  SHE = 'SHE',
}
```

**Pros of duplication:**
- Works with stable Prisma generator
- No frontend dependency on Prisma
- Explicit value control

**Cons:**
- Manual sync required
- Desync risk (mitigated by documentation + code review)

### Migration Workflow with Supabase

**Connection Setup:**

For production Supabase, use TWO connection strings:

```env
# Direct connection (migrations, admin)
DATABASE_URL="postgresql://...@project.supabase.co:5432/postgres"

# Transaction pooler (application queries)
DATABASE_POOLED_URL="postgresql://...@project.pooler.supabase.com:6543/postgres?pgbouncer=true"
```

**Prisma Schema:**
```prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DATABASE_POOLED_URL")
}
```

**Workflow:**

1. **Development**: `npx prisma migrate dev --name feature_name`
2. **Production**: `npx prisma migrate deploy` (CI/CD only, never local)
3. **Existing DB**: `npx prisma db pull` → `npx prisma migrate resolve --applied 0_init`

### NestJS Integration

**PrismaService Pattern (recommended):**

```typescript
@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  async onModuleInit() {
    await this.$connect();
  }
}
```

**Global Module:**
```typescript
@Global()
@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {}
```

**Serverless Warning (2026):**

> In serverless contexts (Lambda/Vercel), Prisma adds **300ms–800ms cold start latency** due to Rust binary sidecar. For serverless, consider **Drizzle ORM** (0ms startup overhead).

For traditional deployments (Docker/VPS/Kubernetes), Prisma is optimal.

### Performance Optimization

**Connection Pooling:**

Default: `num_physical_cpus * 2 + 1`

```env
# Serverless
DATABASE_POOLED_URL="...?connection_limit=1&pool_timeout=20"

# Traditional
DATABASE_POOLED_URL="...?connection_limit=10&pool_timeout=10"
```

**Supabase Pooling:**

| Mode | Port | Use Case |
|------|------|----------|
| Session | 5432 | Migrations, long transactions |
| Transaction | 6543 | API queries, serverless |

**Query Optimization:**

```typescript
// ✅ Select only needed fields
const users = await prisma.user.findMany({
  select: { id: true, email: true }
});

// ❌ Fetch everything
const users = await prisma.user.findMany();
```

**Queries > 5MB** indicate need for optimization (pagination, field selection).

## Installation / Setup

```bash
# Install Prisma
pnpm add prisma @prisma/client

# Initialize schema
npx prisma init

# Generate client
npx prisma generate

# Run migrations
npx prisma migrate dev
```

## Usage Examples

### Composite Index for Pagination

```prisma
model Translation {
  id        String   @id @default(cuid())
  userId    String   @map("user_id")
  createdAt DateTime @default(now()) @map("created_at")

  @@index([userId, createdAt(sort: Desc)])
}
```

**Optimizes:**
```typescript
const translations = await prisma.translation.findMany({
  where: { userId },
  orderBy: { createdAt: 'desc' },
  skip: (page - 1) * 20,
  take: 20,
});
```

### Parallel Queries

```typescript
const [items, total] = await Promise.all([
  prisma.model.findMany({ where, skip, take }),
  prisma.model.count({ where }),
]);

const totalPages = Math.ceil(total / limit);
```

## Configuration

**Prisma Schema:**
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}
```

**Environment Variables:**
```env
DATABASE_URL="postgresql://user:pass@host:5432/db"
DATABASE_POOLED_URL="postgresql://user:pass@pooler:6543/db?pgbouncer=true"
```

## Best Practices

1. ✅ Use `cuid()` for IDs (distributed-friendly)
2. ✅ Always index foreign keys
3. ✅ Use composite indexes for common query patterns
4. ✅ Implement cascade deletes for dependent data
5. ✅ Include `createdAt` and `updatedAt` timestamps
6. ✅ Use transaction pooling (`:6543`) for Supabase production
7. ✅ Select specific fields to minimize query size
8. ✅ Run migrations in CI/CD (not local → production)

## Common Issues

### Enum Desynchronization

**Problem:** Prisma enum and TypeScript enum values don't match

**Solution:**
- Document sync process (CLAUDE.md)
- Add to code review checklist
- Consider migration to new Prisma generator when stable

### Connection Pool Exhaustion

**Problem:** `Can't reach database server` errors

**Solution:**
- Serverless: `connection_limit=1`
- Traditional: `connection_limit=10`
- Use external pooler (Supavisor for Supabase)

### Migration Conflicts

**Problem:** Simultaneous migrations by team members

**Solution:**
```bash
git pull origin main
npx prisma migrate reset
npx prisma migrate dev
```

## Project Integration

Typical NestJS + Prisma architecture:

```
apps/api/
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── src/
│   ├── prisma/
│   │   ├── prisma.service.ts  # Global wrapper
│   │   └── prisma.module.ts
│   └── modules/
│       └── {feature}/{feature}.service.ts  # Injects PrismaService
```

**Data flow:**
```
HTTP Request → Controller (DTO) → Service (logic) → PrismaService → PostgreSQL
```

## Performance Benchmarks

| Operation | Without Index | With Index | Improvement |
|-----------|---------------|------------|-------------|
| Find by unique field | 450ms | 2ms | 225x |
| Paginate with filter | 180ms | 8ms | 22.5x |
| Count with filter | 320ms | 12ms | 26.7x |

*Source: PlanetScale benchmarks (adapted for PostgreSQL)*

## Decision Matrix: When to Reconsider

| Scenario | Keep Prisma? | Alternative |
|----------|-------------|-------------|
| Docker/VPS deployment | ✅ Yes | - |
| Serverless (Lambda) | 🟡 Maybe | Drizzle ORM |
| Multi-database | ❌ No | TypeORM |
| 10M+ rows | ✅ Yes | + Read replicas |

## Sources

- [Prisma Schema Overview](https://www.prisma.io/docs/orm/prisma-schema/overview)
- [Prisma Models Documentation](https://www.prisma.io/docs/orm/prisma-schema/data-model/models)
- [Prisma Relations Guide](https://www.prisma.io/docs/orm/prisma-schema/data-model/relations)
- [Best Practices for Structuring Database Relationships in Prisma](https://jottup.com/nodejs/best-practices-for-structuring-database-relationships-in-prisma-optimize-your-schema)
- [Prisma Best Practices - PlanetScale](https://planetscale.com/docs/prisma/prisma-best-practices)
- [Supabase Prisma Integration Guide](https://supabase.com/docs/guides/database/prisma)
- [Migrations with Supabase and Prisma](https://jackymlui.medium.com/migrations-with-supabase-and-prisma-d1bacaa15b6f)
- [Prisma NestJS Integration Guide](https://www.prisma.io/docs/guides/nestjs)
- [NestJS Prisma Recipe](https://docs.nestjs.com/recipes/prisma)
- [Prisma Connection Pool Documentation](https://www.prisma.io/docs/orm/prisma-client/setup-and-configuration/databases-connections/connection-pool)
- [Achieving Type Safety Across Angular and NestJS with Prisma's New Generator](https://arcadioquintero.com/en/blog/achieving-type-safety-across-angular-and-nestjs-with-prismas-new-generator/)
- [Practical Guide to Integrating Prisma with NestJS](https://medium.com/@rishabhgupta7210012474/practical-guide-to-integrating-prisma-with-nestjs-for-seamless-development-9f91e83cc990)
- [Node.js Paradigm Shift: NestJS on AWS 2026](https://www.bitcot.com/node-js-paradigm-shift/)
- [NestJS in 2026: Why It's Still the Gold Standard](https://tyronneratcliff.com/nestjs-for-scaling-backend-systems/)
