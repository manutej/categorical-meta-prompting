---
title: Monads
description: Iterative refinement until quality is achieved.
---

import { Aside } from '@astrojs/starlight/components';

# Monads: Iterative Refinement

A **monad** enables iterative refinement—generating, evaluating, and improving until the output meets your quality threshold.

## Plain English

Think of a monad as a **while loop for quality**:

```
while quality < threshold:
    output = generate(prompt)
    quality = evaluate(output)
    if quality < threshold:
        prompt = refine(prompt, feedback)
```

## How It Works

```
Iteration 1: Generate → Evaluate (0.72) → Refine
Iteration 2: Generate → Evaluate (0.81) → Refine
Iteration 3: Generate → Evaluate (0.88) → Done!
```

At each iteration:
1. **Generate** output from the current prompt
2. **Evaluate** using the quality assessment
3. **Refine** the prompt based on what's missing

## The RMP Loop

RMP (Recursive Meta-Prompting) is the monad in action:

```bash
/rmp @quality:0.85 @max_iterations:5 "implement rate limiter"
```

This will:
- Generate an implementation
- Score it (correctness, clarity, completeness, efficiency)
- If below 0.85: identify weaknesses and refine
- Repeat until 0.85 or 5 iterations

<Aside type="tip">
Higher quality thresholds require more iterations but produce better results. Start with 0.8 for general tasks, use 0.9+ for critical code.
</Aside>

## Monad Laws

Monads guarantee three properties:

| Law | Meaning |
|-----|---------|
| Left identity | Starting fresh works correctly |
| Right identity | Ending works correctly |
| Associativity | Order of composition doesn't matter |

In practice, this means **RMP always converges to a fixed point** (or hits max iterations).

## Convergence Patterns

```yaml
CHECKPOINT_RMP_1:
  quality: 0.72
  status: CONTINUE

CHECKPOINT_RMP_2:
  quality: 0.81
  quality_delta: +0.09
  status: CONTINUE

CHECKPOINT_RMP_3:
  quality: 0.88
  quality_delta: +0.07
  status: CONVERGED
```

Watch for:
- **CONVERGED**: Quality threshold met
- **PLATEAU**: Quality stopped improving (fixed point)
- **MAX_ITERATIONS**: Hit the limit

## Kleisli Composition

The `>=>` operator chains monadic operations:

```bash
/rmp @quality:0.85 [/analyze>=>design>=>implement] "build feature"
```

Each stage must meet quality before passing to the next. This ensures **quality gates at every step**.

## In Practice

```python
from meta_prompting_engine.categorical import MonadicRefinement

refiner = MonadicRefinement(quality_threshold=0.85)
result = refiner.run("implement rate limiter")

print(f"Iterations: {result.iterations}")
print(f"Final quality: {result.quality}")
print(f"Convergence: {result.status}")
```

## Next

- **[Comonads](/categorical-meta-prompting-oe/core-concepts/comonads/)** — Context extraction
- **[Commands](/categorical-meta-prompting-oe/commands/rmp/)** — Using `/rmp` command
