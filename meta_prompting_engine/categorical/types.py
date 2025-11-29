"""
Type definitions for categorical meta-prompting.

Defines the objects in categories T (Tasks) and P (Prompts),
along with supporting types for complexity analysis and strategies.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


# === Category T (Tasks) ===

@dataclass
class Task:
    """
    Object in category T (Tasks).

    A task represents a problem to be solved via meta-prompting.

    Attributes:
        description: Human-readable task description
        complexity: Estimated complexity [0.0, 1.0] (0 = trivial, 1 = very complex)
        metadata: Additional task metadata
        type: Task type (coding, math, writing, etc.)
        examples: Optional example inputs/outputs
        constraints: Optional constraints on solution

    Example:
        >>> task = Task(
        ...     description="Find the maximum number in [3, 1, 4, 1, 5, 9, 2, 6]",
        ...     complexity=0.25,
        ...     type="coding"
        ... )
    """
    description: str
    complexity: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    type: str = "general"
    examples: List[Dict[str, str]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"Task({self.description[:50]}...)" if len(self.description) > 50 else f"Task({self.description})"

    def __hash__(self) -> int:
        return hash((self.description, self.complexity, self.type))


# === Category P (Prompts) ===

@dataclass
class Prompt:
    """
    Object in category P (Prompts).

    A prompt represents a structured instruction to an LLM.

    Attributes:
        template: Prompt template string
        variables: Template variables to fill
        context: Execution context (complexity, strategy, etc.)
        meta_level: Recursion depth in meta-prompting (0 = initial)

    Example:
        >>> prompt = Prompt(
        ...     template="You are an expert {role}. Solve: {task}",
        ...     variables={"role": "programmer", "task": "find maximum"},
        ...     context={"complexity": 0.25, "strategy": "direct_execution"},
        ...     meta_level=0
        ... )
    """
    template: str
    variables: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    meta_level: int = 0

    def render(self) -> str:
        """Render prompt by filling template with variables."""
        return self.template.format(**self.variables)

    def __str__(self) -> str:
        template_preview = self.template[:50] + "..." if len(self.template) > 50 else self.template
        return f"Prompt(meta_level={self.meta_level}, template={template_preview})"

    def __hash__(self) -> int:
        return hash((self.template, tuple(sorted(self.variables.items())), self.meta_level))


# === Complexity Analysis ===

@dataclass
class ComplexityAnalysis:
    """
    Result of task complexity analysis.

    Attributes:
        overall: Overall complexity score [0.0, 1.0]
        dimensions: Complexity breakdown by dimension
        confidence: Confidence in analysis [0.0, 1.0]

    Example:
        >>> analysis = ComplexityAnalysis(
        ...     overall=0.75,
        ...     dimensions={"algorithmic": 0.8, "domain_knowledge": 0.7},
        ...     confidence=0.9
        ... )
    """
    overall: float
    dimensions: Dict[str, float] = field(default_factory=dict)
    confidence: float = 1.0

    def __post_init__(self):
        """Ensure complexity is in valid range [0.0, 1.0]."""
        if not 0.0 <= self.overall <= 1.0:
            raise ValueError(f"Complexity must be in [0, 1], got {self.overall}")


# === Strategy Selection ===

class StrategyType(Enum):
    """Meta-prompting strategy types based on complexity."""
    DIRECT_EXECUTION = "direct_execution"           # Complexity < 0.3
    MULTI_APPROACH = "multi_approach_synthesis"     # 0.3 <= Complexity < 0.7
    AUTONOMOUS_EVOLUTION = "autonomous_evolution"    # Complexity >= 0.7


@dataclass
class Strategy:
    """
    Meta-prompting strategy.

    Attributes:
        name: Strategy type
        template: Prompt template for this strategy
        max_iterations: Maximum meta-prompting iterations
        quality_threshold: Minimum quality threshold [0.0, 1.0]

    Example:
        >>> strategy = Strategy(
        ...     name=StrategyType.DIRECT_EXECUTION,
        ...     template="Solve directly: {description}",
        ...     max_iterations=1,
        ...     quality_threshold=0.80
        ... )
    """
    name: StrategyType
    template: str
    max_iterations: int
    quality_threshold: float

    def __str__(self) -> str:
        return f"Strategy({self.name.value}, max_iter={self.max_iterations})"


# === Quality Enrichment ===

@dataclass
class QualityScore:
    """
    Quality score in [0,1]-enriched category.

    Attributes:
        value: Quality value [0.0, 1.0] (1.0 = perfect)
        components: Quality breakdown by dimension
        timestamp: When quality was assessed

    Example:
        >>> quality = QualityScore(
        ...     value=0.92,
        ...     components={"correctness": 0.95, "clarity": 0.89}
        ... )
    """
    value: float
    components: Dict[str, float] = field(default_factory=dict)
    timestamp: Optional[float] = None

    def __post_init__(self):
        """Ensure quality is in valid range [0.0, 1.0]."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Quality must be in [0, 1], got {self.value}")

    def __float__(self) -> float:
        return self.value

    def tensor_product(self, other: 'QualityScore') -> 'QualityScore':
        """
        Compute tensor product (minimum) of two quality scores.

        In [0,1]-enriched categories, the tensor product is min:
            q1 ⊗ q2 = min(q1, q2)

        This represents quality degradation in composition.

        Args:
            other: Another quality score

        Returns:
            QualityScore with minimum value

        Example:
            >>> q1 = QualityScore(0.92)
            >>> q2 = QualityScore(0.87)
            >>> q_composed = q1.tensor_product(q2)
            >>> assert q_composed.value == 0.87
        """
        return QualityScore(
            value=min(self.value, other.value),
            components={
                **self.components,
                **other.components,
                'tensor_product': min(self.value, other.value)
            }
        )

    def __str__(self) -> str:
        return f"Quality({self.value:.2f})"
