---
description: Execute Recursive Meta-Prompting loop with quality convergence
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(*), TodoWrite
argument-hint: @quality:[threshold] @max_iterations:[n] @mode:[mode] [task]
---

# Recursive Meta-Prompting (RMP) Loop

## Unified Syntax

```
/rmp @quality:0.85 @max_iterations:5 @mode:iterative "task description"
```

### Supported Modifiers

| Modifier | Default | Description |
|----------|---------|-------------|
| `@quality:` | 0.8 | Target quality threshold (0.0-1.0) |
| `@max_iterations:` | 5 | Maximum refinement iterations |
| `@mode:` | iterative | Execution mode: iterative, dry-run, spec |
| `@budget:` | auto | Token budget for entire RMP loop |
| `@variance:` | 20% | Acceptable budget variance |

### Composition Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `>=>` | Kleisli (monadic refinement) | `[analyze>=>design>=>implement]` |

---

## Parse Input

**Arguments**: $ARGUMENTS

**Parsed Configuration**:

| Setting | Value | Source |
|---------|-------|--------|
| Task | [extracted task] | from arguments |
| Quality Threshold | [0.8 or @quality: value] | modifier or default |
| Max Iterations | [5 or @max_iterations: value] | modifier or default |
| Mode | [iterative or @mode: value] | modifier or default |
| Budget | [auto or @budget: value] | modifier or default |

---

## Mode: Dry-Run

*If @mode:dry-run was specified, show plan and exit:*

```yaml
RMP_PLAN:
  task: [task]
  quality_threshold: [threshold]
  max_iterations: [n]
  estimated_trajectory: [0.5, 0.65, 0.75, 0.82, 0.87]
  budget_allocation: [per-iteration estimate]
  exit: Plan generated, no execution
```

---

## Mode: Spec

*If @mode:spec was specified, generate specification and exit:*

```yaml
name: rmp-[task-hash]
type: iterative_refinement
categorical_structure:
  functor: F(Task) → Prompt
  monad: M(Prompt) →^n Prompt
  enrichment: [0,1]-quality
operators:
  - >=> (Kleisli composition)
config:
  quality_threshold: [value]
  max_iterations: [value]
stages:
  - {name: initial, operator: return}
  - {name: assess, operator: evaluate → [0,1]}
  - {name: refine, operator: >=>, condition: quality < threshold}
  - {name: converge, operator: fix, condition: quality >= threshold}
```

---

## Mode: Iterative (Default)

### RMP Execution Protocol

This is NOT just "trying again" - it's structured iterative refinement with quality tracking implementing the Monad M from categorical meta-prompting.

```
┌─────────────────────────────────────────┐
│ Categorical RMP Loop                    │
├─────────────────────────────────────────┤
│ 1. Generate/Refine Solution (Prompt)    │
│ 2. Evaluate Quality → [0,1]             │
│ 3. If quality >= @quality: CONVERGE     │
│ 4. Else: Extract improvement direction  │
│ 5. Apply >=> (Kleisli) → Iteration N+1  │
└─────────────────────────────────────────┘
```

### Quality Dimensions (Multi-Dimensional Assessment)

For each iteration, assess quality as vector in product category:

| Dimension | Weight | Score (0-1) | Notes |
|-----------|--------|-------------|-------|
| Correctness | 40% | ?/1.0 | Does it solve the problem correctly? |
| Clarity | 25% | ?/1.0 | Is it clear and understandable? |
| Completeness | 20% | ?/1.0 | Are edge cases and requirements covered? |
| Efficiency | 15% | ?/1.0 | Is the solution well-designed? |
| **Aggregate** | 100% | ?/1.0 | Weighted sum for @quality: comparison |

### Convergence Rules (Categorical Laws)

- **Quality Threshold**: Stop if aggregate quality >= @quality:
- **Max Iterations**: Stop if iteration count >= @max_iterations:
- **Improvement Floor**: Stop if quality_delta < 0.02 (fixed-point reached)
- **Budget Limit**: Stop if budget exceeded by > @variance:

---

## BEGIN RMP LOOP

### Iteration 1 (return: Initial Prompt)

**Attempt:**
[Generate initial solution to the task]

**Quality Assessment (evaluate → [0,1]):**

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Correctness | /1.0 | |
| Clarity | /1.0 | |
| Completeness | /1.0 | |
| Efficiency | /1.0 | |
| **Aggregate** | /1.0 | |

**Decision:** [CONVERGED if >= threshold] | [CONTINUE if < threshold]

**Improvement Direction (for >=> application):**
[What specific aspect needs the most improvement - guide next iteration]

---

### Iteration 2+ (>=> Kleisli Refinement)

*Continue iterations, applying monadic bind at each step:*

```
previous_output >=> improvement_function → refined_output
```

**Refinement Focus:** [Based on lowest dimension from previous iteration]

**Attempt:**
[Generate improved solution focusing on the identified weakness]

**Quality Assessment:**

| Dimension | Score | Delta | Notes |
|-----------|-------|-------|-------|
| Correctness | /1.0 | [+/-] | |
| Clarity | /1.0 | [+/-] | |
| Completeness | /1.0 | [+/-] | |
| Efficiency | /1.0 | [+/-] | |
| **Aggregate** | /1.0 | [+/-] | |

**Decision:** [CONVERGED | CONTINUE | MAX_ITERATIONS | NO_IMPROVEMENT]

---

## RMP Checkpoint Format

```yaml
RMP_CHECKPOINT_[i]:
  iteration: [n]
  quality:
    correctness: [0-1]
    clarity: [0-1]
    completeness: [0-1]
    efficiency: [0-1]
    aggregate: [0-1]
  quality_delta: [+/- from previous]
  trend: [RAPID_IMPROVEMENT | STEADY_IMPROVEMENT | PLATEAU | DEGRADING]
  status: [CONTINUE | CONVERGED | MAX_ITERATIONS | NO_IMPROVEMENT]
  budget:
    used: [tokens]
    remaining: [tokens]
    variance: [%]
```

---

## Final Output

```
╔══════════════════════════════════════════════════════════════╗
║ RMP RESULT                                                    ║
╠══════════════════════════════════════════════════════════════╣
║ Task: [original task]                                         ║
║ Iterations: N                                                 ║
║ Final Quality: X.XX/1.0                                       ║
║ Convergence: [ACHIEVED | MAX_ITERATIONS | NO_IMPROVEMENT]     ║
║ Categorical Structure: M(Prompt) via >=> composition          ║
╚══════════════════════════════════════════════════════════════╝

Quality Trace (enriched category trajectory):
Iter 1: 0.XX → Iter 2: 0.XX → ... → Final: 0.XX

Solution:
[final refined solution]
```

---

## Usage Examples

```bash
# Basic - uses defaults (@quality:0.8, @max_iterations:5)
/rmp "implement binary search"

# Explicit quality threshold
/rmp @quality:0.9 "optimize database query"

# With iteration limit
/rmp @quality:0.85 @max_iterations:3 "build REST API"

# With budget tracking
/rmp @quality:0.85 @budget:15000 @variance:15% "implement caching"

# Kleisli composition chain
/rmp @quality:0.85 [analyze>=>design>=>implement] "build auth system"

# Dry-run preview
/rmp @mode:dry-run @quality:0.9 "complex multi-step feature"

# Generate specification only
/rmp @mode:spec @quality:0.85 "data processing pipeline"
```

---

## Backward Compatibility

Old syntax still works:
```bash
/rmp "task" 0.85           # Positional quality threshold
/rmp "task"                # Uses default threshold (0.8)
```

New unified syntax is preferred:
```bash
/rmp @quality:0.85 "task"  # Explicit modifier
```
