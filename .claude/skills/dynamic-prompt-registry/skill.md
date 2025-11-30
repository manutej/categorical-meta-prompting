---
name: dynamic-prompt-registry
description: Dynamic prompt registry with Reader monad for runtime prompt lookup and composition. Use when building meta-prompts that reference sub-prompts by name, creating prompt libraries with quality tracking, implementing deferred prompt resolution, or composing well-tested prompt templates dynamically.
---

# Dynamic Prompt Registry

A categorical extension for dynamic prompt lookup and composition, enabling meta-prompts to reference well-tested sub-prompts at runtime.

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

# Introspect before execution
print(queue.describe())
# PromptQueue:
#   1. Literal(user: 'Analyze the problem:')
#   2. Lookup('fibonacci')
#   3. Lookup('validator')
#   4. Conditional(needs_detail)

# Get all lookups for preloading
lookups = queue.get_lookups()  # ['fibonacci', 'validator', 'detailed_explanation']

# Execute against registry
result = queue.interpret(registry, context={"problem": "Find F(10)"})
```

## Reference Syntax

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{prompt:name}` | Lookup prompt by name | `{prompt:fibonacci}` |
| `{lookup:name}` | Alias for prompt | `{lookup:sorting}` |
| `{best:domain}` | Best prompt for domain | `{best:algorithms}` |
| `{var:name}` | Variable substitution | `{var:problem}` |
| `{name}` | Legacy variable | `{input}` |

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

registry.register(
    name="binary_search",
    template="""Find {target} in sorted array {arr}:
1. Set low=0, high=len-1
2. While low <= high:
   - mid = (low + high) // 2
   - If arr[mid] == target: return mid
   - If arr[mid] < target: low = mid + 1
   - Else: high = mid - 1
3. Return -1 (not found)""",
    domain=DomainTag.ALGORITHMS,
    quality=0.93,
)
```

### 2. Build Meta-Prompts with References

```python
from extensions.dynamic_prompt_registry import ReferenceResolver

resolver = ReferenceResolver(registry)

meta_prompt = """
You are an expert algorithm tutor.

Student question: {var:question}

To solve this, apply the following approach:

{prompt:fibonacci}

Then validate your solution:
{prompt:validator}
"""

# Resolve references
result = resolver.resolve(
    meta_prompt,
    variables={"question": "How do I compute F(50)?"}
)

print(result.resolved)
# Fully resolved prompt with inlined sub-prompts

print(result.resolved_refs)  # ['fibonacci', 'validator']
```

### 3. Deferred Resolution with PromptQueue

```python
from extensions.dynamic_prompt_registry import PromptQueue, literal, lookup, sequence

# Build queue (no execution yet)
algorithm_pipeline = (
    literal("You are solving an algorithm problem.")
    >> lookup("problem_analysis")
    >> lookup("solution_approach")
    >> lookup("complexity_analysis")
    >> literal("Provide the final solution.")
)

# Interpret with different registries
dev_result = algorithm_pipeline.interpret(dev_registry)
prod_result = algorithm_pipeline.interpret(prod_registry)
```

### 4. Quality-Based Selection

```python
# Get best prompt for domain
best_algo = registry.get_best_for_domain(DomainTag.ALGORITHMS)

# Find prompts meeting quality threshold
verified = registry.find_by_quality(min_quality=0.90)

# Use in meta-prompt
meta = """
Apply the best algorithm approach:
{best:algorithms}
"""
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
# Returns prompts in dependency order
```

## Composition Operators

```python
# Sequential (>>)
queue1 >> queue2  # queue1 then queue2

# Concatenation (+)
queue1 + queue2   # Append steps

# Branching
queue.branch(
    predicate=lambda ctx: ctx["complexity"] > 0.7,
    then=lookup("advanced_solver"),
    else_=lookup("simple_solver")
)

# Parallel
queue.parallel(
    lookup("approach_a"),
    lookup("approach_b"),
    lookup("approach_c"),
    combiner=select_best
)
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

# Build meta-prompt with references
meta_template = """
{prompt:analyze}
{prompt:solve}
{prompt:validate}
"""

# Resolve before execution
resolved = resolve_references(meta_template, registry)

# Execute with categorical engine
result = engine.execute(Task(description=resolved))
```

## Categorical Laws

### Reader Monad Laws

```python
from extensions.dynamic_prompt_registry.reader import verify_reader_laws

laws = verify_reader_laws()
# {'left_identity': True, 'right_identity': True, 'associativity': True}
```

### Quality Enrichment

The registry provides [0,1]-enriched structure:
- Each prompt has a quality score in [0, 1]
- Composition degrades quality: `min(q1, q2)`
- Domain thresholds ensure minimum quality

## File Structure

```
extensions/dynamic-prompt-registry/
├── __init__.py       # Module exports
├── registry.py       # PromptRegistry, DomainTag, QualityMetrics
├── reader.py         # Reader monad implementation
├── queue.py          # PromptQueue (Free Applicative)
└── resolver.py       # Reference resolution ({prompt:name})
```

## Key Benefits

1. **Modularity**: Build complex prompts from tested components
2. **Reusability**: Register once, use everywhere
3. **Quality Tracking**: Know which prompts perform well
4. **Deferred Resolution**: Build pipelines, execute later
5. **Type Safety**: Domain tags and type annotations
6. **Composability**: Categorical structure enables clean composition
