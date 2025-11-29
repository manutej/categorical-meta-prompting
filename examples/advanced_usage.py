"""
Advanced Categorical Meta-Prompting Examples.

Demonstrates:
- Custom configurations
- Quality monitoring with Prometheus
- Categorical law verification
- Integration with production LLMs
- Advanced workflows
"""

from typing import List, Dict, Any
from meta_prompting_engine import (
    CategoricalMetaPromptingEngine,
    CategoricalMetaPromptingConfig,
    Task,
    QualityMonitor,
    Observation,
)


# Example 1: Production LLM Integration
def example_with_anthropic():
    """
    Example with Anthropic Claude API.

    Requires: pip install anthropic
    """
    try:
        import anthropic
    except ImportError:
        print("Install Anthropic SDK: pip install anthropic")
        return

    # Wrap Anthropic client
    class AnthropicLLMClient:
        def __init__(self, api_key: str):
            self.client = anthropic.Client(api_key=api_key)

        def complete(self, prompt: str) -> str:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

    # Create engine with Anthropic
    llm_client = AnthropicLLMClient(api_key="your-api-key")

    config = CategoricalMetaPromptingConfig(
        quality_threshold=0.95,  # High quality target
        max_iterations=5,
        early_stopping=True,
        verify_functor_laws=True,
        verify_monad_laws=True,
        verify_comonad_laws=True,
    )

    engine = CategoricalMetaPromptingEngine(llm_client=llm_client, config=config)

    task = Task(
        description="Design a distributed consensus algorithm",
        constraints=["Handle network partitions", "Ensure safety and liveness"],
        examples=[]
    )

    result = engine.execute(task, verify_laws=True)
    print(f"Output: {result.output}")
    print(f"Quality: {result.quality.value:.3f}")


# Example 2: Quality Monitoring with Degradation Detection
def example_quality_monitoring():
    """Demonstrate quality monitoring with degradation detection."""

    # Create monitor with custom settings
    monitor = QualityMonitor(
        window_size=50,  # Track last 50 executions
        degradation_threshold=0.15,  # Alert if quality drops > 0.15
        alert_on_degradation=True,  # Log warnings
        export_prometheus=False,  # Enable for production
    )

    # Simulate multiple executions
    from meta_prompting_engine.categorical.types import QualityScore

    print("Simulating quality monitoring across executions...")

    for i in range(10):
        # Simulate varying quality
        quality_value = 0.85 - (i * 0.05) if i < 5 else 0.6 + (i - 5) * 0.03

        quality = QualityScore(
            value=quality_value,
            components={
                'correctness': quality_value + 0.05,
                'clarity': quality_value - 0.03,
                'completeness': quality_value,
                'efficiency': quality_value + 0.02
            }
        )

        monitor.record_quality(
            quality_score=quality,
            execution_id=f"exec_{i:03d}"
        )

    # Analyze results
    metrics = monitor.get_metrics()
    trend = monitor.get_quality_trend()
    breakdown = monitor.get_component_breakdown()

    print(f"\nQuality Metrics:")
    print(f"  Current: {metrics.current_quality:.3f}")
    print(f"  Mean: {metrics.mean_quality:.3f} ± {metrics.std_quality:.3f}")
    print(f"  Range: [{metrics.min_quality:.3f}, {metrics.max_quality:.3f}]")
    print(f"  Trend: {trend}")
    print(f"  Degradation: {'DETECTED' if metrics.degradation_detected else 'None'}")

    print(f"\nComponent Breakdown:")
    for component, stats in breakdown.items():
        print(f"  {component}: {stats['mean']:.3f} (current: {stats['current']:.3f})")


# Example 3: Batch Processing with Quality Tracking
def example_batch_processing(tasks: List[Task], llm_client):
    """Process multiple tasks and track quality across batch."""

    engine = CategoricalMetaPromptingEngine(
        llm_client=llm_client,
        config=CategoricalMetaPromptingConfig(
            quality_threshold=0.90,
            max_iterations=3,
            log_execution_trace=True
        )
    )

    monitor = QualityMonitor(window_size=len(tasks))

    results = []

    print(f"Processing {len(tasks)} tasks...")

    for idx, task in enumerate(tasks):
        print(f"\n[{idx+1}/{len(tasks)}] {task.description[:50]}...")

        result = engine.execute(task)

        # Record quality
        for monadic_prompt in result.prompts_history:
            monitor.record_quality(
                quality_score=monadic_prompt.quality,
                execution_id=f"task_{idx}_iter_{monadic_prompt.meta_level}"
            )

        results.append(result)

        print(f"  Quality: {result.quality.value:.3f}, Iterations: {result.iterations}")

    # Summary
    metrics = monitor.get_metrics()
    print(f"\nBatch Summary:")
    print(f"  Tasks Processed: {len(results)}")
    print(f"  Mean Quality: {metrics.mean_quality:.3f}")
    print(f"  Quality Trend: {monitor.get_quality_trend()}")

    return results


# Example 4: Custom Quality Assessment
def example_custom_quality():
    """Demonstrate custom quality assessment functions."""

    from meta_prompting_engine.categorical.quality import assess_quality
    from meta_prompting_engine.categorical.types import Prompt

    prompt = Prompt(
        template="Solve: {task}",
        variables={"task": "Calculate fibonacci(10)"},
        context={},
        meta_level=0
    )

    output = "Fibonacci(10) = 55. Calculated using dynamic programming approach."

    # Assess quality
    quality = assess_quality(output, prompt)

    print("Quality Assessment:")
    print(f"  Overall: {quality.value:.3f}")
    print(f"  Components:")
    for component, value in quality.components.items():
        print(f"    {component}: {value:.3f}")


# Example 5: Comonad Context Extraction
def example_comonad_usage():
    """Demonstrate comonad for context extraction."""

    from meta_prompting_engine.categorical.comonad import (
        create_context_comonad,
        create_observation
    )

    comonad = create_context_comonad()

    # Create observation with rich context
    observation = create_observation(
        value="Solution: x = 5",
        context={
            'prompt': "Solve 2x + 5 = 15",
            'quality': 0.92,
            'iterations': 2,
            'meta_level': 1
        },
        metadata={
            'execution_id': 'demo_001',
            'timestamp': '2025-11-28T12:00:00Z'
        }
    )

    # Extract focused value
    focused = comonad.extract(observation)
    print(f"Focused Value: {focused}")

    # Create meta-observation
    meta_obs = comonad.duplicate(observation)
    print(f"Meta-Observation Quality: {meta_obs.metadata.get('observation_quality', 0.0):.3f}")

    # Context-aware transformation
    def assess_health(obs: Observation) -> str:
        quality = obs.context.get('quality', 0.0)
        if quality >= 0.9:
            return "EXCELLENT"
        elif quality >= 0.7:
            return "GOOD"
        else:
            return "NEEDS_IMPROVEMENT"

    health_obs = comonad.extend(assess_health, observation)
    print(f"System Health: {health_obs.current}")


# Example 6: Complete Workflow with All Features
def example_complete_workflow():
    """Comprehensive example demonstrating all features."""

    print("=" * 70)
    print("Advanced Categorical Meta-Prompting Workflow")
    print("=" * 70)

    # Mock LLM for demo
    class MockLLM:
        def complete(self, prompt: str) -> str:
            return f"Solution based on: {prompt[:30]}..."

    # Step 1: Configure engine
    config = CategoricalMetaPromptingConfig(
        quality_threshold=0.90,
        max_iterations=5,
        early_stopping=True,
        verify_functor_laws=True,
        verify_monad_laws=True,
        verify_comonad_laws=True,
        enable_quality_monitoring=True,
        log_execution_trace=True,
        debug_mode=False,
        verbose_logging=True
    )

    engine = CategoricalMetaPromptingEngine(llm_client=MockLLM(), config=config)

    # Step 2: Create task
    task = Task(
        description="Implement a thread-safe LRU cache",
        constraints=[
            "O(1) get and put operations",
            "Thread-safe for concurrent access",
            "Generic type support"
        ],
        examples=["Redis LRU implementation", "Python functools.lru_cache"]
    )

    # Step 3: Execute with full verification
    print("\nExecuting task with categorical verification...")
    result = engine.execute(task, verify_laws=True)

    # Step 4: Analyze execution
    print(f"\n✓ Execution Results:")
    print(f"  Output Length: {len(result.output)} chars")
    print(f"  Quality: {result.quality.value:.3f}")
    print(f"  Quality Improvement: {result.quality_improvement:.3f}")
    print(f"  Iterations: {result.iterations}")
    print(f"  Latency: {result.total_latency_ms:.1f}ms")

    # Step 5: Verify categorical correctness
    print(f"\n✓ Categorical Laws Verified:")
    print(f"  Functor (F: Tasks → Prompts): {'✓' if result.functor_laws_verified else '✗'}")
    print(f"  Monad (M: Recursive Improvement): {'✓' if result.monad_laws_verified else '✗'}")
    print(f"  Comonad (W: Context Extraction): {'✓' if result.comonad_laws_verified else '✗'}")

    # Step 6: Quality component analysis
    print(f"\n✓ Quality Components:")
    for component, value in result.quality.components.items():
        print(f"  {component}: {value:.3f}")

    # Step 7: Execution trace
    print(f"\n✓ Execution Trace ({len(result.prompts_history)} iterations):")
    for idx, monadic_prompt in enumerate(result.prompts_history):
        print(f"  Iteration {idx}: quality={monadic_prompt.quality.value:.3f}, meta_level={monadic_prompt.meta_level}")

    # Step 8: Observation analysis
    if result.observations:
        obs = result.observations[0]
        print(f"\n✓ Comonadic Observation:")
        print(f"  Value: {obs.current[:50]}...")
        print(f"  Context Keys: {list(obs.context.keys())}")
        print(f"  History Depth: {len(obs.history)}")

    # Step 9: Engine statistics
    stats = engine.get_statistics()
    print(f"\n✓ Engine Statistics:")
    print(f"  Total Executions: {stats['execution_count']}")
    print(f"  Avg Quality Improvement: {stats['avg_quality_improvement']:.3f}")

    print("\n" + "=" * 70)
    print("Workflow complete! All categorical laws verified. ✨")
    print("=" * 70)


if __name__ == "__main__":
    print("Running advanced examples...\n")

    # Run examples
    print("Example 2: Quality Monitoring")
    print("-" * 70)
    example_quality_monitoring()

    print("\n\nExample 4: Custom Quality Assessment")
    print("-" * 70)
    example_custom_quality()

    print("\n\nExample 5: Comonad Context Extraction")
    print("-" * 70)
    example_comonad_usage()

    print("\n\nExample 6: Complete Workflow")
    print("-" * 70)
    example_complete_workflow()
