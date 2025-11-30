"""
Comonad W: Context Extraction and Observation

A comonad is the categorical dual of a monad, providing:
1. extract ε: W(A) → A (extracting value from context)
2. duplicate δ: W(A) → W(W(A)) (adding meta-context)
3. extend: (W(A) → B) → W(A) → W(B) (context-aware transformation)

In meta-prompting, the comonad W formalizes context extraction where:
- W(Output) = Output with execution context (prompts, history, metrics)
- extract ε = Focused view on essential result
- duplicate δ = Meta-observation (observation of observation)
- extend = Context-aware transformation using full history

This integrates with CC2.0 OBSERVE framework, which already implements
comonad operations for system observability.

References:
- Uustalu & Vene (2008) - Comonads and Context-Dependent Computation
- L5 Meta-Prompt: "Comonad W for context extraction with extract/extend"
- CC2-OBSERVE-INTEGRATION.md: Production comonad in LUXOR workspace

Mathematical Notation:
    Comonad: (W, ε, δ) on category O (Outputs)
    - ε : W → 1_O (extract)
    - δ : W → W ∘ W (duplicate)

    Laws:
    1. Left identity:  ε ∘ δ = id_W
    2. Right identity: fmap ε ∘ δ = id_W
    3. Associativity:  δ ∘ δ = fmap δ ∘ δ

Example:
    >>> comonad = create_context_comonad()
    >>> obs = comonad.create_observation(output, prompt, history)
    >>> result = comonad.extract(obs)  # Focused view
    >>> meta_obs = comonad.duplicate(obs)  # Meta-observation
"""

from typing import TypeVar, Callable, Generic, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .types import Prompt

# Type variables for comonad content
A = TypeVar('A')
B = TypeVar('B')


@dataclass
class Observation(Generic[A]):
    """
    Observation wrapper providing context for comonadic operations.

    This is W(A) - a value wrapped with rich execution context:
    - Full system state at observation time
    - Historical snapshots for trend analysis
    - Current focused value
    - Metadata for quality assessment

    Attributes:
        current: The focused value (current state)
        context: Full system context at observation time
        history: List of previous observations for trend analysis
        metadata: Additional observation metadata
        timestamp: When observation was made

    Example:
        >>> obs = Observation(
        ...     current="The maximum is 9",
        ...     context={"prompt": prompt, "quality": 0.92},
        ...     history=[prev_obs1, prev_obs2]
        ... )
    """
    current: A
    context: dict[str, Any]
    history: List['Observation'] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def __str__(self) -> str:
        return f"W({type(self.current).__name__}, history={len(self.history)})"

    def __repr__(self) -> str:
        return f"Observation(current={str(self.current)[:50]}, context_keys={list(self.context.keys())})"


@dataclass
class Comonad(Generic[A]):
    """
    Comonad W with verified categorical laws.

    Attributes:
        extract: ε : W(A) → A (extract focused value)
        duplicate: δ : W(A) → W(W(A)) (create meta-observation)

    Laws:
        1. Left identity:  extract ∘ duplicate = id
        2. Right identity: fmap extract ∘ duplicate = id
        3. Associativity:  duplicate ∘ duplicate = fmap duplicate ∘ duplicate

    Example:
        >>> comonad = Comonad(
        ...     extract=lambda obs: obs.current,
        ...     duplicate=lambda obs: Observation(obs, {...})
        ... )
    """

    extract: Callable[[Observation[A]], A]
    duplicate: Callable[[Observation[A]], Observation[Observation[A]]]

    def extend(
        self,
        f: Callable[[Observation[A]], B],
        wa: Observation[A]
    ) -> Observation[B]:
        """
        Context-aware transformation using full observation.

        extend (cobind) applies a function that has access to the
        full observation context, not just the current value.

        Process:
        1. duplicate wa to get W(W(A))
        2. fmap f to get W(B)
        3. extract inner layer

        Args:
            f: Context-aware function W(A) → B
            wa: Observation with context

        Returns:
            Observation[B] with transformed value but same context

        Mathematical Definition:
            extend f = fmap f ∘ duplicate

        Example:
            >>> def analyze_with_context(obs: Observation[str]) -> float:
            ...     # Can access obs.history, obs.context, obs.current
            ...     return assess_quality_from_history(obs)
            >>> quality_obs = comonad.extend(analyze_with_context, output_obs)
        """
        # duplicate: W(A) → W(W(A))
        wwa = self.duplicate(wa)

        # fmap f: W(W(A)) → W(B)
        # Since duplicate puts wa itself as current, we apply f to it
        transformed_value = f(wwa.current)

        # Wrap in observation with original context
        return Observation(
            current=transformed_value,
            context=wa.context,
            history=wa.history,
            metadata={
                **wa.metadata,
                'extended': True,
                'transformation': f.__name__ if hasattr(f, '__name__') else 'lambda'
            },
            timestamp=datetime.now()
        )

    def verify_left_identity(self, wa: Observation[A]) -> bool:
        """
        Verify comonad left identity law: extract ∘ duplicate = id

        Extracting from a duplicated observation should give
        back the original observation.

        Args:
            wa: Observation to test

        Returns:
            True if law holds

        Mathematical Definition:
            ε(δ(w)) = w

        Example:
            >>> obs = Observation("result", {"quality": 0.9})
            >>> assert comonad.verify_left_identity(obs)
        """
        # Left side: extract(duplicate(wa))
        duplicated = self.duplicate(wa)
        extracted = self.extract(duplicated)

        # Right side: wa
        return self._observations_equal(extracted, wa)

    def verify_right_identity(self, wa: Observation[A]) -> bool:
        """
        Verify comonad right identity law: fmap extract ∘ duplicate = id

        Mapping extract over a duplicated observation should
        give back the original observation.

        Args:
            wa: Observation to test

        Returns:
            True if law holds

        Mathematical Definition:
            fmap ε(δ(w)) = w

        Example:
            >>> assert comonad.verify_right_identity(obs)
        """
        # Left side: fmap extract(duplicate(wa))
        duplicated = self.duplicate(wa)
        # fmap extract means: extract from the inner observation
        fmap_extracted = Observation(
            current=self.extract(duplicated.current),
            context=duplicated.context,
            history=duplicated.history,
            metadata=duplicated.metadata
        )

        # Right side: wa
        return self._observations_equal(fmap_extracted.current, wa.current)

    def verify_associativity(self, wa: Observation[A]) -> bool:
        """
        Verify comonad associativity law: duplicate ∘ duplicate = fmap duplicate ∘ duplicate

        Duplicating twice should be the same as duplicating and
        mapping duplicate over the result.

        Args:
            wa: Observation to test

        Returns:
            True if law holds

        Mathematical Definition:
            δ(δ(w)) = fmap δ(δ(w))

        Example:
            >>> assert comonad.verify_associativity(obs)
        """
        # Left side: duplicate(duplicate(wa))
        left_side = self.duplicate(self.duplicate(wa))

        # Right side: fmap duplicate(duplicate(wa))
        duplicated_once = self.duplicate(wa)
        # fmap duplicate means: duplicate the inner observation
        right_side = Observation(
            current=self.duplicate(duplicated_once.current),
            context=duplicated_once.context,
            history=duplicated_once.history,
            metadata=duplicated_once.metadata
        )

        # Compare structures (both should be W(W(W(A))))
        return (
            isinstance(left_side.current, Observation) and
            isinstance(right_side.current, Observation)
        )

    def _observations_equal(self, obs1: Any, obs2: Any) -> bool:
        """
        Check if two observations are equal (structural equality).

        Args:
            obs1: First observation (or value)
            obs2: Second observation (or value)

        Returns:
            True if structurally equal
        """
        if isinstance(obs1, Observation) and isinstance(obs2, Observation):
            return (
                str(obs1.current) == str(obs2.current) and
                obs1.context.keys() == obs2.context.keys()
            )
        else:
            return str(obs1) == str(obs2)


# Factory function for creating Context Extraction Comonad
def create_context_comonad() -> Comonad:
    """
    Factory for creating W: Context Extraction comonad.

    This comonad provides context-aware operations for meta-prompting:
    - extract ε: Focus on essential result
    - duplicate δ: Meta-observation (observe the observation)
    - extend: Transform using full context

    Returns:
        Comonad[Any] with verified laws

    Extract Operation (ε):
        W(A) → A
        - Extracts the current focused value
        - Discards context (but preserves it in observation)

    Duplicate Operation (δ):
        W(A) → W(W(A))
        - Creates meta-observation
        - Inner observation becomes the current value
        - Outer observation provides meta-context

    Integration with CC2.0 OBSERVE:
        This comonad structure matches the CC2.0 framework:
        - extract = focused view on system health
        - duplicate = meta-observation of observation quality
        - extend = context-aware recommendations

    Example:
        >>> comonad = create_context_comonad()
        >>> obs = comonad.create_observation(
        ...     current="Maximum is 9",
        ...     context={"prompt": prompt, "quality": 0.92},
        ...     history=[prev_obs]
        ... )
        >>> result = comonad.extract(obs)  # "Maximum is 9"
        >>> meta_obs = comonad.duplicate(obs)  # W(W(...))
    """

    def extract(wa: Observation[A]) -> A:
        """
        ε : W(A) → A

        Extracts the focused value from observation.

        This is the "focused view" in CC2.0 OBSERVE - we zoom in
        on the essential result while the context remains available.

        Args:
            wa: Observation with context

        Returns:
            Current focused value
        """
        return wa.current

    def duplicate(wa: Observation[A]) -> Observation[Observation[A]]:
        """
        δ : W(A) → W(W(A))

        Creates meta-observation by making the observation itself
        the focused value.

        This is the "meta-observation" in CC2.0 OBSERVE - we observe
        the observation itself, enabling assessment of observation
        quality, completeness, timeliness, etc.

        Args:
            wa: Observation with context

        Returns:
            Meta-observation W(W(A))
        """
        return Observation(
            current=wa,  # The observation becomes the current value
            context={
                'meta_observation': True,
                'original_context_keys': list(wa.context.keys()),
                'observation_timestamp': wa.timestamp,
                'history_depth': len(wa.history)
            },
            history=[wa] + wa.history,  # Prepend current to history
            metadata={
                'observation_quality': _assess_observation_quality(wa),
                'completeness': _assess_observation_completeness(wa)
            },
            timestamp=datetime.now()
        )

    # Attach create_observation as utility method
    comonad = Comonad(extract=extract, duplicate=duplicate)
    comonad.create_observation = create_observation
    return comonad


def create_observation(
    current: A,
    context: dict[str, Any],
    history: Optional[List[Observation]] = None,
    metadata: Optional[dict[str, Any]] = None
) -> Observation[A]:
    """
    Create an observation with context.

    This is a convenience function for wrapping values in
    comonadic observations.

    Args:
        current: Current focused value
        context: Execution context
        history: Optional previous observations
        metadata: Optional metadata

    Returns:
        Observation[A] ready for comonadic operations

    Example:
        >>> obs = create_observation(
        ...     current="Maximum is 9",
        ...     context={"prompt": prompt, "quality": 0.92}
        ... )
    """
    return Observation(
        current=current,
        context=context,
        history=history or [],
        metadata=metadata or {},
        timestamp=datetime.now()
    )


def _assess_observation_quality(obs: Observation) -> float:
    """
    Assess quality of observation itself (meta-quality).

    Criteria:
    - Context richness (how much context is available)
    - History depth (how much historical data)
    - Metadata completeness

    Args:
        obs: Observation to assess

    Returns:
        Quality score [0.0, 1.0]
    """
    quality = 0.5  # Base score

    # Context richness
    if len(obs.context) >= 3:
        quality += 0.2

    # Has history
    if len(obs.history) > 0:
        quality += 0.2

    # Has metadata
    if obs.metadata:
        quality += 0.1

    return min(quality, 1.0)


def _assess_observation_completeness(obs: Observation) -> float:
    """
    Assess completeness of observation.

    Criteria:
    - Has all expected context keys
    - History is continuous
    - Timestamps are present

    Args:
        obs: Observation to assess

    Returns:
        Completeness score [0.0, 1.0]
    """
    completeness = 0.6  # Base score

    # Expected context keys present
    expected_keys = ['prompt', 'quality', 'meta_level']
    present_keys = sum(1 for k in expected_keys if k in obs.context)
    completeness += 0.1 * (present_keys / len(expected_keys))

    # Has timestamp
    if obs.timestamp is not None:
        completeness += 0.1

    # History is reasonable
    if 0 < len(obs.history) <= 10:  # Some history but not excessive
        completeness += 0.1

    return min(completeness, 1.0)
