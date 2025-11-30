# Categorical Meta-Prompting Skills

20 Claude Code skills implementing the categorical meta-prompting framework.

## Skills Overview

| Skill | Size | Description |
|-------|------|-------------|
| **arxiv-categorical-ai** | 11KB | Systematic analysis patterns for categorical AI papers |
| **categorical-meta-prompting** | 12KB | **Core framework: F (Functor), M (Monad), W (Comonad), [0,1]-enriched** |
| **categorical-property-testing** | 10KB | Property-based testing for functor/monad laws with fp-ts |
| **cc2-research-framework** | 14KB | CC2.0 seven-function research workflow |
| **discopy-nlp** | 2KB | DisCoPy categorical quantum NLP string diagrams |
| **dspy-categorical** | 10KB | DSPy compositional prompt optimization |
| **dynamic-prompt-registry** | 9KB | Reader monad for runtime prompt lookup and composition |
| **effect-ts-ai** | 10KB | @effect/ai integration patterns |
| **guidance-grammars** | 7KB | Grammar-constrained generation |
| **hasktorch-typed** | 7KB | Type-safe tensor operations in Haskell |
| **langgraph-orchestration** | 9KB | Stateful multi-agent graphs |
| **llm4s-scala** | 8KB | Scala functional LLM interfaces |
| **lmql-constraints** | 6KB | Constraint-guided generation DSL |
| **mcp-categorical** | 9KB | MCP server categorical patterns |
| **polynomial-functors** | 7KB | Spivak-Niu polynomial functor implementations |
| **prompt-benchmark** | 10KB | Systematic prompt evaluation framework |
| **prompt-dsl** | 10KB | DSL for categorical prompt composition |
| **quality-enriched-prompting** | 11KB | [0,1]-enriched category optimization |
| **recursive-meta-prompting** | 13KB | RMP with monadic refinement loops |
| **voltagent-multiagent** | 8KB | Multi-agent system design |

## Usage

Skills are automatically triggered based on task context. Example invocations:

```
Skill: "categorical-property-testing"
Skill: "effect-ts-ai"
Skill: "langgraph-orchestration"
```

## Framework Alignment

These skills implement the **Unified Categorical Framework**:

### Categorical Layer (F, M, W, [0,1])
- **Functor F**: `categorical-meta-prompting`, `dynamic-prompt-registry`
- **Monad M**: `recursive-meta-prompting`, `dspy-categorical`
- **Comonad W**: `cc2-research-framework` (OBSERVE function)
- **[0,1]-Enriched**: `quality-enriched-prompting`

### Workflow Mapping
1. **F(task)** - Use `dynamic-prompt-registry` for task→prompt mapping
2. **M.unit** - Initialize with `prompt-dsl` for compositional prompts
3. **M.bind(refine)** - Apply `recursive-meta-prompting` for iteration
4. **W.extract** - Deploy `langgraph-orchestration` for execution
5. **Verify Laws** - Validate with `categorical-property-testing`

### Verified Laws (15/15 Tests Pass)
All categorical laws verified via property-based testing:
- Functor identity & composition
- Monad left/right identity & associativity
- Comonad counit laws & coassociativity
- [0,1]-enriched tensor associativity & unit laws

## Source

Generated from Claude Desktop skill exports (.skill files).
