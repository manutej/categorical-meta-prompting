---
description: Execute Recursive Meta-Prompting loop with quality convergence
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(*), TodoWrite
argument-hint: [task] [quality-threshold]
---

# Recursive Meta-Prompting (RMP) Loop

This command implements **Monad M** for iterative refinement with quality convergence.

```
M = (Prompt, unit, bind)
  - unit(p) = MonadPrompt(p, quality=initial)
  - bind(ma, f) = f(ma.prompt) with quality tracking
  - join(mma) = flatten nested monads
```

**Monad Laws Verified**:
- Left Identity: `unit(a) >>= f = f(a)`
- Right Identity: `m >>= unit = m`
- Associativity: `(m >>= f) >>= g = m >>= (λx. f(x) >>= g)`

## Task
$1

## Quality Threshold
Target: $2 (default: 8/10, normalized to 0.8 in [0,1])

---

## Monad M - Execution Protocol

Execute an RMP loop using **M.bind** for structured iterative refinement:

### Iteration Structure (Monadic)

```
┌─────────────────────────────────────────┐
│ M.bind(iteration_n, refine)             │
├─────────────────────────────────────────┤
│ 1. M.unit(prompt) → MonadPrompt         │
│ 2. Execute → output with quality        │
│ 3. M.assess(output) → quality ∈ [0,1]   │
│ 4. If quality >= threshold: M.return    │
│ 5. Else: M.bind(refine) → iteration n+1 │
└─────────────────────────────────────────┘
```

**Categorical Semantics**:
- Each iteration is `M.bind(current, improve)`
- Quality tracked via [0,1]-enriched category
- Convergence = fixpoint of improvement function

### Quality Dimensions ([0,1]-Enriched Category)

For each iteration, assess quality using tensor product semantics:

| Dimension | Weight | Score | [0,1] Normalized | Notes |
|-----------|--------|-------|------------------|-------|
| Correctness | 0.40 | ?/10 | ?/1.0 | Does it solve the problem? |
| Clarity | 0.25 | ?/10 | ?/1.0 | Is it understandable? |
| Completeness | 0.20 | ?/10 | ?/1.0 | Are edge cases handled? |
| Efficiency | 0.15 | ?/10 | ?/1.0 | Is it well-designed? |
| **Tensor ⊗** | 1.00 | ?/10 | ?/1.0 | Weighted combination |

**Quality Formula** (Enriched [0,1]):
```
quality = (0.40 × correct + 0.25 × clear + 0.20 × complete + 0.15 × efficient) / 10
```

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

## M.return - Final Output

Apply **M.return** to extract final value from monad:

```
Task: [original task]
Iterations: N
Final Quality: X/10 (normalized: 0.X)
Convergence: [ACHIEVED | MAX_ITERATIONS | NO_IMPROVEMENT]

Solution:
[final refined solution]
```

**Monadic Quality Trace**:
```
M.unit(p₀) →[bind]→ M(p₁, q₁) →[bind]→ M(p₂, q₂) →...→ M.return(pₙ, qₙ)

Quality progression: q₁ → q₂ → ... → qₙ ≥ threshold
```

**Categorical Verification**:
- Monad laws: ✅ Left identity, Right identity, Associativity
- Quality monotonicity: qₙ ≥ qₙ₋₁ (or convergence triggered)
- Enriched [0,1]: All quality scores normalized to [0,1]
