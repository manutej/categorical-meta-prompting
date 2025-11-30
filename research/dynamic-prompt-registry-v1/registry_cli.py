#!/usr/bin/env python3
"""
Registry CLI - Bridge between slash commands and dynamic prompt registry.

Usage:
    python registry_cli.py list [--domain DOMAIN]
    python registry_cli.py select "problem description"
    python registry_cli.py get NAME
    python registry_cli.py suggest "task description"
"""

import sys
import json
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from extensions.dynamic_prompt_registry import (
        PromptRegistry,
        DomainTag,
        AppropriatePromptSelector,
    )
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False


def create_default_registry() -> 'PromptRegistry':
    """Create registry with built-in prompts from skills."""
    if not REGISTRY_AVAILABLE:
        return None

    registry = PromptRegistry()

    # Register prompts based on existing skills
    registry.register(
        name="code_review_algorithm",
        template="""Review this code focusing on algorithmic efficiency:
1. Time complexity analysis (Big-O)
2. Space complexity analysis
3. Potential optimizations
4. Edge cases handling
5. Data structure choices

Code to review:
{code}""",
        domain=DomainTag.CODE_REVIEW,
        quality=0.85,
        tags={"algorithm", "performance", "complexity"}
    )

    registry.register(
        name="code_review_security",
        template="""Review this code for security vulnerabilities:
1. Input validation gaps
2. Injection risks (SQL, command, XSS)
3. Authentication/authorization issues
4. Sensitive data exposure
5. Error handling that leaks information

Code to review:
{code}""",
        domain=DomainTag.CODE_REVIEW,
        quality=0.88,
        tags={"security", "vulnerability", "owasp"}
    )

    registry.register(
        name="debug_systematic",
        template="""Debug this issue systematically:
1. Reproduce: What exact steps trigger the bug?
2. Isolate: What's the minimal failing case?
3. Hypothesize: What could cause this behavior?
4. Test: How to verify each hypothesis?
5. Fix: What's the minimal correct change?

Issue:
{issue}

Code context:
{code}""",
        domain=DomainTag.REASONING,
        quality=0.82,
        tags={"debug", "systematic", "problem-solving"}
    )

    registry.register(
        name="test_generation",
        template="""Generate comprehensive tests for this code:
1. Happy path: Normal expected usage
2. Edge cases: Boundary conditions, empty inputs
3. Error cases: Invalid inputs, exceptions
4. Integration: Interactions with dependencies

For each test:
- Clear name describing what's tested
- Arrange: Setup
- Act: Execute
- Assert: Verify

Code to test:
{code}""",
        domain=DomainTag.CODE_GENERATION,
        quality=0.84,
        tags={"testing", "unit-test", "coverage"}
    )

    registry.register(
        name="explain_code",
        template="""Explain this code clearly:
1. Purpose: What problem does it solve?
2. Approach: What strategy/algorithm is used?
3. Flow: Step-by-step execution trace
4. Key decisions: Why these design choices?
5. Gotchas: Non-obvious behaviors or edge cases

Code:
{code}""",
        domain=DomainTag.ANALYSIS,
        quality=0.80,
        tags={"explain", "documentation", "understanding"}
    )

    registry.register(
        name="meta_prompting_direct",
        template="""Solve this directly with minimal overhead:

Task: {task}

Provide a clear, concise solution.""",
        domain=DomainTag.GENERAL,
        quality=0.75,
        tags={"simple", "direct", "low-complexity"}
    )

    registry.register(
        name="meta_prompting_multi_approach",
        template="""Solve this using multiple approaches:

Task: {task}

## Approach 1: [Name]
[Solution]

## Approach 2: [Name]
[Solution]

## Comparison
| Aspect | Approach 1 | Approach 2 |
|--------|------------|------------|
| Pros   |            |            |
| Cons   |            |            |

## Recommendation
[Best approach and why]""",
        domain=DomainTag.REASONING,
        quality=0.85,
        tags={"multi-approach", "comparison", "medium-complexity"}
    )

    registry.register(
        name="meta_prompting_autonomous",
        template="""Solve this complex task with iterative refinement:

Task: {task}

## Phase 1: Analysis
- What is the core problem?
- What constraints exist?
- What's the success criteria?

## Phase 2: Strategy
- What approaches could work?
- What's the most promising?

## Phase 3: Implementation
[Initial solution]

## Phase 4: Meta-Reflection
- What's working?
- What needs improvement?
- Quality assessment (0-10):

## Phase 5: Synthesis
[Refined solution incorporating reflection]""",
        domain=DomainTag.REASONING,
        quality=0.90,
        tags={"autonomous", "iterative", "high-complexity"}
    )

    return registry


def cmd_list(domain: str = None):
    """List registered prompts."""
    registry = create_default_registry()
    if not registry:
        print("Registry not available. Install extensions package.")
        return

    prompts = list(registry)
    if domain:
        try:
            tag = DomainTag[domain.upper()]
            prompts = registry.find_by_domain(tag)
        except KeyError:
            prompts = registry.find_by_tag(domain.lower())

    for p in prompts:
        print(f"- {p.name} ({p.domain.name}, quality: {p.quality.score:.2f})")
        if p.tags:
            print(f"  tags: {', '.join(p.tags)}")


def cmd_select(problem: str):
    """Select best prompt for a problem."""
    registry = create_default_registry()
    if not registry:
        print("Registry not available.")
        return

    selector = AppropriatePromptSelector()
    result = selector.select(problem, registry)

    if result:
        print(f"Selected: {result.name}")
        print(f"Domain: {result.domain.name}")
        print(f"Quality: {result.quality.score:.2f}")
        print(f"\nTemplate:\n{result.template}")
    else:
        print("No suitable prompt found.")


def cmd_get(name: str):
    """Get a specific prompt by name."""
    registry = create_default_registry()
    if not registry:
        print("Registry not available.")
        return

    prompt = registry.get(name)
    if prompt:
        print(prompt.template)
    else:
        print(f"Prompt '{name}' not found.")


def cmd_suggest(task: str):
    """Suggest which meta-prompting strategy to use."""
    # Simple complexity heuristic
    complexity_indicators = [
        "complex", "multiple", "compare", "tradeoff", "optimize",
        "iterative", "refine", "autonomous", "difficult", "advanced"
    ]

    task_lower = task.lower()
    indicator_count = sum(1 for w in complexity_indicators if w in task_lower)
    word_count = len(task.split())

    if indicator_count >= 2 or word_count > 50:
        strategy = "autonomous"
        prompt_name = "meta_prompting_autonomous"
    elif indicator_count >= 1 or word_count > 20:
        strategy = "multi_approach"
        prompt_name = "meta_prompting_multi_approach"
    else:
        strategy = "direct"
        prompt_name = "meta_prompting_direct"

    print(f"Recommended strategy: {strategy}")
    print(f"Prompt template: {prompt_name}")

    registry = create_default_registry()
    if registry:
        prompt = registry.get(prompt_name)
        if prompt:
            print(f"\nTemplate:\n{prompt.template}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "list":
        domain = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_list(domain)
    elif cmd == "select":
        problem = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        cmd_select(problem)
    elif cmd == "get":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        cmd_get(name)
    elif cmd == "suggest":
        task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        cmd_suggest(task)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
