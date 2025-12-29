---
title: Core Concepts Overview
description: The four pillars of categorical meta-prompting explained simply.
---

import { Card, CardGrid } from '@astrojs/starlight/components';

# Core Concepts

Categorical meta-prompting is built on four pillars from category theory. Don't worry—you don't need to understand the math. This page explains each concept in plain English.

## The Big Picture

```
Task → [Functor] → Prompt → [Monad] → Refined → [Comonad] → Output
                                ↑
                          [Quality: 0-1]
```

Think of it as a **pipeline** where each stage has a specific job:

<CardGrid>
  <Card title="Functor (F)" icon="right-arrow">
    **Transforms** your task into a structured prompt.
  </Card>
  <Card title="Monad (M)" icon="rocket">
    **Refines** the output iteratively until quality is met.
  </Card>
  <Card title="Comonad (W)" icon="document">
    **Extracts** relevant context from history.
  </Card>
  <Card title="Quality [0,1]" icon="approve-check">
    **Measures** everything with scores from 0 to 1.
  </Card>
</CardGrid>

## Why These Concepts?

Each concept solves a real problem:

| Problem | Concept | Solution |
|---------|---------|----------|
| "My prompts are inconsistent" | Functor | Deterministic transformation |
| "I keep tweaking until it's good" | Monad | Automated refinement loops |
| "I lose context between prompts" | Comonad | Context extraction |
| "How do I know if it's good enough?" | Quality | Measurable 0-1 scores |

## The Composition Operators

These operators let you combine commands:

| Operator | Name | What It Does |
|----------|------|--------------|
| `→` | Sequential | Run A, then run B with A's output |
| `\|\|` | Parallel | Run A and B simultaneously |
| `⊗` | Tensor | Combine A and B's outputs |
| `>=>` | Kleisli | Sequential with quality gates |

### Example

```bash
# Sequential: analyze, then design, then implement
/chain [/analyze→/design→/implement] "build feature"

# Parallel: run multiple approaches at once
/chain [/approach-a || /approach-b] "evaluate options"

# Quality-gated: refine at each step
/rmp @quality:0.85 [/analyze>=>design>=>implement] "critical system"
```

## Deep Dives

Ready to learn more? Each concept has its own page:

- **[Functors](/categorical-meta-prompting-oe/core-concepts/functors/)** — How tasks become prompts
- **[Monads](/categorical-meta-prompting-oe/core-concepts/monads/)** — Iterative refinement explained
- **[Comonads](/categorical-meta-prompting-oe/core-concepts/comonads/)** — Context extraction
- **[Quality Scores](/categorical-meta-prompting-oe/core-concepts/quality-scores/)** — Measuring output quality
- **[Composition](/categorical-meta-prompting-oe/core-concepts/composition/)** — Combining operations

## The "Aha!" Moment

The key insight is this: **prompts are not strings—they're transformations**.

When you write a prompt, you're defining how to transform a task into an output. Category theory gives us the tools to:

1. **Compose** these transformations reliably
2. **Measure** their quality
3. **Refine** them automatically
4. **Preserve** context across transformations

That's the magic. You get predictable, measurable, composable prompt engineering.
