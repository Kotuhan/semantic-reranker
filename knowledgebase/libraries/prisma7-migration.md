---
title: Prisma 7 Migration Guide - Configuration, Adapters, and NestJS Integration
domain: library
tech: [prisma, postgresql, typescript, nestjs, nodejs]
area: [orm, database, migration, configuration]
staleness: 3months
created: 2026-02-12
updated: 2026-02-12
sources:
  - https://www.prisma.io/docs/orm/more/upgrade-guides/upgrading-versions/upgrading-to-prisma-7
  - https://www.prisma.io/docs/orm/reference/prisma-config-reference
  - https://github.com/prisma/prisma/issues/28665
  - https://github.com/prisma/prisma/issues/28573
  - https://medium.com/@msmiraj8/get-started-with-prisma-7-with-nest-js-mysql-3919eaa7c760
  - https://www.prisma.io/blog/announcing-prisma-orm-7-0-0
---

# Prisma 7 Migration Guide - Configuration, Adapters, and NestJS Integration

## Overview

Comprehensive migration guide for upgrading from Prisma 6 to Prisma 7, covering the fundamental architectural changes: the new `prisma.config.ts` file for CLI configuration, mandatory driver adapters for runtime connections, and the shift from `node_modules` generation to custom output paths. Specifically tailored for NestJS applications using PostgreSQL (Supabase) without Prisma Accelerate.

## Key Findings

### Major Breaking Changes

Prisma 7 (released November 19, 2025) introduces several fundamental architectural changes:

1. **Database URL Configuration**: Moved from `schema.prisma` to `prisma.config.ts`
2. **Driver Adapters**: **Mandatory** for all database connections (including standard PostgreSQL)
3. **Generator Changes**: `prisma-client-js` deprecated in favor of `prisma-client` with required `output` path
4. **Rust-Free Architecture**: Faster queries, smaller bundle size, better compatibility
5. **No Auto-Generation**: Client no longer generates in `node_modules` by default
6. **Environment Variables**: No longer auto-loaded; must use `dotenv` explicitly
7. **ESM Support**: Full ESM/CommonJS compatibility via `moduleFormat` field

### Migration Complexity

| Component | Complexity | Required Actions |
|-----------|------------|------------------|
| prisma.config.ts | Medium | Create new file, move DATABASE_URL |
| Driver Adapter | High | Install `@prisma/adapter-pg`, refactor PrismaService |
| Generator Block | Medium | Change provider, add `output` field |
| Imports | Medium | Update all imports to new generated path |
| CLI Commands | Low | Commands work the same (with new flags) |
| Environment Setup | Low | Add `dotenv` import to config |

## Installation / Setup

### Prerequisites

```bash
# Minimum versions
Node.js: >= 20.19.0 (recommended: 22.x)
TypeScript: >= 5.4.0
```

### Step-by-Step Migration

#### 1. Update Dependencies

```bash
# Upgrade Prisma packages
pnpm add prisma@7.4.0 @prisma/client@7.4.0

# Install PostgreSQL adapter (NEW REQUIREMENT)
pnpm add @prisma/adapter-pg

# Ensure dotenv is installed
pnpm add dotenv
```

#### 2. Create `prisma.config.ts`

**Location**: Project root (alongside `package.json`)

**For NestJS monorepo structure** (`apps/api/`):

```typescript
// apps/api/prisma.config.ts
import 'dotenv/config'
import { defineConfig, env } from 'prisma/config'

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: {
    path: 'prisma/migrations',
    seed: 'tsx prisma/seed.ts',  // Optional
  },
  datasource: {
    url: env('DATABASE_URL'),
  },
})
```

**Key Points:**

- `import 'dotenv/config'` must be **first line** (Prisma 7 doesn't auto-load `.env`)
- `env('DATABASE_URL')` provides type-safe environment variable access
- Paths are resolved **relative to the config file location**
- `migrations.seed` is optional (only if you have a seed script)

**Type-Safe Environment Variables (Optional):**

```typescript
import { env } from "prisma/config";

type Env = {
  DATABASE_URL: string
}

export default defineConfig({
  datasource: {
    url: env<Env>('DATABASE_URL'),
  },
});
```

#### 3. Update `schema.prisma`

**REMOVE** the `url` field from `datasource` block:

```prisma
// ❌ BEFORE (Prisma 6)
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DATABASE_POOLED_URL")
}

// ✅ AFTER (Prisma 7)
datasource db {
  provider = "postgresql"
}
```

**IMPORTANT:** The `url` field is **deprecated** in schema.prisma and must be removed. It now lives in `prisma.config.ts`.

**Note on `directUrl`:** If you were using `directUrl` for migrations with Supabase pooling, move that URL to the `url` field in `prisma.config.ts` (the CLI uses `url` for migrations, not `directUrl`).

#### 4. Update Generator Block

**Option A: New Generator (Recommended)**

```prisma
// ✅ Prisma 7 - New prisma-client generator
generator client {
  provider = "prisma-client"
  output   = "./generated/prisma"
}
```

**Option B: Legacy Generator (Backward Compatible)**

```prisma
// 🟡 Still works in Prisma 7 (deprecated, will be removed in future)
generator client {
  provider = "prisma-client-js"
}
```

**Recommendation:** Use the new `prisma-client` provider for:
- Faster queries (Rust-free architecture)
- Smaller bundle size
- Better ESM/CommonJS support
- Future compatibility

**Trade-off:** Requires updating all imports from `@prisma/client` to your custom output path.

#### 5. Refactor NestJS PrismaService

**BEFORE (Prisma 6):**

```typescript
// apps/api/src/prisma/prisma.service.ts
import { Injectable, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  async onModuleInit() {
    await this.$connect();
  }
}
```

**AFTER (Prisma 7 with Adapter):**

```typescript
// apps/api/src/prisma/prisma.service.ts
import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { PrismaClient } from '../generated/prisma/client';  // ⬅ New import path
import { PrismaPg } from '@prisma/adapter-pg';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  constructor() {
    const adapter = new PrismaPg({
      connectionString: process.env.DATABASE_URL as string,
    });
    super({ adapter });
  }

  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
```

**Key Changes:**

1. **Import Path**: Change from `@prisma/client` to your generated path (`./generated/prisma/client`)
2. **Adapter Setup**: Create `PrismaPg` adapter with connection string
3. **Constructor**: Pass `{ adapter }` to `super()`
4. **Lifecycle Hooks**: Add `OnModuleDestroy` for proper cleanup

#### 6. Update All Prisma Imports

Find and replace all imports across your codebase:

```typescript
// ❌ OLD
import { PrismaClient, User, Prisma } from '@prisma/client';

// ✅ NEW
import { PrismaClient, User, Prisma } from './generated/prisma/client';
```

**For NestJS monorepo:**

```typescript
// Backend services (apps/api/src/modules/*/*)
import { User } from '../../generated/prisma/client';

// Tests (apps/api/test/)
import { PrismaClient } from '../src/generated/prisma/client';
```

**Tip:** Use global find-and-replace:

```bash
# From apps/api/ directory
grep -r "from '@prisma/client'" src/ test/ | wc -l  # Check count
# Then manually update each import based on relative path
```

#### 7. Update `package.json` Scripts (Optional)

Prisma 7 no longer auto-runs `generate` or `seed`:

```json
{
  "scripts": {
    "db:migrate": "prisma migrate dev && prisma generate",
    "db:push": "prisma db push && prisma generate",
    "db:seed": "tsx prisma/seed.ts"
  }
}
```

#### 8. Regenerate Prisma Client

```bash
cd apps/api
npx prisma generate
```

Verify the generated client exists at `apps/api/generated/prisma/`.

## Configuration

### Complete `prisma.config.ts` Reference

```typescript
import 'dotenv/config'
import type { PrismaConfig } from "prisma";
import { env } from "prisma/config";

export default {
  schema: "prisma/schema.prisma",
  migrations: {
    path: "prisma/migrations",
    seed: 'tsx prisma/seed.ts',           // Optional
    initShadowDb: 'tsx prisma/init.ts',  // Optional
  },
  views: {
    path: "prisma/views",                 // Optional
  },
  typedSql: {
    path: "prisma/sql",                   // Optional
  },
  datasource: {
    url: env("DATABASE_URL"),
    shadowDatabaseUrl: env("SHADOW_DATABASE_URL"),  // Optional
  },
  experimental: {
    externalTables: false,                // Optional
  },
} satisfies PrismaConfig;
```

### Environment Variables (.env)

```env
# Prisma 7 - Connection string for CLI (migrations)
DATABASE_URL="postgresql://user:password@project.supabase.co:5432/postgres"

# Optional: Shadow database for migration testing
SHADOW_DATABASE_URL="postgresql://user:password@localhost:5432/shadow"
```

**For Supabase with Pooling:**

```env
# Use transaction pooler for migrations (CLI uses this)
DATABASE_URL="postgresql://user:password@project.pooler.supabase.com:6543/postgres?pgbouncer=true"
```

**IMPORTANT:** In Prisma 7, the adapter gets the connection string from `process.env.DATABASE_URL` at runtime, while the CLI uses the value from `prisma.config.ts`. Ensure they match!

### Supabase-Specific Configuration

If you were using `directUrl` for migrations and `url` for application queries in Prisma 6:

**Prisma 6 Pattern:**

```prisma
datasource db {
  url       = env("DATABASE_POOLED_URL")  # App queries (transaction pooler)
  directUrl = env("DATABASE_URL")         # Migrations (direct connection)
}
```

**Prisma 7 Pattern:**

```typescript
// prisma.config.ts - Use direct connection for migrations
export default defineConfig({
  datasource: {
    url: env('DATABASE_URL'),  // Direct connection (port 5432)
  },
});
```

```typescript
// prisma.service.ts - Use pooled connection for queries
const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_POOLED_URL,  // Transaction pooler (port 6543)
});
```

## CLI Command Changes

### Commands That Work the Same

```bash
npx prisma migrate dev --name feature_name   # Create + apply migration
npx prisma migrate deploy                    # Apply migrations (production)
npx prisma db push                           # Push schema without migration
npx prisma generate                          # Generate Prisma Client
npx prisma studio                            # Open Prisma Studio
npx prisma db pull                           # Introspect existing DB
```

### Removed Flags

| Old Flag | Status | Alternative |
|----------|--------|-------------|
| `--skip-generate` | ❌ Removed | Run `prisma generate` manually |
| `--skip-seed` | ❌ Removed | Run seed script manually |
| `--schema` (in `db execute`) | ❌ Removed | Configure in `prisma.config.ts` |
| `--url` (in `db execute`) | ❌ Removed | Configure in `prisma.config.ts` |

### New Flags for `migrate diff`

```bash
# ❌ OLD (Prisma 6)
prisma migrate diff --from-url="postgresql://..." --to-url="postgresql://..."

# ✅ NEW (Prisma 7)
prisma migrate diff --from-config-datasource --to-config-datasource
```

### No Auto-Generation or Auto-Seeding

Prisma 7 no longer auto-runs `generate` or `seed` after migrations. Update your workflows:

```bash
# Prisma 6 - Auto-generated after migrate
npx prisma migrate dev --name add_user_table

# Prisma 7 - Manual generation required
npx prisma migrate dev --name add_user_table
npx prisma generate  # ⬅ Now required
```

## Usage Examples

### Example 1: Basic CRUD with New Import Path

```typescript
import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { User, Prisma } from '../generated/prisma/client';

@Injectable()
export class UserService {
  constructor(private prisma: PrismaService) {}

  async create(data: Prisma.UserCreateInput): Promise<User> {
    return this.prisma.user.create({ data });
  }

  async findAll(): Promise<User[]> {
    return this.prisma.user.findMany();
  }
}
```

### Example 2: Transaction with Adapter

```typescript
async transferCredits(fromId: string, toId: string, amount: number) {
  return this.prisma.$transaction(async (tx) => {
    await tx.user.update({
      where: { id: fromId },
      data: { credits: { decrement: amount } },
    });

    await tx.user.update({
      where: { id: toId },
      data: { credits: { increment: amount } },
    });
  });
}
```

**Note:** Transactions work the same way with adapters. The `@prisma/adapter-pg` package handles connection pooling transparently.

### Example 3: Testing with Adapter

```typescript
// test/setup.ts
import { PrismaClient } from '../src/generated/prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';

let prisma: PrismaClient;

beforeAll(async () => {
  const adapter = new PrismaPg({
    connectionString: process.env.DATABASE_URL as string,
  });
  prisma = new PrismaClient({ adapter });
  await prisma.$connect();
});

afterAll(async () => {
  await prisma.$disconnect();
});
```

## Best Practices

### 1. Adapter Connection Pooling

The `@prisma/adapter-pg` uses the underlying `pg` driver's connection pooling. Configure it explicitly:

```typescript
import { Pool } from 'pg';
import { PrismaPg } from '@prisma/adapter-pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,                    // Max connections
  idleTimeoutMillis: 30000,   // Close idle connections after 30s
  connectionTimeoutMillis: 2000,
});

const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });
```

**Default Behavior:** If you pass a connection string directly, `PrismaPg` creates a pool with Node.js `pg` driver defaults.

### 2. Environment Variable Management

Always use `dotenv` explicitly in `prisma.config.ts`:

```typescript
// ✅ CORRECT
import 'dotenv/config'  // Must be first
import { defineConfig, env } from 'prisma/config'

// ❌ WRONG - Environment variables won't be loaded
import { defineConfig, env } from 'prisma/config'
```

### 3. Generator Output Path

Choose output path based on your project structure:

```prisma
// Option 1: Inside src/ (better for monorepos)
generator client {
  provider = "prisma-client"
  output   = "./src/generated/prisma"
}

// Option 2: Root-level generated/ (simpler imports)
generator client {
  provider = "prisma-client"
  output   = "./generated/prisma"
}
```

### 4. Backward Compatibility Option

If you need to minimize breaking changes (e.g., during gradual migration), keep using `prisma-client-js`:

```prisma
// Still works in Prisma 7 (deprecated)
generator client {
  provider = "prisma-client-js"
}
```

**Trade-offs:**
- ✅ Keeps imports as `@prisma/client`
- ✅ No need to update existing code
- ❌ Slower queries (uses Rust engine)
- ❌ Larger bundle size
- ❌ Will be removed in future Prisma versions

**Recommendation:** Use this as a temporary migration step, then migrate to `prisma-client` when ready.

### 5. CI/CD Pipeline Updates

Ensure your CI/CD generates the client:

```yaml
# .github/workflows/deploy.yml
- name: Install dependencies
  run: pnpm install

- name: Generate Prisma Client
  run: npx prisma generate
  working-directory: apps/api

- name: Run migrations
  run: npx prisma migrate deploy
  working-directory: apps/api
```

### 6. Git Ignore the Generated Client

```gitignore
# apps/api/.gitignore
generated/
src/generated/
```

Always regenerate the client locally and in CI/CD.

## Common Issues

### Issue 1: "The datasource property is required"

**Error:**

```
Error: The datasource property is required in your Prisma config file when using prisma migrate dev.
```

**Cause:** Missing `prisma.config.ts` or missing `datasource.url` field.

**Solution:**

1. Create `prisma.config.ts` at project root
2. Add `datasource.url` field:

```typescript
export default defineConfig({
  datasource: {
    url: env('DATABASE_URL'),
  },
});
```

### Issue 2: "Using engine type 'client' requires either 'adapter' or 'accelerateUrl'"

**Error:**

```
Error: Using engine type "client" requires either "adapter" or "accelerateUrl" to be provided to PrismaClient constructor.
```

**Cause:** Prisma 7 requires explicit adapter for database connections.

**Solution:**

```typescript
import { PrismaPg } from '@prisma/adapter-pg';

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL as string,
});

const prisma = new PrismaClient({ adapter });
```

### Issue 3: Import Path Not Found

**Error:**

```
Cannot find module '@prisma/client' or its corresponding type declarations.
```

**Cause:** Using old import path with new `prisma-client` generator.

**Solution:** Update imports to match your `output` path:

```typescript
// If output = "./generated/prisma"
import { PrismaClient } from './generated/prisma/client';
```

### Issue 4: "url is no longer supported in datasource"

**Error:**

```
Error: url is no longer supported in datasource block
```

**Cause:** Keeping `url` field in `schema.prisma` datasource.

**Solution:** Remove `url` and `directUrl` from schema.prisma:

```prisma
datasource db {
  provider = "postgresql"
  // url = env("DATABASE_URL")  ⬅ REMOVE THIS
}
```

### Issue 5: Environment Variables Not Loaded

**Error:**

```
Error: Environment variable not found: DATABASE_URL
```

**Cause:** Missing `dotenv` import in `prisma.config.ts`.

**Solution:** Add import at the top:

```typescript
import 'dotenv/config'  // ⬅ Must be first line
```

### Issue 6: Adapter Connection Pool Exhaustion

**Symptom:** `ECONNREFUSED` or `Connection pool timeout` errors under load.

**Cause:** Prisma 7 adapters use `pg` driver's default pooling (10 connections).

**Solution:** Configure explicit pool:

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,  // Increase for high-concurrency apps
});

const adapter = new PrismaPg(pool);
```

### Issue 7: Migration Fails with Supabase Pooler

**Symptom:** Migrations fail with `pgbouncer=true` connection string.

**Cause:** PgBouncer transaction mode doesn't support all migration commands.

**Solution:** Use direct connection for CLI, pooled for runtime:

```typescript
// prisma.config.ts - Direct connection
datasource: {
  url: env('DATABASE_URL'),  // postgresql://...@project.supabase.co:5432/...
}

// prisma.service.ts - Pooled connection
const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_POOLED_URL,  // ...@pooler.supabase.com:6543/...
});
```

## Project Integration

### Recommended Directory Structure

```
apps/api/
├── prisma.config.ts           # ⬅ NEW: CLI configuration
├── prisma/
│   ├── schema.prisma          # Models only (no url)
│   ├── migrations/
│   └── seed.ts
├── generated/
│   └── prisma/                # ⬅ NEW: Generated client (gitignored)
│       └── client/
├── src/
│   ├── prisma/
│   │   ├── prisma.service.ts  # ⬅ UPDATED: With adapter
│   │   └── prisma.module.ts
│   └── modules/
│       └── user/
│           └── user.service.ts  # ⬅ UPDATED: New import path
└── test/
    └── setup.ts               # ⬅ UPDATED: Adapter for tests
```

### Migration Checklist

- [ ] Update `prisma` and `@prisma/client` to v7.4.0
- [ ] Install `@prisma/adapter-pg`
- [ ] Install `dotenv` (if not already)
- [ ] Create `prisma.config.ts` at project root
- [ ] Remove `url` field from `schema.prisma`
- [ ] Update generator to `prisma-client` with `output` path
- [ ] Refactor `PrismaService` with adapter
- [ ] Update all imports to new generated path
- [ ] Add `generated/` to `.gitignore`
- [ ] Update CI/CD to run `prisma generate`
- [ ] Test migrations with `npx prisma migrate dev`
- [ ] Verify application starts and connects to DB
- [ ] Run test suite and verify all tests pass

## Performance Considerations

### Prisma 7 Performance Improvements

| Metric | Prisma 6 | Prisma 7 | Improvement |
|--------|----------|----------|-------------|
| Cold Start | 300-800ms | 50-100ms | **6-8x faster** |
| Query Execution | Baseline | -10-20% | **Faster** |
| Bundle Size | 12MB | 8MB | **33% smaller** |
| Memory Usage | Baseline | -20-30% | **Lower** |

**Source:** Prisma ORM 7.0.0 release announcement

### Adapter Performance

The `@prisma/adapter-pg` uses the native Node.js `pg` driver, which has different performance characteristics than Prisma 6's Rust-based engine:

- **Connection Pooling:** Managed by `pg` driver (default: 10 connections)
- **Query Parsing:** Pure JavaScript (no Rust overhead)
- **Transactions:** Native PostgreSQL transactions (same performance)

**Benchmark Recommendations:**

1. Profile your application before and after migration
2. Tune connection pool size based on load (`max` parameter)
3. Monitor query performance (Prisma 7 should be equal or faster)

## Accelerate vs. Adapter Decision Matrix

| Scenario | Use Adapter | Use Accelerate |
|----------|-------------|----------------|
| Self-hosted PostgreSQL (Supabase, AWS RDS) | ✅ Yes | 🟡 Optional |
| Serverless (Lambda, Vercel) | 🟡 Maybe | ✅ Recommended |
| Need global connection pooling | ❌ No | ✅ Yes |
| Need query caching | ❌ No | ✅ Yes |
| Budget-conscious | ✅ Yes (free) | 🟡 Costs $ |
| Traditional deployment (Docker, VPS) | ✅ Yes | ❌ Unnecessary |

**For the project (NestJS + Supabase + Docker):** Use `@prisma/adapter-pg` (no Accelerate needed).

## Sources

- [Upgrade to Prisma ORM 7 - Official Guide](https://www.prisma.io/docs/orm/more/upgrade-guides/upgrading-versions/upgrading-to-prisma-7)
- [Prisma Config Reference Documentation](https://www.prisma.io/docs/orm/reference/prisma-config-reference)
- [Prisma 7 Breaking Changes Discussion (GitHub Issue #28573)](https://github.com/prisma/prisma/issues/28573)
- [Error: The datasource property is required (GitHub Issue #28585)](https://github.com/prisma/prisma/issues/28585)
- [Breaking changes with mysql adapter for prisma 7 (GitHub Issue #28665)](https://github.com/prisma/prisma/issues/28665)
- [Get Started With Prisma 7 with NestJS & MySQL - Medium](https://medium.com/@msmiraj8/get-started-with-prisma-7-with-nest-js-mysql-3919eaa7c760)
- [Prisma 7 Release: Rust-Free, Faster, and More Compatible](https://www.prisma.io/blog/announcing-prisma-orm-7-0-0)
- [Prisma ORM 7.2.0 Released: CLI Improvements, Bug Fixes & Better Configs](https://www.prisma.io/blog/announcing-prisma-orm-7-2-0)
- [Why Prisma ORM Generates Code into Node Modules & Why It'll Change](https://www.prisma.io/blog/why-prisma-orm-generates-code-into-node-modules-and-why-it-ll-change)
