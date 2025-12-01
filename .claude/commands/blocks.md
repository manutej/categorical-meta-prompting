---
description: Compose atomic blocks into custom workflows with full control over execution
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [block1 → block2 → ...] @mode:[mode] "task"
---

# Atomic Block Composition Engine

Compose atomic blocks into custom workflows. This command provides Layer 3 (power user) access to the atomic block system.

```
Skill: atomic-blocks
```

## Unified Syntax

```
/blocks [block_composition] @mode:active "task description"
```

## Task

$ARGUMENTS

---

## Supported Modifiers

| Modifier | Default | Description |
|----------|---------|-------------|
| `@mode:` | active | Execution mode: active, dry-run, spec, validate |
| `@quality:` | 0.8 | Quality threshold for >=> operator |
| `@budget:` | auto | Token budget for entire composition |
| `@catch:` | halt | Error handling: halt, log, retry:N, skip |
| `@fallback:` | - | Recovery: return-best, return-last, empty |
| `@merge:` | concatenate | Parallel merge: concatenate, vote, weighted |

---

## Available Blocks

### Assessment Layer

| Block | Signature | Purpose |
|-------|-----------|---------|
| `assess_difficulty` | Task → [0,1] | Evaluate task complexity |
| `assess_domain` | Task → Domain | Classify task domain |
| `assess_quality` | Output → QualityVector | Multi-dimensional quality |
| `select_tier` | (Difficulty, Domain) → Tier | Map to L1-L7 |

### Transformation Layer

| Block | Signature | Purpose |
|-------|-----------|---------|
| `select_strategy` | Tier → Strategy | Choose prompting strategy |
| `build_template` | (Context, Strategy) → Template | Assemble template |
| `apply_transform` | (Template, Task) → Prompt | Apply functor F |
| `execute_prompt` | Prompt → Output | Execute and capture |

### Refinement Layer

| Block | Signature | Purpose |
|-------|-----------|---------|
| `evaluate_convergence` | (Quality, Threshold) → Status | Check convergence |
| `extract_improvement` | (Output, Quality) → Direction | Identify gaps |
| `apply_refinement` | (Output, Direction) → Output | Monad bind |
| `aggregate_iterations` | [Output] → BestOutput | Select best |

### Composition Operators

| Operator | Symbol | Meaning |
|----------|--------|---------|
| Sequence | `→` | Output of A becomes input to B |
| Parallel | `\|\|` | Execute concurrently, merge results |
| Kleisli | `>=>` | Quality-gated sequential |
| Tensor | `⊗` | Combine capabilities |

---

## Mode: Validate

*If @mode:validate, check composition without executing:*

```yaml
COMPOSITION_VALIDATION:
  composition: [parsed block structure]
  valid: true/false
  errors: [if any]
  type_flow:
    - block: assess_difficulty
      input: Task
      output: DifficultyScore
    - block: select_tier
      input: DifficultyScore
      output: Tier
  estimated_budget: [tokens]
  estimated_quality: [0-1]
```

---

## Mode: Dry-Run

*If @mode:dry-run, show execution plan:*

```yaml
COMPOSITION_PLAN:
  blocks: [list of blocks]
  operators: [list of operators]
  execution_order:
    - stage: 1
      blocks: [blocks at this stage]
      parallel: true/false
  data_flow:
    - from: assess_difficulty
      to: select_tier
      type: DifficultyScore
  budget_estimate: [tokens]
  quality_estimate: [0-1]
  exit: Plan generated, no execution
```

---

## Mode: Spec

*If @mode:spec, generate reusable specification:*

```yaml
name: custom-composition-[hash]
type: block_composition
version: 1.0.0
blocks:
  - name: [block_name]
    config: [any overrides]
operators:
  - type: sequence
    from: [block_a]
    to: [block_b]
quality_gates:
  - threshold: [value]
    at: [block position]
error_handling:
  catch: [strategy]
  fallback: [strategy]
```

---

## Mode: Active (Default)

### Step 1: Parse Composition

From your input, I parse the block composition:

```
Input: $ARGUMENTS

Parsed Structure:
├── Blocks: [list]
├── Operators: [sequence/parallel/kleisli/tensor]
├── Overrides: [any @block: modifiers]
└── Task: [quoted task]
```

### Step 2: Validate Composition

```
Type Checking:
├── Block 1 output type: [type]
├── Block 2 input type: [type]
├── Compatible: ✓/✗
└── ...

Cycle Detection: [none/detected at ...]
Budget Check: [within/exceeds] @budget:
```

### Step 3: Execute Composition

For each block in execution order:

```
═══════════════════════════════════════════════════════
BLOCK: [block_name]
═══════════════════════════════════════════════════════

Input: [from previous block or initial task]
Config: [any overrides]
Operator: [how connected to next]

[Execute block]

Output: [block output]
Quality: [if assessed]
Tokens: [used]

CHECKPOINT_BLOCK_[n]:
  block: [name]
  status: SUCCESS | ERROR | SKIPPED
  output_summary: [brief]
  tokens_used: [count]
```

### Step 4: Handle Operators

**For Sequential (→):**
```
Block_A output → Block_B input
```

**For Parallel (||):**
```
┌── Block_A ──┐
│             ├── merge(@merge:strategy) ──► Combined
└── Block_B ──┘
```

**For Kleisli (>=>):**
```
Block_A output
    │
    ▼
Quality Check (vs @quality:)
    │
    ├── ≥ threshold → Block_B input
    │
    └── < threshold → Refine → Re-check → ...
```

**For Tensor (⊗):**
```
Block_A capability ⊗ Block_B capability = Combined capability
Quality: min(q_A, q_B)
```

---

## Error Handling

### On Block Error

Based on @catch: modifier:

| @catch: | Behavior |
|---------|----------|
| halt | Stop composition, return error |
| log | Log error, continue with empty |
| retry:N | Retry block N times |
| skip | Skip block, continue |

### On Quality Gate Failure

Based on @fallback: modifier:

| @fallback: | Behavior |
|------------|----------|
| return-best | Return highest quality so far |
| return-last | Return last successful output |
| empty | Return empty/minimal |

---

## Composition Result

```
╔══════════════════════════════════════════════════════════════╗
║ BLOCK COMPOSITION RESULT                                      ║
╠══════════════════════════════════════════════════════════════╣
║ Composition: [block1 → block2 → ...]                          ║
║ Blocks Executed: N                                            ║
║ Status: [COMPLETE | PARTIAL | FAILED]                         ║
║ Final Quality: [if assessed]                                  ║
║ Total Tokens: [count]                                         ║
╚══════════════════════════════════════════════════════════════╝
```

| Block | Status | Output Summary | Tokens |
|-------|--------|----------------|--------|
| [name] | ✓/✗ | [brief] | [n] |
| ... | ... | ... | ... |

**Final Output:**
```
[Output from last block in composition]
```

---

## Usage Examples

### Example 1: Custom Assessment Pipeline

```bash
/blocks [assess_difficulty → assess_domain → select_tier] "complex task"
```

Executes: difficulty assessment → domain classification → tier selection

### Example 2: Quality-Gated Transformation

```bash
/blocks @quality:0.85 [
  build_template >=>
  apply_transform >=>
  execute_prompt
] "implement feature"
```

Each stage must meet 0.85 quality before proceeding.

### Example 3: Parallel Analysis

```bash
/blocks @merge:weighted [
  (assess_domain || assess_difficulty) →
  select_tier
] "evaluate task"
```

Parallel assessment, then sequential tier selection.

### Example 4: Full Custom /rmp

```bash
/blocks @quality:0.9 @fallback:return-best [
  apply_transform →
  execute_prompt →
  assess_quality >=>
  (evaluate_convergence | apply_refinement)
] "build robust system"
```

Custom RMP loop with quality gating.

### Example 5: Multi-Expert Composition

```bash
/blocks @merge:vote [
  (assess_domain:SECURITY || assess_domain:PERFORMANCE || assess_domain:API) →
  select_strategy @bias:balanced →
  execute_prompt
] "review code"
```

Three domain perspectives, voted merge, then single strategy.

---

## Block Configuration Overrides

Override block behavior inline:

```bash
# Override threshold
/blocks [assess_quality @threshold:0.9 → evaluate_convergence] "task"

# Override merge strategy
/blocks [block_a @config:x || block_b @config:y] @merge:weighted "task"

# Override entire block
/blocks [custom_assess:my_custom_v2 → select_tier] "task"
```

---

## How /blocks Relates to Other Commands

| Command | Blocks Used Internally | Exposure Level |
|---------|------------------------|----------------|
| `/meta` | assess_* → select_* → build_* → apply_* → execute_* | Hidden |
| `/rmp` | execute → assess_quality → evaluate_convergence → apply_refinement | Hidden |
| `/route` | assess_difficulty → assess_domain → dispatch | Hidden |
| `/blocks` | Any combination | Full access |

---

## Categorical Laws

This command preserves categorical laws:

1. **Sequence Associativity**: `(A → B) → C = A → (B → C)`
2. **Parallel Commutativity**: `A || B = B || A`
3. **Kleisli Laws**: Left/right identity and associativity
4. **Quality Degradation**: `quality(A → B) ≤ min(q_A, q_B)`

---

## Integration

The `/blocks` command integrates with:

- **skill:atomic-blocks** - Block definitions and signatures
- **skill:meta-self** - Unified syntax reference
- **/meta, /rmp, /route** - These use blocks internally

---

## Backward Compatibility

Existing commands work unchanged. `/blocks` is an additional power-user capability that exposes the blocks they use internally.

---

## Version

**Command Version**: 1.0.0
**Requires**: skill:atomic-blocks v1.0.0+
