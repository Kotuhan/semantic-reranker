---
title: Real-World MADR Examples from Open Source Projects
domain: pattern
tech: [documentation, architecture]
area: [adr, madr, decision-records]
staleness: 6months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://github.com/adr/madr
  - https://github.com/omeerkorkmazz/adr-examples
  - https://github.com/apache/james-project/blob/master/src/adr/
  - https://github.com/primer/react/blob/main/contributor-docs/adrs/
  - https://github.com/adr/adr-manager/blob/main/docs/adr/
  - https://elastisys.io/welkin/adr/
---

# Real-World MADR Examples from Open Source Projects

## Overview

This research examines real Architecture Decision Records (ADRs) from notable open source projects to understand practical patterns for:
1. Context section depth and detail
2. Considered Options structure and quantity
3. Consequences formatting (positive, negative, neutral)
4. Numbering and naming conventions
5. Superseding/amending patterns

## Key Findings

### 1. Real ADR Examples from Notable Projects

#### Example 1: MADR Project Itself (Meta-ADR)

**Project:** [adr/madr](https://github.com/adr/madr)
**File:** `docs/decisions/0000-use-markdown-architectural-decision-records.md`

**Structure:**

```markdown
## Context and Problem Statement
Which format and structure should these records follow?

## Considered Options
- MADR 4.0.0 – The Markdown Architectural Decision Records standard
- Michael Nygard's template – The original ADR concept
- Sustainable Architectural Decisions – Y-Statements approach
- Other templates – Various options from community repositories
- Formless approach – No standardized conventions

## Decision Outcome
Chosen: MADR 4.0.0

Rationale:
1. Explicit documentation – Making implicit assumptions explicit
2. Structured flexibility – MADR accommodates any decision type
3. Lean methodology – Aligns with development practices
4. Comprehensible structure – Facilitates usage and maintenance
5. Active community – Maintained actively
```

**Key Observations:**
- **Context:** Very concise (single question)
- **Options:** 5 options listed (brief descriptions)
- **Decision:** Clear choice with 5 rationale points
- **Consequences:** Not explicitly separated (integrated into rationale)

#### Example 2: Apache James Project

**Project:** [apache/james-project](https://github.com/apache/james-project)
**File:** `src/adr/0001-record-architecture-decisions.md`

**Structure:**

```markdown
Date: October 2, 2019
Status: Proposed

## Context
The Apache James project sought to establish a more community-oriented
approach to architectural decisions. The team recognized the need for
a structured process to document and discuss significant design choices
openly.

## Decision
The project adopted Architecture Decision Records (ADRs), as described
by Michael Nygard. Key aspects include:
- Each ADR undergoes discussion on the Apache James developers mailing
  list before acceptance
- Status categories follow Apache Decision Making processes:
  - Proposed: Under discussion on mailing list
  - Accepted (lazy consensus): Community agreement emerged
  - Accepted (voted): Formal voting completed
  - Rejected: Consensus built against the proposal

## Consequences
- ADRs include a References section linking related JIRA tickets and
  mailing list discussions
- JIRA tickets implementing architectural decisions must reference
  the corresponding ADR
- The project uses lightweight ADR tooling for documentation management

## References
- JAMES-2909 (JIRA ticket)
- PR #166 discussing this ADR
```

**Key Observations:**
- **Context:** 2-3 sentences describing the situation
- **Options:** Not explicitly listed (single option presented)
- **Decision:** Detailed with bullet points and sub-categories
- **Consequences:** 3 specific items (process-oriented)
- **Extra:** References section for traceability

#### Example 3: GitHub Primer React - TypeScript Adoption

**Project:** [primer/react](https://github.com/primer/react)
**File:** `contributor-docs/adrs/adr-001-typescript.md`

**Structure:**

```markdown
## Status
| Stage | Status |
|-------|--------|
| Approved | ✅ |
| Adopted | ✅ |

## Context
Primer React initially lacked TypeScript type definitions. In July 2019,
developers created an ambient declaration file (index.d.ts) to provide
typing for TypeScript applications without rewriting components.

While effective initially, this approach proved problematic. The
disconnection between type definitions and implementation code led to
maintenance challenges. The project documented "many TypeScript bug
reports" regarding inaccurate and outdated type information as the
library grew in complexity and scale.

## Decision
The team committed to rewriting Primer React components using TypeScript
natively.

## Consequences
Benefits:
- TypeScript compiler automatically generates accurate type definitions
- Contributors can upstream TypeScript components from other projects
- Refactoring gains increased confidence through type safety
- Prop documentation can be generated automatically via
  react-docgen-typescript
- Reduces maintenance burden for keeping types synchronized with code

Tradeoff:
- New contributors require baseline TypeScript familiarity to contribute
```

**Key Observations:**
- **Context:** Detailed (2 paragraphs explaining history and problem)
- **Options:** Not explicitly listed (single decision path)
- **Decision:** Very concise (single sentence)
- **Consequences:** Structured into Benefits (5 items) and Tradeoffs (1 item)
- **Extra:** Table-based status tracking with emojis

#### Example 4: ADR Manager - Vue.js Selection

**Project:** [adr/adr-manager](https://github.com/adr/adr-manager)
**File:** `docs/adr/0001-use-vue.js.md`

**Structure:**

```markdown
## Status
Accepted

## Context and Problem Statement
A framework makes the creation of a web app significantly easier.
Which framework should be used?

## Considered Options
- Vue.js
- Angular

## Decision Outcome
The team selected Vue.js as their framework of choice.

Rationale: the team has more experience with Vue.js
```

**Key Observations:**
- **Context:** Minimal (2 sentences)
- **Options:** 2 options listed (no details)
- **Decision:** Single sentence with brief rationale
- **Consequences:** Not included
- **Note:** Very minimal ADR (9 lines total)

#### Example 5: API Gateway Selection (Real Scenario)

**Project:** [omeerkorkmazz/adr-examples](https://github.com/omeerkorkmazz/adr-examples)
**File:** `examples/adr-api-gateway.md`

**Structure:**

```markdown
## Summary
Issue: Transitioning from monolithic to microservices. Required
open-source API Gateway supporting authentication/authorization.

## Decision
Selected KrakenD based on:
- Active open-source community support
- Development team familiarity with Go programming language
- Stateless architectural design
- Superior performance characteristics

Status: Accepted (January 2, 2022) with openness to future alternatives

## Constraints
- Open-source development with minimal licensing costs
- High throughput and low latency requirements
- Performance optimization needs
- Alignment with existing developer skill sets

## Positions Considered
1. KrakenD - Selected
2. Ocelot - Rejected
3. Kong - Rejected
4. Tyk - Rejected

## Comparative Arguments
KrakenD advantages: "open-source, large community, stateless
architecture, faster than Kong and Ocelot, written by GoLang"

Kong drawbacks: Too complex, Lua-based, enterprise pricing model,
management overhead

Ocelot limitations: C# dependency, ecosystem lock-in despite
.NET advantages

Tyk concerns: Enterprise focus, AWS marketplace limitations

## Consequences
- Leveraged ready-to-use Go-language plugins
- Accelerated team onboarding and capability
- Need to manage edge case error scenarios
```

**Key Observations:**
- **Context:** Presented as "Issue" with constraints
- **Options:** 4 options with detailed comparative analysis
- **Decision:** Clear with 4 supporting reasons
- **Consequences:** 3 specific outcomes (2 positive, 1 negative)

#### Example 6: MADR Meta-Decision on Status Field

**Project:** [adr/madr](https://github.com/adr/madr)
**File:** `docs/decisions/0008-add-status-field.md`

**Structure:**

```markdown
## Context and Problem Statement
Technical Story: Issue #2
Should ADRs track status and, if so, how to implement this tracking?

## Considered Options
- Use YAML front matter
- Use badge
- Use text line
- Use separate heading
- Use table
- Do not add status

## Decision Outcome
"Use YAML front matter" was selected as the preferred approach.

## Pros and Cons Analysis

YAML Front Matter
- ✓ Supported by most Markdown parsers

Badge Approach
- ✓ Plain markdown; visually appealing
- ✗ Difficult to read in source; relies on external services
- ✗ Requires badge generation for each ADR variant

Text Line
- ✓ Plain markdown; readable; easy to write
- ✗ Requires maintenance; consumes document space

Separate Heading
- ✓ Plain markdown; straightforward
- ✗ Consumes significant space (minimum three lines)

Table Format
- ✓ Enables history tracking; multiple entries
- ✗ Not in CommonMark specification; difficult to read

Do Not Add Status
- ✓ Keeps MADR lean
- ✗ Users request this field; misaligns with other ADR templates

## Additional Information
ADR-0013 provides further rationale for adopting YAML front matter
```

**Key Observations:**
- **Context:** Links to technical story/issue
- **Options:** 6 options with detailed pros/cons for each
- **Decision:** Brief statement
- **Consequences:** Integrated into pros/cons analysis
- **Cross-reference:** Links to related ADR-0013

### 2. Context Section Patterns

#### Detail Levels Observed

**Minimal (1-2 sentences):**
```markdown
## Context and Problem Statement
A framework makes the creation of a web app significantly easier.
Which framework should be used?
```
Used for straightforward, self-explanatory decisions.

**Standard (2-3 sentences):**
```markdown
## Context
The Apache James project sought to establish a more community-oriented
approach to architectural decisions. The team recognized the need for
a structured process to document and discuss significant design choices
openly.
```
Most common pattern. Provides essential background without excessive detail.

**Detailed (Multiple paragraphs):**
```markdown
## Context
Primer React initially lacked TypeScript type definitions. In July 2019,
developers created an ambient declaration file (index.d.ts)...

While effective initially, this approach proved problematic...
```
Used when historical context or problem evolution is important.

#### Context Structure Variations

1. **As a Question** (MADR recommended):
   ```markdown
   Which format and structure should these records follow?
   ```

2. **As Problem Statement**:
   ```markdown
   The project needed to determine how to record architectural decisions...
   ```

3. **With Constraints Section**:
   ```markdown
   ## Context
   [Problem description]

   ## Constraints
   - Open-source development with minimal licensing costs
   - High throughput and low latency requirements
   ```

### 3. Considered Options Structure

#### Number of Options

**Analysis from examples:**

| Project | Options Listed | Notes |
|---------|---------------|-------|
| MADR 0000 | 5 options | Mix of specific templates and "formless" |
| MADR 0008 | 6 options | Including "do nothing" option |
| API Gateway | 4 options | All specific products |
| Vue.js | 2 options | Minimal comparison |
| TypeScript | Not listed | Single path presented |
| Apache James | Not listed | Single approach |

**Patterns:**
- **2-4 options:** Most common for product/framework selection
- **5-6 options:** Comprehensive analysis including "do nothing"
- **Single option:** When decision path is obvious or retrofitting existing choice

#### Option Detail Levels

**Minimal (names only):**
```markdown
## Considered Options
- Vue.js
- Angular
```

**Standard (brief description):**
```markdown
## Considered Options
- MADR 4.0.0 – The Markdown Architectural Decision Records standard
- Michael Nygard's template – The original ADR concept
- Formless approach – No standardized conventions
```

**Detailed (separate pros/cons):**
```markdown
## Considered Options
- Use YAML front matter
- Use badge
- Use text line
[... etc ...]

## Pros and Cons Analysis

### YAML Front Matter
- ✓ Supported by most Markdown parsers

### Badge Approach
- ✓ Plain markdown; visually appealing
- ✗ Difficult to read in source
```

### 4. Consequences Structure

#### Format Variations

**Simple List:**
```markdown
## Consequences
- ADRs include a References section
- JIRA tickets must reference corresponding ADR
- Uses lightweight ADR tooling
```

**Benefits/Tradeoffs:**
```markdown
## Consequences
Benefits:
- TypeScript compiler automatically generates type definitions
- Increased confidence through type safety

Tradeoffs:
- New contributors require TypeScript familiarity
```

**Good/Bad/Neutral (MADR style):**
```markdown
## Consequences
- Good, because TypeScript compiler generates accurate definitions
- Good, because refactoring gains type safety
- Bad, because new contributors need TypeScript knowledge
- Neutral, because existing contributors already know TypeScript
```

**Integrated into Decision:**
```markdown
## Decision Outcome
Chosen: MADR 4.0.0

Because:
1. Explicit documentation [positive]
2. Structured flexibility [positive]
3. Comprehensible structure [positive]
```

#### Consequence Types Observed

**Process Consequences:**
- "ADRs undergo discussion on mailing list before acceptance"
- "JIRA tickets must reference corresponding ADR"

**Technical Consequences:**
- "TypeScript compiler automatically generates type definitions"
- "Leveraged ready-to-use Go-language plugins"

**Team/Human Consequences:**
- "New contributors require TypeScript familiarity"
- "Accelerated team onboarding"

**Maintenance Consequences:**
- "Reduces maintenance burden"
- "Need to manage edge case error scenarios"

### 5. ADR Numbering and Naming Conventions

#### Numbering Patterns

**Four-digit (0001) - Most Common:**
```
0000-use-markdown-architectural-decision-records.md
0001-use-CC0-or-MIT-as-license.md
0008-add-status-field.md
0015-jest-27-implementation.md
```

Projects using this:
- MADR project itself
- Apache James (src/adr/0001-*.md)
- GitHub Primer React (contributor-docs/adrs/adr-001-*.md)
- Welkin/Elastisys (0000-0061 documented)

**Three-digit (001):**
```
adr-001-use-adrs.md
001-index.md
```

Projects using this:
- Arachne Framework
- Some phodal/adr tool examples

#### Naming Patterns

**Pattern:** `[number]-[slug].md`

**Slug characteristics:**
- Lowercase
- Hyphens for spaces
- Verb-noun structure common: "use-X", "add-Y", "adopt-Z"
- Descriptive but concise (3-7 words typical)

**Examples:**
```
0000-use-markdown-architectural-decision-records.md
0001-record-architecture-decisions.md
0008-add-status-field.md
0013-use-yaml-front-matter-for-meta-data.md
0015-jest-27-implementation.md
adr-001-typescript.md
```

#### Directory Structures

**Common patterns:**

```
docs/adr/                    # Most common
docs/decisions/              # MADR 3.0+ recommendation
src/adr/                     # Apache James
contributor-docs/adrs/       # GitHub Primer
```

### 6. Superseding/Amending ADRs

#### Status Field Values

From MADR template and real examples:

```yaml
status: {proposed | rejected | accepted | deprecated | superseded by [ADR-0005](0005-example.md)}
```

**Status meanings:**
- **proposed:** Under discussion
- **rejected:** Decided against
- **accepted:** Approved and active
- **deprecated:** No longer recommended but not replaced
- **superseded by:** Replaced by newer decision

#### Real Superseding Examples

**Apache James pattern:**
```markdown
Status: Accepted (lazy consensus)
Status: Accepted (voted)
Status: Rejected
```

**MADR recommended format:**
```yaml
---
status: superseded by [ADR-0013](0013-use-yaml-front-matter-for-meta-data.md)
---
```

#### Cross-Referencing Patterns

**Forward reference (in superseded ADR):**
```markdown
Status: superseded by ADR-0013
```

**Backward reference (in new ADR):**
```markdown
## Additional Information
ADR-0008 provides context for this decision.
```

**Explicit superseding note:**
```markdown
## Status
This ADR supersedes ADR-0008 "Add Status Field" by providing
additional rationale for using YAML front matter.
```

#### Amendment Patterns

**Not common in examples found.** Most projects prefer:
1. Create new ADR that supersedes old one
2. Mark old ADR as "superseded by ADR-XXXX"
3. New ADR can reference old one in context

**Rationale:** Preserves historical decision context.

### 7. Project-Specific Patterns

#### Welkin/Elastisys (Kubernetes)

- **Volume:** 61+ ADRs (0000-0061)
- **Pattern:** Detailed technical decisions for K8s infrastructure
- **Methodology notes in index:**
  - Prefer CNCF graduated projects
  - Evaluate security track records
  - Document to mitigate information security risks

#### Apache James

- **Integration:** JIRA tickets + mailing list discussions
- **Status variations:** "Accepted (lazy consensus)" vs "Accepted (voted)"
- **Process-heavy:** Community decision-making embedded in ADR process

#### GitHub Primer React

- **Visual status:** Table with checkmarks
- **Multiple stages:** "Approved" and "Adopted" tracked separately
- **Contributor focus:** Consequences emphasize contributor experience

## Best Practices Synthesis

### For Context Section

1. **Keep it concise:** 2-3 sentences for most decisions
2. **Frame as question:** Helps focus the decision
3. **Include "why now":** If timing is relevant to context
4. **Separate constraints:** If decision has hard requirements

### For Considered Options

1. **Include "do nothing":** When relevant (e.g., "keep existing approach")
2. **2-6 options typical:** Fewer shows limited analysis; more shows analysis paralysis
3. **Brief descriptions:** Save details for pros/cons section
4. **Order doesn't imply preference:** Chosen option often listed first

### For Decision Outcome

1. **State it clearly:** First sentence should be unambiguous
2. **Tie to drivers:** Explain how decision addresses context/constraints
3. **Acknowledge tradeoffs:** If consequences section doesn't cover them

### For Consequences

1. **Be specific:** "Faster deployment" < "Reduces deployment time from 30min to 5min"
2. **Include negatives:** Builds trust and helps future readers
3. **Consider categories:**
   - Technical (performance, maintainability)
   - Process (workflows, approvals)
   - Team (learning curve, expertise)
   - Business (cost, time-to-market)

### For Numbering

1. **Use 4-digit format:** Better for long-lived projects (supports up to 9999 ADRs)
2. **Start at 0000 or 0001:** Both common; 0000 often used for "adopt ADRs" meta-decision
3. **Never reuse numbers:** Even if ADR is rejected/superseded
4. **Sequential only:** Don't try to encode meaning in numbers

### For Superseding

1. **Mark both ADRs:** Old one "superseded by", new one "supersedes"
2. **Keep old ADR:** Don't delete; historical context matters
3. **Explain why:** In new ADR's context, explain what changed
4. **Link bidirectionally:** Makes navigation easier

## Templates Comparison

### Minimal Template (Vue.js example)

```markdown
# [Number] [Title]

## Status
[proposed | accepted | rejected | deprecated | superseded]

## Context and Problem Statement
[1-2 sentences or question]

## Considered Options
- Option 1
- Option 2

## Decision Outcome
[Chosen option] because [brief rationale]
```

**Use when:** Straightforward decision, team agreement, limited analysis needed

### Standard Template (MADR recommended)

```markdown
# [Number] [Title]

## Context and Problem Statement
[2-3 sentences describing situation and question]

## Decision Drivers
- [Driver 1]
- [Driver 2]

## Considered Options
- [Option 1]
- [Option 2]
- [Option 3]

## Decision Outcome
Chosen option: "[Option X]", because [justification tied to drivers]

### Consequences
- Good, because [positive outcome 1]
- Good, because [positive outcome 2]
- Bad, because [negative outcome 1]
- Neutral, because [neutral outcome 1]

## Pros and Cons of the Options

### [Option 1]
- Good, because [argument 1]
- Bad, because [argument 2]

### [Option 2]
- Good, because [argument 1]
- Bad, because [argument 2]
```

**Use when:** Standard architectural decision with multiple viable options

### Detailed Template (API Gateway example)

```markdown
# [Number] [Title]

## Summary
[Brief overview of issue and decision]

## Context and Problem Statement
[Detailed background with paragraphs if needed]

## Constraints
- [Hard requirement 1]
- [Hard requirement 2]

## Decision Drivers
- [Force/concern 1]
- [Force/concern 2]

## Considered Options
- [Option 1] - [Status]
- [Option 2] - [Status]

## Comparative Analysis
[Detailed comparison of options with specific criteria]

## Decision Outcome
[Chosen option] based on:
- [Reason 1]
- [Reason 2]

Status: [Status] ([Date]) with [conditions]

## Consequences
[Specific outcomes categorized by type]

## References
- [Link 1]
- [Link 2]
```

**Use when:** Complex decision, multiple stakeholders, significant impact

## Recommendations for Home Automation System

Based on analysis of 60+ real-world ADRs:

### For First ADR (Adopt ADRs)

- **Number:** 0001 (since this is task-022, not the project's first decision)
- **Content:** Brief, focus on "why ADRs" and "which template"
- **Length:** Keep under 20 lines
- **Consequences:** Process-focused (how will we maintain, where stored, etc.)

### For Subsequent ADRs

1. **Use standard MADR template** for most decisions
2. **4-digit numbering** (0001, 0002, etc.) in `docs/adr/`
3. **Include "do nothing"** option when retrofitting decisions
4. **Be honest about tradeoffs** in consequences
5. **Link to tasks** in references section (e.g., "Implemented in task-022")
6. **YAML front matter** for metadata (status, date, decision-makers)

### Specific to System Architect Agent

1. **First ADR content:** Document the decision to create System Architect Agent role
2. **Context:** Current task-driven development lacks architectural oversight
3. **Options:**
   - Create dedicated SA agent
   - Extend TL agent
   - No formal architecture role
4. **Decision:** Create SA agent with ADR responsibilities
5. **Consequences:**
   - Good: Architectural decisions documented
   - Good: Enables pattern reuse across tasks
   - Bad: Additional process overhead
   - Neutral: Learning curve for MADR format

## Sources

- [MADR Project - GitHub](https://github.com/adr/madr)
- [MADR Examples](https://github.com/adr/madr/tree/main/docs/decisions)
- [Apache James ADRs](https://github.com/apache/james-project/blob/master/src/adr/)
- [GitHub Primer React ADRs](https://github.com/primer/react/blob/main/contributor-docs/adrs/)
- [ADR Manager - Vue.js](https://github.com/adr/adr-manager/blob/main/docs/adr/)
- [Real Scenario Examples](https://github.com/omeerkorkmazz/adr-examples)
- [Welkin/Elastisys ADRs](https://elastisys.io/welkin/adr/)
- [Joel Parker Henderson ADR Collection](https://github.com/joelparkerhenderson/architecture-decision-record)
