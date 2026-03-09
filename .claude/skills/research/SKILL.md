---
name: research
description: Research technical topics using Context7 and web sources. Manages the knowledge base and provides research to other agents.
---

# Research Skill

Provides research capabilities for technical documentation, library guides, and implementation patterns.

## CRITICAL: How to Execute This Skill

**When this skill is invoked, you MUST spawn the researcher agent via Task tool.**

```yaml
# MANDATORY: Spawn researcher agent
Task(
  subagent_type: "researcher",
  prompt: "Research <topic>.
    1. Check knowledgebase/CLAUDE.md index first
    2. If exists and not stale, return existing research
    3. If new/stale, use WebSearch/WebFetch to gather info
    4. Create/update file in knowledgebase/{domain}/{slug}.md
    5. Update knowledgebase/CLAUDE.md index
    6. Return summary of findings"
)
```

**DO NOT:**
- Use WebSearch/WebFetch directly yourself
- Create knowledge base files without spawning researcher agent
- Skip the index update step

## Usage

### Direct Invocation
```
/research <topic> [--task <task-id>] [--refresh]
```

### Examples
```bash
# Basic research
/research Claude API structured output patterns

# Research linked to a task
/research Stripe subscription webhooks in NestJS --task task-005

# Force refresh existing research
/research Prisma migration best practices --refresh
```

## Knowledge Base

Research is stored in `knowledgebase/` with categories:

| Category | Content |
|----------|---------|
| `integrations/` | Third-party service integrations |
| `libraries/` | Library/framework documentation |
| `patterns/` | Design patterns and best practices |
| `protocols/` | Communication protocols |
| `troubleshooting/` | Problem-solving guides |

## Templates

### Stub Template
Located at: `.claude/skills/research/templates/stub-template.md`

Used when linking research to a specific task. Creates a lightweight stub in the task's `research/` folder that points to the main knowledge base entry.

## Research File Format

All research files use YAML frontmatter for tagging:

```yaml
---
title: Human-readable title
domain: integration | library | protocol | pattern | troubleshooting
tech: [typescript, nestjs, nextjs, prisma, docker]
area: [auth, billing, ai, websocket]
staleness: 3months | 6months | 1year
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - https://example.com/docs
---
```

## Staleness Rules

| Domain | Refresh After |
|--------|---------------|
| library | 3 months |
| integration | 6 months |
| pattern | 1 year |
| protocol | 1 year |
| troubleshooting | 6 months |

## Integration

Used by:
- **Researcher Agent** - Primary consumer
- **TL Agent** - Requests research before technical design
- **Developer Agents** - Requests implementation details
- **Director Agent** - Orchestrates research requests

## Tools Used

The Researcher Agent uses:
1. **Context7 MCP** - For up-to-date library documentation
2. **WebSearch** - For tutorials and best practices
3. **WebFetch** - For fetching specific documentation pages
