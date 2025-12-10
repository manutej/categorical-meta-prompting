"""
Tests for Enriched Magnitude (Pattern 10)

Tests verify:
1. Basic magnitude computation
2. Diversity scoring
3. Redundancy detection
4. Incremental updates
5. Diverse subset selection

Reference: arXiv:2501.06662 (Magnitude of Categories of Texts)
"""

import pytest
import math

from meta_prompting_engine.categorical.enriched_magnitude import (
    EnrichedMagnitude,
    MagnitudeResult,
    create_magnitude_computer,
    compute_prompt_magnitude,
    assess_prompt_diversity,
    cosine_distance,
    ngram_distance,
)


class TestMagnitudeBasics:
    """Tests for basic magnitude computation."""

    @pytest.fixture
    def mag(self):
        return EnrichedMagnitude()

    def test_empty_set_magnitude(self, mag):
        """Empty set should have magnitude 0."""
        result = mag.compute([])
        assert result.value == 0.0
        assert result.diversity_score == 0.0

    def test_single_item_magnitude(self, mag):
        """Single item should have magnitude 1."""
        result = mag.compute(["hello"])
        assert result.value == 1.0
        assert result.diversity_score == 1.0

    def test_identical_items_low_magnitude(self, mag):
        """Identical items should have magnitude close to 1."""
        result = mag.compute(["hello", "hello", "hello"])
        # Identical items collapse to effectively one
        assert result.value < 1.5

    def test_distinct_items_high_magnitude(self, mag):
        """Completely different items should have high magnitude."""
        items = [
            "abcdefgh",
            "ijklmnop",
            "qrstuvwx",
            "yz123456"
        ]
        result = mag.compute(items)
        # Should be close to item count
        assert result.value >= 3.0

    def test_magnitude_bounded_by_cardinality(self, mag):
        """Magnitude should be ≤ cardinality."""
        items = ["a", "b", "c", "d", "e"]
        result = mag.compute(items)
        assert result.value <= len(items) + 0.1  # Small tolerance

    def test_magnitude_at_least_one(self, mag):
        """Non-empty magnitude should be ≥ 1."""
        for n in range(1, 5):
            items = [f"item_{i}" for i in range(n)]
            result = mag.compute(items)
            assert result.value >= 0.99  # Small tolerance


class TestDiversityScoring:
    """Tests for diversity metrics."""

    @pytest.fixture
    def mag(self):
        return EnrichedMagnitude()

    def test_diversity_score_range(self, mag):
        """Diversity score should be in [0, 1]."""
        for items in [
            ["a"],
            ["a", "b"],
            ["a", "a", "a"],
            ["x", "y", "z", "w"],
        ]:
            result = mag.compute(items)
            assert 0.0 <= result.diversity_score <= 1.0

    def test_high_diversity_score(self, mag):
        """Distinct items should have high diversity."""
        items = ["alpha", "beta", "gamma", "delta"]
        result = mag.compute(items)
        assert result.diversity_score >= 0.6

    def test_low_diversity_score(self, mag):
        """Similar items should have low diversity."""
        items = ["hello", "hallo", "hullo", "heelo"]
        result = mag.compute(items)
        assert result.diversity_score <= 0.5


class TestRedundancyDetection:
    """Tests for redundancy pair detection."""

    @pytest.fixture
    def mag(self):
        return EnrichedMagnitude()

    def test_no_redundancy_distinct_items(self, mag):
        """Distinct items should have no redundancy."""
        items = ["abcdefgh", "ijklmnop", "qrstuvwx"]
        result = mag.compute(items)
        assert len(result.redundancy_pairs) == 0

    def test_detects_redundancy(self, mag):
        """Should detect similar pairs."""
        items = ["hello world", "hello world!", "goodbye world"]
        result = mag.compute(items)
        # First two are very similar
        assert len(result.redundancy_pairs) >= 1

    def test_redundancy_pairs_sorted(self, mag):
        """Redundancy pairs should be sorted by similarity."""
        items = ["a", "a", "b", "b"]
        result = mag.compute(items)
        if len(result.redundancy_pairs) >= 2:
            # Should be descending by similarity
            sims = [p[2] for p in result.redundancy_pairs]
            assert sims == sorted(sims, reverse=True)


class TestIncrementalComputation:
    """Tests for incremental magnitude updates."""

    @pytest.fixture
    def mag(self):
        return EnrichedMagnitude()

    def test_incremental_adds_item(self, mag):
        """Incremental should correctly add item."""
        items = ["a", "b", "c"]
        initial = mag.compute(items)

        updated = mag.compute_incremental(initial, "d", items)
        assert updated.value >= initial.value

    def test_incremental_matches_full(self, mag):
        """Incremental result should match full computation."""
        items = ["a", "b", "c"]
        initial = mag.compute(items)

        # Incremental
        incremental = mag.compute_incremental(initial, "d", items)

        # Full
        full = mag.compute(items + ["d"])

        assert abs(incremental.value - full.value) < 0.01


class TestDiversityContribution:
    """Tests for diversity contribution measurement."""

    @pytest.fixture
    def mag(self):
        return EnrichedMagnitude()

    def test_distinct_item_adds_diversity(self, mag):
        """Distinct item should add positive diversity."""
        existing = ["hello", "world"]
        contribution = mag.diversity_contribution("goodbye", existing)
        assert contribution > 0

    def test_duplicate_adds_little_diversity(self, mag):
        """Similar item should add little diversity."""
        existing = ["hello", "world"]
        contribution = mag.diversity_contribution("hello", existing)
        assert contribution < 0.5

    def test_first_item_contribution(self, mag):
        """First item should contribute 1."""
        contribution = mag.diversity_contribution("anything", [])
        assert contribution == 1.0


class TestDiverseSubsetSelection:
    """Tests for selecting diverse subsets."""

    @pytest.fixture
    def mag(self):
        return EnrichedMagnitude()

    def test_select_all_if_k_large(self, mag):
        """Should return all if k >= len(items)."""
        items = ["a", "b", "c"]
        selected, result = mag.select_diverse_subset(items, 10)
        assert len(selected) == len(items)

    def test_select_k_items(self, mag):
        """Should select exactly k items."""
        items = ["a", "b", "c", "d", "e"]
        k = 3
        selected, result = mag.select_diverse_subset(items, k)
        assert len(selected) == k

    def test_selected_subset_diverse(self, mag):
        """Selected subset should be diverse."""
        items = ["aaa", "aab", "bbb", "bbc", "ccc", "ccd"]
        k = 3
        selected, result = mag.select_diverse_subset(items, k)

        # Selected should be more diverse than random 3
        # At least pick from different groups
        first_chars = set(s[0] for s in selected)
        assert len(first_chars) >= 2


class TestDistanceFunctions:
    """Tests for different distance functions."""

    def test_cosine_distance_identical(self):
        """Identical strings should have zero cosine distance."""
        d = cosine_distance("hello world", "hello world")
        assert d == 0.0

    def test_cosine_distance_different(self):
        """Different strings should have positive distance."""
        d = cosine_distance("hello world", "goodbye moon")
        assert d > 0

    def test_ngram_distance_identical(self):
        """Identical strings should have zero ngram distance."""
        d = ngram_distance("hello", "hello")
        assert d == 0.0

    def test_ngram_distance_different(self):
        """Different strings should have positive distance."""
        d = ngram_distance("hello", "world")
        assert d > 0

    def test_create_magnitude_with_cosine(self):
        """Should create magnitude computer with cosine distance."""
        mag = create_magnitude_computer("cosine")
        result = mag.compute(["hello", "world"])
        assert result.value > 0


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_compute_prompt_magnitude(self):
        """Should compute magnitude directly."""
        prompts = ["prompt one", "prompt two", "prompt three"]
        value = compute_prompt_magnitude(prompts)
        assert value > 0
        assert value <= len(prompts)

    def test_assess_prompt_diversity(self):
        """Should return diversity assessment dict."""
        prompts = ["write code", "debug code", "test code"]
        assessment = assess_prompt_diversity(prompts)

        assert "magnitude" in assessment
        assert "diversity_score" in assessment
        assert "item_count" in assessment
        assert "interpretation" in assessment
        assert assessment["item_count"] == 3


class TestInterpretation:
    """Tests for magnitude interpretation."""

    @pytest.fixture
    def mag(self):
        return EnrichedMagnitude()

    def test_interpretation_exists(self, mag):
        """Should generate interpretation."""
        result = mag.compute(["a", "b", "c"])
        assert result.interpretation is not None
        assert len(result.interpretation) > 0

    def test_interpretation_mentions_diversity(self, mag):
        """Interpretation should mention diversity level."""
        result = mag.compute(["a", "b", "c", "d"])
        interpretation = result.interpretation.lower()
        assert "diversity" in interpretation

    def test_interpretation_includes_stats(self, mag):
        """Interpretation should include magnitude value."""
        result = mag.compute(["x", "y", "z"])
        # Should mention the magnitude number
        assert str(int(result.value)) in result.interpretation or \
               f"{result.value:.2f}" in result.interpretation


class TestPromptScenarios:
    """Integration tests with realistic prompt scenarios."""

    @pytest.fixture
    def mag(self):
        return EnrichedMagnitude()

    def test_code_task_prompts(self, mag):
        """Test with code-related prompts."""
        prompts = [
            "Write a function to sort an array",
            "Implement binary search algorithm",
            "Create a linked list data structure",
            "Build a REST API endpoint",
        ]
        result = mag.compute(prompts)
        # These are distinct tasks, should have good diversity
        assert result.diversity_score >= 0.5

    def test_redundant_prompts(self, mag):
        """Test with redundant prompts."""
        prompts = [
            "Sort the array",
            "Sort this array",
            "Please sort the array",
            "Can you sort the array",
        ]
        result = mag.compute(prompts)
        # These are essentially the same, low diversity
        assert result.diversity_score <= 0.5

    def test_rmp_iteration_prompts(self, mag):
        """Test tracking diversity across RMP iterations."""
        iterations = [
            "Initial prompt for code generation",
            "Refined prompt with more context",
            "Further refined with examples",
            "Final optimized prompt",
        ]

        # Compute magnitude at each step
        magnitudes = []
        for i in range(1, len(iterations) + 1):
            result = mag.compute(iterations[:i])
            magnitudes.append(result.value)

        # Magnitude should generally increase (more iterations = more coverage)
        assert magnitudes[-1] >= magnitudes[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
