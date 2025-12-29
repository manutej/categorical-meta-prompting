---
title: Composition
description: Combining operations with categorical operators.
---

# Composition: Combining Operations

The power of categorical meta-prompting comes from **composition**—combining simple operations into complex workflows.

## The Four Operators

| Operator | Symbol | Meaning |
|----------|--------|---------|
| **Sequential** | `→` | Run A, then B with A's output |
| **Parallel** | `\|\|` | Run A and B simultaneously |
| **Tensor** | `⊗` | Combine A and B's outputs |
| **Kleisli** | `>=>` | Sequential with quality refinement |

## Sequential (→)

Run operations in order, passing output forward:

```bash
/chain [/analyze→/design→/implement] "build feature"
```

Execution:
1. `/analyze "build feature"` → analysis
2. `/design [analysis]` → design
3. `/implement [design]` → code

**Quality rule**: `min(q₁, q₂, q₃)`

## Parallel (||)

Run operations simultaneously:

```bash
/chain [/security-review || /perf-review || /style-review] "api/auth.py"
```

Execution:
- All three reviews run at the same time
- Results are collected and merged

**Quality rule**: `mean(q₁, q₂, q₃)`

## Tensor (⊗)

Combine outputs into a structured result:

```bash
/chain [/frontend ⊗ /backend ⊗ /database] "user profile feature"
```

Execution:
- Each component runs
- Outputs are combined into a coherent whole

**Quality rule**: `min(q₁, q₂, q₃)`

## Kleisli (>=>)

Sequential with quality gates at each step:

```bash
/rmp @quality:0.85 [/analyze>=>design>=>implement] "critical system"
```

Execution:
1. `/analyze` → evaluate quality
2. If quality < 0.85: refine, else continue
3. `/design [analysis]` → evaluate quality
4. If quality < 0.85: refine, else continue
5. `/implement [design]` → evaluate quality

**Quality rule**: Each step must meet threshold before proceeding

## Mixed Composition

You can combine operators:

```bash
/chain [R→(D||F)→I→T] "full-stack feature"
```

This means:
1. R (Research) runs first
2. D (Design) and F (Frontend) run in parallel
3. I (Implement) runs with both outputs
4. T (Test) runs last

## Practical Examples

### Code Review Pipeline

```bash
/chain [/analyze→(/security||/perf||/style)→/summarize] "src/"
```

### Feature Development

```bash
/chain [/spec→/design→(/frontend⊗/backend)→/integrate→/test] "auth"
```

### Quality-Critical Path

```bash
/rmp @quality:0.9 [/research>=>design>=>implement>=>test] "payment"
```

## Composition Laws

The framework guarantees:

| Law | Meaning |
|-----|---------|
| Associativity | `(a→b)→c = a→(b→c)` |
| Identity | `id→f = f = f→id` |
| Distributivity | `a→(b\|\|c) = (a→b)\|\|(a→c)` |

These laws ensure **predictable behavior** regardless of how you parenthesize.

## Quality Through Composition

Remember:
- `→` and `⊗` degrade to `min()` — weakest link
- `||` averages — spreads risk
- `>=>` improves — quality gates

Choose operators based on your quality needs:
- Use `>=>` for critical paths
- Use `||` for redundant validation
- Use `→` for simple pipelines

## Next

- **[Commands Reference](/categorical-meta-prompting-oe/commands/overview/)** — Full command syntax
- **[Examples](/categorical-meta-prompting-oe/examples/game-of-24/)** — Real-world usage
