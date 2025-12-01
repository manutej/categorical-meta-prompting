---
name: dynamic-prompt-registry
description: "Dynamic prompt registry with unified categorical syntax. Supports @skills:discover(), @skills:compose(A⊗B), Reader monad for runtime lookup, and quality-tracked prompt libraries. Use for meta-prompts referencing sub-prompts, building prompt libraries, implementing deferred resolution, or composing templates dynamically."
---

# Dynamic Prompt Registry

A categorical extension for dynamic prompt lookup and composition with unified syntax support.

## Unified Syntax Integration

```bash
# Skill discovery
/meta-command @skills:discover(domain=API,relevance>0.7) "create testing command"

# Skill composition (tensor product)
/meta-command @skills:compose(api-testing⊗jest-patterns) "create test suite"

# Explicit skill list
/meta-command @skills:api-testing,validation "create endpoint command"
```

**Unified Framework Integration**: This skill implements **Functor F** composition from the categorical framework.
- See also: `categorical-meta-prompting` skill for full F/M/W integration
- See also: `/route` command for functor-based task routing
- Quality tracking: [0,1]-enriched category with tensor product for composition

## Core Concept

```
Meta-Prompt with Dynamic References:
┌─────────────────────────────────────────────────────────┐
│  Analyze: {var:problem}                                 │
│                                                         │
│  Step 1: Break down the problem                         │
│  Step 2: {prompt:fibonacci}     ← DYNAMIC LOOKUP        │
│  Step 3: {prompt:validator}     ← DYNAMIC LOOKUP        │
│                                                         │
│  Return the validated result                            │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
           ┌──────────────────┐
           │  Prompt Registry │
           │  ─────────────── │
           │  fibonacci: 0.95 │  ← Quality-tracked
           │  validator: 0.92 │
           │  sorting: 0.88   │
           └──────────────────┘
```

## Categorical Foundations

### Reader Monad (Environment Access)

```python
from extensions.dynamic_prompt_registry import Reader, ask, asks

# Reader[PromptRegistry, A] = PromptRegistry → A

# Lookup is a Reader operation
lookup_fib = asks(lambda reg: reg.get("fibonacci"))

# Compose lookups monadically
program = (
    lookup_fib >>= (lambda fib:
    asks(lambda reg: reg.get("validator")) >>= (lambda val:
    Reader.pure(f"{fib.template}\n{val.template}")))
)

# Run against registry
result = program.run(registry)
```

### Free Applicative (Prompt Queues)

```python
from extensions.dynamic_prompt_registry import PromptQueue, Lookup, Literal

# Build AST without executing
queue = (PromptQueue.empty()
    .literal("Analyze the problem:")
    .lookup("fibonacci")        # Deferred - resolved later
    .lookup("validator")
    .branch(
        lambda ctx: ctx.get("needs_detail"),
        then=PromptQueue.from_lookup("detailed_explanation"),
        else_=PromptQueue.from_literal("Done.")
    ))

# Get all lookups for preloading
lookups = queue.get_lookups()  # ['fibonacci', 'validator', 'detailed_explanation']

# Execute against registry
result = queue.interpret(registry, context={"problem": "Find F(10)"})
```

## Unified Syntax: @skills: Modifier

### @skills:discover() - Dynamic Skill Discovery

```bash
# Discover skills by domain
@skills:discover(domain=ALGORITHM)

# Discover by relevance threshold
@skills:discover(relevance>0.7)

# Combined filters
@skills:discover(domain=API,relevance>0.8,tags=testing)
```

**Implementation**:
```python
def skills_discover(filters: Dict) -> List[Skill]:
    """
    Discover skills matching filter criteria.

    Unified syntax: @skills:discover(domain=X,relevance>Y)
    """
    results = []
    for skill in registry.all():
        if filters.get("domain") and skill.domain != filters["domain"]:
            continue
        if filters.get("relevance") and skill.quality < filters["relevance"]:
            continue
        if filters.get("tags"):
            if not filters["tags"].intersection(skill.tags):
                continue
        results.append(skill)

    return sorted(results, key=lambda s: -s.quality)
```

### @skills:compose() - Tensor Product Composition

```bash
# Compose two skills (tensor product)
@skills:compose(api-testing⊗jest-patterns)

# Chain composition (Kleisli)
@skills:compose(analyze>=>design>=>implement)

# Sequential composition
@skills:compose(research→design→implement)
```

**Implementation**:
```python
def skills_compose(expr: str) -> CompositeSkill:
    """
    Compose skills using categorical operators.

    Operators:
    - ⊗ (tensor): Combine capabilities, quality = min(q1, q2)
    - → (sequence): Chain skills, output → input
    - >=> (Kleisli): Monadic chain with quality gates
    """
    if "⊗" in expr:
        # Tensor product composition
        parts = expr.split("⊗")
        skills = [registry.get(p.strip()) for p in parts]
        return CompositeSkill(
            capabilities=union(s.capabilities for s in skills),
            quality=min(s.quality for s in skills),  # Quality degrades
            components=skills
        )
    elif "→" in expr:
        # Sequential composition
        parts = expr.split("→")
        return SequentialSkill([registry.get(p.strip()) for p in parts])
    elif ">=>" in expr:
        # Kleisli composition with quality gates
        parts = expr.split(">=>")
        return KleisliSkill([registry.get(p.strip()) for p in parts])
```

### @skills:explicit - Direct Skill List

```bash
# Explicit skill list
@skills:api-testing,validation,error-handling

# Use best skill for domain
@skills:best(domain=ALGORITHM)
```

## Reference Syntax

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{prompt:name}` | Lookup prompt by name | `{prompt:fibonacci}` |
| `{lookup:name}` | Alias for prompt | `{lookup:sorting}` |
| `{best:domain}` | Best prompt for domain | `{best:algorithms}` |
| `{var:name}` | Variable substitution | `{var:problem}` |
| `{skill:name}` | Skill reference | `{skill:api-testing}` |
| `@skills:` | Unified modifier | `@skills:discover(domain=X)` |

## Usage Patterns

### 1. Register Domain-Specific Prompts

```python
from extensions.dynamic_prompt_registry import PromptRegistry, DomainTag

registry = PromptRegistry()

# Register well-tested prompts with quality scores
registry.register(
    name="fibonacci",
    template="""Solve fibonacci({n}) using dynamic programming:
1. Create array dp[0..n]
2. Set dp[0]=0, dp[1]=1
3. For i from 2 to n: dp[i] = dp[i-1] + dp[i-2]
4. Return dp[n]""",
    domain=DomainTag.ALGORITHMS,
    quality=0.95,
    description="Optimal fibonacci using DP",
    tags={"dp", "recursion", "memoization"}
)
```

### 2. Build Meta-Prompts with @skills:

```bash
# Using @skills:discover()
/meta-command @skills:discover(domain=API,relevance>0.7) "create API testing"

# This auto-discovers: api-testing (0.92), validation (0.88), endpoint-design (0.85)
# And injects them into the meta-command context
```

### 3. Compose Skills with Tensor Product

```bash
# Tensor product: combine capabilities with quality degradation
/meta-command @skills:compose(api-testing⊗jest-patterns⊗validation) "create test suite"

# Result:
# - Combined capabilities from all three skills
# - Quality = min(0.92, 0.88, 0.91) = 0.88
```

### 4. Quality-Based Selection

```python
# Get best prompt for domain (unified syntax)
best_algo = registry.get_best_for_domain(DomainTag.ALGORITHMS)

# Find prompts meeting @quality: threshold
verified = registry.find_by_quality(min_quality=0.90)

# Use in command
# /meta @skills:best(domain=ALGORITHM) "optimize sorting"
```

### 5. Dependency Tracking

```python
# Check dependencies before execution
resolver = ReferenceResolver(registry)
is_valid, missing = resolver.validate(meta_prompt)

if not is_valid:
    print(f"Missing prompts: {missing}")
    # Register missing prompts...

# Get execution order
order = registry.topological_order("complex_solver")
```

## Composition Operators (Unified)

| Operator | Unicode | Quality Rule | Use Case |
|----------|---------|--------------|----------|
| `⊗` | U+2297 | `min(q1, q2)` | Combine capabilities |
| `→` | U+2192 | `min(q1, q2)` | Sequential pipeline |
| `>=>` | - | `max(q_iterations)` | Quality-gated chain |
| `\|\|` | - | `mean(q1, q2, ...)` | Parallel execution |

```python
# Sequential (→): Output of A → Input of B
queue1 >> queue2  # queue1 then queue2

# Tensor (⊗): Combine skills
skill_a ⊗ skill_b   # quality = min(qa, qb)

# Kleisli (>=>): Monadic with refinement
skill_a >=> skill_b  # quality improves iteratively

# Parallel (||): Concurrent execution
skill_a || skill_b || skill_c  # quality = mean(qa, qb, qc)
```

## Integration with Categorical Engine

```python
from meta_prompting_engine.categorical import CategoricalMetaPromptingEngine
from extensions.dynamic_prompt_registry import PromptRegistry, resolve_references

# Create registry with tested prompts
registry = PromptRegistry()
registry.register("analyze", ..., quality=0.90)
registry.register("solve", ..., quality=0.92)
registry.register("validate", ..., quality=0.88)

# Build meta-prompt with @skills: modifier
# /meta-command @skills:compose(analyze→solve→validate) "process data"

# Resolves to:
meta_template = """
{prompt:analyze}
{prompt:solve}
{prompt:validate}
"""

# Execute with categorical engine
result = engine.execute(Task(description=resolved))
```

## Unified Checkpoint Format

```yaml
SKILL_RESOLUTION_CHECKPOINT:
  modifier: "@skills:compose(api-testing⊗validation)"
  resolved_skills:
    - name: api-testing
      quality: 0.92
      domain: API
    - name: validation
      quality: 0.88
      domain: TESTING
  composition_type: tensor
  composite_quality: 0.88  # min(0.92, 0.88)
  status: RESOLVED
```

## Categorical Laws

### Reader Monad Laws

```python
# Left identity
Reader.pure(a).flat_map(f) == f(a)

# Right identity
m.flat_map(Reader.pure) == m

# Associativity
m.flat_map(f).flat_map(g) == m.flat_map(lambda x: f(x).flat_map(g))
```

### Quality Enrichment Laws

```python
# Tensor product quality degradation
quality(A ⊗ B) == min(quality(A), quality(B))

# Sequential quality
quality(A → B) <= min(quality(A), quality(B))

# Parallel aggregation
quality(A || B) == mean(quality(A), quality(B))
```

## Usage Examples

```bash
# Discover skills by domain
/meta-command @skills:discover(domain=API) "create endpoint"

# Compose with tensor product
/meta-command @skills:compose(testing⊗validation) "create test suite"

# Sequential composition
/meta-command @skills:compose(research→design→implement) "build feature"

# Kleisli composition with quality gates
/meta-command @skills:compose(analyze>=>refine>=>validate) @quality:0.85 "optimize code"

# Use best skill for domain
/meta-command @skills:best(domain=ALGORITHM) "implement sorting"

# Explicit skill list
/meta-command @skills:api-testing,validation "create API tests"

# Combined with other modifiers
/meta-command @mode:iterative @quality:0.85 @skills:discover(relevance>0.8) "build system"
```

## Key Benefits

1. **Modularity**: Build complex prompts from tested components
2. **Reusability**: Register once, use everywhere via @skills:
3. **Quality Tracking**: Know which prompts perform well
4. **Deferred Resolution**: Build pipelines, execute later
5. **Type Safety**: Domain tags and type annotations
6. **Composability**: Categorical structure enables clean composition
7. **Unified Syntax**: Consistent @skills: modifier across all commands

---

## Registered Prompts

### {prompt:categorical-structure}

**Domain**: FRAMEWORK
**Quality**: 0.92
**Tags**: category-theory, framework-extension, mathematical

**Description**: Universal template for implementing categorical structures (functors, monads, comonads, natural transformations, adjunctions, hom-equivalences, enriched categories) in meta-prompting frameworks.

**Template**:
```
You are implementing a categorical structure in a meta-prompting framework.

## Structure Identification

First, identify the categorical structure:
- [ ] Functor (F: C → D) - structure-preserving map
- [ ] Monad (unit, bind, join) - computation with effects
- [ ] Comonad (extract, duplicate, extend) - context-dependent computation
- [ ] Natural Transformation (α: F ⇒ G) - transformation between functors
- [ ] Adjunction (F ⊣ G) - universal pairing of functors
- [ ] Hom-Equivalence - isomorphism of hom-sets
- [ ] Enriched Category - hom-objects with extra structure

## Implementation Template

For the structure "{structure_name}":

### 1. Formal Definition
Provide the type signature:
```
{formal_type_signature}
```

### 2. Operations
List all operations with their type signatures:
- {operation_1}: {type_1} ({description_1})
- {operation_2}: {type_2} ({description_2})

### 3. Laws
State the laws that must be satisfied:
1. {law_1_name}: {law_1_statement}
2. {law_2_name}: {law_2_statement}

### 4. Command Syntax
Design the unified command syntax:
```bash
/{command_name} @mode:{operations} @{param}:{value} "task"
```

### 5. Composition Integration
Define behavior with composition operators:
- With →: {sequential_behavior}
- With ||: {parallel_behavior}
- With ⊗: {tensor_behavior}
- With >=>: {kleisli_behavior}

### 6. Quality Propagation
Specify the quality rule:
```
quality({operation}) = {quality_formula}
```

### 7. Verification Approach
Describe how to verify the laws:
- Property-based testing strategy
- Example test cases
- Edge cases to consider

## Output Format

Produce:
1. Command specification (.claude/commands/{name}.md)
2. ORCHESTRATION-SPEC.md update
3. meta-self skill update
4. Law verification tests
```

**Usage**:
```bash
# Apply to implement a new categorical structure
/meta @skills:categorical-structure "implement comonad W for context extraction"

# Use with refinement
/rmp @quality:0.85 @skills:categorical-structure "design adjunction for task-prompt"
```

---

### {prompt:command-creation}

**Domain**: FRAMEWORK
**Quality**: 0.88
**Tags**: slash-command, framework-extension, design

**Description**: Template for creating new slash commands following unified categorical syntax.

**Template**:
```
You are creating a new slash command for the categorical meta-prompting framework.

## Command Design

### 1. Purpose
What categorical operation does this command implement?
- Primary operation: {operation}
- Categorical role: {categorical_role}

### 2. Syntax Definition
```bash
/{command_name} @modifier1:value @modifier2:value [composition] "task"
```

### 3. Modifiers
| Modifier | Values | Default | Description |
|----------|--------|---------|-------------|
| @mode: | {modes} | {default_mode} | Execution mode |
| @{param}: | {values} | {default} | {description} |

### 4. Categorical Integration
- Functor aspect: {how_it_maps}
- Monad aspect: {how_it_composes}
- Quality tracking: {quality_rule}

### 5. Orchestration Patterns
```
@orchestration
  @sequential[
    → {step_1}
    → {step_2}
  ]
@end
```

### 6. Examples
```bash
# Basic usage
/{command_name} "simple task"

# With modifiers
/{command_name} @mode:iterative @quality:0.85 "complex task"

# In composition
/chain [/{command_name}→/other] "pipeline task"
```

### 7. Checkpoint Format
```yaml
CHECKPOINT_{COMMAND}_[n]:
  command: /{command_name}
  quality:
    aggregate: [0-1]
  status: [CONTINUE | CONVERGED | HALT]
```

## Output Files

1. `.claude/commands/{command_name}.md` - Command definition
2. Update `ORCHESTRATION-SPEC.md` - Add to registry
3. Update `meta-self/skill.md` - Add to reference
```

**Usage**:
```bash
/meta @skills:command-creation "create /context command for comonad operations"
```

---

### {prompt:law-verification}

**Domain**: FRAMEWORK
**Quality**: 0.85
**Tags**: testing, verification, category-theory

**Description**: Template for verifying categorical laws using property-based testing.

**Template**:
```
You are verifying categorical laws for a structure implementation.

## Law Verification Protocol

### 1. Identify Laws
For structure "{structure_name}", the laws are:
1. {law_1}: {statement_1}
2. {law_2}: {statement_2}
3. {law_3}: {statement_3}

### 2. Property-Based Tests

For each law, create a property test:

```python
from hypothesis import given, strategies as st

# Law 1: {law_1_name}
@given(st.{input_strategy})
def test_{law_1_name}(input_value):
    """
    Verify: {law_1_statement}
    """
    left_side = {left_computation}
    right_side = {right_computation}
    assert left_side == right_side, f"Law violated for {input_value}"

# Law 2: {law_2_name}
@given(st.{input_strategy})
def test_{law_2_name}(input_value):
    """
    Verify: {law_2_statement}
    """
    left_side = {left_computation}
    right_side = {right_computation}
    assert left_side == right_side
```

### 3. Edge Cases

Test these specific cases:
- Identity element: {identity_case}
- Composition: {composition_case}
- Empty/null: {empty_case}

### 4. Counterexample Analysis

If a law fails:
1. Capture the counterexample
2. Analyze which assumption was violated
3. Determine if implementation or law statement needs fixing

### 5. Documentation

Record verification results:
```yaml
LAW_VERIFICATION:
  structure: {structure_name}
  laws_tested: {count}
  laws_passed: {passed}
  laws_failed: {failed}
  counterexamples: {list}
  verification_date: {date}
  status: [VERIFIED | PARTIALLY_VERIFIED | FAILED]
```

## Output

1. Test file: `tests/test_{structure_name}_laws.py`
2. Verification log: `logs/verification/{structure_name}.md`
3. Update: `CATEGORICAL-LAWS-PROOFS.md`
```

**Usage**:
```bash
/meta @skills:law-verification "verify comonad laws for /context command"
```

---

## Categorical Workflow Prompts

### {prompt:functor-transform}

**Domain**: CORE
**Quality**: 0.90
**Tags**: functor, task-transformation, meta-prompting
**Categorical Role**: F: Task → Prompt

**Description**: Transform a task into a well-structured prompt using functor principles. Preserves task structure while adding systematic approach.

**Template**:
```
You are applying Functor F to transform a task into an effective prompt.

## Task
{task}

## Functor F: Task → Prompt

### Step 1: Structure Analysis
Identify the core structure of the task:
- Primary objective: [EXTRACT]
- Key constraints: [EXTRACT]
- Domain: [CLASSIFY: ALGORITHM | SECURITY | API | DEBUG | TESTING | GENERAL]
- Complexity: [CLASSIFY: L1-L7]

### Step 2: Structure-Preserving Transformation
Transform while preserving:
- The objective becomes the prompt goal
- Constraints become requirements
- Domain determines approach/persona

### Step 3: Prompt Construction
Build the prompt with:
1. Clear objective statement
2. Systematic approach for the domain
3. Expected output format
4. Quality criteria

## F(Task) Output
[GENERATED PROMPT]
```

**Usage**:
```bash
/meta "implement rate limiter"  # Uses functor internally
/meta @domain:SECURITY "review auth"  # Domain-specific functor
```

---

### {prompt:monad-refine}

**Domain**: CORE
**Quality**: 0.92
**Tags**: monad, refinement, quality-iteration
**Categorical Role**: M: Prompt →^n Prompt

**Description**: Iteratively refine output using monadic bind until quality threshold is met.

**Template**:
```
You are applying Monad M for iterative refinement.

## Current State
Iteration: {n}
Quality Target: {quality_threshold}
Current Output:
{current_output}

## Quality Assessment (0-1 scale)
- Correctness: [0-1] - Does it solve the problem?
- Completeness: [0-1] - Are edge cases handled?
- Clarity: [0-1] - Is it understandable?
- Efficiency: [0-1] - Is it well-designed?

Aggregate = 0.40×correctness + 0.25×clarity + 0.20×completeness + 0.15×efficiency

## M.bind Decision
IF aggregate >= {quality_threshold}:
  STATUS: CONVERGED ✓
  Return current output

ELSE:
  STATUS: CONTINUE

  ### Improvement Direction
  Lowest dimension: [IDENTIFY]
  Specific improvements needed:
  1. [IMPROVEMENT_1]
  2. [IMPROVEMENT_2]

  ### Refined Output
  [IMPROVED VERSION]
```

**Usage**:
```bash
/rmp @quality:0.85 "implement password validation"
/rmp @quality:0.9 @max_iterations:5 "optimize algorithm"
```

---

### {prompt:comonad-extract}

**Domain**: CORE
**Quality**: 0.88
**Tags**: comonad, context-extraction, focus
**Categorical Role**: W: History → Context

**Description**: Extract focused context from execution history using comonad operations.

**Template**:
```
You are applying Comonad W to extract context.

## Operation: {mode}  # extract | duplicate | extend

### W.extract: Focus on Current
IF mode == "extract":
  Focus target: {focus}  # recent | all | file | conversation
  Depth: {depth}

  Extract:
  - Relevant history entries
  - Key decisions made
  - Active files and changes
  - Current state summary

  Output: Focused context object

### W.duplicate: Meta-Observation
IF mode == "duplicate":
  Create observation of the observation:
  - What was focused on
  - What was filtered out
  - Why certain context was prioritized
  - Meta-level insights about the process

  Output: W(W(context)) for debugging prompts

### W.extend: Context-Aware Transform
IF mode == "extend":
  Transform: {transform}  # summarize | analyze | synthesize

  Apply transformation with full context access:
  - Function receives entire context, not just focused value
  - Enables context-dependent processing

  Output: Transformed context with awareness

## Comonad Laws (Verify)
- extract ∘ duplicate = id ✓
- fmap extract ∘ duplicate = id ✓
```

**Usage**:
```bash
/context @mode:extract @focus:recent @depth:5 "what have we done?"
/context @mode:duplicate "why did the prompt fail?"
/context @mode:extend @transform:summarize "executive summary"
```

---

### {prompt:nat-transform}

**Domain**: CORE
**Quality**: 0.89
**Tags**: natural-transformation, strategy-switching, optimization
**Categorical Role**: α: F ⇒ G

**Description**: Transform between prompting strategies while preserving task semantics (naturality condition).

**Template**:
```
You are applying Natural Transformation α: F_{from} ⇒ F_{to}

## Source Strategy: {from}
Quality baseline: {from_quality}
Characteristics: {from_chars}

## Target Strategy: {to}
Quality baseline: {to_quality}
Characteristics: {to_chars}

## Task
{task}

## Transformation α[{from}→{to}]

### Step 1: Extract Task Semantics
From the source prompt, identify:
- Core task objective
- Key requirements
- Domain context

### Step 2: Apply Target Strategy
Transform by adding/modifying:
{transformation_rules}

### Step 3: Verify Naturality
The naturality condition must hold:
  α_B ∘ F(f) = G(f) ∘ α_A

In practice: "Transforming then refining = Refining then transforming"
- Task semantics preserved ✓
- Transformation is uniform ✓

## Transformed Output
Strategy: {to}
Quality factor: {quality_factor}
Expected quality: {from_quality} × {quality_factor}

[TRANSFORMED PROMPT]
```

**Strategy Transformations**:
| From → To | Add | Quality Factor |
|-----------|-----|----------------|
| ZS → CoT | "Let's think step by step" + reasoning structure | 1.25 |
| ZS → FS | Examples (2-5) | 1.15 |
| FS → CoT | Convert examples to reasoning traces | 1.10 |
| CoT → ToT | Branch points + evaluation | 1.05 |
| Any → Meta | Self-reflection wrapper | 1.10-1.35 |

**Usage**:
```bash
/transform @from:zero-shot @to:chain-of-thought "explain binary search"
/transform @mode:analyze "debug intermittent test"  # Auto-recommend
```

---

### {prompt:pipeline-compose}

**Domain**: CORE
**Quality**: 0.91
**Tags**: composition, pipeline, workflow
**Categorical Role**: Kleisli composition (>=>)

**Description**: Compose multiple categorical operations into a pipeline with quality tracking.

**Template**:
```
You are composing a categorical pipeline.

## Pipeline Definition
{pipeline}  # e.g., [W→α→F→M]

## Operators
- → (Sequence): Output flows to next input, quality = min(q1, q2)
- || (Parallel): Execute concurrently, quality = mean(q1, q2, ...)
- ⊗ (Tensor): Combine capabilities, quality = min(q1, q2)
- >=> (Kleisli): Quality-gated composition, quality improves

## Stage Execution

### Stage 1: {stage_1}
Input: {input}
Operation: {op_1}
Output: {output_1}
Quality: {q_1}

### Stage 2: {stage_2}
Input: {output_1}
Operation: {op_2}
Output: {output_2}
Quality: min({q_1}, {q_2})

[Continue for each stage...]

## Pipeline Quality
Aggregate: {pipeline_quality}
Status: {COMPLETE | QUALITY_GATE_FAILED | ERROR}

## Final Output
[PIPELINE RESULT]
```

**Usage**:
```bash
/chain [/context→/transform→/meta→/rmp] "complex feature"
/chain [/review:security || /review:performance] "audit code"
```

---

## Workflow Pattern Prompts

### {prompt:bug-fix-workflow}

**Domain**: WORKFLOW
**Quality**: 0.87
**Tags**: debugging, workflow, systematic
**Pipeline**: W → F → M

**Template**:
```
## Bug Fix Workflow: W → F → M

### Phase 1: Context Extraction (W)
/context @mode:extract @focus:file "{file}"

Extract:
- Error symptoms
- Recent changes to file
- Related code
- Test failures

### Phase 2: Debug Transformation (F)
/meta @domain:DEBUG

Apply systematic debugging:
1. Reproduce the issue
2. Isolate the cause
3. Form hypothesis
4. Test hypothesis
5. Implement fix

### Phase 3: Refinement Loop (M)
/rmp @quality:0.85

Iterate until:
- Fix addresses root cause
- No regression introduced
- Tests pass
- Code quality maintained

## Output
- Fixed code
- Explanation of cause
- Test verification
```

---

### {prompt:code-review-workflow}

**Domain**: WORKFLOW
**Quality**: 0.89
**Tags**: review, parallel, quality
**Pipeline**: W → (F || F || F) → Synthesize

**Template**:
```
## Code Review Workflow: Parallel Analysis

### Phase 1: Context (W)
/context @mode:extract @focus:file

Gather:
- File purpose
- Recent changes
- Project conventions

### Phase 2: Parallel Reviews (F || F || F)

#### Security Review
/meta @domain:SECURITY @template:{context:reviewer}
- Authentication/authorization
- Input validation
- Data exposure

#### Performance Review
/meta @domain:PERFORMANCE @template:{context:reviewer}
- Algorithm efficiency
- Memory usage
- Scalability

#### Quality Review
/meta @domain:QUALITY @template:{context:reviewer}
- Code clarity
- Test coverage
- Documentation

### Phase 3: Synthesis
Aggregate: quality = mean(q_security, q_performance, q_quality)

Combine findings:
- Critical issues (must fix)
- Recommendations (should fix)
- Suggestions (nice to have)
```

---

### {prompt:feature-implementation-workflow}

**Domain**: WORKFLOW
**Quality**: 0.90
**Tags**: implementation, full-pipeline, systematic
**Pipeline**: W → α → F → M

**Template**:
```
## Feature Implementation: Full Pipeline

### Phase 1: Context Gathering (W)
/context @mode:extract @focus:all

Understand:
- Existing architecture
- Project patterns
- Related code
- Conventions

### Phase 2: Strategy Selection (α)
/transform @mode:analyze "{feature}"

Select optimal strategy based on:
- Feature complexity
- Uncertainty level
- Quality requirements

### Phase 3: Implementation (F)
/meta @tier:{tier} @template:{context:expert}+{mode:cot}

Generate implementation:
- Following project patterns
- With proper error handling
- Including tests

### Phase 4: Refinement (M)
/rmp @quality:0.88

Iterate until:
- All requirements met
- Tests pass
- Code quality ≥ 0.88

## Deliverables
- Implementation code
- Unit tests
- Integration tests
- Documentation
```

---

## Quick Reference

### Prompt Registry Summary

| Prompt | Domain | Quality | Usage |
|--------|--------|---------|-------|
| `{prompt:categorical-structure}` | FRAMEWORK | 0.92 | Implement any categorical structure |
| `{prompt:command-creation}` | FRAMEWORK | 0.88 | Create new slash commands |
| `{prompt:law-verification}` | FRAMEWORK | 0.85 | Verify categorical laws |
| `{prompt:functor-transform}` | CORE | 0.90 | Task → Prompt transformation |
| `{prompt:monad-refine}` | CORE | 0.92 | Iterative refinement |
| `{prompt:comonad-extract}` | CORE | 0.88 | Context extraction |
| `{prompt:nat-transform}` | CORE | 0.89 | Strategy switching |
| `{prompt:pipeline-compose}` | CORE | 0.91 | Pipeline composition |
| `{prompt:bug-fix-workflow}` | WORKFLOW | 0.87 | Systematic bug fixing |
| `{prompt:code-review-workflow}` | WORKFLOW | 0.89 | Multi-dimensional review |
| `{prompt:feature-implementation-workflow}` | WORKFLOW | 0.90 | Full implementation pipeline |

### By Categorical Role

| Structure | Prompt | Command |
|-----------|--------|---------|
| Functor F | `{prompt:functor-transform}` | `/meta` |
| Monad M | `{prompt:monad-refine}` | `/rmp` |
| Comonad W | `{prompt:comonad-extract}` | `/context` |
| Nat. Trans α | `{prompt:nat-transform}` | `/transform` |
| Composition | `{prompt:pipeline-compose}` | `/chain` |

---

**Registry Version**: 2.0
**Last Updated**: 2025-12-01
**Prompts Registered**: 11
**Average Quality**: 0.89
