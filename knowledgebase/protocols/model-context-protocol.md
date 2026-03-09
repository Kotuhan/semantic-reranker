---
title: Model Context Protocol (MCP) - Architecture and Capabilities
domain: protocol
tech: [json-rpc, typescript, nodejs, python]
area: [mcp, llm-integration, ai-tools, protocol-design]
staleness: 6months
created: 2026-01-29
updated: 2026-01-29
sources:
  - https://modelcontextprotocol.io/specification/2025-11-25
  - https://github.com/modelcontextprotocol/modelcontextprotocol
  - https://modelcontextprotocol.io/specification/2025-06-18/basic/transports
  - https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/102
  - https://workos.com/blog/mcp-features-guide
  - https://workos.com/blog/how-mcp-servers-work
---

# Model Context Protocol (MCP) - Architecture and Capabilities

## Overview

The Model Context Protocol (MCP) is an open protocol enabling seamless integration between LLM applications and external data sources/tools. It provides a standardized way to connect LLMs with context through JSON-RPC 2.0 messages over stateful connections.

**Current Specification:** 2025-11-25 (donated to Agentic AI Foundation under Linux Foundation in Dec 2025)

## Core Architecture

### Client-Server Model

```
Host (LLM App) → Client (Connector) → Server (Capabilities Provider)
                                         ├── Tools
                                         ├── Resources
                                         ├── Prompts
                                         └── Sampling
```

**Key Components:**
- **Hosts**: LLM applications (Claude Code, Cursor, Windsurf)
- **Clients**: Connectors within host managing server connections
- **Servers**: Services exposing context/capabilities

### Transport Mechanisms

#### stdio (Recommended for Local)

**Process:**
1. Client launches server as subprocess
2. JSON-RPC messages over stdin/stdout
3. Newline-delimited, UTF-8 encoded
4. Server lifetime tied to client process

**Characteristics:**
- High performance (no network overhead)
- Local-only
- Client manages lifecycle
- Logs to stderr permitted

#### Streamable HTTP (For Remote/Production)

**Process:**
1. Server runs as independent, long-lived process
2. Client sends HTTP POST per message
3. Server returns JSON or SSE stream
4. Optional GET for server-initiated messages

**Session Management:**
- Optional `Mcp-Session-Id` header
- Server assigns during initialization
- Client includes in all subsequent requests
- Explicit DELETE to terminate

**Benefits:**
- Multiple simultaneous clients
- Network-based (remote servers)
- Survives client disconnections

## Four Primary Primitives

### 1. Tools

**Definition:** Executable functions with typed inputs/outputs.

**Characteristics:**
- Require explicit user approval per execution
- Schema-defined operations
- Arbitrary code execution capability

**Use Cases:**
- API calls
- Database operations
- File manipulation
- External service integration

**Example:**
```json
{
  "name": "search_web",
  "description": "Search the web for information",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"}
    }
  }
}
```

### 2. Resources

**Definition:** Read-only data entities identified by URIs.

**Characteristics:**
- Text or binary data
- Static or dynamic
- MIME type declarations
- Parameterized templates supported

**Use Cases:**
- Configuration files
- Database records
- Documentation
- Reference data

**Example URI:** `travel://activities/{city}/{category}`

### 3. Prompts

**Definition:** Predefined instruction templates.

**Characteristics:**
- User-controlled (explicit selection)
- Return message lists for model initialization
- Can reference resources/tools dynamically
- Reusable across sessions

**Use Cases:**
- Standard workflows
- Task templates
- Consistent interaction patterns

### 4. Sampling

**Definition:** Server-initiated LLM completion requests.

**Flow:**
1. Server requests completion
2. User approves request
3. Client performs LLM call
4. User reviews results
5. Results sent to server (if approved)

**Use Cases:**
- AI ranking/filtering
- Multi-step reasoning
- Agentic behaviors

**Key Constraint:** User controls prompt and result visibility (server cannot see raw prompts).

## Additional Features

### Roots

Filesystem boundaries defining safe access zones:
- URI-based (e.g., `file:///Users/agent/project`)
- Client-provided to servers
- Prevents access outside specified directories

### Elicitation

Server-initiated requests for missing context:
- Handles unresolved variables
- User reviews/modifies responses
- Fills context gaps during session

## State Management

### Options & Challenges

| Approach | Best For | Challenges |
|----------|----------|------------|
| **In-memory** | Local stdio servers, single-instance | Lost on restart, fails in serverless |
| **Persistent (DB/Redis)** | Production, multi-instance | Complexity, serialization overhead |
| **Stateless** | Simple tools, transactional ops | May require client-side context |

**Emerging Best Practice:** Stateless-first design, adding state only when essential. Community gravitating toward "stateless + optional stateful variants."

### Connection Patterns

**Long-lived (Traditional):**
- Persistent SSE streams
- Problematic for serverless (timeouts)
- Requires sticky routing

**Short-lived/Transactional (Recommended):**
- SSE only during active operations
- Disconnect after response
- Better serverless compatibility

## Client Compatibility (2026)

| Client | Support | Configuration |
|--------|---------|---------------|
| Claude Code/Desktop | ✅ | `claude mcp add`, `claude_desktop_config.json` |
| Cursor | ✅ | `~/.cursor/mcp.json` |
| Windsurf | ✅ | `~/.codeium/windsurf/mcp_config.json` |
| Continue | ✅ | Open-source extension |
| VS Code, JetBrains, Warp | ✅ | Various integrations |

**Adoption:** 20+ clients as of 2026, indicating strong ecosystem support.

## Key Limitations

### Protocol-Level Constraints

#### No Built-In Security
- No authentication/authorization mechanisms
- No encryption (must use TLS)
- No message signing/verification
- Developers must implement security layers

#### No Direct Server-to-Server Communication
- Servers cannot call other servers natively
- Requires client orchestration or proxy patterns
- Tool chaining must go through client

**Workaround:** Wrapper servers like `mcp-tool-chainer` act as MCP clients to other servers, orchestrating sequential execution.

#### No Sandboxing
- Servers run with full process permissions
- No protocol-enforced restrictions
- Must implement external sandboxing (containers, etc.)

### What Servers CAN Do (Unrestricted)

Despite assumptions, MCP servers **CAN**:

✅ **Make HTTP Requests**: No network restrictions (e.g., Fetch MCP server)
✅ **Access Filesystem**: Full file operations possible (e.g., Filesystem MCP server)
✅ **Execute Arbitrary Code**: Tools represent code execution

**Security depends entirely on server implementation, not protocol.**

## Server Composition Patterns

### Problem: Cross-Server Tool Invocation

Servers cannot directly call other servers. Solutions:

#### Pattern 1: Client Orchestration
Client manages multiple servers, coordinates tool calls.

#### Pattern 2: Proxy MCP Server
Wrapper server acts as MCP client to upstream servers.

**Example: mcp-tool-chainer**
- Single `mcp_chain` tool with JSON tool sequence
- Passes results via `CHAIN_RESULT` placeholder
- Supports JsonPath extraction
- Must be configured last (avoid discovery cycles)

```json
{
  "mcpPath": [
    {"server": "context7", "tool": "resolve-library-id", "args": {"library_name": "fastapi"}},
    {"server": "context7", "tool": "get-library-docs", "args": {"library_id": "CHAIN_RESULT"}}
  ]
}
```

#### Pattern 3: HTTP API Direct Calls
Server implements HTTP client to call other services' APIs directly.

## Best Practices

### Server Development

1. **Start Stateless**: Only add state when necessary
2. **Short-lived Connections**: Close SSE after response
3. **Explicit Security**: Implement auth/authz externally
4. **Clear Tool Descriptions**: Critical for LLM understanding
5. **User Approval Awareness**: Design around approval overhead

### Deployment

1. **Local Development**: Use stdio transport
2. **Production**: Use Streamable HTTP with session management
3. **Serverless**: Prefer stateless design, transactional operations
4. **Multi-Instance**: External state storage or sticky routing

### Security

1. **Validate `Origin` header** (prevent DNS rebinding)
2. **Bind to localhost** (127.0.0.1) for local servers
3. **Implement authentication** for all connections
4. **Use TLS** for HTTP transport
5. **Sandbox server processes** (containers, restricted permissions)

## MCP vs. Alternative Approaches

### When to Use MCP

✅ Need multi-client compatibility (not just one editor)
✅ Standardized, discoverable interface required
✅ Can implement HTTP/filesystem access internally
✅ Don't need tight integration with other MCP servers
✅ State can be file-based or in-memory

### When to Use Sub-Agents/Plugins

✅ Tight integration with host's native tools (WebSearch, etc.)
✅ Need to orchestrate multiple existing MCP servers
✅ Benefit from host's context/memory management
✅ Multi-step approval overhead problematic
✅ Simpler development/deployment model preferred

## Project Integration

### Research Agent MCP Evaluation

**Pros:**
- Broad client compatibility (Cursor, Windsurf, etc.)
- Standardized interface for knowledge base access
- Resources for existing research, Tools for new research

**Cons:**
- Cannot directly invoke Context7 MCP server (need workaround)
- WebSearch/WebFetch unavailable (must implement HTTP client)
- User approval per operation (could batch)
- State management for index cache

**Recommended Architecture (if migrating):**
```
Research Agent MCP Server
├── Resources
│   └── knowledge-base-index, research files
├── Tools
│   ├── search-existing-research
│   ├── conduct-research (web search + fetch + synthesize)
│   └── create-research-document
└── State: In-memory index cache (reload on startup)
```

## Common Issues to Avoid

1. **Assuming Sandboxing Exists**: Protocol provides none; implement externally
2. **Long-lived SSE in Serverless**: Use transactional patterns instead
3. **Direct Server-to-Server Calls**: Requires proxy pattern, not native
4. **Ignoring User Approval**: Every tool needs approval; batch operations when possible
5. **Complex State Management**: Start stateless, add state incrementally

## Resources

- [Official Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25)
- [GitHub Repository](https://github.com/modelcontextprotocol/modelcontextprotocol)
- [State Management Discussion](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/102)
- [Features Guide - WorkOS](https://workos.com/blog/mcp-features-guide)
- [Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [Tool Chainer Example](https://github.com/thirdstrandstudio/mcp-tool-chainer)
