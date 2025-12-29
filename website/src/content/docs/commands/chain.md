---
title: /chain Command
description: Compose multiple commands with categorical operators.
---

# /chain Command

The `/chain` command lets you **compose multiple operations** using categorical operators.

## Syntax

```bash
/chain [operation1 OP operation2 OP ...] "task"
```

## Operators

| Operator | Name | Behavior |
|----------|------|----------|
| `→` | Sequential | A then B, passing output |
| `\|\|` | Parallel | A and B simultaneously |
| `⊗` | Tensor | Combine A and B outputs |
| `>=>` | Kleisli | Sequential with quality gates |

## Examples

### Sequential pipeline
```bash
/chain [/analyze→/design→/implement→/test] "build feature"
```

### Parallel execution
```bash
/chain [/security || /performance || /style] "review code"
```

### Mixed composition
```bash
/chain [/research→(/frontend||/backend)→/integrate] "full-stack"
```

### With quality gates
```bash
/chain @quality:0.85 [/analyze>=>design>=>implement] "critical"
```

## Quality Rules

| Operator | Quality Calculation |
|----------|---------------------|
| `→` | `min(q₁, q₂)` |
| `\|\|` | `mean(q₁, q₂)` |
| `⊗` | `min(q₁, q₂)` |
| `>=>` | Each step refined |

## Dry Run

Preview execution without running:

```bash
/chain @mode:dry-run [/a→/b→/c] "task"
```

Output:
```yaml
execution_plan:
  stages:
    - /a: Analyze task
    - /b: Design solution
    - /c: Implement code
  operators: [→, →]
  estimated_budget: 12000
  quality_rule: min(q_a, q_b, q_c)
```

## Practical Recipes

### Code review pipeline
```bash
/chain [/analyze→(/security||/perf||/style)→/summarize] "src/"
```

### Feature development
```bash
/chain [/spec→/design→(/fe⊗/be)→/integrate→/test] "auth"
```

### Debug workflow
```bash
/chain [/diagnose→/hypothesize→/fix→/verify] "TypeError"
```

## When to Use

- **Multi-step workflows**: Analysis → Design → Implementation
- **Parallel reviews**: Multiple perspectives at once
- **Complex features**: Coordinated frontend/backend work
