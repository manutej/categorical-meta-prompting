---
name: voltagent-multiagent
description: VoltAgent multi-agent system design with natural transformation coordination between agents. Use when building TypeScript multi-agent AI systems, implementing agent coordination with categorical patterns, designing supervisor-worker agent hierarchies, or creating composable agent architectures with typed message passing.
---

# VoltAgent Multi-Agent Systems

VoltAgent framework for building multi-agent AI systems with categorical coordination patterns.

## Installation

```bash
npm install @voltagent/core
```

## Core Categorical Concepts

VoltAgent maps to category theory:

- **Agent**: Object with typed input/output interface
- **Message**: Morphism between agent states
- **Supervisor**: Functor coordinating agent composition
- **Handoff**: Natural transformation between agents
- **Memory**: State monad for agent context

## Basic Agent Definition

```typescript
import { Agent, createAgent, Tool } from '@voltagent/core';
import { z } from 'zod';

// Define agent with typed schema
const researcherAgent = createAgent({
  name: 'researcher',
  description: 'Researches topics and gathers information',
  
  // Input/output schemas (object types)
  inputSchema: z.object({
    query: z.string(),
    depth: z.enum(['shallow', 'deep']).default('shallow')
  }),
  
  outputSchema: z.object({
    findings: z.array(z.string()),
    sources: z.array(z.string()),
    confidence: z.number().min(0).max(1)
  }),
  
  // Tools available to agent
  tools: [searchTool, summarizeTool],
  
  // System prompt
  systemPrompt: `You are a research agent. 
    Gather information thoroughly and cite sources.`
});
```

## Tool Definition

```typescript
const searchTool = new Tool({
  name: 'web_search',
  description: 'Search the web for information',
  
  parameters: z.object({
    query: z.string(),
    maxResults: z.number().default(5)
  }),
  
  execute: async ({ query, maxResults }) => {
    // Implementation
    return { results: [`Result for: ${query}`] };
  }
});

const summarizeTool = new Tool({
  name: 'summarize',
  description: 'Summarize text content',
  
  parameters: z.object({
    text: z.string(),
    maxLength: z.number().default(100)
  }),
  
  execute: async ({ text, maxLength }) => {
    return { summary: text.slice(0, maxLength) + '...' };
  }
});
```

## Multi-Agent Coordination

### Supervisor Pattern (Functor)

```typescript
import { Supervisor, createSupervisor } from '@voltagent/core';

// Supervisor as functor: coordinates agent composition
const teamSupervisor = createSupervisor({
  name: 'team_lead',
  description: 'Coordinates research and writing agents',
  
  agents: [researcherAgent, writerAgent, reviewerAgent],
  
  // Routing strategy (coproduct selection)
  routingStrategy: 'llm', // or 'round-robin', 'priority'
  
  // Completion condition
  completionCondition: (state) => 
    state.messages.some(m => m.content.includes('TASK_COMPLETE')),
  
  // Max iterations (fixed-point bound)
  maxIterations: 10
});

// Execute supervised task
const result = await teamSupervisor.run({
  task: 'Research and write an article about quantum computing',
  context: {}
});
```

### Agent Handoff (Natural Transformation)

```typescript
import { handoff, HandoffCondition } from '@voltagent/core';

// Natural transformation: Agent A ⇒ Agent B
const researchToWriter = handoff({
  from: researcherAgent,
  to: writerAgent,
  
  // Transform output of A to input of B
  transform: (researchOutput) => ({
    topic: researchOutput.query,
    facts: researchOutput.findings,
    sources: researchOutput.sources
  }),
  
  // Condition for handoff
  condition: (output) => output.confidence > 0.7
});

// Chain with handoffs
const pipeline = createPipeline([
  researcherAgent,
  researchToWriter,
  writerAgent,
  writerToReviewer,
  reviewerAgent
]);
```

### Parallel Agent Execution (Product)

```typescript
import { parallel, ParallelConfig } from '@voltagent/core';

// Product of agents: run in parallel, combine results
const parallelAnalysis = parallel({
  agents: [
    sentimentAgent,
    keywordAgent,
    summaryAgent
  ],
  
  // Combine results (product type)
  combiner: (results) => ({
    sentiment: results[0].sentiment,
    keywords: results[1].keywords,
    summary: results[2].summary,
    combined_confidence: Math.min(...results.map(r => r.confidence))
  })
});

const analysisResult = await parallelAnalysis.run({
  text: 'Analyze this document...'
});
```

## State Management (State Monad)

```typescript
import { AgentState, createStatefulAgent } from '@voltagent/core';

interface ResearchState {
  findings: string[];
  sourcesVisited: string[];
  iterationCount: number;
}

const statefulResearcher = createStatefulAgent<ResearchState>({
  name: 'stateful_researcher',
  
  initialState: {
    findings: [],
    sourcesVisited: [],
    iterationCount: 0
  },
  
  // State transition (morphism)
  transition: (state, action) => {
    switch (action.type) {
      case 'ADD_FINDING':
        return {
          ...state,
          findings: [...state.findings, action.finding],
          iterationCount: state.iterationCount + 1
        };
      case 'VISIT_SOURCE':
        return {
          ...state,
          sourcesVisited: [...state.sourcesVisited, action.source]
        };
      default:
        return state;
    }
  },
  
  // State-aware execution
  execute: async (input, state, dispatch) => {
    // Can read state and dispatch actions
    if (state.iterationCount >= 5) {
      return { done: true, findings: state.findings };
    }
    
    const finding = await search(input.query);
    dispatch({ type: 'ADD_FINDING', finding });
    
    return { done: false, currentFinding: finding };
  }
});
```

## Memory and Context

```typescript
import { Memory, createMemory } from '@voltagent/core';

// Shared memory (Reader monad pattern)
const sharedMemory = createMemory({
  type: 'vector', // or 'key-value', 'graph'
  
  config: {
    embeddings: openaiEmbeddings,
    maxItems: 1000,
    similarityThreshold: 0.7
  }
});

// Agent with memory access
const memoryAgent = createAgent({
  name: 'memory_agent',
  memory: sharedMemory,
  
  // Memory-aware system prompt
  systemPrompt: `You have access to shared memory.
    Use it to recall previous findings and maintain context.`,
  
  // Memory tools
  tools: [
    sharedMemory.tools.remember,
    sharedMemory.tools.recall,
    sharedMemory.tools.forget
  ]
});
```

## Categorical Patterns

### Agent as Functor

```typescript
// Map over agent outputs
const mappedAgent = researcherAgent.map(output => ({
  ...output,
  findings: output.findings.map(f => f.toUpperCase()),
  processedAt: new Date()
}));

// Functor laws hold:
// agent.map(id) ≡ agent
// agent.map(f).map(g) ≡ agent.map(x => g(f(x)))
```

### Agent Composition (Kleisli)

```typescript
import { compose } from '@voltagent/core';

// Kleisli composition: (A → M B) → (B → M C) → (A → M C)
const researchThenWrite = compose(
  researcherAgent,
  writerAgent,
  // Transform function
  (researchOutput) => ({
    topic: researchOutput.query,
    content: researchOutput.findings.join('\n')
  })
);

// Associativity: compose(compose(f, g), h) ≡ compose(f, compose(g, h))
```

### Natural Transformation Between Agent Types

```typescript
// Transform ReAct agent to simple agent
const reactToSimple = <I, O>(reactAgent: ReActAgent<I, O>): SimpleAgent<I, O> => ({
  name: reactAgent.name,
  execute: async (input) => {
    const trace = await reactAgent.executeWithTrace(input);
    return trace.finalOutput;
  }
});

// Naturality: for all f: A → B
// reactToSimple(reactAgent).map(f) ≡ reactToSimple(reactAgent.map(f))
```

## Error Handling

```typescript
import { AgentError, retry, fallback } from '@voltagent/core';

// Retry with exponential backoff
const resilientAgent = retry(researcherAgent, {
  maxAttempts: 3,
  backoff: 'exponential',
  initialDelay: 1000
});

// Fallback to alternative agent
const withFallback = fallback(
  primaryAgent,
  fallbackAgent,
  (error) => error instanceof RateLimitError
);
```

## Observability

```typescript
import { trace, observe } from '@voltagent/core';

// Trace agent execution
const tracedAgent = trace(researcherAgent, {
  onStart: (input) => console.log('Starting:', input),
  onTool: (tool, args) => console.log('Tool call:', tool, args),
  onComplete: (output) => console.log('Completed:', output),
  onError: (error) => console.error('Error:', error)
});

// Collect metrics
const observedAgent = observe(researcherAgent, {
  metrics: ['latency', 'token_usage', 'tool_calls'],
  exporter: prometheusExporter
});
```

## Categorical Guarantees

VoltAgent ensures these categorical properties:

1. **Type Safety**: Zod schemas enforce input/output types
2. **Composability**: Agents compose via Kleisli arrows
3. **Naturality**: Handoffs preserve agent structure
4. **State Isolation**: Each agent has isolated state
5. **Determinism**: Same input + same seed = same trace
