---
title: Comonads
description: Extracting context from execution history.
---

# Comonads: Context Extraction

A **comonad** extracts relevant context from your execution history, making each prompt smarter based on what came before.

## Plain English

Think of a comonad as a **memory system** that:
1. Remembers previous executions
2. Extracts what's relevant to the current task
3. Injects that context into new prompts

```
History: [debug auth.py, fix imports, test auth]
          ↓ [Comonad W]
Context: "Working on auth module, Python, testing phase"
```

## Why It Matters

Without comonads:
```bash
/meta "add error handling"
# LLM has no idea what code you're working on
```

With comonads:
```bash
/meta "add error handling"
# System knows: auth.py, Python, your coding style, recent fixes
```

## How It Works

The comonad has two key operations:

| Operation | What It Does |
|-----------|--------------|
| **extract** | Pull the current context from history |
| **extend** | Apply a function across all possible contexts |

```
History → [extract] → Current Context
History → [extend f] → Contextualized Output
```

## Context Sources

The comonad pulls from:

- **Recent commands**: What you've been doing
- **File context**: What files you've touched
- **Domain patterns**: What type of work (API, security, testing)
- **Quality trends**: What quality scores you've achieved
- **Error history**: What went wrong before

## In Practice

```python
from meta_prompting_engine.categorical import Comonad

comonad = Comonad(history=execution_history)

# Extract current context
context = comonad.extract()
print(context.domain)     # "authentication"
print(context.language)   # "python"
print(context.recent)     # ["debug auth.py", "fix imports"]

# Apply context to a new task
result = comonad.extend(lambda ctx: generate_prompt(ctx, task))
```

## Implicit vs Explicit Context

**Implicit** (automatic):
```bash
/meta "add tests"
# Comonad infers: what to test, testing patterns you use
```

**Explicit** (manual override):
```bash
/meta @context:"{file:auth.py}+{style:pytest}" "add tests"
```

## The Comonad Laws

| Law | Meaning |
|-----|---------|
| `extract ∘ extend f = f` | Extracting after extending gives the function result |
| `extend extract = id` | Extending with extract is identity |
| Associativity | Order of extensions doesn't matter |

These laws ensure context extraction is **consistent and predictable**.

## Graded Comonads

For fine-grained control, we use **graded comonads** that weight context by relevance:

```
Recent context: 90% weight
Older context:  50% weight
Ancient context: 10% weight
```

This prevents old, irrelevant context from polluting new tasks.

## Next

- **[Quality Scores](/categorical-meta-prompting-oe/core-concepts/quality-scores/)** — How we measure output
- **[Composition](/categorical-meta-prompting-oe/core-concepts/composition/)** — Combining operations
