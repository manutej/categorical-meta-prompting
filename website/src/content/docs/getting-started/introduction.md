---
title: Introduction
description: What is categorical meta-prompting and why should you care?
---

import { Aside } from '@astrojs/starlight/components';

# What is Categorical Meta-Prompting?

**Categorical meta-prompting** is a framework that brings mathematical rigor to prompt engineering. Instead of trial-and-error prompt crafting, you get **predictable, composable, measurable** results.

<Aside type="tip">
You don't need to understand category theory to use this framework. Think of it like using a calculator—you don't need to understand transistors to add numbers.
</Aside>

## The Problem We Solve

Traditional prompt engineering is:

- **Unpredictable**: Same prompt, different results
- **Non-composable**: Can't chain prompts reliably
- **Unmeasurable**: "Good enough" is subjective
- **Context-blind**: History is lost between prompts

## Our Solution

This framework provides:

| Problem | Solution |
|---------|----------|
| Unpredictable | **Functors** transform tasks to prompts deterministically |
| Non-composable | **Operators** chain commands: `→`, `\|\|`, `⊗`, `>=>` |
| Unmeasurable | **Quality scores** from 0-1 on every output |
| Context-blind | **Comonads** extract context from history |

## The Four Pillars

### 1. Functor (F)
**Transforms tasks into structured prompts.**

Think of it as a translator that turns your plain English task into an optimized prompt for the LLM.

```
Task: "implement rate limiter"
  ↓ [Functor]
Prompt: Structured, context-aware, domain-optimized prompt
```

### 2. Monad (M)
**Enables iterative refinement.**

Like a while loop that keeps improving until quality is good enough.

```
Prompt → Generate → Evaluate (0.72) → Refine → Evaluate (0.88) → Done!
```

### 3. Comonad (W)
**Extracts context from history.**

Remembers what worked before and applies that knowledge to new tasks.

### 4. Quality Enrichment [0,1]
**Measures everything with scores.**

Every output gets a quality score:
- **0.9+**: Excellent, production-ready
- **0.8-0.9**: Good, minor polish needed
- **0.7-0.8**: Acceptable, review recommended
- **Below 0.7**: Needs work

## How It Works in Practice

```bash
# Simple: Just run a meta-prompt
/meta "implement rate limiter"

# With quality gate: Keep refining until 0.85
/rmp @quality:0.85 "optimize this algorithm"

# Composed: Chain multiple commands
/chain [/analyze→/design→/implement→/test] "build auth system"
```

## What's Next?

- **[Quick Start](/categorical-meta-prompting-oe/getting-started/quickstart/)** — Run your first meta-prompt in 5 minutes
- **[Core Concepts](/categorical-meta-prompting-oe/core-concepts/overview/)** — Deep dive into the four pillars
