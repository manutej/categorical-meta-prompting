---
name: atomic-blocks
description: "Composable atomic blocks for categorical meta-prompting. Defines 16 reusable blocks across 4 layers (Assessment, Transformation, Refinement, Composition) that can be composed to build custom workflows. Enables progressive disclosure: simple commands work unchanged, power users can override individual blocks or compose freely."
version: 1.0.0
---

# Atomic Blocks: Composable Primitives for Categorical Meta-Prompting

This skill defines the atomic building blocks that underlie all categorical meta-prompting commands. These blocks exist implicitly in commands like `/meta`, `/rmp`, and `/route`. Making them explicit enables:

1. **Mathematical coherence** - Laws verifiable at block level
2. **Testability** - Unit test individual blocks
3. **Performance** - Caching + parallelization
4. **Power user capability** - Custom compositions

---

## Categorical Foundation

```
The framework decomposes into natural atomic morphisms:

F (Functor):     τ: A → B           (pure transformation)
M (Monad):       η: A → M(A)        (unit/return)
                 μ: M(M(A)) → M(A)  (join/flatten)
W (Comonad):     ε: W(A) → A        (extract)
                 δ: W(A) → W(W(A))  (duplicate)
[0,1]:           q: A → [0,1]       (quality assessment)
```

---

## Progressive Disclosure Layers

### Layer 1: Simple Surface (90% of users)

Commands work unchanged - all atoms hidden:

```bash
/meta "task"           # assess → select → transform → execute
/rmp "task"            # [execute → assess → converge]*
/route "task"          # assess → route → dispatch
```

### Layer 2: Override Layer (9% of users)

Override single blocks via `@block:` modifier:

```bash
/meta @block:assess_domain:SECURITY "review code"
/rmp @block:quality_threshold:0.9 "optimize"
/chain @block:merge_strategy:weighted [...] "task"
```

### Layer 3: Composition Layer (1% of users)

Full atomic control via `/compose`:

```bash
/compose [
  assess_difficulty →
  select_strategy @bias:quality →
  build_template →
  apply_transform →
  execute_prompt →
  assess_quality >=>
  evaluate_convergence
] "complex workflow"
```

---

## Block Taxonomy (16 Blocks, 4 Layers)

### Layer 1: Assessment Blocks

These blocks analyze input and classify tasks.

#### `assess_difficulty`

```yaml
name: assess_difficulty
signature: Task → DifficultyScore
category: Assessment
purpose: Evaluate task complexity for tier selection

input:
  task: string  # The task description

output:
  score: float  # Difficulty in [0, 1]
  factors:
    length: float      # Normalized task length
    complexity: float  # Structural complexity
    ambiguity: float   # Requirement clarity
    novelty: float     # Familiarity of domain

mapping:
  score < 0.3:  "easy"   → L1-L2
  0.3 ≤ score ≤ 0.7: "medium" → L3-L4
  score > 0.7:  "hard"   → L5-L7

laws:
  - Deterministic: same input → same output
  - Bounded: output ∈ [0, 1]

example:
  input: "implement rate limiter with sliding window"
  output:
    score: 0.55
    factors: {length: 0.4, complexity: 0.6, ambiguity: 0.3, novelty: 0.5}
```

#### `assess_domain`

```yaml
name: assess_domain
signature: Task → Domain
category: Assessment
purpose: Classify task into domain category

input:
  task: string

output:
  domain: enum[ALGORITHM, SECURITY, API, DEBUG, TESTING, GENERAL]
  confidence: float  # Classification confidence
  signals: list[string]  # Keywords that triggered classification

mapping:
  patterns:
    ALGORITHM: [optimize, complexity, sort, search, tree, graph, O(n)]
    SECURITY: [auth, encrypt, hash, OWASP, injection, XSS, CSRF]
    API: [endpoint, REST, GraphQL, request, response, route]
    DEBUG: [error, bug, fix, trace, exception, crash]
    TESTING: [test, assert, mock, coverage, spec, jest, pytest]

laws:
  - Exhaustive: every task maps to exactly one domain
  - Cacheable: domain stable for same task

example:
  input: "fix XSS vulnerability in login form"
  output:
    domain: SECURITY
    confidence: 0.92
    signals: [XSS, vulnerability, login]
```

#### `assess_quality`

```yaml
name: assess_quality
signature: Output → QualityVector
category: Assessment
purpose: Multi-dimensional quality evaluation

input:
  output: string  # The output to evaluate
  context: string  # Original task for reference

output:
  vector:
    correctness: float   # Does it solve the problem? (weight: 0.40)
    clarity: float       # Is it understandable? (weight: 0.25)
    completeness: float  # Are edge cases handled? (weight: 0.20)
    efficiency: float    # Is it well-designed? (weight: 0.15)
  aggregate: float       # Weighted sum
  weakest: string        # Dimension needing most improvement

formula: |
  aggregate = 0.40×correctness + 0.25×clarity +
              0.20×completeness + 0.15×efficiency

laws:
  - Normalized: all dimensions ∈ [0, 1]
  - Weighted: aggregate is weighted sum
  - Monotonic: refinement should not decrease quality

example:
  input: "def rate_limit(key): return cache.get(key, 0) < 100"
  output:
    vector: {correctness: 0.7, clarity: 0.8, completeness: 0.5, efficiency: 0.6}
    aggregate: 0.665
    weakest: "completeness"
```

#### `select_tier`

```yaml
name: select_tier
signature: (DifficultyScore, Domain) → Tier
category: Assessment
purpose: Map assessment to L1-L7 tier

input:
  difficulty: DifficultyScore
  domain: Domain

output:
  tier: enum[L1, L2, L3, L4, L5, L6, L7]
  strategy: enum[DIRECT, MULTI_APPROACH, AUTONOMOUS_EVOLUTION]
  budget_range: [min, max]  # Token budget

mapping:
  L1: {difficulty: [0.0, 0.15], budget: [600, 1200], strategy: DIRECT}
  L2: {difficulty: [0.15, 0.30], budget: [1500, 3000], strategy: DIRECT}
  L3: {difficulty: [0.30, 0.45], budget: [2500, 4500], strategy: MULTI_APPROACH}
  L4: {difficulty: [0.45, 0.60], budget: [3000, 6000], strategy: MULTI_APPROACH}
  L5: {difficulty: [0.60, 0.75], budget: [5500, 9000], strategy: AUTONOMOUS_EVOLUTION}
  L6: {difficulty: [0.75, 0.90], budget: [8000, 12000], strategy: AUTONOMOUS_EVOLUTION}
  L7: {difficulty: [0.90, 1.0], budget: [12000, 22000], strategy: AUTONOMOUS_EVOLUTION}

domain_modifiers:
  SECURITY: +1 tier (conservative)
  DEBUG: -1 tier if clear reproduction
  ALGORITHM: standard mapping

laws:
  - Deterministic: same inputs → same tier
  - Ordered: L1 < L2 < ... < L7

example:
  input: {difficulty: 0.55, domain: SECURITY}
  output: {tier: L5, strategy: AUTONOMOUS_EVOLUTION, budget_range: [5500, 9000]}
  # Note: L4 base + 1 for SECURITY
```

---

### Layer 2: Transformation Blocks

These blocks transform tasks into prompts.

#### `select_strategy`

```yaml
name: select_strategy
signature: Tier → Strategy
category: Transformation
purpose: Choose prompting strategy for tier

input:
  tier: Tier
  bias: optional[enum[speed, quality, balanced]]  # Override default

output:
  strategy: StrategyConfig
    name: string
    functor: enum[F_ZS, F_FS, F_CoT, F_ToT, F_Meta]
    components: list[string]
    estimated_quality: float

mapping:
  L1-L2 (DIRECT):
    functor: F_ZS (zero-shot)
    components: [context, task]
    quality: 0.65

  L3-L4 (MULTI_APPROACH):
    functor: F_CoT (chain-of-thought)
    components: [context, reasoning, task, format]
    quality: 0.80

  L5-L7 (AUTONOMOUS_EVOLUTION):
    functor: F_Meta (meta-prompting)
    components: [context, meta_analysis, strategy, iteration, task, format]
    quality: 0.90

laws:
  - Monotonic: higher tier → higher quality strategy
  - Cacheable: tier → strategy is pure function

example:
  input: {tier: L5, bias: quality}
  output:
    strategy:
      name: "meta-prompting"
      functor: F_Meta
      components: [context, meta_analysis, strategy, iteration, task, format]
      estimated_quality: 0.90
```

#### `build_template`

```yaml
name: build_template
signature: (Context, Strategy) → Template
category: Transformation
purpose: Assemble prompt template from components

input:
  context: ContextConfig
    role: enum[expert, teacher, reviewer, debugger]
    domain: Domain
  strategy: StrategyConfig
  format: optional[enum[prose, structured, code, checklist]]

output:
  template: Template
    system: string      # System prompt section
    instructions: string  # Domain-specific instructions
    task_slot: "{TASK}"   # Placeholder for task
    format: string      # Output format specification
    quality_criteria: string  # Assessment criteria

template_library:
  context:
    expert: "You are an expert in {domain} with deep knowledge."
    teacher: "You are a patient teacher explaining step by step."
    reviewer: "You are a critical reviewer looking for issues."
    debugger: "You are a systematic debugger isolating problems."

  mode:
    direct: "Provide a direct, concise answer."
    cot: "Think step by step before answering."
    multi: "Consider multiple approaches, then synthesize."
    iterative: "Attempt, assess, refine until quality threshold met."

  format:
    prose: "Write in clear paragraphs."
    structured: "Use headers, lists, and tables."
    code: "Provide working code with comments."
    checklist: "Provide actionable checklist items."

laws:
  - Composable: components combine without interference
  - Deterministic: same inputs → same template

example:
  input:
    context: {role: expert, domain: API}
    strategy: {functor: F_CoT, components: [context, reasoning, task, format]}
    format: code
  output:
    template:
      system: "You are an expert in API design with deep knowledge."
      instructions: "Review this API implementation for RESTful conventions..."
      task_slot: "{TASK}"
      format: "Provide working code with comments."
```

#### `apply_transform`

```yaml
name: apply_transform
signature: (Template, Task) → Prompt
category: Transformation
purpose: Apply template to task (Functor action)

input:
  template: Template
  task: string

output:
  prompt: Prompt
    full_text: string   # Complete prompt ready for execution
    token_estimate: int  # Estimated token count
    sections: list[string]  # Named sections for debugging

process:
  1. Substitute {TASK} placeholder with actual task
  2. Combine all template sections
  3. Validate total length within budget
  4. Return assembled prompt

laws:
  - Functor Identity: apply_transform(id_template, task) = task
  - Functor Composition: apply(compose(T1, T2), task) = apply(T1, apply(T2, task))

example:
  input:
    template: {system: "Expert...", task_slot: "{TASK}", format: "Code..."}
    task: "implement rate limiter"
  output:
    prompt:
      full_text: "Expert...\n\nTask: implement rate limiter\n\nCode..."
      token_estimate: 245
      sections: [system, task, format]
```

#### `execute_prompt`

```yaml
name: execute_prompt
signature: Prompt → RawOutput
category: Transformation
purpose: Execute prompt and capture output

input:
  prompt: Prompt

output:
  raw_output: RawOutput
    content: string     # The generated content
    tokens_used: int    # Actual tokens consumed
    latency_ms: int     # Execution time
    metadata: object    # Additional info

process:
  1. Send prompt to LLM
  2. Capture response
  3. Record metrics
  4. Return raw output

laws:
  - Non-deterministic: same prompt may produce different outputs
  - Bounded: output size limited by model context

example:
  input: {full_text: "Expert...\n\nTask: implement rate limiter..."}
  output:
    raw_output:
      content: "def rate_limiter(key, limit=100, window=60):..."
      tokens_used: 312
      latency_ms: 1240
```

---

### Layer 3: Refinement Blocks

These blocks implement the Monad M for iterative refinement.

#### `evaluate_convergence`

```yaml
name: evaluate_convergence
signature: (QualityVector, Threshold, IterationCount) → ConvergenceStatus
category: Refinement
purpose: Check if quality meets threshold (Monad return condition)

input:
  quality: QualityVector
  threshold: float      # Target quality (default: 0.8)
  iteration: int        # Current iteration count
  max_iterations: int   # Maximum allowed (default: 5)
  previous_quality: optional[float]  # For plateau detection

output:
  status: enum[CONTINUE, CONVERGED, MAX_ITERATIONS, PLATEAU, HALT]
  reason: string
  should_refine: bool

rules:
  CONVERGED: quality.aggregate >= threshold
  MAX_ITERATIONS: iteration >= max_iterations
  PLATEAU: |quality - previous_quality| < 0.02 for 2 iterations
  HALT: quality.aggregate < 0.4 (fundamental failure)
  CONTINUE: otherwise

laws:
  - Deterministic: same inputs → same status
  - Terminal: CONVERGED, MAX_ITERATIONS, PLATEAU, HALT are final

example:
  input:
    quality: {aggregate: 0.82}
    threshold: 0.85
    iteration: 2
    max_iterations: 5
    previous_quality: 0.75
  output:
    status: CONTINUE
    reason: "Quality 0.82 < threshold 0.85, improvement +0.07"
    should_refine: true
```

#### `extract_improvement`

```yaml
name: extract_improvement
signature: (Output, QualityVector) → ImprovementDirection
category: Refinement
purpose: Identify improvement direction from gaps

input:
  output: string
  quality: QualityVector

output:
  direction: ImprovementDirection
    focus_dimension: string  # Weakest dimension
    gap: float              # Distance to threshold
    suggestions: list[string]  # Specific improvements
    priority: enum[critical, high, medium, low]

process:
  1. Identify weakest dimension in quality vector
  2. Analyze output for specific gaps
  3. Generate targeted suggestions
  4. Prioritize by impact on aggregate

laws:
  - Targeted: direction focuses on weakest dimension
  - Actionable: suggestions are specific and implementable

example:
  input:
    output: "def rate_limit(key): return cache.get(key, 0) < 100"
    quality: {correctness: 0.7, clarity: 0.8, completeness: 0.5, efficiency: 0.6}
  output:
    direction:
      focus_dimension: "completeness"
      gap: 0.3  # assuming threshold 0.8
      suggestions:
        - "Handle cache miss scenario"
        - "Add TTL/window parameter"
        - "Handle concurrent requests"
      priority: high
```

#### `apply_refinement`

```yaml
name: apply_refinement
signature: (Output, ImprovementDirection) → RefinedOutput
category: Refinement
purpose: Apply improvement direction (Monad bind)

input:
  output: string
  direction: ImprovementDirection

output:
  refined: RefinedOutput
    content: string        # Improved output
    changes_made: list[string]  # What was changed
    expected_improvement: float  # Predicted quality gain

process:
  1. Parse improvement direction
  2. Generate refinement prompt focusing on weakest dimension
  3. Execute refinement
  4. Return improved output with change log

laws:
  - Monad Left Identity: return(a) >>= f = f(a)
  - Monad Right Identity: m >>= return = m
  - Improvement: quality(refined) >= quality(original) (expected)

example:
  input:
    output: "def rate_limit(key): return cache.get(key, 0) < 100"
    direction: {focus: completeness, suggestions: ["Handle cache miss"...]}
  output:
    refined:
      content: |
        def rate_limit(key, limit=100, window=60):
            current = cache.get(key, 0)
            if current is None:
                cache.set(key, 1, ttl=window)
                return True
            ...
      changes_made: ["Added default parameters", "Handle cache miss", "Added TTL"]
      expected_improvement: 0.15
```

#### `aggregate_iterations`

```yaml
name: aggregate_iterations
signature: list[Output] → BestOutput
category: Refinement
purpose: Select best output from iteration history

input:
  iterations: list[IterationResult]
    each: {output: string, quality: QualityVector, iteration: int}

output:
  best: BestOutput
    output: string
    quality: QualityVector
    iteration: int
    trajectory: list[float]  # Quality progression

selection_criteria:
  primary: highest aggregate quality
  tiebreaker: most recent iteration

laws:
  - Idempotent: aggregate([x]) = x
  - Monotonic: aggregate includes highest quality

example:
  input:
    iterations:
      - {output: "v1...", quality: {aggregate: 0.65}, iteration: 1}
      - {output: "v2...", quality: {aggregate: 0.78}, iteration: 2}
      - {output: "v3...", quality: {aggregate: 0.82}, iteration: 3}
  output:
    best:
      output: "v3..."
      quality: {aggregate: 0.82}
      iteration: 3
      trajectory: [0.65, 0.78, 0.82]
```

---

### Layer 4: Composition Blocks

These blocks implement composition operators.

#### `sequence`

```yaml
name: sequence
signature: (Block, Block) → Block
operator: →
category: Composition
purpose: Sequential composition (Kleisli)

semantics: |
  sequence(A, B) = λx. B(A(x))
  Output of A becomes input to B

quality_rule: |
  quality(A → B) ≤ min(quality(A), quality(B))

laws:
  - Associativity: (A → B) → C = A → (B → C)
  - Identity: id → A = A = A → id

example:
  composition: assess_difficulty → select_tier
  execution:
    1. assess_difficulty("task") → DifficultyScore(0.6)
    2. select_tier(0.6) → Tier(L5)
```

#### `parallel`

```yaml
name: parallel
signature: list[Block] → Block
operator: ||
category: Composition
purpose: Parallel composition (concurrent execution)

semantics: |
  parallel([A, B, C]) = λx. merge(A(x), B(x), C(x))
  All blocks execute concurrently on same input

quality_rule: |
  quality(A || B || C) = mean(quality(A), quality(B), quality(C))

merge_strategies:
  concatenate: Join all outputs with headers
  vote: Majority agreement on structured output
  weighted: Weighted average by quality scores
  first: Return first completed (racing)

laws:
  - Commutativity: A || B = B || A (order independent)
  - Identity: A || id = A (with appropriate merge)

example:
  composition: assess_domain || assess_difficulty
  execution:
    1. Spawn: assess_domain("task"), assess_difficulty("task")
    2. Await both
    3. merge({domain: API}, {score: 0.6}) → {domain: API, difficulty: 0.6}
```

#### `kleisli`

```yaml
name: kleisli
signature: (Block, Block) → Block
operator: >=>
category: Composition
purpose: Quality-gated composition (monadic)

semantics: |
  kleisli(A, B) = λx.
    result_a = A(x)
    if quality(result_a) < threshold:
      result_a = refine_until_threshold(result_a)
    return B(result_a)

quality_rule: |
  quality(A >=> B) improves with each refinement gate

laws:
  - Left Identity: return >=> f = f
  - Right Identity: f >=> return = f
  - Associativity: (f >=> g) >=> h = f >=> (g >=> h)

example:
  composition: analyze >=> design >=> implement
  execution:
    1. analyze("task") → analysis (quality 0.72)
    2. quality < 0.8? refine analysis → quality 0.84
    3. design(analysis) → design (quality 0.78)
    4. quality < 0.8? refine design → quality 0.85
    5. implement(design) → implementation
```

#### `tensor`

```yaml
name: tensor
signature: (Block, Block) → Block
operator: ⊗
category: Composition
purpose: Capability combination (quality-degrading)

semantics: |
  tensor(A, B) = λx. combine_capabilities(A(x), B(x))
  Combines skills/perspectives, quality bounded by weakest

quality_rule: |
  quality(A ⊗ B) = min(quality(A), quality(B))

use_cases:
  - Combining multiple skills: api-testing ⊗ validation
  - Multi-expert analysis: security-expert ⊗ performance-expert
  - Cross-domain review: frontend ⊗ backend

laws:
  - Associativity: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)
  - Identity: A ⊗ id = A (with identity capability)

example:
  composition: assess_domain ⊗ assess_difficulty
  execution:
    1. assess_domain("task") → {domain: API, confidence: 0.9}
    2. assess_difficulty("task") → {score: 0.6, confidence: 0.85}
    3. combine → {domain: API, score: 0.6, confidence: min(0.9, 0.85) = 0.85}
```

---

## Composition Error Handling

### Error Types

```typescript
type CompositionError =
  | { type: 'TYPE_MISMATCH', expected: BlockType, got: BlockType, position: int }
  | { type: 'CIRCULAR_DEPENDENCY', cycle: Block[] }
  | { type: 'MISSING_INPUT', block: Block, missing: string }
  | { type: 'QUALITY_GATE_FAILED', block: Block, quality: float, threshold: float }
  | { type: 'BUDGET_EXCEEDED', used: int, limit: int }
  | { type: 'INVALID_OPERATOR', operator: string, context: string }
```

### Validation Rules

```yaml
validate_composition:
  1. Type Compatibility:
     - Output type of block A must match input type of block B in A → B
     - All blocks in A || B must accept same input type

  2. Cycle Detection:
     - Build dependency graph
     - Check for cycles via DFS
     - Report cycle path if found

  3. Budget Validation:
     - Sum estimated tokens for all blocks
     - Compare against @budget: limit
     - Warn if within @variance:, halt if exceeded

  4. Operator Validation:
     - → requires exactly 2 blocks
     - || requires 2+ blocks
     - >=> requires quality threshold
     - ⊗ requires compatible capabilities
```

### Error Messages

```yaml
error_templates:
  TYPE_MISMATCH: |
    Type mismatch at position {position}:
      Block '{block_a}' outputs: {output_type}
      Block '{block_b}' expects: {input_type}

    Suggestion: Insert a transformation block between them,
    or use '{suggested_block}' which accepts {output_type}

  CIRCULAR_DEPENDENCY: |
    Circular dependency detected:
      {cycle_path}

    Suggestion: Remove the back-edge from '{last}' to '{first}'

  QUALITY_GATE_FAILED: |
    Quality gate failed at '{block}':
      Achieved: {quality}
      Required: {threshold}

    Suggestion: Use @fallback:return-best to accept partial result,
    or increase @max_iterations for more refinement attempts
```

---

## Block Testing Strategy

### Unit Test Template

```python
def test_block_{block_name}():
    """Unit test for {block_name} block"""

    # Arrange
    input_data = {
        # Typical input
    }
    expected_output = {
        # Expected output shape
    }

    # Act
    result = {block_name}(input_data)

    # Assert
    assert result.keys() == expected_output.keys()
    assert result['primary_field'] in expected_range

    # Property: Deterministic
    result2 = {block_name}(input_data)
    assert result == result2  # Same input → same output

    # Property: Bounded
    assert 0 <= result['score'] <= 1  # If applicable
```

### Composition Test Template

```python
def test_composition_{block_a}_{block_b}():
    """Test composition: {block_a} → {block_b}"""

    # Arrange
    input_data = "test task"

    # Act
    intermediate = {block_a}(input_data)
    final = {block_b}(intermediate)

    # Assert type compatibility
    assert type(intermediate) == {block_b}.input_type

    # Assert composition equivalence
    composed = sequence({block_a}, {block_b})
    composed_result = composed(input_data)
    assert composed_result == final
```

### Categorical Law Tests

```python
def test_monad_associativity():
    """(f >=> g) >=> h = f >=> (g >=> h)"""
    f = assess_quality
    g = extract_improvement
    h = apply_refinement

    input_data = "test output"

    # Left grouping
    fg = kleisli(f, g)
    fgh_left = kleisli(fg, h)
    result_left = fgh_left(input_data)

    # Right grouping
    gh = kleisli(g, h)
    fgh_right = kleisli(f, gh)
    result_right = fgh_right(input_data)

    # Assert associativity (output equivalence)
    assert result_left.quality == result_right.quality
```

---

## Integration with Existing Commands

### /meta Internal Block Flow

```
/meta "task"
    │
    ├─► assess_difficulty(task) → difficulty
    ├─► assess_domain(task) → domain
    │       │
    │       ▼
    ├─► select_tier(difficulty, domain) → tier
    │       │
    │       ▼
    ├─► select_strategy(tier) → strategy
    │       │
    │       ▼
    ├─► build_template(context, strategy) → template
    │       │
    │       ▼
    ├─► apply_transform(template, task) → prompt
    │       │
    │       ▼
    └─► execute_prompt(prompt) → output
```

### /rmp Internal Block Flow

```
/rmp @quality:0.85 "task"
    │
    ├─► apply_transform(default_template, task) → prompt
    │       │
    │       ▼
    ├─► execute_prompt(prompt) → output
    │       │
    │       ▼
    ├─► assess_quality(output) → quality
    │       │
    │       ▼
    ├─► evaluate_convergence(quality, 0.85, iteration) → status
    │       │
    │       ├── CONVERGED → return output
    │       │
    │       └── CONTINUE ──┐
    │                      │
    │       ┌──────────────┘
    │       ▼
    ├─► extract_improvement(output, quality) → direction
    │       │
    │       ▼
    └─► apply_refinement(output, direction) → refined_output
            │
            └─► (loop back to assess_quality)
```

### /route Internal Block Flow

```
/route "task"
    │
    ├─► assess_difficulty(task) → difficulty
    │       │
    │       ▼
    ├─► assess_domain(task) → domain
    │       │
    │       ▼
    └─► dispatch(difficulty, domain) → selected_command
            │
            ├── difficulty < 0.3 → /meta (DIRECT)
            ├── domain == DEBUG → /debug
            ├── domain == REVIEW → /review
            ├── 0.3 ≤ diff ≤ 0.7 → /meta @tier:L3-L4
            └── difficulty > 0.7 → /rmp or /hekat
```

---

## Block Override Syntax

### Single Block Override

```bash
# Override assessment
/meta @block:assess_domain:SECURITY "task"

# Override quality threshold in refinement
/rmp @block:evaluate_convergence.threshold:0.9 "task"

# Override merge strategy in parallel
/chain @block:parallel.merge:weighted [...] "task"
```

### Multiple Block Overrides

```bash
/meta @block:assess_domain:API @block:select_strategy.bias:quality "task"
```

### Block Replacement

```bash
# Replace entire block with custom implementation
/meta @block:assess_difficulty:custom_difficulty_v2 "task"
```

---

## Version

**Specification Version**: 1.0.0
**Compatibility**: Extends meta-self v2.3
**Foundation**: Category Theory (F, M, W, α, E, [0,1]-enriched)
**Blocks**: 16 (4 Assessment + 4 Transformation + 4 Refinement + 4 Composition)
**Created**: 2025-12-01
