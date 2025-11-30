#!/usr/bin/env python3
"""
Visible Test Suite - Shows what's being tested and results

Run with: python3 test_visible.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from registry import PromptRegistry, Domain, Prompt, create_default_registry
from selector import select_prompt, classify_domain, explain_selection, DOMAIN_KEYWORDS


def header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def test_result(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {name}")
    if details:
        print(f"         {details}")
    return passed


def test_registry_basics():
    """Test basic registry operations."""
    header("TEST 1: Registry Basics")

    print("Creating empty registry...")
    r = PromptRegistry()

    t1 = test_result(
        "Empty registry has length 0",
        len(r) == 0,
        f"len(r) = {len(r)}"
    )

    print("\nRegistering a prompt...")
    r.register("test", "Hello {name}", domain=Domain.GENERAL, quality=0.5)

    t2 = test_result(
        "Registry has 1 prompt after register",
        len(r) == 1,
        f"len(r) = {len(r)}"
    )

    print("\nGetting the prompt...")
    p = r.get("test")

    t3 = test_result(
        "get() returns the prompt",
        p is not None and p.name == "test",
        f"p.name = {p.name if p else 'None'}"
    )

    print("\nRendering with variable...")
    rendered = p.render(name="World")

    t4 = test_result(
        "render() substitutes variables",
        rendered == "Hello World",
        f"rendered = '{rendered}'"
    )

    print("\nGetting non-existent prompt...")
    missing = r.get("nonexistent")

    t5 = test_result(
        "get() returns None for missing",
        missing is None,
        f"result = {missing}"
    )

    return all([t1, t2, t3, t4, t5])


def test_domain_filtering():
    """Test domain-based filtering."""
    header("TEST 2: Domain Filtering")

    print("Creating registry with multiple domains...")
    r = PromptRegistry()
    r.register("sec1", "Security 1", domain=Domain.SECURITY, quality=0.8)
    r.register("sec2", "Security 2", domain=Domain.SECURITY, quality=0.9)
    r.register("algo1", "Algorithm 1", domain=Domain.ALGORITHM, quality=0.7)
    r.register("gen1", "General 1", domain=Domain.GENERAL, quality=0.5)

    print(f"  Registered: {[p.name for p in r.list_all()]}")

    print("\nFinding security prompts...")
    security = r.find_by_domain(Domain.SECURITY)

    t1 = test_result(
        "find_by_domain(SECURITY) returns 2",
        len(security) == 2,
        f"found: {[p.name for p in security]}"
    )

    print("\nFinding best security prompt...")
    best = r.best_for_domain(Domain.SECURITY)

    t2 = test_result(
        "best_for_domain() returns highest quality",
        best is not None and best.name == "sec2",
        f"best = {best.name if best else 'None'} (quality={best.quality if best else 0})"
    )

    print("\nFinding prompts with quality >= 0.8...")
    high_quality = r.find_by_quality(0.8)

    t3 = test_result(
        "find_by_quality(0.8) returns 2",
        len(high_quality) == 2,
        f"found: {[(p.name, p.quality) for p in high_quality]}"
    )

    print("\nFinding best for empty domain...")
    empty = r.best_for_domain(Domain.DATABASE)

    t4 = test_result(
        "best_for_domain() returns None for empty",
        empty is None,
        f"result = {empty}"
    )

    return all([t1, t2, t3, t4])


def test_selector_classification():
    """Test domain classification."""
    header("TEST 3: Domain Classification")

    test_cases = [
        ("Review for SQL injection vulnerabilities", Domain.SECURITY, ["injection", "vulnerability"]),
        ("Analyze the sorting algorithm complexity", Domain.ALGORITHM, ["algorithm", "complexity", "sort"]),
        ("Write unit tests for this function", Domain.TESTING, ["test"]),
        ("Fix this bug in my code", Domain.DEBUG, ["bug", "fix"]),
        ("Hello world", Domain.GENERAL, []),  # No keywords match
    ]

    results = []
    for text, expected_domain, expected_keywords in test_cases:
        domain, count = classify_domain(text)
        matched = [kw for kw in DOMAIN_KEYWORDS.get(domain, []) if kw in text.lower()]

        passed = domain == expected_domain
        results.append(passed)

        print(f"  Input: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
        print(f"  Expected: {expected_domain.name}, Got: {domain.name}")
        print(f"  Matches: {count} keywords {matched}")
        test_result(f"Classified as {expected_domain.name}", passed)
        print()

    return all(results)


def test_selector_integration():
    """Test selector with registry."""
    header("TEST 4: Selector Integration")

    r = create_default_registry()
    print(f"Using default registry with {len(r)} prompts:")
    for p in r.list_all():
        print(f"  - {p.name} ({p.domain.name}, q={p.quality})")

    test_cases = [
        ("Help me debug this TypeError", "debug"),
        ("Review for SQL injection", "review_security"),
        ("Check the time complexity of this sort", "review_algorithm"),
        ("Generate tests for my API", "test_generate"),
    ]

    print()
    results = []
    for problem, expected in test_cases:
        selected = select_prompt(problem, r)
        passed = selected is not None and selected.name == expected
        results.append(passed)

        print(f"  Problem: \"{problem}\"")
        print(f"  Expected: {expected}")
        print(f"  Selected: {selected.name if selected else 'None'}")
        test_result(f"Selected {expected}", passed)
        print()

    return all(results)


def test_edge_cases():
    """Test edge cases and error handling."""
    header("TEST 5: Edge Cases")

    results = []

    # Empty registry selection
    print("Selecting from empty registry...")
    empty_r = PromptRegistry()
    result = select_prompt("any problem", empty_r)
    t1 = test_result(
        "Empty registry returns None",
        result is None,
        f"result = {result}"
    )
    results.append(t1)

    # Render with missing variable
    print("\nRendering with missing variable...")
    r = PromptRegistry()
    r.register("test", "Hello {name}, you are {age}")
    p = r.get("test")
    rendered = p.render(name="Alice")  # Missing 'age'
    t2 = test_result(
        "Missing variable left as placeholder",
        "{age}" in rendered,
        f"rendered = '{rendered}'"
    )
    results.append(t2)

    # Empty string classification
    print("\nClassifying empty string...")
    domain, count = classify_domain("")
    t3 = test_result(
        "Empty string → GENERAL with 0 matches",
        domain == Domain.GENERAL and count == 0,
        f"domain = {domain.name}, count = {count}"
    )
    results.append(t3)

    # Very long input
    print("\nClassifying very long input...")
    long_input = "security " * 100  # 900 chars
    domain, count = classify_domain(long_input)
    t4 = test_result(
        "Long input still works",
        domain == Domain.SECURITY and count > 0,
        f"domain = {domain.name}, count = {count}"
    )
    results.append(t4)

    # Special characters
    print("\nClassifying with special characters...")
    special = "Fix the SQL injection bug! @#$%^&*()"
    domain, count = classify_domain(special)
    # Note: "bug" + "fix" = 2 DEBUG matches > "injection" = 1 SECURITY match
    # This is correct behavior - DEBUG wins because more keywords matched
    t5 = test_result(
        "Special chars don't break classification",
        domain == Domain.DEBUG,  # DEBUG wins: bug+fix (2) > injection (1)
        f"domain = {domain.name} (bug+fix=2 > injection=1)"
    )
    results.append(t5)

    return all(results)


def test_tags():
    """Test tag-based filtering."""
    header("TEST 6: Tag Filtering")

    r = PromptRegistry()
    r.register("p1", "Prompt 1", tags=["review", "security"])
    r.register("p2", "Prompt 2", tags=["review", "algorithm"])
    r.register("p3", "Prompt 3", tags=["test"])

    print("Registered prompts with tags:")
    for p in r.list_all():
        print(f"  - {p.name}: {p.tags}")

    print("\nFinding prompts with 'review' tag...")
    review = r.find_by_tag("review")
    t1 = test_result(
        "find_by_tag('review') returns 2",
        len(review) == 2,
        f"found: {[p.name for p in review]}"
    )

    print("\nFinding prompts with 'nonexistent' tag...")
    none = r.find_by_tag("nonexistent")
    t2 = test_result(
        "find_by_tag('nonexistent') returns empty",
        len(none) == 0,
        f"found: {[p.name for p in none]}"
    )

    return all([t1, t2])


def test_contains():
    """Test 'in' operator."""
    header("TEST 7: Contains Operator")

    r = PromptRegistry()
    r.register("exists", "I exist")

    t1 = test_result(
        "'exists' in registry",
        "exists" in r,
        f"'exists' in r = {'exists' in r}"
    )

    t2 = test_result(
        "'missing' not in registry",
        "missing" not in r,
        f"'missing' in r = {'missing' in r}"
    )

    return all([t1, t2])


def main():
    """Run all tests and summarize."""
    header("DYNAMIC PROMPT REGISTRY - VISIBLE TEST SUITE")

    print("This test suite shows exactly what's being tested")
    print("and prints results for human review.\n")

    tests = [
        ("Registry Basics", test_registry_basics),
        ("Domain Filtering", test_domain_filtering),
        ("Selector Classification", test_selector_classification),
        ("Selector Integration", test_selector_integration),
        ("Edge Cases", test_edge_cases),
        ("Tag Filtering", test_tags),
        ("Contains Operator", test_contains),
    ]

    results = []
    for name, test_fn in tests:
        try:
            passed = test_fn()
            results.append((name, passed, None))
        except Exception as e:
            results.append((name, False, str(e)))

    # Summary
    header("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for _, p, _ in results if p)

    for name, result, error in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
        if error:
            print(f"      Error: {error}")

    print(f"\n  Total: {passed}/{total} test groups passed")

    if passed == total:
        print("\n  🎉 ALL TESTS PASSED")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test group(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
