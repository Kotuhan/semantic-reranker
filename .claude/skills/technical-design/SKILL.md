---
name: technical-design
description: Templates and helpers for Team Lead technical design. Provides structured formats for architecture documentation and implementation planning.
---

# Technical Design Skill

Provides templates for technical design documentation.

## Templates

### Technical Notes Template
Located at: `.claude/skills/technical-design/templates/technical-notes-template.md`

Use this template for documenting:
- Affected modules
- New entities/modules
- Database changes
- Architectural considerations
- Risks and trade-offs
- Test plan

### Implementation Steps Template
Located at: `.claude/skills/technical-design/templates/implementation-steps-template.md`

Use this template for creating:
- Ordered, atomic steps
- File-level changes
- Verification criteria
- Dependencies between steps

## Usage

When using the TL Agent, reference these templates for consistent output format.

The templates ensure:
- Complete technical context
- Ordered, verifiable steps
- Risk assessment
- Test strategy definition

## Integration

Used by:
- Team Lead Agent
- Director Agent (for validation)
- Developer Agents (for implementation guidance)
