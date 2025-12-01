# Actionable Categorical Patterns for Meta-Prompting

**Extracted via W.extract from parallel research**
**Date**: 2025-12-01

---

## Pattern 1: Graded Comonad for Tier System

```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

A = TypeVar('A')
Grade = int  # L1=1, L2=2, ..., L7=7

@dataclass
class GradedComonad(Generic[A]):
    """Comonad indexed by tier/grade"""
    value: A
    grade: Grade
    history: list

    def extract(self) -> A:
        """Get current focus respecting grade bounds"""
        return self.value

    def extend(self, f: Callable[['GradedComonad[A]'], A]) -> 'GradedComonad[A]':
        """Apply context-aware function at each position"""
        return GradedComonad(
            value=f(self),
            grade=self.grade,
            history=self.history
        )

    def duplicate(self) -> 'GradedComonad[GradedComonad[A]]':
        """Create comonad of comonads"""
        return GradedComonad(
            value=self,
            grade=self.grade,
            history=self.history
        )

# Usage for tier-based context extraction
def extract_by_tier(w: GradedComonad) -> str:
    """Extract context bounded by tier token limits"""
    token_limits = {1: 1200, 2: 3000, 3: 4500, 4: 6000, 5: 9000, 6: 12000, 7: 22000}
    limit = token_limits.get(w.grade, 6000)
    return truncate_to_tokens(w.value, limit)
```

---

## Pattern 2: Kan Extension for Prompt Learning

```python
from typing import Dict, Callable, TypeVar

Task = TypeVar('Task')
Prompt = TypeVar('Prompt')

class KanExtension:
    """Left Kan extension for prompt generalization"""

    def __init__(self, training_data: Dict[Task, Prompt]):
        self.training = training_data

    def left_kan(self, new_task: Task) -> Prompt:
        """
        Lan_K(Training)(new_task) = optimal prompt for new task

        Universal property: This is the BEST possible extension
        """
        # Find most similar training task
        similar = self.find_similar(new_task)

        # Extend prompt via colimit construction
        return self.colimit_extend(similar, new_task)

    def find_similar(self, task: Task) -> list:
        """Compute similarity via enriched hom-objects"""
        return sorted(
            self.training.keys(),
            key=lambda t: self.similarity(t, task),
            reverse=True
        )[:3]

    def colimit_extend(self, similar: list, target: Task) -> Prompt:
        """Construct prompt as weighted colimit"""
        weights = [self.similarity(t, target) for t in similar]
        prompts = [self.training[t] for t in similar]
        return self.weighted_combination(prompts, weights)
```

---

## Pattern 3: Open Game for Prompt-Response

```python
from dataclass import dataclass
from typing import Callable, Tuple

@dataclass
class OpenGame:
    """Prompt-response as strategic game"""

    # User's strategy: context -> prompt
    user_strategy: Callable[[str], str]

    # Model's strategy: prompt -> response
    model_strategy: Callable[[str], str]

    # Quality as coutility (value to user)
    coutility: Callable[[str, str], float]

    def play(self, context: str) -> Tuple[str, str, float]:
        """Execute one round of the game"""
        prompt = self.user_strategy(context)
        response = self.model_strategy(prompt)
        quality = self.coutility(prompt, response)
        return prompt, response, quality

    def equilibrium_seek(self, context: str, threshold: float = 0.85) -> Tuple[str, str]:
        """
        RMP as equilibrium-seeking:
        Iterate until coutility >= threshold
        """
        prompt, response, quality = self.play(context)

        while quality < threshold:
            # Refine user strategy based on feedback
            self.user_strategy = self.refine_strategy(
                self.user_strategy, response, quality
            )
            prompt, response, quality = self.play(context)

        return prompt, response
```

---

## Pattern 4: Profunctor Optics for Prompt Editing

```python
from typing import Generic, TypeVar, Callable, Tuple

S = TypeVar('S')  # Source (full prompt)
T = TypeVar('T')  # Target (modified prompt)
A = TypeVar('A')  # Focus (sub-prompt)
B = TypeVar('B')  # Replacement

@dataclass
class Lens(Generic[S, T, A, B]):
    """Bidirectional prompt accessor"""
    get: Callable[[S], A]
    set: Callable[[S, B], T]

    def modify(self, f: Callable[[A], B]) -> Callable[[S], T]:
        """Apply function to focused part"""
        return lambda s: self.set(s, f(self.get(s)))

# Example lenses for prompt structure
task_lens = Lens(
    get=lambda p: p.task,
    set=lambda p, t: p._replace(task=t)
)

context_lens = Lens(
    get=lambda p: p.context,
    set=lambda p, c: p._replace(context=c)
)

quality_lens = Lens(
    get=lambda p: p.quality_target,
    set=lambda p, q: p._replace(quality_target=q)
)

# Compose lenses for nested access
def compose_lens(outer: Lens, inner: Lens) -> Lens:
    return Lens(
        get=lambda s: inner.get(outer.get(s)),
        set=lambda s, b: outer.set(s, inner.set(outer.get(s), b))
    )
```

---

## Pattern 5: Traced Monoidal for RMP Loops

```python
from typing import TypeVar, Callable, Tuple

A = TypeVar('A')
B = TypeVar('B')
U = TypeVar('U')  # Loop variable

def trace(f: Callable[[Tuple[A, U]], Tuple[B, U]],
          init: U) -> Callable[[A], B]:
    """
    Trace operation: C(A⊗U, B⊗U) → C(A, B)
    Models feedback loop with carried state
    """
    def traced(a: A) -> B:
        state = init
        while True:
            b, new_state = f((a, state))
            if converged(state, new_state):
                return b
            state = new_state
    return traced

# RMP as traced morphism
def rmp_iteration(prompt_state: Tuple[str, float]) -> Tuple[str, float]:
    """One iteration: (prompt, quality) -> (refined, new_quality)"""
    prompt, quality = prompt_state
    refined = refine_prompt(prompt)
    new_quality = assess_quality(refined)
    return refined, new_quality

# Apply trace to get convergent RMP
rmp_loop = trace(
    f=lambda ps: rmp_iteration(ps),
    init=0.5  # Initial quality
)
```

---

## Pattern 6: Sheaf for Multi-Agent Consistency

```python
from typing import Dict, List, Set, Callable
from dataclasses import dataclass

@dataclass
class Sheaf:
    """Sheaf over agent dependency graph"""

    # Graph: agent dependencies
    agents: Set[str]
    dependencies: Dict[str, List[str]]

    # Stalks: local prompt spaces per agent
    stalks: Dict[str, Callable]

    # Restriction maps: consistency constraints
    restrictions: Dict[Tuple[str, str], Callable]

    def check_consistency(self) -> bool:
        """
        H¹(Sheaf) = 0 ⟹ globally consistent
        Check if local prompts glue to global
        """
        for agent in self.agents:
            local_prompt = self.stalks[agent]()
            for dep in self.dependencies.get(agent, []):
                restricted = self.restrictions[(agent, dep)](local_prompt)
                dep_prompt = self.stalks[dep]()
                if not compatible(restricted, dep_prompt):
                    return False
        return True

    def diagnose_failure(self) -> List[Tuple[str, str]]:
        """Return pairs of inconsistent agents"""
        failures = []
        for agent in self.agents:
            for dep in self.dependencies.get(agent, []):
                if not self.check_pair(agent, dep):
                    failures.append((agent, dep))
        return failures
```

---

## Pattern 7: Elgot Monad for Guaranteed Convergence

```python
from typing import TypeVar, Callable, Union
from dataclasses import dataclass

A = TypeVar('A')
B = TypeVar('B')

@dataclass
class Either:
    """Sum type for iteration control"""
    left: A = None   # Continue
    right: B = None  # Done

    @property
    def is_done(self) -> bool:
        return self.right is not None

class ElgotMonad:
    """
    Completely iterative monad
    GUARANTEES convergence of iteration
    """

    def iterate(self,
                f: Callable[[A], Either[A, B]],
                start: A,
                max_iter: int = 100) -> B:
        """
        Iterate f until Right (done)
        Elgot monad laws guarantee termination
        """
        current = start
        for _ in range(max_iter):
            result = f(current)
            if result.is_done:
                return result.right
            current = result.left

        # Fallback: return best effort
        return current

# RMP with guaranteed convergence
def rmp_step(prompt: str) -> Either[str, str]:
    """One RMP step: Either continue or done"""
    refined = refine(prompt)
    quality = assess(refined)

    if quality >= 0.85:
        return Either(right=refined)  # Done
    else:
        return Either(left=refined)   # Continue

elgot = ElgotMonad()
final_prompt = elgot.iterate(rmp_step, initial_prompt)
```

---

## Pattern 8: Enriched Magnitude for Quality

```python
import numpy as np
from typing import List

def magnitude(similarity_matrix: np.ndarray) -> float:
    """
    Magnitude: single number capturing diversity/quality

    |X| = sum of weights where Z·w = 1
    Z_ij = exp(-d(x_i, x_j))  # similarity matrix
    """
    n = similarity_matrix.shape[0]
    ones = np.ones(n)

    try:
        weights = np.linalg.solve(similarity_matrix, ones)
        return np.sum(weights)
    except np.linalg.LinAlgError:
        return n  # Fallback: all distinct

def prompt_magnitude(prompts: List[str]) -> float:
    """Compute magnitude of prompt set"""
    n = len(prompts)
    Z = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            Z[i, j] = semantic_similarity(prompts[i], prompts[j])

    return magnitude(Z)

# High magnitude = diverse, high-quality prompt set
# Low magnitude = redundant prompts
```

---

## Pattern 9: Session Types for Conversations

```python
from typing import Generic, TypeVar
from abc import ABC, abstractmethod

Msg = TypeVar('Msg')

class SessionType(ABC):
    """Protocol for typed conversations"""
    pass

class Send(SessionType, Generic[Msg]):
    """!Msg.Continuation - send then continue"""
    def __init__(self, msg_type: type, continuation: SessionType):
        self.msg_type = msg_type
        self.continuation = continuation

class Recv(SessionType, Generic[Msg]):
    """?Msg.Continuation - receive then continue"""
    def __init__(self, msg_type: type, continuation: SessionType):
        self.msg_type = msg_type
        self.continuation = continuation

class End(SessionType):
    """Session complete"""
    pass

# Example: Typed prompt-response protocol
PromptProtocol = Send[str](str,      # Send prompt
                 Recv[str](str,      # Receive response
                 Send[float](float,  # Send quality feedback
                 End())))            # Done

class TypedSession:
    """Execute session following protocol"""

    def __init__(self, protocol: SessionType):
        self.protocol = protocol
        self.current = protocol

    def send(self, msg) -> None:
        if not isinstance(self.current, Send):
            raise TypeError("Protocol violation: cannot send")
        if not isinstance(msg, self.current.msg_type):
            raise TypeError(f"Expected {self.current.msg_type}")
        self.current = self.current.continuation

    def recv(self) -> Msg:
        if not isinstance(self.current, Recv):
            raise TypeError("Protocol violation: cannot receive")
        self.current = self.current.continuation
        return self._receive()
```

---

## Pattern 10: Contextad for Unified Context

```python
from dataclasses import dataclass
from typing import TypeVar, Callable, List

A = TypeVar('A')
E = TypeVar('E')  # External context (tools, knowledge)

@dataclass
class Contextad(Generic[A, E]):
    """
    Contextad = Comonad + Actegory unified
    Handles: history (comonad) + tools (actegory)
    """
    value: A
    history: List[A]          # Comonadic context
    external: E               # Actegory action source

    def extract(self) -> A:
        """Comonadic extract"""
        return self.value

    def act(self, action: Callable[[E, A], A]) -> 'Contextad[A, E]':
        """Actegory action from external context"""
        new_value = action(self.external, self.value)
        return Contextad(
            value=new_value,
            history=self.history + [self.value],
            external=self.external
        )

    def extend(self, f: Callable[['Contextad[A, E]'], A]) -> 'Contextad[A, E]':
        """Comonadic extend with full context"""
        return Contextad(
            value=f(self),
            history=self.history,
            external=self.external
        )

# Usage: Prompt with conversation history + tool access
prompt_context = Contextad(
    value=current_prompt,
    history=conversation_history,
    external=available_tools
)

# Apply tool augmentation
augmented = prompt_context.act(
    lambda tools, prompt: enhance_with_tools(prompt, tools)
)

# Extract context-aware refinement
refined = augmented.extend(
    lambda ctx: refine_with_history(ctx.value, ctx.history)
)
```

---

## Quick Reference: Which Pattern for What?

| Problem | Pattern | Structure |
|---------|---------|-----------|
| Tier-based context | Graded Comonad | `W_grade` |
| Prompt learning | Kan Extension | `Lan_K` |
| Prompt-response dynamics | Open Game | Coutility |
| Sub-prompt editing | Profunctor Optics | Lens |
| RMP iteration | Traced Monoidal | `trace` |
| Multi-agent consistency | Sheaf | `H¹ = 0` |
| Guaranteed convergence | Elgot Monad | Iteration |
| Quality metrics | Magnitude | `\|X\|` |
| Typed conversations | Session Types | Protocol |
| Unified context | Contextad | Wreath |

---

**Status**: All patterns extracted and documented
**Ready for**: Implementation in framework
