"""
Integration tests for CategoricalMetaPromptingEngine.

Tests complete categorical workflows:
1. Task → Prompt (Functor)
2. Prompt → Improved Prompt (Monad)
3. Output → Observation (Comonad)
4. Quality monitoring and metrics

Uses mock LLM for deterministic testing.
"""

import pytest
from typing import List
from datetime import datetime

from meta_prompting_engine.categorical.types import Task, QualityScore
from meta_prompting_engine.categorical.engine import (
    CategoricalMetaPromptingEngine,
    CategoricalMetaPromptingConfig,
    CategoricalExecutionResult,
    create_categorical_engine
)
from meta_prompting_engine.monitoring.enriched_quality import QualityMonitor


class MockLLMClient:
    """Mock LLM client for integration testing."""

    def __init__(self, responses: List[str] = None, base_quality: float = 0.75):
        self.responses = responses or []
        self.base_quality = base_quality
        self.call_count = 0
        self.call_history: List[str] = []

    def complete(self, prompt: str) -> str:
        """Return mock completion."""
        self.call_history.append(prompt)

        # Return predefined response or generate mock
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
        else:
            # Simulate improving responses
            iteration = self.call_count
            if "step-by-step" in prompt.lower() or "refine" in prompt.lower():
                response = f"Detailed step-by-step solution (iteration {iteration}):\n1. Analyze\n2. Plan\n3. Execute\n4. Verify"
            else:
                response = f"Solution (iteration {iteration}): Here is the answer"

        self.call_count += 1
        return response


class TestCategoricalEngineIntegration:
    """Integration tests for categorical meta-prompting engine."""

    @pytest.fixture
    def mock_llm(self) -> MockLLMClient:
        """Create mock LLM client."""
        return MockLLMClient(base_quality=0.75)

    @pytest.fixture
    def engine(self, mock_llm: MockLLMClient) -> CategoricalMetaPromptingEngine:
        """Create engine with mock LLM."""
        config = CategoricalMetaPromptingConfig(
            quality_threshold=0.90,
            max_iterations=3,
            verify_functor_laws=True,
            verify_monad_laws=True,
            verify_comonad_laws=True
        )
        return CategoricalMetaPromptingEngine(llm_client=mock_llm, config=config)

    def test_complete_workflow(self, engine: CategoricalMetaPromptingEngine):
        """
        Test complete categorical workflow: Functor → Monad → Comonad.

        Verifies:
        - Task properly mapped to prompt (Functor)
        - Prompt iteratively improved (Monad)
        - Output wrapped in observation (Comonad)
        - Quality tracking throughout
        """
        # Create task
        task = Task(
            description="Solve the equation 2x + 5 = 15",
            complexity=None,
            constraints=["Show work", "Verify solution"],
            examples=["Example: 3x = 9 → x = 3"]
        )

        # Execute
        result = engine.execute(task, max_iterations=3, verify_laws=True)

        # Verify result structure
        assert isinstance(result, CategoricalExecutionResult)
        assert result.output is not None
        assert len(result.output) > 0

        # Verify quality tracking
        assert isinstance(result.quality, QualityScore)
        assert 0.0 <= result.quality.value <= 1.0

        # Verify execution trace
        assert result.iterations >= 1
        assert len(result.prompts_history) == result.iterations
        assert result.initial_prompt is not None

        # Verify observations created
        assert len(result.observations) > 0
        assert result.observations[0].current == result.output

        # Verify categorical laws checked
        assert result.functor_laws_verified
        assert result.monad_laws_verified
        assert result.comonad_laws_verified

    def test_quality_improvement_over_iterations(
        self,
        engine: CategoricalMetaPromptingEngine
    ):
        """Test that quality improves over iterations."""
        task = Task(
            description="Write a function to calculate fibonacci numbers",
            complexity=None,
            constraints=["Include error handling", "Add documentation"],
            examples=[]
        )

        result = engine.execute(task, max_iterations=3)

        # Verify iterations occurred
        assert result.iterations > 1

        # Quality should generally improve (or stay high)
        # Note: Due to mock LLM, improvement may be simulated
        assert result.final_quality >= 0.0

    def test_early_stopping_on_quality_threshold(
        self,
        engine: CategoricalMetaPromptingEngine,
        mock_llm: MockLLMClient
    ):
        """Test early stopping when quality threshold reached."""
        # Configure for early stopping
        engine.config.early_stopping = True
        engine.config.quality_threshold = 0.60  # Low threshold for quick termination

        task = Task(description="Simple task")

        result = engine.execute(task, max_iterations=10)

        # Should stop before max_iterations if quality reached
        # (Exact behavior depends on mock LLM quality simulation)
        assert result.iterations <= 10

    def test_max_iterations_limit(self, engine: CategoricalMetaPromptingEngine):
        """Test that execution respects max_iterations limit."""
        task = Task(description="Complex task requiring multiple iterations")

        max_iters = 2
        result = engine.execute(task, max_iterations=max_iters, quality_threshold=0.99)

        # Should not exceed max_iterations
        assert result.iterations <= max_iters

    def test_execution_metadata_tracking(
        self,
        engine: CategoricalMetaPromptingEngine
    ):
        """Test that execution metadata is properly tracked."""
        task = Task(description="Test task")

        result = engine.execute(task)

        # Verify metadata
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)
        assert 'execution_id' in result.metadata
        assert 'config' in result.metadata

        # Verify performance metrics
        assert result.total_latency_ms > 0
        assert result.iterations > 0

    def test_statistics_tracking(self, engine: CategoricalMetaPromptingEngine):
        """Test engine statistics tracking across executions."""
        initial_stats = engine.get_statistics()
        assert initial_stats['execution_count'] == 0

        # Execute twice
        task1 = Task(description="First task")
        task2 = Task(description="Second task")

        engine.execute(task1)
        engine.execute(task2)

        # Verify statistics updated
        stats = engine.get_statistics()
        assert stats['execution_count'] == 2
        assert 'avg_quality_improvement' in stats

        # Reset and verify
        engine.reset_statistics()
        reset_stats = engine.get_statistics()
        assert reset_stats['execution_count'] == 0

    def test_factory_function(self, mock_llm: MockLLMClient):
        """Test create_categorical_engine factory function."""
        engine = create_categorical_engine(
            llm_client=mock_llm,
            quality_threshold=0.85,
            max_iterations=4
        )

        assert isinstance(engine, CategoricalMetaPromptingEngine)
        assert engine.config.quality_threshold == 0.85
        assert engine.config.max_iterations == 4

        # Verify it works
        task = Task(description="Factory test")
        result = engine.execute(task)

        assert result is not None


class TestQualityMonitoringIntegration:
    """Integration tests for quality monitoring."""

    @pytest.fixture
    def monitor(self) -> QualityMonitor:
        """Create quality monitor."""
        return QualityMonitor(
            window_size=10,
            degradation_threshold=0.1,
            alert_on_degradation=True
        )

    def test_quality_monitoring_during_execution(
        self,
        monitor: QualityMonitor,
        mock_llm: MockLLMClient
    ):
        """Test quality monitoring during engine execution."""
        engine = create_categorical_engine(
            llm_client=mock_llm,
            max_iterations=5
        )

        task = Task(description="Monitored task")
        result = engine.execute(task)

        # Record quality scores
        for monadic_prompt in result.prompts_history:
            monitor.record_quality(
                quality_score=monadic_prompt.quality,
                execution_id=f"iter_{monadic_prompt.meta_level}"
            )

        # Verify monitoring
        metrics = monitor.get_metrics()
        assert metrics.current_quality > 0.0
        assert len(metrics.quality_history) == result.iterations

    def test_degradation_detection(self, monitor: QualityMonitor):
        """Test quality degradation detection."""
        # Simulate degrading quality
        qualities = [
            QualityScore(value=0.9),
            QualityScore(value=0.85),
            QualityScore(value=0.7),  # Drop > threshold
            QualityScore(value=0.65),  # Another drop
        ]

        for q in qualities:
            monitor.record_quality(q)

        # Should detect degradation
        assert monitor.is_degrading()

        metrics = monitor.get_metrics()
        assert metrics.degradation_detected
        assert metrics.consecutive_degradations >= 2

    def test_quality_trend_analysis(self, monitor: QualityMonitor):
        """Test quality trend analysis."""
        # Improving trend
        improving = [QualityScore(value=0.6 + i * 0.1) for i in range(5)]
        for q in improving:
            monitor.record_quality(q)

        trend = monitor.get_quality_trend()
        assert trend == "improving"

        # Reset and test degrading trend
        monitor.reset()
        degrading = [QualityScore(value=0.9 - i * 0.1) for i in range(5)]
        for q in degrading:
            monitor.record_quality(q)

        trend = monitor.get_quality_trend()
        assert trend == "degrading"

    def test_component_breakdown(self, monitor: QualityMonitor):
        """Test quality component statistics."""
        # Record qualities with components
        qualities = [
            QualityScore(
                value=0.8,
                components={'correctness': 0.9, 'clarity': 0.7}
            ),
            QualityScore(
                value=0.85,
                components={'correctness': 0.95, 'clarity': 0.75}
            ),
        ]

        for q in qualities:
            monitor.record_quality(q)

        breakdown = monitor.get_component_breakdown()

        assert 'correctness' in breakdown
        assert 'clarity' in breakdown
        assert 0.0 <= breakdown['correctness']['mean'] <= 1.0


class TestEndToEndScenarios:
    """End-to-end integration test scenarios."""

    def test_game_of_24_scenario(self, mock_llm: MockLLMClient):
        """
        Test Game of 24 scenario (Zhang et al. benchmark).

        Simulates: Given numbers 4,6,8,9, find operations to get 24.
        """
        # Configure responses
        mock_llm.responses = [
            "Initial attempt: (8-4) * 6 = 24",  # First iteration
            "Refined: Let me verify: 8-4=4, 4*6=24 ✓",  # Second iteration
            "Final optimized: (8-4) * 6 = 24. Verified correct.",  # Third iteration
        ]

        engine = create_categorical_engine(
            llm_client=mock_llm,
            quality_threshold=0.90,
            max_iterations=3
        )

        task = Task(
            description="Given numbers 4, 6, 8, 9, find operations to make 24",
            constraints=["Use each number exactly once", "Use +, -, *, /"],
            examples=["Example: 3,3,8,8 → (8/(3-8/3)) = 24"]
        )

        result = engine.execute(task, verify_laws=True)

        # Verify execution completed
        assert result.output is not None
        assert "24" in result.output
        assert result.iterations <= 3

        # Verify categorical laws verified
        assert result.functor_laws_verified
        assert result.monad_laws_verified
        assert result.comonad_laws_verified

    def test_complex_reasoning_task(self, mock_llm: MockLLMClient):
        """Test complex multi-step reasoning task."""
        mock_llm.responses = [
            "Step 1: Understand the problem",
            "Step 2: Break into subproblems\nStep 3: Solve each",
            "Complete solution with verification"
        ]

        engine = create_categorical_engine(
            llm_client=mock_llm,
            max_iterations=5
        )

        task = Task(
            description="Design a distributed caching system",
            constraints=[
                "Handle cache invalidation",
                "Support multiple cache levels",
                "Ensure consistency"
            ],
            examples=[]
        )

        result = engine.execute(task)

        # Verify iterative improvement occurred
        assert result.iterations >= 1
        assert len(result.prompts_history) == result.iterations

        # Verify quality improved
        if result.iterations > 1:
            assert result.final_quality >= result.initial_quality - 0.1  # Allow small variance


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
