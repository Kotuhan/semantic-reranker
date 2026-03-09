# Knowledge Base

Central repository for research conducted across all tasks. This file serves as an index and search guide for the Researcher agent.

## Structure

```
knowledgebase/
├── CLAUDE.md              # This index file
├── integrations/          # Third-party service integrations
├── libraries/             # Library/framework documentation
├── patterns/              # Design patterns and best practices
├── protocols/             # Communication protocols
├── troubleshooting/       # Problem-solving guides
```

## Tag Schema

Each research file uses YAML frontmatter with hierarchical tags:

```yaml
---
title: Human-readable title
domain: integration | library | protocol | pattern | troubleshooting
tech: [typescript, nestjs, nextjs, prisma, docker, ...]
area: [auth, billing, ai, websocket, ...]
staleness: 3months | 6months | 1year
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [url1, url2, ...]
---
```

## Staleness Thresholds

| Domain | Refresh After |
|--------|---------------|
| library | 3 months |
| integration | 6 months |
| pattern | 1 year |
| protocol | 1 year |
| troubleshooting | 6 months |

## Research Index

<!-- AUTO-GENERATED: Researcher agent updates this section -->

### Libraries

| Title | Tech | Area | Staleness | Updated |
|-------|------|------|-----------|---------|
| [React Chart Libraries Comparison (2026)](libraries/react-chart-libraries-2026.md) | react, typescript, javascript, data-visualization | charts, dashboard, time-series | 3months | 2026-01-29 |
| [React Animation Libraries Comparison (2026)](libraries/react-animation-libraries-2026.md) | react, typescript, javascript, animation | animations, micro-interactions, ui-transitions | 3months | 2026-01-29 |
| [MCP Server Implementation Patterns](libraries/mcp-typescript-sdk.md) | typescript, nodejs, mcp | mcp, server-development | 3months | 2026-01-29 |
| [Mermaid Diagram Syntax for Architecture](libraries/mermaid-architecture-diagrams.md) | mermaid, markdown | architecture-diagrams, visualization | 3months | 2026-01-29 |
| [Claude API Multi-Agent Pipeline Patterns](libraries/claude-api-patterns.md) | typescript, nodejs, anthropic | ai, multi-agent, structured-output | 3months | 2026-01-29 |
| [Prisma ORM Schema Design Best Practices](libraries/prisma-orm-patterns.md) | prisma, postgresql, typescript | orm, database, schema-design | 3months | 2026-01-29 |
| [Prisma 7 Migration Guide](libraries/prisma7-migration.md) | prisma, postgresql, typescript | orm, database, migration | 3months | 2026-02-12 |
| [Framer Motion Animation Patterns for Next.js](libraries/framer-motion-nextjs-patterns.md) | framer-motion, react, nextjs | animations, micro-interactions | 3months | 2026-02-12 |

### Patterns

| Title | Tech | Area | Staleness | Updated |
|-------|------|------|-----------|---------|
| [JWT Authentication Patterns](patterns/jwt-authentication-patterns.md) | jwt, typescript, nestjs, passport | auth, security, session-management | 6months | 2026-01-29 |
| [NestJS Architecture Patterns](patterns/nestjs-architecture-patterns.md) | nestjs, typescript | architecture, module-organization, guards | 3months | 2026-01-29 |
| [Glassmorphism CSS Best Practices](patterns/glassmorphism-css-2026.md) | css, html | ui-design, glassmorphism | 6months | 2026-01-29 |
| [Next.js WebSocket Integration](patterns/nextjs-websocket-realtime-2026.md) | nextjs, react, websocket | real-time, dashboard | 6months | 2026-01-29 |
| [NestJS SSE Streaming Patterns](patterns/nestjs-sse-streaming-patterns.md) | nestjs, sse, typescript | sse, real-time, streaming | 6months | 2026-01-29 |
| [NestJS WebSocket Chat Patterns](patterns/nestjs-websocket-chat-patterns.md) | nestjs, websocket, typescript | websocket, real-time, chat | 6months | 2026-01-29 |
| [MADR Format](patterns/madr-format.md) | markdown, adr | architecture, decision-records | 6months | 2026-01-29 |
| [MADR Examples from Open Source](patterns/madr-examples.md) | documentation, adr | decision-records, best-practices | 6months | 2026-01-29 |
| [Retroactive ADR Patterns](patterns/retroactive-adr-patterns.md) | madr, adr | architecture, documentation | 6months | 2026-01-29 |
| [System Design Documentation for SaaS](patterns/system-design-documentation-saas-ai-apps.md) | system-design, architecture | architecture, documentation, system-design | 6months | 2026-01-30 |

### Protocols

| Title | Tech | Area | Staleness | Updated |
|-------|------|------|-----------|---------|
| [Model Context Protocol (MCP)](protocols/model-context-protocol.md) | json-rpc, typescript | mcp, llm-integration, ai-tools | 6months | 2026-01-29 |

<!-- END AUTO-GENERATED -->

---

## Search Instructions (for Researcher Agent)

When searching for existing research:

1. **Tag-based search**: Match `domain`, `tech`, and `area` tags
2. **Keyword search**: Search file contents for specific terms
3. **Staleness check**: Compare `updated` date against staleness threshold

### Search Priority
1. Exact domain + area match
2. Tech stack match
3. Keyword in title
4. Keyword in content

## Adding New Research

1. Determine appropriate `domain` category
2. Create file: `knowledgebase/{domain}/{topic-slug}.md`
3. Add YAML frontmatter with all required tags
4. Update this index (Research Index section)
5. If task-related, create stub in `docs/tasks/{task-id}/research/`
