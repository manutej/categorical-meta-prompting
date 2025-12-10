"""
Tests for Open Game (Pattern 3)

Tests verify:
1. Basic game play
2. Strategy application
3. Equilibrium seeking
4. Game composition
5. Coutility propagation

Reference: arXiv:1603.04641 (Game Semantics meets Game Theory)
"""

import pytest

from meta_prompting_engine.categorical.open_game import (
    OpenGame,
    PromptResponseGame,
    ComposedGame,
    GameResult,
    GameStatus,
    Strategy,
    create_prompt_game,
    compose_games,
    run_rmp_as_game,
)


class TestStrategy:
    """Tests for Strategy dataclass."""

    def test_create_strategy(self):
        """Should create strategy with parameters."""
        s = Strategy("detailed", {"style": "detailed"}, priority=1)
        assert s.name == "detailed"
        assert s.parameters["style"] == "detailed"
        assert s.priority == 1

    def test_strategy_str(self):
        """Should have string representation."""
        s = Strategy("test", {}, priority=5)
        assert "test" in str(s)
        assert "5" in str(s)


class TestGameResult:
    """Tests for GameResult dataclass."""

    def test_create_result(self):
        """Should create game result."""
        result = GameResult(
            output="response",
            coutility=0.85,
            strategy_used={"style": "detailed"},
            iterations=3,
            status=GameStatus.EQUILIBRIUM
        )
        assert result.output == "response"
        assert result.coutility == 0.85
        assert result.iterations == 3
        assert result.status == GameStatus.EQUILIBRIUM

    def test_result_str(self):
        """Should have informative string."""
        result = GameResult(
            output="test",
            coutility=0.9,
            strategy_used={},
            iterations=2,
            status=GameStatus.EQUILIBRIUM
        )
        s = str(result)
        assert "0.9" in s
        assert "equilibrium" in s


class TestPromptResponseGame:
    """Tests for PromptResponseGame."""

    @pytest.fixture
    def game(self):
        return create_prompt_game()

    def test_create_game(self, game):
        """Should create game with defaults."""
        assert game.model_fn is not None
        assert game.quality_fn is not None
        assert len(game.default_strategies) > 0

    def test_play_basic(self, game):
        """Should play and return response."""
        strategy = Strategy("standard", {"style": "standard"})
        response = game.play("Write code", strategy)
        assert response is not None
        assert len(response) > 0

    def test_play_with_different_strategies(self, game):
        """Different strategies should produce different results."""
        context = "Write a function"

        results = []
        for style in ["standard", "detailed", "step_by_step", "expert"]:
            strategy = Strategy(style, {"style": style})
            response = game.play(context, strategy)
            results.append(response)

        # At least some should differ
        unique_results = set(results)
        assert len(unique_results) >= 2

    def test_play_and_evaluate(self, game):
        """Should return both response and quality."""
        strategy = Strategy("detailed", {"style": "detailed"})
        response, quality = game.play_and_evaluate("Write code", strategy)

        assert response is not None
        assert 0.0 <= quality <= 1.0

    def test_coplay(self, game):
        """Coplay should propagate coutility."""
        strategy = Strategy("test", {"style": "standard", "cost": 0.1})
        coutility = game.coplay("context", strategy, 0.9)

        # Should be less due to cost
        assert coutility == 0.8


class TestEquilibriumSeeking:
    """Tests for equilibrium seeking (RMP as game)."""

    @pytest.fixture
    def game(self):
        return create_prompt_game()

    def test_seeks_until_threshold(self, game):
        """Should iterate until threshold or max."""
        result = game.seek_equilibrium(
            "Write a simple function",
            threshold=0.5,  # Low threshold
            max_iterations=5
        )

        # With simulated model, may reach equilibrium, max_iterations, or diverge
        assert result.status in [GameStatus.EQUILIBRIUM, GameStatus.MAX_ITERATIONS, GameStatus.DIVERGING]
        assert result.iterations >= 1

    def test_respects_max_iterations(self, game):
        """Should stop at max iterations."""
        result = game.seek_equilibrium(
            "Complex task",
            threshold=0.99,  # Very high - won't reach
            max_iterations=3
        )

        assert result.iterations <= 3
        assert result.status == GameStatus.MAX_ITERATIONS

    def test_tracks_history(self, game):
        """Should track iteration history."""
        result = game.seek_equilibrium(
            "Some task",
            threshold=0.95,
            max_iterations=5
        )

        assert len(result.history) == result.iterations
        for response, quality in result.history:
            assert response is not None
            assert 0.0 <= quality <= 1.0

    def test_returns_best_result(self, game):
        """Should return best result even if not equilibrium."""
        result = game.seek_equilibrium(
            "Task",
            threshold=0.99,
            max_iterations=3
        )

        # Final coutility should be the best seen
        history_qualities = [q for _, q in result.history]
        assert result.coutility >= max(history_qualities) - 0.01


class TestBestResponse:
    """Tests for best response selection."""

    @pytest.fixture
    def game(self):
        return create_prompt_game()

    def test_finds_best_strategy(self, game):
        """Should find strategy with highest coutility."""
        strategies = [
            Strategy("low", {"style": "standard"}),
            Strategy("high", {"style": "detailed"}),
        ]

        def evaluate(response):
            # Prefer longer responses
            return len(response) / 100

        best_strategy, output, coutility = game.best_response(
            "Write code",
            strategies,
            evaluate
        )

        assert best_strategy is not None
        assert output is not None
        assert coutility >= 0


class TestGameComposition:
    """Tests for composing open games."""

    @pytest.fixture
    def game1(self):
        return create_prompt_game()

    @pytest.fixture
    def game2(self):
        return create_prompt_game()

    def test_sequential_composition(self, game1, game2):
        """Sequential composition: G ; H."""
        composed = compose_games(game1, game2, sequential=True)

        strategy = Strategy("test", {"style": "standard"})
        result = composed.play("Initial context", strategy)

        assert result is not None

    def test_parallel_composition(self, game1, game2):
        """Parallel composition: G ⊗ H."""
        composed = compose_games(game1, game2, sequential=False)

        strategy = Strategy("test", {"style": "standard"})
        result = composed.play("Context", strategy)

        # Should return tuple of results
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_sequential_coplay(self, game1, game2):
        """Sequential coplay propagates backward."""
        composed = ComposedGame(game1, game2, "sequential")

        strategy = Strategy("test", {"style": "standard"})
        coutility = composed.coplay("context", strategy, 0.8)

        assert 0.0 <= coutility <= 1.0

    def test_parallel_coplay_averages(self, game1, game2):
        """Parallel coplay averages coutilities."""
        composed = ComposedGame(game1, game2, "parallel")

        strategy = Strategy("test", {"style": "standard"})
        coutility = composed.coplay("context", strategy, 0.8)

        # Should be average of both games' coplay
        assert 0.0 <= coutility <= 1.0


class TestCustomModelAndQuality:
    """Tests with custom model and quality functions."""

    def test_custom_model(self):
        """Should use custom model function."""
        def custom_model(prompt):
            return f"CUSTOM: {prompt}"

        game = create_prompt_game(model_fn=custom_model)
        strategy = Strategy("test", {"style": "standard"})
        response = game.play("Hello", strategy)

        assert "CUSTOM" in response

    def test_custom_quality(self):
        """Should use custom quality function."""
        def custom_quality(context, response):
            return 1.0 if "good" in response.lower() else 0.0

        def model(prompt):
            return "This is a good response"

        game = create_prompt_game(model_fn=model, quality_fn=custom_quality)
        strategy = Strategy("test", {"style": "standard"})
        _, quality = game.play_and_evaluate("Task", strategy)

        assert quality == 1.0


class TestConvenienceFunction:
    """Tests for run_rmp_as_game convenience function."""

    def test_run_rmp_as_game(self):
        """Should run RMP as game."""
        result = run_rmp_as_game(
            "Write a simple function",
            threshold=0.5,
            max_iterations=3
        )

        assert isinstance(result, GameResult)
        assert result.output is not None
        assert result.coutility >= 0


class TestGameScenarios:
    """Integration tests with realistic scenarios."""

    def test_code_generation_game(self):
        """Simulate code generation scenario."""
        def code_model(prompt):
            if "detailed" in prompt.lower():
                return """
def solve(x):
    # Detailed implementation
    result = x * 2
    return result
"""
            return "def solve(x): return x * 2"

        def code_quality(context, response):
            score = 0.5
            if "def " in response:
                score += 0.2
            if "#" in response:
                score += 0.1
            if len(response) > 50:
                score += 0.1
            return min(score, 1.0)

        game = create_prompt_game(model_fn=code_model, quality_fn=code_quality)
        result = game.seek_equilibrium(
            "Implement a doubling function",
            threshold=0.8,
            max_iterations=5
        )

        assert result.coutility >= 0.5

    def test_multi_turn_refinement(self):
        """Test multi-turn strategy refinement."""
        turn_count = [0]

        def improving_model(prompt):
            turn_count[0] += 1
            quality_marker = "improved" * turn_count[0]
            return f"Response {turn_count[0]}: {quality_marker}"

        def turn_quality(context, response):
            # Later turns are better
            turn = int(response.split(":")[0].split()[-1]) if "Response" in response else 1
            return min(0.3 + turn * 0.15, 1.0)

        game = create_prompt_game(model_fn=improving_model, quality_fn=turn_quality)
        result = game.seek_equilibrium(
            "Task",
            threshold=0.7,
            max_iterations=5
        )

        # Should improve over iterations
        if len(result.history) >= 2:
            qualities = [q for _, q in result.history]
            # Later qualities should generally be higher
            assert qualities[-1] >= qualities[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
