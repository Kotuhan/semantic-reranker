---
title: System Design Documentation Best Practices for AI-Powered SaaS Applications
domain: pattern
tech: [system-design, documentation, architecture, saas, ai, llm, nextjs, nestjs]
area: [architecture, documentation, system-design, saas, freemium, ai-integration, streaming]
staleness: 6months
created: 2026-01-30
updated: 2026-01-30
sources:
  - https://www.systemdesignhandbook.com/guides/system-design/
  - https://www.atlassian.com/work-management/knowledge-sharing/documentation/software-design-document
  - https://medium.com/@ar.aldhafeeri11/ive-written-over-100-system-design-papers-as-a-professional-consultant-here-s-the-template-i-3fe7d48ef523
  - https://dev.to/adityasatrio/comparing-software-architecture-documentation-models-and-when-to-use-them-495n
  - https://arc42.org/overview
  - https://docs.arc42.org/home/
  - https://c4model.com/
  - https://github.com/arc42/arc42-template
  - https://medium.com/nerd-for-tech/an-introduction-to-arc42-283b559d62cc
  - https://dev.to/divyanshulohani/implementing-real-time-chat-with-sse-vs-websockets-and-why-i-chose-one-2mn2
  - https://medium.com/codetodeploy/why-server-sent-events-beat-websockets-for-95-of-real-time-cloud-applications-830eff5a1d7c
  - https://dev.to/hobbada/the-complete-guide-to-streaming-llm-responses-in-web-applications-from-sse-to-real-time-ui-3534
  - https://apidog.com/blog/stream-llm-responses-using-sse/
  - https://kotrotsos.medium.com/claude-code-internals-part-7-sse-stream-processing-c620ae9d64a1
  - https://medium.com/appfoster/architecture-patterns-for-saas-platforms-billing-rbac-and-onboarding-964ea071f571
  - https://dev.to/aniefon_umanah_ac5f21311c/feature-gating-how-we-built-a-freemium-saas-without-duplicating-components-1lo6
  - https://demogo.com/2025/06/25/feature-gating-strategies-for-your-saas-freemium-model-to-boost-conversions/
  - https://userpilot.com/blog/saas-reverse-trial/
  - https://www.secondtalent.com/resources/top-llm-frameworks-for-building-ai-agents/
  - https://machinelearningmastery.com/7-agentic-ai-trends-to-watch-in-2026/
  - https://www.clarifai.com/blog/llms-and-ai-trends
---

# System Design Documentation Best Practices for AI-Powered SaaS Applications

## Overview

This research synthesizes best practices for documenting system design in AI-powered SaaS applications with freemium models and real-time streaming features. It combines industry-standard documentation frameworks (C4, arc42, ADR) with specific patterns for LLM integration, subscription systems, and SSE streaming architectures.

**Target Context**: Your project is a relationship communication app with:
- Free translator (anonymous-first)
- Paid AI chat adviser with memory (SSE streaming)
- Progressive monetization (freemium → trial → subscription)
- Tech stack: Next.js 14, NestJS, Prisma, PostgreSQL, Redis, Claude API, Paddle

## Key Findings

### 1. Documentation Format Recommendations for SaaS Startups

#### Recommended Hybrid Approach: C4 + ADR + Lightweight arc42

**For startups and fast-moving teams**, the optimal documentation strategy is:

1. **C4 Model for Visualization** (4 levels of detail)
2. **ADRs (MADR format) for Decisions** (lightweight, markdown)
3. **Selective arc42 Sections** (skip heavy process, focus on key areas)

**Why This Combination Works:**
- C4 provides clear visual communication for diverse stakeholders
- ADRs create decision history without heavyweight process
- arc42 provides structure without overwhelming early-stage teams

### 2. System Design Document Essential Sections

Based on analysis of 100+ professional system design documents, the core template includes:

#### 2.1 Document Structure

```markdown
# System Design Document: {Product Name}

## 1. Introduction
### 1.1 Product Overview
- Purpose: What problem does this solve?
- Goals: Business objectives
- Scope: What's in/out of scope

### 1.2 Stakeholders
- Engineering team
- Product Owner
- QA Engineer
- End users (personas)

### 1.3 Quality Goals (Top 3)
Priority-ordered quality attributes:
1. **Availability**: 99.5% uptime for paid users
2. **Performance**: <100ms API response, <500ms LLM first token
3. **Security**: PCI DSS compliant billing, GDPR compliant data

## 2. Constraints
### 2.1 Technical Constraints
- Must use Paddle for payments (business decision)
- Must use Claude API (no self-hosted LLMs)
- Must support anonymous users (legal requirement)

### 2.2 Organizational Constraints
- Team size: 1-3 developers
- Budget: $X/month for infrastructure
- Timeline: MVP in N months

### 2.3 Conventions
- Monorepo: Turborepo + pnpm workspaces
- API: RESTful + SSE for streaming
- Database: Single Postgres instance (vertical scaling first)

## 3. System Context (C4 Level 1)
{High-level diagram showing system boundaries}

**External Systems**:
- Claude API (Anthropic)
- Paddle (Payments)
- Supabase (Postgres hosting)
- Upstash (Redis)
- Email provider

**Users**:
- Anonymous users (translator)
- Registered users (Deep Dive)
- Admins

## 4. Solution Strategy
### 4.1 Key Architectural Decisions
- **Anonymous-first architecture**: JWT tokens for all users (anon + registered)
- **SSE for streaming**: Simpler than WebSockets, good enough for unidirectional LLM output
- **Monolithic backend**: Single NestJS app (microservices later if needed)
- **Shared types package**: TypeScript types shared between frontend/backend

### 4.2 Technology Choices
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend | Next.js 14 App Router | SEO, server components, edge deployment |
| Backend | NestJS | TypeScript, DI, enterprise patterns |
| Database | PostgreSQL (Supabase) | Relational, ACID, mature ecosystem |
| Cache | Redis (Upstash) | Session store, rate limiting, caching |
| LLM | Claude API | Best-in-class reasoning, JSON mode, streaming |
| Payments | Paddle | Merchant of record, handles tax/compliance |
| UI | shadcn/ui + Tailwind | Customizable, accessible, modern |

## 5. Building Block View (C4 Level 2: Containers)
{Container diagram showing apps, services, databases}

### 5.1 Containers
- **Web App** (Next.js): Server-side rendered UI
- **API Server** (NestJS): Business logic, DB access
- **Database** (PostgreSQL): User data, sessions, translations, memories
- **Cache** (Redis): Session store, rate limiting, temporary data
- **CDN** (Vercel Edge): Static assets, edge functions

## 6. Runtime View: Key Scenarios
### 6.1 Anonymous Translation Flow
{Sequence diagram: User → Web App → API → Claude API → Response}

### 6.2 Deep Dive Streaming Flow
{Sequence diagram: User → Web App → API → Claude Stream → SSE → UI update}

### 6.3 Subscription Webhook Flow
{Sequence diagram: Paddle → Webhook → API → DB update → User notification}

### 6.4 Trial Expiration Flow
{State diagram: Active trial → Expiring soon → Expired → Paywall}

## 7. Deployment View
### 7.1 Infrastructure
- **Frontend**: Vercel (Next.js)
- **Backend**: Fly.io / Railway / Render (Docker container)
- **Database**: Supabase (managed Postgres)
- **Cache**: Upstash (serverless Redis)

### 7.2 Environments
- **Development**: Local (Docker Compose)
- **Staging**: Vercel preview + staging backend
- **Production**: Production deployments

## 8. Crosscutting Concepts
### 8.1 Security
- **Authentication**: JWT (access + refresh tokens)
- **Authorization**: Guard-based (JwtAuthGuard, TrialGuard, RegisteredUserGuard)
- **Encryption**: bcrypt for passwords, AES for sensitive data
- **API Security**: Rate limiting, CORS, helmet.js

### 8.2 Session Management
- Anonymous users: JWT with `isAnonymous: true`
- Registered users: JWT with user ID
- Refresh tokens: Stored in Redis with expiration

### 8.3 Error Handling
- API: NestJS exception filters (standardized error responses)
- Frontend: Error boundaries, toast notifications
- LLM: Retry with exponential backoff, fallback messages

### 8.4 Observability
- Logging: Structured JSON logs (Winston)
- Monitoring: Sentry (errors), Uptime monitoring
- Metrics: Token usage tracking, API latency

## 9. Architecture Decisions (ADRs)
{Link to MADR files in `architecture/decisions/`}

Key decisions:
- **ADR-001**: Use anonymous-first JWT architecture
- **ADR-002**: Choose SSE over WebSockets for streaming
- **ADR-003**: Implement trial guard pattern for feature gating
- **ADR-004**: Use Paddle instead of Stripe
- **ADR-005**: Monorepo with Turborepo

## 10. Quality Requirements
### 10.1 Performance
- **API Latency**: p95 < 200ms (non-streaming)
- **LLM First Token**: p95 < 500ms
- **LLM Total Response**: p95 < 10s for typical response
- **Frontend Load**: p95 < 2s (FCP)

### 10.2 Scalability
- **Target Users**: 10,000 MAU (MVP), 100,000 MAU (scale)
- **Concurrent Sessions**: 1,000 simultaneous Deep Dive chats
- **Database**: Single Postgres instance → read replicas at scale

### 10.3 Reliability
- **Uptime**: 99.5% for paid users
- **Data Durability**: Automated daily backups
- **Disaster Recovery**: RPO 24h, RTO 4h

### 10.4 Security
- **Authentication**: Industry-standard JWT
- **Data Privacy**: GDPR compliant, user data deletion
- **Payment Security**: PCI DSS via Paddle (Merchant of Record)

## 11. Risks and Technical Debt
### 11.1 Known Risks
- **LLM API Reliability**: Claude API downtime → fallback message
- **Cost Scaling**: LLM costs scale with usage → monitor and optimize
- **Trial Abuse**: Anonymous users creating multiple accounts → IP-based rate limiting

### 11.2 Technical Debt
- **No database migrations in prod yet**: Need Prisma migration strategy
- **No rate limiting per user**: Currently IP-based only
- **No LLM cost tracking**: Need token usage per user

## 12. Glossary
- **Anonymous User**: User without registration, limited features
- **Deep Dive**: AI chat mode with memory and context
- **Translator**: Instant message decode mode (free forever)
- **Trial**: 72-hour full access period for registered users
- **Reverse Trial**: Full access first, then downgrade to freemium
```

## 3. Documentation Formats Comparison

### 3.1 C4 Model

**Purpose**: Hierarchical visualization from high-level context down to code-level components.

**Structure**: Four levels—Context, Container, Component, Code

**When to Use**:
- Agile teams
- Developer-centric communication
- Fast onboarding scenarios
- SaaS products needing rapid stakeholder alignment

**Advantages**:
- Low-to-medium overhead
- Visual clarity for diverse audiences
- Naturally supports quick developer onboarding
- Works well with PlantUML, Structurizr, IcePanel

**Disadvantages**:
- Primarily diagram-focused
- Limited guidance on rationale documentation
- Requires supplementation with ADRs for decisions

**Example C4 Levels for the project:**

```
Level 1 (Context):
┌───────────────────────────────────────────────┐
│          the project System Context             │
│                                               │
│  [Anonymous User]  [Registered User]          │
│         │                 │                   │
│         └────────┬────────┘                   │
│                  │                            │
│                  ▼                            │
│         ┌────────────────┐                    │
│         │   the project    │                    │
│         │   Platform     │                    │
│         └────────┬───────┘                    │
│                  │                            │
│         ┌────────┼────────┬──────────┐        │
│         │        │        │          │        │
│         ▼        ▼        ▼          ▼        │
│      [Claude] [Paddle] [Supabase] [Upstash]  │
│        API    Payments   Postgres    Redis    │
└───────────────────────────────────────────────┘

Level 2 (Container):
┌──────────────────────────────────────────────────┐
│  [Browser]                                       │
│      │                                           │
│      ▼                                           │
│  ┌─────────────┐                                 │
│  │  Next.js    │  HTTPS/SSE                      │
│  │  Web App    ├──────────────────┐              │
│  │  (Vercel)   │                  │              │
│  └─────────────┘                  ▼              │
│                          ┌──────────────────┐    │
│                          │   NestJS API     │    │
│                          │   (Docker)       │    │
│                          └────┬──────┬──────┘    │
│                               │      │           │
│                     ┌─────────┘      └────────┐  │
│                     ▼                         ▼  │
│              ┌──────────┐              ┌─────────┐│
│              │PostgreSQL│              │  Redis  ││
│              │(Supabase)│              │(Upstash)││
│              └──────────┘              └─────────┘│
└──────────────────────────────────────────────────┘
```

### 3.2 arc42 Template

**Purpose**: Comprehensive architecture template addressing structure, decisions, quality attributes, and cross-cutting concerns.

**Structure**: 12 sections covering all aspects of architecture

**When to Use**:
- Teams looking for a complete architecture documentation template
- Projects requiring thorough coverage across multiple concerns
- Regulated environments (ISO 42010 compliance)

**Advantages**:
- Structured yet flexible
- Captures decision rationale
- Suitable for regulated environments
- Covers quality requirements, risks, glossary

**Disadvantages**:
- Can feel overwhelming initially
- Requires discipline to maintain
- Overkill for early-stage startups

**Recommended for SaaS Startups**: Use **selective arc42** sections:

| arc42 Section | Priority | Notes |
|---------------|----------|-------|
| 1. Introduction and Goals | ✅ Essential | Product overview, quality goals |
| 2. Constraints | ✅ Essential | Technical/organizational limits |
| 3. Context and Scope | ✅ Essential | C4 Level 1 equivalent |
| 4. Solution Strategy | ✅ Essential | Key tech decisions |
| 5. Building Block View | ✅ Essential | C4 Level 2/3 equivalent |
| 6. Runtime View | ✅ Essential | Sequence diagrams, flows |
| 7. Deployment View | ⚠️ Optional | Infrastructure (important for SaaS) |
| 8. Crosscutting Concepts | ✅ Essential | Security, error handling, sessions |
| 9. Architecture Decisions | ✅ Essential | Use MADR format |
| 10. Quality Requirements | ⚠️ Optional | Performance targets (important for SaaS) |
| 11. Risks and Technical Debt | ⚠️ Optional | Known issues (important for transparency) |
| 12. Glossary | ⚠️ Optional | Domain terms (useful for product clarity) |

**Recommendation**: Start with sections 1-6, 8-9. Add 7, 10-12 as product matures.

### 3.3 ADR (Architecture Decision Records)

**Purpose**: Document individual architectural or technical decisions as short markdown/text files.

**Format**: MADR (Markdown Architecture Decision Records) is the most popular lightweight format.

**When to Use**:
- All projects (minimal overhead)
- Agile teams needing decision audit trails
- Complements higher-level documentation (C4, arc42)

**Advantages**:
- Minimal overhead
- Creates maintainable decision history
- Excellent for distributed teams
- Version-controlled alongside code

**Disadvantages**:
- Not a complete documentation framework
- Requires supplementation with diagrams

**MADR Template**:

```markdown
---
status: {proposed | accepted | rejected | deprecated | superseded}
date: YYYY-MM-DD
decision-makers: [Tech Lead, CTO, ...]
---

# {Decision Title}

## Context and Problem Statement

{Describe the context and problem statement}

How do we {achieve goal X} given {constraint Y}?

## Considered Options

* Option 1: {description}
* Option 2: {description}
* Option 3: {description}

## Decision Outcome

Chosen option: "{option}", because:
1. {reason 1}
2. {reason 2}
3. {reason 3}

### Consequences

* Good, because {positive consequence}
* Good, because {positive consequence}
* Bad, because {negative consequence}
* Bad, because {negative consequence}

## More Information

{Links to related decisions, tasks, research}
```

### 3.4 RFC (Request for Comments)

**Purpose**: Propose changes and gather team input before implementation.

**When to Use**:
- Major architectural changes
- Breaking changes to APIs
- Controversial decisions requiring consensus

**Format**:
- Problem statement
- Proposed solution
- Alternatives considered
- Open questions
- Implementation plan

**Relationship to ADR**:
- RFC → Discussion → Decision → ADR
- RFCs are temporary (archived after decision)
- ADRs are permanent (record of decision)

### 3.5 Design Docs at Google Style

**Purpose**: Proposal document for significant technical work.

**Structure**:
- Context and scope
- Goals and non-goals
- Design overview
- Detailed design
- Alternatives considered
- Cross-cutting concerns

**When to Use**:
- Major feature development
- Requires review/approval before implementation
- Similar to RFC but more detailed

**For Startups**: Too heavyweight for most decisions. Use ADRs instead.

## 4. AI-Powered Application System Design Patterns

### 4.1 LLM Integration Architecture Patterns (2026)

#### Multi-Agent Architectures

**Trend**: Single all-purpose agents are being replaced by orchestrated teams of specialized agents, with "puppeteer" orchestrators coordinating specialist agents.

**Pattern**: Director + Specialist Agents

```
┌────────────────────────────────────────────────┐
│              User Request                      │
└───────────────┬────────────────────────────────┘
                │
                ▼
       ┌────────────────┐
       │    Director    │
       │  Orchestrator  │
       └───────┬────────┘
               │
       ┌───────┼───────┬───────┐
       │       │       │       │
       ▼       ▼       ▼       ▼
   [Research][Code][QA][Design]
   Specialist Specialist Specialist Specialist
```

**Application to the project**:
- Not immediately applicable (single LLM interaction)
- Consider for future "Deep Dive" enhancements (research agent, relationship expert agent, etc.)

#### Seven Essential LLM Design Patterns

1. **ReAct** (Reasoning + Acting): LLM reasons about next action, executes, observes result, repeats
2. **Reflection**: LLM evaluates its own output and refines
3. **Tool Use**: LLM decides which tools/APIs to call
4. **Planning**: Break complex tasks into subtasks
5. **Multi-Agent Collaboration**: Multiple LLMs with different roles
6. **Sequential Workflows**: Chain of LLM calls (output → next input)
7. **Human-in-the-Loop (HITL)**: LLM suggests, human approves

**Application to the project**:
- **Translator**: Simple single-shot pattern (no multi-turn)
- **Deep Dive**: Sequential workflow (chat history → context → response)
- **Future**: Reflection (LLM evaluates relationship advice quality)

#### Human-in-the-Loop (HITL) Integration

**Pattern**: Hybrid human-agent systems producing better outcomes than either alone.

**Application to the project**:
- User provides original message + context
- LLM provides decoded interpretation
- User validates/refines before taking action

#### Cost Optimization: Plan-and-Execute Pattern

**Pattern**: Capable model creates strategy, cheaper models execute.

**Cost Savings**: Up to 90% compared to using frontier models for everything.

**Application to the project**:
- Use Claude Opus for initial Deep Dive context understanding
- Use Claude Sonnet for follow-up chat responses
- Use Claude Haiku for simple translation tasks

**Implementation**:

```typescript
// Cost-tiered model selection
function selectModel(task: TaskType): ClaudeModel {
  switch (task) {
    case 'deep-dive-init':
      return 'claude-opus-4'; // Best reasoning for context setup
    case 'deep-dive-followup':
      return 'claude-sonnet-4'; // Good balance for chat
    case 'translator':
      return 'claude-haiku-3.5'; // Fast and cheap for simple decode
  }
}
```

### 4.2 LLM Streaming Architecture

#### SSE (Server-Sent Events) for LLM Streaming

**Why SSE is the Standard for LLM Streaming**:
- OpenAI, Anthropic, and most LLM APIs use SSE natively
- Simpler than WebSockets (HTTP-based, no protocol upgrade)
- Automatic reconnection in browsers
- Works over standard HTTP infrastructure (firewalls, proxies)

**SSE Format**:

```
Content-Type: text/event-stream

event: message_start
data: {"type":"message_start","message":{...}}

event: content_block_start
data: {"type":"content_block_start","index":0}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"The"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" meaning"}}

event: message_stop
data: {"type":"message_stop"}
```

**NestJS SSE Controller Pattern**:

```typescript
import { Controller, Sse, UseGuards } from '@nestjs/common';
import { Observable } from 'rxjs';

@Controller('chat')
export class ChatController {
  @Sse('stream/:sessionId')
  @UseGuards(JwtAuthGuard, RegisteredUserGuard, TrialGuard)
  async streamResponse(
    @Param('sessionId') sessionId: string,
    @CurrentUser() user: User,
  ): Observable<MessageEvent> {
    return this.claudeService.streamChatResponse(sessionId, user.id);
  }
}
```

**Client-Side EventSource**:

```typescript
const eventSource = new EventSource(`/api/chat/stream/${sessionId}?token=${streamToken}`);

eventSource.addEventListener('content_block_delta', (event) => {
  const data = JSON.parse(event.data);
  appendToUI(data.delta.text);
});

eventSource.addEventListener('message_stop', (event) => {
  eventSource.close();
  markComplete();
});

eventSource.onerror = (error) => {
  console.error('Stream error:', error);
  eventSource.close();
};
```

#### SSE Authentication Pattern for Chat

**Challenge**: EventSource API cannot set custom headers (no `Authorization: Bearer token`).

**Solution**: Short-lived scoped JWT in query parameter

```typescript
// Step 1: Client gets stream token via authenticated POST
@Post('stream/init')
@UseGuards(JwtAuthGuard, RegisteredUserGuard, TrialGuard)
initStream(@CurrentUser() user: User) {
  const streamToken = this.jwtService.sign(
    { sub: user.id, type: 'sse', sessionId: uuid() },
    { expiresIn: '5m' }, // Short-lived
  );
  return { streamToken };
}

// Step 2: SSE endpoint validates token manually
@Sse('stream/:sessionId')
async stream(@Query('token') token: string, @Param('sessionId') sessionId: string) {
  const decoded = this.jwtService.verify(token);

  if (decoded.type !== 'sse') {
    throw new UnauthorizedException('Invalid token type');
  }

  if (decoded.sessionId !== sessionId) {
    throw new UnauthorizedException('Token/session mismatch');
  }

  // Stream response
  return this.claudeService.stream(sessionId, decoded.sub);
}
```

**Security Rules**:
- Token must have scoped `type` field (prevents use as general auth)
- Short TTL (5 minutes max)
- Manual validation in SSE handler (no NestJS guards)
- Bind token to specific session ID

#### Token Tracking and Cost Optimization

**Pattern**: Track input/output tokens for all LLM calls

```typescript
interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  modelUsed: string;
  cost: number; // Calculate based on model pricing
}

// Save to database per user/session
await this.prisma.chatSession.update({
  where: { id: sessionId },
  data: {
    totalInputTokens: { increment: usage.inputTokens },
    totalOutputTokens: { increment: usage.outputTokens },
    estimatedCost: { increment: usage.cost },
  },
});
```

**Use Cases**:
- Cost analysis per user
- Detect abuse (excessive token usage)
- Optimize prompts (reduce input tokens)
- Model selection (cost vs. quality tradeoffs)

#### Structured Output Validation

**Pattern**: Always validate Claude responses with Zod schemas to handle hallucinations

```typescript
import { z } from 'zod';

const TranslationSchema = z.object({
  decoded: z.string(),
  tone: z.enum(['affectionate', 'concerned', 'frustrated', 'neutral']),
  confidence: z.number().min(0).max(1),
  explanation: z.string(),
});

const response = await this.claudeService.translate(message);

const result = TranslationSchema.safeParse(JSON.parse(response));

if (!result.success) {
  throw new Error(`LLM validation failed: ${result.error.message}`);
}

return result.data;
```

**Why Validation Matters**:
- LLMs can hallucinate or output malformed JSON
- Zod provides type safety + runtime validation
- Fail fast with clear error messages

#### Retry Logic with Exponential Backoff

**Pattern**: Retry Claude API calls with exponential backoff

```typescript
async function callClaudeWithRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 500,
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      // Retry on: rate limits (429), server errors (5xx), network errors
      if (error.status === 429 || error.status >= 500 || error.code === 'NETWORK_ERROR') {
        if (attempt < maxRetries) {
          const delay = baseDelay * Math.pow(2, attempt); // 500ms, 1s, 2s
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }
      }

      // No retry on: client errors (400, 401, 403)
      throw error;
    }
  }
}
```

**Important**: Streaming does not retry (partial content already sent)

## 5. SaaS Freemium Architecture Patterns

### 5.1 Feature Gating Architecture

#### FeatureGate Component Pattern

**Problem**: Avoid scattering billing checks throughout codebase (`if (user.plan === 'pro')` everywhere).

**Solution**: Centralized FeatureGate component

```typescript
// Backend: FeatureGate decorator
function RequireFeature(feature: Feature) {
  return applyDecorators(
    UseGuards(JwtAuthGuard, RegisteredUserGuard, FeatureGuard),
    SetMetadata('feature', feature),
  );
}

@Get('memories')
@RequireFeature(Feature.DEEP_DIVE)
async getMemories(@CurrentUser() user: User) {
  // Only accessible to users with Deep Dive feature
}

// Frontend: <FeatureGate> component
<FeatureGate feature="deep-dive" fallback={<UpgradePrompt />}>
  <ChatInterface />
</FeatureGate>
```

**Benefits**:
- Single source of truth for feature access
- Easy to update billing logic (change one place)
- Clear UI feedback (fallback component)

#### Progressive Feature Gating Strategies

1. **Usage-Based Gating** (the project pattern):
   - Free: 5 translations → soft registration popup
   - Anonymous Deep Dive: 5 messages → hard paywall
   - Registered: Full Deep Dive for 72h trial

2. **Status/Progress Gating**:
   - Unlock advanced features after onboarding milestones
   - Reward engagement

3. **Team/Permission Gating**:
   - Free for individual use
   - Payment required for teams/multiple users

4. **Progressive Disclosure**:
   - Gradually reveal premium features
   - Show "locked" features to create FOMO

**the project Implementation**:

```typescript
// Guard ordering matters!
@Controller('chat')
export class ChatController {
  // Free translator: No guards (anonymous OK)
  @Post('translate')
  async translate(@Body() dto: TranslateDto) {
    // Check translation count in session/IP
    // Show registration popup after 5 translations
  }

  // Deep Dive: Requires authentication + trial check
  @Post('deep-dive')
  @UseGuards(JwtAuthGuard, RegisteredUserGuard, TrialGuard)
  async deepDive(@CurrentUser() user: User, @Body() dto: ChatDto) {
    // Full access during trial
    // Blocks after trial expiration
  }

  // DELETE always allowed (no TrialGuard)
  @Delete(':id')
  @UseGuards(JwtAuthGuard)
  async deleteChat(@CurrentUser() user: User, @Param('id') id: string) {
    // Users can delete their data even after trial expires
  }
}
```

### 5.2 Trial and Subscription Architecture

#### Reverse Trial Pattern

**Definition**: Users experience full version for limited time, then auto-downgrade to freemium if they don't upgrade.

**Benefits**:
- Higher conversion than traditional trial (7-21% vs 8-25%)
- Lower friction (no credit card upfront)
- Users experience value before committing

**the project Application**:
1. Anonymous user tries translator (free forever)
2. Clicks "Try Deep Dive" CTA → 5 anonymous messages
3. Hits paywall → registers
4. Gets 72-hour full Deep Dive trial
5. After 72h → downgrades to translator-only (freemium)
6. Can upgrade to paid subscription anytime

**State Machine**:

```
[Anonymous] ──translate──> [Anonymous + 5 translations used]
                                 │
                          try Deep Dive
                                 │
                                 ▼
                    [Anonymous Deep Dive (5 messages)]
                                 │
                           hits paywall
                                 │
                                 ▼
                          [Registration]
                                 │
                                 ▼
                      [Active Trial (72h full access)]
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              trial expires              subscribes
                    │                         │
                    ▼                         ▼
            [Freemium: Translator]    [Paid: Full Access]
```

#### Trial Guard Pattern

**Implementation**:

```typescript
@Injectable()
export class TrialGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const user = request.user;

    // Allow if user has active subscription
    if (user.subscription?.status === 'active') {
      return true;
    }

    // Allow if user is in trial period
    if (user.trialEndsAt && new Date() < user.trialEndsAt) {
      return true;
    }

    // Block: Trial expired, no subscription
    throw new ForbiddenException({
      statusCode: 403,
      error: 'TRIAL_EXPIRED',
      message: 'Your trial has expired. Please subscribe to continue.',
    });
  }
}
```

**Frontend Handling**:

```typescript
// Intercept 403 TRIAL_EXPIRED errors
if (error.response?.error === 'TRIAL_EXPIRED') {
  router.push('/upgrade');
}
```

#### Paddle Webhook Architecture

**Pattern**: Event-driven subscription state updates

```typescript
@Controller('webhooks')
export class WebhooksController {
  @Post('paddle')
  async handlePaddleWebhook(@Body() payload: any, @Req() req: Request) {
    // 1. Verify webhook signature
    const isValid = this.paddleService.verifySignature(req.headers, payload);
    if (!isValid) throw new UnauthorizedException();

    // 2. Idempotency check (prevent duplicate processing)
    const processed = await this.prisma.processedWebhook.findUnique({
      where: { eventId: payload.event_id },
    });
    if (processed) return { received: true };

    // 3. Process event
    switch (payload.event_type) {
      case 'subscription.created':
        await this.subscriptionService.activate(payload.data);
        break;
      case 'subscription.canceled':
        await this.subscriptionService.cancel(payload.data);
        break;
      case 'subscription.updated':
        await this.subscriptionService.update(payload.data);
        break;
    }

    // 4. Mark as processed
    await this.prisma.processedWebhook.create({
      data: { eventId: payload.event_id, processedAt: new Date() },
    });

    return { received: true };
  }
}
```

**Key Patterns**:
- **Idempotency**: Track processed webhook IDs to prevent duplicate execution
- **Signature Verification**: Validate webhook authenticity
- **Event-Driven**: Update database state, emit internal events
- **Error Handling**: Return 200 even on partial failure (Paddle will retry on non-200)

### 5.3 Anonymous-First JWT Architecture

**Pattern**: Use JWT tokens for all users (anonymous + registered)

**Benefits**:
- Consistent authentication model
- Rate limiting per user (even anonymous)
- Session continuity (anonymous → registered)
- Easier to implement GDPR (delete anonymous data after N days)

**Implementation**:

```typescript
// Anonymous user gets JWT on first visit
@Post('anonymous/create')
async createAnonymousSession() {
  const anonymousId = uuid();
  const token = this.jwtService.sign({
    sub: anonymousId,
    isAnonymous: true,
  });

  return { token, anonymousId };
}

// Registration upgrades anonymous session
@Post('auth/register')
async register(@Body() dto: RegisterDto, @CurrentUser() anonymousUser: User) {
  // Create registered user
  const user = await this.prisma.user.create({
    data: {
      email: dto.email,
      passwordHash: await bcrypt.hash(dto.password, 12),
      trialEndsAt: addDays(new Date(), 3), // 72h trial
    },
  });

  // Migrate anonymous data (translations, sessions)
  if (anonymousUser?.isAnonymous) {
    await this.migrateAnonymousData(anonymousUser.id, user.id);
  }

  // Return registered user token
  return {
    accessToken: this.jwtService.sign({ sub: user.id }),
    refreshToken: this.jwtService.sign({ sub: user.id, jti: uuid() }, { expiresIn: '7d' }),
  };
}
```

## 6. Real-Time Streaming Architecture

### 6.1 SSE vs WebSocket Decision Framework

| Aspect | SSE | WebSockets |
|--------|-----|-----------|
| **Direction** | Unidirectional (server→client) | Bidirectional |
| **Protocol** | HTTP-based | Separate protocol (WS://) |
| **Complexity** | Low (standard HTTP) | Moderate (handshake, protocol) |
| **Latency** | Acceptable for most apps | Ultra-low latency |
| **Scaling** | Standard load balancing | Requires sticky sessions + Redis |
| **Browser Support** | Universal (EventSource API) | Universal (WebSocket API) |
| **Reconnection** | Automatic (built-in) | Manual (must implement) |
| **Binary Data** | Text only (Base64 for binary) | Supported natively |
| **Firewall/Proxy** | Better (standard HTTP) | May be blocked |

### 6.2 When to Choose Each

**Choose SSE When**:
- **Unidirectional updates**: Server pushing to client (LLM streaming, notifications, live feeds)
- **Simpler infrastructure**: Want to leverage existing HTTP setup
- **Rapid development**: Need to ship quickly
- **Good enough latency**: 95% of use cases (<500ms acceptable)

**Choose WebSockets When**:
- **Bidirectional required**: Real-time collaboration, gaming, voice/video
- **Ultra-low latency needed**: Every millisecond matters
- **Binary data**: Large binary payloads (images, audio)

**LinkedIn Example**: Uses SSE for chat (unidirectional message delivery) + regular HTTP POST for sending messages. This hybrid approach works well.

### 6.3 SSE Scaling Patterns

**Challenge**: SSE connections are long-lived, holding server connections open.

**Solutions**:

1. **Horizontal Scaling with Sticky Sessions**:

```nginx
# nginx config
upstream backend {
  ip_hash; # Sticky sessions (same client → same server)
  server backend1:3000;
  server backend2:3000;
}
```

2. **Redis Pub/Sub for Multi-Instance**:

```typescript
// Server A receives message, publishes to Redis
await redis.publish(`chat:${sessionId}`, JSON.stringify(message));

// All servers subscribe to Redis
redis.subscribe(`chat:${sessionId}`, (message) => {
  // Forward to connected SSE clients
  sseClients.get(sessionId)?.send(message);
});
```

3. **Serverless with Edge Functions**:
- Deploy SSE endpoints to edge (Vercel Edge Functions, Cloudflare Workers)
- Automatically scales per request
- Lower latency (geographically distributed)

**the project Recommendation**: Start with single-instance (simpler). Add Redis pub/sub when scaling beyond 1,000 concurrent SSE connections.

## 7. Recommended Documentation Workflow for the project

### 7.1 Documentation Phases

**Phase 1: MVP (Current State)**
- ✅ C4 Level 1: System Context (done in architecture/overview.md)
- ✅ C4 Level 2: Container Diagram (done in architecture/overview.md)
- ✅ ADRs: Key decisions (see architecture/decisions/)
- ⚠️ TODO: Sequence diagrams (anonymous flow, deep dive flow, webhook flow)
- ⚠️ TODO: State diagram (trial lifecycle)

**Phase 2: Pre-Launch**
- C4 Level 3: Component Diagrams (per module: auth, translator, chat, billing)
- API documentation (OpenAPI spec)
- Deployment runbook
- Incident response runbook

**Phase 3: Post-Launch**
- Performance monitoring dashboard
- Cost tracking per user
- Quality metrics (uptime, latency, token usage)
- User feedback integration

### 7.2 Documentation Tools

**Diagramming**:
- **Mermaid**: Markdown-native, GitHub-rendered, version-controlled
- **PlantUML**: Text-based UML, generates PNGs/SVGs
- **Excalidraw**: Visual, exports to SVG

**Schema Validation**:
- **Zod**: Runtime validation + TypeScript types
- **OpenAPI**: REST API specification
- **AsyncAPI**: Event-driven API specification

**Documentation Hosting**:
- **GitHub**: Markdown files in `architecture/` and `docs/`
- **Notion**: Internal team documentation
- **Mintlify/GitBook**: Public-facing docs (post-launch)

### 7.3 Recommended File Structure

```
architecture/
├── overview.md                    # System overview (C4 Level 1 & 2)
├── diagrams/
│   ├── context.mmd               # Mermaid: System context
│   ├── containers.mmd            # Mermaid: Container diagram
│   ├── sequences/
│   │   ├── anonymous-flow.mmd
│   │   ├── deep-dive-flow.mmd
│   │   └── webhook-flow.mmd
│   └── state-machines/
│       └── trial-lifecycle.mmd
├── decisions/                     # MADR ADRs
│   ├── 0001-anonymous-jwt.md
│   ├── 0002-sse-over-websocket.md
│   ├── 0003-trial-guard.md
│   ├── 0004-paddle-payments.md
│   └── 0005-monorepo.md
├── contracts/                     # API contracts
│   ├── rest-api.yaml             # OpenAPI spec
│   ├── sse-events.yaml           # AsyncAPI spec
│   └── paddle-webhooks.md        # Webhook documentation
└── runbooks/
    ├── deployment.md
    ├── incident-response.md
    └── cost-monitoring.md
```

## 8. Key Takeaways for the project

### 8.1 Documentation Strategy

1. **Use C4 + ADR + Selective arc42**:
   - C4 diagrams for visual clarity
   - ADRs (MADR format) for decisions
   - arc42 sections 1-6, 8-9 (skip heavyweight sections)

2. **Keep docs in Git**:
   - Markdown files in `architecture/` and `docs/`
   - Review docs in PRs
   - Version alongside code

3. **Automate where possible**:
   - Mermaid diagrams (text → rendered)
   - OpenAPI from NestJS decorators
   - TypeScript types from Zod schemas

### 8.2 Architecture Patterns

1. **Anonymous-First JWT**: All users get JWT (anonymous + registered)
2. **SSE for LLM Streaming**: Simpler than WebSockets, good enough for unidirectional
3. **FeatureGate Pattern**: Centralized billing checks, not scattered
4. **Reverse Trial**: Full access → freemium downgrade (higher conversion)
5. **Cost-Tiered Models**: Opus for complex, Sonnet for standard, Haiku for simple

### 8.3 System Design Document Priority

**Essential Sections** (do first):
1. Introduction (product overview, goals, stakeholders)
2. Constraints (technical, organizational)
3. System Context (C4 Level 1)
4. Solution Strategy (key decisions)
5. Building Block View (C4 Level 2)
6. Runtime View (sequence diagrams for 3 core flows)
7. Crosscutting Concepts (security, sessions, error handling)
8. Architecture Decisions (ADRs)

**Optional Sections** (add later):
9. Deployment View (infrastructure)
10. Quality Requirements (performance targets)
11. Risks and Technical Debt
12. Glossary

### 8.4 Most Important Diagrams

**Priority 1** (MVP):
1. System Context (C4 Level 1) ✅
2. Container Diagram (C4 Level 2) ✅
3. Anonymous Flow (sequence diagram) ⚠️
4. Deep Dive Flow (sequence diagram) ⚠️
5. Trial Lifecycle (state diagram) ⚠️

**Priority 2** (Pre-Launch):
6. Webhook Flow (sequence diagram)
7. Component Diagrams (auth, translator, chat, billing)
8. Deployment Architecture

## Sources

- [System Design: The Complete Guide 2026](https://www.systemdesignhandbook.com/guides/system-design/)
- [Software Design Document [Tips & Best Practices] | The Workstream](https://www.atlassian.com/work-management/knowledge-sharing/documentation/software-design-document)
- [The Template I used for Over 100 System Design Document | by araldhafeeri | Medium](https://medium.com/@ar.aldhafeeri11/ive-written-over-100-system-design-papers-as-a-professional-consultant-here-s-the-template-i-3fe7d48ef523)
- [Comparing Software Architecture Documentation Models and When to Use Them - DEV Community](https://dev.to/adityasatrio/comparing-software-architecture-documentation-models-and-when-to-use-them-495n)
- [arc42 Template Overview - arc42](https://arc42.org/overview)
- [GitHub - arc42/arc42-template](https://github.com/arc42/arc42-template)
- [An introduction to arc42 | by Manserpatrice | Nerd For Tech | Medium](https://medium.com/nerd-for-tech/an-introduction-to-arc42-283b559d62cc)
- [Implementing Real-Time Chat with SSE vs WebSockets (and Why I Chose One) - DEV Community](https://dev.to/divyanshulohani/implementing-real-time-chat-with-sse-vs-websockets-and-why-i-chose-one-2mn2)
- [Why Server-Sent Events Beat WebSockets for 95% of Real-Time Cloud Applications | by Anurag singh | CodeToDeploy | Medium](https://medium.com/codetodeploy/why-server-sent-events-beat-websockets-for-95-of-real-time-cloud-applications-830eff5a1d7c)
- [The Complete Guide to Streaming LLM Responses in Web Applications - DEV Community](https://dev.to/hobbada/the-complete-guide-to-streaming-llm-responses-in-web-applications-from-sse-to-real-time-ui-3534)
- [How to Stream LLM Responses Using Server-Sent Events (SSE)](https://apidog.com/blog/stream-llm-responses-using-sse/)
- [Claude Code Internals, Part 7: SSE Stream Processing | by Marco Kotrotsos | Medium](https://kotrotsos.medium.com/claude-code-internals-part-7-sse-stream-processing-c620ae9d64a1)
- [Architecture Patterns for SaaS Platforms: Billing, RBAC, and Onboarding | by Kishan Rank | Medium](https://medium.com/appfoster/architecture-patterns-for-saas-platforms-billing-rbac-and-onboarding-964ea071f571)
- [Feature Gating: How We Built a Freemium SaaS Without Duplicating Components - DEV Community](https://dev.to/aniefon_umanah_ac5f21311c/feature-gating-how-we-built-a-freemium-saas-without-duplicating-components-1lo6)
- [Feature Gating Strategies for Your SaaS Freemium Model to Boost Conversions - Demogo](https://demogo.com/2025/06/25/feature-gating-strategies-for-your-saas-freemium-model-to-boost-conversions/)
- [Reverse Trial Method: How to Increase SaaS Conversions (+ Examples)](https://userpilot.com/blog/saas-reverse-trial/)
- [Top 8 LLM Frameworks for Building AI Agents in 2026 | Second Talent](https://www.secondtalent.com/resources/top-llm-frameworks-for-building-ai-agents/)
- [7 Agentic AI Trends to Watch in 2026 - MachineLearningMastery.com](https://machinelearningmastery.com/7-agentic-ai-trends-to-watch-in-2026/)
- [Top LLMs and AI Trends for 2026 | Clarifai Industry Guide](https://www.clarifai.com/blog/llms-and-ai-trends)
