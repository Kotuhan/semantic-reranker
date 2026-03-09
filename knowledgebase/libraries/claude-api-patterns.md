---
title: Claude API Multi-Agent Pipeline and LLM Integration Patterns
domain: library
tech: [typescript, nodejs, nestjs, anthropic, ai, zod]
area: [ai, multi-agent, structured-output, orchestration, llm-integration]
staleness: 3months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://platform.claude.com/docs/en/build-with-claude/structured-outputs
  - https://www.anthropic.com/engineering/multi-agent-research-system
  - https://platform.claude.com/docs/en/api/rate-limits
  - https://www.anthropic.com/engineering/advanced-tool-use
  - https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk
  - https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms
  - https://dev.to/heuperman/how-to-get-consistent-structured-output-from-claude-20o5
  - https://www.aifreeapi.com/en/posts/fix-claude-api-429-rate-limit-error
  - https://amitkoth.com/claude-api-rate-limits-enterprise/
  - https://codesignal.com/learn/courses/parallelizing-claude-agentic-systems-in-python/lessons/concurrent-agent-conversations
---

# Claude API Multi-Agent Pipeline and LLM Integration Patterns

## Overview

This research evaluates Claude API integration patterns for multi-agent systems, with specific focus on structured output validation, orchestration strategies, error handling, and cost optimization. Based on Anthropic's official documentation and real-world implementations as of January 2026.

**Key Finding**: The project's sequential pipeline pattern (Her Psychologist → His Interpreter → Bridge) with Zod validation is a solid foundation, but can be optimized with native structured outputs (GA in 2026), prompt caching, and selective parallelization.

## 1. Structured Output Patterns

### Native Structured Outputs (Recommended - GA 2026)

Anthropic's **Structured Outputs** feature is now generally available for Claude Sonnet 4.5, Opus 4.5, and Haiku 4.5. This is the **recommended approach** over manual JSON parsing.

**Two Modes:**

1. **JSON Outputs** (`output_config.format`): Controls Claude's response format
2. **Strict Tool Use** (`strict: true`): Guarantees schema validation on tool inputs

**Key Benefits:**
- **Always valid**: No more `JSON.parse()` errors due to constrained decoding
- **Type safe**: Guaranteed field types and required fields
- **No retries**: Eliminates retry logic for schema violations
- **SDK integration**: Works with Zod (TypeScript) and Pydantic (Python)

**Implementation:**

```typescript
import Anthropic from '@anthropic-ai/sdk';
import { z } from 'zod';
import { zodOutputFormat } from '@anthropic-ai/sdk/helpers/zod';

const OutputSchema = z.object({
  translation: z.string(),
  tip: z.string(),
});

const response = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 1024,
  messages: [{ role: "user", content: "..." }],
  output_config: { format: zodOutputFormat(OutputSchema) },
});

// Guaranteed valid JSON in response.content[0].text
const result = JSON.parse(response.content[0].text);
```

**When to Use:**
- Data extraction tasks (emails, invoices, documents)
- API response formatting
- Multi-agent systems requiring reliable handoffs
- **Should be default for all production LLM applications**

### The Project's Current Pattern (Manual JSON Parsing)

The project currently uses **manual JSON extraction with Zod validation**:

```typescript
// Current pattern in the project's BaseAgent.parseOutput()
const jsonMatch = content.match(/\{[\s\S]*\}/);
const parsed = JSON.parse(jsonMatch[0]);
const result = this.outputSchema.safeParse(parsed);
```

**Issues with Current Approach:**
- Relies on regex to extract JSON from freeform text
- Claude may add preambles or explanations before JSON
- Risk of parsing errors if Claude's output format changes
- Requires retry logic if validation fails

**Migration Path:**
1. Add `output_config.format` with `zodOutputFormat()` helper
2. Remove manual JSON regex extraction
3. Keep Zod schemas (reuse with SDK helper)
4. Simplify error handling (no more retry for schema violations)

### Performance Considerations

**Grammar Compilation and Caching:**
- First request with a new schema has additional latency (grammar compilation)
- Compiled grammars are **cached for 24 hours** from last use
- Cache invalidation: only when schema structure changes (not `name`/`description`)
- Slight increase in input tokens (system prompt injection)

**Limitations:**
- **Refusals** (`stop_reason: "refusal"`): Output may not match schema if Claude refuses for safety
- **Token limits** (`stop_reason: "max_tokens"`): Incomplete output if cut off
- **JSON Schema constraints**: Some features not supported (see Schema Limitations section)

## 2. Multi-Agent Orchestration Patterns

### Anthropic's Official Recommendation: Orchestrator-Worker Pattern

Anthropic's research system uses an **orchestrator-worker pattern** where a lead agent coordinates specialized subagents operating in parallel.

**Architecture:**
```
Lead Agent (Orchestrator)
    │
    ├─> Subagent 1 (parallel)
    ├─> Subagent 2 (parallel)
    └─> Subagent 3 (parallel)
    │
    └─> Synthesize results
```

**Key Performance Gains:**
1. **Lead agent parallelization**: Spin up 3-5 subagents in parallel (not sequentially)
2. **Tool parallelization**: Subagents use 3+ tools concurrently
3. **Result**: Cut research time by **up to 90%** for complex queries

### Sequential vs Parallel Execution

**Sequential (the project Current):**
- Agents execute one-by-one: Psychologist → Interpreter → Bridge
- Each agent waits for previous agent's output
- Simple to implement and debug
- **Best for**: Tasks requiring tight context sharing, dependent steps

**Parallel:**
- Independent agents execute simultaneously
- Async/await with `Promise.all()` or `AsyncAnthropic` client
- **80% of performance variance** explained by token usage (more capacity = more parallelization)
- **Best for**: Tasks with heavy parallelization, information exceeding single context windows

**the project Analysis:**
- **Translation pipeline**: Sequential is CORRECT (each agent depends on previous output)
- **Deep Dive pipeline**: Her Psychologist + His Psychologist can run in **parallel** (independent analysis)

**Optimization Opportunity:**

```typescript
// Current Deep Dive (sequential)
const herAnalysis = await herPsychologist.invoke(input);
const hisAnalysis = await hisPsychologist.invoke(input);

// Optimized Deep Dive (parallel)
const [herAnalysis, hisAnalysis] = await Promise.all([
  herPsychologist.invoke(input),
  hisPsychologist.invoke(input),
]);
```

### Context Management

**For Extended Operations:**
- Summarize completed work phases before proceeding
- Store essential information in external memory (database, Redis)
- Spawn fresh subagents with clean contexts
- Retrieve stored context to prevent token limit overflow
- **the project already implements this**: Memory table stores relationship context

**Token Efficiency:**
- Multi-agent systems use **~15× more tokens** than single chats
- Best suited for tasks with sufficient value to justify costs
- Avoid for domains requiring shared context (most coding tasks)

## 3. Zod Validation Best Practices

### Current the project Pattern (Good Foundation)

```typescript
export const BridgeOutputSchema = z.object({
  translation: z.string().min(1),
  tip: z.string().min(1),
});
export type BridgeOutput = z.infer<typeof BridgeOutputSchema>;
```

**Strengths:**
- Type safety from API response to application logic
- `safeParse()` prevents runtime errors
- Schema inference with `z.infer`

### Migration to Native Structured Outputs

**With SDK Helper (Recommended):**

```typescript
import { zodOutputFormat } from '@anthropic-ai/sdk/helpers/zod';

const response = await client.messages.create({
  model: "claude-sonnet-4-5",
  output_config: { format: zodOutputFormat(BridgeOutputSchema) },
  messages: [...]
});

// SDK automatically transforms schema and validates response
const result = JSON.parse(response.content[0].text);
// result is guaranteed to match BridgeOutputSchema
```

**SDK Transformation (Automatic):**
1. Removes unsupported constraints (`minLength`, `maxLength`, `minimum`, `maximum`)
2. Updates descriptions with constraint info ("Must be at least 100")
3. Adds `additionalProperties: false` to all objects
4. Filters string formats to supported list
5. **Still validates** against original schema with all constraints

**Best Practices:**
- Use `safeParse()` for resilience (even with structured outputs)
- Custom refinements for complex validation
- Schema reuse across agents
- **Keep existing Zod schemas** - they work with SDK helpers

## 4. Prompt Engineering for Structured Output

### Anthropic's Recommendations

**When NOT Using Structured Outputs:**
1. **Use Structured Formats**: JSON or other structured formats in prompts
2. **Provide Examples**: More examples = better consistency
3. **Prefilling**: Start response with `{` to skip preambles
4. **Be Explicit**: Claude 4.x responds well to clear instructions

**When Using Structured Outputs:**
- **Use structured outputs instead** - it's more reliable than prompt engineering
- Prompting is no longer needed for format consistency

**the project Current Approach:**
- Prompts already instruct JSON output: "Respond with a JSON object containing..."
- **Can simplify prompts** after migrating to structured outputs (format is guaranteed)

## 5. Token Usage Optimization and Cost Management

### Key Strategies (2026)

#### 1. Prompt Caching (Highest Impact)

**Savings**: 90% cost reduction on repeated content after 2 requests

**How It Works:**
- Cache read tokens: **0.1× base input token price**
- Cache durations: 5 minutes (default) or 1 hour
- Only **uncached input tokens** count toward ITPM rate limits

**the project Opportunity:**
```typescript
// Cache system prompts (static across requests)
const response = await client.messages.create({
  model: "claude-sonnet-4-5",
  system: [
    {
      type: "text",
      text: buildSystemPrompt(context), // This can be cached
      cache_control: { type: "ephemeral" }
    }
  ],
  messages: [...]
});
```

**What to Cache:**
- System instructions and prompts (agent role definitions)
- Large context documents (profile information)
- Tool definitions
- Conversation history (for chat sessions)

**Impact Calculation:**
- 80% cache hit rate + 2M ITPM limit = **10M effective tokens/min**
- Combined optimizations can reduce costs by **95%+**

#### 2. Model Selection

**2026 Pricing:**
- Claude Haiku 4.5: $1 input / $5 output per MTok (fastest)
- Claude Sonnet 4.5: $3 input / $15 output per MTok (balanced)
- Claude Opus 4.5: $5 input / $25 output per MTok (most capable)

**Rule:** Don't use Opus when Sonnet suffices. Don't use Sonnet when Haiku works.

**the project Current:** Uses Sonnet 4 (configurable via `CLAUDE_MODEL`)
- **Analysis**: Appropriate for relationship advice (requires nuance)
- **Opportunity**: Use Haiku for simpler agents (e.g., validation, classification)

#### 3. Batch Processing

**Savings**: 50% discount on both input and output tokens

**When to Use:**
- Non-urgent workloads
- Bulk translation processing
- Overnight analysis jobs

**the project Application:** Not applicable (real-time translation required)

#### 4. Output Token Optimization

```typescript
// Current: Uses 1024 max_tokens
maxTokens: AGENTS_CONFIG.maxResponseTokens // 1024

// Optimization: Set to expected response length
maxTokens: 300 // Bridge agent typically produces 200-250 tokens
```

**Benefits:**
- Better rate limiter predictions
- Reduced OTPM usage
- Faster `stop_reason: "max_tokens"` detection

#### 5. Long Context Pricing Awareness

- Standard: $3/MTok for ≤200K tokens
- Premium: Higher rate for >200K tokens (all tokens)
- **the project**: Not relevant (small contexts)

### Cost Tracking

**the project Already Implements:**
```typescript
interface PipelineResult {
  totalInputTokens: number;
  totalOutputTokens: number;
  modelUsed: string;
  latencyMs: number;
}
```

**Enhancement Opportunities:**
- Track cache hit rates (new field: `cacheReadTokens`)
- Per-agent cost breakdown
- Monthly cost projections
- Alert thresholds

## 6. Error Handling and Retry Strategies

### Rate Limiting (429 Errors)

**Anthropic's Token Bucket Algorithm:**
- Capacity continuously replenished up to maximum limit
- No fixed interval resets
- **Short bursts** can trigger rate limits (60 RPM = 1 req/sec enforcement)

**Response Headers:**
```
retry-after: 5
anthropic-ratelimit-requests-remaining: 0
anthropic-ratelimit-tokens-remaining: 0
anthropic-ratelimit-requests-reset: 2026-01-29T12:34:56Z
```

**the project Current Implementation (Good):**

```typescript
// Retries on: 429, 5xx, network errors
// No retry on: 400, 401, 403
private isNonRetryableError(error: unknown): boolean {
  if (error instanceof Anthropic.APIError) {
    const status = error.status;
    if (status === 429 || status >= 500) {
      return false; // Retryable
    }
    return true; // Not retryable
  }
  return false; // Network errors are retryable
}
```

**Exponential Backoff (the project Current):**
```typescript
const delay = Math.min(
  AGENTS_CONFIG.retryBaseDelay * Math.pow(2, attempt - 1), // 500ms → 1s → 2s
  AGENTS_CONFIG.retryMaxDelay, // Max 5s
);
```

**Enhancement Opportunity:**

```typescript
// Use retry-after header when available
if (error.response?.headers?.['retry-after']) {
  const retryAfter = parseInt(error.response.headers['retry-after']) * 1000;
  delay = retryAfter; // Server-provided timing
} else {
  delay = Math.min(...); // Fallback to exponential backoff
}
```

### Rate Limit Optimization

**Cache-Aware ITPM (Key Advantage):**
- Only **uncached input tokens** count toward ITPM for most models
- `cache_read_input_tokens` do NOT count toward rate limits
- This makes rate limits **effectively higher** with caching

**the project Tier Estimates:**
- Tier 1 (30K ITPM): ~1,000 translations/hour (without caching)
- Tier 2 (450K ITPM): ~15,000 translations/hour
- **With 80% cache hit rate**: 5× effective throughput

### Other Error Patterns

**Refusals (`stop_reason: "refusal"`):**
- Claude maintains safety properties even with structured outputs
- Output may not match schema (refusal message takes precedence)
- **the project**: Unlikely for translation tasks, but handle gracefully

**Token Limit (`stop_reason: "max_tokens"`):**
- Response cut off before completion
- Retry with higher `max_tokens`

**Timeout Handling (the project Current: 15s per agent):**
- Appropriate for translation tasks
- Total pipeline timeout: 45s (good for UX)

## 7. JSON Schema Limitations (Structured Outputs)

### Supported Features

- All basic types: object, array, string, integer, number, boolean, null
- `enum` (strings, numbers, bools, nulls only)
- `const`, `anyOf`, `allOf` (with limitations)
- `$ref`, `$def`, `definitions` (no external `$ref`)
- `default` property
- `required` and `additionalProperties: false` (mandatory for objects)
- String formats: `date-time`, `time`, `date`, `duration`, `email`, `hostname`, `uri`, `ipv4`, `ipv6`, `uuid`
- Array `minItems` (only 0 and 1 supported)

### Not Supported

- Recursive schemas
- Complex types within enums
- External `$ref` (e.g., `http://...`)
- Numerical constraints (`minimum`, `maximum`, `multipleOf`)
- String constraints (`minLength`, `maxLength`)
- Array constraints beyond `minItems: 0 or 1`
- `additionalProperties` set to anything other than `false`

**SDK Workaround:**
- SDK automatically removes unsupported constraints
- Adds constraint info to descriptions
- Still validates against original schema with all constraints

**the project Schemas (Compatible):**
```typescript
// Simple schemas with .min(1) - SDK will transform
z.string().min(1) // → description: "Must be at least 1 character"
z.string().email() // → format: "email" (supported)
```

## 8. Comparison: the project Pattern vs Best Practices

### What the project Does Well

✅ **Zod Validation**: Type-safe schema validation at every agent boundary
✅ **Retry Logic**: Exponential backoff on retryable errors
✅ **Token Tracking**: Comprehensive token usage across pipeline
✅ **Timeout Handling**: Per-agent and pipeline-level timeouts
✅ **Error Classification**: Distinguishes retryable vs non-retryable errors
✅ **Sequential Pipeline**: Correct for translation (dependent steps)
✅ **Abstract Base Class**: DRY principle for agent implementation

### Optimization Opportunities

🔄 **Structured Outputs**: Migrate from manual JSON parsing to native `output_config.format`
🔄 **Prompt Caching**: Cache static system prompts (90% cost reduction)
🔄 **Parallel Execution**: Run Her Psychologist + His Psychologist in parallel (Deep Dive)
🔄 **Retry-After Header**: Use server-provided timing for 429 retries
🔄 **Dynamic max_tokens**: Set per-agent instead of global 1024
🔄 **Cache Tracking**: Monitor `cache_read_input_tokens` for optimization
🔄 **Model Selection**: Consider Haiku for simpler agents

### When NOT to Change

❌ **Sequential Translation Pipeline**: Keep as-is (correct pattern for dependent steps)
❌ **3 Retries**: Reasonable default (matches Anthropic recommendations)
❌ **15s Agent Timeout**: Appropriate for complex reasoning
❌ **Sonnet Model**: Appropriate for nuanced relationship advice

## 9. Recommended Implementation Priorities

### Phase 1: Structured Outputs (High Impact, Low Risk)

**Goal**: Eliminate JSON parsing errors, reduce retry logic complexity

**Changes:**
1. Add `output_config` with `zodOutputFormat()` to all agent calls
2. Remove manual JSON regex extraction from `BaseAgent.parseOutput()`
3. Simplify error handling (no retries for schema violations)
4. Keep existing Zod schemas (reuse with SDK helper)

**Estimated Effort**: 2-4 hours
**Impact**: Reliability improvement, fewer errors in production

### Phase 2: Prompt Caching (High Impact, Medium Risk)

**Goal**: 90% cost reduction on repeated content

**Changes:**
1. Add `cache_control` to system prompts in each agent
2. Track `cache_read_input_tokens` in token usage
3. Monitor cache hit rates via API response headers
4. Tune cache breakpoints for optimal performance

**Estimated Effort**: 4-6 hours
**Impact**: Significant cost reduction, higher effective rate limits

### Phase 3: Deep Dive Parallelization (Medium Impact, Medium Risk)

**Goal**: Reduce Deep Dive latency by 30-50%

**Changes:**
1. Refactor Deep Dive pipeline to use `Promise.all()` for psychologists
2. Test with production load (ensure rate limits not exceeded)
3. Monitor token usage (parallel = more concurrent requests)

**Estimated Effort**: 3-5 hours
**Impact**: Better user experience for Deep Dive feature

### Phase 4: Rate Limit Enhancements (Low Impact, Low Risk)

**Goal**: Better handling of rate limit errors

**Changes:**
1. Parse `retry-after` header in error responses
2. Use server-provided timing instead of exponential backoff
3. Add proactive monitoring of rate limit headers
4. Dashboard for rate limit utilization

**Estimated Effort**: 2-3 hours
**Impact**: Fewer failed requests during peak usage

## 10. Project Integration (the project Specific)

### Module Architecture

**Current Structure (Good):**
```
modules/agents/
├── agents.module.ts
├── config/agents.config.ts
├── schemas/                  # Zod schemas (keep these!)
├── services/
│   ├── claude.service.ts     # Wrapper with retry (enhance)
│   └── pipeline-orchestrator.service.ts # Orchestration (optimize)
├── agents/
│   ├── base.agent.ts         # Abstract base (migrate to structured outputs)
│   └── ...agent.ts           # Concrete agents
└── prompts/                  # Prompt builders (simplify after migration)
```

### Migration Checklist

**ClaudeService:**
- [ ] Add support for `output_config` parameter
- [ ] Add support for `cache_control` in system prompts
- [ ] Parse `retry-after` header from 429 responses
- [ ] Track `cache_read_input_tokens` in result

**BaseAgent:**
- [ ] Update `invoke()` to use `output_config.format`
- [ ] Remove regex-based JSON extraction
- [ ] Keep Zod validation (SDK doesn't validate, only transforms)
- [ ] Add cache control to system prompts

**PipelineOrchestratorService:**
- [ ] Parallelize Her/His Psychologists in Deep Dive pipeline
- [ ] Keep sequential execution for Translation pipeline
- [ ] Track cache hit rates in pipeline results

**Configuration:**
- [ ] Add `enableStructuredOutputs` flag (gradual rollout)
- [ ] Add `enablePromptCaching` flag
- [ ] Per-agent `maxTokens` instead of global default

### Testing Strategy

1. **Unit Tests**: Mock Claude responses with structured output format
2. **Integration Tests**: Test with real API (small batches)
3. **A/B Testing**: Compare old vs new pattern (same prompts)
4. **Monitoring**: Track error rates, latency, token usage, cache hits
5. **Gradual Rollout**: Enable structured outputs per-agent (Bridge first)

## 11. Key Takeaways

### For Architecture Review

1. **the project pipeline pattern is sound**: Sequential for Translation (correct), parallelizable for Deep Dive (opportunity)
2. **Zod validation is best practice**: Keep schemas, enhance with native structured outputs
3. **Retry logic is correct**: Matches Anthropic recommendations (enhance with `retry-after` header)
4. **Cost optimization potential**: Prompt caching can reduce costs by 90%+
5. **Rate limits are manageable**: Tier 1 sufficient for MVP, caching increases effective limits 5-10×

### For Implementation

1. **Prioritize structured outputs**: GA feature, high impact, low risk
2. **Implement prompt caching**: Biggest cost optimization (90% reduction)
3. **Parallelize Deep Dive**: Her/His Psychologists can run concurrently
4. **Monitor token usage**: Add cache hit rate tracking
5. **Keep sequential Translation**: Correct pattern for dependent steps

### For Product/Business

1. **Current implementation is production-ready**: Solid foundation with established patterns
2. **Cost can be reduced significantly**: 90%+ savings with prompt caching
3. **Reliability can be improved**: Structured outputs eliminate parsing errors
4. **Scalability is proven**: Multi-agent pattern used by Anthropic themselves
5. **Rate limits scale naturally**: Tier advancement is automatic, caching increases effective limits

## Sources

- [Structured outputs - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [How we built our multi-agent research system - Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Rate limits - Claude API Docs](https://platform.claude.com/docs/en/api/rate-limits)
- [Advanced tool use - Anthropic Engineering](https://www.anthropic.com/engineering/advanced-tool-use)
- [Building agents with the Claude Agent SDK - Anthropic Engineering](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
- [The guide to structured outputs and function calling with LLMs - Agenta.ai](https://agenta.ai/blog/the-guide-to-structured-outputs-and-function-calling-with-llms)
- [How to get consistent structured output from Claude - DEV Community](https://dev.to/heuperman/how-to-get-consistent-structured-output-from-claude-20o5)
- [How to Fix Claude API 429 Rate Limit Error - AI Free API](https://www.aifreeapi.com/en/posts/fix-claude-api-429-rate-limit-error)
- [Claude API rate limits for enterprise - Amit Kothari](https://amitkoth.com/claude-api-rate-limits-enterprise/)
- [Going Async with Claude Agents - CodeSignal Learn](https://codesignal.com/learn/courses/parallelizing-claude-agentic-systems-in-python/lessons/concurrent-agent-conversations)
