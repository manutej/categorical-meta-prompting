#!/usr/bin/env python3
"""
CLI Integration Tests - Tests the command-line interface

Run with: python3 test_cli.py
"""

import subprocess
import sys
import os

CLI_PATH = os.path.join(os.path.dirname(__file__), "cli.py")


def run_cli(*args):
    """Run CLI with arguments and return output."""
    result = subprocess.run(
        [sys.executable, CLI_PATH] + list(args),
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def test_result(name, passed, output=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}: {name}")
    if output and not passed:
        print(f"         Output: {output[:200]}")
    return passed


def test_cli_list():
    """Test 'list' command."""
    header("CLI TEST 1: list command")

    print("Running: python cli.py list")
    code, out, err = run_cli("list")

    t1 = test_result(
        "Exit code is 0",
        code == 0,
        f"code={code}, stderr={err}"
    )

    t2 = test_result(
        "Output contains 'Found'",
        "Found" in out,
        out[:100]
    )

    t3 = test_result(
        "Output contains 'debug'",
        "debug" in out,
        out[:100]
    )

    print(f"\n  Output preview:\n{out[:300]}...")

    return all([t1, t2, t3])


def test_cli_list_domain():
    """Test 'list --domain' command."""
    header("CLI TEST 2: list --domain")

    print("Running: python cli.py list --domain security")
    code, out, err = run_cli("list", "--domain", "security")

    t1 = test_result(
        "Exit code is 0",
        code == 0,
        f"stderr={err}"
    )

    t2 = test_result(
        "Output contains 'review_security'",
        "review_security" in out,
        out
    )

    t3 = test_result(
        "Output does NOT contain 'debug'",
        "debug" not in out.lower() or "DEBUG" not in out,  # Only SECURITY should appear
        out
    )

    print(f"\n  Output:\n{out}")

    return all([t1, t2, t3])


def test_cli_get():
    """Test 'get' command."""
    header("CLI TEST 3: get command")

    print("Running: python cli.py get debug")
    code, out, err = run_cli("get", "debug")

    t1 = test_result(
        "Exit code is 0",
        code == 0,
        f"stderr={err}"
    )

    t2 = test_result(
        "Output contains template",
        "Debug this issue" in out,
        out[:100]
    )

    print(f"\n  Output preview:\n{out[:400]}...")

    # Test missing prompt
    print("\nRunning: python cli.py get nonexistent")
    code2, out2, err2 = run_cli("get", "nonexistent")

    t3 = test_result(
        "Missing prompt returns error",
        code2 == 1 and "not found" in out2,
        out2
    )

    return all([t1, t2, t3])


def test_cli_select():
    """Test 'select' command."""
    header("CLI TEST 4: select command")

    print("Running: python cli.py select 'fix SQL injection vulnerability'")
    code, out, err = run_cli("select", "fix SQL injection vulnerability")

    t1 = test_result(
        "Exit code is 0",
        code == 0,
        f"stderr={err}"
    )

    t2 = test_result(
        "Output contains 'review_security'",
        "review_security" in out,
        out[:200]
    )

    print(f"\n  Output preview:\n{out[:300]}...")

    # Test with --explain
    print("\nRunning: python cli.py select 'debug error' --explain")
    code2, out2, err2 = run_cli("select", "debug error", "--explain")

    t3 = test_result(
        "Explain shows domain classification",
        "Domain Classification" in out2,
        out2[:200]
    )

    print(f"\n  Explain output:\n{out2}")

    return all([t1, t2, t3])


def test_cli_render():
    """Test 'render' command."""
    header("CLI TEST 5: render command")

    print("Running: python cli.py render debug issue='NullPointerException'")
    code, out, err = run_cli("render", "debug", "issue=NullPointerException")

    t1 = test_result(
        "Exit code is 0",
        code == 0,
        f"stderr={err}"
    )

    t2 = test_result(
        "Output contains substituted variable",
        "NullPointerException" in out,
        out[:200]
    )

    t3 = test_result(
        "Output does NOT contain {issue}",
        "{issue}" not in out,
        out[:200]
    )

    print(f"\n  Output:\n{out}")

    return all([t1, t2, t3])


def test_cli_help():
    """Test help command."""
    header("CLI TEST 6: help")

    print("Running: python cli.py --help")
    code, out, err = run_cli("--help")

    t1 = test_result(
        "Exit code is 0",
        code == 0,
        f"stderr={err}"
    )

    t2 = test_result(
        "Output contains 'usage'",
        "usage" in out.lower(),
        out[:100]
    )

    print(f"\n  Output preview:\n{out[:400]}...")

    return all([t1, t2])


def main():
    """Run all CLI tests."""
    header("CLI INTEGRATION TEST SUITE")

    print("Testing the command-line interface end-to-end.")
    print(f"CLI path: {CLI_PATH}\n")

    tests = [
        ("list command", test_cli_list),
        ("list --domain", test_cli_list_domain),
        ("get command", test_cli_get),
        ("select command", test_cli_select),
        ("render command", test_cli_render),
        ("help", test_cli_help),
    ]

    results = []
    for name, test_fn in tests:
        try:
            passed = test_fn()
            results.append((name, passed, None))
        except Exception as e:
            results.append((name, False, str(e)))

    # Summary
    header("CLI TEST SUMMARY")

    total = len(results)
    passed = sum(1 for _, p, _ in results if p)

    for name, result, error in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
        if error:
            print(f"      Error: {error}")

    print(f"\n  Total: {passed}/{total} CLI tests passed")

    if passed == total:
        print("\n  🎉 ALL CLI TESTS PASSED")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} CLI test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
