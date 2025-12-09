# Atomic Blocks: Practical Examples

**Version**: 1.0.0
**Skill**: `atomic-blocks`
**Commands**: `/blocks`, `/rmp`, `/meta`, `/route`

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1 (90%): Use commands normally - blocks are hidden      │
│  LAYER 2 (9%):  Override specific blocks with @block:          │
│  LAYER 3 (1%):  Full composition with /blocks                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1 Examples: Simple Surface

Most users never need to know about atomic blocks. Commands just work:

### Example 1.1: Basic Meta-Prompting

```bash
/meta "implement a rate limiter for API endpoints"
```

**What happens internally** (hidden from user):
```
Task ──► assess_difficulty ──► assess_domain ──► select_tier ──► select_strategy
                                                      │
                                                      ▼
Output ◄── execute_prompt ◄── apply_transform ◄── build_template
```

### Example 1.2: Quality-Gated Refinement

```bash
/rmp @quality:0.85 "optimize database query performance"
```

**Internal block flow** (hidden):
```
┌──────────────────────────────────────────────┐
│  Task ──► apply_transform ──► execute_prompt │
│                                     │        │
│                                     ▼        │
│                             assess_quality   │
│                                     │        │
│                 ┌───────────────────┴───┐    │
│                 ▼                       ▼    │
│          CONVERGED?               CONTINUE   │
│              │                        │      │
│              ▼                        ▼      │
│           RETURN          extract_improvement│
│                                       │      │
│                                       ▼      │
│                              apply_refinement│
│                                       │      │
│                                       └──────┤
└──────────────────────────────────────────────┘
```

### Example 1.3: Command Chaining

```bash
/chain [/debug→/fix→/test] "TypeError in auth.py:42"
```

Each stage uses its own internal blocks, completely hidden.

---

## Layer 2 Examples: Override Layer

For users who need fine-grained control over specific behaviors:

### Example 2.1: Override Quality Threshold

```bash
# Default threshold is 0.8, but for critical code we want 0.95
/rmp @block:evaluate_convergence.threshold:0.95 "implement payment processing"
```

**Effect**: The `evaluate_convergence` block now uses 0.95 instead of the default.

### Example 2.2: Override Quality Weights

```bash
# For algorithm tasks, correctness matters more than clarity
/rmp @block:assess_quality.weights:{correctness:0.6,clarity:0.15,completeness:0.15,efficiency:0.1} "implement quicksort"
```

**Effect**: Quality assessment now weights correctness at 60% instead of 40%.

### Example 2.3: Force Domain Classification

```bash
# Sometimes auto-detection misses security implications
/meta @block:assess_domain:SECURITY "review the user input handler"
```

**Effect**: Forces SECURITY domain, triggering security-focused prompting strategies.

### Example 2.4: Override Tier Selection

```bash
# Force L5 (hierarchical parallel) for a task auto-detected as L3
/meta @block:select_tier:L5 "build authentication system"
```

**Effect**: Uses L5 prompting patterns instead of auto-detected tier.

### Example 2.5: Override Refinement Strategy

```bash
# Limit refinement attempts to prevent over-iteration
/rmp @block:apply_refinement.max_attempts:2 "design API schema"
```

**Effect**: Each iteration tries refinement at most 2 times before accepting.

---

## Layer 3 Examples: Full Composition

For power users who want complete control:

### Example 3.1: Custom Assessment Pipeline

```bash
/blocks [assess_difficulty → assess_domain → select_tier] "build microservices gateway"
```

**Output**:
```yaml
COMPOSITION_RESULT:
  assess_difficulty:
    score: 0.78
    factors: {length: 0.6, complexity: 0.85, ambiguity: 0.4, novelty: 0.7}
  assess_domain: API
  select_tier: L5
  status: COMPLETE
```

### Example 3.2: Quality-Gated Transformation

```bash
/blocks @quality:0.85 [
  build_template >=>
  apply_transform >=>
  execute_prompt
] "implement caching layer"
```

**Effect**: Each stage must meet 0.85 quality before proceeding to next. The `>=>` (Kleisli) operator enforces quality gates.

### Example 3.3: Parallel Domain Analysis

```bash
/blocks @merge:weighted [
  (assess_domain:SECURITY || assess_domain:PERFORMANCE || assess_domain:API) →
  select_strategy
] "review authentication endpoint"
```

**What happens**:
1. Three domain assessments run in parallel
2. Results merged using weighted voting
3. Single strategy selected based on combined analysis

### Example 3.4: Custom RMP Loop

```bash
/blocks @quality:0.9 @fallback:return-best [
  apply_transform →
  execute_prompt →
  assess_quality >=>
  evaluate_convergence →
  (apply_refinement | aggregate_iterations)
] "build robust error handling"
```

**Effect**: Custom refinement loop with 0.9 quality threshold and fallback to best result if max iterations reached.

### Example 3.5: Multi-Expert Composition

```bash
/blocks @merge:vote [
  (build_template:security_expert || build_template:performance_expert || build_template:api_expert) →
  apply_transform →
  execute_prompt →
  assess_quality
] "design user authentication"
```

**What happens**:
1. Three expert templates generated in parallel
2. Templates voted/merged
3. Single transform applied
4. Quality assessed on merged result

### Example 3.6: Dry-Run Preview

```bash
/blocks @mode:dry-run [
  assess_difficulty →
  select_tier →
  build_template →
  apply_transform
] "complex distributed task"
```

**Output**:
```yaml
COMPOSITION_PLAN:
  blocks: [assess_difficulty, select_tier, build_template, apply_transform]
  operators: [→, →, →]
  execution_order:
    - stage: 1
      blocks: [assess_difficulty]
      parallel: false
    - stage: 2
      blocks: [select_tier]
      parallel: false
    - stage: 3
      blocks: [build_template]
      parallel: false
    - stage: 4
      blocks: [apply_transform]
      parallel: false
  data_flow:
    - from: assess_difficulty
      to: select_tier
      type: DifficultyScore
    - from: select_tier
      to: build_template
      type: Tier
    - from: build_template
      to: apply_transform
      type: Template
  budget_estimate: 3500
  quality_estimate: 0.82
  exit: Plan generated, no execution
```

### Example 3.7: Generate Reusable Spec

```bash
/blocks @mode:spec [
  assess_difficulty →
  assess_domain →
  select_tier →
  select_strategy
] "classification pipeline"
```

**Output**:
```yaml
name: custom-composition-a7f3b2
type: block_composition
version: 1.0.0
blocks:
  - name: assess_difficulty
    config: {}
  - name: assess_domain
    config: {}
  - name: select_tier
    config: {}
  - name: select_strategy
    config: {}
operators:
  - type: sequence
    from: assess_difficulty
    to: assess_domain
  - type: sequence
    from: assess_domain
    to: select_tier
  - type: sequence
    from: select_tier
    to: select_strategy
quality_gates: []
error_handling:
  catch: halt
  fallback: null
```

---

## Advanced Composition Patterns

### Pattern A: Conditional Branching

```bash
/blocks [
  assess_difficulty →
  (
    [difficulty < 0.3] → select_tier:L2 |
    [difficulty < 0.7] → select_tier:L4 |
    [default] → select_tier:L6
  )
] "adaptive task"
```

### Pattern B: Error Recovery

```bash
/blocks @catch:retry:3 @fallback:return-last [
  apply_transform →
  execute_prompt →
  assess_quality
] "fault-tolerant execution"
```

**Behavior**:
- On error: retry up to 3 times
- If all retries fail: return last successful output

### Pattern C: Tensor Product (Capability Combination)

```bash
/blocks [
  (assess_domain ⊗ assess_difficulty) →
  select_tier
] "combined assessment"
```

**Effect**: Domain and difficulty assessed as combined capability, not sequentially.

### Pattern D: Iterative Refinement Loop

```bash
/blocks @quality:0.85 @max_iterations:5 [
  execute_prompt →
  assess_quality >=>
  extract_improvement →
  apply_refinement
]⟲ "converging solution"
```

**Note**: `⟲` indicates iteration until convergence.

---

## Block Reference Card

| Block | Input | Output | Layer |
|-------|-------|--------|-------|
| `assess_difficulty` | Task | DifficultyScore [0,1] | Assessment |
| `assess_domain` | Task | Domain enum | Assessment |
| `assess_quality` | Output | QualityVector | Assessment |
| `select_tier` | (Difficulty, Domain) | Tier (L1-L7) | Assessment |
| `select_strategy` | Tier | Strategy | Transformation |
| `build_template` | (Context, Strategy) | Template | Transformation |
| `apply_transform` | (Template, Task) | Prompt | Transformation |
| `execute_prompt` | Prompt | Output | Transformation |
| `evaluate_convergence` | (Quality, Threshold) | Status | Refinement |
| `extract_improvement` | (Output, Quality) | Direction | Refinement |
| `apply_refinement` | (Output, Direction) | Output | Refinement |
| `aggregate_iterations` | [Output] | BestOutput | Refinement |
| `sequence` (→) | (A→B, B→C) | A→C | Composition |
| `parallel` (\|\|) | (A→B, A→C) | A→(B,C) | Composition |
| `kleisli` (>=>) | (A→M[B], B→M[C]) | A→M[C] | Composition |
| `tensor` (⊗) | (A→B) ⊗ (C→D) | (A,C)→(B,D) | Composition |

---

## Operator Reference

| Operator | Symbol | Quality Rule | Use When |
|----------|--------|--------------|----------|
| Sequence | `→` | `min(q₁, q₂)` | Order matters, output feeds input |
| Parallel | `\|\|` | `mean(q₁, q₂, ...)` | Independent operations to combine |
| Kleisli | `>=>` | improves iteratively | Quality-gated progression |
| Tensor | `⊗` | `min(q₁, q₂)` | Combining capabilities |

---

## Common Recipes

### Recipe 1: Security-First Review
```bash
/blocks @block:assess_domain:SECURITY [
  assess_difficulty → select_tier → build_template:security → execute_prompt
] "review authentication code"
```

### Recipe 2: High-Quality Implementation
```bash
/blocks @quality:0.95 [
  build_template >=> apply_transform >=> execute_prompt >=> assess_quality
] "implement payment processing"
```

### Recipe 3: Parallel Expert Analysis
```bash
/blocks @merge:weighted [
  (build_template:security || build_template:performance || build_template:maintainability) →
  apply_transform → execute_prompt
] "comprehensive code review"
```

### Recipe 4: Iterative Optimization
```bash
/rmp @quality:0.9 @max_iterations:7 @block:assess_quality.weights:{efficiency:0.5} "optimize algorithm"
```

---

## Troubleshooting

### "Block not found"
```bash
# Check available blocks
/blocks @mode:validate [your_block] "task"
```

### "Type mismatch"
```bash
# Verify type flow with dry-run
/blocks @mode:dry-run [block1 → block2] "task"
# Check data_flow in output
```

### "Quality not improving"
```bash
# Check if you've hit a fixed point
# Reduce threshold or restructure approach
/blocks @quality:0.75 [...] "task"  # Lower threshold
```

### "Composition too slow"
```bash
# Use parallel where possible
/blocks [(block1 || block2) → block3] "task"  # Parallel first two
```

---

## See Also

- `skill:atomic-blocks` - Full block specifications
- `skill:meta-self` - Unified syntax reference
- `/rmp` - Built-in iterative refinement
- `/meta` - Categorical meta-prompting
- `/chain` - Command composition

---

**Version**: 1.0.0
**Last Updated**: 2025-12-08
