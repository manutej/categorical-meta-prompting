---
description: Chain multiple slash commands together, passing output as input to next command
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [/cmd1→/cmd2→/cmd3] @mode:[mode] [initial-input]
---

# Prompt Chain Executor

Execute a sequence of slash commands using categorical composition operators.

## Unified Syntax

```
/chain [/cmd1→/cmd2→/cmd3] @mode:active "initial input"
```

### Composition Operators

| Operator | Unicode | Meaning | Categorical Type |
|----------|---------|---------|------------------|
| `→` | U+2192 | Sequence (Kleisli) | Output of A → Input of B |
| `then` | - | Sequence (legacy) | Same as → |
| `\|\|` | - | Parallel | Execute concurrently |
| `>=>` | - | Kleisli refinement | Monadic with quality gates |

### Supported Modifiers

| Modifier | Default | Description |
|----------|---------|-------------|
| `@mode:` | active | Execution mode: active, dry-run, spec |
| `@budget:` | auto | Total token budget for chain |
| `@variance:` | 20% | Acceptable budget variance |
| `@quality:` | - | Quality gate between stages |

---

## Chain Specification

**Arguments**: $ARGUMENTS

---

## Parse Chain

From your input, I detect the following chain structure:

### Operator Detection

```
Input: $ARGUMENTS

Detected Operators:
- → (sequence): Commands execute sequentially, output → input
- || (parallel): Commands execute concurrently
- >=> (Kleisli): Commands with quality-gated refinement
- "then" (legacy): Treated as →
```

### Chain Structure

| Position | Command | Input Source | Operator |
|----------|---------|--------------|----------|
| 1 | [first command] | [initial input] | (start) |
| 2 | [second command] | [output from 1] | → |
| 3 | [third command] | [output from 2] | → |
| ... | ... | ... | ... |

---

## Mode: Dry-Run

*If @mode:dry-run was specified, show plan and exit:*

```yaml
CHAIN_PLAN:
  stages: [/cmd1, /cmd2, /cmd3]
  operators: [→, →]
  categorical_structure: Kleisli composition
  estimated_budget: [total estimate]
  data_flow:
    - {stage: 1, input: "initial", output: "→ stage 2"}
    - {stage: 2, input: "from stage 1", output: "→ stage 3"}
    - {stage: 3, input: "from stage 2", output: "final"}
  exit: Plan generated, no execution
```

---

## Mode: Spec

*If @mode:spec was specified, generate specification and exit:*

```yaml
name: chain-[hash]
type: sequential_composition
categorical_structure:
  functor: F(Command) → Prompt
  composition: Kleisli (→)
  law: (f → g) → h = f → (g → h)  # Associativity
stages:
  - {name: stage_1, command: /cmd1, operator: start}
  - {name: stage_2, command: /cmd2, operator: →}
  - {name: stage_3, command: /cmd3, operator: →}
quality_gates: [if @quality: specified]
budget: [if @budget: specified]
```

---

## Mode: Active (Default)

### How Chaining Works (Categorical)

```
/cmd1 [input]
    │
    ↓ output becomes context (Kleisli →)
    │
/cmd2 [context from cmd1]
    │
    ↓ output becomes context (Kleisli →)
    │
/cmd3 [context from cmd2]
    │
    ↓
Final Result
```

**Categorical Law**: `(f → g) → h = f → (g → h)` (Associativity)

Each command is a morphism in the prompt category. Chaining them = Kleisli composition.

---

## Execute Chain

### Stage 1: [Command 1]

```
Input: [initial input]
Executing: /[command1]
Operator: (start)
```

[Execute first command here]

**Output from Stage 1:**
```
[capture output - this becomes input for stage 2]
```

**Checkpoint:**
```yaml
CHAIN_CHECKPOINT_1:
  command: /[cmd1]
  status: COMPLETE
  quality: [if assessed]
  tokens_used: [estimate]
  output_summary: [brief]
```

---

### Stage 2: [Command 2]

```
Input: [output from stage 1]
Executing: /[command2]
Operator: → (sequence)
```

[Execute second command with context from first]

**Output from Stage 2:**
```
[capture output - this becomes input for stage 3]
```

**Checkpoint:**
```yaml
CHAIN_CHECKPOINT_2:
  command: /[cmd2]
  status: COMPLETE
  quality: [if assessed]
  tokens_used: [estimate]
  output_summary: [brief]
```

---

### Stage 3: [Command 3] (if specified)

```
Input: [output from stage 2]
Executing: /[command3]
Operator: → (sequence)
```

[Execute third command with context from second]

**Output from Stage 3:**
```
[capture output - final result]
```

**Checkpoint:**
```yaml
CHAIN_CHECKPOINT_3:
  command: /[cmd3]
  status: COMPLETE
  quality: [if assessed]
  tokens_used: [estimate]
  output_summary: [brief]
```

---

## Parallel Execution (|| operator)

When `||` is detected, execute commands concurrently:

```
[/cmdA || /cmdB || /cmdC]
         ↓
    ┌────┼────┐
    ↓    ↓    ↓
  cmdA cmdB cmdC  (parallel)
    ↓    ↓    ↓
    └────┼────┘
         ↓
    [aggregate results]
```

**Aggregation Strategy**: Concatenate outputs with headers, or merge if structured.

---

## Kleisli Refinement (>=> operator)

When `>=>` is detected, apply quality-gated monadic composition:

```
[/analyze >=> /design >=> /implement]

Each stage:
1. Execute command
2. Assess quality
3. If quality < @quality: threshold, refine before continuing
4. Pass refined output to next stage
```

---

## Chain Summary

```
╔══════════════════════════════════════════════════════════════╗
║ CHAIN RESULT                                                  ║
╠══════════════════════════════════════════════════════════════╣
║ Chain: /cmd1 → /cmd2 → /cmd3                                  ║
║ Composition: Kleisli (→)                                      ║
║ Total Stages: N                                               ║
║ Status: [COMPLETE | PARTIAL | FAILED]                         ║
╚══════════════════════════════════════════════════════════════╝
```

| Stage | Command | Status | Quality | Output Summary |
|-------|---------|--------|---------|----------------|
| 1 | /cmd1 | ✅ | [score] | [brief] |
| 2 | /cmd2 | ✅ | [score] | [brief] |
| 3 | /cmd3 | ✅ | [score] | [brief] |

**Final Result:**
```
[last stage output]
```

---

## Usage Examples

### Sequential Composition (→)

```bash
# Using → operator (preferred)
/chain [/debug→/review] "TypeError in auth.py line 42"

# Using Unicode arrow
/chain [/build-prompt→/rmp] "implement rate limiter"

# Multiple stages
/chain [/analyze→/plan→/implement→/test] "add caching layer"
```

### Legacy Syntax (then)

```bash
# Still supported for backward compatibility
/chain "/debug then /review" "TypeError in auth.py"
/chain "/build-prompt then /rmp" "implement feature"
```

### Parallel Composition (||)

```bash
# Execute reviews in parallel
/chain [/review-security || /review-performance] "api/auth.py"

# Multiple parallel analyses
/chain [/analyze-frontend || /analyze-backend || /analyze-db] "audit system"
```

### Kleisli Refinement (>=>)

```bash
# Quality-gated chain
/chain @quality:0.85 [/analyze>=>/ design>=>/ implement] "build auth"

# Each stage refines until quality threshold before continuing
```

### With Modifiers

```bash
# Dry-run preview
/chain @mode:dry-run [/debug→/fix→/test] "error in payment.py"

# With budget
/chain @budget:20000 [/research→/design→/implement] "new feature"

# Generate spec only
/chain @mode:spec [/analyze→/plan] "refactoring project"
```

### Mixed Operators

```bash
# Sequential with parallel sub-chain
/chain [/research→(/frontend || /backend)→/integrate] "full-stack feature"

# Note: Parentheses group parallel operations within sequence
```

---

## Backward Compatibility

Old syntax still works:
```bash
/chain "/cmd1 then /cmd2 then /cmd3" "input"
```

New unified syntax is preferred:
```bash
/chain [/cmd1→/cmd2→/cmd3] "input"
```

Both produce identical Kleisli composition.

---

## Categorical Laws Verified

1. **Identity**: `id → f = f = f → id`
2. **Associativity**: `(f → g) → h = f → (g → h)`
3. **Quality Degradation**: `quality(f → g) <= min(quality(f), quality(g))`
