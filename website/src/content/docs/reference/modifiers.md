---
title: Modifiers Reference
description: Complete reference for all command modifiers.
---

# Modifiers Reference

All modifiers follow the pattern `@name:value`.

## Core Modifiers

### @mode
Execution mode for the command.

| Value | Description |
|-------|-------------|
| `active` | Execute immediately (default) |
| `iterative` | Enable RMP refinement loop |
| `dry-run` | Preview without executing |
| `spec` | Generate YAML specification |

### @quality
Quality threshold for convergence (0.0 to 1.0).

```bash
/rmp @quality:0.85 "task"
```

### @max_iterations
Maximum refinement iterations.

```bash
/rmp @quality:0.9 @max_iterations:3 "task"
```

### @tier
Complexity tier (L1-L7).

| Tier | Complexity | Budget |
|------|------------|--------|
| L1 | Trivial | 1K |
| L2 | Simple | 2K |
| L3 | Moderate | 5K |
| L4 | Complex | 10K |
| L5 | Advanced | 15K |
| L6 | Expert | 20K |
| L7 | Research | 30K+ |

### @domain
Force specific domain classification.

| Value | Use Case |
|-------|----------|
| `ALGORITHM` | Data structures, algorithms |
| `SECURITY` | Auth, encryption, vulnerabilities |
| `API` | REST, GraphQL, endpoints |
| `DEBUG` | Error fixing, troubleshooting |
| `TESTING` | Unit tests, integration tests |

### @budget
Token budget override.

```bash
/meta @budget:15000 "large task"
```

### @template
Template components for prompt construction.

Format: `{context}+{mode}+{format}`

| Context | Mode | Format |
|---------|------|--------|
| expert | cot (chain-of-thought) | code |
| novice | direct | prose |
| research | structured | json |

Example:
```bash
/meta @template:{expert}+{cot}+{code} "implement algorithm"
```

## Combination Examples

```bash
# Full specification
/meta @mode:active @tier:L5 @domain:SECURITY @budget:20000 "auth system"

# Quality-focused
/rmp @quality:0.95 @max_iterations:5 @mode:iterative "critical code"

# Preview execution
/chain @mode:dry-run [/a→/b→/c] "workflow"
```
