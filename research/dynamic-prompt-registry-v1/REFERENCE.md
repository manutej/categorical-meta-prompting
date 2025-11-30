# Dynamic Prompt Registry - Research Archive (v1)

## What This Contains

This folder preserves the theoretical/aspirational implementation of a dynamic prompt registry with categorical foundations. It was moved here because:

1. **It doesn't run** - Import structure is broken
2. **It's over-engineered** - 2548 lines for ~200 lines of actual function
3. **But the concepts are valuable** - Worth preserving for future reference

## File Reference

| File | Lines | What It Contains | What's Valuable |
|------|-------|------------------|-----------------|
| `reader.py` | 207 | Reader monad implementation | **Actually works.** Monad laws verified. Copy this. |
| `registry.py` | 407 | PromptRegistry, DomainTag, QualityMetrics | Good API design. Needs simpler implementation. |
| `queue.py` | 433 | PromptQueue "Free Applicative" | Concept of build→introspect→interpret. Implementation is just a list. |
| `resolver.py` | 287 | Reference resolution `{prompt:name}` | Regex patterns are useful. Over-complicated. |
| `selector.py` | 422 | AppropriatePromptSelector | Concept of domain classification. Implementation is keyword matching. |
| `integration.py` | 291 | Engine integration | Dead code - depends on non-existent engine. |
| `registry_cli.py` | 232 | CLI interface | Good interface, broken imports. |
| `__init__.py` | 65 | Module exports | Reference for what to export. |

## Concepts Worth Keeping

### 1. Reader Monad (Solid)
```
Location: reader.py
Status: Works
Use for: Deferred prompt lookup, composable environment access
```

### 2. Registry API Design (Good)
```python
# From registry.py - this API is clean
registry.register(name, template, domain, quality)
registry.get(name)
registry.find_by_domain(domain)
registry.find_by_quality(min_quality)
```

### 3. Reference Syntax (Useful)
```
{prompt:name}     - Lookup prompt by name
{var:name}        - Variable substitution
{best:domain}     - Best prompt for domain
```

### 4. Domain Classification (Concept)
```python
# From selector.py - the concept, not the implementation
DomainTag: ALGORITHMS, MATHEMATICS, CODE_GENERATION, CODE_REVIEW, etc.
```

### 5. PromptQueue Pattern (Concept)
```python
# Build pipeline, inspect before execution
queue = (PromptQueue.empty()
    .literal("Analyze")
    .lookup("fibonacci")
    .branch(predicate, then_queue, else_queue))

# Introspect
queue.get_lookups()  # ['fibonacci']

# Execute
queue.interpret(registry)
```

## What Was Wrong

1. **Relative imports without package structure** - Add `__init__.py` to parent
2. **150 hardcoded keywords** - Should use embeddings or Claude classification
3. **Arbitrary scoring weights** - (0.3, 0.2, 0.15, 0.1, 0.25) with no justification
4. **"Parallel" that's sequential** - False advertising
5. **Claims without verification** - Called things "Functor" without proving laws

## How To Reuse

### To extract the Reader monad:
```bash
cp research/dynamic-prompt-registry-v1/reader.py extensions/dynamic-prompt-registry/
# Remove relative imports from line 1
# Works standalone
```

### To extract the reference patterns:
```python
# From resolver.py lines 49-54
PATTERNS = {
    'prompt': r'\{prompt:([a-zA-Z_][a-zA-Z0-9_]*)\}',
    'lookup': r'\{lookup:([a-zA-Z_][a-zA-Z0-9_]*)\}',
    'best': r'\{best:([a-zA-Z_][a-zA-Z0-9_]*)\}',
    'var': r'\{var:([a-zA-Z_][a-zA-Z0-9_]*)\}',
}
```

### To use the API design:
```python
# Simplified version of registry.py
class PromptRegistry:
    def __init__(self):
        self.prompts = {}

    def register(self, name, template, domain=None, quality=0.0):
        self.prompts[name] = {"template": template, "domain": domain, "quality": quality}

    def get(self, name):
        return self.prompts.get(name, {}).get("template")
```

## Lessons Learned

1. **Test before you write 2000 more lines**
2. **Categorical formalism is decoration unless you verify laws**
3. **Start with 50 lines that work, not 2500 that don't**
4. **Keyword matching is not "semantic selection"**
5. **Self-assessment is unreliable - test externally**

## Commit History

This code was developed in branch `claude/dynamic-prompt-meta-prompting-01G5LUMCYZY3uMhm3453KHTw` with commits:
- `02e8aee` - Initial implementation
- `4a8cbdb` - Added slash commands
- `00d24a6` - Honest assessment
- (next) - Archived to research/
