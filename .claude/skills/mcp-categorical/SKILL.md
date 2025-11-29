---
name: mcp-categorical
description: MCP (Model Context Protocol) server patterns with categorical tool composition and typed context protocols. Use when building MCP servers with categorical composition patterns, designing tool interfaces using functors and natural transformations, implementing typed context management, or creating composable AI tool ecosystems with categorical guarantees.
---

# MCP Categorical Tool Composition

Categorical patterns for Model Context Protocol server design and tool composition.

## Core Categorical Mapping

MCP structures map to category theory:

- **Tools**: Morphisms `Parameters → Result`
- **Resources**: Objects with URI-based identity
- **Prompts**: Exponential objects `Context → Prompt`
- **Context**: Product type of available information
- **Server**: Category of tools with composition

## Basic MCP Server (TypeScript)

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Create server (category of tools)
const server = new Server(
  { name: "categorical-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// Define tool (morphism)
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "analyze",
      description: "Analyze input with categorical structure",
      inputSchema: {
        type: "object",
        properties: {
          input: { type: "string" },
          category: { type: "string" }
        },
        required: ["input"]
      }
    }
  ]
}));

// Tool implementation (morphism execution)
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === "analyze") {
    return {
      content: [{ type: "text", text: `Analyzed: ${args.input}` }]
    };
  }
  
  throw new Error(`Unknown tool: ${name}`);
});

// Run server
const transport = new StdioServerTransport();
server.connect(transport);
```

## Categorical Tool Composition

### Tool as Functor

```typescript
import { z } from "zod";

// Tool type: Parameters → Effect<Result, Error>
interface Tool<P, R> {
  name: string;
  schema: z.ZodType<P>;
  execute: (params: P) => Promise<R>;
}

// Functor: map over tool results
function mapTool<P, R, S>(
  tool: Tool<P, R>,
  f: (r: R) => S
): Tool<P, S> {
  return {
    name: tool.name,
    schema: tool.schema,
    execute: async (params) => f(await tool.execute(params))
  };
}

// Example
const searchTool: Tool<{ query: string }, string[]> = {
  name: "search",
  schema: z.object({ query: z.string() }),
  execute: async ({ query }) => [`Result for: ${query}`]
};

const formattedSearch = mapTool(searchTool, (results) =>
  results.join("\n")
);
```

### Tool Composition (Kleisli)

```typescript
// Compose tools: (A → B) → (B → C) → (A → C)
function composeTool<A, B, C>(
  first: Tool<A, B>,
  second: Tool<B, C>
): Tool<A, C> {
  return {
    name: `${first.name}_then_${second.name}`,
    schema: first.schema,
    execute: async (params: A) => {
      const intermediate = await first.execute(params);
      return second.execute(intermediate as any);
    }
  };
}

// Product of tools: run in parallel
function productTool<A, B, C>(
  tool1: Tool<A, B>,
  tool2: Tool<A, C>
): Tool<A, [B, C]> {
  return {
    name: `${tool1.name}_and_${tool2.name}`,
    schema: tool1.schema,
    execute: async (params: A) => {
      const [r1, r2] = await Promise.all([
        tool1.execute(params),
        tool2.execute(params)
      ]);
      return [r1, r2];
    }
  };
}
```

### Natural Transformation Between Tool Categories

```typescript
// Transform tool category to another
interface ToolTransform<F, G> {
  transform: <P, R>(tool: Tool<P, R>) => Tool<P, R>;
}

// Logging transformation
const withLogging: ToolTransform<any, any> = {
  transform: (tool) => ({
    ...tool,
    execute: async (params) => {
      console.log(`Calling ${tool.name} with`, params);
      const result = await tool.execute(params);
      console.log(`Result from ${tool.name}:`, result);
      return result;
    }
  })
};

// Retry transformation
const withRetry = (maxRetries: number): ToolTransform<any, any> => ({
  transform: (tool) => ({
    ...tool,
    execute: async (params) => {
      for (let i = 0; i < maxRetries; i++) {
        try {
          return await tool.execute(params);
        } catch (e) {
          if (i === maxRetries - 1) throw e;
        }
      }
      throw new Error("Unreachable");
    }
  })
});
```

## Python MCP Server

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Categorical tool registry
class ToolCategory:
    """Category of tools with composition."""
    
    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self.handlers: dict[str, callable] = {}
    
    def register(self, name: str, schema: dict, handler: callable):
        """Register tool as morphism."""
        self.tools[name] = Tool(
            name=name,
            description=f"Tool: {name}",
            inputSchema=schema
        )
        self.handlers[name] = handler
    
    def compose(self, name1: str, name2: str) -> str:
        """Compose two tools."""
        composed_name = f"{name1}_then_{name2}"
        
        async def composed_handler(params):
            result1 = await self.handlers[name1](params)
            return await self.handlers[name2](result1)
        
        self.handlers[composed_name] = composed_handler
        return composed_name

# Create server
app = Server("categorical-mcp")
category = ToolCategory()

# Register tools
category.register(
    "fetch",
    {"type": "object", "properties": {"url": {"type": "string"}}},
    lambda p: f"Fetched: {p['url']}"
)

category.register(
    "parse",
    {"type": "object", "properties": {"content": {"type": "string"}}},
    lambda p: f"Parsed: {p['content']}"
)

@app.list_tools()
async def list_tools():
    return list(category.tools.values())

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    handler = category.handlers.get(name)
    if handler:
        result = await handler(arguments) if asyncio.iscoroutinefunction(handler) else handler(arguments)
        return [TextContent(type="text", text=str(result))]
    raise ValueError(f"Unknown tool: {name}")

# Run
async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write)
```

## Resource Management (Objects)

```typescript
// Resources as objects in category
interface Resource<T> {
  uri: string;
  name: string;
  mimeType: string;
  read: () => Promise<T>;
}

// Resource functor
function mapResource<T, U>(
  resource: Resource<T>,
  f: (t: T) => U
): Resource<U> {
  return {
    ...resource,
    read: async () => f(await resource.read())
  };
}

// Resource registry
class ResourceCategory {
  private resources: Map<string, Resource<any>> = new Map();
  
  register<T>(resource: Resource<T>): void {
    this.resources.set(resource.uri, resource);
  }
  
  get<T>(uri: string): Resource<T> | undefined {
    return this.resources.get(uri);
  }
  
  // Natural transformation: Resource → Tool
  toTool<T>(uri: string): Tool<{}, T> {
    const resource = this.get<T>(uri);
    if (!resource) throw new Error(`Unknown resource: ${uri}`);
    
    return {
      name: `read_${resource.name}`,
      schema: z.object({}),
      execute: async () => resource.read()
    };
  }
}
```

## Typed Context Protocol

```typescript
import { z } from "zod";

// Context as product type
const ContextSchema = z.object({
  conversation: z.array(z.object({
    role: z.enum(["user", "assistant"]),
    content: z.string()
  })),
  tools: z.array(z.string()),
  resources: z.array(z.string()),
  metadata: z.record(z.unknown())
});

type Context = z.infer<typeof ContextSchema>;

// Context functor operations
const contextOps = {
  // Add message (endofunctor)
  addMessage: (ctx: Context, role: "user" | "assistant", content: string): Context => ({
    ...ctx,
    conversation: [...ctx.conversation, { role, content }]
  }),
  
  // Filter tools (subfunctor)
  filterTools: (ctx: Context, predicate: (t: string) => boolean): Context => ({
    ...ctx,
    tools: ctx.tools.filter(predicate)
  }),
  
  // Merge contexts (coproduct)
  merge: (ctx1: Context, ctx2: Context): Context => ({
    conversation: [...ctx1.conversation, ...ctx2.conversation],
    tools: [...new Set([...ctx1.tools, ...ctx2.tools])],
    resources: [...new Set([...ctx1.resources, ...ctx2.resources])],
    metadata: { ...ctx1.metadata, ...ctx2.metadata }
  })
};
```

## Prompt Templates (Exponential Objects)

```typescript
// Prompt as exponential: Context → String
interface PromptTemplate {
  name: string;
  template: (ctx: Context) => string;
}

// Prompt composition
function composePrompts(
  p1: PromptTemplate,
  p2: PromptTemplate
): PromptTemplate {
  return {
    name: `${p1.name}_then_${p2.name}`,
    template: (ctx) => `${p1.template(ctx)}\n\n${p2.template(ctx)}`
  };
}

// Example prompts
const systemPrompt: PromptTemplate = {
  name: "system",
  template: (ctx) => `You have access to: ${ctx.tools.join(", ")}`
};

const contextPrompt: PromptTemplate = {
  name: "context",
  template: (ctx) => ctx.conversation
    .map(m => `${m.role}: ${m.content}`)
    .join("\n")
};
```

## Categorical Guarantees

MCP with categorical patterns ensures:

1. **Tool Composability**: Tools compose via Kleisli composition
2. **Type Safety**: Zod schemas validate parameters at boundaries
3. **Resource Identity**: URIs provide unique object identification
4. **Context Coherence**: Product structure preserves all context
5. **Natural Transformations**: Tool transformations preserve structure
