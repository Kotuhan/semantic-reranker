---
title: NestJS Server-Sent Events (SSE) Patterns for AI Response Streaming
domain: pattern
tech: [nestjs, sse, server-sent-events, typescript, rxjs, observable, claude-api, openai]
area: [sse, real-time, streaming, llm-streaming, authentication, scaling]
staleness: 6months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://docs.nestjs.com/techniques/server-sent-events
  - https://medium.com/@kumar.gowtham/nestjs-server-sent-events-sse-and-its-use-cases-9f7316e78fa0
  - https://devkamal.medium.com/real-time-communication-made-simple-building-server-sent-events-sse-with-nestjs-f6a8f5715d18
  - https://iliabedian.com/blog/server-side-events-on-nestjs-emitting-events-to-clients
  - https://medium.com/using-nestjs-sse-for-updating-front-end/backend-implementation-cedd3801c210
  - https://medium.com/@piotrkorowicki/server-sent-events-sse-with-nestjs-and-angular-d90635783d8c
  - https://medium.com/@leonardoacrg.dev/nestjs-a-request-progress-tracker-using-sse-b9f2fded9d70
  - https://github.com/nestjs/nest/issues/12670
  - https://github.com/nestjs/nest/issues/4826
  - https://medium.com/@pranavprakash4777/streaming-ai-responses-with-websockets-sse-and-grpc-which-one-wins-a481cab403d3
  - https://medium.com/@raulblazquezbullon/sse-vs-websockets-in-aws-building-a-serverless-openai-chatbot-with-lambda-22ab29c75405
  - https://procedure.tech/blogs/the-streaming-backbone-of-llms-why-server-sent-events-(sse)-still-wins-in-2025
  - https://blog.theodormarcu.com/p/how-chatgpt-streams-responses-back
  - https://medium.com/@hitesh4296/server-sent-events-breaking-down-how-chatgpt-streams-text-4b1d2d4db4ce
  - https://compute.hivenet.com/post/llm-streaming-sse-websockets
  - https://medium.com/@daniakabani/how-we-used-sse-to-stream-llm-responses-at-scale-fa0d30a6773f
  - https://apidog.com/blog/stream-llm-responses-using-sse/
  - https://community.openai.com/t/assistant-streaming-websockets-vs-sse/738161
  - https://platform.claude.com/docs/en/build-with-claude/streaming
  - https://blog.logrocket.com/nextjs-vercel-ai-sdk-streaming/
  - https://til.simonwillison.net/llms/streaming-llm-apis
  - https://kotrotsos.medium.com/claude-code-internals-part-7-sse-stream-processing-c620ae9d64a1
  - https://ai-sdk.dev/cookbook/api-servers/nest
  - https://eclipse.dev/ditto/httpapi-sse.html
  - https://forums.servicestack.net/t/serverevents-jwt-authentication/4998
  - https://dev.to/debajit13/deep-dive-into-server-sent-events-sse-52
  - https://github.com/whatwg/html/issues/2177
  - https://medium.com/trendyol-tech/delivering-real-time-notifications-to-over-300k-sellers-with-server-sent-events-on-growth-center-95e180c486bc
  - https://www.aklivity.io/post/a-primer-on-server-sent-events-sse
  - https://www.infoq.com/articles/reactive-notification-system-server-sent-events/
  - https://medium.com/walkme-engineering/horizontal-scaling-of-a-stateful-server-with-redis-pub-sub-fc56c875b1aa
  - https://www.oreateai.com/blog/unlocking-redis-pubsubs-potential-scaling-your-messaging-with-sharded-channels/da0bdea4096874c6d1d0469841992982
  - https://developer.mozilla.org/en-US/docs/Web/API/EventSource
  - https://html.spec.whatwg.org/multipage/server-sent-events.html
---

# NestJS Server-Sent Events (SSE) Patterns for AI Response Streaming

## Overview

Server-Sent Events (SSE) is an HTTP-based protocol for unidirectional server-to-client streaming, providing a simpler alternative to WebSockets for use cases where only server-to-client communication is required. This research covers SSE implementation in NestJS for streaming AI responses from LLMs like Claude API, including authentication strategies, scalability patterns, and comparison with WebSocket alternatives.

**Use Case Context**: The project's Deep Dive chat module with multi-agent LLM orchestration streaming responses from Claude API to Next.js frontend.

---

## SSE vs WebSocket for LLM Streaming

### Industry Consensus (2025-2026)

**SSE is the preferred choice for LLM token streaming** according to recent industry analysis. Major platforms including ChatGPT, OpenAI, Claude, and Anthropic use SSE for streaming AI responses.

### Comparison Matrix

| Aspect | SSE | WebSocket |
|--------|-----|-----------|
| **Direction** | Unidirectional (server→client) | Bidirectional (server↔client) |
| **Protocol** | HTTP/1.1 or HTTP/2 | WebSocket protocol (upgrade from HTTP) |
| **Auto-reconnection** | ✅ Built-in (EventSource API) | ❌ Manual implementation required |
| **Authentication** | ⚠️ Limited (query params, cookies, polyfill) | ✅ Custom headers in handshake |
| **Complexity** | ✅ Very simple (standard HTTP) | ⚠️ More complex (persistent connection) |
| **Scaling** | ✅ Stateless servers, standard load balancing | ⚠️ Requires sticky sessions + Redis |
| **Browser support** | ✅ 98%+ (EventSource API) | ✅ 98%+ (WebSocket API) |
| **Latency** | ~5-15ms (HTTP overhead) | ~3-5ms (optimized) |
| **HTTP/2 multiplexing** | ✅ Multiple SSE streams per connection | ❌ Each WebSocket = separate TCP connection |
| **Best for** | LLM streaming, notifications, live feeds | Chat with uploads, real-time collaboration |

### Performance Characteristics

**SSE Advantages for LLM Streaming:**
- Since SSE is just HTTP, horizontal scaling with multiple stateless API servers is straightforward with no need for sticky sessions or socket brokers
- If the connection drops, the browser's EventSource automatically retries
- Easier to implement, debug, and scale when use case is server-only streaming
- Low latency with easiest setup and easy scaling with stateless servers

**When to Use WebSocket Instead:**
- Building interactive agents, chat with file upload, or multi-agent apps that require bi-directional communication
- Real-time two-way interaction (voice systems, collaborative editing)
- Need for custom headers in authentication (though SSE workarounds exist)

### Real-World LLM Implementations

**ChatGPT/OpenAI:**
- Uses Server-Sent Events over HTTP for token streaming
- Event streams supported even in HTTP/1.1
- Format: `content-type: text/event-stream`, blocks separated by `\r\n\r\n`, each with `data: JSON` line

**Claude/Anthropic:**
- Client iterates over text stream using SSE
- Each server-sent event includes named event type + JSON data
- SDK provides `client.messages.stream()` helper with event handlers

**Industry Verdict:**
> "The protocol powering LLM streaming isn't WebSockets or gRPC, but Server-Sent Events (SSE), which is the simplest, most reliable way to deliver real-time LLM outputs."

---

## NestJS SSE Implementation

### Installation

```bash
npm install @nestjs/common rxjs
```

No additional packages required - SSE is supported natively in NestJS via `@Sse()` decorator.

### Basic SSE Endpoint with @Sse Decorator

```typescript
import { Controller, Sse } from '@nestjs/common';
import { Observable, interval } from 'rxjs';
import { map } from 'rxjs/operators';

@Controller('events')
export class EventsController {
  @Sse('sse')
  sse(): Observable<MessageEvent> {
    return interval(1000).pipe(
      map((_) => ({ data: { hello: 'world' } }))
    );
  }
}
```

**Key Points:**
- `@Sse()` decorator marks route as SSE endpoint
- Must return `Observable<MessageEvent>`
- Server sends events to client as observable emits

### Pattern 1: EventEmitter2 Integration (Recommended)

Combine `@Sse()` with EventEmitter2 for event-driven architecture:

```typescript
import { Controller, Sse } from '@nestjs/common';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { Observable, fromEvent } from 'rxjs';
import { map } from 'rxjs/operators';

@Controller('chat')
export class ChatController {
  constructor(private readonly eventEmitter: EventEmitter2) {}

  @Sse('stream/:sessionId')
  streamSession(
    @Param('sessionId') sessionId: string,
  ): Observable<MessageEvent> {
    return fromEvent(this.eventEmitter, `chat.${sessionId}.chunk`).pipe(
      map((payload) => ({ data: JSON.stringify(payload) }))
    );
  }
}
```

**Service emits events:**

```typescript
@Injectable()
export class ChatService {
  constructor(private readonly eventEmitter: EventEmitter2) {}

  async processMessage(sessionId: string, content: string): Promise<void> {
    const stream = await this.claudeService.stream({ messages: [...] });

    for await (const chunk of stream) {
      this.eventEmitter.emit(`chat.${sessionId}.chunk`, { chunk });
    }

    this.eventEmitter.emit(`chat.${sessionId}.complete`, { done: true });
  }
}
```

**Benefits:**
- Decouples SSE endpoint from business logic
- Service can emit events from anywhere
- Multiple SSE endpoints can listen to same events

### Pattern 2: Direct Observable Return (Simple Use Cases)

For straightforward streaming without event emitters:

```typescript
import { Controller, Sse, Param } from '@nestjs/common';
import { Observable } from 'rxjs';

@Controller('ai')
export class AIController {
  constructor(private readonly aiService: AIService) {}

  @Sse('stream/:promptId')
  streamAIResponse(@Param('promptId') promptId: string): Observable<MessageEvent> {
    return this.aiService.streamResponse(promptId);
  }
}
```

```typescript
@Injectable()
export class AIService {
  streamResponse(promptId: string): Observable<MessageEvent> {
    return new Observable((observer) => {
      this.generateResponse(promptId)
        .then(async (stream) => {
          for await (const chunk of stream) {
            observer.next({ data: JSON.stringify({ chunk }) });
          }
          observer.complete();
        })
        .catch((error) => observer.error(error));
    });
  }

  private async generateResponse(promptId: string): Promise<AsyncIterable<string>> {
    // Claude API streaming implementation
    const stream = await this.anthropic.messages.stream({
      model: 'claude-opus-4-5',
      max_tokens: 4096,
      messages: [{ role: 'user', content: 'Hello' }],
    });

    return (async function* () {
      for await (const event of stream) {
        if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
          yield event.delta.text;
        }
      }
    })();
  }
}
```

### Pattern 3: Without @Sse Decorator (Advanced Control)

**Why skip @Sse decorator?**

Due to known issues with `@Sse()` (connection established before handler runs, HttpException doesn't return proper HTTP errors), some implementations use Express Response directly:

```typescript
import { Controller, Get, Res, Param } from '@nestjs/common';
import { Response } from 'express';

@Controller('stream')
export class StreamController {
  constructor(private readonly streamService: StreamService) {}

  @Get('ai/:sessionId')
  async streamAI(
    @Param('sessionId') sessionId: string,
    @Res() res: Response,
  ): Promise<void> {
    // Validate session before establishing SSE connection
    const session = await this.streamService.validateSession(sessionId);
    if (!session) {
      res.status(404).json({ error: 'Session not found' });
      return;
    }

    // Set SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.flushHeaders();

    const stream = await this.streamService.generateAIResponse(sessionId);

    for await (const chunk of stream) {
      res.write(`data: ${JSON.stringify({ chunk })}\n\n`);
    }

    res.write('event: done\ndata: {}\n\n');
    res.end();
  }
}
```

**Benefits:**
- Full control over response headers
- Can return HTTP errors before establishing SSE connection
- Better error handling

**Drawbacks:**
- Manual SSE format management (`data: ...\n\n`)
- No RxJS observable abstraction

---

## Authentication for SSE

### Challenge: EventSource API Doesn't Support Custom Headers

The native browser `EventSource` API does not allow setting custom headers like `Authorization: Bearer <token>`. This creates authentication challenges for JWT-based systems.

### Solution 1: Query Parameter Authentication (Simplest)

Pass JWT token as URL query parameter:

**Backend:**

```typescript
import { Controller, Sse, Query, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';

@Controller('stream')
export class StreamController {
  constructor(private readonly jwtService: JwtService) {}

  @Sse('ai')
  async streamAI(@Query('token') token: string): Observable<MessageEvent> {
    // Validate token
    try {
      const payload = this.jwtService.verify(token);
      const userId = payload.sub;

      // Return stream scoped to user
      return this.createUserStream(userId);
    } catch (error) {
      throw new UnauthorizedException('Invalid token');
    }
  }
}
```

**Frontend (Next.js):**

```typescript
'use client';

import { useEffect, useState } from 'react';

export function AIStreamComponent({ sessionId }: { sessionId: string }) {
  const [chunks, setChunks] = useState<string[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('jwt_token');
    const eventSource = new EventSource(
      `http://localhost:3001/stream/ai?token=${token}&session=${sessionId}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setChunks((prev) => [...prev, data.chunk]);
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [sessionId]);

  return (
    <div>
      {chunks.map((chunk, i) => (
        <span key={i}>{chunk}</span>
      ))}
    </div>
  );
}
```

**Security Considerations:**
- ⚠️ Tokens in query params appear in server logs
- ⚠️ Tokens may be cached by browsers/proxies
- ✅ Acceptable for short-lived tokens (e.g., 5-minute SSE-specific tokens)
- ✅ Use HTTPS to prevent token interception

**Mitigation:**
Generate a short-lived token specifically for SSE:

```typescript
// POST /stream/init
@Post('init')
async initStream(@Req() req: Request): Promise<{ streamToken: string }> {
  const userId = req.user.sub; // From JWT guard

  // Generate 5-minute token for SSE only
  const streamToken = this.jwtService.sign(
    { sub: userId, type: 'sse' },
    { expiresIn: '5m' }
  );

  return { streamToken };
}
```

```typescript
// Client: First get stream token, then connect
const { streamToken } = await fetch('/stream/init', {
  headers: { Authorization: `Bearer ${mainJWT}` }
}).then(r => r.json());

const eventSource = new EventSource(`/stream/ai?token=${streamToken}`);
```

### Solution 2: Cookie-Based Authentication (Most Secure)

Use HttpOnly cookies for authentication:

**Backend:**

```typescript
@Controller('stream')
export class StreamController {
  @Sse('ai')
  async streamAI(@Req() req: Request): Observable<MessageEvent> {
    // Cookie automatically sent by browser
    const token = req.cookies['access_token'];

    if (!token) {
      throw new UnauthorizedException('No token');
    }

    const payload = this.jwtService.verify(token);
    return this.createUserStream(payload.sub);
  }
}
```

**Frontend:**

```typescript
// No token needed - browser sends cookie automatically
const eventSource = new EventSource('http://localhost:3001/stream/ai', {
  withCredentials: true, // Include cookies in cross-origin requests
});
```

**CORS Configuration Required:**

```typescript
// main.ts
app.enableCors({
  origin: process.env.FRONTEND_URL,
  credentials: true, // Allow cookies
});
```

**Benefits:**
- ✅ Tokens not exposed in URLs
- ✅ HttpOnly cookies prevent XSS theft
- ✅ Automatic browser handling

**Drawbacks:**
- ⚠️ Requires cookie-based auth (may not fit all architectures)
- ⚠️ CORS configuration complexity

### Solution 3: EventSource Polyfill (Custom Headers)

Use `eventsource` npm package (polyfill) to send custom headers:

**Installation:**

```bash
npm install eventsource
```

**Frontend:**

```typescript
import EventSource from 'eventsource';

const token = localStorage.getItem('jwt_token');
const eventSource = new EventSource('http://localhost:3001/stream/ai', {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

**Backend (same as normal @Sse):**

```typescript
@Controller('stream')
export class StreamController {
  @UseGuards(JwtAuthGuard) // Works with custom headers
  @Sse('ai')
  streamAI(@Req() req: Request): Observable<MessageEvent> {
    const userId = req.user.sub;
    return this.createUserStream(userId);
  }
}
```

**Benefits:**
- ✅ Standard JWT Bearer token in headers
- ✅ Works with existing JwtAuthGuard

**Drawbacks:**
- ⚠️ Requires npm package (not native browser API)
- ⚠️ Polyfill may have different behavior than native EventSource
- ⚠️ Larger bundle size

### Recommendation for the project

**Use Solution 1 (Query Parameter) with 5-minute SSE-specific tokens:**
- Simple implementation
- No additional dependencies
- Security adequate with short-lived tokens over HTTPS
- Tokens don't grant access to REST APIs (scoped to `type: 'sse'`)

---

## Streaming Claude API Responses via SSE

### Claude SDK Streaming Basics

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Approach 1: stream() helper
const stream = await client.messages.stream({
  model: 'claude-opus-4-5',
  max_tokens: 4096,
  messages: [{ role: 'user', content: 'Explain SSE' }],
});

// Listen to events
stream.on('text', (text) => {
  console.log(text); // Accumulated text so far
});

stream.on('finalMessage', (message) => {
  console.log(message.usage); // Token counts
});

// Approach 2: create() with stream: true
const stream = await client.messages.create({
  model: 'claude-opus-4-5',
  max_tokens: 4096,
  messages: [{ role: 'user', content: 'Explain SSE' }],
  stream: true,
});

for await (const event of stream) {
  if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
    console.log(event.delta.text); // Chunk
  }
}
```

### Bridging Claude Stream to NestJS SSE

**Service Layer:**

```typescript
import Anthropic from '@anthropic-ai/sdk';
import { Injectable } from '@nestjs/common';

@Injectable()
export class ClaudeService {
  private client: Anthropic;

  constructor() {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
  }

  async *streamResponse(messages: any[]): AsyncGenerator<string, void, unknown> {
    const stream = await this.client.messages.create({
      model: 'claude-opus-4-5',
      max_tokens: 4096,
      messages,
      stream: true,
    });

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
        yield event.delta.text;
      }
    }
  }
}
```

**Controller with SSE:**

```typescript
import { Controller, Sse, Param } from '@nestjs/common';
import { Observable } from 'rxjs';

@Controller('ai')
export class AIController {
  constructor(private readonly claudeService: ClaudeService) {}

  @Sse('chat/:sessionId')
  async streamChat(@Param('sessionId') sessionId: string): Promise<Observable<MessageEvent>> {
    const messages = await this.getMessageHistory(sessionId);

    return new Observable((observer) => {
      this.claudeService
        .streamResponse(messages)
        .then(async (stream) => {
          for await (const chunk of stream) {
            observer.next({
              data: JSON.stringify({ sessionId, chunk }),
            } as MessageEvent);
          }

          observer.next({
            data: JSON.stringify({ sessionId, done: true }),
          } as MessageEvent);

          observer.complete();
        })
        .catch((error) => {
          observer.error(error);
        });
    });
  }
}
```

### Event-Driven Pattern with EventEmitter2

Decouple streaming logic from SSE endpoint:

**Service:**

```typescript
import { Injectable } from '@nestjs/common';
import { EventEmitter2 } from '@nestjs/event-emitter';

@Injectable()
export class ChatService {
  constructor(
    private readonly claudeService: ClaudeService,
    private readonly eventEmitter: EventEmitter2,
  ) {}

  async processMessage(sessionId: string, userMessage: string): Promise<void> {
    // Save user message
    await this.saveMessage(sessionId, 'USER', userMessage);

    // Emit processing start
    this.eventEmitter.emit(`chat.${sessionId}.status`, { status: 'processing' });

    // Stream AI response
    const messages = await this.getMessageHistory(sessionId);
    const stream = await this.claudeService.streamResponse(messages);

    let fullResponse = '';

    for await (const chunk of stream) {
      fullResponse += chunk;
      this.eventEmitter.emit(`chat.${sessionId}.chunk`, { chunk });
    }

    // Save AI message
    await this.saveMessage(sessionId, 'ASSISTANT', fullResponse);

    // Emit completion
    this.eventEmitter.emit(`chat.${sessionId}.complete`, { done: true });
  }
}
```

**Controller:**

```typescript
@Controller('chat')
export class ChatController {
  constructor(private readonly eventEmitter: EventEmitter2) {}

  @Sse('stream/:sessionId')
  streamSession(@Param('sessionId') sessionId: string): Observable<MessageEvent> {
    return fromEvent(this.eventEmitter, `chat.${sessionId}.*`).pipe(
      map((payload) => ({ data: JSON.stringify(payload) }))
    );
  }

  @Post('message')
  @UseGuards(JwtAuthGuard)
  async sendMessage(
    @Body() dto: SendMessageDto,
    @Req() req: Request,
  ): Promise<void> {
    const userId = req.user.sub;
    await this.chatService.processMessage(dto.sessionId, dto.content);
  }
}
```

**Client Flow:**

1. Open SSE connection to `/chat/stream/:sessionId`
2. POST message to `/chat/message`
3. SSE receives chunks as they're generated
4. Close SSE when done

---

## Reconnection Handling

### Automatic Browser Reconnection

EventSource API automatically reconnects when connection drops:

```typescript
const eventSource = new EventSource('/stream/ai');

eventSource.addEventListener('open', () => {
  console.log('SSE connection established');
});

eventSource.addEventListener('error', (error) => {
  console.error('SSE error:', error);
  // Browser automatically attempts reconnection with exponential backoff
});
```

**Default Behavior:**
- Browser retries with exponential backoff (1s, 2s, 4s, ...)
- Max retry interval: ~60 seconds
- No limit on retry attempts

### Custom Retry Logic

Override default retry interval with `retry` field:

**Backend:**

```typescript
@Sse('stream')
stream(): Observable<MessageEvent> {
  return new Observable((observer) => {
    // Send retry interval (3 seconds)
    observer.next({
      retry: 3000, // milliseconds
    } as MessageEvent);

    // Send data events
    observer.next({ data: JSON.stringify({ chunk: 'Hello' }) });
  });
}
```

**SSE Format:**

```
retry: 3000

data: {"chunk":"Hello"}

```

### Event ID for Resume After Reconnection

Use `Last-Event-ID` header to resume from last received event:

**Backend:**

```typescript
@Sse('stream/:sessionId')
async streamSession(
  @Param('sessionId') sessionId: string,
  @Headers('last-event-id') lastEventId?: string,
): Promise<Observable<MessageEvent>> {
  let messageId = lastEventId ? parseInt(lastEventId) : 0;

  return new Observable((observer) => {
    const messages = await this.getMessagesSince(sessionId, messageId);

    messages.forEach((msg) => {
      observer.next({
        id: msg.id.toString(), // Event ID
        data: JSON.stringify(msg),
      } as MessageEvent);
    });

    observer.complete();
  });
}
```

**Client:**

Browser automatically sends `Last-Event-ID` header on reconnection if events had `id` field.

### Manual Reconnection Control

```typescript
let eventSource: EventSource | null = null;
let reconnectAttempts = 0;
const MAX_RECONNECTS = 5;

function connect() {
  eventSource = new EventSource('/stream/ai');

  eventSource.onopen = () => {
    reconnectAttempts = 0; // Reset on success
  };

  eventSource.onerror = () => {
    eventSource?.close();

    if (reconnectAttempts < MAX_RECONNECTS) {
      reconnectAttempts++;
      setTimeout(() => connect(), 1000 * reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  };
}
```

---

## Scaling SSE with Redis Pub/Sub

### Why Redis is Needed for Horizontal Scaling

**Problem:** SSE connections are stateful (tied to specific server instance). If you have 2 API instances:
- User A connects to Server 1 for SSE
- Service on Server 2 emits event via EventEmitter2
- User A never receives the event (EventEmitter2 is in-process only)

**Solution:** Redis Pub/Sub distributes events across all server instances.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                         │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  EventSource connection to SSE endpoint            │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP (SSE)
        ┌─────────────────────────────────────────┐
        │         Load Balancer (nginx/ALB)       │
        └─────────────────────────────────────────┘
                          ↓
        ┌─────────────┬─────────────┬─────────────┐
        │   API #1    │   API #2    │   API #3    │
        │  (NestJS)   │  (NestJS)   │  (NestJS)   │
        │             │             │             │
        │ SSE clients │ SSE clients │ SSE clients │
        └──────┬──────┴──────┬──────┴──────┬───────┘
               │             │             │
               └─────────────┼─────────────┘
                             ↓
                    ┌────────────────┐
                    │  Redis Pub/Sub │
                    │   (Upstash)    │
                    └────────────────┘
```

### Redis Adapter Implementation

**Installation:**

```bash
npm install redis
```

**Redis Pub/Sub Service:**

```typescript
import { Injectable, OnModuleInit } from '@nestjs/common';
import { createClient, RedisClientType } from 'redis';
import { EventEmitter2 } from '@nestjs/event-emitter';

@Injectable()
export class RedisPubSubService implements OnModuleInit {
  private publisher: RedisClientType;
  private subscriber: RedisClientType;

  constructor(private readonly eventEmitter: EventEmitter2) {}

  async onModuleInit() {
    this.publisher = createClient({ url: process.env.REDIS_URL });
    this.subscriber = this.publisher.duplicate();

    await Promise.all([this.publisher.connect(), this.subscriber.connect()]);

    // Subscribe to SSE events channel
    await this.subscriber.subscribe('sse:events', (message) => {
      const { event, payload } = JSON.parse(message);
      this.eventEmitter.emit(event, payload); // Re-emit to local EventEmitter2
    });
  }

  async publish(event: string, payload: any): Promise<void> {
    await this.publisher.publish(
      'sse:events',
      JSON.stringify({ event, payload })
    );
  }
}
```

**Modified Chat Service:**

```typescript
@Injectable()
export class ChatService {
  constructor(
    private readonly claudeService: ClaudeService,
    private readonly redisPubSub: RedisPubSubService,
  ) {}

  async processMessage(sessionId: string, userMessage: string): Promise<void> {
    const stream = await this.claudeService.streamResponse([...]);

    for await (const chunk of stream) {
      // Publish to Redis instead of local EventEmitter
      await this.redisPubSub.publish(`chat.${sessionId}.chunk`, { chunk });
    }

    await this.redisPubSub.publish(`chat.${sessionId}.complete`, { done: true });
  }
}
```

**Controller (unchanged):**

```typescript
@Sse('stream/:sessionId')
streamSession(@Param('sessionId') sessionId: string): Observable<MessageEvent> {
  // Listens to EventEmitter2, which receives events from Redis subscriber
  return fromEvent(this.eventEmitter, `chat.${sessionId}.*`).pipe(
    map((payload) => ({ data: JSON.stringify(payload) }))
  );
}
```

**How it Works:**

1. Service on Server 2 calls `redisPubSub.publish('chat.123.chunk', ...)`
2. Redis broadcasts message to all subscribed instances (Server 1, 2, 3)
3. Each server's RedisPubSubService receives message and emits to local EventEmitter2
4. Server 1's SSE connection (User A) receives event via EventEmitter2 → RxJS Observable

### Redis Sharded Pub/Sub (Redis 7.0+)

For better performance at scale, use sharded pub/sub:

```typescript
// Instead of subscriber.subscribe('sse:events', ...)
await this.subscriber.sSubscribe('sse:events', (message, channel) => {
  const { event, payload } = JSON.parse(message);
  this.eventEmitter.emit(event, payload);
});

// Publish to sharded channel
await this.publisher.sPublish('sse:events', JSON.stringify({ event, payload }));
```

**Benefits:**
- Reduces Redis CPU usage by 30-50%
- Better message distribution across cluster
- Supported by Upstash Redis

### Upstash Redis Configuration

**Environment Variables:**

```env
REDIS_URL=rediss://:password@region.upstash.io:6379
```

**Cost:** Pay-per-request (no fixed monthly cost) - ideal for MVP.

---

## Error Handling

### Categorized Error Responses

```typescript
@Sse('stream/:sessionId')
async streamSession(@Param('sessionId') sessionId: string): Promise<Observable<MessageEvent>> {
  return new Observable((observer) => {
    this.processStream(sessionId, observer).catch((error) => {
      if (error instanceof NotFoundException) {
        observer.next({
          event: 'error',
          data: JSON.stringify({ type: 'NOT_FOUND', message: 'Session not found' }),
        } as MessageEvent);
      } else if (error instanceof UnauthorizedException) {
        observer.next({
          event: 'error',
          data: JSON.stringify({ type: 'AUTH_ERROR', message: 'Unauthorized' }),
        } as MessageEvent);
      } else {
        observer.next({
          event: 'error',
          data: JSON.stringify({ type: 'INTERNAL_ERROR', message: 'Something went wrong' }),
        } as MessageEvent);
      }

      observer.complete();
    });
  });
}
```

**Client-Side:**

```typescript
eventSource.addEventListener('error', (event) => {
  if (event.data) {
    const error = JSON.parse(event.data);
    if (error.type === 'AUTH_ERROR') {
      // Redirect to login
    }
  }
});
```

### Timeout Handling

```typescript
@Sse('stream/:sessionId')
async streamSession(@Param('sessionId') sessionId: string): Promise<Observable<MessageEvent>> {
  return new Observable((observer) => {
    const timeout = setTimeout(() => {
      observer.next({
        event: 'error',
        data: JSON.stringify({ type: 'TIMEOUT', message: 'Request timed out' }),
      } as MessageEvent);
      observer.complete();
    }, 30000); // 30 second timeout

    this.processStream(sessionId, observer)
      .finally(() => clearTimeout(timeout));
  });
}
```

### Graceful Shutdown

```typescript
// main.ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  process.on('SIGTERM', async () => {
    console.log('SIGTERM received, closing SSE connections...');
    // EventEmitter2 broadcast shutdown event
    app.get(EventEmitter2).emit('server:shutdown', { message: 'Server restarting' });

    await new Promise((resolve) => setTimeout(resolve, 1000)); // Give clients 1s
    await app.close();
  });

  await app.listen(3000);
}
```

**Client Auto-Reconnects:**

Browser's EventSource will automatically reconnect after server shutdown.

---

## Known Issues with @Sse Decorator

### Issue 1: Connection Established Before Handler

**Problem:** When using `@Sse()`, the SSE connection is established **before** the handler is called. This means:
- You cannot return HTTP errors (404, 401) before SSE starts
- Client receives SSE connection, then error events instead of HTTP status codes

**Workaround:** Use `@Get()` with manual SSE headers (Pattern 3 above).

### Issue 2: HttpException Sends SSE Error Message

**Problem:** Throwing `HttpException` inside `@Sse()` handler sends an SSE error event instead of HTTP error response.

```typescript
@Sse('stream')
stream(): Observable<MessageEvent> {
  throw new NotFoundException(); // Client receives SSE error event, not HTTP 404
}
```

**Expected:** HTTP 404 response
**Actual:** SSE connection established, then error event

**Workaround:** Validate before returning observable, send errors as SSE events.

### GitHub Issues

- [#12670 - Server-Sent Events implementation needs improvements](https://github.com/nestjs/nest/issues/12670)
- [#9517 - SSE events not disconnecting and retrying correctly with enableShutdownHooks](https://github.com/nestjs/nest/issues/9517)
- [#4826 - Server-Sent Events support (original feature request)](https://github.com/nestjs/nest/issues/4826)

---

## Testing SSE Endpoints

### Unit Testing with RxJS TestScheduler

```typescript
import { Test } from '@nestjs/testing';
import { EventsController } from './events.controller';
import { TestScheduler } from 'rxjs/testing';

describe('EventsController', () => {
  let controller: EventsController;
  let testScheduler: TestScheduler;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      controllers: [EventsController],
      providers: [MockEventService],
    }).compile();

    controller = module.get(EventsController);

    testScheduler = new TestScheduler((actual, expected) => {
      expect(actual).toEqual(expected);
    });
  });

  it('should emit SSE events', () => {
    testScheduler.run(({ expectObservable }) => {
      const result$ = controller.streamEvents();

      expectObservable(result$).toBe('a-b-c', {
        a: { data: 'event1' },
        b: { data: 'event2' },
        c: { data: 'event3' },
      });
    });
  });
});
```

### Integration Testing with Supertest

```typescript
import { Test } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';

describe('SSE E2E', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const module = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = module.createNestApplication();
    await app.init();
  });

  it('should stream SSE events', (done) => {
    const chunks: string[] = [];

    request(app.getHttpServer())
      .get('/stream/test-session')
      .set('Accept', 'text/event-stream')
      .buffer(false) // Don't buffer response
      .parse((res, callback) => {
        res.on('data', (chunk) => {
          chunks.push(chunk.toString());
        });
        res.on('end', () => callback(null, chunks));
      })
      .end((err, res) => {
        expect(chunks.length).toBeGreaterThan(0);
        expect(chunks[0]).toContain('data:');
        done();
      });
  });
});
```

---

## Performance Considerations

### Connection Limits

| Infrastructure | Concurrent SSE Connections | Cost |
|----------------|---------------------------|------|
| Single Node.js instance (2GB RAM) | ~10,000 | Free (self-hosted) |
| Cluster (4 instances + Redis) | ~40,000 | ~$150/month (Upstash + hosting) |
| Cloud-managed (AWS ALB + ECS) | 100,000+ | ~$500-1000/month |

**the project MVP Target:** 1,000-10,000 concurrent users → Single instance + Upstash Redis sufficient.

### Memory Management

Each SSE connection consumes ~5KB of memory:
- 10,000 connections = ~50MB
- Monitor with:

```typescript
setInterval(() => {
  const connections = this.getActiveConnections();
  console.log(`Active SSE connections: ${connections.size}`);
}, 60000); // Every minute
```

### HTTP/2 Multiplexing Advantage

SSE over HTTP/2 allows multiple streams per TCP connection:
- 100 SSE connections = 1 TCP connection (with HTTP/2)
- 100 SSE connections = 100 TCP connections (with HTTP/1.1)

**Ensure HTTP/2 is enabled** on reverse proxy (nginx, ALB, CloudFlare).

### Rate Limiting

Prevent abuse by limiting SSE connection rate:

```typescript
import { ThrottlerGuard } from '@nestjs/throttler';

@Controller('stream')
export class StreamController {
  @UseGuards(ThrottlerGuard)
  @Sse('ai')
  streamAI(): Observable<MessageEvent> {
    // Limit: 5 connections per minute per user
  }
}
```

---

## Project Integration (the project Chat Module)

### Recommended Architecture for Task-009

```
┌─────────────────────────────────────────────────────────────┐
│                  Next.js Frontend (Vercel)                  │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ChatInterface Component ('use client')            │    │
│  │  - EventSource connection (native browser API)     │    │
│  │  - Short-lived SSE token from /stream/init         │    │
│  │  - Progressive chunk rendering                     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP SSE
┌─────────────────────────────────────────────────────────────┐
│              NestJS API (Railway/Fly.io + Upstash)          │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  StreamController (@Sse or @Get)                   │    │
│  │  - Query param auth with 5-min tokens              │    │
│  │  - Returns Observable<MessageEvent>                │    │
│  │  - Listens to EventEmitter2 events                 │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ChatService                                       │    │
│  │  - Processes user messages                         │    │
│  │  - Emits chunks via RedisPubSubService             │    │
│  │  - Integrates multi-agent pipeline                 │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ClaudeService (streaming)                         │    │
│  │  - AsyncGenerator<string> for chunks               │    │
│  │  - Token tracking                                  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓ Redis Pub/Sub
┌─────────────────────────────────────────────────────────────┐
│                    Upstash Redis (Serverless)               │
│  - Pub/Sub for cross-instance event distribution          │
│  - Pay-per-request (no fixed monthly cost)                 │
└─────────────────────────────────────────────────────────────┘
```

### Environment Variables

```env
# apps/api/.env
FRONTEND_URL=http://localhost:3000
REDIS_URL=rediss://:password@region.upstash.io:6379
ANTHROPIC_API_KEY=sk-ant-xxx
```

```env
# apps/web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:3001
```

### Key Implementation Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Transport Protocol** | SSE (not WebSocket) | Simpler for unidirectional streaming, industry standard for LLMs |
| **Authentication** | Query param with 5-min SSE-specific token | Avoids EventSource header limitation, secure enough with short TTL |
| **NestJS Pattern** | @Sse() with EventEmitter2 | Decouples streaming from business logic |
| **Streaming Source** | Claude SDK async generator | Native SDK support, clean async iteration |
| **Scaling Strategy** | Redis Pub/Sub for cross-instance events | Horizontal scaling for 10K+ users |
| **Error Recovery** | Browser auto-reconnect + event IDs | Resume after network failure |
| **Multi-Agent Events** | EventEmitter2 → Redis → SSE observable | Clean separation of concerns |

---

## SSE vs WebSocket Decision Matrix for the project

| Requirement | SSE | WebSocket | Recommended |
|-------------|-----|-----------|-------------|
| **Stream AI responses to client** | ✅ Perfect fit | ⚠️ Overkill | **SSE** |
| **Client sends messages to server** | ⚠️ Requires separate POST endpoint | ✅ Same connection | **SSE** (POST + SSE simpler than WebSocket) |
| **Typing indicators** | ⚠️ Client polls or sends via POST | ✅ Bidirectional | **WebSocket** (if needed) |
| **File uploads during chat** | ⚠️ Separate HTTP POST | ✅ Can send via WebSocket | **SSE** (file uploads rare, HTTP fine) |
| **Reconnection handling** | ✅ Automatic (EventSource) | ⚠️ Manual | **SSE** |
| **Authentication** | ⚠️ Query params or cookies | ✅ Custom headers | **SSE** (workarounds acceptable) |
| **Scaling** | ✅ Stateless HTTP | ⚠️ Requires sticky sessions | **SSE** |
| **Industry precedent** | ✅ ChatGPT, Claude, OpenAI use SSE | ⚠️ Rare for LLM streaming | **SSE** |

**Verdict for the project Task-009:**

**Use SSE** for the MVP implementation. It's simpler, follows industry best practices for LLM streaming, and scales more easily. Evaluate WebSocket only if future requirements include:
- Real-time collaborative features
- Voice/video integration
- High-frequency bidirectional events (e.g., live coding, whiteboard)

---

## Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| **Using @Sse with auth guards** | HttpException doesn't return HTTP errors | Validate token inside handler, send errors as SSE events |
| **Tokens in query params logged** | Security risk if tokens long-lived | Use short-lived (5-min) SSE-specific tokens |
| **No Redis for multi-instance** | Events only received on same server | Implement Redis Pub/Sub adapter |
| **Blocking event loop** | SSE connections freeze | Use async/await, avoid sync operations |
| **Not testing reconnection** | Poor UX on network issues | Test with Chrome DevTools throttling |
| **Missing CORS for cross-origin** | EventSource fails to connect | Enable CORS with `credentials: true` if using cookies |
| **No heartbeat/keepalive** | Proxies close idle connections | Send comment lines every 15-30s: `res.write(': keepalive\n\n')` |

---

## Best Practices Summary

### DO

✅ Use SSE for unidirectional LLM streaming (industry standard)
✅ Authenticate with query params + short-lived tokens (5-min TTL)
✅ Decouple streaming logic with EventEmitter2 + RxJS
✅ Implement Redis Pub/Sub for horizontal scaling
✅ Send keepalive comments every 30 seconds
✅ Use event IDs for resumable streams
✅ Test reconnection scenarios
✅ Monitor active connection count

### DO NOT

❌ Use WebSocket for simple LLM streaming (over-engineering)
❌ Put long-lived JWT tokens in query params
❌ Block event loop with synchronous operations
❌ Forget CORS configuration for cross-origin requests
❌ Skip graceful shutdown handling
❌ Assume single-server deployment (plan for scale)
❌ Use @Sse decorator if you need HTTP error responses before connection

---

## Sources

- [NestJS Server-Sent Events Documentation](https://docs.nestjs.com/techniques/server-sent-events)
- [NestJS Server-Sent Events (SSE) and Its Use Cases - Medium](https://medium.com/@kumar.gowtham/nestjs-server-sent-events-sse-and-its-use-cases-9f7316e78fa0)
- [Real-Time Communication Made Simple: Building Server-Sent Events (SSE) with NestJS - Medium](https://devkamal.medium.com/real-time-communication-made-simple-building-server-sent-events-sse-with-nestjs-f6a8f5715d18)
- [Utilize Real-Time NestJS using Server-Sent Events](https://iliabedian.com/blog/server-side-events-on-nestjs-emitting-events-to-clients)
- [Backend Implementation - Using NestJS SSE for Updating Front-end - Medium](https://medium.com/using-nestjs-sse-for-updating-front-end/backend-implementation-cedd3801c210)
- [Server-Sent Events (SSE) with NestJS and Angular - Medium](https://medium.com/@piotrkorowicki/server-sent-events-sse-with-nestjs-and-angular-d90635783d8c)
- [NestJS: A Request Progress Tracker Using SSE - Medium](https://medium.com/@leonardoacrg.dev/nestjs-a-request-progress-tracker-using-sse-b9f2fded9d70)
- [Server-Sent Events implementation needs improvements - GitHub Issue #12670](https://github.com/nestjs/nest/issues/12670)
- [Server-Sent Events support - GitHub Issue #4826](https://github.com/nestjs/nest/issues/4826)
- [Streaming AI Responses with WebSockets, SSE, and gRPC - Medium](https://medium.com/@pranavprakash4777/streaming-ai-responses-with-websockets-sse-and-grpc-which-one-wins-a481cab403d3)
- [SSE vs WebSockets in AWS: Building a Serverless OpenAI Chatbot - Medium](https://medium.com/@raulblazquezbullon/sse-vs-websockets-in-aws-building-a-serverless-openai-chatbot-with-lambda-22ab29c75405)
- [The Streaming Backbone of LLMs: Why SSE Still Wins in 2025](https://procedure.tech/blogs/the-streaming-backbone-of-llms-why-server-sent-events-(sse)-still-wins-in-2025)
- [How ChatGPT Streams Responses Back to the User](https://blog.theodormarcu.com/p/how-chatgpt-streams-responses-back)
- [Server-Sent Events: Breaking Down How ChatGPT Streams Text - Medium](https://medium.com/@hitesh4296/server-sent-events-breaking-down-how-chatgpt-streams-text-4b1d2d4db4ce)
- [Streaming for LLM Apps: SSE vs WebSockets - Hivenet](https://compute.hivenet.com/post/llm-streaming-sse-websockets)
- [How We Used SSE to Stream LLM Responses at Scale - Medium](https://medium.com/@daniakabani/how-we-used-sse-to-stream-llm-responses-at-scale-fa0d30a6773f)
- [How to Stream LLM Responses Using Server-Sent Events (SSE)](https://apidog.com/blog/stream-llm-responses-using-sse/)
- [Assistant Streaming: WebSockets VS SSE - OpenAI Community](https://community.openai.com/t/assistant-streaming-websockets-vs-sse/738161)
- [Streaming Messages - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [Real-time AI in Next.js: How to stream responses with Vercel AI SDK - LogRocket](https://blog.logrocket.com/nextjs-vercel-ai-sdk-streaming/)
- [How streaming LLM APIs work - Simon Willison's TILs](https://til.simonwillison.net/llms/streaming-llm-apis)
- [Claude Code Internals, Part 7: SSE Stream Processing - Medium](https://kotrotsos.medium.com/claude-code-internals-part-7-sse-stream-processing-c620ae9d64a1)
- [API Servers: Nest.js - AI SDK](https://ai-sdk.dev/cookbook/api-servers/nest)
- [HTTP API server sent events (SSE) - Eclipse Ditto](https://eclipse.dev/ditto/httpapi-sse.html)
- [ServerEvents + JWT authentication - ServiceStack Forums](https://forums.servicestack.net/t/serverevents-jwt-authentication/4998)
- [Deep Dive into Server-sent Events (SSE) - DEV Community](https://dev.to/debajit13/deep-dive-into-server-sent-events-sse-52)
- [Setting headers for EventSource - WHATWG GitHub Issue #2177](https://github.com/whatwg/html/issues/2177)
- [Delivering Real-Time Notifications with Server-Sent Events on Growth Center - Medium](https://medium.com/trendyol-tech/delivering-real-time-notifications-to-over-300k-sellers-with-server-sent-events-on-growth-center-95e180c486bc)
- [A Primer on Server-Sent Events (SSE) - Aklivity Blog](https://www.aklivity.io/post/a-primer-on-server-sent-events-sse)
- [Reactive Real-Time Notifications with SSE, Spring Boot, and Redis Pub/Sub - InfoQ](https://www.infoq.com/articles/reactive-notification-system-server-sent-events/)
- [Horizontal Scaling of a Stateful Server with redis pub/sub - Medium](https://medium.com/walkme-engineering/horizontal-scaling-of-a-stateful-server-with-redis-pub-sub-fc56c875b1aa)
- [Unlocking Redis Pub/Sub's Potential: Scaling with Sharded Channels - Oreate AI Blog](https://www.oreateai.com/blog/unlocking-redis-pubsubs-potential-scaling-your-messaging-with-sharded-channels/da0bdea4096874c6d1d0469841992982)
- [EventSource - Web APIs - MDN](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [Server-sent events - HTML Standard - WHATWG](https://html.spec.whatwg.org/multipage/server-sent-events.html)
