"""
Simple Prompt Selector - Keyword Matching Edition

Selects prompts based on keyword matching.
NOT semantic, NOT AI-powered, just keywords.
Honest about what it does.
"""

from typing import Optional, List, Tuple
from registry import PromptRegistry, Prompt, Domain


# Domain keywords - simple heuristic, not magic
DOMAIN_KEYWORDS = {
    Domain.ALGORITHM: ["algorithm", "sort", "search", "complexity", "big-o", "O(n)", "recursive", "tree", "graph"],
    Domain.SECURITY: ["security", "auth", "password", "token", "injection", "xss", "csrf", "vulnerability"],
    Domain.API: ["api", "endpoint", "rest", "http", "request", "response", "route"],
    Domain.DATABASE: ["database", "sql", "query", "table", "index", "transaction"],
    Domain.TESTING: ["test", "tests", "testing", "unit", "mock", "assert", "coverage"],  # Added plurals
    Domain.DEBUG: ["debug", "error", "bug", "fix", "issue", "crash", "exception"],
}


def classify_domain(text: str) -> Tuple[Domain, int]:
    """
    Classify text into a domain based on keyword matching.

    Returns (domain, match_count).
    This is simple keyword matching - not semantic understanding.
    """
    text_lower = text.lower()
    best_domain = Domain.GENERAL
    best_count = 0

    for domain, keywords in DOMAIN_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > best_count:
            best_count = count
            best_domain = domain

    return best_domain, best_count


def select_prompt(
    problem: str,
    registry: PromptRegistry,
    min_quality: float = 0.0
) -> Optional[Prompt]:
    """
    Select the best prompt for a problem.

    Algorithm:
    1. Classify problem domain via keywords
    2. Get prompts from that domain
    3. Filter by minimum quality
    4. Return highest quality

    This is NOT semantic matching. It's keyword heuristics.
    For real semantic selection, use embeddings or ask Claude.
    """
    # Classify domain
    domain, match_count = classify_domain(problem)

    # Get domain prompts
    if match_count > 0:
        candidates = registry.find_by_domain(domain)
    else:
        # No matches - use all prompts
        candidates = registry.list_all()

    # Filter by quality
    candidates = [p for p in candidates if p.quality >= min_quality]

    if not candidates:
        return None

    # Return highest quality
    return max(candidates, key=lambda p: p.quality)


def explain_selection(problem: str, registry: PromptRegistry) -> str:
    """
    Explain why a prompt was selected.
    Useful for debugging and transparency.
    """
    domain, match_count = classify_domain(problem)

    lines = [
        f"Problem: {problem[:80]}{'...' if len(problem) > 80 else ''}",
        f"",
        f"Domain Classification: {domain.name}",
        f"Keyword matches: {match_count}",
    ]

    if match_count > 0:
        matched_keywords = [kw for kw in DOMAIN_KEYWORDS.get(domain, []) if kw in problem.lower()]
        lines.append(f"Matched keywords: {matched_keywords}")

    selected = select_prompt(problem, registry)
    if selected:
        lines.extend([
            f"",
            f"Selected: {selected.name}",
            f"Quality: {selected.quality}",
        ])
    else:
        lines.append(f"\nNo suitable prompt found.")

    return "\n".join(lines)


if __name__ == "__main__":
    # Self-test
    from registry import create_default_registry

    r = create_default_registry()

    # Test 1: Security problem
    problem1 = "Review this code for SQL injection vulnerabilities"
    selected1 = select_prompt(problem1, r)
    print(f"Test 1 - Security problem:")
    print(f"  Problem: {problem1}")
    print(f"  Selected: {selected1.name if selected1 else 'None'}")
    print(f"  Expected: review_security")
    assert selected1 and selected1.name == "review_security", "FAILED"
    print(f"  PASSED\n")

    # Test 2: Algorithm problem
    problem2 = "Analyze the time complexity of this sorting algorithm"
    selected2 = select_prompt(problem2, r)
    print(f"Test 2 - Algorithm problem:")
    print(f"  Problem: {problem2}")
    print(f"  Selected: {selected2.name if selected2 else 'None'}")
    print(f"  Expected: review_algorithm")
    assert selected2 and selected2.name == "review_algorithm", "FAILED"
    print(f"  PASSED\n")

    # Test 3: Debug problem
    problem3 = "Help me debug this error in my code"
    selected3 = select_prompt(problem3, r)
    print(f"Test 3 - Debug problem:")
    print(f"  Problem: {problem3}")
    print(f"  Selected: {selected3.name if selected3 else 'None'}")
    print(f"  Expected: debug")
    assert selected3 and selected3.name == "debug", "FAILED"
    print(f"  PASSED\n")

    # Test 4: Explain selection
    print("Test 4 - Explain selection:")
    explanation = explain_selection(problem1, r)
    print(explanation)
    print("  PASSED\n")

    print("All self-tests: PASSED")
