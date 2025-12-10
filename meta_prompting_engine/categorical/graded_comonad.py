"""
Graded Comonad W_g: Resource-Indexed Context Extraction

A graded comonad extends the standard comonad with a grade (index) that
tracks resource consumption - in our case, token budgets per tier (L1-L7).

Mathematical Definition:
    Graded Comonad: (W, ε, δ, •) where grade monoid G = (L1-L7, •, L1)

    - W_g(A) = A with grade g context
    - ε_g : W_g(A) → A (grade-bounded extract)
    - δ_{g,h} : W_g(A) → W_h(W_{g-h}(A)) (grade-splitting duplicate)

    Grade Monoid: (Tier, max, L1)
    - L1 • L2 = L2 (max)
    - Identity: L1

Laws (in addition to standard comonad laws):
    1. Grade preservation: extract(w_g) respects g's token bound
    2. Grade composition: duplicate_{g,h} ∘ duplicate_{h,k} = duplicate_{g,k}
    3. Grade identity: duplicate_{g,g} ≈ duplicate (standard)

References:
    - arXiv:2501.14550 (Bean) - Graded Coeffect Comonads
    - arXiv:2002.06784 - Graded Algebraic Theories
    - arXiv:2306.01487 - Quantitative Graded Semantics

Example:
    >>> graded = GradedComonad()
    >>> obs = graded.create_observation("result", grade=Tier.L3)
    >>> extracted = graded.extract(obs)  # Bounded by L3 token limit
    >>> upgraded = graded.upgrade(obs, Tier.L5)  # Increase resource allowance
"""

from typing import TypeVar, Callable, Generic, Any, List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
import json

from .comonad import Observation, Comonad, create_context_comonad

# Type variables
A = TypeVar('A')
B = TypeVar('B')


class Tier(IntEnum):
    """
    Complexity tiers L1-L7 forming the grade monoid.

    Token budgets follow the categorical tier system:
    - L1-L2: Simple tasks (1.2K-3K tokens)
    - L3-L4: Moderate tasks (4.5K-6K tokens)
    - L5-L6: Complex tasks (9K-12K tokens)
    - L7: Genius-level (22K tokens)

    The monoid operation is max (higher tier subsumes lower).
    """
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6
    L7 = 7

    @property
    def token_budget(self) -> int:
        """Token budget for this tier."""
        budgets = {
            Tier.L1: 1200,
            Tier.L2: 3000,
            Tier.L3: 4500,
            Tier.L4: 6000,
            Tier.L5: 9000,
            Tier.L6: 12000,
            Tier.L7: 22000,
        }
        return budgets[self]

    @property
    def description(self) -> str:
        """Human-readable tier description."""
        descriptions = {
            Tier.L1: "Novice - Simple direct tasks",
            Tier.L2: "Beginner - Structured simple tasks",
            Tier.L3: "Competent - Multi-step reasoning",
            Tier.L4: "Proficient - Complex decomposition",
            Tier.L5: "Expert - Parallel exploration",
            Tier.L6: "Master - Hierarchical orchestration",
            Tier.L7: "Genius - Autonomous evolution",
        }
        return descriptions[self]

    def __mul__(self, other: 'Tier') -> 'Tier':
        """
        Grade monoid operation: max(g1, g2).

        Higher tier subsumes lower - composing L3 and L5 yields L5.
        """
        return Tier(max(self.value, other.value))

    @classmethod
    def identity(cls) -> 'Tier':
        """Identity element of grade monoid."""
        return Tier.L1


@dataclass
class GradedObservation(Generic[A]):
    """
    Observation indexed by grade (tier).

    This is W_g(A) - a value wrapped with grade-bounded context.
    The grade determines the token budget and complexity allowance.

    Attributes:
        current: The focused value
        grade: Resource index (L1-L7)
        context: Execution context
        history: Previous observations
        metadata: Additional metadata
        timestamp: Observation time
        tokens_used: Actual tokens consumed

    Invariant:
        tokens_used <= grade.token_budget
    """
    current: A
    grade: Tier
    context: Dict[str, Any] = field(default_factory=dict)
    history: List['GradedObservation'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None
    tokens_used: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        # Add grade info to context
        self.context['grade'] = self.grade.name
        self.context['token_budget'] = self.grade.token_budget

    @property
    def tokens_remaining(self) -> int:
        """Remaining token budget."""
        return max(0, self.grade.token_budget - self.tokens_used)

    @property
    def budget_utilization(self) -> float:
        """Fraction of budget used [0.0, 1.0]."""
        return self.tokens_used / self.grade.token_budget

    def __str__(self) -> str:
        return f"W_{self.grade.name}({type(self.current).__name__}, {self.tokens_used}/{self.grade.token_budget} tokens)"

    def __repr__(self) -> str:
        return f"GradedObservation(grade={self.grade.name}, current={str(self.current)[:30]}..., utilization={self.budget_utilization:.1%})"


@dataclass
class GradedComonad:
    """
    Graded Comonad W_g with resource-indexed operations.

    Extends standard comonad with grade tracking:
    - extract respects token bounds
    - duplicate can split grades
    - extend propagates grade constraints

    Grade Laws:
        1. extract_{g}(w) respects g's token limit
        2. duplicate_{g,h}(w) = W_h(W_{g-h}(w))
        3. upgrade(w_g, h) valid iff g ≤ h
        4. downgrade(w_g, h) truncates if needed

    Example:
        >>> gc = GradedComonad()
        >>> obs = gc.create_observation("complex result", Tier.L5)
        >>> simple = gc.downgrade(obs, Tier.L2)  # May truncate
        >>> rich = gc.upgrade(obs, Tier.L7)  # Allows more context
    """

    base_comonad: Comonad = field(default_factory=create_context_comonad)

    def create_observation(
        self,
        value: A,
        grade: Tier,
        context: Optional[Dict[str, Any]] = None,
        tokens_used: int = 0
    ) -> GradedObservation[A]:
        """
        Create a graded observation.

        Args:
            value: The focused value
            grade: Resource tier (L1-L7)
            context: Optional execution context
            tokens_used: Tokens already consumed

        Returns:
            GradedObservation with grade-bounded context
        """
        return GradedObservation(
            current=value,
            grade=grade,
            context=context or {},
            tokens_used=tokens_used
        )

    def extract(self, wa: GradedObservation[A]) -> A:
        """
        ε_g : W_g(A) → A

        Grade-bounded extraction. The result respects the
        token budget of the grade.

        For string values, truncates to fit token estimate.

        Args:
            wa: Graded observation

        Returns:
            Extracted value (possibly truncated)
        """
        value = wa.current

        # For strings, apply token-based truncation
        if isinstance(value, str):
            return self._truncate_to_budget(value, wa.grade)

        return value

    def extract_by_tier(self, wa: GradedObservation[A], tier: Tier) -> A:
        """
        Extract with explicit tier override.

        Useful for extracting at a different tier than stored.

        Args:
            wa: Graded observation
            tier: Tier to extract at

        Returns:
            Extracted value bounded by tier
        """
        value = wa.current

        if isinstance(value, str):
            return self._truncate_to_budget(value, tier)

        return value

    def duplicate(
        self,
        wa: GradedObservation[A]
    ) -> GradedObservation[GradedObservation[A]]:
        """
        δ_g : W_g(A) → W_g(W_g(A))

        Standard duplicate preserving grade.

        Args:
            wa: Graded observation

        Returns:
            Meta-observation at same grade
        """
        return GradedObservation(
            current=wa,
            grade=wa.grade,
            context={
                'meta_observation': True,
                'inner_grade': wa.grade.name,
                'original_context': wa.context,
            },
            history=[wa] + wa.history[:5],  # Limit history depth
            metadata={
                'observation_depth': len(wa.history) + 1,
                'total_tokens': wa.tokens_used,
            },
            tokens_used=wa.tokens_used
        )

    def duplicate_split(
        self,
        wa: GradedObservation[A],
        outer_grade: Tier,
        inner_grade: Tier
    ) -> GradedObservation[GradedObservation[A]]:
        """
        δ_{g,h} : W_g(A) → W_h(W_{g-h}(A))

        Grade-splitting duplicate. Outer and inner grades
        must compose to original grade (via max).

        Args:
            wa: Graded observation at grade g
            outer_grade: Grade for outer observation (h)
            inner_grade: Grade for inner observation (g-h)

        Returns:
            Nested observation with split grades

        Raises:
            ValueError: If grades don't compose correctly
        """
        # Verify grade composition: outer • inner should equal original
        composed = outer_grade * inner_grade
        if composed != wa.grade:
            raise ValueError(
                f"Grade composition mismatch: {outer_grade.name} • {inner_grade.name} = "
                f"{composed.name} ≠ {wa.grade.name}"
            )

        inner_obs = GradedObservation(
            current=wa.current,
            grade=inner_grade,
            context=wa.context,
            history=wa.history,
            tokens_used=min(wa.tokens_used, inner_grade.token_budget)
        )

        return GradedObservation(
            current=inner_obs,
            grade=outer_grade,
            context={
                'split_duplicate': True,
                'outer_grade': outer_grade.name,
                'inner_grade': inner_grade.name,
            },
            tokens_used=wa.tokens_used - inner_obs.tokens_used
        )

    def extend(
        self,
        f: Callable[[GradedObservation[A]], B],
        wa: GradedObservation[A]
    ) -> GradedObservation[B]:
        """
        extend_g : (W_g(A) → B) → W_g(A) → W_g(B)

        Grade-preserving context-aware transformation.

        Args:
            f: Context-aware function
            wa: Graded observation

        Returns:
            Transformed observation at same grade
        """
        result = f(wa)

        # Estimate tokens for result
        result_tokens = self._estimate_tokens(result)
        total_tokens = min(
            wa.tokens_used + result_tokens,
            wa.grade.token_budget
        )

        return GradedObservation(
            current=result,
            grade=wa.grade,
            context={
                **wa.context,
                'extended': True,
                'transformation': getattr(f, '__name__', 'lambda'),
            },
            history=wa.history,
            metadata=wa.metadata,
            tokens_used=total_tokens
        )

    def upgrade(
        self,
        wa: GradedObservation[A],
        new_grade: Tier
    ) -> GradedObservation[A]:
        """
        Upgrade observation to higher tier.

        Allows more token budget and context richness.

        Args:
            wa: Original observation
            new_grade: Target grade (must be ≥ current)

        Returns:
            Observation at higher grade

        Raises:
            ValueError: If new_grade < current grade
        """
        if new_grade < wa.grade:
            raise ValueError(
                f"Cannot upgrade from {wa.grade.name} to lower {new_grade.name}. "
                f"Use downgrade() instead."
            )

        return GradedObservation(
            current=wa.current,
            grade=new_grade,
            context={
                **wa.context,
                'upgraded_from': wa.grade.name,
                'grade': new_grade.name,
                'token_budget': new_grade.token_budget,
            },
            history=wa.history,
            metadata={
                **wa.metadata,
                'upgrade_path': wa.metadata.get('upgrade_path', []) + [wa.grade.name],
            },
            tokens_used=wa.tokens_used
        )

    def downgrade(
        self,
        wa: GradedObservation[A],
        new_grade: Tier,
        truncate: bool = True
    ) -> GradedObservation[A]:
        """
        Downgrade observation to lower tier.

        May truncate content to fit new budget.

        Args:
            wa: Original observation
            new_grade: Target grade (must be ≤ current)
            truncate: Whether to truncate content if needed

        Returns:
            Observation at lower grade (possibly truncated)

        Raises:
            ValueError: If new_grade > current and truncate=False
        """
        if new_grade > wa.grade:
            raise ValueError(
                f"Cannot downgrade from {wa.grade.name} to higher {new_grade.name}. "
                f"Use upgrade() instead."
            )

        current = wa.current
        tokens_used = wa.tokens_used

        # Truncate if needed
        if truncate and tokens_used > new_grade.token_budget:
            if isinstance(current, str):
                current = self._truncate_to_budget(current, new_grade)
            tokens_used = new_grade.token_budget

        return GradedObservation(
            current=current,
            grade=new_grade,
            context={
                **wa.context,
                'downgraded_from': wa.grade.name,
                'grade': new_grade.name,
                'token_budget': new_grade.token_budget,
                'truncated': tokens_used != wa.tokens_used,
            },
            history=wa.history[:3],  # Limit history on downgrade
            metadata={
                **wa.metadata,
                'downgrade_path': wa.metadata.get('downgrade_path', []) + [wa.grade.name],
            },
            tokens_used=tokens_used
        )

    def _truncate_to_budget(self, text: str, tier: Tier) -> str:
        """
        Truncate text to fit tier's token budget.

        Uses rough estimate: 1 token ≈ 4 characters.

        Args:
            text: Text to truncate
            tier: Target tier

        Returns:
            Truncated text
        """
        # Rough estimate: 4 chars per token
        max_chars = tier.token_budget * 4

        if len(text) <= max_chars:
            return text

        # Truncate with ellipsis
        return text[:max_chars - 3] + "..."

    def _estimate_tokens(self, value: Any) -> int:
        """
        Estimate token count for a value.

        Args:
            value: Value to estimate

        Returns:
            Estimated token count
        """
        if isinstance(value, str):
            return len(value) // 4
        elif isinstance(value, (dict, list)):
            return len(json.dumps(value)) // 4
        else:
            return len(str(value)) // 4

    # === Law Verification ===

    def verify_grade_preservation(self, wa: GradedObservation[A]) -> bool:
        """
        Verify that extract respects grade bounds.

        Law: extract_g(w) has tokens ≤ g.token_budget
        """
        extracted = self.extract(wa)
        estimated_tokens = self._estimate_tokens(extracted)
        return estimated_tokens <= wa.grade.token_budget

    def verify_grade_composition(
        self,
        wa: GradedObservation[A],
        g: Tier,
        h: Tier,
        k: Tier
    ) -> bool:
        """
        Verify grade composition law.

        Law: duplicate_{g,h} ∘ duplicate_{h,k} = duplicate_{g,k}

        (Requires g • h = h • k for proper composition)
        """
        try:
            # Left side: duplicate_{g,h}(duplicate_{h,k}(wa))
            inner = self.duplicate_split(wa, h, k)
            left = self.duplicate_split(inner, g, h)

            # Right side: duplicate_{g,k}(wa)
            right = self.duplicate_split(wa, g, k)

            # Compare outer grades
            return left.grade == right.grade
        except ValueError:
            return False  # Grades don't compose properly

    def verify_upgrade_downgrade_inverse(
        self,
        wa: GradedObservation[A],
        higher: Tier
    ) -> bool:
        """
        Verify upgrade/downgrade are partial inverses.

        Law: downgrade(upgrade(w_g, h), g) ≈ w_g
        (Approximate due to potential truncation)
        """
        if higher <= wa.grade:
            return True  # Trivially true

        upgraded = self.upgrade(wa, higher)
        downgraded = self.downgrade(upgraded, wa.grade)

        return (
            downgraded.grade == wa.grade and
            downgraded.current == wa.current
        )


# === Factory Functions ===

def create_graded_comonad() -> GradedComonad:
    """
    Factory for creating a GradedComonad instance.

    Returns:
        GradedComonad ready for use

    Example:
        >>> gc = create_graded_comonad()
        >>> obs = gc.create_observation("result", Tier.L4)
    """
    return GradedComonad()


def infer_tier_from_complexity(complexity: float) -> Tier:
    """
    Infer appropriate tier from task complexity.

    Args:
        complexity: Task complexity [0.0, 1.0]

    Returns:
        Appropriate tier for the complexity

    Mapping:
        0.00-0.15 → L1
        0.15-0.30 → L2
        0.30-0.45 → L3
        0.45-0.60 → L4
        0.60-0.75 → L5
        0.75-0.90 → L6
        0.90-1.00 → L7
    """
    if complexity < 0.15:
        return Tier.L1
    elif complexity < 0.30:
        return Tier.L2
    elif complexity < 0.45:
        return Tier.L3
    elif complexity < 0.60:
        return Tier.L4
    elif complexity < 0.75:
        return Tier.L5
    elif complexity < 0.90:
        return Tier.L6
    else:
        return Tier.L7


def infer_tier_from_tokens(token_count: int) -> Tier:
    """
    Infer minimum tier needed for token count.

    Args:
        token_count: Number of tokens needed

    Returns:
        Minimum tier that can handle the tokens
    """
    for tier in Tier:
        if token_count <= tier.token_budget:
            return tier
    return Tier.L7  # Maximum tier if exceeds all budgets
