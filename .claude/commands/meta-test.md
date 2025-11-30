---
description: Comprehensive orchestrated testing workflow with multiple test types and coverage analysis
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [component-or-feature]
---

# Meta-Test: Orchestrated Comprehensive Testing

Execute a full testing workflow with coordinated test types and analysis.

## Test Target
$ARGUMENTS

---

## Orchestration Plan

```
@orchestration
  @sequential[

    ═══════════════════════════════════════════════════════
    STAGE 1: DISCOVER TEST ENVIRONMENT
    ═══════════════════════════════════════════════════════

    @run:now
    → Detect test framework and runner
    → Find existing tests
    → Identify target code to test

    ◆ environment:detected

    ═══════════════════════════════════════════════════════
    STAGE 2: ANALYZE & PLAN
    ═══════════════════════════════════════════════════════

    @run:now
    → Read target code
    → Identify testable units
    → Plan test categories

    ◆ strategy:defined

    ═══════════════════════════════════════════════════════
    STAGE 3: GENERATE TESTS
    ═══════════════════════════════════════════════════════

    @parallel[
      → Unit tests (functions/methods)
      → Integration tests (interactions)
      → Edge case tests (boundaries)
      → Property tests (invariants)
    ]

    ⚡ Skill: "categorical-property-testing"

    ◆ tests:generated

    ═══════════════════════════════════════════════════════
    STAGE 4: EXECUTE TESTS (fast → slow)
    ═══════════════════════════════════════════════════════

    @sequential[
      → Run unit tests first
      @if:unit:pass → Run integration tests
      @if:integration:pass → Run property tests
    ]

    ◆ execution:complete

    ═══════════════════════════════════════════════════════
    STAGE 5: COVERAGE & GAP ANALYSIS
    ═══════════════════════════════════════════════════════

    @run:now
    → Measure coverage
    → Identify uncovered code
    → Generate additional tests if < 80%

    ◆ coverage >= 80 OR gaps:documented

    ═══════════════════════════════════════════════════════
    STAGE 6: FAILURE HANDLING
    ═══════════════════════════════════════════════════════

    @if:any_tests_failed
      → /debug ${failures}
      → Fix or document issues
      @retry:2 → Rerun failed tests

    ◆ all:tests:pass OR failures:documented

  ]
@end
```

---

## STAGE 1: Discover Test Environment

**ACTION: Detect testing infrastructure**

```
1. Find test framework:
   Use Glob: **/pytest.ini, **/setup.cfg, **/pyproject.toml, **/jest.config.*, **/package.json
   Use Grep: "pytest", "unittest", "jest", "mocha", "go test"

2. Find existing tests:
   Use Glob: **/*test*.py, **/*.test.ts, **/*_test.go

3. Identify test runner command:
   [Detected command based on framework]
```

**Environment Detected:**
| Aspect | Value |
|--------|-------|
| Language | [Python/TypeScript/Go/...] |
| Framework | [pytest/jest/go test/...] |
| Test command | [e.g., `pytest -v`] |
| Coverage command | [e.g., `pytest --cov`] |
| Existing tests | [count] in [locations] |

**Target Code:**
| File | Functions/Classes | Current Test Coverage |
|------|-------------------|----------------------|
| [path] | [list] | [None/Partial/Full] |

---

## STAGE 2: Analyze & Plan

**ACTION: Read target and plan tests**

```
1. Read the target code:
   Use Read: [target files]

2. For each function/class, identify:
   - Happy path behavior
   - Error conditions
   - Edge cases
   - Dependencies to mock
```

**Testable Units:**
| Unit | Type | Inputs | Outputs | Edge Cases |
|------|------|--------|---------|------------|
| [function_name] | function | [types] | [type] | [list] |
| [ClassName] | class | [constructor] | [methods] | [list] |

**Test Plan:**
| Category | Count | Focus |
|----------|-------|-------|
| Unit | [N] | [individual functions] |
| Integration | [N] | [component interactions] |
| Edge cases | [N] | [boundary conditions] |
| Property | [N] | [invariants] |

---

## STAGE 3: Generate Tests

**ACTION: Write tests for each category**

### Unit Tests
```python
# Test file: [path/test_target.py]

def test_[function]_happy_path():
    """Test [function] with normal input."""
    # Arrange
    [setup]
    # Act
    result = [function call]
    # Assert
    assert result == [expected]

def test_[function]_error_case():
    """Test [function] raises on invalid input."""
    with pytest.raises([ExceptionType]):
        [function call with bad input]
```

### Integration Tests
```python
def test_[component]_integration():
    """Test [component] works with [dependency]."""
    # Arrange
    [setup components]
    # Act
    [trigger interaction]
    # Assert
    [verify end-to-end behavior]
```

### Edge Case Tests
```python
def test_[function]_empty_input():
    """Test [function] handles empty input."""
    assert [function]([]) == [expected]

def test_[function]_boundary():
    """Test [function] at boundary values."""
    assert [function](MAX_VALUE) == [expected]
    assert [function](MIN_VALUE) == [expected]
```

### Property Tests (⚡ categorical-property-testing)
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_[function]_property(input_list):
    """[Property description]."""
    result = [function](input_list)
    assert [property holds]  # e.g., len(result) == len(input_list)
```

**Generated Tests Summary:**
| Category | Count | File |
|----------|-------|------|
| Unit | | |
| Integration | | |
| Edge case | | |
| Property | | |
| **Total** | | |

---

## STAGE 4: Execute Tests

**ACTION: Run tests in order (fast → slow)**

### Step 1: Unit Tests
```bash
Command: [test command for unit tests]
```

**Results:**
| Metric | Value |
|--------|-------|
| Passed | |
| Failed | |
| Skipped | |
| Time | |
| Status | [PASS/FAIL] |

### Step 2: Integration Tests (if unit passed)
```bash
Command: [test command for integration tests]
```

**Results:**
| Metric | Value |
|--------|-------|
| Passed | |
| Failed | |
| Time | |
| Status | [PASS/FAIL] |

### Step 3: Property Tests (if integration passed)
```bash
Command: [test command for property tests]
```

**Results:**
| Metric | Value |
|--------|-------|
| Properties verified | |
| Counterexamples | |
| Status | [PASS/FAIL] |

---

## STAGE 5: Coverage & Gap Analysis

**ACTION: Measure and analyze coverage**

```bash
Command: [coverage command, e.g., pytest --cov=src --cov-report=term-missing]
```

**Coverage Report:**
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Line coverage | X% | 80% | [PASS/FAIL] |
| Branch coverage | X% | 70% | [PASS/FAIL] |
| Function coverage | X% | 90% | [PASS/FAIL] |

**Uncovered Code:**
| File | Lines | Reason | Additional Test Needed |
|------|-------|--------|------------------------|
| [path] | [N-M] | [why not covered] | [test to add] |

**Gap Filling (if < 80%):**
```python
# Additional test for uncovered path
def test_[uncovered_scenario]():
    """Cover [description of uncovered code]."""
    [test implementation]
```

---

## STAGE 6: Failure Handling

**ACTION: Debug and fix any failures**

```
@if:any_tests_failed

Failed Test Analysis:
| Test | Error | Root Cause | Fix |
|------|-------|------------|-----|
| [name] | [error msg] | [why] | [how to fix] |
```

**Retry Log:**
| Attempt | Tests Run | Passed | Failed |
|---------|-----------|--------|--------|
| 1 | | | |
| 2 | | | |

**Unresolved Failures (if any):**
```
Test: [name]
Issue: [description]
Blocking: [YES/NO - why it can't be fixed now]
```

---

## Test Summary

**Results:**
| Category | Total | Passed | Failed | Coverage |
|----------|-------|--------|--------|----------|
| Unit | | | | |
| Integration | | | | |
| Edge Case | | | | |
| Property | | | | |
| **Total** | | | | **X%** |

**Quality Gate:**
- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] No flaky tests detected

**Status:** [PASSED / FAILED - list blockers]

**Test Files Created:**
```
[list of new test files with paths]
```

**Skills Used:**
- ⚡ categorical-property-testing

**Commands Used:**
- [test runner command]
- [coverage command]
