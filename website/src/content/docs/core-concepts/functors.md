---
title: Functors
description: How tasks are transformed into structured prompts.
---

import { Aside } from '@astrojs/starlight/components';

# Functors: Task → Prompt

A **functor** transforms your task into a structured prompt while preserving the essential structure of your request.

## Plain English

Think of a functor as a **translator** that:
1. Takes your plain English task
2. Adds context, structure, and optimization
3. Produces a prompt optimized for the LLM

```
Input:  "implement rate limiter"
          ↓ [Functor F]
Output: Structured prompt with:
        - Domain classification (API/ALGORITHM)
        - Complexity tier (L3)
        - Template selection (expert + CoT)
        - Context injection
```

## Why It Matters

Without a functor, you write:
```
Write a rate limiter in Python.
```

With a functor, the system generates:
```
You are an expert API engineer. Implement a rate limiter with:
- Sliding window algorithm
- Thread-safe implementation
- Configurable thresholds
- Error handling for edge cases
- Unit tests demonstrating correctness

Think step by step about the design before implementing.
```

The functor automatically:
- Detected this is an API/algorithm task
- Selected expert context and chain-of-thought mode
- Added completeness requirements
- Structured the output expectations

## The Key Property

Functors must preserve **composition**:

```
F(g ∘ f) = F(g) ∘ F(f)
```

In plain terms: if you compose two tasks, the functor should produce the same result as composing two prompts.

<Aside type="note">
This property guarantees that chained commands work predictably. You can trust that `/chain [/a→/b]` will behave the same as running `/a` then `/b`.
</Aside>

## In Practice

```python
from meta_prompting_engine.categorical import Functor

# The functor transforms tasks to prompts
functor = Functor()
prompt = functor.apply("implement rate limiter")

print(prompt.template)    # "expert + cot"
print(prompt.domain)      # "API"
print(prompt.tier)        # "L3"
```

## Modifiers That Affect Functors

| Modifier | Effect |
|----------|--------|
| `@tier:L5` | Force higher complexity treatment |
| `@domain:SECURITY` | Force security-focused prompt |
| `@template:{expert}+{cot}` | Specify exact template |

Example:
```bash
/meta @domain:SECURITY @tier:L5 "implement authentication"
```

## Next

- **[Monads](/categorical-meta-prompting-oe/core-concepts/monads/)** — How refinement works
- **[Commands](/categorical-meta-prompting-oe/commands/meta/)** — Using `/meta` command
