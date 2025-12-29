---
title: Quality Scores
description: Measuring output quality with [0,1] enrichment.
---

import { Aside } from '@astrojs/starlight/components';

# Quality Scores: [0,1] Enrichment

Every output in the framework has a **quality score** from 0 to 1. This isn't subjective—it's computed using a multi-dimensional assessment.

## The Four Dimensions

| Dimension | Weight | Question |
|-----------|--------|----------|
| **Correctness** | 40% | Does it solve the problem? |
| **Clarity** | 25% | Is it understandable? |
| **Completeness** | 20% | Are edge cases handled? |
| **Efficiency** | 15% | Is it well-designed? |

## Aggregate Formula

```
aggregate = 0.40 × correctness
          + 0.25 × clarity
          + 0.20 × completeness
          + 0.15 × efficiency
```

## Score Thresholds

| Score | Rating | Action |
|-------|--------|--------|
| **0.9+** | Excellent | Production ready |
| **0.8-0.9** | Good | Minor polish needed |
| **0.7-0.8** | Acceptable | Review recommended |
| **0.6-0.7** | Poor | Refinement required |
| **Below 0.6** | Failed | Restructure approach |

<Aside type="tip">
Use `@quality:0.8` for general development, `@quality:0.9` for production code, `@quality:0.95` for critical systems.
</Aside>

## Composition Rules

Quality degrades through composition:

| Operation | Rule | Example |
|-----------|------|---------|
| Sequential `→` | `min(q₁, q₂)` | 0.9 → 0.85 = 0.85 |
| Parallel `\|\|` | `mean(q₁, q₂)` | 0.9 \|\| 0.8 = 0.85 |
| Tensor `⊗` | `min(q₁, q₂)` | 0.9 ⊗ 0.85 = 0.85 |
| Kleisli `>=>` | Improves | Each step refines |

This means: **your pipeline is only as good as its weakest link** (except for Kleisli, which refines).

## Checkpoint Format

Every operation produces a quality checkpoint:

```yaml
CHECKPOINT_RMP_3:
  command: /rmp
  iteration: 3
  quality:
    correctness: 0.92
    clarity: 0.88
    completeness: 0.85
    efficiency: 0.90
    aggregate: 0.89
  quality_delta: +0.07
  status: CONVERGED
```

## Using Quality Gates

### Basic threshold

```bash
/rmp @quality:0.85 "implement feature"
# Iterate until 0.85 or max iterations
```

### Custom weights

```python
engine.execute(
    task="implement feature",
    quality_weights={
        "correctness": 0.50,  # More weight on correctness
        "clarity": 0.20,
        "completeness": 0.20,
        "efficiency": 0.10
    }
)
```

### Domain-specific thresholds

| Domain | Recommended Threshold |
|--------|----------------------|
| Prototype | 0.7 |
| Development | 0.8 |
| Production | 0.9 |
| Security-critical | 0.95 |

## Quality Trends

Watch for patterns in your checkpoints:

- **Improving**: Quality going up each iteration (good)
- **Plateau**: Quality stable (fixed point reached)
- **Degrading**: Quality going down (restructure needed)

```
Iter 1: 0.72 (CONTINUE)
Iter 2: 0.81 (+0.09, CONTINUE)
Iter 3: 0.88 (+0.07, CONVERGED)
```

## Next

- **[Composition](/categorical-meta-prompting-oe/core-concepts/composition/)** — Combining operations
- **[Commands](/categorical-meta-prompting-oe/commands/rmp/)** — Using `/rmp` with quality gates
