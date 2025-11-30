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
