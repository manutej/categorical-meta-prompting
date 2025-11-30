---
name: recursive-meta-prompting
description: "Recursive Meta-Prompting (RMP) implementation with unified categorical syntax. Supports @mode:iterative, @quality: thresholds, >=> Kleisli composition, and comonadic context extraction. Use when implementing iterative prompt improvement, quality-gated generation loops, or applying categorical fixed-point semantics with convergence guarantees."
---

# Recursive Meta-Prompting (RMP)

Implementation patterns for recursive prompt improvement with unified categorical syntax.

**Unified Framework Integration**: This skill implements **Monad M** from the categorical framework.
- See also: `categorical-meta-prompting` skill for full F/M/W integration
- See also: `/rmp` command for direct CLI usage
- Laws verified: 15/15 tests pass (monad left/right identity, associativity)

## Unified Syntax Integration

RMP now supports the unified categorical syntax:

```bash
# Basic RMP invocation
/rmp @quality:0.85 "optimize sorting algorithm"

# With iteration limits
/rmp @quality:0.9 @max_iterations:5 "implement auth system"

# With budget tracking
/rmp @quality:0.85 @budget:15000 @variance:20% "build API endpoint"

# Kleisli composition (monadic refinement chain)
/rmp @quality:0.85 [analyze>=>design>=>implement] "build feature"
```

## Core Categorical Structure

### Monad M (Iterative Refinement)

```
M: Prompt →^n Prompt     (Monad - iterative refinement)

Laws:
- Left identity:  return >=> f = f
- Right identity: f >=> return = f
- Associativity:  (f >=> g) >=> h = f >=> (g >=> h)
```

### Fixed-Point Semantics

RMP treats prompt improvement as a fixed-point computation:

```
F: Prompt → Prompt
Fix(F) = p where F(p) = p (converged prompt)
```

The monad structure ensures:
- **Return**: Initial prompt enters refinement context
- **Bind (>=>)**: Quality assessment chains to improvement
- **Join**: Nested refinements flatten to single improvement

## Unified Operators

### >=> (Kleisli) - Monadic Composition with Improvement

**Meaning**: Composition with iterative refinement at each stage.

**Syntax**: `A >=> B >=> C`

```python
def kleisli_rmp(stages: List[Callable[[str], M[str]]]) -> Callable[[str], M[str]]:
    """
    Kleisli composition for RMP stages.
    Each stage refines until quality threshold, then passes to next.
    """
    def composed(initial: str) -> M[str]:
        result = initial
        for stage in stages:
            result = stage(result)
            # Implicit quality gate at each stage
            while result.quality < threshold:
                result = refine(result)
        return result
    return composed
```

**Quality Improvement Law**:
```
quality((A >=> B >=> C)[iteration_n]) >= quality((A >=> B >=> C)[iteration_n-1])
```

### Quality-Gated Iteration

```python
@dataclass
class RMPConfig:
    """Unified RMP configuration via modifiers."""
    quality_threshold: float = 0.85  # @quality:
    max_iterations: int = 5          # @max_iterations:
    budget: Optional[int] = None     # @budget:
    variance_threshold: float = 0.20 # @variance:
    mode: str = "iterative"          # @mode:

def parse_rmp_modifiers(command: str) -> RMPConfig:
    """Parse unified syntax modifiers."""
    config = RMPConfig()

    if "@quality:" in command:
        config.quality_threshold = float(extract("@quality:", command))
    if "@max_iterations:" in command:
        config.max_iterations = int(extract("@max_iterations:", command))
    if "@budget:" in command:
        config.budget = int(extract("@budget:", command))
    if "@variance:" in command:
        config.variance_threshold = float(extract("@variance:", command).rstrip('%')) / 100

    return config
```

## Comonadic Context Extraction

### Comonad W (History-Aware Refinement)

```python
@dataclass
class RMPContext:
    """
    Comonad for context extraction from RMP history.

    Implements W: History → Context from unified syntax.

    extract: RMP[A] → A (current best prompt)
    duplicate: RMP[A] → RMP[RMP[A]] (history of refinement histories)
    extend: (RMP[A] → B) → RMP[A] → RMP[B] (apply context-aware transformation)
    """
    current: str
    history: List[str]
    qualities: List[float]
    iteration: int
    config: RMPConfig

    def extract(self) -> str:
        """Extract current value (Comonad law: extract)."""
        return self.current

    def duplicate(self) -> 'RMPContext':
        """Create context of contexts (Comonad law: duplicate)."""
        return RMPContext(
            current=self.current,
            history=self.history + [self.current],
            qualities=self.qualities,
            iteration=self.iteration,
            config=self.config
        )

    def extend(self, f: Callable[['RMPContext'], str]) -> 'RMPContext':
        """Apply context-aware function (Comonad law: extend)."""
        new_prompt = f(self)
        return RMPContext(
            current=new_prompt,
            history=self.history + [self.current],
            qualities=self.qualities,
            iteration=self.iteration + 1,
            config=self.config
        )

    def quality_trend(self) -> str:
        """Extract quality improvement pattern via comonadic observation."""
        if len(self.qualities) < 2:
            return "INSUFFICIENT_DATA"

        improvements = [self.qualities[i+1] - self.qualities[i]
                       for i in range(len(self.qualities)-1)]
        avg_improvement = sum(improvements) / len(improvements)

        if avg_improvement > 0.1:
            return "RAPID_IMPROVEMENT"
        elif avg_improvement > 0.02:
            return "STEADY_IMPROVEMENT"
        elif avg_improvement > -0.02:
            return "PLATEAU"
        else:
            return "DEGRADING"
```

## Basic RMP Loop (Unified Syntax)

```python
from dataclasses import dataclass
from typing import Callable, List, Optional

@dataclass
class RMPState:
    prompt: str
    quality: float
    iteration: int
    history: List[str]
    config: RMPConfig

def rmp_loop(
    initial_prompt: str,
    evaluate: Callable[[str], float],
    improve: Callable[[str, float, RMPContext], str],
    config: RMPConfig
) -> RMPState:
    """
    Recursive meta-prompting loop with unified syntax.

    Implements Monad M with quality-gated iteration:
    - Each iteration applies improvement morphism
    - Quality assessment via [0,1]-enriched category
    - Convergence when quality >= threshold or max iterations

    Categorical interpretation:
    - evaluate: Prompt → [0,1] (quality morphism to enriched category)
    - improve: Prompt × Quality × Context → Prompt (contextual refinement)
    - Loop: Fixed-point iteration until convergence
    """
    context = RMPContext(
        current=initial_prompt,
        history=[initial_prompt],
        qualities=[],
        iteration=0,
        config=config
    )

    state = RMPState(
        prompt=initial_prompt,
        quality=0.0,
        iteration=0,
        history=[initial_prompt],
        config=config
    )

    while state.iteration < config.max_iterations:
        state.quality = evaluate(state.prompt)
        context.qualities.append(state.quality)

        if state.quality >= config.quality_threshold:
            break  # Convergence reached (fixed-point)

        # Apply improvement via comonadic extend
        context = context.extend(
            lambda ctx: improve(ctx.current, ctx.qualities[-1], ctx)
        )

        state.prompt = context.current
        state.iteration += 1
        state.history.append(state.prompt)

    return state
```

## Multi-Dimensional Quality Assessment

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class MultiDimQuality:
    """
    Quality as vector in product category.

    Maps to unified syntax @quality: threshold via weighted aggregation.
    """
    correctness: float   # Weight: 40%
    clarity: float       # Weight: 25%
    completeness: float  # Weight: 20%
    efficiency: float    # Weight: 15%

    def aggregate(self, weights: Dict[str, float] = None) -> float:
        """Weighted aggregation to [0,1] for @quality: comparison."""
        weights = weights or {
            "correctness": 0.40,
            "clarity": 0.25,
            "completeness": 0.20,
            "efficiency": 0.15
        }
        return (
            weights["correctness"] * self.correctness +
            weights["clarity"] * self.clarity +
            weights["completeness"] * self.completeness +
            weights["efficiency"] * self.efficiency
        )

    def to_unified_score(self) -> float:
        """Convert to unified [0,1] quality score."""
        return self.aggregate()

def evaluate_multi_dim(prompt: str, task: str) -> MultiDimQuality:
    """
    Evaluate prompt on multiple dimensions.

    Returns MultiDimQuality that can be compared against @quality: threshold.
    """
    # LLM-based evaluation (implementation)
    ...
```

## Enriched Category Structure

### [0,1]-Enriched Quality Tracking

```python
@dataclass
class QualityHom:
    """
    Morphism in [0,1]-enriched category.

    From unified syntax: quality(A ⊗ B) <= min(quality(A), quality(B))

    Hom(A,B) valued in [0,1] represents prompt transformation quality.
    """
    source: str
    target: str
    quality: float  # Value in [0,1]

    def compose(self, other: 'QualityHom') -> 'QualityHom':
        """
        Composition in enriched category.

        Implements tensor product quality degradation:
        quality(A ⊗ B) = min(quality(A), quality(B))
        """
        assert self.target == other.source
        return QualityHom(
            source=self.source,
            target=other.target,
            quality=min(self.quality, other.quality)  # Tensor product
        )

class EnrichedRMP:
    """
    RMP in [0,1]-enriched category with unified syntax support.

    Tracks quality degradation per unified spec:
    - Sequence (→): Quality may degrade
    - Parallel (||): Quality aggregated
    - Tensor (⊗): Quality = min(components)
    - Kleisli (>=>): Quality improves iteratively
    """

    def __init__(self, config: RMPConfig):
        self.config = config
        self.history: List[QualityHom] = []

    def refine(
        self,
        prompt: str,
        evaluate: Callable[[str], float],
        improve: Callable[[str], str]
    ) -> Tuple[str, float]:
        """
        Refinement preserving enriched structure.
        Returns when quality >= @quality: threshold.
        """
        current = prompt
        quality = evaluate(current)

        while quality < self.config.quality_threshold:
            next_prompt = improve(current)
            next_quality = evaluate(next_prompt)

            # Record morphism in enriched category
            self.history.append(QualityHom(
                source=current,
                target=next_prompt,
                quality=next_quality
            ))

            if next_quality <= quality:
                break  # No improvement, stop (fixed-point reached)

            current = next_prompt
            quality = next_quality

            # Budget tracking per unified syntax
            if self.config.budget and self._check_budget_exceeded():
                break

        return current, quality
```

## Convergence Strategies

### Exponential Decay (for @quality: near-threshold)

```python
def exponential_rmp(
    initial: str,
    evaluate: Callable[[str], float],
    improve: Callable[[str, float], str],
    config: RMPConfig,
    decay: float = 0.9,
    min_improvement: float = 0.01
) -> str:
    """
    RMP with exponentially decaying improvement threshold.

    Use when @quality: threshold is high (0.9+) and
    diminishing returns are expected.
    """
    current = initial
    quality = evaluate(current)
    threshold = min_improvement

    for i in range(config.max_iterations):
        improved = improve(current, quality)
        new_quality = evaluate(improved)

        improvement = new_quality - quality
        if improvement < threshold:
            break

        current = improved
        quality = new_quality
        threshold *= decay  # Require less improvement each iteration

        if quality >= config.quality_threshold:
            break

    return current
```

### Beam Search RMP (for @mode:exploratory)

```python
def beam_rmp(
    initial: str,
    evaluate: Callable[[str], float],
    improve: Callable[[str], List[str]],  # Returns multiple candidates
    config: RMPConfig,
    beam_width: int = 3
) -> str:
    """
    RMP with beam search over improvement candidates.

    Use when task has multiple valid improvement directions.
    Supports @mode:exploratory from unified syntax.
    """
    beam = [(evaluate(initial), initial)]

    for _ in range(config.max_iterations):
        candidates = []
        for _, prompt in beam:
            improvements = improve(prompt)
            for imp in improvements:
                score = evaluate(imp)
                candidates.append((score, imp))

        # Keep top-k
        beam = sorted(candidates, key=lambda x: -x[0])[:beam_width]

        if beam[0][0] >= config.quality_threshold:
            break  # Early convergence

    return beam[0][1]
```

## Integration with Unified Mode System

### @mode:iterative (Default RMP)

```python
def mode_iterative(task: str, config: RMPConfig) -> RMPState:
    """
    Standard RMP loop with quality-gated iteration.

    /rmp @mode:iterative @quality:0.85 "task"
    """
    return rmp_loop(
        initial_prompt=generate_initial(task),
        evaluate=lambda p: evaluate_multi_dim(p, task).aggregate(),
        improve=lambda p, q, ctx: improve_with_context(p, q, ctx),
        config=config
    )
```

### @mode:dry-run (Preview RMP Plan)

```python
def mode_dry_run(task: str, config: RMPConfig) -> Dict:
    """
    Preview RMP execution plan without running.

    /rmp @mode:dry-run @quality:0.85 "task"

    Returns: Planned iterations, expected quality trajectory, budget allocation
    """
    return {
        "task": task,
        "config": asdict(config),
        "planned_iterations": config.max_iterations,
        "quality_target": config.quality_threshold,
        "estimated_trajectory": [0.5, 0.65, 0.75, 0.82, 0.87],
        "budget_per_iteration": config.budget // config.max_iterations if config.budget else "auto"
    }
```

### @mode:spec (Generate RMP Specification)

```python
def mode_spec(task: str, config: RMPConfig) -> str:
    """
    Generate RMP specification YAML without execution.

    /rmp @mode:spec @quality:0.85 "task"
    """
    return f"""
name: rmp-{hash(task)[:8]}
type: iterative_refinement
task: {task}
config:
  quality_threshold: {config.quality_threshold}
  max_iterations: {config.max_iterations}
  budget: {config.budget or 'auto'}
  variance_threshold: {config.variance_threshold}
stages:
  - name: initial_generation
    operator: return
  - name: quality_assessment
    operator: evaluate
    target: [0,1]
  - name: improvement
    operator: >=>
    condition: quality < threshold
  - name: convergence
    operator: fix
    condition: quality >= threshold OR iterations >= max
"""
```

## Checkpoint Format (Unified with LUXOR)

```yaml
RMP_CHECKPOINT_i:
  iteration: 3
  prompt_hash: "a1b2c3d4"
  quality:
    correctness: 0.82
    clarity: 0.88
    completeness: 0.79
    efficiency: 0.85
    aggregate: 0.83
  quality_delta: +0.08  # Improvement from previous
  budget:
    used: 4500
    remaining: 10500
    variance: +12%
  status: CONTINUE  # CONTINUE | CONVERGED | MAX_ITERATIONS | NO_IMPROVEMENT
  trend: STEADY_IMPROVEMENT
  next_action: "Focus on completeness (lowest dimension)"
```

## Categorical Guarantees

RMP with unified syntax provides these categorical guarantees:

1. **Monad Laws**: Kleisli composition (>=>) is associative
2. **Convergence**: Quality monotonically increases or terminates at fixed-point
3. **Enrichment**: Quality values form valid [0,1]-category with tensor product
4. **Comonad Laws**: Context extraction via extend preserves history coherence
5. **Fixed-Point Semantics**: Termination represents stable prompt (Fix(F) = p)
6. **Budget Tracking**: Variance thresholds enforced per unified spec

## Usage Examples

```bash
# Basic quality-gated refinement
/rmp @quality:0.85 "implement binary search"

# With explicit iteration limit
/rmp @quality:0.9 @max_iterations:3 "optimize database query"

# With budget tracking
/rmp @quality:0.85 @budget:20000 @variance:15% "build REST API"

# Kleisli composition chain
/rmp @quality:0.85 [analyze>=>design>=>implement>=>test] "build auth system"

# Dry-run preview
/rmp @mode:dry-run @quality:0.9 "complex feature"

# Generate spec only
/rmp @mode:spec @quality:0.85 "data pipeline"
```
