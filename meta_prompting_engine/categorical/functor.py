"""
Functor F: Tasks → Prompts

A functor is a structure-preserving mapping between categories that preserves:
1. Identity: F(id_A) = id_F(A)
2. Composition: F(g ∘ f) = F(g) ∘ F(f)

In meta-prompting, the functor F maps tasks to prompts while preserving
the compositional structure of task transformations.

References:
- Zhang et al. (arXiv:2311.11482) - Empirical validation
- de Wynter et al. (arXiv:2312.06562) - Exponential objects P^T

Mathematical Notation:
    Categories: T (Tasks), P (Prompts)
    Functor: F : T → P
    - F_obj : Ob(T) → Ob(P)  (object mapping)
    - F_mor : Hom_T(A,B) → Hom_P(F(A), F(B))  (morphism mapping)

Example:
    >>> from tasks import Task, Prompt
    >>> functor = create_task_to_prompt_functor(llm_client)
    >>> task = Task("Find max number in [3,1,4,1,5,9]")
    >>> prompt = functor(task)  # F_obj(task)
    >>> assert functor.verify_identity_law(task)
    >>> assert functor.verify_composition_law(task, f, g)
"""

from typing import TypeVar, Callable, Generic, Any
from dataclasses import dataclass
import hashlib

# Type variables for categories
T = TypeVar('T')  # Tasks category
P = TypeVar('P')  # Prompts category


@dataclass
class Functor(Generic[T, P]):
    """
    Functor F: T → P with verified categorical laws.

    Attributes:
        map_object: F_obj : T → P (maps objects)
        map_morphism: F_mor : (T → T) → (P → P) (maps morphisms)

    Laws:
        1. Identity: F(id) = id
        2. Composition: F(g ∘ f) = F(g) ∘ F(f)

    Example:
        >>> functor = Functor(
        ...     map_object=lambda task: generate_prompt(task),
        ...     map_morphism=lambda f: lambda p: generate_prompt(f(reconstruct_task(p)))
        ... )
        >>> task = Task("Find maximum")
        >>> assert functor.verify_identity_law(task)
    """

    map_object: Callable[[T], P]
    map_morphism: Callable[[Callable[[T], T]], Callable[[P], P]]

    def __call__(self, task: T) -> P:
        """
        Apply functor to task (object mapping).

        This is syntactic sugar for map_object:
            F(task) ≡ F_obj(task)

        Args:
            task: Input task of type T

        Returns:
            Prompt of type P

        Example:
            >>> prompt = functor(task)  # F_obj(task)
        """
        return self.map_object(task)

    def fmap(self, f: Callable[[T], T]) -> Callable[[P], P]:
        """
        Apply functor to morphism (morphism mapping).

        Maps a task transformation to a prompt transformation:
            F_mor(f) : P → P

        Args:
            f: Task transformation (T → T)

        Returns:
            Prompt transformation (P → P)

        Example:
            >>> f = lambda task: enhance_task(task)
            >>> prompt_transform = functor.fmap(f)
            >>> enhanced_prompt = prompt_transform(original_prompt)
        """
        return self.map_morphism(f)

    def verify_identity_law(self, task: T) -> bool:
        """
        Verify functor identity law: F(id) = id

        The identity morphism on tasks must map to the identity morphism
        on prompts:
            F_mor(id_T) = id_P

        Args:
            task: Sample task for testing

        Returns:
            True if law holds, False otherwise

        Mathematical Definition:
            ∀τ ∈ Ob(T). F(id_T(τ)) = id_P(F(τ))

        Example:
            >>> assert functor.verify_identity_law(task)
        """
        identity = lambda x: x

        # F(id_T(task))
        left_side = self.map_object(identity(task))

        # id_P(F(task))
        right_side = self.map_morphism(identity)(self.map_object(task))

        return self._prompts_equal(left_side, right_side)

    def verify_composition_law(
        self,
        task: T,
        f: Callable[[T], T],
        g: Callable[[T], T]
    ) -> bool:
        """
        Verify functor composition law: F(g ∘ f) = F(g) ∘ F(f)

        Composition of task transformations must map to composition
        of prompt transformations.

        Args:
            task: Sample task for testing
            f: First task transformation (T → T)
            g: Second task transformation (T → T)

        Returns:
            True if law holds, False otherwise

        Mathematical Definition:
            ∀f: A→B, g: B→C in T.
                F_mor(g ∘_T f) = F_mor(g) ∘_P F_mor(f)

        Example:
            >>> f = lambda t: enhance_task(t)
            >>> g = lambda t: simplify_task(t)
            >>> assert functor.verify_composition_law(task, f, g)
        """
        # F(g ∘ f) = F_mor(g ∘ f)
        composed = lambda x: g(f(x))
        left_side = self.map_morphism(composed)(self.map_object(task))

        # F(g) ∘ F(f) = F_mor(g) ∘ F_mor(f)
        right_side = self.map_morphism(g)(
            self.map_morphism(f)(self.map_object(task))
        )

        return self._prompts_equal(left_side, right_side)

    def _prompts_equal(self, p1: P, p2: P) -> bool:
        """
        Check if two prompts are equal (structural equality).

        Uses hash-based comparison for efficiency. Override for custom equality.

        Args:
            p1: First prompt
            p2: Second prompt

        Returns:
            True if prompts are structurally equal
        """
        return self._hash_prompt(p1) == self._hash_prompt(p2)

    def _hash_prompt(self, prompt: P) -> str:
        """
        Compute hash of prompt for equality checking.

        Args:
            prompt: Prompt to hash

        Returns:
            SHA-256 hash as hex string
        """
        prompt_str = str(prompt)
        return hashlib.sha256(prompt_str.encode()).hexdigest()


# Factory function for creating Task → Prompt functor
def create_task_to_prompt_functor(llm_client) -> Functor:
    """
    Factory for creating F: Tasks → Prompts functor.

    This functor maps tasks to structured prompts while preserving
    compositional structure.

    Args:
        llm_client: LLM client for prompt generation

    Returns:
        Functor[Task, Prompt] with verified laws

    Object Mapping (F_obj):
        Task → Prompt via structured generation based on:
        - Task complexity analysis
        - Strategy selection (direct, multi-approach, autonomous)
        - Context building

    Morphism Mapping (F_mor):
        (Task → Task) → (Prompt → Prompt) via:
        - Task transformation f
        - Prompt reconstruction to task
        - Re-application of F_obj

    Example:
        >>> functor = create_task_to_prompt_functor(claude_client)
        >>> task = Task("Find maximum number in list")
        >>> prompt = functor(task)
        >>> print(prompt.template)
        "You are an expert problem solver..."
    """
    from .types import Task, Prompt
    from .complexity import analyze_complexity
    from .strategy import select_strategy

    def map_object(task: Task) -> Prompt:
        """
        F_obj: Map task to prompt.

        Process:
        1. Analyze task complexity (0.0-1.0)
        2. Select strategy based on complexity
        3. Build context with task metadata
        4. Generate structured prompt

        Args:
            task: Input task

        Returns:
            Structured prompt
        """
        # Analyze complexity
        complexity = analyze_complexity(task)

        # Select strategy
        strategy = select_strategy(complexity.overall)

        # Build context
        context = {
            'complexity': complexity.overall,
            'strategy': strategy.name,
            'task_type': task.type,
            'metadata': task.metadata
        }

        # Generate prompt
        return Prompt(
            template=strategy.template,
            variables=extract_variables(task),
            context=context,
            meta_level=0
        )

    def map_morphism(f: Callable[[Task], Task]) -> Callable[[Prompt], Prompt]:
        """
        F_mor: Map task transformation to prompt transformation.

        Process:
        1. Reconstruct task from prompt
        2. Apply task transformation f
        3. Generate new prompt via F_obj

        Args:
            f: Task transformation (T → T)

        Returns:
            Prompt transformation (P → P)
        """
        def prompt_transform(prompt: Prompt) -> Prompt:
            # Reconstruct task from prompt
            reconstructed_task = reconstruct_task(prompt)

            # Apply task transformation
            transformed_task = f(reconstructed_task)

            # Re-generate prompt
            return map_object(transformed_task)

        return prompt_transform

    return Functor(
        map_object=map_object,
        map_morphism=map_morphism
    )


def extract_variables(task: 'Task') -> dict:
    """
    Extract template variables from task.

    Args:
        task: Input task

    Returns:
        Dictionary of template variables
    """
    return {
        'description': task.description,
        'examples': task.examples if hasattr(task, 'examples') else [],
        'constraints': task.constraints if hasattr(task, 'constraints') else []
    }


def reconstruct_task(prompt: 'Prompt') -> 'Task':
    """
    Reconstruct task from prompt (inverse operation).

    This is used in morphism mapping to transform prompts via
    task transformations.

    Args:
        prompt: Input prompt

    Returns:
        Reconstructed task

    Note:
        This is a partial inverse - not all prompt information
        may map back to the original task perfectly.
    """
    from .types import Task

    return Task(
        description=prompt.variables.get('description', ''),
        complexity=prompt.context.get('complexity', 0.5),
        metadata=prompt.context.get('metadata', {})
    )
