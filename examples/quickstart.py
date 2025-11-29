"""
Categorical Meta-Prompting Engine - Quickstart Example

Demonstrates complete workflow:
1. Create task
2. Execute with categorical engine
3. Monitor quality
4. Verify categorical laws

Requirements:
    pip install anthropic  # or any LLM client
"""

from meta_prompting_engine import (
    CategoricalMetaPromptingEngine,
    create_categorical_engine,
    Task,
    QualityMonitor,
    create_quality_monitor,
)


# Example 1: Simple LLM Client Wrapper
class SimpleLLMClient:
    """
    Simple LLM client wrapper.

    Replace with your actual LLM client (OpenAI, Anthropic, etc.)
    """

    def complete(self, prompt: str) -> str:
        """
        Execute prompt and return completion.

        In production, replace with actual LLM API call.
        """
        # Simulated response for demo
        return f"This is a simulated response to: {prompt[:50]}..."


def main():
    """Demonstrate categorical meta-prompting workflow."""

    print("=" * 60)
    print("Categorical Meta-Prompting Engine - Quickstart")
    print("=" * 60)

    # Step 1: Create LLM client
    llm_client = SimpleLLMClient()

    # Step 2: Create categorical engine
    print("\n[1] Creating categorical engine...")
    engine = create_categorical_engine(
        llm_client=llm_client,
        quality_threshold=0.90,  # Target quality
        max_iterations=3,  # Maximum improvement iterations
        verify_functor_laws=True,  # Verify Functor F laws
        verify_monad_laws=True,  # Verify Monad M laws
        verify_comonad_laws=True,  # Verify Comonad W laws
    )
    print("✓ Engine created with verified categorical structures")

    # Step 3: Create task
    print("\n[2] Creating task...")
    task = Task(
        description="Solve the Game of 24 with numbers 4, 6, 8, 9",
        constraints=[
            "Use each number exactly once",
            "Use only +, -, *, / operations",
            "Result must equal 24"
        ],
        examples=[
            "Example: 3,3,8,8 → (8/(3-8/3)) = 24",
            "Example: 1,5,5,5 → 5 * (5 - 1/5) = 24"
        ]
    )
    print(f"✓ Task: {task.description}")

    # Step 4: Execute with categorical workflow
    print("\n[3] Executing categorical workflow (Functor → Monad → Comonad)...")
    result = engine.execute(
        task=task,
        max_iterations=3,
        quality_threshold=0.90,
        verify_laws=True  # Runtime law verification
    )
    print(f"✓ Execution complete in {result.iterations} iterations")

    # Step 5: Analyze results
    print("\n[4] Results:")
    print(f"   Output: {result.output[:100]}...")
    print(f"   Quality: {result.quality.value:.3f}")
    print(f"   Quality Improvement: +{result.quality_improvement:.3f}")
    print(f"   Latency: {result.total_latency_ms:.1f}ms")

    # Step 6: Verify categorical laws
    print("\n[5] Categorical Law Verification:")
    print(f"   Functor Laws: {'✓' if result.functor_laws_verified else '✗'}")
    print(f"   Monad Laws: {'✓' if result.monad_laws_verified else '✗'}")
    print(f"   Comonad Laws: {'✓' if result.comonad_laws_verified else '✗'}")

    # Step 7: Quality monitoring
    print("\n[6] Quality Monitoring:")
    monitor = create_quality_monitor(window_size=10, degradation_threshold=0.1)

    # Record quality from execution
    for monadic_prompt in result.prompts_history:
        monitor.record_quality(
            quality_score=monadic_prompt.quality,
            execution_id=f"iter_{monadic_prompt.meta_level}"
        )

    metrics = monitor.get_metrics()
    trend = monitor.get_quality_trend()

    print(f"   Current Quality: {metrics.current_quality:.3f}")
    print(f"   Mean Quality: {metrics.mean_quality:.3f}")
    print(f"   Quality Trend: {trend}")
    print(f"   Degradation Detected: {'Yes' if metrics.degradation_detected else 'No'}")

    # Step 8: Component breakdown
    if metrics.quality_components:
        print("\n[7] Quality Component Breakdown:")
        for component, value in metrics.quality_components.items():
            print(f"   {component}: {value:.3f}")

    # Step 9: Engine statistics
    print("\n[8] Engine Statistics:")
    stats = engine.get_statistics()
    print(f"   Total Executions: {stats['execution_count']}")
    print(f"   Avg Quality Improvement: {stats['avg_quality_improvement']:.3f}")

    print("\n" + "=" * 60)
    print("Quickstart complete! ✨")
    print("=" * 60)


if __name__ == "__main__":
    main()
