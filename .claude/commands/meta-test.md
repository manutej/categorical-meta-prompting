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
    STAGE 1: TEST STRATEGY FORMATION
    ═══════════════════════════════════════════════════════

    @run:now
    → /route {target}
    # Analyze component to determine testing strategy

    @run:now
    → /build-prompt "test strategy for ${target}"
    # Construct optimal testing approach

    ◆ strategy:defined

    ═══════════════════════════════════════════════════════
    STAGE 2: PARALLEL TEST GENERATION
    ═══════════════════════════════════════════════════════

    @parallel[
      → Generate unit tests
      → Generate integration tests
      → Generate edge case tests
      → Generate property-based tests
    ]

    ⚡ Skill: "categorical-property-testing"
    # Generate property-based tests from type invariants

    ◆ tests:generated

    ═══════════════════════════════════════════════════════
    STAGE 3: SEQUENTIAL TEST EXECUTION (ORDER MATTERS)
    ═══════════════════════════════════════════════════════

    @sequential[
      @run:now
      → Run unit tests
      ◆ unit:pass OR unit:fail

      @if:unit:pass
        @run:now
        → Run integration tests
        ◆ integration:pass OR integration:fail

      @if:integration:pass
        @run:now
        → Run property tests
        ◆ property:pass OR property:fail
    ]
    # Fast tests first, slow tests only if fast pass

    ═══════════════════════════════════════════════════════
    STAGE 4: COVERAGE ANALYSIS
    ═══════════════════════════════════════════════════════

    @run:now
    → Collect and analyze coverage

    @if:coverage<80
      @run:now
      → /template "additional tests for uncovered paths"
      # Generate tests for uncovered code

    ◆ coverage >= 80

    ═══════════════════════════════════════════════════════
    STAGE 5: FAILURE ANALYSIS & RETRY
    ═══════════════════════════════════════════════════════

    @if:any_tests_failed
      @sequential[
        → /debug ${failed_tests}
        → Fix identified issues
        @retry:2
          → Rerun failed tests
      ]

    ═══════════════════════════════════════════════════════
    STAGE 6: QUALITY GATE
    ═══════════════════════════════════════════════════════

    @run:now
    → Final quality assessment

    ◆ all:tests:pass
    ◆ coverage >= 80
    ◆ no:flaky:tests

  ]
@end
```

---

## Execution Trace

### Stage 1: Test Strategy Formation

```
┌─────────────────────────────────────────────┐
│ @run:now → /route                           │
│                                             │
│ Target: ${target}                           │
│ Type: [function/class/module/service]       │
│ Domain: [detected domain]                   │
│                                             │
│ Dependencies:                               │
│ - [dep1]                                    │
│ - [dep2]                                    │
│                                             │
│ Testing Focus:                              │
│ - [focus area 1]                            │
│ - [focus area 2]                            │
└─────────────────────────────────────────────┘
```

[Analyze target for testing strategy]

```
┌─────────────────────────────────────────────┐
│ @run:now → /build-prompt                    │
│                                             │
│ Test Strategy Prompt:                       │
│ - Context: {context:tester}                 │
│ - Mode: {mode:systematic}                   │
│ - Format: {format:test-cases}               │
│                                             │
│ Strategy Output:                            │
│ - Unit test focus: [areas]                  │
│ - Integration points: [connections]         │
│ - Edge cases: [identified]                  │
│ - Properties to verify: [invariants]        │
└─────────────────────────────────────────────┘
```

---

### Stage 2: Parallel Test Generation

```
@parallel[
┌────────────────────┬────────────────────┬────────────────────┬────────────────────┐
│ UNIT TESTS         │ INTEGRATION        │ EDGE CASES         │ PROPERTY TESTS     │
│                    │ TESTS              │                    │                    │
├────────────────────┼────────────────────┼────────────────────┼────────────────────┤
│                    │                    │                    │                    │
│ □ Happy path       │ □ API contracts    │ □ Null/empty       │ □ Invariants       │
│ □ Error handling   │ □ DB operations    │ □ Boundaries       │ □ Commutativity    │
│ □ Return values    │ □ External calls   │ □ Overflow         │ □ Idempotence      │
│ □ State changes    │ □ Message queues   │ □ Unicode          │ □ Associativity    │
│                    │                    │ □ Concurrency      │ □ Functor laws     │
│                    │                    │                    │                    │
│ Count: [N]         │ Count: [N]         │ Count: [N]         │ Count: [N]         │
└────────────────────┴────────────────────┴────────────────────┴────────────────────┘
]

⚡ Skill: "categorical-property-testing"
   Generating property-based tests:
   - Functor: map(id) == id
   - Monad: bind(return) == id
   - Custom: [domain-specific properties]
```

#### Generated Tests Summary

| Category | Test Count | Focus Areas |
|----------|------------|-------------|
| Unit | | |
| Integration | | |
| Edge Case | | |
| Property | | |
| **Total** | | |

---

### Stage 3: Sequential Test Execution

```
@sequential[
  ┌─────────────────────────────────────────────┐
  │ STEP 1: Unit Tests                          │
  │                                             │
  │ Command: [test runner command]              │
  │                                             │
  │ Results:                                    │
  │ ✓ Passed: [N]                               │
  │ ✗ Failed: [N]                               │
  │ ○ Skipped: [N]                              │
  │                                             │
  │ Time: [duration]                            │
  │ Status: [PASS/FAIL]                         │
  └─────────────────────────────────────────────┘
          ↓ ◆ unit:pass
  ┌─────────────────────────────────────────────┐
  │ STEP 2: Integration Tests                   │
  │                                             │
  │ Command: [test runner command]              │
  │                                             │
  │ Results:                                    │
  │ ✓ Passed: [N]                               │
  │ ✗ Failed: [N]                               │
  │ ○ Skipped: [N]                              │
  │                                             │
  │ Time: [duration]                            │
  │ Status: [PASS/FAIL]                         │
  └─────────────────────────────────────────────┘
          ↓ ◆ integration:pass
  ┌─────────────────────────────────────────────┐
  │ STEP 3: Property Tests                      │
  │                                             │
  │ Command: [hypothesis/quickcheck command]    │
  │                                             │
  │ Results:                                    │
  │ ✓ Properties verified: [N]                  │
  │ ✗ Counterexamples found: [N]                │
  │                                             │
  │ Time: [duration]                            │
  │ Status: [PASS/FAIL]                         │
  └─────────────────────────────────────────────┘
]
```

[Execute tests in sequence]

---

### Stage 4: Coverage Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│                    COVERAGE REPORT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Line Coverage:     [████████░░] 82%                             │
│ Branch Coverage:   [███████░░░] 75%                             │
│ Function Coverage: [█████████░] 90%                             │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Uncovered Areas:                                                 │
│                                                                  │
│ file1.py:45-52    [error handling path]                         │
│ file2.py:120-125  [edge case branch]                            │
│ file3.py:78       [exception handler]                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

```
@if:coverage<80
┌─────────────────────────────────────────────┐
│ Coverage below 80% - generating more tests  │
│                                             │
│ → /template "tests for uncovered paths"     │
│                                             │
│ Targeting:                                  │
│ - [uncovered path 1]                        │
│ - [uncovered path 2]                        │
└─────────────────────────────────────────────┘
```

---

### Stage 5: Failure Analysis & Retry

```
@if:any_tests_failed
┌─────────────────────────────────────────────┐
│ Test failures detected - analyzing          │
│                                             │
│ Failed Tests:                               │
│ 1. [test_name]: [failure reason]            │
│ 2. [test_name]: [failure reason]            │
│                                             │
│ → /debug ${failed_tests}                    │
│                                             │
│ Analysis:                                   │
│ - Root cause: [identified cause]            │
│ - Fix: [proposed fix]                       │
└─────────────────────────────────────────────┘

@retry:2
┌─────────────────────────────────────────────┐
│ Retry attempt ${retry.count}/2              │
│                                             │
│ Rerunning failed tests...                   │
│                                             │
│ Result: [PASS/FAIL]                         │
└─────────────────────────────────────────────┘
```

[Debug and retry failed tests if any]

---

### Stage 6: Quality Gate

```
┌─────────────────────────────────────────────────────────────────┐
│                      QUALITY GATE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ◆ all:tests:pass                                                │
│   Unit Tests:        [✓ PASS / ✗ FAIL]                          │
│   Integration Tests: [✓ PASS / ✗ FAIL]                          │
│   Property Tests:    [✓ PASS / ✗ FAIL]                          │
│                                                                  │
│ ◆ coverage >= 80                                                │
│   Current Coverage:  [X]%  [✓ PASS / ✗ FAIL]                    │
│                                                                  │
│ ◆ no:flaky:tests                                                │
│   Flaky Tests Found: [N]   [✓ PASS / ✗ FAIL]                    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   QUALITY GATE STATUS: [✓ PASSED / ✗ FAILED]                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Test Summary

| Test Type | Total | Passed | Failed | Skipped | Time |
|-----------|-------|--------|--------|---------|------|
| Unit | | | | | |
| Integration | | | | | |
| Edge Case | | | | | |
| Property | | | | | |
| **Total** | | | | | |

**Coverage:**
- Line: X%
- Branch: X%
- Function: X%

**Quality Gate:** [PASSED / FAILED]

**Skills Used:**
- ⚡ categorical-property-testing

**Commands Invoked:**
- /route (strategy)
- /build-prompt (test planning)
- /template (gap coverage)
- /debug (failure analysis)
