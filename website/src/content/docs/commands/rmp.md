---
title: /rmp Command
description: Recursive meta-prompting with quality gates.
---

# /rmp Command

The `/rmp` command enables **Recursive Meta-Prompting**—iterative refinement until your quality threshold is met.

## Syntax

```bash
/rmp @quality:threshold @max_iterations:n "task"
```

## Examples

### Basic quality gate
```bash
/rmp @quality:0.85 "implement rate limiter"
```

### Higher quality threshold
```bash
/rmp @quality:0.95 "implement payment processing"
```

### With iteration limit
```bash
/rmp @quality:0.9 @max_iterations:3 "optimize algorithm"
```

### Kleisli composition
```bash
/rmp @quality:0.85 [/analyze>=>design>=>implement] "build auth"
```

## Modifiers

| Modifier | Values | Default |
|----------|--------|---------|
| `@quality:` | 0.0-1.0 | 0.8 |
| `@max_iterations:` | 1-10 | 5 |
| `@mode:` | active, iterative, dry-run, spec | iterative |

## How It Works

```
┌─────────────────────────────────────────┐
│ RMP Loop                                │
├─────────────────────────────────────────┤
│ 1. Generate output                      │
│ 2. Evaluate quality → [0,1]             │
│ 3. If quality ≥ threshold: CONVERGE     │
│ 4. Else: Extract feedback, refine       │
│ 5. Repeat until threshold or max iters  │
└─────────────────────────────────────────┘
```

## Output

Each iteration produces a checkpoint:

```yaml
CHECKPOINT_RMP_1:
  iteration: 1
  quality:
    aggregate: 0.72
  status: CONTINUE

CHECKPOINT_RMP_2:
  iteration: 2
  quality:
    aggregate: 0.81
  quality_delta: +0.09
  status: CONTINUE

CHECKPOINT_RMP_3:
  iteration: 3
  quality:
    aggregate: 0.88
  quality_delta: +0.07
  status: CONVERGED
```

## Status Values

| Status | Meaning |
|--------|---------|
| `CONTINUE` | Quality below threshold, refining |
| `CONVERGED` | Quality threshold met |
| `PLATEAU` | Quality stopped improving |
| `MAX_ITERATIONS` | Hit iteration limit |

## Recommended Thresholds

| Use Case | Threshold |
|----------|-----------|
| Prototype | 0.7 |
| Development | 0.8 |
| Production | 0.9 |
| Critical | 0.95 |

## When to Use

- **Quality-critical code**: When "good enough" isn't good enough
- **Complex tasks**: When first attempt rarely succeeds
- **Production code**: When you need confidence in output
