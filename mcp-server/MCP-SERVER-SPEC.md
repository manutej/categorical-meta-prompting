# Meta-Prompting MCP Server - Minimum Viable Specification

**Version**: 1.0.0-alpha
**Protocol**: Model Context Protocol (MCP)
**Language**: TypeScript (Node.js)

---

## Minimum Viable Product (MVP)

**Goal**: Expose 2 core meta-prompting capabilities as MCP tools that any MCP client can use.

### MVP Scope

```
┌─────────────────────────────────────────────────────────────┐
│           meta-prompting-mcp-server (MVP)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TOOLS (2):                                                 │
│  ├── analyze_complexity                                     │
│  │   Input: { task: string }                               │
│  │   Output: { score: 0.0-1.0, tier: L1-L7, strategy }     │
│  │                                                          │
│  └── iterate_prompt                                         │
│      Input: { task: string, threshold: 0.0-1.0 }           │
│      Output: { result: string, quality: 0.0-1.0, iterations}│
│                                                             │
│  RESOURCES (1):                                             │
│  └── prompt://templates/{template_id}                       │
│      Returns: Template content from registry                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Tool Specifications

### 1. `analyze_complexity`

**Purpose**: Score task complexity and recommend meta-prompting strategy

**Input Schema**:
```json
{
  "name": "analyze_complexity",
  "description": "Analyze task complexity and recommend meta-prompting tier (L1-L7)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task": {
        "type": "string",
        "description": "The task description to analyze"
      }
    },
    "required": ["task"]
  }
}
```

**Output Schema**:
```json
{
  "score": 0.75,
  "tier": "L5",
  "strategy": "AUTONOMOUS_EVOLUTION",
  "reasoning": "Multi-component system with fault tolerance and observability requirements",
  "suggested_iterations": 3,
  "estimated_tokens": 7500
}
```

**Implementation** (pseudocode):
```typescript
async function analyze_complexity(task: string): Promise<ComplexityAnalysis> {
  const indicators = {
    multi_component: /\b(and|plus|with|including)\b/i.test(task),
    architecture: /\b(design|architect|system|platform)\b/i.test(task),
    fault_tolerance: /\b(self-healing|resilient|fault|recovery)\b/i.test(task),
    scale: /\b(distributed|scale|cluster|microservices)\b/i.test(task),
  };

  const score = Object.values(indicators).filter(v => v).length / 10;

  return {
    score,
    tier: mapScoreToTier(score),
    strategy: mapTierToStrategy(tier),
    reasoning: generateReasoning(indicators),
    suggested_iterations: calculateIterations(score),
    estimated_tokens: estimateTokens(tier),
  };
}
```

---

### 2. `iterate_prompt`

**Purpose**: Recursive meta-prompting with quality-driven stopping

**Input Schema**:
```json
{
  "name": "iterate_prompt",
  "description": "Execute recursive meta-prompting with quality assessment",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task": {
        "type": "string",
        "description": "Task to complete with meta-prompting"
      },
      "threshold": {
        "type": "number",
        "description": "Quality threshold (0.0-1.0) for stopping",
        "default": 0.8
      },
      "max_iterations": {
        "type": "number",
        "description": "Maximum iterations before stopping",
        "default": 3
      }
    },
    "required": ["task"]
  }
}
```

**Output Schema**:
```json
{
  "result": "Final output after iterations",
  "quality": {
    "correctness": 0.9,
    "clarity": 0.85,
    "completeness": 0.88,
    "efficiency": 0.82,
    "aggregate": 0.86
  },
  "iterations": 2,
  "improvement": 0.15,
  "converged": true
}
```

**Implementation** (pseudocode):
```typescript
async function iterate_prompt(
  task: string,
  threshold: number = 0.8,
  max_iterations: number = 3
): Promise<IterationResult> {
  let current_output = await executeTask(task);
  let current_quality = await assessQuality(current_output, task);

  for (let i = 1; i <= max_iterations; i++) {
    if (current_quality.aggregate >= threshold) {
      return {
        result: current_output,
        quality: current_quality,
        iterations: i,
        converged: true,
      };
    }

    const context = await extractContext(current_output);
    const refinement_prompt = buildRefinementPrompt(task, context, current_quality);
    current_output = await executeTask(refinement_prompt);
    const new_quality = await assessQuality(current_output, task);

    if (new_quality.aggregate <= current_quality.aggregate) {
      // Quality plateau - stop
      return {
        result: current_output,
        quality: current_quality,
        iterations: i,
        converged: false,
      };
    }

    current_quality = new_quality;
  }

  return {
    result: current_output,
    quality: current_quality,
    iterations: max_iterations,
    converged: current_quality.aggregate >= threshold,
  };
}
```

---

## Resource: Prompt Templates

**URI Pattern**: `prompt://templates/{template_id}`

**Example Templates**:
- `prompt://templates/algorithm-review`
- `prompt://templates/security-review`
- `prompt://templates/debug-systematic`

**Resource Schema**:
```json
{
  "uri": "prompt://templates/algorithm-review",
  "name": "Algorithm Review Template",
  "description": "Review code for algorithmic correctness",
  "mimeType": "text/markdown",
  "content": "Review this code for algorithmic correctness:\n- Time complexity (Big-O)\n- Space complexity\n- Edge cases\n- Correctness proof"
}
```

---

## Project Structure (MVP)

```
meta-prompting-mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts                 # MCP server entry point
│   ├── tools/
│   │   ├── analyze-complexity.ts
│   │   └── iterate-prompt.ts
│   ├── resources/
│   │   └── prompt-templates.ts
│   └── utils/
│       ├── quality-assessment.ts
│       ├── complexity-scoring.ts
│       └── template-registry.ts
├── templates/                   # Prompt template files
│   ├── algorithm-review.md
│   ├── security-review.md
│   └── debug-systematic.md
└── README.md
```

---

## Installation & Usage

### Install

```bash
# Install from npm (future)
npm install -g @manutej/meta-prompting-mcp-server

# Or run locally
cd meta-prompting-mcp-server
npm install
npm run build
```

### Configure in Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "meta-prompting": {
      "command": "node",
      "args": ["/path/to/meta-prompting-mcp-server/dist/index.js"],
      "env": {}
    }
  }
}
```

### Use in Claude Code

Once connected, Claude Code can use the tools:

```
User: "Analyze the complexity of building a rate limiter"

Claude: I'll use the meta-prompting MCP server to analyze this task.

[Uses mcp__meta-prompting__analyze_complexity tool]

Result:
- Score: 0.4 (Medium complexity)
- Tier: L3 (Balanced)
- Strategy: MULTI_APPROACH
- Suggested iterations: 2
- Estimated tokens: 3500

This is a moderate complexity task that would benefit from a
design → implement → test pipeline.
```

---

## Development Timeline (MVP)

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Setup** | 1 hour | Project structure, TypeScript config |
| **Tool 1** | 2 hours | `analyze_complexity` implementation |
| **Tool 2** | 3 hours | `iterate_prompt` with quality tracking |
| **Resources** | 1 hour | Prompt template registry |
| **Testing** | 2 hours | MCP protocol testing, integration |
| **Docs** | 1 hour | README, examples |
| **Total** | **10 hours** | **Working MVP** |

---

## Future Enhancements (Post-MVP)

### Phase 2: Extended Tools
- `assess_quality` (standalone quality checker)
- `extract_context` (context extraction from output)
- `generate_framework` (full L1-L7 framework generation)

### Phase 3: State Management
- Store past iterations in SQLite
- Learn from quality patterns
- Suggest templates based on history

### Phase 4: Agent Integration
- Launch agents via MCP (e.g., `hekat_orchestrate`)
- Parallel agent coordination
- MARS synthesis patterns

### Phase 5: Community Features
- Shared prompt registry (crowd-sourced templates)
- Quality benchmarks (compare your scores)
- Plugin marketplace integration

---

## Open Questions

1. **LLM Provider**: Should the MCP server have its own API key, or rely on the client's?
   - **Recommendation**: Client provides (via MCP context)

2. **Storage**: Where to persist quality scores, templates, history?
   - **MVP**: In-memory only
   - **Future**: SQLite, then PostgreSQL

3. **Template Source**: Static files or dynamic fetching?
   - **MVP**: Static markdown files in `templates/`
   - **Future**: Remote registry with versioning

---

## Success Metrics

**MVP is successful if**:
- ✅ Claude Code can call `analyze_complexity` and get L1-L7 tier
- ✅ Claude Code can call `iterate_prompt` and get quality-improved output
- ✅ Templates are accessible via `prompt://` URIs
- ✅ Installation takes <5 minutes
- ✅ Works with MCP Inspector for debugging

---

## Next Step: Prototype in 10 Hours

Would you like me to:
1. **Generate the full TypeScript boilerplate** (package.json, tsconfig, src/)
2. **Implement `analyze_complexity` tool** (2-hour task)
3. **Create 3 initial prompt templates** (algorithm, security, debug)

Or should I create a **complete specification document** first for review?
