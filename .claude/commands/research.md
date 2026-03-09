# Research

Conduct or find research on a technical topic: $ARGUMENTS

## Arguments Format

```
/research <topic> [--task <task-id>] [--refresh]
```

**Examples:**
- `/research Claude API structured output patterns`
- `/research Stripe subscription webhooks in NestJS --task task-005`
- `/research Prisma migration best practices --refresh`

## Steps

1. **Parse Arguments**
   - Extract the research topic
   - Check for `--task` flag to link research to a specific task
   - Check for `--refresh` flag to force refresh even if research exists

2. **Invoke Researcher Agent**
   - Use the Task tool with `subagent_type: "researcher"`
   - Pass the full research request with context
   - Include task ID if provided

3. **Process Results**
   - The Researcher Agent will:
     - Search existing research in `knowledgebase/`
     - Check staleness of any matching research
     - Conduct new research if needed (Context7 + WebSearch)
     - Save to knowledgebase with proper tags
     - Create task stub if task ID was provided

4. **Report Results**
   - Show research file location
   - Provide key findings summary
   - If task-linked, show stub file path

## Integration

This command can be invoked:
- **Directly by user**: `/research <topic>`
- **By other agents**: TL, PO, Dev agents can request research
- **By Director**: When research is needed before planning

## Knowledge Base Structure

Research is organized in `knowledgebase/`:
- `integrations/` - Third-party service integrations
- `libraries/` - Library/framework documentation
- `patterns/` - Design patterns and best practices
- `protocols/` - Communication protocols
- `troubleshooting/` - Problem-solving guides

## Output

The research will be saved to:
- **Main file**: `knowledgebase/{domain}/{topic-slug}.md`
- **Task stub** (if task provided): `docs/tasks/{task-id}/research/{topic-slug}.md`
