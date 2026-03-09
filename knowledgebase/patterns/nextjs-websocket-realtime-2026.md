---
title: Next.js WebSocket Integration for Real-Time Dashboards (2026)
domain: pattern
tech: [nextjs, react, websocket, typescript, nodejs]
area: [real-time, app-router, server-components, dashboard]
staleness: 6months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://github.com/apteryxxyz/next-ws
  - https://medium.com/@saadiqbalch786/implementing-web-sockets-with-next-js-and-api-routes-a-guide-d4143e3edcb0
  - https://github.com/vercel/next.js/discussions/14950
  - https://fly.io/javascript-journal/websockets-with-nextjs/
  - https://ably.com/blog/realtime-chat-app-nextjs-vercel
  - https://arnab-k.medium.com/websocket-implementations-in-next-js-d58a1b79d923
  - https://dev.to/franciscomendes10866/building-real-time-applications-with-nextjs-and-websockets-588j
---

# Next.js WebSocket Integration for Real-Time Dashboards (2026)

## Overview

WebSocket integration in Next.js App Router requires understanding the distinction between Server Components and Client Components, as WebSocket connections are inherently client-side. This guide covers strategies for building real-time dashboards that consume WebSocket data from external servers (like Home Assistant).

## App Router vs Pages Router

**Key Difference:**
- **Pages Router**: Can use API routes with custom server (express, ws)
- **App Router**: Uses Route Handlers, requires patching or external solutions for WebSockets

**Recommendation:** Use **next-ws** for App Router or consume external WebSocket servers from Client Components.

## Architecture Patterns

### Pattern 1: Client-Side WebSocket (Recommended for External Servers)

**Best for:** Consuming data from external WebSocket servers (Home Assistant, Socket.IO backends, etc.)

```tsx
'use client';

import { useEffect, useState } from 'react';

export function BatteryDashboard() {
  const [batteryData, setBatteryData] = useState(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Connect to external WebSocket server (e.g., Home Assistant)
    const websocket = new WebSocket('ws://localhost:8123/api/websocket');

    websocket.onopen = () => {
      console.log('Connected to Home Assistant');
      // Authenticate
      websocket.send(JSON.stringify({
        type: 'auth',
        access_token: process.env.NEXT_PUBLIC_HA_TOKEN
      }));
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'event') {
        // Handle battery state updates
        if (message.event.event_type === 'state_changed') {
          const entity_id = message.event.data.entity_id;
          if (entity_id === 'sensor.battery_soc') {
            setBatteryData(message.event.data.new_state);
          }
        }
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('Disconnected. Reconnecting in 5s...');
      setTimeout(() => {
        // Reconnect logic
      }, 5000);
    };

    setWs(websocket);

    // Cleanup on unmount
    return () => {
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.close();
      }
    };
  }, []);

  if (!batteryData) return <div>Connecting...</div>;

  return (
    <div className="glass-card">
      <h2>Battery SOC: {batteryData.state}%</h2>
    </div>
  );
}
```

**Pros:**
- ✅ Works on any hosting platform (Vercel, Netlify, etc.)
- ✅ Simple, no Next.js patching required
- ✅ Follows React hooks patterns

**Cons:**
- ❌ No server-side fallback (requires JS enabled)
- ❌ Exposes WebSocket URL/token to client

---

### Pattern 2: next-ws (For Self-Hosted WebSocket Servers)

**Best for:** Running your own WebSocket server within Next.js

**Installation:**

```bash
npm install next-ws ws
```

**Setup in package.json:**

```json
{
  "scripts": {
    "prepare": "next-ws patch"
  }
}
```

**API Route Handler:**

```typescript
// app/api/ws/route.ts
import type { NextRequest } from 'next/server';
import type { WebSocket, WebSocketServer } from 'ws';

export function UPGRADE(
  client: WebSocket,
  server: WebSocketServer,
  request: NextRequest,
  context: { params: unknown }
) {
  client.on('message', (message) => {
    console.log('Received:', message.toString());

    // Echo back
    client.send(JSON.stringify({
      type: 'battery_update',
      data: { soc: 85, voltage: 54.2 }
    }));
  });

  client.once('close', () => {
    console.log('Client disconnected');
  });

  client.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
}
```

**Client Component:**

```tsx
'use client';

import { useEffect, useState } from 'react';

export function LiveBatteryStatus() {
  const [soc, setSoc] = useState(0);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:3000/api/ws');

    ws.onopen = () => {
      ws.send(JSON.stringify({ type: 'subscribe', entity: 'battery' }));
    };

    ws.onmessage = (event) => {
      const { type, data } = JSON.parse(event.data);
      if (type === 'battery_update') {
        setSoc(data.soc);
      }
    };

    return () => ws.close();
  }, []);

  return <div>SOC: {soc}%</div>;
}
```

**Pros:**
- ✅ Self-contained (no external server needed)
- ✅ Can proxy/transform data before sending to clients

**Cons:**
- ❌ **NOT compatible with Vercel/serverless** (requires persistent server)
- ❌ Requires patching Next.js (maintenance burden)
- ❌ App Router only (no Pages Router support)

---

### Pattern 3: Server-Sent Events (SSE) Alternative

**Best for:** One-way real-time updates (server → client)

SSE works on serverless platforms unlike WebSockets.

```typescript
// app/api/battery-stream/route.ts
export async function GET(request: Request) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      // Simulate battery updates every 2 seconds
      const interval = setInterval(() => {
        const data = JSON.stringify({
          soc: Math.random() * 100,
          timestamp: Date.now()
        });

        controller.enqueue(
          encoder.encode(`data: ${data}\n\n`)
        );
      }, 2000);

      // Cleanup
      request.signal.addEventListener('abort', () => {
        clearInterval(interval);
        controller.close();
      });
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    }
  });
}
```

**Client:**

```tsx
'use client';

import { useEffect, useState } from 'react';

export function SSEBatteryStatus() {
  const [soc, setSoc] = useState(0);

  useEffect(() => {
    const eventSource = new EventSource('/api/battery-stream');

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setSoc(data.soc);
    };

    return () => eventSource.close();
  }, []);

  return <div>SOC: {soc}%</div>;
}
```

**Pros:**
- ✅ Works on Vercel/serverless (respects function timeout)
- ✅ Simpler than WebSockets (HTTP-based)
- ✅ Auto-reconnects on connection loss

**Cons:**
- ❌ One-way only (can't send data from client → server)
- ❌ Less efficient than WebSockets for bidirectional communication

---

## Server Components vs Client Components

**Critical Rule:** WebSocket connections REQUIRE Client Components.

```tsx
// ❌ WRONG: Server Component with WebSocket
export default function Dashboard() {
  const ws = new WebSocket('ws://localhost:8123'); // ERROR: window is not defined
  return <div>...</div>;
}

// ✅ CORRECT: Client Component
'use client';

export default function Dashboard() {
  const ws = new WebSocket('ws://localhost:8123'); // Works
  return <div>...</div>;
}
```

**Hybrid Pattern (Recommended):**

```tsx
// app/dashboard/page.tsx (Server Component)
export default function DashboardPage() {
  return (
    <div>
      <h1>Battery Dashboard</h1>
      {/* Server-rendered static content */}
      <StaticBatteryInfo />

      {/* Client-side live updates */}
      <LiveBatteryStatus />
    </div>
  );
}

// components/LiveBatteryStatus.tsx (Client Component)
'use client';

export function LiveBatteryStatus() {
  // WebSocket logic here
}
```

**Benefits:**
- ⚡ Fast initial render (Server Component)
- 🔄 Real-time updates (Client Component)
- 📦 Smaller JS bundle (only Client Component shipped to browser)

---

## Deployment Considerations

### Vercel / Serverless Platforms

**WebSocket Limitations:**
- ❌ Vercel serverless functions have **10-second timeout** (Hobby), **60 seconds** (Pro)
- ❌ Cannot maintain persistent WebSocket connections
- ❌ `next-ws` **does NOT work** on Vercel

**Solutions:**
1. **Use external WebSocket server** (Pattern 1)
   - Host WebSocket server separately (Home Assistant, Railway, Fly.io)
   - Connect from Client Components
2. **Use third-party services**
   - Ably, Pusher, Socket.IO managed hosting
   - Vercel Edge Functions can proxy messages
3. **Switch to SSE** (Pattern 3)
   - Works within serverless function timeout
   - One-way communication only

### Self-Hosted / VPS (Fly.io, Railway, DigitalOcean)

**WebSocket Support:**
- ✅ `next-ws` works perfectly
- ✅ Full WebSocket server capabilities
- ✅ No timeout limitations

**Deployment:**

```dockerfile
# Dockerfile for Next.js with WebSockets
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

**Docker Compose:**

```yaml
services:
  nextjs-dashboard:
    build: .
    ports:
      - "3000:3000"
    environment:
      - HA_WEBSOCKET_URL=ws://homeassistant:8123/api/websocket
    restart: unless-stopped
```

---

## Best Practices

### 1. Auto-Reconnect Logic

```tsx
'use client';

import { useEffect, useRef, useState } from 'react';

function useWebSocket(url: string) {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    function connect() {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('Connected');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        setData(JSON.parse(event.data));
      };

      ws.onclose = () => {
        console.log('Disconnected. Reconnecting in 5s...');
        setIsConnected(false);
        reconnectTimeoutRef.current = setTimeout(connect, 5000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
      };

      wsRef.current = ws;
    }

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      wsRef.current?.close();
    };
  }, [url]);

  return { data, isConnected };
}

export function BatteryDashboard() {
  const { data, isConnected } = useWebSocket('ws://localhost:8123/api/websocket');

  return (
    <div>
      <StatusIndicator connected={isConnected} />
      {data && <BatteryCard data={data} />}
    </div>
  );
}
```

### 2. Graceful Degradation

Provide fallback for when WebSocket fails:

```tsx
'use client';

export function BatteryDashboard() {
  const { data, isConnected } = useWebSocket('ws://...');
  const [fallbackData, setFallbackData] = useState(null);

  // Fallback: poll REST API every 10s if WebSocket disconnected
  useEffect(() => {
    if (!isConnected) {
      const interval = setInterval(async () => {
        const res = await fetch('/api/battery');
        const data = await res.json();
        setFallbackData(data);
      }, 10000);

      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const displayData = isConnected ? data : fallbackData;

  return <BatteryCard data={displayData} />;
}
```

### 3. Environment-Aware URLs

```tsx
// lib/websocket-url.ts
export function getWebSocketURL(): string {
  if (typeof window === 'undefined') {
    // Server-side (should not happen for WebSockets)
    return '';
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = process.env.NEXT_PUBLIC_HA_HOST || 'localhost:8123';

  return `${protocol}//${host}/api/websocket`;
}
```

### 4. TypeScript Types

```typescript
// types/battery.ts
export interface BatteryState {
  soc: number;
  voltage: number;
  current: number;
  power: number;
  temperature: number;
  timestamp: string;
}

export interface WebSocketMessage {
  type: 'auth' | 'auth_ok' | 'event' | 'subscribe';
  event?: {
    event_type: string;
    data: {
      entity_id: string;
      new_state: BatteryState;
    };
  };
}
```

---

## Home Assistant Specific Implementation

### Authentication Flow

```tsx
'use client';

import { useEffect, useState } from 'react';

export function useHomeAssistantWebSocket() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8123/api/websocket');
    let messageId = 1;

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      // Step 1: Receive auth_required
      if (message.type === 'auth_required') {
        websocket.send(JSON.stringify({
          type: 'auth',
          access_token: process.env.NEXT_PUBLIC_HA_TOKEN
        }));
      }

      // Step 2: Receive auth_ok
      if (message.type === 'auth_ok') {
        setAuthenticated(true);

        // Step 3: Subscribe to state changes
        websocket.send(JSON.stringify({
          id: messageId++,
          type: 'subscribe_events',
          event_type: 'state_changed'
        }));
      }

      // Step 4: Handle events
      if (message.type === 'event') {
        const entity_id = message.event.data.entity_id;
        if (entity_id.startsWith('sensor.battery_')) {
          // Handle battery sensor updates
        }
      }
    };

    setWs(websocket);

    return () => websocket.close();
  }, []);

  return { ws, authenticated };
}
```

---

## Performance Considerations

### 1. Debounce Rapid Updates

```tsx
import { useEffect, useState, useRef } from 'react';
import { debounce } from 'lodash';

function useDebouncedWebSocket(url: string, delay: number = 500) {
  const [data, setData] = useState(null);
  const debouncedSetData = useRef(debounce(setData, delay)).current;

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      debouncedSetData(parsed); // Debounce rapid updates
    };

    return () => {
      ws.close();
      debouncedSetData.cancel();
    };
  }, [url]);

  return data;
}
```

### 2. Selective Subscriptions

Only subscribe to entities you need:

```tsx
// Subscribe to specific sensors
websocket.send(JSON.stringify({
  id: 1,
  type: 'subscribe_trigger',
  trigger: {
    platform: 'state',
    entity_id: ['sensor.battery_soc', 'sensor.battery_voltage']
  }
}));
```

### 3. Connection Status Indicator

```tsx
function ConnectionStatus({ isConnected }: { isConnected: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${
        isConnected ? 'bg-green-500' : 'bg-red-500'
      }`} />
      <span className="text-sm text-gray-400">
        {isConnected ? 'Live' : 'Reconnecting...'}
      </span>
    </div>
  );
}
```

---

## Project Integration (task-020)

### Recommended Approach

**For Home Battery Dashboard:**

1. **Use Pattern 1** (Client-Side WebSocket to Home Assistant)
2. **Deploy on Vercel** (or any static host)
3. **Fallback to REST API** if WebSocket fails
4. **Use Tailscale** for remote access (already configured in project)

**Architecture:**

```
┌─────────────────────────────────────────┐
│         Next.js Dashboard (Vercel)      │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ Server Components (Static)        │  │
│  │ - Layout, Nav, Initial UI         │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ Client Component (WebSocket)      │  │
│  │ 'use client'                      │  │
│  │                                   │  │
│  │  useHomeAssistantWebSocket()      │  │
│  │   ↓                               │  │
│  │  ws://localhost:8123 (Tailscale)  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                  ↓
    WebSocket connection via Tailscale
                  ↓
┌─────────────────────────────────────────┐
│   Home Assistant (Docker on MacBook)    │
│   ws://localhost:8123/api/websocket     │
└─────────────────────────────────────────┘
```

---

## Sources

- [next-ws: WebSockets inside Next.js app routes](https://github.com/apteryxxyz/next-ws)
- [Implementing Web Sockets with Next.js and API Routes](https://medium.com/@saadiqbalch786/implementing-web-sockets-with-next-js-and-api-routes-a-guide-d4143e3edcb0)
- [Next.js + WebSocket / Real-time examples](https://github.com/vercel/next.js/discussions/14950)
- [Using WebSockets with Next.js on Fly.io](https://fly.io/javascript-journal/websockets-with-nextjs/)
- [Building a realtime chat app with Next.js and Vercel](https://ably.com/blog/realtime-chat-app-nextjs-vercel)
- [WebSocket implementations in Next.js](https://arnab-k.medium.com/websocket-implementations-in-next-js-d58a1b79d923)
- [Building Real-Time Next.js Apps with WebSockets and Soketi](https://dev.to/franciscomendes10866/building-real-time-applications-with-nextjs-and-websockets-588j)
