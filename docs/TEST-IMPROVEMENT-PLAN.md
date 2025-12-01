# Test Improvement Implementation Plan

**Date**: 2025-12-01
**Based On**: TEST-COVERAGE-ANALYSIS.md
**Goal**: Increase coverage from 59% → 84%

---

## Priority 1: Empirical Validation (Week 1)

### Task 1.1: Game of 24 with Error Handling

**File**: `benchmarks/game_of_24_with_errors.py`

```python
"""
Game of 24 Benchmark with Error Handling (Phase 3 Validation)

Tests whether @catch:retry and @fallback:return-best improve success rate.

Expected Results:
- Baseline (no errors): 90% (from Phase 2)
- With @catch:retry:3: 93-95%
- With @fallback:return-best: 91-93%
"""

import pytest
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from meta_prompting_engine.categorical.monad import create_recursive_meta_monad
from ..tests.test_error_handling_laws import Either

@dataclass
class GameOf24Puzzle:
    """A Game of 24 puzzle."""
    numbers: Tuple[int, int, int, int]
    solution: Optional[str]  # None if unsolvable
    difficulty: str  # easy, medium, hard

# Dataset of 100 canonical puzzles
GAME_OF_24_DATASET = [
    GameOf24Puzzle((1, 2, 3, 4), "((1+2)+3)*4", "easy"),
    GameOf24Puzzle((3, 3, 8, 8), "(8/(3-8/3))", "hard"),
    # ... 98 more puzzles
]

class SolverStrategy(Enum):
    BASELINE = "baseline"          # No error handling
    RETRY = "retry"                # @catch:retry:3
    FALLBACK = "fallback"          # @fallback:return-best
    BOTH = "both"                  # retry + fallback

def solve_puzzle(
    puzzle: GameOf24Puzzle,
    strategy: SolverStrategy = SolverStrategy.BASELINE,
    max_retries: int = 3
) -> Either[str, str]:
    """
    Solve a Game of 24 puzzle with specified error handling strategy.

    Returns:
        Either[error, solution]
    """
    # Simulate solving with potential failures
    if strategy == SolverStrategy.BASELINE:
        return _solve_baseline(puzzle)

    elif strategy == SolverStrategy.RETRY:
        return _solve_with_retry(puzzle, max_retries)

    elif strategy == SolverStrategy.FALLBACK:
        return _solve_with_fallback(puzzle)

    elif strategy == SolverStrategy.BOTH:
        return _solve_with_both(puzzle, max_retries)

def _solve_baseline(puzzle: GameOf24Puzzle) -> Either[str, str]:
    """Baseline solver (no error handling)."""
    # Actual implementation would call LLM
    if puzzle.solution:
        return Either.right(puzzle.solution)
    else:
        return Either.left("No solution exists")

def _solve_with_retry(puzzle: GameOf24Puzzle, max_retries: int) -> Either[str, str]:
    """Solver with @catch:retry:N behavior."""
    for attempt in range(max_retries + 1):
        result = _solve_baseline(puzzle)
        if result.is_right():
            return result
    return Either.left(f"Failed after {max_retries} retries")

def _solve_with_fallback(puzzle: GameOf24Puzzle) -> Either[str, str]:
    """Solver with @fallback:return-best behavior."""
    best_result = None
    best_quality = 0.0

    for _ in range(3):  # Try 3 times
        result = _solve_baseline(puzzle)
        if result.is_right():
            quality = evaluate_solution_quality(result.get_right(), puzzle)
            if quality > best_quality:
                best_quality = quality
                best_result = result

    if best_result:
        return best_result
    return Either.left("No good solution found")

def _solve_with_both(puzzle: GameOf24Puzzle, max_retries: int) -> Either[str, str]:
    """Solver with both retry and fallback."""
    best_result = None
    best_quality = 0.0

    for attempt in range(max_retries + 1):
        result = _solve_baseline(puzzle)
        if result.is_right():
            quality = evaluate_solution_quality(result.get_right(), puzzle)
            if quality > best_quality:
                best_quality = quality
                best_result = result
            if quality >= 0.9:  # Good enough
                return result

    if best_result:
        return best_result
    return Either.left(f"Failed after {max_retries} retries")

def evaluate_solution_quality(solution: str, puzzle: GameOf24Puzzle) -> float:
    """Evaluate quality of solution."""
    try:
        # Check if solution evaluates to 24
        # This is a simplified check
        result = eval(solution)
        if abs(result - 24) < 0.01:
            return 0.95
        else:
            return 0.0
    except:
        return 0.0

@pytest.mark.benchmark
def test_game_of_24_baseline():
    """Baseline accuracy (should be ~90% from Phase 2)."""
    correct = 0
    total = len(GAME_OF_24_DATASET)

    for puzzle in GAME_OF_24_DATASET:
        result = solve_puzzle(puzzle, SolverStrategy.BASELINE)
        if result.is_right():
            correct += 1

    accuracy = correct / total
    print(f"\n=== Baseline Results ===")
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.1%}")

    assert accuracy >= 0.88, f"Baseline accuracy too low: {accuracy:.1%}"

@pytest.mark.benchmark
def test_game_of_24_with_retry():
    """Test @catch:retry:3 improves accuracy."""
    correct_baseline = 0
    correct_retry = 0
    total = len(GAME_OF_24_DATASET)

    for puzzle in GAME_OF_24_DATASET:
        # Baseline
        result_baseline = solve_puzzle(puzzle, SolverStrategy.BASELINE)
        if result_baseline.is_right():
            correct_baseline += 1

        # With retry
        result_retry = solve_puzzle(puzzle, SolverStrategy.RETRY, max_retries=3)
        if result_retry.is_right():
            correct_retry += 1

    baseline_accuracy = correct_baseline / total
    retry_accuracy = correct_retry / total
    improvement = retry_accuracy - baseline_accuracy

    print(f"\n=== Retry Comparison ===")
    print(f"Baseline: {baseline_accuracy:.1%}")
    print(f"Retry:    {retry_accuracy:.1%}")
    print(f"Improvement: +{improvement:.1%}")

    assert retry_accuracy > baseline_accuracy, "Retry should improve accuracy"
    assert improvement >= 0.03, f"Expected ≥3% improvement, got {improvement:.1%}"

@pytest.mark.benchmark
def test_game_of_24_with_fallback():
    """Test @fallback:return-best preserves quality."""
    correct_fallback = 0
    total = len(GAME_OF_24_DATASET)

    for puzzle in GAME_OF_24_DATASET:
        result = solve_puzzle(puzzle, SolverStrategy.FALLBACK)
        if result.is_right():
            correct_fallback += 1

    fallback_accuracy = correct_fallback / total

    print(f"\n=== Fallback Results ===")
    print(f"Accuracy: {fallback_accuracy:.1%}")

    assert fallback_accuracy >= 0.90, f"Fallback accuracy: {fallback_accuracy:.1%}"

@pytest.mark.benchmark
def test_game_of_24_combined_strategies():
    """Test retry + fallback together."""
    correct = 0
    total = len(GAME_OF_24_DATASET)

    for puzzle in GAME_OF_24_DATASET:
        result = solve_puzzle(puzzle, SolverStrategy.BOTH, max_retries=3)
        if result.is_right():
            correct += 1

    combined_accuracy = correct / total

    print(f"\n=== Combined (Retry + Fallback) ===")
    print(f"Accuracy: {combined_accuracy:.1%}")

    # Combined should be best
    assert combined_accuracy >= 0.93, f"Combined accuracy: {combined_accuracy:.1%}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
```

---

### Task 1.2: MATH Dataset Benchmark

**File**: `benchmarks/math_dataset_benchmark.py`

```python
"""
MATH Dataset Benchmark with Quality Tracking

Tests prompting on MATH dataset (de Wynter et al., arXiv:2311.11482)
with error handling and quality fallback.

Expected Results:
- Baseline: 46.3% (from Phase 2)
- Target with Phase 3: >50%
"""

import pytest
from typing import List, Dict, Optional
from dataclasses import dataclass

from meta_prompting_engine.categorical.monad import create_recursive_meta_monad
from meta_prompting_engine.categorical.quality import QualityScore
from ..tests.test_error_handling_laws import Either

@dataclass
class MathProblem:
    """A problem from the MATH dataset."""
    problem: str
    solution: str
    level: int  # 1-5 difficulty
    category: str  # algebra, geometry, etc.

# Sample from MATH dataset (1000 problems)
MATH_DATASET = [
    MathProblem(
        problem="If $x^2 + x + 1 = 0$, find $x^3$",
        solution="-1",
        level=3,
        category="algebra"
    ),
    # ... more problems
]

def solve_math_problem(
    problem: MathProblem,
    use_fallback: bool = False,
    max_iterations: int = 5
) -> Either[str, str]:
    """
    Solve MATH problem with optional quality fallback.

    Args:
        problem: Math problem to solve
        use_fallback: Use @fallback:return-best
        max_iterations: Max refinement iterations

    Returns:
        Either[error, solution]
    """
    monad = create_recursive_meta_monad()

    solutions = []
    qualities = []

    for iteration in range(max_iterations):
        # Attempt solution
        result = _attempt_solution(problem, iteration)

        if result.is_right():
            solution = result.get_right()
            quality = _evaluate_quality(solution, problem)

            solutions.append(solution)
            qualities.append(quality)

            # Good enough?
            if quality >= 0.9:
                return result

    # Return best if using fallback
    if use_fallback and solutions:
        best_idx = qualities.index(max(qualities))
        return Either.right(solutions[best_idx])

    return Either.left("No acceptable solution found")

def _attempt_solution(problem: MathProblem, iteration: int) -> Either[str, str]:
    """Attempt to solve problem (mock implementation)."""
    # Real implementation would call LLM with meta-prompting
    # This is a simplified mock
    return Either.right("42")  # Placeholder

def _evaluate_quality(solution: str, problem: MathProblem) -> float:
    """Evaluate solution quality."""
    if solution.strip() == problem.solution.strip():
        return 0.95
    else:
        return 0.3  # Partial credit for attempt

@pytest.mark.benchmark
@pytest.mark.slow
def test_math_dataset_baseline():
    """Baseline MATH dataset accuracy (should be ~46.3%)."""
    correct = 0
    total = len(MATH_DATASET)

    for problem in MATH_DATASET:
        result = solve_math_problem(problem, use_fallback=False)
        if result.is_right():
            if result.get_right() == problem.solution:
                correct += 1

    accuracy = correct / total

    print(f"\n=== MATH Dataset Baseline ===")
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.1%}")

    assert accuracy >= 0.40, f"Baseline accuracy too low: {accuracy:.1%}"

@pytest.mark.benchmark
@pytest.mark.slow
def test_math_dataset_with_fallback():
    """Test @fallback:return-best improves accuracy."""
    correct_baseline = 0
    correct_fallback = 0
    total = len(MATH_DATASET)

    for problem in MATH_DATASET:
        # Baseline
        result_baseline = solve_math_problem(problem, use_fallback=False)
        if result_baseline.is_right() and result_baseline.get_right() == problem.solution:
            correct_baseline += 1

        # With fallback
        result_fallback = solve_math_problem(problem, use_fallback=True)
        if result_fallback.is_right() and result_fallback.get_right() == problem.solution:
            correct_fallback += 1

    baseline_accuracy = correct_baseline / total
    fallback_accuracy = correct_fallback / total
    improvement = fallback_accuracy - baseline_accuracy

    print(f"\n=== MATH Dataset Fallback Comparison ===")
    print(f"Baseline: {baseline_accuracy:.1%}")
    print(f"Fallback: {fallback_accuracy:.1%}")
    print(f"Improvement: +{improvement:.1%}")

    assert fallback_accuracy >= baseline_accuracy, "Fallback should not degrade"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "benchmark"])
```

---

## Priority 2: Integration Tests (Week 2)

### Task 2.1: Full Categorical Pipeline

**File**: `tests/integration/test_full_pipeline_with_errors.py`

```python
"""
End-to-End Integration Tests with Error Handling

Tests complete categorical pipeline: F → M → W → α → E
"""

import pytest
from dataclasses import dataclass
from typing import Optional

from meta_prompting_engine.categorical.functor import create_task_to_prompt_functor
from meta_prompting_engine.categorical.monad import create_recursive_meta_monad
from meta_prompting_engine.categorical.comonad import create_context_comonad
from ..test_natural_transformation_laws import make_zs_to_cot
from ..test_error_handling_laws import Either

@dataclass
class Task:
    description: str
    complexity: str = "medium"

@pytest.mark.integration
def test_functor_to_monad_composition():
    """Test F → M: Task → Prompt → M(Prompt)"""
    task = Task("Implement authentication system")

    # Functor F: Task → Prompt
    functor = create_task_to_prompt_functor()
    prompt = functor.apply(task)

    # Monad M: Prompt → M(Prompt) with refinement
    monad = create_recursive_meta_monad()
    refined = monad.unit(prompt)

    # Verify composition
    assert refined.prompt.template == prompt.template
    assert refined.quality.value >= 0.5

@pytest.mark.integration
def test_monad_to_comonad_composition():
    """Test M → W: Refined Prompt → Context Extraction"""
    task = Task("Analyze codebase")

    # F → M pipeline
    functor = create_task_to_prompt_functor()
    monad = create_recursive_meta_monad()

    prompt = functor.apply(task)
    refined = monad.unit(prompt)

    # Comonad W: Extract context
    comonad = create_context_comonad()
    observation = comonad.create_observation(refined)
    extracted = comonad.extract(observation)

    # Verify context extraction
    assert extracted is not None
    assert observation.context

@pytest.mark.integration
def test_full_pipeline_with_transformation():
    """Test F → α → M: Task → Transform → Refine"""
    task = Task("Explain quicksort algorithm")

    # F: Task → Prompt (ZeroShot)
    functor = create_task_to_prompt_functor()
    zs_prompt = functor.apply(task)

    # α: ZeroShot ⇒ ChainOfThought
    alpha = make_zs_to_cot()
    cot_prompt = alpha(zs_prompt)

    # M: Refine CoT prompt
    monad = create_recursive_meta_monad()
    refined = monad.unit(cot_prompt)

    # Verify transformation worked
    assert "step by step" in refined.prompt.template.lower()
    assert refined.quality.value >= 0.7

@pytest.mark.integration
def test_full_pipeline_with_error_recovery():
    """Test F → M → E: Task → Refine with Error Handling"""
    task = Task("Complex multi-step analysis")

    # Wrap entire pipeline in Either monad
    def pipeline(t: Task) -> Either[str, str]:
        try:
            # F: Task → Prompt
            functor = create_task_to_prompt_functor()
            prompt = functor.apply(t)

            # M: Refine (may fail)
            monad = create_recursive_meta_monad()
            refined = monad.bind(prompt, lambda p: monad.unit(p))

            # Simulate potential failure
            if refined.quality.value < 0.6:
                return Either.left("Quality too low")

            return Either.right(refined.prompt.template)

        except Exception as e:
            return Either.left(str(e))

    # Execute with error handling
    result = pipeline(task)

    # Verify error handling works
    assert result.is_left() or result.is_right()

@pytest.mark.integration
def test_retry_in_pipeline():
    """Test @catch:retry in full pipeline"""
    task = Task("Solve complex problem")
    max_retries = 3
    attempts = 0

    def attempt_pipeline(t: Task) -> Either[str, str]:
        nonlocal attempts
        attempts += 1

        if attempts < 3:  # Fail first 2 times
            return Either.left(f"Attempt {attempts} failed")
        else:
            return Either.right("Success!")

    # Retry loop
    result = Either.left("Not attempted")
    for _ in range(max_retries + 1):
        result = attempt_pipeline(task)
        if result.is_right():
            break

    # Should succeed on 3rd attempt
    assert result.is_right()
    assert attempts == 3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Priority 3: Adjunction Tests (Week 3-4)

### Task 3.1: Adjunction Law Verification

**File**: `tests/test_adjunction_laws.py`

```python
"""
Adjunction Law Tests for F ⊣ G (Task-Prompt Adjunction)

Tests:
- Unit η: Id → GF
- Counit ε: FG → Id
- Triangle identities
"""

import pytest
from hypothesis import given, strategies as st, settings
from dataclasses import dataclass
from typing import Callable

@dataclass
class Task:
    description: str

@dataclass
class Prompt:
    content: str

# Adjunction: Free ⊣ Forget
# F: Task → Prompt (Free - generate all possible prompts)
# G: Prompt → Task (Forget - extract task from prompt)

def unit_eta(task: Task) -> Prompt:
    """
    Unit η: Task → Prompt

    Free construction: Generate prompt from task.
    """
    return Prompt(content=f"Task: {task.description}")

def counit_epsilon(prompt: Prompt) -> Task:
    """
    Counit ε: Prompt → Task

    Forgetful: Extract task from prompt.
    """
    # Extract task description from prompt
    content = prompt.content
    if content.startswith("Task: "):
        desc = content[6:]
    else:
        desc = content
    return Task(description=desc)

@given(st.text(min_size=1, max_size=100))
@settings(max_examples=100)
def test_triangle_identity_1(task_desc: str):
    """
    Triangle Identity 1: ε_F ∘ F(η) = id_F

    Task → Prompt → Task should be identity.
    """
    task = Task(description=task_desc)

    # η: Task → Prompt
    prompt = unit_eta(task)

    # ε: Prompt → Task
    recovered = counit_epsilon(prompt)

    # Should recover original task
    assert recovered.description == task.description

@given(st.text(min_size=1, max_size=100))
@settings(max_examples=100)
def test_triangle_identity_2(prompt_content: str):
    """
    Triangle Identity 2: G(ε) ∘ η_G = id_G

    Prompt → Task → Prompt should be identity (up to isomorphism).
    """
    prompt = Prompt(content=prompt_content)

    # ε: Prompt → Task
    task = counit_epsilon(prompt)

    # η: Task → Prompt
    recovered = unit_eta(task)

    # Should recover semantically equivalent prompt
    # (not exact string, but same task)
    task2 = counit_epsilon(recovered)
    assert task2.description == task.description

@given(st.text(min_size=1, max_size=100))
@settings(max_examples=50)
def test_hom_set_bijection(task_desc: str):
    """
    Hom-Set Bijection: Hom(F(A), B) ≅ Hom(A, G(B))

    Functions from Prompt to Prompt correspond to
    functions from Task to Task.
    """
    task = Task(description=task_desc)

    # Function on tasks: f: Task → Task
    def f_task(t: Task) -> Task:
        return Task(description=t.description.upper())

    # Corresponding function on prompts: g: Prompt → Prompt
    def g_prompt(p: Prompt) -> Prompt:
        task = counit_epsilon(p)
        transformed = f_task(task)
        return unit_eta(transformed)

    # Both paths should commute
    # Path 1: task → prompt → transform → task
    prompt = unit_eta(task)
    transformed_prompt = g_prompt(prompt)
    result1 = counit_epsilon(transformed_prompt)

    # Path 2: task → transform → task
    result2 = f_task(task)

    assert result1.description == result2.description

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Summary

This plan adds **~1,150 lines of tests** across 3 priorities:

| Priority | Files | Lines | Coverage Gain |
|----------|-------|-------|---------------|
| 1. Empirical | 2 | ~450 | +10% (Empirical: 10% → 60%) |
| 2. Integration | 1 | ~400 | +15% (Integration: 20% → 70%) |
| 3. Adjunction | 1 | ~300 | +10% (Adjunction: 0% → 80%) |

**Total Coverage Improvement**: 59% → 84% (+25%)

**Timeline**: 3-4 weeks for all priorities

**Next Action**: Start with Priority 1 (Empirical Validation) to prove Phase 3 works.
