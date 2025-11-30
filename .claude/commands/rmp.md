---
description: Execute Recursive Meta-Prompting loop with quality convergence
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(*), TodoWrite
argument-hint: [task] [quality-threshold]
---

# Recursive Meta-Prompting (RMP) Loop

## Task
$1

## Quality Threshold
Target: $2 (default: 8/10 if not specified)

---

## RMP Execution Protocol

I will now execute an RMP loop. This is NOT just "trying again" - it's a structured iterative refinement with quality tracking.

### Iteration Structure

```
┌─────────────────────────────────────────┐
│ Iteration N                             │
├─────────────────────────────────────────┤
│ 1. Generate/Refine Solution             │
│ 2. Evaluate Quality (multi-dimensional) │
│ 3. If quality >= threshold: STOP        │
│ 4. Else: Extract improvement direction  │
│ 5. Apply improvement → Iteration N+1    │
└─────────────────────────────────────────┘
```

### Quality Dimensions

For each iteration, assess:

| Dimension | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Correctness | 40% | ?/10 | Does it solve the problem? |
| Clarity | 25% | ?/10 | Is it understandable? |
| Completeness | 20% | ?/10 | Are edge cases handled? |
| Efficiency | 15% | ?/10 | Is it well-designed? |
| **Weighted** | 100% | ?/10 | |

### Convergence Rules

- **Max iterations**: 5 (prevent infinite loops)
- **Improvement threshold**: Must improve by ≥0.5 points or stop
- **Quality floor**: Stop if quality ≥ threshold

---

## BEGIN RMP LOOP

### Iteration 1

**Attempt:**
[Generate initial solution to the task]

**Quality Assessment:**
| Dimension | Score | Justification |
|-----------|-------|---------------|
| Correctness | | |
| Clarity | | |
| Completeness | | |
| Efficiency | | |
| **Weighted** | | |

**Decision:** [CONVERGED if ≥ threshold, else CONTINUE]

**Improvement Direction:** [What specific aspect to improve]

---

*Continue iterations until convergence or max iterations reached*

---

## Final Output

```
Task: [original task]
Iterations: N
Final Quality: X/10
Convergence: [ACHIEVED | MAX_ITERATIONS | NO_IMPROVEMENT]

Solution:
[final refined solution]

Quality Trace:
Iter 1: X.X → Iter 2: X.X → ... → Final: X.X
```
