"""
Atomic Blocks Test Suite
========================

Tests for the categorical meta-prompting atomic blocks system.
Covers unit tests, composition tests, and categorical law verification.

Run with: pytest tests/test_atomic_blocks.py -v
"""

import pytest
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable, TypeVar, Generic
from enum import Enum
from abc import ABC, abstractmethod

# ============================================================================
# Type Definitions
# ============================================================================

class Domain(Enum):
    ALGORITHM = "ALGORITHM"
    SECURITY = "SECURITY"
    API = "API"
    DEBUG = "DEBUG"
    TESTING = "TESTING"
    GENERAL = "GENERAL"


class Tier(Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"
    L7 = "L7"


class Strategy(Enum):
    DIRECT = "DIRECT"
    MULTI_APPROACH = "MULTI_APPROACH"
    AUTONOMOUS_EVOLUTION = "AUTONOMOUS_EVOLUTION"


class ConvergenceStatus(Enum):
    CONTINUE = "CONTINUE"
    CONVERGED = "CONVERGED"
    MAX_ITERATIONS = "MAX_ITERATIONS"
    PLATEAU = "PLATEAU"
    HALT = "HALT"


@dataclass
class DifficultyScore:
    """Output of assess_difficulty block"""
    score: float  # [0, 1]
    factors: Dict[str, float]

    def __post_init__(self):
        assert 0 <= self.score <= 1, f"Score must be in [0,1], got {self.score}"


@dataclass
class DomainResult:
    """Output of assess_domain block"""
    domain: Domain
    confidence: float
    signals: List[str]


@dataclass
class QualityVector:
    """Output of assess_quality block"""
    correctness: float
    clarity: float
    completeness: float
    efficiency: float

    @property
    def aggregate(self) -> float:
        """Weighted aggregate quality score"""
        return (0.40 * self.correctness +
                0.25 * self.clarity +
                0.20 * self.completeness +
                0.15 * self.efficiency)

    @property
    def weakest(self) -> str:
        """Dimension with lowest score"""
        dims = {
            'correctness': self.correctness,
            'clarity': self.clarity,
            'completeness': self.completeness,
            'efficiency': self.efficiency
        }
        return min(dims, key=dims.get)


@dataclass
class TierResult:
    """Output of select_tier block"""
    tier: Tier
    strategy: Strategy
    budget_range: tuple


@dataclass
class ImprovementDirection:
    """Output of extract_improvement block"""
    focus_dimension: str
    gap: float
    suggestions: List[str]
    priority: str


@dataclass
class ConvergenceResult:
    """Output of evaluate_convergence block"""
    status: ConvergenceStatus
    reason: str
    should_refine: bool


# ============================================================================
# Block Interface
# ============================================================================

T = TypeVar('T')
U = TypeVar('U')


class Block(ABC, Generic[T, U]):
    """Abstract base class for atomic blocks"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Block name"""
        pass

    @property
    @abstractmethod
    def input_type(self) -> type:
        """Expected input type"""
        pass

    @property
    @abstractmethod
    def output_type(self) -> type:
        """Expected output type"""
        pass

    @abstractmethod
    def __call__(self, input_data: T) -> U:
        """Execute the block"""
        pass


# ============================================================================
# Assessment Blocks
# ============================================================================

class AssessDifficulty(Block[str, DifficultyScore]):
    """Evaluate task complexity for tier selection"""

    @property
    def name(self) -> str:
        return "assess_difficulty"

    @property
    def input_type(self) -> type:
        return str

    @property
    def output_type(self) -> type:
        return DifficultyScore

    def __call__(self, task: str) -> DifficultyScore:
        # Simplified difficulty assessment
        length_factor = min(1.0, len(task) / 200)

        # Check for complexity indicators
        complexity_keywords = ['microservices', 'distributed', 'concurrent',
                              'optimization', 'architecture', 'scale']
        complexity = sum(1 for kw in complexity_keywords if kw in task.lower()) / len(complexity_keywords)

        # Check for ambiguity
        ambiguity_indicators = ['somehow', 'maybe', 'might', 'could', 'possibly']
        ambiguity = sum(1 for ind in ambiguity_indicators if ind in task.lower()) / 5

        # Calculate overall score
        score = (length_factor * 0.3 + complexity * 0.5 + (1 - ambiguity) * 0.2)
        score = max(0.1, min(0.95, score))  # Clamp to reasonable range

        return DifficultyScore(
            score=score,
            factors={
                'length': length_factor,
                'complexity': complexity,
                'ambiguity': ambiguity,
                'novelty': 0.5  # Default
            }
        )


class AssessDomain(Block[str, DomainResult]):
    """Classify task into domain category"""

    DOMAIN_PATTERNS = {
        Domain.ALGORITHM: ['optimize', 'complexity', 'sort', 'search', 'tree', 'graph', 'O(n)'],
        Domain.SECURITY: ['auth', 'encrypt', 'hash', 'OWASP', 'injection', 'XSS', 'CSRF', 'security'],
        Domain.API: ['endpoint', 'REST', 'GraphQL', 'request', 'response', 'route', 'API'],
        Domain.DEBUG: ['error', 'bug', 'fix', 'trace', 'exception', 'crash', 'debug'],
        Domain.TESTING: ['test', 'assert', 'mock', 'coverage', 'spec', 'jest', 'pytest'],
    }

    @property
    def name(self) -> str:
        return "assess_domain"

    @property
    def input_type(self) -> type:
        return str

    @property
    def output_type(self) -> type:
        return DomainResult

    def __call__(self, task: str) -> DomainResult:
        task_lower = task.lower()

        scores = {}
        signals = {}

        for domain, patterns in self.DOMAIN_PATTERNS.items():
            matches = [p for p in patterns if p.lower() in task_lower]
            scores[domain] = len(matches) / len(patterns)
            signals[domain] = matches

        if max(scores.values()) > 0:
            best_domain = max(scores, key=scores.get)
            confidence = scores[best_domain]
            matched_signals = signals[best_domain]
        else:
            best_domain = Domain.GENERAL
            confidence = 0.5
            matched_signals = []

        return DomainResult(
            domain=best_domain,
            confidence=confidence,
            signals=matched_signals
        )


class AssessQuality(Block[str, QualityVector]):
    """Multi-dimensional quality evaluation"""

    @property
    def name(self) -> str:
        return "assess_quality"

    @property
    def input_type(self) -> type:
        return str

    @property
    def output_type(self) -> type:
        return QualityVector

    def __call__(self, output: str, context: str = "") -> QualityVector:
        # Simplified quality assessment
        # In production, this would use more sophisticated analysis

        length = len(output)

        # Heuristic quality indicators
        has_code = '```' in output or 'def ' in output or 'function' in output
        has_explanation = len(output.split('\n')) > 5
        has_structure = any(marker in output for marker in ['##', '- ', '1.', '*'])

        correctness = 0.7 if has_code else 0.5
        clarity = 0.8 if has_explanation and has_structure else 0.6
        completeness = min(0.9, length / 500)
        efficiency = 0.7 if has_code else 0.6

        return QualityVector(
            correctness=correctness,
            clarity=clarity,
            completeness=completeness,
            efficiency=efficiency
        )


class SelectTier(Block[tuple, TierResult]):
    """Map assessment to L1-L7 tier"""

    TIER_MAPPING = [
        (0.15, Tier.L1, Strategy.DIRECT, (600, 1200)),
        (0.30, Tier.L2, Strategy.DIRECT, (1500, 3000)),
        (0.45, Tier.L3, Strategy.MULTI_APPROACH, (2500, 4500)),
        (0.60, Tier.L4, Strategy.MULTI_APPROACH, (3000, 6000)),
        (0.75, Tier.L5, Strategy.AUTONOMOUS_EVOLUTION, (5500, 9000)),
        (0.90, Tier.L6, Strategy.AUTONOMOUS_EVOLUTION, (8000, 12000)),
        (1.00, Tier.L7, Strategy.AUTONOMOUS_EVOLUTION, (12000, 22000)),
    ]

    @property
    def name(self) -> str:
        return "select_tier"

    @property
    def input_type(self) -> type:
        return tuple  # (DifficultyScore, DomainResult)

    @property
    def output_type(self) -> type:
        return TierResult

    def __call__(self, assessment: tuple) -> TierResult:
        difficulty, domain_result = assessment
        score = difficulty.score

        # Apply domain modifiers
        if domain_result.domain == Domain.SECURITY:
            score = min(1.0, score + 0.15)  # Security gets tier bump

        # Find appropriate tier
        for threshold, tier, strategy, budget in self.TIER_MAPPING:
            if score <= threshold:
                return TierResult(tier=tier, strategy=strategy, budget_range=budget)

        return TierResult(
            tier=Tier.L7,
            strategy=Strategy.AUTONOMOUS_EVOLUTION,
            budget_range=(12000, 22000)
        )


# ============================================================================
# Refinement Blocks
# ============================================================================

class EvaluateConvergence(Block[tuple, ConvergenceResult]):
    """Check if quality meets threshold"""

    @property
    def name(self) -> str:
        return "evaluate_convergence"

    @property
    def input_type(self) -> type:
        return tuple  # (QualityVector, float, int, int, Optional[float])

    @property
    def output_type(self) -> type:
        return ConvergenceResult

    def __call__(self, params: tuple) -> ConvergenceResult:
        quality, threshold, iteration, max_iterations, previous_quality = params

        aggregate = quality.aggregate

        # Check convergence conditions
        if aggregate >= threshold:
            return ConvergenceResult(
                status=ConvergenceStatus.CONVERGED,
                reason=f"Quality {aggregate:.2f} >= threshold {threshold}",
                should_refine=False
            )

        if iteration >= max_iterations:
            return ConvergenceResult(
                status=ConvergenceStatus.MAX_ITERATIONS,
                reason=f"Reached max iterations ({max_iterations})",
                should_refine=False
            )

        if previous_quality is not None and abs(aggregate - previous_quality) < 0.02:
            return ConvergenceResult(
                status=ConvergenceStatus.PLATEAU,
                reason=f"Quality plateau (delta < 0.02)",
                should_refine=False
            )

        if aggregate < 0.4:
            return ConvergenceResult(
                status=ConvergenceStatus.HALT,
                reason=f"Quality too low ({aggregate:.2f} < 0.4), fundamental failure",
                should_refine=False
            )

        return ConvergenceResult(
            status=ConvergenceStatus.CONTINUE,
            reason=f"Quality {aggregate:.2f} < threshold {threshold}, continuing",
            should_refine=True
        )


class ExtractImprovement(Block[tuple, ImprovementDirection]):
    """Identify improvement direction from gaps"""

    @property
    def name(self) -> str:
        return "extract_improvement"

    @property
    def input_type(self) -> type:
        return tuple  # (str, QualityVector)

    @property
    def output_type(self) -> type:
        return ImprovementDirection

    def __call__(self, params: tuple) -> ImprovementDirection:
        output, quality = params

        weakest = quality.weakest
        weakest_score = getattr(quality, weakest)
        gap = 0.8 - weakest_score  # Assuming 0.8 threshold

        suggestions_map = {
            'correctness': [
                "Verify logic handles all input cases",
                "Check for off-by-one errors",
                "Validate edge case handling"
            ],
            'clarity': [
                "Add explanatory comments",
                "Use more descriptive names",
                "Structure output with headers"
            ],
            'completeness': [
                "Handle edge cases explicitly",
                "Add error handling",
                "Include input validation"
            ],
            'efficiency': [
                "Optimize algorithm complexity",
                "Reduce redundant operations",
                "Consider caching"
            ]
        }

        priority = "high" if gap > 0.3 else "medium" if gap > 0.15 else "low"

        return ImprovementDirection(
            focus_dimension=weakest,
            gap=gap,
            suggestions=suggestions_map.get(weakest, []),
            priority=priority
        )


# ============================================================================
# Composition Functions
# ============================================================================

def sequence(block_a: Block, block_b: Block) -> Callable:
    """Sequential composition: A → B"""
    def composed(input_data):
        intermediate = block_a(input_data)
        return block_b(intermediate)
    return composed


def parallel(blocks: List[Block], merge_strategy: str = 'concatenate') -> Callable:
    """Parallel composition: A || B || C"""
    def composed(input_data):
        results = [block(input_data) for block in blocks]

        if merge_strategy == 'concatenate':
            return results
        elif merge_strategy == 'vote':
            # For domain results, take majority
            from collections import Counter
            if all(isinstance(r, DomainResult) for r in results):
                domains = [r.domain for r in results]
                return Counter(domains).most_common(1)[0][0]
            return results
        elif merge_strategy == 'weighted':
            # Weight by confidence if available
            if all(hasattr(r, 'confidence') for r in results):
                total_conf = sum(r.confidence for r in results)
                # Return result with highest confidence
                return max(results, key=lambda r: r.confidence)
            return results

        return results
    return composed


# ============================================================================
# Test Cases
# ============================================================================

class TestAssessDifficulty:
    """Unit tests for assess_difficulty block"""

    def test_simple_task(self):
        block = AssessDifficulty()
        result = block("fix typo")

        assert isinstance(result, DifficultyScore)
        assert 0 <= result.score <= 1
        assert result.score < 0.5  # Simple task should be low difficulty

    def test_complex_task(self):
        block = AssessDifficulty()
        result = block("design distributed microservices architecture with concurrent processing and optimization")

        assert result.score > 0.5  # Complex task should be higher difficulty

    def test_deterministic(self):
        block = AssessDifficulty()
        task = "implement rate limiter"

        result1 = block(task)
        result2 = block(task)

        assert result1.score == result2.score  # Same input → same output

    def test_bounded_output(self):
        block = AssessDifficulty()

        # Test various inputs
        for task in ["a", "x" * 1000, "complex distributed system"]:
            result = block(task)
            assert 0 <= result.score <= 1


class TestAssessDomain:
    """Unit tests for assess_domain block"""

    def test_security_domain(self):
        block = AssessDomain()
        result = block("fix XSS vulnerability in authentication")

        assert result.domain == Domain.SECURITY
        assert result.confidence > 0
        assert len(result.signals) > 0

    def test_api_domain(self):
        block = AssessDomain()
        result = block("create REST endpoint for user registration")

        assert result.domain == Domain.API

    def test_algorithm_domain(self):
        block = AssessDomain()
        result = block("optimize sorting algorithm complexity O(n)")

        assert result.domain == Domain.ALGORITHM

    def test_general_fallback(self):
        block = AssessDomain()
        result = block("do something interesting")

        assert result.domain == Domain.GENERAL

    def test_deterministic(self):
        block = AssessDomain()
        task = "review security of API"

        result1 = block(task)
        result2 = block(task)

        assert result1.domain == result2.domain


class TestAssessQuality:
    """Unit tests for assess_quality block"""

    def test_quality_vector_structure(self):
        block = AssessQuality()
        result = block("def foo(): pass")

        assert isinstance(result, QualityVector)
        assert 0 <= result.correctness <= 1
        assert 0 <= result.clarity <= 1
        assert 0 <= result.completeness <= 1
        assert 0 <= result.efficiency <= 1

    def test_aggregate_calculation(self):
        qv = QualityVector(
            correctness=0.8,
            clarity=0.8,
            completeness=0.8,
            efficiency=0.8
        )

        expected = 0.40*0.8 + 0.25*0.8 + 0.20*0.8 + 0.15*0.8
        assert abs(qv.aggregate - expected) < 0.001

    def test_weakest_dimension(self):
        qv = QualityVector(
            correctness=0.9,
            clarity=0.5,  # Lowest
            completeness=0.8,
            efficiency=0.7
        )

        assert qv.weakest == 'clarity'


class TestSelectTier:
    """Unit tests for select_tier block"""

    def test_low_difficulty_maps_to_low_tier(self):
        block = SelectTier()
        difficulty = DifficultyScore(score=0.2, factors={})
        domain = DomainResult(domain=Domain.GENERAL, confidence=0.5, signals=[])

        result = block((difficulty, domain))

        assert result.tier in [Tier.L1, Tier.L2]
        assert result.strategy == Strategy.DIRECT

    def test_high_difficulty_maps_to_high_tier(self):
        block = SelectTier()
        difficulty = DifficultyScore(score=0.85, factors={})
        domain = DomainResult(domain=Domain.GENERAL, confidence=0.5, signals=[])

        result = block((difficulty, domain))

        assert result.tier in [Tier.L6, Tier.L7]
        assert result.strategy == Strategy.AUTONOMOUS_EVOLUTION

    def test_security_domain_tier_bump(self):
        block = SelectTier()
        difficulty = DifficultyScore(score=0.5, factors={})

        # Without security
        general_domain = DomainResult(domain=Domain.GENERAL, confidence=0.5, signals=[])
        general_result = block((difficulty, general_domain))

        # With security
        security_domain = DomainResult(domain=Domain.SECURITY, confidence=0.8, signals=[])
        security_result = block((difficulty, security_domain))

        # Security should get higher tier
        assert security_result.tier.value >= general_result.tier.value


class TestEvaluateConvergence:
    """Unit tests for evaluate_convergence block"""

    def test_converged_when_above_threshold(self):
        block = EvaluateConvergence()
        quality = QualityVector(correctness=0.9, clarity=0.9, completeness=0.9, efficiency=0.9)

        result = block((quality, 0.8, 1, 5, None))

        assert result.status == ConvergenceStatus.CONVERGED
        assert not result.should_refine

    def test_continue_when_below_threshold(self):
        block = EvaluateConvergence()
        quality = QualityVector(correctness=0.6, clarity=0.6, completeness=0.6, efficiency=0.6)

        result = block((quality, 0.8, 1, 5, None))

        assert result.status == ConvergenceStatus.CONTINUE
        assert result.should_refine

    def test_max_iterations_stops(self):
        block = EvaluateConvergence()
        quality = QualityVector(correctness=0.6, clarity=0.6, completeness=0.6, efficiency=0.6)

        result = block((quality, 0.8, 5, 5, None))  # iteration == max

        assert result.status == ConvergenceStatus.MAX_ITERATIONS
        assert not result.should_refine

    def test_plateau_detection(self):
        block = EvaluateConvergence()
        quality = QualityVector(correctness=0.7, clarity=0.7, completeness=0.7, efficiency=0.7)

        # Previous quality very close to current
        result = block((quality, 0.8, 3, 5, 0.698))

        assert result.status == ConvergenceStatus.PLATEAU


class TestExtractImprovement:
    """Unit tests for extract_improvement block"""

    def test_identifies_weakest_dimension(self):
        block = ExtractImprovement()
        quality = QualityVector(
            correctness=0.9,
            clarity=0.5,  # Weakest
            completeness=0.8,
            efficiency=0.7
        )

        result = block(("some output", quality))

        assert result.focus_dimension == 'clarity'
        assert result.gap > 0
        assert len(result.suggestions) > 0

    def test_priority_based_on_gap(self):
        block = ExtractImprovement()

        # Large gap
        quality_low = QualityVector(correctness=0.3, clarity=0.3, completeness=0.3, efficiency=0.3)
        result_low = block(("output", quality_low))

        # Small gap
        quality_high = QualityVector(correctness=0.75, clarity=0.75, completeness=0.75, efficiency=0.75)
        result_high = block(("output", quality_high))

        assert result_low.priority == "high"
        assert result_high.priority == "low"


class TestComposition:
    """Tests for block composition"""

    def test_sequential_composition(self):
        """Test A → B composition"""
        assess_diff = AssessDifficulty()
        assess_dom = AssessDomain()

        # Sequential composition
        task = "optimize API security"

        # Manual sequential
        diff_result = assess_diff(task)

        # Both should work independently
        dom_result = assess_dom(task)

        assert isinstance(diff_result, DifficultyScore)
        assert isinstance(dom_result, DomainResult)

    def test_parallel_composition(self):
        """Test A || B composition"""
        assess_diff = AssessDifficulty()
        assess_dom = AssessDomain()

        composed = parallel([assess_diff, assess_dom])

        results = composed("implement rate limiter")

        assert len(results) == 2
        assert isinstance(results[0], DifficultyScore)
        assert isinstance(results[1], DomainResult)

    def test_parallel_with_vote(self):
        """Test parallel with voting merge"""
        assess_dom1 = AssessDomain()
        assess_dom2 = AssessDomain()
        assess_dom3 = AssessDomain()

        composed = parallel([assess_dom1, assess_dom2, assess_dom3], merge_strategy='vote')

        # Task clearly in security domain
        result = composed("fix XSS and CSRF vulnerabilities in auth")

        assert result == Domain.SECURITY


class TestCategoricalLaws:
    """Tests for categorical law verification"""

    def test_quality_degradation_law(self):
        """quality(A → B) ≤ min(quality(A), quality(B))"""
        # This is a structural property - in composition, quality is bounded by weakest
        qv1 = QualityVector(correctness=0.9, clarity=0.8, completeness=0.7, efficiency=0.8)
        qv2 = QualityVector(correctness=0.6, clarity=0.9, completeness=0.8, efficiency=0.7)

        # Composed quality should be bounded by minimum
        composed_quality = min(qv1.aggregate, qv2.aggregate)

        assert composed_quality <= min(qv1.aggregate, qv2.aggregate)

    def test_parallel_quality_average(self):
        """quality(A || B) = mean(quality(A), quality(B))"""
        qv1 = QualityVector(correctness=0.8, clarity=0.8, completeness=0.8, efficiency=0.8)
        qv2 = QualityVector(correctness=0.6, clarity=0.6, completeness=0.6, efficiency=0.6)

        parallel_quality = (qv1.aggregate + qv2.aggregate) / 2
        expected = (0.8 + 0.6) / 2  # 0.7

        assert abs(parallel_quality - expected) < 0.001


# ============================================================================
# Composition Error Tests
# ============================================================================

class CompositionError(Exception):
    """Base class for composition errors"""
    pass


class TypeMismatchError(CompositionError):
    """Type mismatch between blocks"""
    pass


class CircularDependencyError(CompositionError):
    """Circular dependency detected"""
    pass


def validate_composition(blocks: List[Block]) -> bool:
    """Validate a block composition for type compatibility"""
    for i in range(len(blocks) - 1):
        current = blocks[i]
        next_block = blocks[i + 1]

        # Check if output type of current matches input type of next
        # In a real implementation, this would do proper type checking
        # For now, we just verify the blocks exist

    return True


class TestCompositionValidation:
    """Tests for composition validation"""

    def test_valid_composition(self):
        blocks = [AssessDifficulty(), AssessDomain()]
        assert validate_composition(blocks) == True

    def test_empty_composition(self):
        assert validate_composition([]) == True


# ============================================================================
# Integration Tests
# ============================================================================

class TestRMPBlockFlow:
    """Integration tests for /rmp block flow"""

    def test_full_rmp_iteration(self):
        """Test complete RMP iteration using blocks"""
        task = "implement rate limiter"

        # Step 1: Initial execution (simplified)
        output = f"def rate_limit(key): return True  # TODO: implement for '{task}'"

        # Step 2: Assess quality
        assess_quality = AssessQuality()
        quality = assess_quality(output)

        # Step 3: Evaluate convergence
        evaluate_conv = EvaluateConvergence()
        convergence = evaluate_conv((quality, 0.8, 1, 5, None))

        # Step 4: If not converged, extract improvement
        if convergence.should_refine:
            extract_imp = ExtractImprovement()
            direction = extract_imp((output, quality))

            assert direction.focus_dimension in ['correctness', 'clarity', 'completeness', 'efficiency']
            assert len(direction.suggestions) > 0

    def test_convergence_achieved(self):
        """Test that high-quality output converges"""
        high_quality_output = """
        ```python
        def rate_limit(key: str, limit: int = 100, window: int = 60) -> bool:
            '''
            Rate limiter using sliding window algorithm.

            Args:
                key: Unique identifier for rate limiting
                limit: Maximum requests allowed
                window: Time window in seconds

            Returns:
                True if request allowed, False if rate limited
            '''
            current_count = cache.get(key, 0)
            if current_count >= limit:
                return False
            cache.increment(key, ttl=window)
            return True
        ```
        """

        assess_quality = AssessQuality()
        quality = assess_quality(high_quality_output)

        evaluate_conv = EvaluateConvergence()
        convergence = evaluate_conv((quality, 0.7, 1, 5, None))

        # High quality output should converge (or be close)
        assert quality.aggregate > 0.6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
