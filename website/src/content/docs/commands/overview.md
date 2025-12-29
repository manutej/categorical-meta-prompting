---
title: Commands Overview
description: All available commands and the unified syntax.
---

import { Aside } from '@astrojs/starlight/components';

# Commands Overview

All commands follow the **unified syntax pattern**:

```bash
/<command> @modifier:value [composition] "task"
```

## Core Commands

| Command | Purpose | Key Modifiers |
|---------|---------|---------------|
| [`/meta`](/categorical-meta-prompting-oe/commands/meta/) | Basic meta-prompting | `@tier:`, `@template:` |
| [`/rmp`](/categorical-meta-prompting-oe/commands/rmp/) | Recursive refinement | `@quality:`, `@max_iterations:` |
| [`/chain`](/categorical-meta-prompting-oe/commands/chain/) | Command composition | `[→, \|\|, ⊗, >=>]` |

## Available Modifiers

| Modifier | Values | Default | Description |
|----------|--------|---------|-------------|
| `@mode:` | active, iterative, dry-run, spec | active | Execution mode |
| `@quality:` | 0.0-1.0 | 0.8 | Quality threshold |
| `@tier:` | L1-L7 | auto | Complexity tier |
| `@budget:` | integer | auto | Token budget |
| `@max_iterations:` | integer | 5 | Max RMP iterations |
| `@domain:` | ALGORITHM, SECURITY, API, DEBUG | auto | Domain |
| `@template:` | {context}+{mode}+{format} | auto | Template |

## Execution Modes

### @mode:active (Default)
Execute immediately with auto-detection:
```bash
/meta "implement rate limiter"
```

### @mode:iterative
Enable RMP refinement loop:
```bash
/rmp @mode:iterative @quality:0.85 "optimize algorithm"
```

### @mode:dry-run
Preview without executing:
```bash
/chain @mode:dry-run [/a→/b→/c] "task"
```

### @mode:spec
Generate YAML specification:
```bash
/meta @mode:spec "complex task"
```

## Composition Operators

| Operator | Name | Quality Rule |
|----------|------|--------------|
| `→` | Sequential | `min(q₁, q₂)` |
| `\|\|` | Parallel | `mean(q₁, q₂)` |
| `⊗` | Tensor | `min(q₁, q₂)` |
| `>=>` | Kleisli | Refines each step |

## Complexity Tiers

| Tier | Description | Budget |
|------|-------------|--------|
| L1 | Trivial | 1K tokens |
| L2 | Simple | 2K tokens |
| L3 | Moderate | 5K tokens |
| L4 | Complex | 10K tokens |
| L5 | Advanced | 15K tokens |
| L6 | Expert | 20K tokens |
| L7 | Research | 30K+ tokens |

<Aside type="tip">
Let the system auto-detect tier when possible. Override only when you know the task complexity.
</Aside>

## Quick Reference

```bash
# Simple task
/meta "implement feature"

# With quality gate
/rmp @quality:0.85 "critical code"

# Chained operations
/chain [/analyze→/design→/implement] "build system"

# Parallel execution
/chain [/test-a || /test-b || /test-c] "validate"

# Full syntax
/meta @mode:active @tier:L4 @domain:API "endpoint"
```

## Detailed Command Pages

- [`/meta`](/categorical-meta-prompting-oe/commands/meta/) — Basic meta-prompting
- [`/rmp`](/categorical-meta-prompting-oe/commands/rmp/) — Recursive refinement
- [`/chain`](/categorical-meta-prompting-oe/commands/chain/) — Command composition
