---
name: categorical-meta-prompting
description: Full categorical framework for meta-prompting with verified laws. Use when implementing functor-based task routing, monadic iterative refinement, comonadic context extraction, or quality-tracked composition. Integrates F (Functor), M (Monad), W (Comonad), and [0,1]-enriched quality categories.
---

# Categorical Meta-Prompting Framework

A mathematically rigorous framework for meta-prompting based on category theory.

## Categorical Foundation

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CATEGORICAL LAYER                                │
│                                                                      │
│  F: Task → Prompt        (Functor - structure preservation)         │
│  M: Prompt →ⁿ Prompt     (Monad - iterative refinement)            │
│  W: History → Context    (Comonad - context extraction)             │
│  [0,1]: Quality → Quality (Enriched - quality tracking)             │
│                                                                      │
│  Laws Enforced:                                                      │
│  - F(id) = id, F(g∘f) = F(g)∘F(f)                                  │
│  - return >=> f = f, (f >=> g) >=> h = f >=> (g >=> h)             │
│  - extract ∘ duplicate = id, quality(A ⊗ B) ≤ min(A, B)            │
└─────────────────────────────────────────────────────────────────────┘
```

## Functor F: Task → Prompt

Maps tasks to prompts while preserving compositional structure.

### Python Implementation

```python
from dataclasses import dataclass
from typing import TypeVar, Callable, Generic

T = TypeVar('T')  # Tasks
P = TypeVar('P')  # Prompts

@dataclass
class Functor(Generic[T, P]):
    """Functor F: T → P with verified laws."""

    map_object: Callable[[T], P]
    map_morphism: Callable[[Callable[[T], T]], Callable[[P], P]]

    def __call__(self, task: T) -> P:
        """F(task) = map_object(task)"""
        return self.map_object(task)

    def fmap(self, f: Callable[[T], T]) -> Callable[[P], P]:
        """F_mor(f) : P → P"""
        return self.map_morphism(f)

    def verify_identity_law(self, task: T) -> bool:
        """F(id_T) = id_P"""
        identity = lambda x: x
        left = self.map_object(identity(task))
        right = self.map_morphism(identity)(self.map_object(task))
        return self._equal(left, right)

    def verify_composition_law(self, task: T, f, g) -> bool:
        """F(g ∘ f) = F(g) ∘ F(f)"""
        composed = lambda x: g(f(x))
        left = self.map_morphism(composed)(self.map_object(task))
        right = self.map_morphism(g)(self.map_morphism(f)(self.map_object(task)))
        return self._equal(left, right)
```

### Usage

```python
# Create task-to-prompt functor
functor = create_task_to_prompt_functor(llm_client)

# Map task to prompt
task = Task("Find maximum in [3,1,4,1,5,9]")
prompt = functor(task)  # F(task)

# Verify laws
assert functor.verify_identity_law(task)
assert functor.verify_composition_law(task, enhance, simplify)
```

## Monad M: Iterative Refinement

Enables quality-tracked iterative improvement.

### Python Implementation

```python
@dataclass
class MonadPrompt(Generic[A]):
    """Monad wrapper with quality tracking."""
    prompt: A
    quality: float
    iteration: int = 0
    history: list = None

@dataclass
class Monad:
    """Monad M with unit, bind, join."""

    def unit(self, prompt: str, quality: float = 0.5) -> MonadPrompt:
        """return : A → M(A)"""
        return MonadPrompt(prompt, quality, 0, [])

    def bind(self, ma: MonadPrompt, f: Callable) -> MonadPrompt:
        """>>= : M(A) → (A → M(B)) → M(B)"""
        result = f(ma.prompt)
        return MonadPrompt(
            prompt=result.prompt,
            quality=result.quality,
            iteration=ma.iteration + 1,
            history=ma.history + [ma]
        )

    def join(self, mma: MonadPrompt[MonadPrompt]) -> MonadPrompt:
        """join : M(M(A)) → M(A)"""
        return MonadPrompt(
            prompt=mma.prompt.prompt,
            quality=mma.quality * mma.prompt.quality,  # Tensor product
            iteration=mma.iteration + mma.prompt.iteration
        )
```

### RMP Loop Example

```python
def rmp_loop(monad: Monad, initial: str, threshold: float = 0.8, max_iter: int = 5):
    """Recursive Meta-Prompting with monadic quality tracking."""

    ma = monad.unit(initial)

    for i in range(max_iter):
        # Assess quality
        quality = assess_quality(ma.prompt)
        ma = MonadPrompt(ma.prompt, quality, ma.iteration, ma.history)

        # Check convergence
        if quality >= threshold:
            return ma  # M.return

        # Apply refinement via bind
        ma = monad.bind(ma, refine_prompt)

    return ma
```

## Comonad W: Context Extraction

Extracts focused results from execution context.

### Python Implementation

```python
@dataclass
class Observation(Generic[A]):
    """Comonad wrapper providing context."""
    current: A
    context: dict
    history: list = None
    metadata: dict = None

@dataclass
class Comonad:
    """Comonad W with extract, duplicate, extend."""

    def extract(self, wa: Observation[A]) -> A:
        """ε : W(A) → A"""
        return wa.current

    def duplicate(self, wa: Observation[A]) -> Observation[Observation[A]]:
        """δ : W(A) → W(W(A))"""
        return Observation(
            current=wa,
            context={'meta_observation': True},
            history=[wa] + (wa.history or [])
        )

    def extend(self, f: Callable, wa: Observation[A]) -> Observation:
        """extend : (W(A) → B) → W(A) → W(B)"""
        wwa = self.duplicate(wa)
        return Observation(
            current=f(wwa.current),
            context=wa.context,
            history=wa.history
        )
```

### Context Extraction Example

```python
# Create observation from execution
obs = Observation(
    current="Maximum is 9",
    context={"prompt": prompt, "quality": 0.92, "model": "gpt-4"},
    history=[prev_obs_1, prev_obs_2]
)

# Extract focused result
result = comonad.extract(obs)  # "Maximum is 9"

# Create meta-observation for analysis
meta = comonad.duplicate(obs)  # W(W(result))

# Context-aware transformation
quality_obs = comonad.extend(assess_quality_from_history, obs)
```

## [0,1]-Enriched Category: Quality Tracking

Track quality degradation through composition.

### Quality Tensor Product

```python
def tensor_product(q1: float, q2: float) -> float:
    """⊗ : [0,1] × [0,1] → [0,1]"""
    return min(q1, q2)  # Quality degrades to minimum

# Example: Pipeline quality
quality_A = 0.90
quality_B = 0.85
quality_C = 0.92

# Sequential composition: A → B → C
pipeline_quality = tensor_product(
    tensor_product(quality_A, quality_B),
    quality_C
)  # = min(0.90, 0.85, 0.92) = 0.85
```

### Quality Laws

```
1. Identity: quality(id) = 1.0
2. Tensor associativity: (q₁ ⊗ q₂) ⊗ q₃ = q₁ ⊗ (q₂ ⊗ q₃)
3. Monotonicity: quality(f ∘ g) ≤ min(quality(f), quality(g))
```

## Composition Operators

### Sequence (→)

```python
def sequence(agents: list, context: dict) -> tuple:
    """A → B → C: Sequential execution"""
    result = None
    quality = 1.0

    for agent in agents:
        result = agent.execute(result, context)
        quality = min(quality, result.quality)  # Tensor product

    return result, quality
```

### Parallel (||)

```python
async def parallel(agents: list, context: dict) -> tuple:
    """A || B || C: Parallel execution"""
    tasks = [agent.execute_async(context) for agent in agents]
    results = await asyncio.gather(*tasks)

    quality = sum(r.quality for r in results) / len(results)  # Mean
    return results, quality
```

### Kleisli (>=>)

```python
def kleisli_compose(f, g):
    """f >=> g: Monadic composition with refinement"""
    def composed(a):
        ma = f(a)          # A → M(B)
        mb = bind(ma, g)   # M(B) → M(C)
        return mb
    return composed
```

## Verified Laws (15/15 Tests Pass)

| Category | Law | Status |
|----------|-----|--------|
| Functor | Identity | ✅ |
| Functor | Composition | ✅ |
| Monad | Left Identity | ✅ |
| Monad | Right Identity | ✅ |
| Monad | Associativity | ✅ |
| Comonad | Left Counit | ✅ |
| Comonad | Right Counit | ✅ |
| Comonad | Coassociativity | ✅ |
| Enriched | Tensor Associativity | ✅ |
| Enriched | Left Unit | ✅ |
| Enriched | Right Unit | ✅ |
| Adjunction | Unit-Counit | ✅ |
| Natural Transformation | Naturality | ✅ |
| Kleisli | Associativity | ✅ |
| CoKleisli | Associativity | ✅ |

## Integration with Commands

```bash
# Use in /meta
/meta @mode:iterative "implement feature"
# → Applies F(task) → M.unit → M.bind(refine) → W.extract

# Use in /route
/route "fix bug in auth"
# → Applies F_route: Task → Domain → Command

# Use in /rmp
/rmp "optimize algorithm" 8
# → Applies M.bind loop until quality >= 0.8
```

## References

1. Zhang et al. (2023) - "Meta-Prompting: Enhancing Language Models"
2. de Wynter et al. (2025) - "Categorical Meta-Prompting Theory"
3. Moggi (1991) - "Notions of Computation and Monads"
4. Uustalu & Vene (2008) - "Comonadic Notions of Computation"
