---
name: meta-self
description: "Master reference for categorical meta-prompting unified syntax. Contains all modifiers, operators, composition patterns, and execution protocols. Use this skill for self-reference when executing any prompt workflow, ensuring consistent syntax across all commands and skills."
---

# Meta-Self: Unified Categorical Syntax Reference

This skill serves as the authoritative reference for the categorical meta-prompting framework. All commands and skills should align with this specification.

## Categorical Foundation

```
F: Task → Prompt        (Functor - structure-preserving transformation)
M: Prompt →^n Prompt    (Monad - iterative refinement)
W: History → Context    (Comonad - context extraction)
[0,1]: Quality → Quality (Enriched - quality tracking)
```

### Categorical Laws (Must Be Satisfied)

```
1. Functor Identity:     F(id) = id
2. Functor Composition:  F(g ∘ f) = F(g) ∘ F(f)
3. Monad Left Identity:  return >=> f = f
4. Monad Right Identity: f >=> return = f
5. Monad Associativity:  (f >=> g) >=> h = f >=> (g >=> h)
6. Quality Monotonicity: quality(A ⊗ B) ≤ min(quality(A), quality(B))
```

---

## Unified Modifiers

All commands support these modifiers. Place them before the task description.

### @mode: - Execution Mode

| Mode | Description | Effect |
|------|-------------|--------|
| `@mode:active` | Default execution | Execute with auto-detection |
| `@mode:iterative` | RMP loop | Iterate until @quality: met |
| `@mode:dry-run` | Preview only | Show plan, no execution |
| `@mode:spec` | Generate spec | Output YAML specification |

**Example**: `/meta @mode:iterative "build auth system"`

### @quality: - Quality Threshold

| Format | Description | Range |
|--------|-------------|-------|
| `@quality:0.85` | Target threshold | 0.0 - 1.0 |
| `@quality:85%` | Percentage form | 0% - 100% |

**Example**: `/rmp @quality:0.9 "optimize algorithm"`

### @tier: - Complexity Tier

| Tier | Tokens | Pattern | Strategy |
|------|--------|---------|----------|
| `@tier:L1` | 600-1200 | Single op | DIRECT |
| `@tier:L2` | 1500-3000 | A → B | DIRECT |
| `@tier:L3` | 2500-4500 | A → B → C | MULTI_APPROACH |
| `@tier:L4` | 3000-6000 | A \|\| B \|\| C | MULTI_APPROACH |
| `@tier:L5` | 5500-9000 | Hierarchical | AUTONOMOUS_EVOLUTION |
| `@tier:L6` | 8000-12000 | Iterative | AUTONOMOUS_EVOLUTION |
| `@tier:L7` | 12000-22000 | Ensemble | AUTONOMOUS_EVOLUTION |

**Example**: `/meta @tier:L5 "design microservices"`

### @budget: - Token Budget

| Format | Description |
|--------|-------------|
| `@budget:20000` | Total tokens |
| `@budget:[5K,4K,6K]` | Per-agent allocation |
| `@budget:auto` | Automatic calculation |

**Example**: `/task-relay @budget:[5000,4000,6000] [R→D→I]`

### @variance: - Budget Variance Threshold

| Format | Description | Action |
|--------|-------------|--------|
| `@variance:15%` | Acceptable variance | WARN if exceeded |
| `@variance:20%` | Default | HALT if exceeded |

**Example**: `/hekat @budget:18K @variance:15% [R→D→I]`

### @max_iterations: - Iteration Limit

| Format | Description |
|--------|-------------|
| `@max_iterations:5` | Maximum RMP iterations |
| `@max_iterations:3` | Fewer iterations |

**Example**: `/rmp @quality:0.9 @max_iterations:3 "task"`

### @template: - Template Components

| Format | Description |
|--------|-------------|
| `@template:{context:expert}` | Single component |
| `@template:{context:X}+{mode:Y}+{format:Z}` | Combined |

**Components**:
- `{context:expert\|teacher\|reviewer\|debugger}`
- `{mode:direct\|cot\|multi\|iterative}`
- `{format:prose\|structured\|code\|checklist}`

**Example**: `/meta @template:{context:expert}+{mode:cot}+{format:code} "implement"`

### @domain: - Force Domain Classification

| Domain | Use Case |
|--------|----------|
| `@domain:ALGORITHM` | Algorithmic correctness |
| `@domain:SECURITY` | Security review |
| `@domain:API` | API design/review |
| `@domain:DEBUG` | Debugging |
| `@domain:TESTING` | Test generation |

**Example**: `/meta @domain:SECURITY "review auth code"`

### @skills: - Skill Discovery & Composition

| Format | Description |
|--------|-------------|
| `@skills:discover(domain=X)` | Discover by domain |
| `@skills:discover(relevance>0.7)` | Discover by quality |
| `@skills:compose(A⊗B)` | Tensor composition |
| `@skills:compose(A→B→C)` | Sequential |
| `@skills:compose(A>=>B)` | Kleisli |
| `@skills:skill1,skill2` | Explicit list |
| `@skills:best(domain=X)` | Best for domain |

**Example**: `/meta-command @skills:compose(api-testing⊗validation) "create tests"`

---

## Composition Operators

### → (Sequence) - Kleisli Composition

**Unicode**: U+2192
**Meaning**: Output of A becomes input of B
**Quality**: `quality(A → B) ≤ min(quality(A), quality(B))`

```bash
# Command syntax
/chain [/debug→/review→/test] "error in auth.py"

# Agent syntax
[R→D→I→T] "build feature"

# Skill syntax
@skills:compose(research→design→implement)
```

### || (Parallel) - Concurrent Execution

**Meaning**: Execute A, B, C concurrently, aggregate results
**Quality**: `quality(A || B || C) = mean(quality(A), quality(B), quality(C))`

```bash
# Parallel commands
/chain [/review-security || /review-performance] "audit code"

# Parallel agents
[R||D||A] "evaluate options"

# Mixed
[R→(D||F)→I] "full-stack with parallel design"
```

### ⊗ (Tensor) - Quality-Degrading Combination

**Unicode**: U+2297
**Meaning**: Combine capabilities, quality degrades to minimum
**Quality**: `quality(A ⊗ B) = min(quality(A), quality(B))`

```bash
# Skill tensor
@skills:compose(api-testing⊗jest-patterns⊗validation)

# Agent tensor
[debug-detective⊗test-engineer] "fix and test"
```

### >=> (Kleisli) - Monadic Refinement

**Meaning**: Composition with quality-gated iteration at each stage
**Quality**: `quality(A >=> B)` improves with each iteration

```bash
# RMP stages
/rmp @quality:0.85 [analyze>=>design>=>implement] "build feature"

# Each stage:
# 1. Execute
# 2. Assess quality
# 3. If quality < threshold: refine
# 4. Pass to next stage
```

---

## Command Invocation Syntax

### Standard Pattern

```
/<command> @modifier1:value @modifier2:value [composition] "task description"
```

### Examples

```bash
# Simple
/meta "implement rate limiter"

# With modifiers
/meta @mode:iterative @quality:0.85 "build API"

# With composition
/chain [/debug→/fix→/test] "TypeError in auth.py"

# Full syntax
/hekat @mode:active @tier:L5 @budget:18K [R→D→(I||T)] "build auth system"

# With skills
/meta-command @skills:discover(domain=API) @mode:iterative "create endpoint"
```

---

## Agent Hotkeys (HEKAT Compatible)

### Tier 1 - Single Agent

| Key | Agent | Domain |
|-----|-------|--------|
| `[R]` | deep-researcher | Research |
| `[D]` | api-architect | Design |
| `[I]` | practical-programmer | Implementation |
| `[T]` | test-engineer | Testing |
| `[B]` | build-engineer | Build |
| `[F]` | frontend-specialist | Frontend |
| `[A]` | analyzer | Analysis |

### Tier 2 - Ctrl Modifiers

| Key | Effect |
|-----|--------|
| `[Ctrl+P]` | L4 Parallel mode |
| `[Ctrl+H]` | L5 Hierarchical mode |
| `[Ctrl+I]` | L6 Iterative mode |

### Tier 3 - Agent Chains

```bash
[R→D→I]        # Research → Design → Implement
[R→D→I→T]      # Full pipeline with testing
[P:R||D||A]    # Parallel: Research, Design, Analyze
[R→(D||F)→I]   # Mixed: Research, parallel Design/Frontend, Implement
```

---

## Quality Assessment Structure

### Multi-Dimensional Quality Vector

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Correctness | 40% | Does it solve the problem? |
| Clarity | 25% | Is it understandable? |
| Completeness | 20% | Are edge cases handled? |
| Efficiency | 15% | Is it well-designed? |

### Aggregate Score

```
aggregate = (0.40 × correctness) + (0.25 × clarity) +
            (0.20 × completeness) + (0.15 × efficiency)
```

### Quality Thresholds

| Score | Status | Action |
|-------|--------|--------|
| ≥0.9 | Excellent | Stop, success |
| 0.8-0.9 | Good | Stop, success |
| 0.7-0.8 | Acceptable | Continue if @mode:iterative |
| 0.6-0.7 | Poor | Refine if iterations remain |
| <0.6 | Failed | Abort or restructure |

---

## Checkpoint Format

All commands produce standardized checkpoints:

```yaml
CHECKPOINT_[type]_[n]:
  command: /[command]
  iteration: [n]
  quality:
    correctness: [0-1]
    clarity: [0-1]
    completeness: [0-1]
    efficiency: [0-1]
    aggregate: [0-1]
  quality_delta: [+/- from previous]
  budget:
    used: [tokens]
    remaining: [tokens]
    variance: [%]
  status: [CONTINUE | CONVERGED | MAX_ITERATIONS | HALT]
  trend: [RAPID_IMPROVEMENT | STEADY_IMPROVEMENT | PLATEAU | DEGRADING]
```

---

## Workflow Patterns

### Pattern 1: Simple Task

```bash
/meta "task"
```
- Auto-detect domain, tier, template
- Single-pass execution

### Pattern 2: Quality-Gated Iteration

```bash
/rmp @quality:0.85 @max_iterations:5 "task"
```
- Iterate until quality threshold
- Track quality improvement

### Pattern 3: Multi-Stage Pipeline

```bash
/chain [/analyze→/design→/implement→/test] "feature"
```
- Sequential execution
- Output → Input flow

### Pattern 4: Parallel Exploration

```bash
/chain [/approach-a || /approach-b || /approach-c] "evaluate options"
```
- Concurrent execution
- Aggregate results

### Pattern 5: Hierarchical Orchestration

```bash
/hekat @tier:L5 [Lead→(Worker||Worker)→Synthesize] "complex task"
```
- Lead agent coordinates
- Workers execute in parallel
- Synthesizer combines results

### Pattern 6: Skill-Driven Meta-Command

```bash
/meta-command @skills:discover(domain=API,relevance>0.7) "create endpoint command"
```
- Auto-discover relevant skills
- Inject into command creation

---

## Mode Behaviors

### @mode:active
- Execute immediately
- Auto-detect all parameters
- Single-pass unless combined with @mode:iterative

### @mode:iterative
- Enable RMP loop
- Iterate until @quality: threshold
- Track quality across iterations

### @mode:dry-run
- Show execution plan
- Do not execute
- Exit after plan display

### @mode:spec
- Generate YAML specification
- Do not execute
- Exit after spec generation

---

## Error Handling

### Budget Exceeded

```yaml
STATUS: HALT
reason: "Budget variance exceeded @variance: threshold"
action: "Review agent outputs, adjust budget allocation"
```

### Quality Plateau

```yaml
STATUS: NO_IMPROVEMENT
reason: "Quality improvement < 0.02 for 2 iterations"
action: "Fixed-point reached, returning best result"
```

### Max Iterations

```yaml
STATUS: MAX_ITERATIONS
reason: "Reached @max_iterations: limit"
action: "Return best result from iterations"
```

---

## Self-Reference Protocol

When executing any command or skill:

1. **Check modifiers**: Parse all @modifier: values
2. **Apply defaults**: Use defaults for unspecified modifiers
3. **Validate syntax**: Ensure operators match specification
4. **Execute**: Follow categorical laws
5. **Checkpoint**: Output standardized checkpoint
6. **Quality assess**: Evaluate using multi-dimensional vector
7. **Decide**: CONTINUE, CONVERGE, or HALT based on rules

---

## Command Reference Quick Look

| Command | Purpose | Key Modifiers |
|---------|---------|---------------|
| `/meta` | Categorical meta-prompting | @mode:, @tier:, @template:, @domain: |
| `/rmp` | Recursive meta-prompting loop | @quality:, @max_iterations:, @mode: |
| `/chain` | Command composition | @mode:, @budget:, @quality: |
| `/review` | Domain-aware code review | @domain: |
| `/debug` | Systematic debugging | @mode: |
| `/build-prompt` | Template assembly | @template: |
| `/route` | Dynamic routing | @domain: |
| `/hekat` | Agent orchestration DSL | @tier:, @budget:, @variance: |
| `/meta-command` | Create new commands | @skills:, @mode: |
| `/task-relay` | Multi-agent relay | @budget:, @pattern: |

---

## Skill Reference Quick Look

| Skill | Purpose | Integration |
|-------|---------|-------------|
| `recursive-meta-prompting` | RMP implementation patterns | @mode:iterative |
| `dynamic-prompt-registry` | Prompt lookup/composition | @skills:, {prompt:} |
| `quality-enriched-prompting` | [0,1]-enriched quality | @quality: |
| `meta-self` | This reference | Self-reference |

---

## Validation Checklist

Before executing any prompt:

- [ ] All modifiers use `@name:value` syntax
- [ ] Operators match: `→`, `||`, `⊗`, `>=>`
- [ ] Quality thresholds in [0,1] range
- [ ] Budget values are positive integers or "auto"
- [ ] Tier values are L1-L7
- [ ] Mode values are: active, iterative, dry-run, spec
- [ ] Composition brackets match: `[...]`
- [ ] Task description is quoted: `"task"`

---

## Version

**Specification Version**: 2.0
**Compatibility**: 100% backward compatible
**Foundation**: Category Theory (F, M, W, [0,1]-enriched)
