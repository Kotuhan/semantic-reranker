---
title: MADR (Markdown Architecture Decision Records) Format
domain: pattern
tech: [markdown, documentation, adr]
area: [architecture, decision-records, documentation]
staleness: 6months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://adr.github.io/madr/
  - https://github.com/adr/madr
  - https://ozimmer.ch/practices/2022/11/22/MADRTemplatePrimer.html
  - https://github.com/joelparkerhenderson/architecture-decision-record
  - https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/
---

# MADR (Markdown Architecture Decision Records) Format

## Overview

MADR (Markdown Architectural Decision Records) is a lightweight, structured format for documenting architectural decisions using Markdown. Version 4.0.0 (released September 2024) is the current stable version.

MADR provides a standardized way to capture **why** architectural decisions were made, not just what was decided. This creates transparent records that help teams maintain consistency, onboard new members, and revisit decisions when circumstances change.

## Key Benefits

- **Plain text format**: Enables version control integration (Git), team collaboration, and tool flexibility
- **Focused content**: Encourages focus on substance over presentation
- **Immutability**: ADRs capture decisions at a point in time, creating an append-only journal
- **Accountability**: Documents who made decisions and why, supporting organizational learning
- **Searchability**: Markdown files are easily searchable across codebases

## 1. Standard MADR Template Structure

### Complete Template (All Sections)

```markdown
---
# Optional metadata elements
status: "{proposed | rejected | accepted | deprecated | superseded by ADR-0123}"
date: {YYYY-MM-DD when the decision was last updated}
decision-makers: {list everyone involved in the decision}
consulted: {list everyone whose opinions are sought (typically SMEs)}
informed: {list everyone kept up-to-date on progress}
---

# {short title, representative of solved problem and found solution}

## Context and Problem Statement

{Describe the context and problem statement in 2-3 sentences or as an
illustrative story. Ideally frame as a question. Add links to collaboration
boards or issue management systems.}

## Decision Drivers

* {decision driver 1, e.g., a force, facing concern, constraint}
* {decision driver 2, e.g., a force, facing concern, constraint}
* … <!-- numbers of drivers can vary -->

## Considered Options

* {title of option 1}
* {title of option 2}
* {title of option 3}
* … <!-- numbers of options can vary -->

## Decision Outcome

Chosen option: "{title of option 1}", because {justification. e.g.,
only option which meets k.o. criterion | which resolves force X |
comes out best (see below)}.

### Consequences

* Good, because {positive consequence, e.g., improvement of quality}
* Bad, because {negative consequence, e.g., compromising quality}
* … <!-- numbers of consequences can vary -->

### Confirmation

{Describe how implementation/compliance will be confirmed. Automated
or manual fitness functions? Design/code review? Testing with ArchUnit?
Note: This is optional but recommended.}

## Pros and Cons of the Options

### {title of option 1}

{example | description | pointer to more information}

* Good, because {argument a}
* Good, because {argument b}
* Neutral, because {argument c}
* Bad, because {argument d}
* …

### {title of option 2}

{example | description | pointer to more information}

* Good, because {argument a}
* Good, because {argument b}
* Neutral, because {argument c}
* Bad, because {argument d}
* …

## More Information

{Additional evidence/confidence for the decision. Team agreement details.
When/how this decision should be realized. When it should be re-visited.
Links to other ADRs and resources.}
```

### Minimal Template (Mandatory Sections Only)

For lighter documentation, these five elements suffice:

1. **Title**: Short, representative of problem and solution
2. **Context and Problem Statement**: What decision needs to be made
3. **Considered Options**: List of alternatives evaluated
4. **Decision Outcome**: Chosen option with justification
5. **Consequences**: Positive and negative impacts

This mirrors Michael Nygard's original 2011 ADR format.

### Template Variants Available

The MADR project provides four template files:

| Template | Description |
|----------|-------------|
| `adr-template.md` | All sections with explanations |
| `adr-template-minimal.md` | Mandatory sections with explanations |
| `adr-template-bare.md` | All sections, empty (no explanations) |
| `adr-template-bare-minimal.md` | Mandatory sections, no explanations |

## 2. Best Practices for Writing ADRs

### Naming and Organization

**File naming convention:**
```
docs/decisions/NNNN-title-with-dashes.md
```

Where:
- `NNNN` is a sequential number (0001, 0002, etc.)
- Title uses lowercase with dashes
- Examples: `0001-use-postgres-for-data-storage.md`, `0023-adopt-microservices-architecture.md`

**Directory structure:**
```
docs/decisions/
├── 0001-use-markdown-adrs.md
├── 0002-choose-cloud-provider.md
├── 0003-select-authentication-method.md
└── ...
```

For large projects, use subdirectories for categorization:
```
docs/decisions/
├── backend/
│   ├── 0001-database-choice.md
│   └── 0005-api-design.md
├── frontend/
│   ├── 0002-ui-framework.md
│   └── 0007-state-management.md
└── infrastructure/
    ├── 0003-deployment-strategy.md
    └── 0009-monitoring-approach.md
```

### Writing Effective Content

#### Context and Problem Statement
- **Be detailed**: Future context may differ, so don't be vague
- **Frame as question**: "How should we store user data?" vs "Database selection"
- **Provide background**: What led to this decision being needed?
- **Link to issues**: Connect to Jira tickets, GitHub issues, or discussion threads

**Example:**
```markdown
## Context and Problem Statement

Our application currently stores all user data in memory, which doesn't
persist across restarts and limits scalability. We need to select a
database that can handle:
- 10,000+ concurrent users
- Real-time queries with <100ms latency
- ACID transactions for financial data

How should we store and retrieve user data reliably at scale?

Related: Issue #234, Slack thread: https://...
```

#### Decision Drivers
- **Identify constraints**: Technical, business, team, regulatory
- **List quality attributes**: Performance, security, maintainability
- **Note forces**: Competing concerns that must be balanced

**Example:**
```markdown
## Decision Drivers

* Must support ACID transactions (regulatory requirement)
* Team has strong PostgreSQL expertise
* Need to minimize infrastructure costs (<$500/month)
* Should integrate with existing Kubernetes deployment
* Performance: <100ms query latency at 10k concurrent users
```

#### Considered Options
- **Same abstraction level**: Don't compare "PostgreSQL" vs "Microservices architecture"
- **Genuinely viable**: Avoid pseudo-alternatives that don't solve the problem
- **Be specific**: "PostgreSQL 15 on AWS RDS" not just "SQL database"

**Bad example:**
```markdown
## Considered Options
* Use a database
* Don't use a database
* Maybe use something else
```

**Good example:**
```markdown
## Considered Options
* PostgreSQL 15 on AWS RDS (managed service)
* MongoDB Atlas (managed NoSQL)
* Self-hosted PostgreSQL on Kubernetes
* Amazon DynamoDB (serverless)
```

#### Decision Outcome and Justification
- **Explain why**: Not just what was chosen, but the reasoning
- **Reference drivers**: Show how choice addresses decision drivers
- **Be honest about trade-offs**: Acknowledge what you're giving up

**Example:**
```markdown
## Decision Outcome

Chosen option: "PostgreSQL 15 on AWS RDS", because:

* **Knock-out criterion**: Only option providing full ACID compliance
  required by financial regulations
* **Team expertise**: 3/5 backend engineers have 5+ years PostgreSQL experience
* **Operational simplicity**: Managed service reduces operational burden
  compared to self-hosting
* **Cost-effective**: $350/month estimated cost fits budget constraint
* **Performance**: Benchmarks show 45ms average query latency under load

This comes with trade-offs: we're accepting vendor lock-in to AWS and
slightly higher costs than self-hosted PostgreSQL, but the reduction in
operational complexity and regulatory compliance justify this.
```

#### Consequences
- **Use structured format**: "Good, because..." and "Bad, because..."
- **Be comprehensive**: Include both immediate and long-term impacts
- **Consider multiple dimensions**: Code, operations, team, business

**Example:**
```markdown
### Consequences

* Good, because RDS handles automated backups, reducing operational burden
* Good, because PostgreSQL's mature ecosystem provides extensive tooling
* Good, because team expertise enables fast development and debugging
* Bad, because RDS costs 30% more than self-hosted (acceptable trade-off)
* Bad, because multi-region setup requires additional configuration
* Neutral, because migration from in-memory storage requires 2 weeks effort
```

### Versioning and Timestamps

**Always include:**
- **Date field**: When decision was last updated (YYYY-MM-DD)
- **Version context**: Which system/component version this affects
- **Status field**: Current state in the lifecycle

**Example:**
```yaml
---
status: accepted
date: 2026-01-29
decision-makers: [Alice Chen (Tech Lead), Bob Smith (Architect)]
consulted: [DevOps team, Security team]
informed: [Engineering org, Product team]
---
```

### Collaboration and Stakeholders

Document the decision-making process:
- **Decision-makers**: Who had voting power
- **Consulted**: SMEs providing input (two-way communication)
- **Informed**: Stakeholders kept updated (one-way communication)

This creates accountability and helps future teams understand the context.

## 3. Status Lifecycle

ADRs progress through defined states to track their lifecycle:

```
proposed → {rejected | accepted}
           ↓
           accepted → {deprecated | superseded by ADR-XXXX}
```

### Status Definitions

| Status | Meaning | When to Use |
|--------|---------|-------------|
| **proposed** | Under discussion, not yet decided | Draft ADR being reviewed |
| **accepted** | Decision made and implementation begun/complete | After team consensus |
| **rejected** | Considered but not chosen | Documenting why an approach was dismissed |
| **deprecated** | No longer recommended but not replaced | Gradual phase-out |
| **superseded by ADR-XXXX** | Replaced by a newer decision | When requirements/context changed |

### Status Management Rules

**Immutability principle:** ADRs should be **append-only**
- ✅ Fix typos and formatting
- ✅ Update STATUS field
- ✅ Add cross-references in "More Information"
- ❌ Don't change the decision or justification
- ❌ Don't rewrite history

**When to supersede:**
```markdown
# In the OLD ADR (0015-use-rest-api.md)
---
status: superseded by ADR-0043
date: 2026-01-29  # Date of supersession
---

# Use REST API for client-server communication

[Original content remains unchanged]

## More Information

**Status Update (2026-01-29):** This decision has been superseded by
ADR-0043 due to new requirements for real-time bidirectional communication
that REST cannot efficiently provide. See ADR-0043 for the new approach.
```

```markdown
# In the NEW ADR (0043-migrate-to-graphql-subscriptions.md)
---
status: accepted
date: 2026-01-29
---

# Migrate to GraphQL with Subscriptions

## Context and Problem Statement

ADR-0015 established REST APIs as our client-server communication pattern.
However, new real-time features (live notifications, collaborative editing)
require bidirectional streaming that REST cannot efficiently provide.

How should we enable real-time bidirectional communication?

## More Information

This ADR supersedes ADR-0015. The REST APIs will remain for legacy endpoints
during a 6-month migration period.
```

### Status Update Examples

**Marking as deprecated:**
```yaml
---
status: deprecated
date: 2026-01-29  # Date of deprecation
---
```

Add note in "More Information":
```markdown
## More Information

**Deprecation Notice (2026-01-29):** While this approach remains functional,
new projects should follow ADR-0052 which provides better performance
characteristics. Existing implementations need not be migrated unless
performance issues arise.
```

## 4. Example ADR in MADR Format

Here's a complete, filled-out example:

```markdown
---
status: accepted
date: 2026-01-29
decision-makers: [Tech Lead, Senior Backend Engineer]
consulted: [QA Lead, DevOps Engineer]
informed: [Engineering Team, Product Manager]
---

# Use Plain JUnit5 for Advanced Test Assertions

## Context and Problem Statement

Our test suite currently uses a mix of assertion libraries (JUnit4,
Hamcrest, AssertJ), leading to inconsistent test styles and requiring
developers to learn multiple APIs. Test readability varies significantly
across the codebase.

How should we write readable test assertions for both simple and advanced
test scenarios while maintaining consistency?

Related: Issue #456 - Test code quality initiative

## Decision Drivers

* **Consistency**: Single assertion style across entire test suite
* **Readability**: Tests should be self-documenting
* **Learning curve**: Minimize ramp-up time for new team members
* **IDE support**: Strong autocomplete and error detection
* **Maintenance burden**: Prefer standard library over external dependencies
* **Existing codebase**: 60% of tests already use JUnit5

## Considered Options

* Plain JUnit5 assertions
* Hamcrest matchers
* AssertJ fluent assertions

## Decision Outcome

Chosen option: "Plain JUnit5 assertions", because:

1. **Already present**: No new dependency required (JUnit5 is our test framework)
2. **Consistency**: 60% of existing tests use JUnit5; consolidating reduces fragmentation
3. **Learning curve**: Standard library assertions familiar to all Java developers
4. **IDE support**: IntelliJ IDEA and Eclipse provide excellent support
5. **Sufficient capabilities**: JUnit5's `assertAll`, `assertThrows`, `assertTimeout`
   cover our advanced testing needs

Trade-off: AssertJ offers more readable fluent API, but the benefits don't
justify adding another dependency when JUnit5 assertions meet our requirements.

### Consequences

* Good, because removing Hamcrest/AssertJ dependencies reduces JAR size by ~800KB
* Good, because single assertion style improves test readability and consistency
* Good, because JUnit5 assertions are well-documented and widely understood
* Good, because reduced cognitive load when reading tests (one API to learn)
* Bad, because some complex assertions (deep object comparison) are more
  verbose than AssertJ equivalents
* Bad, because requires refactoring 40% of existing tests (estimated 3 days effort)
* Neutral, because IDE refactoring tools can automate most assertion migrations

### Confirmation

Implementation compliance will be confirmed through:

1. **Automated checks**: Add ArchUnit rule to fail build if Hamcrest/AssertJ
   imports detected in new test files
2. **Code review**: PR template includes checklist item "Uses JUnit5 assertions"
3. **Migration tracking**: GitHub issue #456 tracks refactoring progress
4. **Documentation**: Update testing guidelines in wiki with examples

Migration deadline: 2026-03-01 (6 weeks)

## Pros and Cons of the Options

### Plain JUnit5

JUnit5 is the standard testing framework for Java, providing built-in
assertions without additional dependencies.

* Good, because no additional dependencies needed
* Good, because familiar to all Java developers (standard library)
* Good, because excellent IDE support (autocomplete, quick fixes)
* Good, because sufficient for 95% of our assertion needs
* Good, because `assertAll()` enables multiple assertions with full reporting
* Neutral, because assertion messages require explicit string formatting
* Bad, because complex object comparison more verbose than alternatives
* Bad, because lacks fluent API style (some developers prefer chaining)

Example:
```java
@Test
void testUser() {
    User user = userService.findById(123);
    assertAll(
        () -> assertEquals("Alice", user.getName()),
        () -> assertTrue(user.isActive()),
        () -> assertNotNull(user.getEmail())
    );
}
```

### Hamcrest

Hamcrest provides matcher-based assertions with a readable syntax.

Homepage: http://hamcrest.org/

* Good, because readable "assertThat" syntax
* Good, because extensive matcher library for collections, strings
* Good, because custom matchers enable domain-specific assertions
* Neutral, because requires learning matcher API (not standard Java)
* Bad, because adds external dependency (~300KB JAR)
* Bad, because matcher composition can be confusing for complex cases
* Bad, because IDE support weaker than JUnit5 assertions

Example:
```java
@Test
void testUser() {
    User user = userService.findById(123);
    assertThat(user.getName(), is(equalTo("Alice")));
    assertThat(user.isActive(), is(true));
    assertThat(user.getEmail(), is(notNullValue()));
}
```

### AssertJ

AssertJ provides fluent assertion API with strong typing and discoverability.

Homepage: https://assertj.github.io/doc/

* Good, because most readable fluent API (chaining)
* Good, because excellent IDE autocomplete due to strong typing
* Good, because extensive assertion library (dates, files, exceptions)
* Good, because superior error messages with detailed diffs
* Good, because soft assertions (`assertSoftly`) group multiple checks
* Neutral, because custom assertions require some boilerplate
* Bad, because adds external dependency (~500KB JAR)
* Bad, because another API for team to learn and maintain
* Bad, because not standard library (less familiar to new hires)

Example:
```java
@Test
void testUser() {
    User user = userService.findById(123);
    assertThat(user)
        .hasFieldOrPropertyWithValue("name", "Alice")
        .extracting(User::isActive).isEqualTo(true);
    assertThat(user.getEmail()).isNotNull();
}
```

## More Information

**Team Agreement:** Decision approved by unanimous consensus at 2026-01-29
architecture review meeting (5/5 attendees).

**Confidence Level:** High - This decision addresses a clear pain point
(inconsistent test styles) with measurable benefits (reduced dependencies,
improved consistency).

**Implementation Plan:**
- Week 1-2: Add ArchUnit rule, update documentation
- Week 3-4: Refactor high-traffic test files (services, controllers)
- Week 5-6: Refactor remaining test files
- Week 6: Remove Hamcrest/AssertJ dependencies

**Related Decisions:**
- ADR-0008: Adopted JUnit5 as standard test framework
- ADR-0034: Established test coverage requirements

**Re-evaluation Trigger:** If JUnit5 assertions prove insufficient for >10%
of new tests, revisit this decision and consider adopting AssertJ.
```

## 5. Common Mistakes to Avoid

### ❌ Mistake #1: Editing Past Decisions

**Wrong:**
```markdown
# ADR-0015 (originally from 2024)
---
status: accepted
date: 2026-01-29  # Updated!
---

# Use GraphQL instead of REST  <-- Changed!

We chose GraphQL because... <-- Rewritten!
```

**Right:**
```markdown
# ADR-0015 (from 2024)
---
status: superseded by ADR-0043
date: 2024-06-15  # Original date preserved
---

# Use REST API for client-server communication

[Original content unchanged]

## More Information

**Status Update (2026-01-29):** Superseded by ADR-0043.
```

**Why:** ADRs capture decisions at a point in time. Rewriting history obscures
the evolution of your architecture and loses valuable context.

### ❌ Mistake #2: Vague Context

**Wrong:**
```markdown
## Context and Problem Statement

We need to pick a database.
```

**Right:**
```markdown
## Context and Problem Statement

Our event-sourcing system currently stores events in PostgreSQL, but
write throughput has become a bottleneck. We're seeing 500ms write latency
during peak hours (10k events/sec), which delays order processing.

We need an event store that can:
- Handle 50k events/sec write throughput
- Provide optimistic concurrency control
- Support event replay for projections
- Cost <$2k/month at scale

How should we store and retrieve events reliably at high throughput?

Related: Issue #789 - Order processing delays
```

**Why:** Future readers won't have the context you have today. Detailed
problem statements help them understand why this decision mattered.

### ❌ Mistake #3: Pseudo-Alternatives

**Wrong:**
```markdown
## Considered Options

* PostgreSQL (the right choice)
* NoSQL databases (too risky)
* Not using a database (obviously wrong)
```

**Right:**
```markdown
## Considered Options

* EventStoreDB (purpose-built event store)
* Apache Kafka (distributed event log)
* PostgreSQL with optimizations (current approach)
* Amazon EventBridge (managed event bus)
```

**Why:** ADRs should document genuine alternatives that were seriously
considered. Straw-man options undermine credibility.

### ❌ Mistake #4: Missing Justification

**Wrong:**
```markdown
## Decision Outcome

Chosen option: "EventStoreDB".
```

**Right:**
```markdown
## Decision Outcome

Chosen option: "EventStoreDB", because:

1. **Purpose-built**: Designed specifically for event sourcing patterns
2. **Performance**: Benchmarks show 80k writes/sec (exceeds 50k requirement)
3. **Optimistic concurrency**: Built-in support via stream versioning
4. **Projections**: Native support for event replay and projections
5. **Cost**: $1,200/month at projected scale (fits budget)

PostgreSQL with partitioning was close, but EventStoreDB's native event
sourcing features (projections, stream categories) reduce custom code by ~40%.
```

**Why:** The justification is the most valuable part of an ADR. It explains
the reasoning that led to the decision.

### ❌ Mistake #5: Inconsistent Abstraction Levels

**Wrong:**
```markdown
## Considered Options

* Use microservices architecture
* PostgreSQL database
* Implement caching
* Deploy to Kubernetes
```

**Right:**
```markdown
## Considered Options

* Microservices architecture
* Modular monolith architecture
* Service-oriented architecture (SOA)
```

**Why:** Options should address the same question at the same level of
abstraction. Mixing architectural patterns with technology choices creates
confusion.

### ❌ Mistake #6: Incomplete Consequences

**Wrong:**
```markdown
### Consequences

* Good, because it's better than the old approach
```

**Right:**
```markdown
### Consequences

* Good, because 80k writes/sec meets performance requirements with 60% headroom
* Good, because native event sourcing features reduce custom code maintenance
* Good, because built-in projections simplify read model updates
* Bad, because team must learn new database system (estimated 2 weeks ramp-up)
* Bad, because EventStoreDB expertise is rare (hiring challenge)
* Bad, because migration requires 3 weeks downtime or complex dual-write period
* Neutral, because $1,200/month cost is higher than PostgreSQL but within budget
```

**Why:** Comprehensive consequences help future teams understand the full
impact of the decision, both immediate and long-term.

### ❌ Mistake #7: No Validation Plan

**Wrong:**
```markdown
## Decision Outcome

Chosen option: "EventStoreDB"

[No confirmation section]
```

**Right:**
```markdown
### Confirmation

Implementation will be validated through:

1. **Load testing**: Run 80k events/sec for 1 hour in staging
2. **Latency monitoring**: P99 write latency must stay <50ms
3. **Code review**: Verify event sourcing patterns follow EventStoreDB best practices
4. **ArchUnit tests**: Ensure aggregate boundaries are not violated
5. **Gradual rollout**: 10% → 50% → 100% traffic over 2 weeks

Success criteria:
- Zero data loss during migration
- P99 write latency <50ms
- No rollback needed after 100% traffic
```

**Why:** A validation plan ensures the decision's implementation is measured
against its goals and can be verified objectively.

## 6. How to Reference Other ADRs

### Superseding an ADR

When a decision needs to be changed due to new requirements, context changes,
or learning:

**Step 1: Update the old ADR**
```markdown
# docs/decisions/0015-use-rest-api.md
---
status: superseded by ADR-0043
date: 2024-08-10  # Original decision date (unchanged)
---

# Use REST API for client-server communication

[Original content remains unchanged]

## More Information

**Status Update (2026-01-29):** This decision has been superseded by
ADR-0043 "Migrate to GraphQL Subscriptions" due to new requirements for
real-time bidirectional communication that REST cannot efficiently provide.

The REST APIs will remain operational for 6 months during migration to
maintain backward compatibility with mobile clients.
```

**Step 2: Create the new ADR**
```markdown
# docs/decisions/0043-migrate-to-graphql-subscriptions.md
---
status: accepted
date: 2026-01-29
---

# Migrate to GraphQL with Subscriptions for Real-Time Features

## Context and Problem Statement

ADR-0015 established REST APIs as our client-server communication pattern
in 2024. This worked well for request-response scenarios.

However, our 2026 roadmap introduces real-time collaborative features:
- Live notifications (100+ updates/minute per user)
- Collaborative document editing
- Real-time dashboard updates

REST requires polling, which creates 10x more traffic and 5s latency.
WebSockets would work but lack type safety and tooling.

How should we enable efficient real-time bidirectional communication with
type safety?

## Decision Outcome

Chosen option: "GraphQL with Subscriptions"...

## More Information

**Relationship to Other Decisions:**
- **Supersedes ADR-0015**: REST remains for legacy endpoints during 6-month migration
- **Builds on ADR-0028**: Uses existing TypeScript schema definitions
- **Complements ADR-0035**: Authentication middleware applies to both REST and GraphQL
```

### Amending an ADR

When you need to add information without changing the core decision:

```markdown
# docs/decisions/0020-use-postgresql-rds.md
---
status: accepted
date: 2025-03-15  # Original date
---

# Use PostgreSQL on AWS RDS

[Original content]

## More Information

[Original content]

**Amendment (2026-01-29):** After 10 months in production, we've learned:
- Read replica scaling works well (added 2 replicas per ADR-0038)
- Connection pooling required PgBouncer (see ADR-0041)
- Monthly costs stable at $420/month (within budget)

These learnings don't change the core decision but provide valuable
implementation insights for future projects.
```

### Cross-Referencing Related ADRs

Build a web of related decisions to show architectural evolution:

```markdown
## More Information

**Related Decisions:**

**Prerequisites:**
- ADR-0008: Established Kubernetes as deployment platform (enables RDS VPC setup)
- ADR-0012: Selected AWS as cloud provider (enables RDS usage)

**Depends on this:**
- ADR-0038: Add read replicas for query scaling
- ADR-0041: Use PgBouncer for connection pooling
- ADR-0045: Implement automatic failover procedures

**Alternatives considered:**
- ADR-0019: Rejected DynamoDB due to ACID requirements (see decision drivers)

**Related context:**
- ADR-0025: Backup and disaster recovery strategy
- ADR-0030: Data retention and archival policy
```

### Linking in Decision Outcome

Reference related decisions directly in your justification:

```markdown
## Decision Outcome

Chosen option: "PostgreSQL on AWS RDS", because:

1. **Consistency with ADR-0012**: We're already standardized on AWS, and
   RDS integrates with our existing VPC setup (ADR-0008)
2. **Rejected alternative in ADR-0019**: DynamoDB was considered but lacks
   the ACID guarantees required by our financial transaction processing
3. **Enables future scaling**: This decision unblocks ADR-0038 (read replicas)
   and ADR-0041 (connection pooling)
```

### Timeline View

For complex architectural evolutions, create a timeline in a summary ADR:

```markdown
# docs/decisions/0050-database-evolution-summary.md

# Summary: Database Architecture Evolution (2024-2026)

This ADR summarizes the evolution of our database architecture over 2 years.

## Timeline

**2024-03-15** - ADR-0015: Initial PostgreSQL selection
- Chose PostgreSQL for ACID compliance
- Single RDS instance, 4 vCPU, 16GB RAM

**2024-08-10** - ADR-0025: Added automated backups
- 7-day retention, daily snapshots
- Cross-region backup replication

**2025-11-20** - ADR-0038: Scaled with read replicas
- Added 2 read replicas for query load
- Implemented read/write splitting in application

**2026-01-15** - ADR-0041: Introduced connection pooling
- Added PgBouncer due to connection exhaustion
- Reduced connection count from 5000 to 500

**2026-01-29** - ADR-0045: Automated failover procedures
- Implemented health checks and automatic failover
- Recovery Time Objective (RTO): <5 minutes

## Key Learnings

[...]
```

## Project Integration

For the Home Automation project's System Architect agent (task-022):

### Implementation Guidelines

1. **Location**: Store ADRs in `docs/decisions/`
2. **Naming**: `NNNN-title-with-dashes.md` (e.g., `0001-use-madr-format.md`)
3. **Categories**: Use subdirectories for large projects
   - `docs/decisions/esphome/`
   - `docs/decisions/homeassistant/`
   - `docs/decisions/infrastructure/`
4. **Index**: Maintain `docs/decisions/README.md` listing all ADRs with status
5. **Integration**: System Architect agent should:
   - Detect architectural decisions in task contexts
   - Propose ADR creation when significant decisions are made
   - Update existing ADRs when superseded
   - Maintain cross-references between related ADRs
   - Ensure compliance with MADR format

### Example Use Cases for Home Automation

Potential ADRs for this project:
- **0001-use-esp32s3-for-bms-reader**: Why ESP32S3 over ESP8266/ESP32
- **0002-choose-esphome-over-arduino**: Firmware framework selection
- **0003-ha-vs-autonomous-control**: Current HA-based vs future ESP32-autonomous
- **0004-tuya-local-vs-esphome-plugs**: Smart plug technology decision
- **0005-docker-compose-deployment**: Why Docker vs bare metal for HA
- **0006-battery-chemistry-nmc**: Confirmed Li-ion NMC, not LiFePO4
- **0007-grid-detection-via-current**: Why current sensor vs voltage for grid detection

### Agent Workflow

```
1. Monitor task completion → Detect architectural decision
2. Check if decision qualifies for ADR (significant, reversible, trade-offs)
3. Propose ADR creation to user
4. Generate ADR draft using MADR template
5. Save to docs/decisions/NNNN-{slug}.md
6. Update docs/decisions/README.md index
7. Cross-reference related ADRs
8. Commit with descriptive message
```

## Sources

- [GitHub - adr/madr: Markdown Architectural Decision Records](https://github.com/adr/madr)
- [About MADR | MADR](https://adr.github.io/madr/)
- [The MADR Template Explained and Distilled](https://ozimmer.ch/practices/2022/11/22/MADRTemplatePrimer.html)
- [GitHub - joelparkerhenderson/architecture-decision-record](https://github.com/joelparkerhenderson/architecture-decision-record)
- [Master architecture decision records (ADRs): Best practices | AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/)
- [8 best practices for creating architecture decision records | TechTarget](https://www.techtarget.com/searchapparchitecture/tip/4-best-practices-for-creating-architecture-decision-records)
