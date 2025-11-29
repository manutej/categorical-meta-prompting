---
name: quality-enriched-prompting
description: "[0,1]-enriched category implementation for gradient-based prompt quality optimization. Use when implementing quality-aware prompt systems, building enriched categorical structures for prompt evaluation, creating continuous optimization over prompt spaces, or applying Bradley's enriched category theory to language model quality scoring."
---

# Quality-Enriched Prompting

Implementation of [0,1]-enriched categories for continuous prompt quality optimization.

## Enriched Category Foundations

In a [0,1]-enriched category (following Bradley's framework):
- **Objects**: Prompts, responses, contexts
- **Hom-objects**: Quality scores in [0,1] instead of sets
- **Composition**: Quality degradation via multiplication or minimum
- **Identity**: Perfect quality (1.0)

## Basic Enriched Structure

```python
from dataclasses import dataclass
from typing import Callable, Dict, Tuple, List
import numpy as np

@dataclass
class EnrichedHom:
    """
    Morphism in [0,1]-enriched category.
    
    Hom(A,B) ∈ [0,1] represents quality of transformation A → B.
    """
    source: str
    target: str
    quality: float  # Value in [0,1]
    
    def __post_init__(self):
        assert 0 <= self.quality <= 1, "Quality must be in [0,1]"
    
    def compose(self, other: 'EnrichedHom') -> 'EnrichedHom':
        """
        Composition in enriched category.
        
        Quality degrades: Hom(A,C) = Hom(A,B) ⊗ Hom(B,C)
        Using multiplication as monoidal product.
        """
        assert self.target == other.source, "Cannot compose non-adjacent morphisms"
        return EnrichedHom(
            source=self.source,
            target=other.target,
            quality=self.quality * other.quality
        )
    
    @staticmethod
    def identity(obj: str) -> 'EnrichedHom':
        """Identity morphism with perfect quality."""
        return EnrichedHom(source=obj, target=obj, quality=1.0)

# Alternative composition: minimum (pessimistic)
def min_compose(h1: EnrichedHom, h2: EnrichedHom) -> EnrichedHom:
    """Composition using minimum (worst-case quality)."""
    return EnrichedHom(
        source=h1.source,
        target=h2.target,
        quality=min(h1.quality, h2.quality)
    )
```

## Quality Metrics

```python
@dataclass
class QualityVector:
    """
    Multi-dimensional quality as product of enriched categories.
    
    Quality is a vector in [0,1]^n for n quality dimensions.
    """
    clarity: float
    specificity: float
    completeness: float
    coherence: float
    relevance: float
    
    def __post_init__(self):
        for field in ['clarity', 'specificity', 'completeness', 'coherence', 'relevance']:
            val = getattr(self, field)
            assert 0 <= val <= 1, f"{field} must be in [0,1]"
    
    def aggregate(self, weights: Dict[str, float] = None) -> float:
        """Weighted aggregation to scalar quality."""
        weights = weights or {
            'clarity': 0.2, 'specificity': 0.2, 'completeness': 0.2,
            'coherence': 0.2, 'relevance': 0.2
        }
        return sum(
            weights[k] * getattr(self, k)
            for k in weights
        )
    
    def pareto_dominates(self, other: 'QualityVector') -> bool:
        """Check Pareto dominance (better in all dimensions)."""
        dominated = all(
            getattr(self, f) >= getattr(other, f)
            for f in ['clarity', 'specificity', 'completeness', 'coherence', 'relevance']
        )
        strictly_better = any(
            getattr(self, f) > getattr(other, f)
            for f in ['clarity', 'specificity', 'completeness', 'coherence', 'relevance']
        )
        return dominated and strictly_better
    
    def as_array(self) -> np.ndarray:
        return np.array([
            self.clarity, self.specificity, self.completeness,
            self.coherence, self.relevance
        ])
```

## Enriched Prompt Category

```python
class EnrichedPromptCategory:
    """
    Category of prompts enriched over [0,1].
    
    Objects: Prompts
    Hom(P1, P2): Quality of transformation from P1 to P2
    """
    
    def __init__(self):
        self.objects: Dict[str, str] = {}  # id → prompt content
        self.homs: Dict[Tuple[str, str], float] = {}  # (src, tgt) → quality
    
    def add_prompt(self, id: str, content: str):
        """Add prompt as object."""
        self.objects[id] = content
    
    def add_morphism(self, source: str, target: str, quality: float):
        """Add quality-enriched morphism."""
        assert source in self.objects, f"Unknown source: {source}"
        assert target in self.objects, f"Unknown target: {target}"
        self.homs[(source, target)] = quality
    
    def compose(self, path: List[str]) -> float:
        """
        Compute composed quality along a path.
        
        Uses multiplicative composition (quality degradation).
        """
        if len(path) < 2:
            return 1.0
        
        quality = 1.0
        for i in range(len(path) - 1):
            edge_quality = self.homs.get((path[i], path[i+1]), 0.0)
            quality *= edge_quality
        
        return quality
    
    def best_path(self, source: str, target: str) -> Tuple[List[str], float]:
        """Find highest-quality path between objects."""
        from heapq import heappush, heappop
        
        # Dijkstra variant maximizing quality
        best = {source: (1.0, [source])}
        queue = [(-1.0, source)]  # Negative for max-heap behavior
        
        while queue:
            neg_quality, current = heappop(queue)
            quality = -neg_quality
            
            if current == target:
                return best[current][1], best[current][0]
            
            for (src, tgt), edge_q in self.homs.items():
                if src == current:
                    new_quality = quality * edge_q
                    if tgt not in best or new_quality > best[tgt][0]:
                        best[tgt] = (new_quality, best[current][1] + [tgt])
                        heappush(queue, (-new_quality, tgt))
        
        return [], 0.0
```

## Quality-Based Optimization

```python
class QualityOptimizer:
    """
    Gradient-based optimization in enriched category.
    
    Optimizes prompts to maximize quality morphisms.
    """
    
    def __init__(self, evaluate: Callable[[str], QualityVector]):
        self.evaluate = evaluate
        self.history: List[Tuple[str, QualityVector]] = []
    
    def optimize(
        self,
        initial_prompt: str,
        improve: Callable[[str, QualityVector], str],
        threshold: float = 0.9,
        max_iterations: int = 10
    ) -> Tuple[str, QualityVector]:
        """
        Iterative quality optimization.
        
        Follows gradient in quality space until threshold reached.
        """
        current = initial_prompt
        quality = self.evaluate(current)
        self.history.append((current, quality))
        
        for _ in range(max_iterations):
            if quality.aggregate() >= threshold:
                break
            
            # Generate improvement
            improved = improve(current, quality)
            new_quality = self.evaluate(improved)
            
            # Accept if quality improves
            if new_quality.aggregate() > quality.aggregate():
                current = improved
                quality = new_quality
                self.history.append((current, quality))
            else:
                # Try again with different parameters
                continue
        
        return current, quality
    
    def pareto_frontier(self) -> List[Tuple[str, QualityVector]]:
        """Extract Pareto-optimal prompts from history."""
        frontier = []
        for prompt, quality in self.history:
            dominated = any(
                other_q.pareto_dominates(quality)
                for _, other_q in self.history
            )
            if not dominated:
                frontier.append((prompt, quality))
        return frontier
```

## LLM-Based Quality Evaluation

```python
from openai import OpenAI

client = OpenAI()

def llm_quality_eval(prompt: str, context: str = "") -> QualityVector:
    """
    Evaluate prompt quality using LLM.
    
    Returns quality vector in [0,1]^5.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": """
                Evaluate the prompt quality on these dimensions (0.0-1.0):
                - clarity: How clear and unambiguous?
                - specificity: How specific and detailed?
                - completeness: Does it cover all aspects?
                - coherence: Is it logically structured?
                - relevance: Is it relevant to the task?
                
                Return JSON with these 5 fields.
            """},
            {"role": "user", "content": f"Context: {context}\n\nPrompt: {prompt}"}
        ]
    )
    
    import json
    data = json.loads(response.choices[0].message.content)
    return QualityVector(**data)

def llm_quality_improve(prompt: str, quality: QualityVector) -> str:
    """
    Use LLM to improve prompt based on quality assessment.
    """
    weak_dimensions = []
    if quality.clarity < 0.8: weak_dimensions.append("clarity")
    if quality.specificity < 0.8: weak_dimensions.append("specificity")
    if quality.completeness < 0.8: weak_dimensions.append("completeness")
    if quality.coherence < 0.8: weak_dimensions.append("coherence")
    if quality.relevance < 0.8: weak_dimensions.append("relevance")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""
                Improve this prompt focusing on: {', '.join(weak_dimensions)}.
                Current scores: clarity={quality.clarity:.2f}, 
                specificity={quality.specificity:.2f}, 
                completeness={quality.completeness:.2f},
                coherence={quality.coherence:.2f}, 
                relevance={quality.relevance:.2f}
                
                Return only the improved prompt.
            """},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()
```

## Enriched Functor

```python
class QualityFunctor:
    """
    Functor F: C → [0,1]-Cat preserving enriched structure.
    
    Maps objects to quality assessments and morphisms to quality degradations.
    """
    
    def __init__(self, eval_fn: Callable[[str], float]):
        self.eval_fn = eval_fn
    
    def map_object(self, prompt: str) -> float:
        """Map prompt to quality score."""
        return self.eval_fn(prompt)
    
    def map_morphism(self, transform: Callable[[str], str], source: str) -> EnrichedHom:
        """Map transformation to quality morphism."""
        source_quality = self.map_object(source)
        target = transform(source)
        target_quality = self.map_object(target)
        
        # Quality preservation ratio
        quality_ratio = target_quality / source_quality if source_quality > 0 else 0
        
        return EnrichedHom(
            source=source,
            target=target,
            quality=min(1.0, quality_ratio)
        )
```

## Categorical Guarantees

Quality-enriched prompting ensures:

1. **Enriched Composition**: Quality degradation follows monoidal laws
2. **Transitivity**: Composed quality ≤ individual qualities
3. **Reflexivity**: Identity has perfect quality (1.0)
4. **Pareto Optimality**: Frontier prompts are non-dominated
5. **Monotonic Improvement**: Optimization never decreases aggregate quality
