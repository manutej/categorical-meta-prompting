"""
Tests for Graded Comonad (Pattern 1)

Tests verify:
1. Basic operations (create, extract, duplicate, extend)
2. Grade laws (preservation, composition)
3. Upgrade/downgrade operations
4. Token budget enforcement
5. Tier inference functions

Reference: arXiv:2501.14550 (Bean - Graded Coeffect Comonads)
"""

import pytest
from datetime import datetime

from meta_prompting_engine.categorical.graded_comonad import (
    Tier,
    GradedObservation,
    GradedComonad,
    create_graded_comonad,
    infer_tier_from_complexity,
    infer_tier_from_tokens,
)


class TestTier:
    """Tests for the Tier grade monoid."""

    def test_tier_ordering(self):
        """Tiers should be properly ordered L1 < L2 < ... < L7."""
        assert Tier.L1 < Tier.L2 < Tier.L3 < Tier.L4 < Tier.L5 < Tier.L6 < Tier.L7

    def test_tier_token_budgets(self):
        """Each tier should have expected token budget."""
        assert Tier.L1.token_budget == 1200
        assert Tier.L2.token_budget == 3000
        assert Tier.L3.token_budget == 4500
        assert Tier.L4.token_budget == 6000
        assert Tier.L5.token_budget == 9000
        assert Tier.L6.token_budget == 12000
        assert Tier.L7.token_budget == 22000

    def test_tier_monoid_operation(self):
        """Grade monoid operation should be max."""
        assert Tier.L1 * Tier.L1 == Tier.L1
        assert Tier.L2 * Tier.L3 == Tier.L3
        assert Tier.L5 * Tier.L3 == Tier.L5
        assert Tier.L7 * Tier.L1 == Tier.L7

    def test_tier_identity(self):
        """L1 should be identity element."""
        assert Tier.identity() == Tier.L1
        for tier in Tier:
            assert Tier.L1 * tier == tier

    def test_tier_descriptions(self):
        """Each tier should have a description."""
        for tier in Tier:
            assert tier.description is not None
            assert len(tier.description) > 0


class TestGradedObservation:
    """Tests for GradedObservation dataclass."""

    def test_create_observation(self):
        """Should create observation with grade."""
        obs = GradedObservation(
            current="test result",
            grade=Tier.L3
        )
        assert obs.current == "test result"
        assert obs.grade == Tier.L3
        assert obs.tokens_used == 0

    def test_observation_context_includes_grade(self):
        """Context should include grade info."""
        obs = GradedObservation(
            current="result",
            grade=Tier.L4
        )
        assert obs.context['grade'] == 'L4'
        assert obs.context['token_budget'] == 6000

    def test_tokens_remaining(self):
        """Should calculate remaining tokens correctly."""
        obs = GradedObservation(
            current="result",
            grade=Tier.L3,
            tokens_used=1000
        )
        assert obs.tokens_remaining == 3500  # 4500 - 1000

    def test_budget_utilization(self):
        """Should calculate utilization correctly."""
        obs = GradedObservation(
            current="result",
            grade=Tier.L2,
            tokens_used=1500
        )
        assert obs.budget_utilization == 0.5  # 1500/3000

    def test_str_representation(self):
        """Should have informative string representation."""
        obs = GradedObservation(
            current="test",
            grade=Tier.L5,
            tokens_used=2000
        )
        s = str(obs)
        assert "L5" in s
        assert "2000" in s
        assert "9000" in s


class TestGradedComonad:
    """Tests for GradedComonad operations."""

    @pytest.fixture
    def gc(self):
        """Create GradedComonad instance."""
        return create_graded_comonad()

    def test_create_observation(self, gc):
        """Should create graded observation."""
        obs = gc.create_observation("result", Tier.L4)
        assert obs.current == "result"
        assert obs.grade == Tier.L4

    def test_extract_basic(self, gc):
        """Extract should return current value."""
        obs = gc.create_observation("hello world", Tier.L3)
        extracted = gc.extract(obs)
        assert extracted == "hello world"

    def test_extract_truncates_long_string(self, gc):
        """Extract should truncate strings exceeding budget."""
        # L1 has 1200 tokens ≈ 4800 chars
        long_text = "x" * 10000
        obs = gc.create_observation(long_text, Tier.L1)
        extracted = gc.extract(obs)
        assert len(extracted) <= 1200 * 4
        assert extracted.endswith("...")

    def test_extract_by_tier(self, gc):
        """Should extract at specified tier."""
        text = "x" * 20000
        obs = gc.create_observation(text, Tier.L7)

        # Extract at lower tier
        extracted = gc.extract_by_tier(obs, Tier.L1)
        assert len(extracted) <= Tier.L1.token_budget * 4

    def test_duplicate(self, gc):
        """Duplicate should create meta-observation."""
        obs = gc.create_observation("result", Tier.L4)
        dup = gc.duplicate(obs)

        assert isinstance(dup.current, GradedObservation)
        assert dup.grade == Tier.L4
        assert dup.context['meta_observation'] is True

    def test_duplicate_preserves_grade(self, gc):
        """Duplicate should preserve grade."""
        for tier in Tier:
            obs = gc.create_observation("test", tier)
            dup = gc.duplicate(obs)
            assert dup.grade == tier

    def test_duplicate_split(self, gc):
        """Should split grades correctly."""
        obs = gc.create_observation("result", Tier.L5)
        split = gc.duplicate_split(obs, Tier.L5, Tier.L3)

        assert split.grade == Tier.L5  # outer
        assert split.current.grade == Tier.L3  # inner

    def test_duplicate_split_invalid_composition(self, gc):
        """Should reject invalid grade compositions."""
        obs = gc.create_observation("result", Tier.L3)

        # L5 • L5 = L5 ≠ L3
        with pytest.raises(ValueError):
            gc.duplicate_split(obs, Tier.L5, Tier.L5)

    def test_extend(self, gc):
        """Extend should apply function with context."""
        obs = gc.create_observation("hello", Tier.L3)

        def uppercase_with_context(w):
            return f"{w.current.upper()} (grade: {w.grade.name})"

        result = gc.extend(uppercase_with_context, obs)
        assert result.current == "HELLO (grade: L3)"
        assert result.grade == Tier.L3

    def test_extend_preserves_grade(self, gc):
        """Extend should preserve grade."""
        obs = gc.create_observation("test", Tier.L5)
        result = gc.extend(lambda w: w.current * 2, obs)
        assert result.grade == Tier.L5


class TestGradeUpgradeDowngrade:
    """Tests for upgrade/downgrade operations."""

    @pytest.fixture
    def gc(self):
        return create_graded_comonad()

    def test_upgrade(self, gc):
        """Should upgrade to higher tier."""
        obs = gc.create_observation("result", Tier.L2)
        upgraded = gc.upgrade(obs, Tier.L5)

        assert upgraded.grade == Tier.L5
        assert upgraded.current == obs.current
        assert upgraded.context['upgraded_from'] == 'L2'

    def test_upgrade_rejects_lower_tier(self, gc):
        """Should reject upgrade to lower tier."""
        obs = gc.create_observation("result", Tier.L5)
        with pytest.raises(ValueError):
            gc.upgrade(obs, Tier.L2)

    def test_downgrade(self, gc):
        """Should downgrade to lower tier."""
        obs = gc.create_observation("result", Tier.L5)
        downgraded = gc.downgrade(obs, Tier.L2)

        assert downgraded.grade == Tier.L2
        assert downgraded.context['downgraded_from'] == 'L5'

    def test_downgrade_truncates(self, gc):
        """Should truncate on downgrade if needed."""
        long_text = "x" * 50000
        obs = gc.create_observation(long_text, Tier.L7, tokens_used=12000)
        downgraded = gc.downgrade(obs, Tier.L1)

        assert downgraded.tokens_used <= Tier.L1.token_budget

    def test_downgrade_rejects_higher_tier(self, gc):
        """Should reject downgrade to higher tier."""
        obs = gc.create_observation("result", Tier.L2)
        with pytest.raises(ValueError):
            gc.downgrade(obs, Tier.L5)

    def test_upgrade_downgrade_roundtrip(self, gc):
        """Upgrade then downgrade should approximately restore."""
        obs = gc.create_observation("short text", Tier.L3, tokens_used=100)
        upgraded = gc.upgrade(obs, Tier.L6)
        restored = gc.downgrade(upgraded, Tier.L3)

        assert restored.grade == obs.grade
        assert restored.current == obs.current


class TestGradeLaws:
    """Tests for categorical graded comonad laws."""

    @pytest.fixture
    def gc(self):
        return create_graded_comonad()

    def test_grade_preservation_law(self, gc):
        """Extract should respect grade bounds."""
        for tier in Tier:
            obs = gc.create_observation("test content", tier)
            assert gc.verify_grade_preservation(obs)

    def test_grade_preservation_with_long_text(self, gc):
        """Grade preservation should hold for long text."""
        long_text = "x" * 100000
        for tier in Tier:
            obs = gc.create_observation(long_text, tier)
            assert gc.verify_grade_preservation(obs)

    def test_upgrade_downgrade_inverse_law(self, gc):
        """Upgrade/downgrade should be partial inverses."""
        obs = gc.create_observation("short text", Tier.L3)
        assert gc.verify_upgrade_downgrade_inverse(obs, Tier.L6)


class TestTierInference:
    """Tests for tier inference functions."""

    def test_infer_tier_from_complexity(self):
        """Should map complexity to appropriate tier."""
        assert infer_tier_from_complexity(0.0) == Tier.L1
        assert infer_tier_from_complexity(0.10) == Tier.L1
        assert infer_tier_from_complexity(0.20) == Tier.L2
        assert infer_tier_from_complexity(0.35) == Tier.L3
        assert infer_tier_from_complexity(0.50) == Tier.L4
        assert infer_tier_from_complexity(0.65) == Tier.L5
        assert infer_tier_from_complexity(0.80) == Tier.L6
        assert infer_tier_from_complexity(0.95) == Tier.L7

    def test_infer_tier_from_tokens(self):
        """Should find minimum tier for token count."""
        assert infer_tier_from_tokens(500) == Tier.L1
        assert infer_tier_from_tokens(1200) == Tier.L1
        assert infer_tier_from_tokens(1500) == Tier.L2
        assert infer_tier_from_tokens(5000) == Tier.L4
        assert infer_tier_from_tokens(10000) == Tier.L6
        assert infer_tier_from_tokens(20000) == Tier.L7
        assert infer_tier_from_tokens(50000) == Tier.L7  # Exceeds all, use max


class TestIntegrationScenarios:
    """Integration tests for realistic usage scenarios."""

    @pytest.fixture
    def gc(self):
        return create_graded_comonad()

    def test_rmp_iteration_with_grade_tracking(self, gc):
        """Simulate RMP iteration tracking grade consumption."""
        # Start at L4
        initial = gc.create_observation(
            "Initial prompt analysis",
            Tier.L4,
            tokens_used=500
        )

        # Iteration 1: extend with refinement
        def refine(w):
            return f"Refined: {w.current} (iteration 1)"

        iter1 = gc.extend(refine, initial)
        assert iter1.grade == Tier.L4

        # Iteration 2: need more context, upgrade
        upgraded = gc.upgrade(iter1, Tier.L5)
        assert upgraded.grade == Tier.L5
        assert upgraded.tokens_remaining > iter1.tokens_remaining

    def test_multi_agent_grade_coordination(self, gc):
        """Simulate multi-agent scenario with different grades."""
        # Agent 1: Simple task at L2
        agent1_obs = gc.create_observation(
            "Simple analysis result",
            Tier.L2,
            tokens_used=800
        )

        # Agent 2: Complex task at L5
        agent2_obs = gc.create_observation(
            "Complex synthesis result",
            Tier.L5,
            tokens_used=4000
        )

        # Coordinator: Combine at highest grade
        combined_grade = agent1_obs.grade * agent2_obs.grade
        assert combined_grade == Tier.L5

        coordinator_obs = gc.create_observation(
            f"Combined: {agent1_obs.current} + {agent2_obs.current}",
            combined_grade,
            tokens_used=agent1_obs.tokens_used + agent2_obs.tokens_used
        )

        assert coordinator_obs.grade == Tier.L5
        assert coordinator_obs.tokens_used == 4800

    def test_context_extraction_with_history(self, gc):
        """Test context extraction across observation history."""
        obs1 = gc.create_observation("Step 1", Tier.L3, tokens_used=100)
        obs2 = GradedObservation(
            current="Step 2",
            grade=Tier.L3,
            history=[obs1],
            tokens_used=200
        )
        obs3 = GradedObservation(
            current="Step 3",
            grade=Tier.L3,
            history=[obs2, obs1],
            tokens_used=300
        )

        # Duplicate gives access to full history
        meta = gc.duplicate(obs3)
        assert len(meta.history) >= 1
        assert meta.current.current == "Step 3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
