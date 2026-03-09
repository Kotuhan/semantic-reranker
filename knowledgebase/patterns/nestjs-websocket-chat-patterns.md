---
title: NestJS WebSocket Architecture Patterns for Real-Time Chat with LLM Streaming
domain: pattern
tech: [nestjs, websocket, socketio, typescript, redis, jwt, claude-api]
area: [websocket, real-time, chat, llm-streaming, authentication, scaling]
staleness: 6months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://dev.to/mouloud_hasrane_c99b0f49a/websocket-authentication-in-nestjs-handling-jwt-and-guards-4j27
  - https://preetmishra.com/blog/the-best-way-to-authenticate-websockets-in-nestjs
  - https://node.kumarchaudhary.com.np/securing-socketio-in-nestjs-with-jwt-and-passport-a-comprehensive-guide
  - https://platform.claude.com/docs/en/build-with-claude/streaming
  - https://dev.to/hobbada/the-complete-guide-to-streaming-llm-responses-in-web-applications-from-sse-to-real-time-ui-3534
  - https://medium.com/@case3/scaling-socket-io-with-nestjs-or-nodejs-and-redis-using-pub-sub-model-c6ef8ea7dad8
  - https://praeclarumtech.com/websockets-at-scale-real-time-architectures-with-nestjs-and-redis-pub-sub/
  - https://medium.com/@mohsenmahoski/clustering-and-scaling-socket-io-server-using-node-js-nest-js-and-redis-43e8e67847b7
  - https://blog.logrocket.com/scalable-websockets-with-nestjs-and-redis/
  - https://socket.io/docs/v4/redis-adapter/
  - https://www.index.dev/skill-vs-skill/socketio-vs-websockets-vs-server-sent-events
  - https://medium.com/@avijitbera775/comprehensive-websocket-connection-management-in-nestjs-building-scalable-real-time-applications-dc6808015b1b
  - https://medium.com/@marufpulok98/building-a-production-ready-real-time-notification-system-in-nestjs-websockets-redis-offline-6cc2f1bd0b05
  - https://docs.nestjs.com/websockets/gateways
  - https://docs.nestjs.com/websockets/adapter
---

# NestJS WebSocket Architecture Patterns for Real-Time Chat with LLM Streaming

## Overview

This research covers WebSocket implementation patterns in NestJS specifically for building a real-time chat application with multi-agent LLM orchestration and streaming responses. The focus is on Socket.IO vs native WebSocket tradeoffs, JWT authentication strategies, connection management, state recovery, and scaling with Redis for horizontal deployment.

**Use Case Context**: the project Deep Dive chat module with Session Facilitator + Psychologist agents streaming responses from Claude API over WebSocket to Next.js frontend.

---

## Socket.IO vs Native WebSocket in NestJS

### Comparison Matrix

| Aspect | Socket.IO | Native WebSocket |
|--------|-----------|------------------|
| **Protocol** | WebSocket + HTTP long-polling fallback | WebSocket only |
| **Auto-reconnection** | ✅ Built-in with exponential backoff | ❌ Manual implementation required |
| **Rooms/Namespaces** | ✅ Built-in (`join`, `leave`, `to`) | ❌ Manual implementation required |
| **Bandwidth overhead** | 10-15% more due to protocol wrapping | Lower (no protocol overhead) |
| **Browser support** | ~99% (fallback to polling) | ~98% (modern browsers only) |
| **NestJS integration** | ✅ First-class support via `@nestjs/platform-socket.io` | ⚠️ Via `@nestjs/platform-ws` (less featured) |
| **Redis scaling** | ✅ Official adapter (`@socket.io/redis-adapter`) | ⚠️ Manual Pub/Sub implementation |
| **Binary data** | ✅ Supported | ✅ Supported |
| **Compression** | ✅ Built-in (gzip, deflate) | ⚠️ Manual implementation |
| **Latency (sub-5ms)** | ⚠️ ~10ms average | ✅ ~3-5ms (optimized) |
| **Connection overhead** | Higher (handshake involves multiple HTTP requests) | Lower (single upgrade request) |
| **Best for** | Most real-time apps (chat, notifications, dashboards) | Gaming, trading, high-throughput IoT |

### Performance Characteristics

**Socket.IO:**
- Bandwidth: +10-15% overhead (negligible for chat applications)
- Connection cost: ~15-20ms handshake time
- Scaling: Horizontal scaling with Redis Pub/Sub (built-in adapter)
- Recommended for: 80% of use cases where developer productivity > micro-optimizations

**Native WebSocket:**
- Bandwidth: Minimal overhead (raw protocol)
- Connection cost: ~5-10ms handshake time
- Scaling: Manual Redis Pub/Sub implementation required
- Recommended for: 100K+ concurrent connections, sub-5ms latency requirements, dedicated DevOps team

### Decision Criteria for the project

**Socket.IO is recommended because:**
1. ✅ Built-in reconnection with exponential backoff (critical for mobile clients)
2. ✅ Room support for per-session message routing (`socket.join(sessionId)`)
3. ✅ Redis adapter for horizontal scaling (simple configuration)
4. ✅ HTTP long-polling fallback (works in restrictive networks)
5. ✅ First-class NestJS support with decorator-based API
6. ⚠️ 10-15% bandwidth overhead is negligible for chat (text-heavy, not video/gaming)

**Estimated scale:** the project MVP targets ~1-10K concurrent users. Socket.IO handles this effortlessly. Re-evaluate at 50K+ users if profiling shows protocol overhead as bottleneck.

---

## NestJS WebSocket Gateway Setup

### Installation

```bash
npm install @nestjs/websockets @nestjs/platform-socket.io socket.io
```

### Basic Gateway Structure

```typescript
// chat.gateway.ts
import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  OnGatewayConnection,
  OnGatewayDisconnect,
  ConnectedSocket,
  MessageBody,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';

@WebSocketGateway({
  cors: {
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true,
  },
  namespace: '/chat', // Optional: isolate chat events
})
export class ChatGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server: Server;

  constructor(
    private readonly chatService: ChatService,
    private readonly jwtService: JwtService,
  ) {}

  async handleConnection(client: Socket): Promise<void> {
    console.log(`Client connected: ${client.id}`);
    // Authentication happens here (see JWT section)
  }

  async handleDisconnect(client: Socket): Promise<void> {
    console.log(`Client disconnected: ${client.id}`);
    // Cleanup logic
  }

  @SubscribeMessage('message:send')
  async handleMessage(
    @ConnectedSocket() client: Socket,
    @MessageBody() payload: { sessionId: string; content: string },
  ): Promise<void> {
    // Process message and emit response
  }
}
```

### Connection Lifecycle Events

| Event | When It Fires | Use Case |
|-------|---------------|----------|
| `handleConnection` | Client connects to gateway | Authenticate, initialize session state |
| `handleDisconnect` | Client disconnects (intentional or network failure) | Cleanup resources, mark user offline |
| `@SubscribeMessage` | Client emits specific event | Handle chat messages, subscriptions, typing indicators |

---

## JWT Authentication for WebSockets

### Challenge: Guards Don't Work for WebSocket Connections

**Problem:** NestJS guards are designed for request-response cycles. WebSockets maintain long-lived connections. If you use short-lived JWT tokens and verify on every message, tokens expire mid-connection, breaking the flow.

**Solution:** Authenticate **only during handshake**, then trust the connection.

### Pattern 1: Custom WebSocket Adapter (Recommended)

Create a custom adapter to intercept and validate the JWT token before the connection is established.

```typescript
// ws-auth.adapter.ts
import { IoAdapter } from '@nestjs/platform-socket.io';
import { ServerOptions } from 'socket.io';
import { JwtService } from '@nestjs/jwt';
import { INestApplication } from '@nestjs/common';

export class WsAuthAdapter extends IoAdapter {
  private jwtService: JwtService;

  constructor(app: INestApplication) {
    super(app);
    this.jwtService = app.get(JwtService);
  }

  createIOServer(port: number, options?: ServerOptions): any {
    const server = super.createIOServer(port, options);

    // Middleware to authenticate on connection
    server.use((socket, next) => {
      const token = socket.handshake.auth?.token || socket.handshake.query?.token;

      if (!token) {
        return next(new Error('Authentication error: Token missing'));
      }

      try {
        const payload = this.jwtService.verify(token.replace('Bearer ', ''));
        socket.data.userId = payload.sub; // Attach userId to socket
        socket.data.email = payload.email;
        next();
      } catch (error) {
        return next(new Error('Authentication error: Invalid token'));
      }
    });

    return server;
  }
}
```

**Usage in `main.ts`:**

```typescript
import { WsAuthAdapter } from './ws-auth.adapter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.useWebSocketAdapter(new WsAuthAdapter(app));
  await app.listen(3000);
}
```

**Client-Side (Next.js):**

```typescript
import { io } from 'socket.io-client';

const socket = io('http://localhost:3000/chat', {
  auth: {
    token: 'Bearer YOUR_JWT_TOKEN',
  },
});
```

### Pattern 2: handleConnection Authentication

Validate token in the gateway's `handleConnection` method and disconnect if invalid.

```typescript
async handleConnection(client: Socket): Promise<void> {
  try {
    const token = client.handshake.auth?.token || client.handshake.query?.token;

    if (!token) {
      client.disconnect();
      return;
    }

    const payload = this.jwtService.verify(token.replace('Bearer ', ''));
    client.data.userId = payload.sub;
    client.data.email = payload.email;

    console.log(`Authenticated: ${client.data.email}`);
  } catch (error) {
    console.error('Authentication failed:', error.message);
    client.disconnect();
  }
}
```

### Pattern 3: Per-Message Guards (NOT Recommended)

**Why it fails:** Tokens expire mid-connection, causing disconnects during active conversations.

```typescript
// ❌ DON'T DO THIS
@UseGuards(WsJwtGuard)
@SubscribeMessage('message:send')
async handleMessage(...) {
  // If JWT expires after 15 minutes, user gets kicked mid-chat
}
```

**Best Practice:** Authenticate on connection, trust the socket thereafter. Use connection-level authorization (room membership, session ownership) for subsequent messages.

---

## Real-Time LLM Streaming Over WebSocket

### Claude API Streaming Basics

Claude API supports streaming via Server-Sent Events (SSE):

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const stream = await client.messages.stream({
  model: 'claude-opus-4-5',
  max_tokens: 4096,
  messages: [{ role: 'user', content: 'Explain WebSockets' }],
});

for await (const event of stream) {
  if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
    console.log(event.delta.text); // Streamed chunk
  }
}

const finalMessage = await stream.finalMessage();
console.log(finalMessage.usage); // Token counts
```

### Bridging Claude Stream to Socket.IO

**Pattern: Consume Claude stream, emit chunks via WebSocket**

```typescript
@SubscribeMessage('message:send')
async handleMessage(
  @ConnectedSocket() client: Socket,
  @MessageBody() payload: { sessionId: string; content: string },
): Promise<void> {
  const { sessionId, content } = payload;
  const userId = client.data.userId;

  // 1. Verify session ownership
  const session = await this.chatService.findSession(userId, sessionId);
  if (!session) {
    client.emit('error', { message: 'Session not found' });
    return;
  }

  // 2. Save user message
  await this.chatService.createMessage(sessionId, 'USER', content);

  // 3. Stream AI response
  try {
    const stream = await this.claudeService.stream({
      messages: await this.chatService.getMessageHistory(sessionId),
      systemPrompt: 'You are a helpful assistant...',
      maxTokens: 4096,
    });

    let fullResponse = '';

    // 4. Emit chunks progressively
    for await (const chunk of stream) {
      fullResponse += chunk;
      client.emit('message:chunk', { sessionId, chunk });
    }

    // 5. Get token usage from final message
    const result = await stream.finalMessage();

    // 6. Save AI message with token tracking
    const aiMessage = await this.chatService.createMessage(
      sessionId,
      'ASSISTANT',
      fullResponse,
      { inputTokens: result.inputTokens, outputTokens: result.outputTokens },
    );

    // 7. Emit completion
    client.emit('message:complete', { sessionId, message: aiMessage });
  } catch (error) {
    client.emit('error', { message: 'Failed to generate response' });
  }
}
```

### Client-Side Streaming Consumption (Next.js)

```typescript
'use client';

import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export function ChatInterface({ sessionId }: { sessionId: string }) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const [streamingChunk, setStreamingChunk] = useState('');

  useEffect(() => {
    const newSocket = io('http://localhost:3000/chat', {
      auth: { token: `Bearer ${getToken()}` },
    });

    newSocket.on('message:chunk', ({ chunk }) => {
      setStreamingChunk((prev) => prev + chunk);
    });

    newSocket.on('message:complete', ({ message }) => {
      setMessages((prev) => [...prev, message.content]);
      setStreamingChunk(''); // Clear streaming buffer
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const sendMessage = (content: string) => {
    socket?.emit('message:send', { sessionId, content });
  };

  return (
    <div>
      {messages.map((msg, i) => <div key={i}>{msg}</div>)}
      {streamingChunk && <div className="streaming">{streamingChunk}</div>}
    </div>
  );
}
```

---

## Connection Management & State Recovery

### Connection State Tracking

```typescript
@WebSocketGateway()
export class ChatGateway {
  private connections = new Map<string, Set<string>>(); // userId -> Set<socketId>

  async handleConnection(client: Socket): Promise<void> {
    const userId = client.data.userId;

    if (!this.connections.has(userId)) {
      this.connections.set(userId, new Set());
    }
    this.connections.get(userId)!.add(client.id);

    console.log(`User ${userId} connected (${this.connections.get(userId)!.size} devices)`);
  }

  async handleDisconnect(client: Socket): Promise<void> {
    const userId = client.data.userId;

    if (this.connections.has(userId)) {
      this.connections.get(userId)!.delete(client.id);

      if (this.connections.get(userId)!.size === 0) {
        this.connections.delete(userId);
        console.log(`User ${userId} fully disconnected`);
      }
    }
  }
}
```

### Reconnection Handling

**Socket.IO Client Auto-Reconnection:**

```typescript
const socket = io('http://localhost:3000/chat', {
  auth: { token: `Bearer ${getToken()}` },
  reconnection: true,
  reconnectionDelay: 1000,        // Start with 1s delay
  reconnectionDelayMax: 5000,     // Max 5s delay
  reconnectionAttempts: 10,       // Try 10 times
});

socket.on('connect', () => {
  console.log('Connected to server');
  // Re-subscribe to session after reconnection
  socket.emit('subscribe', sessionId);
});

socket.on('disconnect', (reason) => {
  if (reason === 'io server disconnect') {
    // Server forcefully disconnected (auth failure, ban, etc.)
    // Manual reconnection required
    socket.connect();
  }
  // Else: automatic reconnection will handle it
});
```

### State Recovery After Reconnection

**Problem:** User disconnects mid-stream. When they reconnect, they've missed chunks.

**Solution: Message ID + Recovery API**

```typescript
@SubscribeMessage('subscribe')
async handleSubscribe(
  @ConnectedSocket() client: Socket,
  @MessageBody() payload: { sessionId: string; lastMessageId?: string },
): Promise<void> {
  const { sessionId, lastMessageId } = payload;
  const userId = client.data.userId;

  // 1. Verify session ownership
  const session = await this.chatService.findSession(userId, sessionId);
  if (!session) {
    client.emit('error', { message: 'Session not found' });
    return;
  }

  // 2. Join room for session-specific events
  client.join(sessionId);

  // 3. If lastMessageId provided, send missed messages
  if (lastMessageId) {
    const missedMessages = await this.chatService.getMessagesSince(sessionId, lastMessageId);
    client.emit('messages:missed', { sessionId, messages: missedMessages });
  }

  client.emit('subscribed', { sessionId });
}
```

**Client-Side:**

```typescript
socket.on('connect', () => {
  const lastMessageId = localStorage.getItem(`session-${sessionId}-lastMessageId`);
  socket.emit('subscribe', { sessionId, lastMessageId });
});

socket.on('message:complete', ({ message }) => {
  localStorage.setItem(`session-${sessionId}-lastMessageId`, message.id);
});
```

---

## Scaling WebSockets with Redis

### Why Redis is Required for Horizontal Scaling

**Problem:** Each WebSocket server instance keeps connections in memory. If you have 2 instances:
- User A connects to Server 1
- User B connects to Server 2
- When User B sends a message, Server 2 cannot emit it to User A (different process)

**Solution:** Redis Pub/Sub distributes messages across all server instances.

### Redis Adapter Setup

**Installation:**

```bash
npm install @socket.io/redis-adapter redis
```

**Configuration:**

```typescript
// main.ts
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const pubClient = createClient({ url: process.env.REDIS_URL });
  const subClient = pubClient.duplicate();

  await Promise.all([pubClient.connect(), subClient.connect()]);

  const io = app.get(Server); // Get Socket.IO server instance
  io.adapter(createAdapter(pubClient, subClient));

  await app.listen(3000);
}
```

**How it Works:**

1. Server 1 emits `server.to(sessionId).emit('message:chunk', data)`
2. Redis adapter publishes event to Redis Pub/Sub channel
3. Server 2 (and all other instances) receive event from Redis
4. Server 2 emits to clients connected to it that are in the `sessionId` room

**Upstash Redis (Recommended for the project):**

```env
REDIS_URL=rediss://:password@region.upstash.io:6379
```

Upstash is serverless Redis with pay-per-request pricing (no fixed monthly cost). Ideal for MVP.

### Room-Based Routing (Critical for Multi-User Chat)

```typescript
// When user subscribes to a session
@SubscribeMessage('subscribe')
async handleSubscribe(client: Socket, sessionId: string): Promise<void> {
  client.join(sessionId); // Join room named by sessionId
}

// When broadcasting message chunks
this.server.to(sessionId).emit('message:chunk', { chunk });
```

**Benefits:**
- Messages only sent to clients subscribed to that session
- No need to track userId-to-socketId mappings manually
- Works seamlessly across Redis-scaled instances

### Sticky Sessions (Load Balancer Configuration)

**Problem:** Socket.IO handshake involves multiple HTTP requests. Without sticky sessions, requests may hit different servers, causing "Session ID unknown" HTTP 400 errors.

**Solution:** Enable sticky sessions based on `sessionId` cookie.

**Nginx Example:**

```nginx
upstream socketio {
  ip_hash; # Route same IP to same server
  server 127.0.0.1:3000;
  server 127.0.0.1:3001;
}

server {
  location /socket.io/ {
    proxy_pass http://socketio;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

**AWS ALB Example:**

Enable **sticky sessions** in target group settings:
- Stickiness type: Application-based cookie
- Duration: 86400 seconds (24 hours)

### Redis Sharded Adapter (2026 Recommendation)

For Redis 7.0+, use sharded Pub/Sub for better performance:

```bash
npm install @socket.io/redis-sharded-adapter
```

```typescript
import { createShardedAdapter } from '@socket.io/redis-sharded-adapter';

const adapter = createShardedAdapter(pubClient, subClient);
io.adapter(adapter);
```

**Benefits:**
- Reduces Redis CPU usage by 30-50% at scale
- Better message distribution across cluster

---

## Event-Driven Multi-Agent Orchestration

### Pattern: Pipeline Events via Internal Emitter

For the project Deep Dive chat with Session Facilitator → Psychologists → Wise Friend pipeline:

```typescript
import { EventEmitter2 } from '@nestjs/event-emitter';

@Injectable()
export class ChatPipelineService {
  constructor(
    private readonly eventEmitter: EventEmitter2,
    private readonly sessionFacilitator: SessionFacilitatorAgent,
    private readonly herPsychologist: HerPsychologistAgent,
    private readonly hisPsychologist: HisPsychologistAgent,
    private readonly wiseFriend: WiseFriendAgent,
  ) {}

  async processMessage(sessionId: string, userMessage: string): Promise<void> {
    // Stage 1: Session Facilitator
    this.eventEmitter.emit('pipeline.stage', { sessionId, stage: 'facilitator' });
    const facilitatorOutput = await this.sessionFacilitator.analyze(userMessage);

    if (!facilitatorOutput.hasEnoughContext) {
      this.eventEmitter.emit('pipeline.complete', {
        sessionId,
        response: facilitatorOutput.nextQuestion,
      });
      return;
    }

    // Stage 2: Psychologists (parallel)
    this.eventEmitter.emit('pipeline.stage', { sessionId, stage: 'psychologists' });
    const [herAnalysis, hisAnalysis] = await Promise.all([
      this.herPsychologist.analyze(facilitatorOutput.contextSummary),
      this.hisPsychologist.analyze(facilitatorOutput.contextSummary),
    ]);

    // Stage 3: Wise Friend (streaming)
    this.eventEmitter.emit('pipeline.stage', { sessionId, stage: 'wise-friend' });
    const stream = await this.wiseFriend.synthesize({
      herAnalysis,
      hisAnalysis,
      context: facilitatorOutput.contextSummary,
    });

    for await (const chunk of stream) {
      this.eventEmitter.emit('pipeline.chunk', { sessionId, chunk });
    }

    this.eventEmitter.emit('pipeline.complete', { sessionId });
  }
}
```

**Gateway Listens to Pipeline Events:**

```typescript
@WebSocketGateway()
export class ChatGateway implements OnModuleInit {
  constructor(private readonly eventEmitter: EventEmitter2) {}

  onModuleInit() {
    this.eventEmitter.on('pipeline.stage', ({ sessionId, stage }) => {
      this.server.to(sessionId).emit('pipeline:stage', { stage });
    });

    this.eventEmitter.on('pipeline.chunk', ({ sessionId, chunk }) => {
      this.server.to(sessionId).emit('message:chunk', { chunk });
    });

    this.eventEmitter.on('pipeline.complete', ({ sessionId }) => {
      this.server.to(sessionId).emit('message:complete', {});
    });
  }
}
```

**Benefits:**
- Decouples pipeline logic from WebSocket gateway
- Pipeline can be tested independently
- Easy to add progress indicators (e.g., "Her Psychologist analyzing...")

---

## Error Handling & Resilience

### Categorized Error Handling

```typescript
@SubscribeMessage('message:send')
async handleMessage(client: Socket, payload: any): Promise<void> {
  try {
    // Process message
  } catch (error) {
    if (error instanceof UnauthorizedException) {
      // Authentication issue
      client.emit('error', { type: 'AUTH_ERROR', message: 'Session expired' });
      client.disconnect();
    } else if (error instanceof NotFoundException) {
      // Session not found
      client.emit('error', { type: 'NOT_FOUND', message: 'Session not found' });
    } else if (error instanceof RateLimitException) {
      // Rate limit exceeded
      client.emit('error', { type: 'RATE_LIMIT', message: 'Too many requests' });
    } else {
      // Internal server error
      client.emit('error', { type: 'INTERNAL_ERROR', message: 'Something went wrong' });
      console.error('Unhandled error in WebSocket:', error);
    }
  }
}
```

### Timeout Handling for LLM Streaming

```typescript
async handleMessage(client: Socket, payload: any): Promise<void> {
  const timeout = setTimeout(() => {
    client.emit('error', { type: 'TIMEOUT', message: 'Request timed out after 30s' });
  }, 30000); // 30 second timeout

  try {
    // Process message with streaming
  } finally {
    clearTimeout(timeout);
  }
}
```

### Graceful Shutdown

```typescript
// main.ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  process.on('SIGTERM', async () => {
    console.log('SIGTERM received, closing WebSocket server...');
    const server = app.get(Server);

    // Notify clients before disconnect
    server.emit('server:shutdown', { message: 'Server restarting, please reconnect' });

    await new Promise((resolve) => setTimeout(resolve, 1000)); // Give clients 1s to receive
    await app.close();
  });

  await app.listen(3000);
}
```

---

## Testing WebSocket Gateways

### Unit Testing with Mocked Socket

```typescript
// chat.gateway.spec.ts
import { Test } from '@nestjs/testing';
import { ChatGateway } from './chat.gateway';
import { Socket } from 'socket.io';

describe('ChatGateway', () => {
  let gateway: ChatGateway;
  let mockSocket: Partial<Socket>;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [ChatGateway, MockChatService, MockJwtService],
    }).compile();

    gateway = module.get(ChatGateway);

    mockSocket = {
      id: 'test-socket-id',
      data: { userId: 'user-123' },
      emit: jest.fn(),
      join: jest.fn(),
      disconnect: jest.fn(),
    };
  });

  it('should handle message send', async () => {
    await gateway.handleMessage(mockSocket as Socket, {
      sessionId: 'session-123',
      content: 'Hello',
    });

    expect(mockSocket.emit).toHaveBeenCalledWith('message:chunk', expect.any(Object));
  });
});
```

### Integration Testing with Real Socket.IO Client

```typescript
// chat.gateway.e2e-spec.ts
import { io, Socket } from 'socket.io-client';

describe('ChatGateway (e2e)', () => {
  let client: Socket;

  beforeAll((done) => {
    client = io('http://localhost:3000/chat', {
      auth: { token: 'Bearer test-jwt-token' },
    });

    client.on('connect', done);
  });

  afterAll(() => {
    client.close();
  });

  it('should receive message chunks', (done) => {
    const chunks: string[] = [];

    client.on('message:chunk', ({ chunk }) => {
      chunks.push(chunk);
    });

    client.on('message:complete', () => {
      expect(chunks.length).toBeGreaterThan(0);
      done();
    });

    client.emit('message:send', { sessionId: 'test-session', content: 'Hello' });
  });
});
```

---

## Performance Considerations

### Connection Limits

| Infrastructure | Concurrent Connections | Cost |
|----------------|------------------------|------|
| Single Node.js instance (2GB RAM) | ~10,000 | Free (self-hosted) |
| Cluster (4 instances + Redis) | ~40,000 | ~$200/month (managed Redis) |
| Cloud-managed (AWS ALB + ECS) | 100,000+ | ~$500-1000/month |

**the project MVP Target:** 1,000-10,000 concurrent users → Single instance + Upstash Redis sufficient.

### Memory Management

```typescript
// Limit connection lifetime to prevent memory leaks
const CONNECTION_MAX_AGE = 24 * 60 * 60 * 1000; // 24 hours

async handleConnection(client: Socket): Promise<void> {
  setTimeout(() => {
    client.emit('server:timeout', { message: 'Connection expired, please reconnect' });
    client.disconnect();
  }, CONNECTION_MAX_AGE);
}
```

### Message Rate Limiting

```typescript
import { RateLimiterMemory } from 'rate-limiter-flexible';

const rateLimiter = new RateLimiterMemory({
  points: 10, // 10 messages
  duration: 60, // per 60 seconds
});

@SubscribeMessage('message:send')
async handleMessage(client: Socket, payload: any): Promise<void> {
  const userId = client.data.userId;

  try {
    await rateLimiter.consume(userId);
    // Process message
  } catch (error) {
    client.emit('error', { type: 'RATE_LIMIT', message: 'Too many messages' });
  }
}
```

---

## Project Integration (the project Chat Module)

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Next.js Frontend (Vercel)                  │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ChatInterface Component ('use client')            │    │
│  │  - Socket.IO client connection                     │    │
│  │  - JWT from localStorage/cookie                    │    │
│  │  - Progressive chunk rendering                     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓ WebSocket (Socket.IO)
┌─────────────────────────────────────────────────────────────┐
│              NestJS API (Railway/Fly.io + Upstash)          │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ChatGateway (@WebSocketGateway)                   │    │
│  │  - JWT auth via WsAuthAdapter                      │    │
│  │  - Room-based routing (socket.join(sessionId))     │    │
│  │  - Listen to EventEmitter2 pipeline events         │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ChatPipelineService                               │    │
│  │  - Session Facilitator → Psychologists → Wise Friend│   │
│  │  - Emit pipeline.chunk events                      │    │
│  │  - Integrate MemoryService for context             │    │
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
│  - Socket.IO adapter for horizontal scaling                │
│  - Pay-per-request (no fixed monthly cost)                 │
└─────────────────────────────────────────────────────────────┘
```

### Environment Variables

```env
# apps/api/.env
FRONTEND_URL=http://localhost:3000
REDIS_URL=rediss://:password@region.upstash.io:6379
ANTHROPIC_API_KEY=sk-ant-xxx

# apps/web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_WS_URL=ws://localhost:3001
```

### Key Implementation Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Transport Protocol** | Socket.IO | Auto-reconnection, rooms, Redis adapter built-in |
| **Authentication** | JWT via handshake (WsAuthAdapter) | Validate once, trust connection thereafter |
| **Streaming Pattern** | Claude SSE → WebSocket chunks | Real-time progressive rendering |
| **Scaling Strategy** | Redis Pub/Sub adapter | Horizontal scaling for 10K+ users |
| **Error Recovery** | Client auto-reconnect + message recovery API | Resume after network failure |
| **Multi-Agent Events** | EventEmitter2 → Gateway listeners | Decouple pipeline from transport layer |
| **Rate Limiting** | 10 messages/minute per user | Prevent abuse |

---

## Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| **Authenticating on every message** | Tokens expire mid-conversation | Authenticate on connection only |
| **No sticky sessions with load balancer** | HTTP 400 "Session ID unknown" | Enable sticky sessions (ip_hash, cookies) |
| **Forgetting to join rooms** | Messages broadcast to all clients | Always `client.join(sessionId)` on subscribe |
| **No reconnection logic** | Users lose connection on network blip | Use Socket.IO auto-reconnect + recovery API |
| **Blocking event loop with sync operations** | Gateway becomes unresponsive | Use async/await for all I/O operations |
| **Not tracking connection state** | Cannot limit concurrent connections | Maintain userId → Set<socketId> map |
| **Ignoring graceful shutdown** | Connections abruptly closed on deploy | Emit `server:shutdown` event before close |

---

## Sources

- [WebSocket Authentication in NestJS: Handling JWT and Guards](https://dev.to/mouloud_hasrane_c99b0f49a/websocket-authentication-in-nestjs-handling-jwt-and-guards-4j27)
- [The Best Way to Authenticate WebSockets in NestJS](https://preetmishra.com/blog/the-best-way-to-authenticate-websockets-in-nestjs)
- [Securing Socket.IO in NestJS with JWT and Passport](https://node.kumarchaudhary.com.np/securing-socketio-in-nestjs-with-jwt-and-passport-a-comprehensive-guide)
- [Streaming Messages - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [The Complete Guide to Streaming LLM Responses in Web Applications](https://dev.to/hobbada/the-complete-guide-to-streaming-llm-responses-in-web-applications-from-sse-to-real-time-ui-3534)
- [Scaling socket.io with NestJS or NodeJS and Redis using Pub/Sub model](https://medium.com/@case3/scaling-socket-io-with-nestjs-or-nodejs-and-redis-using-pub-sub-model-c6ef8ea7dad8)
- [WebSockets at Scale: Real-Time Architectures with NestJS and Redis Pub/Sub](https://praeclarumtech.com/websockets-at-scale-real-time-architectures-with-nestjs-and-redis-pub-sub/)
- [Clustering and scaling Socket.io server using Node.js, Nest.js and Redis](https://medium.com/@mohsenmahoski/clustering-and-scaling-socket-io-server-using-node-js-nest-js-and-redis-43e8e67847b7)
- [Scalable WebSockets with NestJS and Redis - LogRocket](https://blog.logrocket.com/scalable-websockets-with-nestjs-and-redis/)
- [Redis adapter | Socket.IO](https://socket.io/docs/v4/redis-adapter/)
- [Socket.io vs WebSockets vs Server-Sent Events: Real-Time Communication Comparison 2026](https://www.index.dev/skill-vs-skill/socketio-vs-websockets-vs-server-sent-events)
- [Comprehensive WebSocket Connection Management in NestJS](https://medium.com/@avijitbera775/comprehensive-websocket-connection-management-in-nestjs-building-scalable-real-time-applications-dc6808015b1b)
- [Building a Production-Ready Real-Time Notification System in NestJS](https://medium.com/@marufpulok98/building-a-production-ready-real-time-notification-system-in-nestjs-websockets-redis-offline-6cc2f1bd0b05)
- [NestJS WebSockets - Gateways](https://docs.nestjs.com/websockets/gateways)
- [NestJS WebSockets - Adapter](https://docs.nestjs.com/websockets/adapter)
