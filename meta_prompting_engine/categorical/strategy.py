"""
Strategy selection for meta-prompting based on task complexity.

Implements complexity-based strategy selection for the F: Tasks → Prompts
functor object mapping.
"""

from .types import Strategy, StrategyType


def select_strategy(complexity: float) -> Strategy:
    """
    Select meta-prompting strategy based on task complexity.

    Strategy Selection Rules:
    - complexity < 0.3  → DIRECT_EXECUTION
    - 0.3 ≤ complexity < 0.7 → MULTI_APPROACH
    - complexity ≥ 0.7  → AUTONOMOUS_EVOLUTION

    Args:
        complexity: Task complexity [0.0, 1.0]

    Returns:
        Strategy with appropriate template and parameters

    Example:
        >>> strategy = select_strategy(0.25)
        >>> assert strategy.name == StrategyType.DIRECT_EXECUTION
        >>> assert strategy.max_iterations == 1
    """
    if complexity < 0.3:
        return _direct_execution_strategy()
    elif complexity < 0.7:
        return _multi_approach_strategy()
    else:
        return _autonomous_evolution_strategy()


def _direct_execution_strategy() -> Strategy:
    """
    Direct execution strategy for low-complexity tasks.

    Characteristics:
    - Single-pass execution
    - Minimal meta-cognitive overhead
    - Direct problem-solving approach

    Suitable for:
    - Simple retrieval tasks
    - Basic calculations
    - Straightforward transformations

    Returns:
        Direct execution strategy
    """
    template = """You are an expert problem solver. Solve the following task directly and concisely.

Task: {description}

Provide a clear, direct solution."""

    return Strategy(
        name=StrategyType.DIRECT_EXECUTION,
        template=template,
        max_iterations=1,
        quality_threshold=0.80
    )


def _multi_approach_strategy() -> Strategy:
    """
    Multi-approach synthesis strategy for medium-complexity tasks.

    Characteristics:
    - Generate multiple solution approaches
    - Evaluate and synthesize best elements
    - 2-3 meta-prompting iterations

    Suitable for:
    - Problems with multiple valid approaches
    - Tasks requiring trade-off analysis
    - Medium algorithmic complexity

    Returns:
        Multi-approach strategy
    """
    template = """You are an expert problem solver with meta-cognitive awareness.

Task: {description}

Approach this problem systematically:
1. **Analyze**: Break down the task into key components
2. **Explore**: Consider 2-3 different solution approaches
3. **Evaluate**: Compare approaches based on:
   - Correctness
   - Efficiency
   - Clarity
4. **Synthesize**: Combine the best elements into a final solution

Provide your analysis and final solution."""

    return Strategy(
        name=StrategyType.MULTI_APPROACH,
        template=template,
        max_iterations=3,
        quality_threshold=0.85
    )


def _autonomous_evolution_strategy() -> Strategy:
    """
    Autonomous evolution strategy for high-complexity tasks.

    Characteristics:
    - Self-reflective reasoning
    - Iterative refinement through meta-prompting
    - Adaptive approach based on intermediate results
    - Up to 5 meta-prompting iterations

    Suitable for:
    - Complex optimization problems
    - Open-ended research tasks
    - Problems requiring domain expertise

    Returns:
        Autonomous evolution strategy
    """
    template = """You are an advanced AI system with meta-cognitive capabilities and deep domain expertise.

Task: {description}

Apply autonomous reasoning through iterative refinement:

**Phase 1: Deep Analysis**
- Identify core problem structure
- Map to known problem classes
- Assess computational complexity
- Determine required domain knowledge

**Phase 2: Strategy Formation**
- Generate multiple solution hypotheses
- Identify potential failure modes
- Design validation criteria

**Phase 3: Implementation**
- Implement most promising approach
- Monitor for edge cases
- Adapt strategy based on intermediate results

**Phase 4: Meta-Reflection**
- Evaluate solution quality
- Identify potential improvements
- Consider alternative framings

**Phase 5: Synthesis**
- Integrate insights from all phases
- Provide final solution with confidence assessment

Provide detailed reasoning at each phase and your final solution."""

    return Strategy(
        name=StrategyType.AUTONOMOUS_EVOLUTION,
        template=template,
        max_iterations=5,
        quality_threshold=0.90
    )
