---
title: /meta Command
description: Basic categorical meta-prompting command.
---

# /meta Command

The `/meta` command transforms your task into an optimized prompt using categorical meta-prompting.

## Syntax

```bash
/meta @modifier:value "task description"
```

## Examples

### Basic usage
```bash
/meta "implement rate limiter"
```

### With tier override
```bash
/meta @tier:L5 "implement microservices gateway"
```

### With domain specification
```bash
/meta @domain:SECURITY "implement authentication"
```

### With template
```bash
/meta @template:{expert}+{cot} "complex algorithm"
```

## Modifiers

| Modifier | Values | Default |
|----------|--------|---------|
| `@mode:` | active, dry-run, spec | active |
| `@tier:` | L1-L7 | auto |
| `@domain:` | ALGORITHM, SECURITY, API, DEBUG, TESTING | auto |
| `@template:` | {context}+{mode}+{format} | auto |
| `@budget:` | integer | auto |

## Output

The command produces:
- Transformed prompt
- Execution output
- Quality checkpoint

```yaml
CHECKPOINT_META_1:
  command: /meta
  quality:
    correctness: 0.88
    clarity: 0.85
    completeness: 0.82
    efficiency: 0.87
    aggregate: 0.86
  budget:
    used: 3200
    tier: L3
```

## When to Use

- **Simple tasks**: Single-shot implementations
- **Quick prototypes**: When iteration isn't needed
- **Exploration**: Understanding task complexity

For quality-critical tasks, use [`/rmp`](/categorical-meta-prompting-oe/commands/rmp/) instead.
