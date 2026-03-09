---
title: MCP Server Implementation Patterns and Best Practices
domain: library
tech: [typescript, nodejs, mcp, sdk]
area: [mcp, knowledge-management, server-development]
staleness: 3months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://github.com/modelcontextprotocol/typescript-sdk
  - https://modelcontextprotocol.io/docs/develop/build-server
  - https://github.com/modelcontextprotocol/servers
  - https://github.com/bsmi021/mcp-file-operations-server
  - https://github.com/ftaricano/mcp-notion
  - https://modelcontextprotocol.io/specification/2025-06-18/schema
  - https://www.builder.io/blog/best-mcp-servers-2026
  - https://mcpcat.io/guides/error-handling-custom-mcp-servers/
  - https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices
---

# MCP Server Implementation Patterns and Best Practices

Research for evaluating whether to migrate the research agent into an MCP (Model Context Protocol) server. This document covers TypeScript SDK patterns, real-world examples, tool/resource/prompt definitions, error handling, and testing strategies.

## Overview

The Model Context Protocol (MCP) allows applications to provide context for LLMs in a standardized way, separating the concerns of providing context from the actual LLM interaction. MCP servers can expose three main capabilities: **Resources** (file-like data), **Tools** (callable functions), and **Prompts** (reusable templates).

## 1. MCP TypeScript SDK

### Installation & Setup

```bash
npm install @modelcontextprotocol/sdk zod@3
npm install -D @types/node typescript
```

**Key Files:**
- `@modelcontextprotocol/sdk` - Core SDK package
- `zod@3` - Required peer dependency for schema validation (supports v3.25+)

**Project Structure (Monorepo):**
```
packages/
├── @modelcontextprotocol/server     # Server libraries
├── @modelcontextprotocol/client     # Client libraries
├── @modelcontextprotocol/express    # Express middleware
├── @modelcontextprotocol/hono       # Hono middleware
└── @modelcontextprotocol/node       # Node.js utilities

docs/
├── server.md      # Server implementation guide
├── client.md      # Client implementation guide
├── capabilities.md # Sampling, elicitation, experimental features
└── faq.md         # Troubleshooting

examples/
├── server/        # Runnable server examples
└── client/        # Runnable client examples
```

### Basic Server Initialization

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create server instance
const server = new McpServer({
  name: "my-server",
  version: "1.0.0",
});

// Register capabilities (tools, resources, prompts)
// ... (see sections below)

// Start server with stdio transport
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
```

**Key Patterns:**
- Use `console.error()` for logging (NOT `console.log()`) to avoid corrupting JSON-RPC messages on stdout
- Server initialization includes name, version, and capabilities
- Transports: stdio (standard I/O) or Streamable HTTP

### Version Roadmap

- **v1.x**: Current stable version (recommended for production)
- **v2.x**: Anticipated Q1 2026 (stable release expected)

## 2. Real-World MCP Server Examples

### Example 1: File Operations Server (bsmi021/mcp-file-operations-server)

**Purpose:** Enhanced file operation capabilities with streaming, patching, and change tracking

**Architecture:**
```
src/
├── index.ts         # Main server entry
├── tools/           # Tool implementations
├── resources/       # Resource handlers
├── utils/           # Helpers (validation, sanitization)
└── security/        # Access controls
```

**Key Features:**
- Basic operations: copy, read, write, move, delete
- Directory operations with progress reporting
- File watching with change tracking
- Dual transport: stdio and HTTP (port 3001)

**Tool Categories:**
```typescript
// Basic file operations
server.registerTool("copy_file", {...});
server.registerTool("read_file", {...});
server.registerTool("write_file", {...});

// Directory operations
server.registerTool("make_directory", {...});
server.registerTool("copy_directory", {...}); // with progress

// Watch operations
server.registerTool("watch_directory", {...});
server.registerTool("unwatch_directory", {...});

// Change tracking
server.registerTool("get_changes", {...});
server.registerTool("clear_changes", {...});
```

**Resource Patterns:**
```typescript
// URI-based resource templates
file://{path}              // Access file contents
metadata://{path}          // File metadata
directory://{path}         // Directory listing
file:///recent-changes     // Static resource (operation history)
```

**Security:**
- Path validation (no `../` traversal)
- Rate limiting with retry-after periods
- Input sanitization on all parameters
- Safe resource cleanup

**Configuration:**
```bash
# Environment variables
MCP_TRANSPORT=stdio|http  # Default: stdio

# NPM scripts
npm start            # Stdio mode
npm run start:http   # HTTP mode (port 3001)
npm run dev          # Dev with auto-reload
```

### Example 2: Notion Knowledge Management (ftaricano/mcp-notion)

**Purpose:** Comprehensive Notion API integration for knowledge management

**Architecture:**
```
src/
├── index.ts         # Main MCP server entry
├── tools/           # Page operation implementations
├── utils/           # Block creation, rich text, templates
├── config/          # Configuration management
├── security/        # Token validation, rate limiting
└── cache/           # Caching layer (60%+ hit rate)
```

**Knowledge Organization:**
- **Pages**: Atomic units with metadata and content blocks
- **Templates**: Reusable patterns (meeting notes, project plans, bug tracking)
- **Block types**: Headings, paragraphs, lists, callouts, code, quotes, dividers
- **Localization**: Portuguese support

**Tools (10 total):**
```typescript
// Basic operations
search_pages             // Full-text discovery
get_page                 // Retrieve page
get_page_content         // Get content blocks
create_page              // Basic creation
update_page              // Modification

// Enhanced operations
create_rich_page         // Multi-block composition
create_page_from_template // Template instantiation
add_content_blocks       // Incremental content
list_templates           // Template discovery
create_root_page         // Workspace-level creation
```

**Resource Patterns:**
- Environment-based secrets (`NOTION_TOKEN`)
- Retry mechanics: 3 attempts with exponential backoff
- Rate limiting: 60 requests/minute (Notion API constraint)
- Error classification: temporary, permanent, auth, rate-limit
- Audit logging for compliance

**Configuration:**
```typescript
// Hot-reloadable config
{
  "secrets": "environment", // or "config-file"
  "cache": {
    "enabled": true,
    "ttl": 3600
  },
  "rateLimit": {
    "requests": 60,
    "window": 60000
  }
}
```

### Example 3: Memory Server (Official modelcontextprotocol/servers)

**Purpose:** Knowledge graph-based persistent memory system

**Architecture:**
- Graph-based relationships (not flat storage)
- Contextual retrieval and reasoning
- Persistent storage across sessions

**Pattern:** Structures data as interconnected nodes enabling semantic search

### Example 4: Filesystem Server (Official)

**Purpose:** Secure file operations with configurable access controls

**Key Pattern:**
- Permission boundaries prevent unauthorized traversal
- Configurable allowed paths via NPX arguments

```bash
npx @modelcontextprotocol/server-filesystem --allow-dir /path/to/workspace
```

### Example 5: Everything Server (Official)

**Purpose:** Reference/test server demonstrating all MCP capabilities

**Features:**
- Prompts: Reusable templates
- Resources: Static and dynamic data
- Tools: Executable functions
- Combined search, retrieval, and invocation patterns

## 3. Tool Definition Patterns

### Input Schema with Zod

MCP uses JSON Schema for tool input validation, with Zod providing runtime validation and TypeScript types:

```typescript
import { z } from "zod";

server.registerTool(
  "search_knowledge_base",
  {
    description: "Search the knowledge base for relevant information",
    inputSchema: {
      query: z
        .string()
        .min(2)
        .describe("Search query (minimum 2 characters)"),
      domain: z
        .enum(["integration", "library", "protocol", "pattern", "troubleshooting"])
        .optional()
        .describe("Filter by domain category"),
      limit: z
        .number()
        .int()
        .min(1)
        .max(50)
        .default(10)
        .describe("Maximum number of results"),
    },
  },
  async ({ query, domain, limit }) => {
    // Implementation
    const results = await searchKnowledgeBase(query, domain, limit);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(results, null, 2),
        },
      ],
    };
  },
);
```

### Schema Best Practices

**Keep Schemas Flat:**
- Avoid deep nesting (increases token count and LLM cognitive load)
- Use simple types when possible

**Required vs Optional:**
- Parameters in `required` array prompt LLMs to ask for clarification if missing
- Optional parameters allow graceful degradation

**Clear Descriptions:**
- Descriptions are sent to the LLM as instructions
- Be specific about formats, constraints, and examples

**Example (from weather server):**
```typescript
server.registerTool(
  "get_forecast",
  {
    description: "Get weather forecast for a location",
    inputSchema: {
      latitude: z
        .number()
        .min(-90)
        .max(90)
        .describe("Latitude of the location"),
      longitude: z
        .number()
        .min(-180)
        .max(180)
        .describe("Longitude of the location"),
    },
  },
  async ({ latitude, longitude }) => {
    // Fetch forecast logic
    const forecast = await getForecast(latitude, longitude);

    return {
      content: [
        { type: "text", text: forecast }
      ],
    };
  },
);
```

### Error Handling in Tools

**Application-level errors should be returned in the result, NOT as MCP protocol errors:**

```typescript
server.registerTool(
  "perform_operation",
  { /* schema */ },
  async (params) => {
    try {
      const result = performOperation(params);
      return {
        content: [
          { type: "text", text: `Success: ${result}` }
        ],
      };
    } catch (error) {
      // Return error in result (LLM can see and handle it)
      return {
        isError: true,
        content: [
          { type: "text", text: `Error: ${error.message}` }
        ],
      };
    }
  },
);
```

**When to use MCP protocol errors:**
- JSON-RPC 2.0 violations (malformed JSON, invalid parameters)
- Transport-level errors (network timeouts, broken pipes)
- Authentication failures

## 4. Resource Definition Patterns

### Resource URI Patterns

Resources are identified by URIs following the pattern: `[protocol]://[host]/[path]`

**Examples:**
```typescript
// File resources
file:///workspace/src/main.js
file://{path}                    // Template with parameter

// Knowledge base resources
knowledge://integrations/telegram-grammy.md
knowledge://{domain}/{slug}      // Template pattern

// Database resources
mysql://analytics/sales/quarterly_reports
postgres://db/customers/{id}     // Dynamic template

// In-memory resources
memory://context/conversation_history
memory://recent-changes          // Static resource
```

### Resource Templates

**Standard parameters** match one segment:
```typescript
files://{filename}     // Matches: files://config.json
                       // Does NOT match: files://path/to/config.json
```

**Wildcard parameters** match multiple segments:
```typescript
path://{filepath*}     // Matches: path://src/utils/helper.ts
```

### Resource Registration Example

```typescript
import { z } from "zod";

// Static resource
server.registerResource(
  "knowledge://index",
  {
    name: "Knowledge Base Index",
    description: "Complete index of all knowledge base files",
    mimeType: "text/markdown",
  },
  async () => {
    const indexContent = await readFile("knowledgebase/CLAUDE.md");
    return {
      content: [
        { type: "text", text: indexContent }
      ],
    };
  },
);

// Dynamic resource template
server.registerResourceTemplate(
  "knowledge://{domain}/{slug}",
  {
    name: "Knowledge Base File",
    description: "Access a specific knowledge base file by domain and slug",
    parameters: {
      domain: z.enum(["integrations", "libraries", "patterns", "protocols", "troubleshooting"]),
      slug: z.string(),
    },
  },
  async ({ domain, slug }) => {
    const filePath = `knowledgebase/${domain}/${slug}.md`;
    const content = await readFile(filePath);

    return {
      uri: `knowledge://${domain}/${slug}`,
      mimeType: "text/markdown",
      content: [
        { type: "text", text: content }
      ],
    };
  },
);
```

### Resource Security Best Practices

**URI Validation:**
```typescript
// Validate against known patterns
const ALLOWED_PATTERNS = [
  /^knowledge:\/\/[a-z]+\/[a-z0-9-]+$/,
  /^file:\/\/\/workspace\/.+/,
];

function validateURI(uri: string): boolean {
  return ALLOWED_PATTERNS.some(pattern => pattern.test(uri));
}

// Prevent directory traversal
if (uri.includes("../") || uri.includes("..\\")) {
  throw new Error("Invalid URI: directory traversal not allowed");
}
```

**Access Controls:**
```typescript
// Role-based access
async function getResource(uri: string, userRole: string) {
  const resource = parseURI(uri);

  if (resource.domain === "secrets" && userRole !== "admin") {
    throw new Error("Unauthorized access");
  }

  return await loadResource(resource);
}
```

**Caching:**
```typescript
// Cache static resources
const resourceCache = new Map<string, { content: string; timestamp: number }>();

async function getCachedResource(uri: string) {
  const cached = resourceCache.get(uri);
  const now = Date.now();

  if (cached && (now - cached.timestamp) < 3600000) { // 1 hour
    return cached.content;
  }

  const content = await loadResource(uri);
  resourceCache.set(uri, { content, timestamp: now });
  return content;
}
```

**Pagination for Large Resources:**
```typescript
server.registerResource(
  "knowledge://all-files",
  { /* metadata */ },
  async ({ cursor, limit = 20 }) => {
    const offset = cursor ? parseInt(cursor) : 0;
    const files = await listFiles(offset, limit);

    return {
      content: files.map(f => ({ type: "text", text: f })),
      nextCursor: files.length === limit ? String(offset + limit) : undefined,
    };
  },
);
```

## 5. Prompt Definition Patterns

### Prompt Structure

Prompts are reusable message templates that help guide LLM behavior:

```typescript
server.registerPrompt(
  "analyze_code",
  {
    name: "Analyze Code Quality",
    description: "Analyze code for best practices and potential issues",
    arguments: [
      {
        name: "language",
        description: "Programming language (e.g., typescript, python)",
        required: true,
      },
      {
        name: "focus",
        description: "Analysis focus area (e.g., security, performance, readability)",
        required: false,
      },
    ],
  },
  async ({ language, focus }) => {
    const focusText = focus ? ` with focus on ${focus}` : "";

    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Please analyze the following ${language} code${focusText}.
                   Provide specific recommendations for improvement.`,
          },
        },
      ],
    };
  },
);
```

### Prompt Versioning

```typescript
// Multiple versions under the same name
server.registerPrompt(
  "research_topic",
  {
    name: "Research Topic (v2)",
    version: 2,
    description: "Enhanced research prompt with source validation",
    // ...
  },
  async (args) => {
    // v2 implementation with source validation
  },
);

server.registerPrompt(
  "research_topic",
  {
    name: "Research Topic (v1)",
    version: 1,
    description: "Basic research prompt",
    // ...
  },
  async (args) => {
    // v1 implementation
  },
);

// Clients automatically receive the highest version
```

### Prompt with Context Injection

```typescript
server.registerPrompt(
  "knowledge_base_search",
  {
    name: "Search Knowledge Base",
    description: "Search and summarize knowledge base findings",
    arguments: [
      {
        name: "topic",
        description: "Topic to research",
        required: true,
      },
    ],
  },
  async ({ topic }) => {
    // Pre-fetch relevant context
    const relevantFiles = await searchKnowledgeBase(topic);
    const context = relevantFiles.map(f => f.content).join("\n\n---\n\n");

    return {
      messages: [
        {
          role: "system",
          content: {
            type: "text",
            text: "You are a research assistant with access to a knowledge base.",
          },
        },
        {
          role: "user",
          content: {
            type: "text",
            text: `Based on this context:\n\n${context}\n\nProvide a summary of ${topic}.`,
          },
        },
      ],
    };
  },
);
```

### Prompt Message Types

```typescript
interface PromptMessage {
  role: "user" | "assistant" | "system";
  content: {
    type: "text" | "image" | "resource";
    text?: string;           // For text content
    data?: string;           // For image (base64)
    mimeType?: string;       // For image/resource
    resource?: ResourceRef;  // For embedded resources
  };
}
```

## 6. Error Handling and Logging Best Practices

### Critical stdout/stderr Rule

**For STDIO-based servers:**
- **NEVER** write to stdout (`console.log()` in JavaScript)
- **ALWAYS** write logs to stderr (`console.error()`)
- Stdout is reserved for JSON-RPC messages only

```typescript
// ❌ BAD (STDIO)
console.log("Server started");
console.log("Processing request");

// ✅ GOOD (STDIO)
console.error("Server started");
console.error("Processing request");

// ✅ GOOD (HTTP servers - stdout is fine)
console.log("Server started on port 3000");
```

**Structured Logging:**
```typescript
const logger = {
  info: (msg: string, data?: any) =>
    console.error(`[INFO] ${msg}`, data || ''),
  error: (msg: string, err?: Error) =>
    console.error(`[ERROR] ${msg}`, err?.stack || err || ''),
  debug: (msg: string, data?: any) =>
    console.error(`[DEBUG] ${msg}`, data || ''),
};

// Usage
logger.info("Tool invoked", { tool: "search", params });
logger.error("Database connection failed", error);
```

### Error Type Classification

**1. Transport-level errors:**
- Network timeouts
- Broken pipes
- Authentication failures

**2. Protocol-level errors (JSON-RPC 2.0):**
- Malformed JSON
- Invalid parameters
- Method not found

**3. Application-level errors:**
- Business logic failures
- External API errors
- Resource not found

### Error Handling Pattern

```typescript
import { McpError } from "@modelcontextprotocol/sdk";

server.registerTool(
  "search_external_api",
  { /* schema */ },
  async (params) => {
    try {
      // Attempt operation
      const result = await externalAPI.search(params.query);

      return {
        content: [
          { type: "text", text: JSON.stringify(result) }
        ],
      };

    } catch (error) {
      // Log internally with full details
      logger.error("External API search failed", error);

      // Return sanitized error to client
      return {
        isError: true,
        content: [
          {
            type: "text",
            text: `Search failed: ${error.message}. Please try again or contact support.`
          }
        ],
      };
    }
  },
);

// For protocol-level errors, use McpError
function validateRequest(request: any) {
  if (!request.params) {
    throw new McpError(
      -32602, // Invalid params code
      "Missing required parameters"
    );
  }
}
```

### MCP Logging Levels (RFC 5424)

```typescript
type LoggingLevel =
  | "debug"     // Detailed debug information
  | "info"      // General informational messages
  | "notice"    // Normal but significant events
  | "warning"   // Warning messages
  | "error"     // Error conditions
  | "critical"  // Critical conditions
  | "alert"     // Action must be taken immediately
  | "emergency" // System is unusable
;

// Clients can dynamically set minimum log level
server.setLogLevel("info"); // Only log info and above
```

### Monitoring and Observability

```typescript
// Correlation IDs for request tracking
function generateCorrelationId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

server.on("toolCall", (event) => {
  const correlationId = generateCorrelationId();

  logger.info("Tool call started", {
    correlationId,
    tool: event.toolName,
    params: event.params,
  });

  // Track in monitoring system
  metrics.increment("tool_calls_total", { tool: event.toolName });
});

// Health check endpoint (for HTTP servers)
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    uptime: process.uptime(),
    memoryUsage: process.memoryUsage(),
  });
});

// Error rate monitoring
const errorCounter = new Map<string, number>();

function trackError(errorType: string) {
  errorCounter.set(errorType, (errorCounter.get(errorType) || 0) + 1);

  // Alert if error rate exceeds threshold
  if (errorCounter.get(errorType)! > 10) {
    logger.error(`High error rate detected: ${errorType}`);
    // Send alert to monitoring system
  }
}
```

## 7. Testing MCP Servers

### Local Testing Tools

**1. MCP Inspector (Primary tool)**
- Runs on `http://127.0.0.1:6274`
- Interactive Web UI for testing servers
- Connect to servers and test tools interactively

```bash
# Install and run MCP Inspector
npx @modelcontextprotocol/inspector

# Or globally
npm install -g @modelcontextprotocol/inspector
mcp-inspector
```

**2. mcp-cli (Terminal testing)**
```bash
npm install -g @modelcontextprotocol/cli

# Test a server
mcp-cli connect ./path/to/server/build/index.js

# List available tools
mcp-cli tools

# Call a tool
mcp-cli call tool_name '{"param": "value"}'
```

**3. Claude Desktop App**
- Easiest environment for integration testing
- Configuration: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
- Logs: `~/Library/Logs/Claude/mcp*.log`

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/absolute/path/to/server/build/index.js"]
    }
  }
}
```

**Debugging Claude Desktop:**
```bash
# View logs
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log

# General MCP logging
cat ~/Library/Logs/Claude/mcp.log

# Server-specific errors
cat ~/Library/Logs/Claude/mcp-server-my-server.log
```

### Development Setup for Fast Iteration

**Node.js 22.18.0+ with built-in type stripping:**
```json
// package.json
{
  "type": "module",
  "scripts": {
    "dev": "node --watch --experimental-strip-types src/index.ts",
    "build": "tsc"
  }
}
```

**Development vs Production Logging:**
```typescript
const isDev = process.env.NODE_ENV !== "production";

const logger = {
  info: (msg: string, data?: any) => {
    const output = isDev
      ? `[INFO] ${msg} ${JSON.stringify(data, null, 2)}`  // Pretty-printed
      : JSON.stringify({ level: "info", msg, data });     // Structured JSON

    console.error(output);
  },
};
```

### Unit Testing Tools

```typescript
// test/server.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

describe("Knowledge Base Server", () => {
  let server: McpServer;

  beforeEach(() => {
    server = new McpServer({
      name: "test-server",
      version: "1.0.0",
    });
  });

  it("should register search tool", () => {
    server.registerTool("search", { /* ... */ }, async () => {});

    const tools = server.listTools();
    expect(tools).toHaveLength(1);
    expect(tools[0].name).toBe("search");
  });

  it("should validate tool input schema", async () => {
    server.registerTool(
      "search",
      {
        inputSchema: {
          query: z.string().min(2),
        },
      },
      async ({ query }) => {
        return { content: [{ type: "text", text: `Results for: ${query}` }] };
      },
    );

    // Valid input
    const result = await server.callTool("search", { query: "test" });
    expect(result.content[0].text).toContain("test");

    // Invalid input (too short)
    await expect(
      server.callTool("search", { query: "x" })
    ).rejects.toThrow();
  });
});
```

### Integration Testing Pattern

```typescript
// test/integration.test.ts
import { spawn } from "child_process";
import { McpClient } from "@modelcontextprotocol/sdk/client/mcp.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

describe("Server Integration", () => {
  let client: McpClient;
  let serverProcess: any;

  beforeAll(async () => {
    // Start server process
    serverProcess = spawn("node", ["./build/index.js"]);

    // Connect client
    const transport = new StdioClientTransport({
      command: "node",
      args: ["./build/index.js"],
    });

    client = new McpClient();
    await client.connect(transport);
  });

  afterAll(async () => {
    await client.disconnect();
    serverProcess.kill();
  });

  it("should list available tools", async () => {
    const tools = await client.listTools();
    expect(tools).toContain("search");
    expect(tools).toContain("update_index");
  });

  it("should execute search tool", async () => {
    const result = await client.callTool("search", {
      query: "typescript",
      limit: 5,
    });

    expect(result.content).toBeDefined();
    expect(result.content[0].type).toBe("text");
  });
});
```

### Testing Checklist

- [ ] Tool schemas validate correctly
- [ ] Resource URIs match expected patterns
- [ ] Error responses include helpful messages
- [ ] Logging goes to stderr (not stdout)
- [ ] Server handles disconnections gracefully
- [ ] No memory leaks during long-running sessions
- [ ] Rate limiting works as expected
- [ ] Caching improves performance
- [ ] Security validations prevent unauthorized access

## Architecture Recommendations for Research Agent MCP

Based on the patterns above, here are recommendations for migrating the research agent:

### Proposed Structure

```
research-mcp-server/
├── src/
│   ├── index.ts                  # Main server entry
│   ├── tools/
│   │   ├── search.ts             # Search existing research
│   │   ├── research.ts           # Conduct new research
│   │   ├── check-staleness.ts   # Check if refresh needed
│   │   └── update-index.ts      # Update CLAUDE.md index
│   ├── resources/
│   │   ├── knowledge-index.ts   # knowledge://index
│   │   └── knowledge-file.ts    # knowledge://{domain}/{slug}
│   ├── prompts/
│   │   └── research-template.ts # Standardized research prompt
│   ├── utils/
│   │   ├── web-search.ts        # WebSearch wrapper
│   │   ├── context7.ts          # Context7 MCP integration
│   │   ├── frontmatter.ts       # YAML parsing/generation
│   │   └── staleness.ts         # Staleness calculation
│   └── config.ts                # Configuration management
├── test/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── package.json
├── tsconfig.json
└── README.md
```

### Tool Definitions

```typescript
// 1. Search existing research
server.registerTool(
  "search_knowledge_base",
  {
    description: "Search existing research in the knowledge base",
    inputSchema: {
      query: z.string().min(2),
      domain: z.enum(["integration", "library", "protocol", "pattern", "troubleshooting"]).optional(),
      tech: z.array(z.string()).optional(),
      area: z.array(z.string()).optional(),
    },
  },
  async ({ query, domain, tech, area }) => {
    // Implementation
  },
);

// 2. Check staleness
server.registerTool(
  "check_staleness",
  {
    description: "Check if existing research needs refreshing",
    inputSchema: {
      filePath: z.string(),
    },
  },
  async ({ filePath }) => {
    // Parse frontmatter, compare dates
  },
);

// 3. Conduct new research
server.registerTool(
  "research_topic",
  {
    description: "Conduct new research using web search and Context7",
    inputSchema: {
      topic: z.string(),
      domain: z.enum(["integration", "library", "protocol", "pattern", "troubleshooting"]),
      tech: z.array(z.string()),
      area: z.array(z.string()),
      taskId: z.string().optional(),
    },
  },
  async ({ topic, domain, tech, area, taskId }) => {
    // 1. WebSearch
    // 2. Context7 (if library)
    // 3. Synthesize findings
    // 4. Save file
    // 5. Update index
    // 6. Create task stub (if taskId)
  },
);

// 4. Update index
server.registerTool(
  "update_knowledge_index",
  {
    description: "Update the CLAUDE.md index after adding research",
    inputSchema: {
      filePath: z.string(),
      metadata: z.object({
        title: z.string(),
        domain: z.string(),
        tech: z.array(z.string()),
        area: z.array(z.string()),
        staleness: z.string(),
        updated: z.string(),
      }),
    },
  },
  async ({ filePath, metadata }) => {
    // Parse CLAUDE.md, insert new row, write back
  },
);
```

### Resource Definitions

```typescript
// Static resource: Knowledge base index
server.registerResource(
  "knowledge://index",
  {
    name: "Knowledge Base Index",
    description: "Complete index of all research files (CLAUDE.md)",
    mimeType: "text/markdown",
  },
  async () => {
    const content = await readFile("knowledgebase/CLAUDE.md");
    return { content: [{ type: "text", text: content }] };
  },
);

// Dynamic resource: Individual files
server.registerResourceTemplate(
  "knowledge://{domain}/{slug}",
  {
    name: "Knowledge Base File",
    description: "Access a specific research file",
    parameters: {
      domain: z.enum(["integrations", "libraries", "patterns", "protocols", "troubleshooting", "hardware", "infrastructure"]),
      slug: z.string(),
    },
  },
  async ({ domain, slug }) => {
    const filePath = `knowledgebase/${domain}/${slug}.md`;
    const content = await readFile(filePath);

    return {
      uri: `knowledge://${domain}/${slug}`,
      mimeType: "text/markdown",
      content: [{ type: "text", text: content }],
    };
  },
);
```

### Prompt Definitions

```typescript
server.registerPrompt(
  "research_workflow",
  {
    name: "Research Workflow",
    description: "Guide for conducting comprehensive research",
    arguments: [
      { name: "topic", required: true },
      { name: "domain", required: true },
    ],
  },
  async ({ topic, domain }) => {
    return {
      messages: [
        {
          role: "system",
          content: {
            type: "text",
            text: "You are a research assistant. Follow this workflow: 1) Search existing research, 2) Assess staleness, 3) Conduct new research if needed, 4) Save findings, 5) Update index.",
          },
        },
        {
          role: "user",
          content: {
            type: "text",
            text: `Research topic: ${topic} (domain: ${domain})`,
          },
        },
      ],
    };
  },
);
```

### Integration with Context7 MCP

The research agent can connect to Context7 as an MCP client:

```typescript
import { McpClient } from "@modelcontextprotocol/sdk/client/mcp.js";

// Connect to Context7 MCP server
const context7Client = new McpClient();
await context7Client.connect(context7Transport);

// Use in research tool
async function researchLibrary(libraryName: string) {
  // 1. Resolve library ID
  const libraryId = await context7Client.callTool("resolve-library-id", {
    name: libraryName,
  });

  // 2. Fetch documentation
  const docs = await context7Client.callTool("get-library-docs", {
    libraryId: libraryId.content[0].text,
  });

  return docs;
}
```

## Pros and Cons of MCP Migration

### Pros

1. **Standardized interface**: Other agents/tools can discover and use research capabilities
2. **Composability**: Research server can connect to Context7 MCP, WebSearch MCP, etc.
3. **Reusability**: Any MCP client (Claude Desktop, custom tools) can use the research agent
4. **Resource exposure**: Knowledge base files become first-class MCP resources
5. **Protocol enforcement**: Input validation, error handling, logging become standardized
6. **Testability**: MCP Inspector and mcp-cli enable easy testing
7. **Versioning**: Prompts and tools can be versioned independently

### Cons

1. **Additional complexity**: Adds SDK dependency and server lifecycle management
2. **Learning curve**: Team needs to learn MCP protocol and SDK
3. **Deployment overhead**: Requires running a separate server process
4. **Debugging complexity**: Adds another layer to debug (MCP protocol + application logic)
5. **STDIO logging constraints**: Must avoid `console.log()` in STDIO mode
6. **Not needed for single-use**: If only one agent uses research, MCP may be overkill

### When to Migrate

**Migrate if:**
- Multiple agents need research capabilities
- You want to expose knowledge base as MCP resources
- You plan to integrate with other MCP servers (Context7, WebSearch)
- You want standardized tool discovery and invocation
- You need versioned research workflows

**Don't migrate if:**
- Only the main Claude Code session uses research
- Simplicity is prioritized over composability
- Team is unfamiliar with MCP and doesn't want the learning curve
- Current Task-based approach is working well

## Sources

- [GitHub - modelcontextprotocol/typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk)
- [Build an MCP server - Model Context Protocol](https://modelcontextprotocol.io/docs/develop/build-server)
- [GitHub - modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- [GitHub - bsmi021/mcp-file-operations-server](https://github.com/bsmi021/mcp-file-operations-server)
- [GitHub - ftaricano/mcp-notion](https://github.com/ftaricano/mcp-notion)
- [Schema Reference - Model Context Protocol](https://modelcontextprotocol.io/specification/2025-06-18/schema)
- [The Best MCP Servers for Developers in 2026](https://www.builder.io/blog/best-mcp-servers-2026)
- [Error Handling in MCP Servers - Best Practices Guide](https://mcpcat.io/guides/error-handling-custom-mcp-servers/)
- [Debugging MCP Servers: Tips and Best Practices](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices)
- [MCP Logging Tutorial](https://www.mcpevals.io/blog/mcp-logging-tutorial)
- [Build MCP Servers in TypeScript - Complete Guide](https://mcpcat.io/guides/building-mcp-server-typescript/)
