"""
Prompt Queue: Free Applicative for Deferred Prompt Sequencing

Categorical Structure:
    Free[F, A] - Free monad/applicative over functor F

The PromptQueue builds an abstract syntax tree (AST) of prompt operations
that can be:
1. Introspected before execution
2. Optimized (batching, parallelization)
3. Interpreted with different strategies
4. Composed with other queues

Operations:
    - Literal(text): Embed literal prompt text
    - Lookup(name): Dynamic lookup from registry
    - Apply(fn): Apply transformation to result
    - Conditional(pred, then, else): Branching

Example:
    queue = (PromptQueue.empty()
        .then(Literal("Analyze the problem:"))
        .then(Lookup("fibonacci"))        # Resolved at runtime
        .then(Apply(validate_result))
        .branch(
            lambda ctx: ctx.get("needs_detail"),
            then=Lookup("detailed_explanation"),
            else_=Literal("Done.")
        ))

    # Interpret against registry
    result = queue.interpret(registry, executor)
"""

from dataclasses import dataclass, field
from typing import (
    TypeVar, Generic, Callable, List, Optional,
    Union, Any, Dict, Protocol
)
from abc import ABC, abstractmethod
from enum import Enum, auto

A = TypeVar('A')
B = TypeVar('B')


class StepType(Enum):
    """Types of queue steps."""
    LITERAL = auto()
    LOOKUP = auto()
    APPLY = auto()
    CONDITIONAL = auto()
    PARALLEL = auto()
    SEQUENCE = auto()


@dataclass
class QueueStep(ABC):
    """
    Abstract base for queue steps.

    Each step is a node in the prompt queue AST.
    """
    step_type: StepType

    @abstractmethod
    def describe(self) -> str:
        """Human-readable description."""
        pass


@dataclass
class Literal(QueueStep):
    """
    Literal prompt text (pure value).

    Does not require registry lookup.
    """
    text: str
    role: str = "user"
    step_type: StepType = field(default=StepType.LITERAL, init=False)

    def describe(self) -> str:
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Literal({self.role}: {preview!r})"


@dataclass
class Lookup(QueueStep):
    """
    Dynamic prompt lookup from registry.

    Resolved at interpretation time.
    """
    name: str
    fallback: Optional[str] = None
    step_type: StepType = field(default=StepType.LOOKUP, init=False)

    def describe(self) -> str:
        fb = f", fallback={self.fallback!r}" if self.fallback else ""
        return f"Lookup({self.name!r}{fb})"


@dataclass
class Apply(QueueStep):
    """
    Apply transformation to accumulated result.

    The function receives current context and returns modified context.
    """
    name: str
    transform: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    step_type: StepType = field(default=StepType.APPLY, init=False)

    def describe(self) -> str:
        return f"Apply({self.name})"


@dataclass
class Conditional(QueueStep):
    """
    Conditional branching in the queue.

    Evaluates predicate at runtime to choose branch.
    """
    predicate: Callable[[Dict[str, Any]], bool]
    then_branch: 'PromptQueue'
    else_branch: Optional['PromptQueue'] = None
    description: str = "condition"
    step_type: StepType = field(default=StepType.CONDITIONAL, init=False)

    def describe(self) -> str:
        return f"Conditional({self.description})"


@dataclass
class Parallel(QueueStep):
    """
    Parallel execution of multiple queues.

    Results are combined.
    """
    branches: List['PromptQueue']
    combiner: Callable[[List[Any]], Any] = field(default=lambda x: x)
    step_type: StepType = field(default=StepType.PARALLEL, init=False)

    def describe(self) -> str:
        return f"Parallel({len(self.branches)} branches)"


class QueueExecutor(Protocol):
    """Protocol for queue execution strategies."""

    def execute_literal(self, step: Literal, ctx: Dict[str, Any]) -> str:
        ...

    def execute_lookup(
        self,
        step: Lookup,
        registry: 'PromptRegistry',
        ctx: Dict[str, Any]
    ) -> str:
        ...

    def execute_apply(self, step: Apply, ctx: Dict[str, Any]) -> Dict[str, Any]:
        ...


@dataclass
class PromptQueue:
    """
    Free Applicative structure for prompt sequencing.

    Builds an AST of prompt operations that can be:
    - Introspected: See all steps before execution
    - Optimized: Batch lookups, parallelize independent steps
    - Interpreted: Execute with different strategies/registries

    Categorical Properties:
    - Functor: map transforms final result
    - Applicative: combine independent queues
    - Monad: sequence dependent queues (via bind)
    """

    steps: List[QueueStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def empty(cls) -> 'PromptQueue':
        """Create empty queue (identity for composition)."""
        return cls(steps=[])

    @classmethod
    def from_literal(cls, text: str, role: str = "user") -> 'PromptQueue':
        """Create queue with single literal step."""
        return cls(steps=[Literal(text=text, role=role)])

    @classmethod
    def from_lookup(cls, name: str, fallback: str = None) -> 'PromptQueue':
        """Create queue with single lookup step."""
        return cls(steps=[Lookup(name=name, fallback=fallback)])

    def then(self, step: Union[QueueStep, 'PromptQueue', str]) -> 'PromptQueue':
        """
        Append step to queue (monadic bind).

        Accepts:
        - QueueStep: Add directly
        - PromptQueue: Concatenate steps
        - str: Convert to Literal
        """
        new_steps = list(self.steps)

        if isinstance(step, str):
            new_steps.append(Literal(text=step))
        elif isinstance(step, PromptQueue):
            new_steps.extend(step.steps)
        else:
            new_steps.append(step)

        return PromptQueue(steps=new_steps, metadata=self.metadata)

    def lookup(self, name: str, fallback: str = None) -> 'PromptQueue':
        """Add lookup step."""
        return self.then(Lookup(name=name, fallback=fallback))

    def literal(self, text: str, role: str = "user") -> 'PromptQueue':
        """Add literal step."""
        return self.then(Literal(text=text, role=role))

    def apply(
        self,
        name: str,
        transform: Callable[[Dict[str, Any]], Dict[str, Any]] = None
    ) -> 'PromptQueue':
        """Add apply step."""
        return self.then(Apply(name=name, transform=transform))

    def branch(
        self,
        predicate: Callable[[Dict[str, Any]], bool],
        then: Union['PromptQueue', QueueStep],
        else_: Union['PromptQueue', QueueStep] = None,
        description: str = "condition"
    ) -> 'PromptQueue':
        """
        Add conditional branch.

        At runtime, predicate is evaluated and appropriate branch taken.
        """
        then_queue = then if isinstance(then, PromptQueue) else PromptQueue.empty().then(then)
        else_queue = None
        if else_ is not None:
            else_queue = else_ if isinstance(else_, PromptQueue) else PromptQueue.empty().then(else_)

        return self.then(Conditional(
            predicate=predicate,
            then_branch=then_queue,
            else_branch=else_queue,
            description=description
        ))

    def parallel(
        self,
        *queues: 'PromptQueue',
        combiner: Callable[[List[Any]], Any] = None
    ) -> 'PromptQueue':
        """
        Add parallel execution of multiple queues.
        """
        return self.then(Parallel(
            branches=list(queues),
            combiner=combiner or (lambda x: x)
        ))

    # Functor operations

    def map(self, f: Callable[[str], str]) -> 'PromptQueue':
        """
        Map over final result (functor operation).

        Adds an Apply step that transforms the output.
        """
        return self.apply(
            name=f"map_{f.__name__ if hasattr(f, '__name__') else 'fn'}",
            transform=lambda ctx: {**ctx, "output": f(ctx.get("output", ""))}
        )

    # Introspection

    def describe(self) -> str:
        """Get human-readable description of queue."""
        lines = ["PromptQueue:"]
        for i, step in enumerate(self.steps):
            lines.append(f"  {i+1}. {step.describe()}")
        return "\n".join(lines)

    def get_lookups(self) -> List[str]:
        """Get all lookup names (for batching/preloading)."""
        names = []
        for step in self.steps:
            if isinstance(step, Lookup):
                names.append(step.name)
            elif isinstance(step, Conditional):
                names.extend(step.then_branch.get_lookups())
                if step.else_branch:
                    names.extend(step.else_branch.get_lookups())
            elif isinstance(step, Parallel):
                for branch in step.branches:
                    names.extend(branch.get_lookups())
        return names

    def get_literals(self) -> List[str]:
        """Get all literal texts."""
        texts = []
        for step in self.steps:
            if isinstance(step, Literal):
                texts.append(step.text)
        return texts

    # Interpretation

    def interpret(
        self,
        registry: 'PromptRegistry',
        context: Dict[str, Any] = None,
        executor: QueueExecutor = None
    ) -> Dict[str, Any]:
        """
        Interpret queue against a registry.

        Args:
            registry: Prompt registry for lookups
            context: Initial context dict
            executor: Custom executor (uses default if None)

        Returns:
            Context dict with accumulated results
        """
        ctx = context or {}
        ctx.setdefault("prompts", [])
        ctx.setdefault("output", "")

        for step in self.steps:
            ctx = self._interpret_step(step, registry, ctx, executor)

        return ctx

    def _interpret_step(
        self,
        step: QueueStep,
        registry: 'PromptRegistry',
        ctx: Dict[str, Any],
        executor: QueueExecutor = None
    ) -> Dict[str, Any]:
        """Interpret a single step."""

        if isinstance(step, Literal):
            ctx["prompts"].append({"role": step.role, "content": step.text})
            ctx["output"] += step.text + "\n"

        elif isinstance(step, Lookup):
            prompt = registry.get(step.name)
            if prompt:
                # Render with current context
                rendered = prompt.render(ctx)
                ctx["prompts"].append({"role": "user", "content": rendered})
                ctx["output"] += rendered + "\n"
                ctx[f"resolved_{step.name}"] = rendered
            elif step.fallback:
                ctx["prompts"].append({"role": "user", "content": step.fallback})
                ctx["output"] += step.fallback + "\n"
            else:
                ctx["errors"] = ctx.get("errors", []) + [f"Missing: {step.name}"]

        elif isinstance(step, Apply):
            if step.transform:
                ctx = step.transform(ctx)

        elif isinstance(step, Conditional):
            if step.predicate(ctx):
                ctx = step.then_branch.interpret(registry, ctx, executor)
            elif step.else_branch:
                ctx = step.else_branch.interpret(registry, ctx, executor)

        elif isinstance(step, Parallel):
            # Execute branches (could be parallelized)
            results = [
                branch.interpret(registry, dict(ctx), executor)
                for branch in step.branches
            ]
            ctx["parallel_results"] = step.combiner(results)

        return ctx

    # Composition

    def __add__(self, other: 'PromptQueue') -> 'PromptQueue':
        """Concatenate queues."""
        return PromptQueue(
            steps=self.steps + other.steps,
            metadata={**self.metadata, **other.metadata}
        )

    def __rshift__(self, step: Union[QueueStep, 'PromptQueue', str]) -> 'PromptQueue':
        """Operator >> for then."""
        return self.then(step)

    def __len__(self) -> int:
        return len(self.steps)

    def __iter__(self):
        return iter(self.steps)


# Convenience constructors

def literal(text: str, role: str = "user") -> PromptQueue:
    """Create queue with literal step."""
    return PromptQueue.from_literal(text, role)


def lookup(name: str, fallback: str = None) -> PromptQueue:
    """Create queue with lookup step."""
    return PromptQueue.from_lookup(name, fallback)


def sequence(*steps: Union[QueueStep, PromptQueue, str]) -> PromptQueue:
    """Create queue from sequence of steps."""
    queue = PromptQueue.empty()
    for step in steps:
        queue = queue.then(step)
    return queue
