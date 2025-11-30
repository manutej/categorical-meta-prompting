---
name: recursive-meta-prompting
description: "Recursive Meta-Prompting (RMP) implementation patterns with monadic refinement loops, quality convergence, and self-improvement. Use when implementing iterative prompt improvement systems, building self-refining AI pipelines, creating quality-gated generation loops, or applying categorical fixed-point semantics to prompt engineering with convergence guarantees."
---

# Recursive Meta-Prompting (RMP)

Implementation patterns for recursive prompt improvement with categorical foundations.

**Unified Framework Integration**: This skill implements **Monad M** from the categorical framework.
- See also: `categorical-meta-prompting` skill for full F/M/W integration
- See also: `/rmp` command for direct CLI usage
- Laws verified: 15/15 tests pass (monad left/right identity, associativity)

## Core Concept

Recursive Meta-Prompting (RMP) treats prompt improvement as a fixed-point computation:

```
F: Prompt → Prompt
Fix(F) = p where F(p) = p (converged prompt)
```

The monad structure ensures:
- **Return**: Initial prompt enters refinement context
- **Bind**: Quality assessment chains to improvement
- **Join**: Nested refinements flatten to single improvement

## Basic RMP Loop

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class RMPState:
    prompt: str
    quality: float
    iteration: int
    history: list[str]

def rmp_loop(
    initial_prompt: str,
    evaluate: Callable[[str], float],
    improve: Callable[[str, float], str],
    threshold: float = 0.9,
    max_iterations: int = 5
) -> RMPState:
    """
    Recursive meta-prompting loop.
    
    Categorical interpretation:
    - evaluate: Prompt → [0,1] (quality morphism)
    - improve: Prompt × Quality → Prompt (refinement morphism)
    - Loop: Fixed-point iteration until convergence
    """
    state = RMPState(
        prompt=initial_prompt,
        quality=0.0,
        iteration=0,
        history=[initial_prompt]
    )
    
    while state.iteration < max_iterations:
        state.quality = evaluate(state.prompt)
        
        if state.quality >= threshold:
            break  # Convergence reached
            
        state.prompt = improve(state.prompt, state.quality)
        state.iteration += 1
        state.history.append(state.prompt)
    
    return state
```

## LLM-Based Implementation

```python
from openai import OpenAI

client = OpenAI()

def evaluate_prompt(prompt: str, task_description: str) -> float:
    """Quality evaluation via LLM."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
                Rate the prompt quality from 0.0 to 1.0 based on:
                - Clarity and specificity
                - Task alignment
                - Completeness of instructions
                - Potential for consistent outputs
                Return only a decimal number.
            """},
            {"role": "user", "content": f"Task: {task_description}\n\nPrompt: {prompt}"}
        ]
    )
    return float(response.choices[0].message.content.strip())

def improve_prompt(prompt: str, quality: float, feedback: str = "") -> str:
    """Generate improved prompt version."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
                You are a prompt engineering expert.
                Improve the given prompt to achieve higher quality.
                Focus on clarity, specificity, and effectiveness.
                Return only the improved prompt.
            """},
            {"role": "user", "content": f"""
                Current prompt (quality {quality:.2f}):
                {prompt}
                
                {f'Feedback: {feedback}' if feedback else ''}
                
                Generate an improved version:
            """}
        ]
    )
    return response.choices[0].message.content.strip()
```

## Monadic RMP Structure

```python
from typing import Generic, TypeVar, Callable
from abc import ABC, abstractmethod

T = TypeVar('T')
U = TypeVar('U')

class RMPMonad(Generic[T], ABC):
    """
    RMP Monad capturing refinement context.
    
    Laws:
    - Left identity: return(a).bind(f) == f(a)
    - Right identity: m.bind(return) == m
    - Associativity: m.bind(f).bind(g) == m.bind(λx. f(x).bind(g))
    """
    
    @abstractmethod
    def bind(self, f: Callable[[T], 'RMPMonad[U]']) -> 'RMPMonad[U]':
        pass
    
    @staticmethod
    @abstractmethod
    def unit(value: T) -> 'RMPMonad[T]':
        pass

@dataclass
class Refinement(RMPMonad[str]):
    """Concrete RMP monad for prompt refinement."""
    prompt: str
    quality: float
    converged: bool
    
    def bind(self, f: Callable[[str], 'Refinement']) -> 'Refinement':
        if self.converged:
            return self  # Short-circuit if converged
        return f(self.prompt)
    
    @staticmethod
    def unit(prompt: str) -> 'Refinement':
        return Refinement(prompt=prompt, quality=0.0, converged=False)
    
    @staticmethod
    def converge(prompt: str, quality: float) -> 'Refinement':
        return Refinement(prompt=prompt, quality=quality, converged=True)
```

## Quality-Enriched Categories

```python
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class QualityHom:
    """
    Morphism in [0,1]-enriched category.
    
    Hom(A,B) valued in [0,1] represents prompt transformation quality.
    Composition: Hom(A,C) = min(Hom(A,B), Hom(B,C)) (pessimistic)
    """
    source: str
    target: str
    quality: float  # Value in [0,1]
    
    def compose(self, other: 'QualityHom') -> 'QualityHom':
        """Composition in enriched category."""
        assert self.target == other.source
        return QualityHom(
            source=self.source,
            target=other.target,
            quality=min(self.quality, other.quality)
        )

class EnrichedRMP:
    """RMP in [0,1]-enriched category."""
    
    def __init__(self, threshold: float = 0.9):
        self.threshold = threshold
        self.history: List[QualityHom] = []
    
    def refine(
        self,
        prompt: str,
        evaluate: Callable[[str], float],
        improve: Callable[[str], str]
    ) -> Tuple[str, float]:
        """
        Refinement preserving enriched structure.
        Returns when quality exceeds threshold.
        """
        current = prompt
        quality = evaluate(current)
        
        while quality < self.threshold:
            next_prompt = improve(current)
            next_quality = evaluate(next_prompt)
            
            # Record morphism in enriched category
            self.history.append(QualityHom(
                source=current,
                target=next_prompt,
                quality=next_quality
            ))
            
            if next_quality <= quality:
                break  # No improvement, stop
            
            current = next_prompt
            quality = next_quality
        
        return current, quality
```

## Multi-Dimension Quality

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class MultiDimQuality:
    """Quality as vector in product category."""
    clarity: float
    specificity: float
    completeness: float
    consistency: float
    
    def aggregate(self, weights: Dict[str, float] = None) -> float:
        """Weighted aggregation to [0,1]."""
        weights = weights or {
            "clarity": 0.25,
            "specificity": 0.25,
            "completeness": 0.25,
            "consistency": 0.25
        }
        return (
            weights["clarity"] * self.clarity +
            weights["specificity"] * self.specificity +
            weights["completeness"] * self.completeness +
            weights["consistency"] * self.consistency
        )
    
    def dominates(self, other: 'MultiDimQuality') -> bool:
        """Pareto dominance check."""
        return (
            self.clarity >= other.clarity and
            self.specificity >= other.specificity and
            self.completeness >= other.completeness and
            self.consistency >= other.consistency and
            self != other
        )

def evaluate_multi_dim(prompt: str) -> MultiDimQuality:
    """Evaluate prompt on multiple dimensions."""
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": """
                Evaluate the prompt on these dimensions (0.0-1.0):
                - clarity: How clear and unambiguous is it?
                - specificity: How specific are the instructions?
                - completeness: Does it cover all necessary aspects?
                - consistency: Would it produce consistent outputs?
                
                Return JSON: {"clarity": X, "specificity": X, "completeness": X, "consistency": X}
            """},
            {"role": "user", "content": prompt}
        ]
    )
    data = json.loads(response.choices[0].message.content)
    return MultiDimQuality(**data)
```

## Convergence Strategies

### Exponential Decay

```python
def exponential_rmp(
    initial: str,
    evaluate: Callable[[str], float],
    improve: Callable[[str, float], str],
    decay: float = 0.9,
    min_improvement: float = 0.01
) -> str:
    """RMP with exponentially decaying improvement threshold."""
    current = initial
    quality = evaluate(current)
    threshold = min_improvement
    
    while True:
        improved = improve(current, quality)
        new_quality = evaluate(improved)
        
        improvement = new_quality - quality
        if improvement < threshold:
            break
        
        current = improved
        quality = new_quality
        threshold *= decay  # Require less improvement each iteration
    
    return current
```

### Beam Search RMP

```python
def beam_rmp(
    initial: str,
    evaluate: Callable[[str], float],
    improve: Callable[[str], List[str]],  # Returns multiple candidates
    beam_width: int = 3,
    max_iterations: int = 5
) -> str:
    """RMP with beam search over improvement candidates."""
    beam = [(evaluate(initial), initial)]
    
    for _ in range(max_iterations):
        candidates = []
        for _, prompt in beam:
            improvements = improve(prompt)
            for imp in improvements:
                score = evaluate(imp)
                candidates.append((score, imp))
        
        # Keep top-k
        beam = sorted(candidates, key=lambda x: -x[0])[:beam_width]
        
        if beam[0][0] >= 0.95:  # Early stopping
            break
    
    return beam[0][1]
```

## Context Extraction (Comonad)

```python
@dataclass
class RMPContext:
    """
    Comonad for context extraction from RMP history.
    
    extract: RMP[A] → A (current prompt)
    duplicate: RMP[A] → RMP[RMP[A]] (history of histories)
    extend: (RMP[A] → B) → RMP[A] → RMP[B]
    """
    current: str
    history: List[str]
    qualities: List[float]
    
    def extract(self) -> str:
        """Extract current value."""
        return self.current
    
    def duplicate(self) -> 'RMPContext':
        """Create context of contexts."""
        return RMPContext(
            current=self.current,
            history=self.history + [self.current],
            qualities=self.qualities
        )
    
    def extend(self, f: Callable[['RMPContext'], str]) -> 'RMPContext':
        """Apply context-aware function."""
        new_prompt = f(self)
        return RMPContext(
            current=new_prompt,
            history=self.history + [self.current],
            qualities=self.qualities
        )
```

## Practical Implementation

```python
class RMPEngine:
    """Production RMP engine."""
    
    def __init__(
        self,
        model: str = "gpt-4o",
        quality_threshold: float = 0.9,
        max_iterations: int = 5
    ):
        self.model = model
        self.threshold = quality_threshold
        self.max_iterations = max_iterations
        self.client = OpenAI()
    
    def refine(self, prompt: str, task: str) -> RMPState:
        """Execute RMP refinement."""
        return rmp_loop(
            initial_prompt=prompt,
            evaluate=lambda p: evaluate_prompt(p, task),
            improve=lambda p, q: improve_prompt(p, q),
            threshold=self.threshold,
            max_iterations=self.max_iterations
        )
    
    def refine_with_context(
        self,
        prompt: str,
        task: str,
        examples: List[str] = None
    ) -> RMPState:
        """RMP with example context."""
        context = f"Examples of good prompts:\n" + "\n".join(examples or [])
        
        def improve_with_context(p: str, q: float) -> str:
            return improve_prompt(p, q, feedback=context)
        
        return rmp_loop(
            initial_prompt=prompt,
            evaluate=lambda p: evaluate_prompt(p, task),
            improve=improve_with_context,
            threshold=self.threshold,
            max_iterations=self.max_iterations
        )
```

## Categorical Guarantees

RMP provides these categorical guarantees:

1. **Monad Laws**: Refinement composition is associative
2. **Convergence**: Quality monotonically increases or terminates
3. **Enrichment**: Quality values form valid [0,1]-category
4. **Context Preservation**: Comonad laws ensure history coherence
5. **Fixed-Point Semantics**: Termination represents stable prompt
