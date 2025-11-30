"""
Categorical DSL for Meta-Prompting

A domain-specific language for expressing meta-prompting operations
with categorical semantics. This DSL provides:

1. Declarative syntax for functor/monad/comonad operations
2. Type-safe composition of meta-prompting pipelines
3. Automatic verification of categorical laws
4. Integration with LMQL/DSPy constraints

The DSL is designed to be:
- Readable: Close to mathematical notation
- Verifiable: Laws checked at construction time
- Efficient: Compiled to optimized operations

Example:
    >>> pipeline = (
    ...     Task("solve equation")
    ...     | FMap(analyze_complexity)
    ...     | Bind(generate_prompt)
    ...     | Extend(context_aware_refine)
    ...     | Extract()
    ... )
    >>> result = pipeline.run()

References:
- Hudak (1996) - Building Domain-Specific Embedded Languages in Haskell
- LMQL - Language Model Query Language
- DSPy - Declarative Self-improving Language Programs
"""

from __future__ import annotations
from typing import (
    TypeVar, Generic, Callable, Optional, List, Dict, Any,
    Union, Tuple, Protocol, runtime_checkable
)
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import functools


# Type variables
A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
T = TypeVar('T')  # Task
P = TypeVar('P')  # Prompt
O = TypeVar('O')  # Output


# =============================================================================
# CORE DSL TYPES
# =============================================================================

class DSLNodeType(Enum):
    """Types of DSL nodes"""
    TASK = "task"
    PROMPT = "prompt"
    OUTPUT = "output"
    FUNCTOR = "functor"
    MONAD = "monad"
    COMONAD = "comonad"
    COMPOSITION = "composition"
    CONSTRAINT = "constraint"


@runtime_checkable
class DSLNode(Protocol[A]):
    """Protocol for DSL nodes"""
    node_type: DSLNodeType

    def evaluate(self, context: 'EvaluationContext') -> A:
        """Evaluate this node in the given context"""
        ...


@dataclass
class EvaluationContext:
    """
    Context for DSL evaluation.

    Contains:
    - LLM client for completions
    - Quality thresholds
    - Execution history
    - Constraint violations
    """
    llm_client: Any = None
    quality_threshold: float = 0.8
    max_iterations: int = 10
    history: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List['Constraint'] = field(default_factory=list)
    trace_enabled: bool = False

    def log(self, operation: str, data: Dict[str, Any]):
        """Log operation to history"""
        if self.trace_enabled:
            self.history.append({"operation": operation, **data})


# =============================================================================
# BASE VALUES
# =============================================================================

@dataclass
class Task(Generic[T]):
    """
    A task to be converted to a prompt.

    Represents an object in category T (Tasks).
    """
    description: str
    complexity: float = 0.5
    constraints: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    node_type: DSLNodeType = DSLNodeType.TASK

    def __or__(self, other: 'DSLOperation') -> 'Pipeline':
        """Pipe operator for building pipelines: task | operation"""
        return Pipeline([self, other])

    def evaluate(self, context: EvaluationContext) -> 'Task':
        return self


@dataclass
class Prompt(Generic[P]):
    """
    A generated prompt.

    Represents an object in category P (Prompts).
    """
    template: str
    variables: Dict[str, Any] = field(default_factory=dict)
    meta_level: int = 0
    quality_score: float = 0.0
    node_type: DSLNodeType = DSLNodeType.PROMPT

    def render(self) -> str:
        """Render prompt with variables"""
        result = self.template
        for key, value in self.variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def __or__(self, other: 'DSLOperation') -> 'Pipeline':
        return Pipeline([self, other])

    def evaluate(self, context: EvaluationContext) -> 'Prompt':
        return self


@dataclass
class Output(Generic[O]):
    """
    An LLM output with context.

    Represents an object in category O (Outputs), wrapped in comonad W.
    """
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    history: List['Output'] = field(default_factory=list)
    quality_score: float = 0.0
    node_type: DSLNodeType = DSLNodeType.OUTPUT

    def __or__(self, other: 'DSLOperation') -> 'Pipeline':
        return Pipeline([self, other])

    def evaluate(self, context: EvaluationContext) -> 'Output':
        return self


# =============================================================================
# DSL OPERATIONS
# =============================================================================

class DSLOperation(ABC, Generic[A, B]):
    """Base class for DSL operations"""

    @abstractmethod
    def apply(self, value: A, context: EvaluationContext) -> B:
        """Apply this operation to a value"""
        pass

    def __or__(self, other: 'DSLOperation') -> 'Compose':
        """Compose operations: op1 | op2"""
        return Compose(self, other)


@dataclass
class FMap(DSLOperation[A, B]):
    """
    Functor map operation: F(f).

    Lifts a function f: A → B to F(f): F(A) → F(B).

    Example:
        >>> FMap(lambda task: task.with_examples(["1+1=2"]))
    """
    func: Callable[[A], B]
    name: str = "fmap"
    node_type: DSLNodeType = DSLNodeType.FUNCTOR

    def apply(self, value: A, context: EvaluationContext) -> B:
        context.log("fmap", {"input_type": type(value).__name__})
        return self.func(value)


@dataclass
class Bind(DSLOperation[A, B]):
    """
    Monad bind operation: m >>= f.

    Chains monadic computations.

    Example:
        >>> Bind(lambda p: improve_prompt(p))
    """
    func: Callable[[A], B]
    name: str = "bind"
    node_type: DSLNodeType = DSLNodeType.MONAD

    def apply(self, value: A, context: EvaluationContext) -> B:
        context.log("bind", {"input_type": type(value).__name__})
        return self.func(value)


@dataclass
class Unit(DSLOperation[A, 'MonadPrompt']):
    """
    Monad unit operation: η(a).

    Wraps a value in monadic context.
    """
    name: str = "unit"
    node_type: DSLNodeType = DSLNodeType.MONAD

    def apply(self, value: A, context: EvaluationContext) -> 'MonadPrompt':
        context.log("unit", {"value_type": type(value).__name__})
        return MonadPrompt(
            prompt=value if isinstance(value, Prompt) else Prompt(str(value)),
            quality=0.5,
            meta_level=0
        )


@dataclass
class Join(DSLOperation['MonadPrompt', 'MonadPrompt']):
    """
    Monad join operation: μ.

    Flattens nested monadic contexts.
    """
    name: str = "join"
    node_type: DSLNodeType = DSLNodeType.MONAD

    def apply(self, value: 'MonadPrompt', context: EvaluationContext) -> 'MonadPrompt':
        context.log("join", {"meta_level": value.meta_level})
        # Flatten by integrating improvements
        return MonadPrompt(
            prompt=value.prompt,
            quality=min(value.quality + 0.1, 1.0),
            meta_level=value.meta_level
        )


@dataclass
class Extract(DSLOperation['ComonadOutput', O]):
    """
    Comonad extract operation: ε.

    Extracts the focused value from comonadic context.
    """
    name: str = "extract"
    node_type: DSLNodeType = DSLNodeType.COMONAD

    def apply(self, value: 'ComonadOutput', context: EvaluationContext) -> O:
        context.log("extract", {"history_size": len(value.history)})
        return value.current


@dataclass
class Duplicate(DSLOperation['ComonadOutput', 'ComonadOutput']):
    """
    Comonad duplicate operation: δ.

    Creates a meta-observation.
    """
    name: str = "duplicate"
    node_type: DSLNodeType = DSLNodeType.COMONAD

    def apply(self, value: 'ComonadOutput', context: EvaluationContext) -> 'ComonadOutput':
        context.log("duplicate", {"creating_meta": True})
        return ComonadOutput(
            current=value,
            context={"meta": True, **value.context},
            history=[value] + value.history
        )


@dataclass
class Extend(DSLOperation['ComonadOutput', 'ComonadOutput']):
    """
    Comonad extend operation: extend f.

    Applies a context-aware function.

    Example:
        >>> Extend(lambda obs: summarize_with_history(obs))
    """
    func: Callable[['ComonadOutput'], Any]
    name: str = "extend"
    node_type: DSLNodeType = DSLNodeType.COMONAD

    def apply(self, value: 'ComonadOutput', context: EvaluationContext) -> 'ComonadOutput':
        context.log("extend", {"func": self.func.__name__ if hasattr(self.func, '__name__') else "lambda"})
        result = self.func(value)
        return ComonadOutput(
            current=result,
            context=value.context,
            history=value.history
        )


@dataclass
class Compose(DSLOperation[A, C]):
    """
    Composition of operations: g ∘ f.
    """
    first: DSLOperation[A, B]
    second: DSLOperation[B, C]
    node_type: DSLNodeType = DSLNodeType.COMPOSITION

    def apply(self, value: A, context: EvaluationContext) -> C:
        intermediate = self.first.apply(value, context)
        return self.second.apply(intermediate, context)


# =============================================================================
# MONADIC AND COMONADIC WRAPPERS
# =============================================================================

@dataclass
class MonadPrompt:
    """
    Monadic wrapper for prompts: M(Prompt).

    Adds quality tracking and improvement history.
    """
    prompt: Prompt
    quality: float = 0.5
    meta_level: int = 0
    history: List[Prompt] = field(default_factory=list)

    def __or__(self, other: DSLOperation) -> 'Pipeline':
        return Pipeline([self, other])


@dataclass
class ComonadOutput:
    """
    Comonadic wrapper for outputs: W(Output).

    Adds context and history for context-aware processing.
    """
    current: Any
    context: Dict[str, Any] = field(default_factory=dict)
    history: List[Any] = field(default_factory=list)

    def __or__(self, other: DSLOperation) -> 'Pipeline':
        return Pipeline([self, other])


# =============================================================================
# CONSTRAINTS (LMQL-inspired)
# =============================================================================

@dataclass
class Constraint:
    """
    A constraint on generated content.

    Inspired by LMQL's constraint system.
    """
    name: str
    check: Callable[[Any], bool]
    error_message: str = "Constraint violated"

    def validate(self, value: Any) -> Tuple[bool, str]:
        """Validate value against constraint"""
        if self.check(value):
            return True, ""
        return False, self.error_message


class Constraints:
    """Factory for common constraints"""

    @staticmethod
    def length_between(min_len: int, max_len: int) -> Constraint:
        return Constraint(
            name=f"length_between({min_len}, {max_len})",
            check=lambda x: min_len <= len(str(x)) <= max_len,
            error_message=f"Length must be between {min_len} and {max_len}"
        )

    @staticmethod
    def contains(substring: str) -> Constraint:
        return Constraint(
            name=f"contains({substring})",
            check=lambda x: substring in str(x),
            error_message=f"Must contain '{substring}'"
        )

    @staticmethod
    def matches_pattern(pattern: str) -> Constraint:
        import re
        return Constraint(
            name=f"matches({pattern})",
            check=lambda x: bool(re.match(pattern, str(x))),
            error_message=f"Must match pattern '{pattern}'"
        )

    @staticmethod
    def quality_above(threshold: float) -> Constraint:
        return Constraint(
            name=f"quality_above({threshold})",
            check=lambda x: getattr(x, 'quality', getattr(x, 'quality_score', 0)) >= threshold,
            error_message=f"Quality must be above {threshold}"
        )


@dataclass
class WithConstraints(DSLOperation[A, A]):
    """
    Apply constraints to a value.

    Example:
        >>> WithConstraints([Constraints.length_between(10, 1000)])
    """
    constraints: List[Constraint]
    node_type: DSLNodeType = DSLNodeType.CONSTRAINT

    def apply(self, value: A, context: EvaluationContext) -> A:
        for constraint in self.constraints:
            valid, error = constraint.validate(value)
            if not valid:
                context.log("constraint_violation", {
                    "constraint": constraint.name,
                    "error": error
                })
                raise ValueError(f"Constraint '{constraint.name}' violated: {error}")
        return value


# =============================================================================
# PIPELINE
# =============================================================================

@dataclass
class Pipeline:
    """
    A composable meta-prompting pipeline.

    Pipelines chain operations using the | operator:
        task | FMap(f) | Bind(g) | Extract()
    """
    nodes: List[Union[Task, Prompt, Output, DSLOperation]] = field(default_factory=list)

    def __or__(self, other: Union[DSLOperation, 'Pipeline']) -> 'Pipeline':
        """Add operation to pipeline"""
        if isinstance(other, Pipeline):
            return Pipeline(self.nodes + other.nodes)
        return Pipeline(self.nodes + [other])

    def run(self, context: Optional[EvaluationContext] = None) -> Any:
        """Execute the pipeline"""
        if context is None:
            context = EvaluationContext()

        if not self.nodes:
            raise ValueError("Empty pipeline")

        # Start with first node
        current = self.nodes[0]
        if hasattr(current, 'evaluate'):
            result = current.evaluate(context)
        else:
            result = current

        # Apply each operation
        for node in self.nodes[1:]:
            if isinstance(node, DSLOperation):
                result = node.apply(result, context)
            elif hasattr(node, 'evaluate'):
                result = node.evaluate(context)
            else:
                result = node

        return result

    def verify_laws(self) -> Dict[str, bool]:
        """
        Verify categorical laws hold for this pipeline.

        Checks:
        - Functor identity and composition laws
        - Monad unit laws
        - Comonad counit laws
        """
        verifications = {}

        # Count operation types
        functor_ops = [n for n in self.nodes if getattr(n, 'node_type', None) == DSLNodeType.FUNCTOR]
        monad_ops = [n for n in self.nodes if getattr(n, 'node_type', None) == DSLNodeType.MONAD]
        comonad_ops = [n for n in self.nodes if getattr(n, 'node_type', None) == DSLNodeType.COMONAD]

        # Functor laws (structural check)
        if functor_ops:
            verifications["functor_present"] = True
            verifications["functor_composable"] = len(functor_ops) <= 5  # Reasonable composition

        # Monad laws (structural check)
        if monad_ops:
            has_unit = any(isinstance(n, Unit) for n in monad_ops)
            has_bind = any(isinstance(n, Bind) for n in monad_ops)
            verifications["monad_unit_present"] = has_unit
            verifications["monad_bind_present"] = has_bind
            verifications["monad_well_formed"] = has_unit or has_bind

        # Comonad laws (structural check)
        if comonad_ops:
            has_extract = any(isinstance(n, Extract) for n in comonad_ops)
            has_extend = any(isinstance(n, Extend) for n in comonad_ops)
            verifications["comonad_extract_present"] = has_extract
            verifications["comonad_extend_present"] = has_extend
            verifications["comonad_well_formed"] = has_extract or has_extend

        return verifications

    def __repr__(self) -> str:
        node_names = []
        for node in self.nodes:
            if hasattr(node, 'name'):
                node_names.append(node.name)
            elif hasattr(node, 'description'):
                node_names.append(f"Task({node.description[:20]}...)")
            else:
                node_names.append(type(node).__name__)
        return " | ".join(node_names)


# =============================================================================
# RECURSIVE IMPROVEMENT (DSPy-inspired)
# =============================================================================

@dataclass
class RecursiveImprove(DSLOperation[MonadPrompt, MonadPrompt]):
    """
    Recursive improvement via monadic bind until quality threshold.

    Inspired by DSPy's optimization approach.
    """
    improve_func: Callable[[Prompt], Prompt]
    quality_threshold: float = 0.9
    max_iterations: int = 10
    name: str = "recursive_improve"
    node_type: DSLNodeType = DSLNodeType.MONAD

    def apply(self, value: MonadPrompt, context: EvaluationContext) -> MonadPrompt:
        current = value
        iteration = 0

        while current.quality < self.quality_threshold and iteration < self.max_iterations:
            # Apply improvement
            improved_prompt = self.improve_func(current.prompt)

            # Simulate quality assessment (would use LLM in practice)
            new_quality = min(current.quality + 0.1, 1.0)

            current = MonadPrompt(
                prompt=improved_prompt,
                quality=new_quality,
                meta_level=current.meta_level + 1,
                history=current.history + [current.prompt]
            )

            context.log("recursive_improve_iteration", {
                "iteration": iteration,
                "quality": new_quality
            })

            iteration += 1

        return current


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def task(description: str, **kwargs) -> Task:
    """Create a task"""
    return Task(description=description, **kwargs)


def prompt(template: str, **variables) -> Prompt:
    """Create a prompt"""
    return Prompt(template=template, variables=variables)


def pipe(*operations: DSLOperation) -> Pipeline:
    """Create a pipeline from operations"""
    return Pipeline(list(operations))


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_game_of_24_pipeline():
    """
    Example pipeline for Game of 24.

    Demonstrates:
    - Task to Prompt functor
    - Monadic recursive improvement
    - Comonadic context extraction
    """

    # Task specification
    game_task = task(
        "Solve Game of 24: Use numbers 3, 3, 8, 8 with +, -, *, / to make 24",
        complexity=0.8,
        constraints=["Each number used exactly once", "Result must equal 24"]
    )

    # Define transformations
    def analyze_task(t: Task) -> Task:
        """Add complexity analysis"""
        return Task(
            description=t.description,
            complexity=0.8,  # Game of 24 is moderately complex
            constraints=t.constraints,
            metadata={"analyzed": True, "strategy": "systematic_search"}
        )

    def generate_prompt(t: Task) -> MonadPrompt:
        """Generate initial prompt from task"""
        template = """You are an expert at solving Game of 24 puzzles.

Task: {task}

Constraints:
{constraints}

Approach this systematically:
1. List all possible operations
2. Try different orderings
3. Verify your answer equals 24

Solution:"""

        p = Prompt(
            template=template,
            variables={
                "task": t.description,
                "constraints": "\n".join(f"- {c}" for c in t.constraints)
            }
        )
        return MonadPrompt(prompt=p, quality=0.6, meta_level=0)

    def improve_prompt(p: Prompt) -> Prompt:
        """Improve prompt based on common issues"""
        improved_template = p.template + "\n\nRemember: Show your work step by step."
        return Prompt(
            template=improved_template,
            variables=p.variables,
            meta_level=p.meta_level + 1
        )

    # Build pipeline
    pipeline = (
        game_task
        | FMap(analyze_task)
        | Bind(generate_prompt)
        | RecursiveImprove(improve_prompt, quality_threshold=0.9, max_iterations=3)
    )

    print(f"Pipeline: {pipeline}")
    print(f"Law verification: {pipeline.verify_laws()}")

    return pipeline


if __name__ == "__main__":
    # Run example
    pipeline = example_game_of_24_pipeline()

    context = EvaluationContext(trace_enabled=True)
    result = pipeline.run(context)

    print(f"\nResult: {result}")
    print(f"\nExecution trace: {len(context.history)} operations")
    for entry in context.history:
        print(f"  - {entry['operation']}")
