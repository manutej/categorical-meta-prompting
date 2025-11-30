---
description: Orchestrated refactoring workflow - analyze, plan, refactor safely with verification
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [refactoring-goal]
---

# Meta-Refactor: Orchestrated Safe Refactoring

Refactor code with full orchestration ensuring behavior preservation.

## Refactoring Goal
$ARGUMENTS

---

## Orchestration Plan

```
@orchestration
  @sequential[

    ═══════════════════════════════════════════════════════
    STAGE 1: BASELINE ESTABLISHMENT
    ═══════════════════════════════════════════════════════

    @parallel[
      → Run existing tests (capture baseline)
      → Analyze current behavior
      → Document current API surface
    ]
    # Establish behavior baseline before any changes

    ◆ baseline:established
    ◆ tests:green

    ═══════════════════════════════════════════════════════
    STAGE 2: REFACTORING ANALYSIS
    ═══════════════════════════════════════════════════════

    @run:now
    → /route {refactoring_goal}
    # Determine refactoring type and approach

    @run:now
    → /build-prompt "safe refactoring plan for ${goal}"
    # Construct refactoring strategy

    ⚡ Skill: "categorical-property-testing"
    # Identify invariants that must be preserved

    ◆ plan:formed
    ◆ invariants:identified

    ═══════════════════════════════════════════════════════
    STAGE 3: INCREMENTAL REFACTORING WITH VERIFICATION
    ═══════════════════════════════════════════════════════

    @loop:for-each:refactoring_step[
      @sequential[
        @run:now
        → Apply single refactoring step

        @run:now
        → Run tests
        ◆ tests:green

        @if:tests:red
          @run:now
          → Revert step
          → /debug ${failure}
      ]
    ]
    # Each step verified before proceeding

    ═══════════════════════════════════════════════════════
    STAGE 4: BEHAVIOR VERIFICATION
    ═══════════════════════════════════════════════════════

    @parallel[
      → Compare API surface: before vs after
      → Run property tests
      → Verify performance characteristics
    ]

    ◆ api:compatible OR api:intentionally_changed
    ◆ properties:preserved
    ◆ performance:acceptable

    ═══════════════════════════════════════════════════════
    STAGE 5: REVIEW REFACTORED CODE
    ═══════════════════════════════════════════════════════

    @run:now
    → /meta-review ${refactored_code}
    # Full multi-dimensional review

    ◆ review:approved

  ]
@end
```

---

## Execution Trace

### Stage 1: Baseline Establishment

```
@parallel[
┌───────────────────┬───────────────────┬───────────────────┐
│ TEST BASELINE     │ BEHAVIOR          │ API SURFACE       │
│                   │ ANALYSIS          │                   │
├───────────────────┼───────────────────┼───────────────────┤
│                   │                   │                   │
│ Running tests...  │ Documenting:      │ Public interfaces:│
│                   │ - Input/output    │ - Functions       │
│ ✓ Passed: [N]     │ - Side effects    │ - Classes         │
│ ✗ Failed: [N]     │ - Error behavior  │ - Types           │
│                   │ - Edge cases      │ - Constants       │
│                   │                   │                   │
│ Coverage: [X]%    │ Behavior Doc: ✓   │ API Snapshot: ✓   │
└───────────────────┴───────────────────┴───────────────────┘
]
```

**Baseline Status:**
- Tests: [all passing / some failing]
- Coverage: [X]%
- API Surface: [documented]
- Behavior: [documented]

---

### Stage 2: Refactoring Analysis

```
┌─────────────────────────────────────────────┐
│ @run:now → /route                           │
│                                             │
│ Refactoring Type Detected:                  │
│ □ Extract method/class                      │
│ □ Rename/move                               │
│ □ Simplify conditionals                     │
│ □ Introduce abstraction                     │
│ □ Remove duplication                        │
│ □ Performance optimization                  │
│ □ Architecture change                       │
│                                             │
│ Risk Level: [Low/Medium/High]               │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ @run:now → /build-prompt                    │
│                                             │
│ Refactoring Plan:                           │
│                                             │
│ Step 1: [first atomic refactoring]          │
│ Step 2: [second atomic refactoring]         │
│ Step 3: [third atomic refactoring]          │
│ ...                                         │
│                                             │
│ Total Steps: [N]                            │
│ Estimated Impact: [scope]                   │
└─────────────────────────────────────────────┘

⚡ Skill: "categorical-property-testing"
┌─────────────────────────────────────────────┐
│ Invariants to Preserve:                     │
│                                             │
│ - [invariant 1]: [description]              │
│ - [invariant 2]: [description]              │
│ - [invariant 3]: [description]              │
│                                             │
│ Property Tests Generated: [N]               │
└─────────────────────────────────────────────┘
```

---

### Stage 3: Incremental Refactoring

```
@loop:for-each:refactoring_step

┌─────────────────────────────────────────────┐
│ STEP 1/N: [step description]                │
│                                             │
│ @run:now → Apply step                       │
│ Changes: [files affected]                   │
│                                             │
│ @run:now → Run tests                        │
│ Result: [✓ PASS / ✗ FAIL]                   │
│                                             │
│ @if:tests:red                               │
│   → Reverting step                          │
│   → /debug ${failure}                       │
└─────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────┐
│ STEP 2/N: [step description]                │
│                                             │
│ @run:now → Apply step                       │
│ Changes: [files affected]                   │
│                                             │
│ @run:now → Run tests                        │
│ Result: [✓ PASS / ✗ FAIL]                   │
└─────────────────────────────────────────────┘
          ↓
         ...
```

**Refactoring Progress:**
| Step | Description | Status | Tests |
|------|-------------|--------|-------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

### Stage 4: Behavior Verification

```
@parallel[
┌───────────────────┬───────────────────┬───────────────────┐
│ API COMPARISON    │ PROPERTY TESTS    │ PERFORMANCE       │
├───────────────────┼───────────────────┼───────────────────┤
│                   │                   │                   │
│ Before vs After:  │ Invariants:       │ Before:           │
│                   │                   │ - [metric]: [val] │
│ + Added: [N]      │ ✓ [prop1]: PASS   │                   │
│ - Removed: [N]    │ ✓ [prop2]: PASS   │ After:            │
│ ~ Changed: [N]    │ ✓ [prop3]: PASS   │ - [metric]: [val] │
│                   │                   │                   │
│ Breaking: [Y/N]   │ All: [PASS/FAIL]  │ Δ: [+/-X%]        │
└───────────────────┴───────────────────┴───────────────────┘
]
```

**Verification Summary:**
- API Compatible: [Yes / No - intentional changes listed]
- Properties Preserved: [Yes / No]
- Performance: [Acceptable / Degraded / Improved]

---

### Stage 5: Review

```
┌─────────────────────────────────────────────┐
│ @run:now → /meta-review                     │
│                                             │
│ Reviewing refactored code through:          │
│ - Correctness review                        │
│ - Maintainability review                    │
│ - Performance review                        │
│                                             │
│ Review Status: [PENDING]                    │
└─────────────────────────────────────────────┘
```

[Execute /meta-review for full review]

---

## Refactoring Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Lines of Code | | | |
| Cyclomatic Complexity | | | |
| Test Coverage | | | |
| Duplication | | | |

**Steps Completed:** [N]/[Total]

**Files Changed:**
- [file1]: [change summary]
- [file2]: [change summary]

**Invariants Verified:**
- ✓ [invariant 1]
- ✓ [invariant 2]

**Final Status:** [SUCCESS / PARTIAL / ROLLBACK]

**Commands Invoked:**
- /route (analysis)
- /build-prompt (planning)
- /debug (if failures)
- /meta-review (final review)

**Skills Used:**
- ⚡ categorical-property-testing
