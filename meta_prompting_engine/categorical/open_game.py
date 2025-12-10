"""
Open Game: Compositional Game Theory for Prompt-Response

Open games model bidirectional information flow in strategic interactions.
In meta-prompting, we model the prompt-response loop as a game where:
- The user plays prompts (strategy)
- The model plays responses (counter-strategy)
- Quality is the coutility (value flowing back to user)

Mathematical Definition:
    An open game G: X → Y consists of:
    - Play: X × Σ → Y (forward computation)
    - Coplay: X × Σ × R → R' (backward utility propagation)

    Where:
    - X = input context
    - Y = output
    - Σ = strategy space
    - R = coutility (reward from continuation)
    - R' = total coutility

Composition:
    Games compose via tensor (parallel) and sequence:
    - G ⊗ H: Run games in parallel, combine coutility
    - G ; H: Chain output of G to input of H

Applications in Meta-Prompting:
    1. RMP as equilibrium-seeking: Iterate until coutility stabilizes
    2. Quality as coutility: Quality score flows backward
    3. Strategy refinement: Improve prompt strategy based on feedback
    4. Multi-agent coordination: Compose agent games

References:
    - arXiv:1603.04641 - Game Semantics meets Game Theory
    - arXiv:1711.07059 - Morphisms of Open Games
    - arXiv:1910.03656 - Bayesian Open Games
    - Hedges (2018) - Compositional Game Theory

Example:
    >>> game = PromptResponseGame()
    >>> result = game.play("Write code", strategy={"style": "detailed"})
    >>> refined = game.seek_equilibrium(context, threshold=0.85)
"""

from typing import TypeVar, Callable, Generic, Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum


# Type variables
X = TypeVar('X')  # Input/Context
Y = TypeVar('Y')  # Output
Sigma = TypeVar('Sigma')  # Strategy
R = TypeVar('R')  # Coutility (reward)


class GameStatus(Enum):
    """Status of game execution."""
    PLAYING = "playing"
    EQUILIBRIUM = "equilibrium"
    MAX_ITERATIONS = "max_iterations"
    DIVERGING = "diverging"
    HALTED = "halted"


@dataclass
class GameResult(Generic[Y]):
    """
    Result of playing an open game.

    Attributes:
        output: The game output (response)
        coutility: Quality/reward value [0, 1]
        strategy_used: The strategy that produced this result
        iterations: Number of iterations to reach result
        status: Game status
        history: History of (output, coutility) pairs
    """
    output: Y
    coutility: float
    strategy_used: Dict[str, Any]
    iterations: int
    status: GameStatus
    history: List[Tuple[Any, float]] = field(default_factory=list)

    def __str__(self) -> str:
        return f"GameResult(coutility={self.coutility:.3f}, status={self.status.value}, iterations={self.iterations})"


@dataclass
class Strategy:
    """
    A strategy in the prompt-response game.

    Attributes:
        name: Strategy identifier
        parameters: Strategy parameters
        priority: Higher priority strategies tried first
    """
    name: str
    parameters: Dict[str, Any]
    priority: int = 0

    def __str__(self) -> str:
        return f"Strategy({self.name}, priority={self.priority})"


class OpenGame(ABC, Generic[X, Y, R]):
    """
    Abstract base class for open games.

    An open game has:
    - play: Forward computation X × Σ → Y
    - coplay: Backward utility propagation X × Σ × R → R'

    The game is "open" because it can compose with other games
    via its input/output interfaces.
    """

    @abstractmethod
    def play(
        self,
        context: X,
        strategy: Strategy
    ) -> Y:
        """
        Forward play: Generate output from context and strategy.

        Args:
            context: Input context
            strategy: Strategy to use

        Returns:
            Output of the game
        """
        pass

    @abstractmethod
    def coplay(
        self,
        context: X,
        strategy: Strategy,
        continuation_coutility: R
    ) -> R:
        """
        Backward coplay: Propagate coutility from continuation.

        Args:
            context: Original input context
            strategy: Strategy used
            continuation_coutility: Coutility from downstream

        Returns:
            Total coutility including this game's contribution
        """
        pass

    def best_response(
        self,
        context: X,
        strategies: List[Strategy],
        evaluate: Callable[[Y], float]
    ) -> Tuple[Strategy, Y, float]:
        """
        Find best responding strategy.

        Args:
            context: Input context
            strategies: Available strategies
            evaluate: Function to evaluate outputs

        Returns:
            (best_strategy, output, coutility)
        """
        best_strategy = None
        best_output = None
        best_coutility = -float('inf')

        for strategy in sorted(strategies, key=lambda s: -s.priority):
            output = self.play(context, strategy)
            coutility = evaluate(output)

            if coutility > best_coutility:
                best_coutility = coutility
                best_strategy = strategy
                best_output = output

        return best_strategy, best_output, best_coutility


@dataclass
class PromptResponseGame(OpenGame[str, str, float]):
    """
    Open game modeling prompt-response interaction.

    The user's strategy determines prompt style/content.
    The model responds, and quality flows back as coutility.

    Attributes:
        model_fn: Function that generates responses (simulated LLM)
        quality_fn: Function that assesses response quality
        default_strategies: Available prompt strategies
    """

    model_fn: Callable[[str], str] = None
    quality_fn: Callable[[str, str], float] = None
    default_strategies: List[Strategy] = field(default_factory=list)

    def __post_init__(self):
        if self.model_fn is None:
            self.model_fn = self._default_model
        if self.quality_fn is None:
            self.quality_fn = self._default_quality
        if not self.default_strategies:
            self.default_strategies = self._default_strategies()

    def play(
        self,
        context: str,
        strategy: Strategy
    ) -> str:
        """
        Generate response using strategy.

        Args:
            context: Task/prompt context
            strategy: Prompt strategy

        Returns:
            Model response
        """
        # Apply strategy to construct prompt
        prompt = self._apply_strategy(context, strategy)

        # Get model response
        response = self.model_fn(prompt)

        return response

    def coplay(
        self,
        context: str,
        strategy: Strategy,
        continuation_coutility: float
    ) -> float:
        """
        Propagate quality as coutility.

        Args:
            context: Original context
            strategy: Strategy used
            continuation_coutility: Downstream quality

        Returns:
            Combined coutility
        """
        # In simple case, just return continuation coutility
        # More complex games might modify based on strategy cost
        strategy_cost = strategy.parameters.get("cost", 0.0)
        return continuation_coutility - strategy_cost

    def play_and_evaluate(
        self,
        context: str,
        strategy: Strategy
    ) -> Tuple[str, float]:
        """
        Play game and evaluate result.

        Args:
            context: Task context
            strategy: Strategy to use

        Returns:
            (response, quality)
        """
        response = self.play(context, strategy)
        quality = self.quality_fn(context, response)
        return response, quality

    def seek_equilibrium(
        self,
        context: str,
        threshold: float = 0.85,
        max_iterations: int = 10,
        strategies: Optional[List[Strategy]] = None
    ) -> GameResult[str]:
        """
        Iterate until quality equilibrium is reached.

        This models RMP as equilibrium-seeking in a game.

        Args:
            context: Initial task context
            threshold: Quality threshold for equilibrium
            max_iterations: Maximum iterations
            strategies: Strategies to try (uses defaults if None)

        Returns:
            GameResult with final response and status
        """
        strategies = strategies or self.default_strategies
        history = []
        best_result = None
        best_quality = 0.0

        current_context = context
        current_strategy = strategies[0] if strategies else Strategy("default", {})

        for i in range(max_iterations):
            # Play current strategy
            response, quality = self.play_and_evaluate(current_context, current_strategy)
            history.append((response, quality))

            # Track best
            if quality > best_quality:
                best_quality = quality
                best_result = response

            # Check equilibrium
            if quality >= threshold:
                return GameResult(
                    output=response,
                    coutility=quality,
                    strategy_used=current_strategy.parameters,
                    iterations=i + 1,
                    status=GameStatus.EQUILIBRIUM,
                    history=history
                )

            # Check for divergence (quality getting worse)
            if len(history) >= 3:
                recent_qualities = [h[1] for h in history[-3:]]
                if all(q < recent_qualities[0] for q in recent_qualities[1:]):
                    return GameResult(
                        output=best_result,
                        coutility=best_quality,
                        strategy_used=current_strategy.parameters,
                        iterations=i + 1,
                        status=GameStatus.DIVERGING,
                        history=history
                    )

            # Refine strategy based on feedback
            current_strategy = self._refine_strategy(
                current_strategy,
                response,
                quality,
                strategies
            )

            # Update context with response for next iteration
            current_context = self._update_context(context, response, quality)

        # Max iterations reached
        return GameResult(
            output=best_result or response,
            coutility=best_quality,
            strategy_used=current_strategy.parameters,
            iterations=max_iterations,
            status=GameStatus.MAX_ITERATIONS,
            history=history
        )

    def _apply_strategy(self, context: str, strategy: Strategy) -> str:
        """Apply strategy to create prompt."""
        style = strategy.parameters.get("style", "standard")
        prefix = strategy.parameters.get("prefix", "")
        suffix = strategy.parameters.get("suffix", "")

        if style == "detailed":
            prompt = f"{prefix}Please provide a detailed solution:\n{context}\n{suffix}"
        elif style == "concise":
            prompt = f"{prefix}Briefly: {context}{suffix}"
        elif style == "step_by_step":
            prompt = f"{prefix}Step by step:\n{context}\n{suffix}"
        elif style == "expert":
            prompt = f"{prefix}As an expert, {context}\n{suffix}"
        else:
            prompt = f"{prefix}{context}{suffix}"

        return prompt.strip()

    def _refine_strategy(
        self,
        current: Strategy,
        response: str,
        quality: float,
        available: List[Strategy]
    ) -> Strategy:
        """Refine strategy based on feedback."""
        # Try next strategy if quality is low
        if quality < 0.5:
            # Find next strategy by priority
            current_idx = -1
            for i, s in enumerate(available):
                if s.name == current.name:
                    current_idx = i
                    break

            if current_idx >= 0 and current_idx < len(available) - 1:
                return available[current_idx + 1]

        # Otherwise adjust current strategy parameters
        new_params = dict(current.parameters)

        # Add more detail if quality is moderate
        if 0.5 <= quality < 0.7:
            new_params["prefix"] = new_params.get("prefix", "") + "Be more specific. "

        # Request structured output if still not great
        if 0.7 <= quality < 0.85:
            new_params["suffix"] = "\nProvide a structured answer."

        return Strategy(current.name + "_refined", new_params, current.priority + 1)

    def _update_context(self, original: str, response: str, quality: float) -> str:
        """Update context with previous response for next iteration."""
        return f"{original}\n\nPrevious attempt (quality {quality:.2f}):\n{response}\n\nPlease improve upon this."

    def _default_model(self, prompt: str) -> str:
        """Default model: echo with transformation."""
        # Simple simulation - in production, call actual LLM
        words = prompt.split()
        return f"Response to: {' '.join(words[:10])}..."

    def _default_quality(self, context: str, response: str) -> float:
        """Default quality: length-based heuristic."""
        # Simple heuristic - in production, use actual quality assessment
        if not response:
            return 0.0

        # Longer responses generally better (up to a point)
        length_score = min(len(response) / 500, 1.0) * 0.4

        # Contains context keywords
        context_words = set(context.lower().split())
        response_words = set(response.lower().split())
        overlap = len(context_words & response_words) / max(len(context_words), 1)
        relevance_score = overlap * 0.4

        # Structured (has newlines, bullet points)
        structure_score = 0.2 if '\n' in response or '-' in response else 0.0

        return min(length_score + relevance_score + structure_score, 1.0)

    def _default_strategies(self) -> List[Strategy]:
        """Default prompt strategies."""
        return [
            Strategy("standard", {"style": "standard"}, priority=0),
            Strategy("detailed", {"style": "detailed"}, priority=1),
            Strategy("step_by_step", {"style": "step_by_step"}, priority=2),
            Strategy("expert", {"style": "expert"}, priority=3),
        ]


@dataclass
class ComposedGame(OpenGame[X, Y, R]):
    """
    Composition of two open games.

    Supports:
    - Sequential: G ; H (output of G feeds into H)
    - Parallel: G ⊗ H (run both, combine coutility)
    """

    game1: OpenGame
    game2: OpenGame
    composition_type: str = "sequential"  # or "parallel"

    def play(self, context: X, strategy: Strategy) -> Y:
        """Play composed game."""
        if self.composition_type == "sequential":
            # G ; H: output of G feeds H
            intermediate = self.game1.play(context, strategy)
            return self.game2.play(intermediate, strategy)
        else:
            # G ⊗ H: parallel play
            out1 = self.game1.play(context, strategy)
            out2 = self.game2.play(context, strategy)
            return (out1, out2)

    def coplay(
        self,
        context: X,
        strategy: Strategy,
        continuation_coutility: R
    ) -> R:
        """Propagate coutility through composition."""
        if self.composition_type == "sequential":
            # Propagate backward: H then G
            intermediate_coutility = self.game2.coplay(
                context, strategy, continuation_coutility
            )
            return self.game1.coplay(context, strategy, intermediate_coutility)
        else:
            # Parallel: combine coutilities
            cout1 = self.game1.coplay(context, strategy, continuation_coutility)
            cout2 = self.game2.coplay(context, strategy, continuation_coutility)
            # Combine via mean (could use other aggregation)
            return (cout1 + cout2) / 2


# === Factory Functions ===

def create_prompt_game(
    model_fn: Optional[Callable[[str], str]] = None,
    quality_fn: Optional[Callable[[str, str], float]] = None
) -> PromptResponseGame:
    """
    Factory for creating prompt-response games.

    Args:
        model_fn: Function to generate responses
        quality_fn: Function to assess quality

    Returns:
        PromptResponseGame instance
    """
    return PromptResponseGame(model_fn=model_fn, quality_fn=quality_fn)


def compose_games(
    game1: OpenGame,
    game2: OpenGame,
    sequential: bool = True
) -> ComposedGame:
    """
    Compose two open games.

    Args:
        game1: First game
        game2: Second game
        sequential: If True, G;H. If False, G⊗H

    Returns:
        ComposedGame
    """
    return ComposedGame(
        game1=game1,
        game2=game2,
        composition_type="sequential" if sequential else "parallel"
    )


def run_rmp_as_game(
    task: str,
    threshold: float = 0.85,
    max_iterations: int = 5,
    model_fn: Optional[Callable[[str], str]] = None
) -> GameResult[str]:
    """
    Run RMP iteration as equilibrium-seeking game.

    Convenience function for treating RMP as a game.

    Args:
        task: Task description
        threshold: Quality threshold
        max_iterations: Max iterations
        model_fn: Optional model function

    Returns:
        GameResult with final output
    """
    game = create_prompt_game(model_fn=model_fn)
    return game.seek_equilibrium(task, threshold, max_iterations)
