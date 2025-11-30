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

## STAGE 1: Baseline Establishment

**ACTION: Capture current state before any changes**

```
1. Run existing tests:
   Command: [test command]
   All tests MUST pass before refactoring starts

2. Document current behavior:
   - Read target files
   - List public functions/methods
   - Note return types and side effects

3. Capture API surface:
   Use Grep: "def ", "class ", "export " in target files
   Document all public interfaces
```

**Test Baseline:**
| Metric | Value |
|--------|-------|
| Tests run | |
| Passed | |
| Failed | |
| Coverage | % |

**ABORT CONDITION:** If any tests fail, fix them first before refactoring.

**API Surface Snapshot:**
```
[file.py]:
  - function_a(param1: type) -> return_type
  - function_b(param1: type, param2: type) -> return_type
  - class ClassName:
      - method_a() -> type
```

---

## STAGE 2: Refactoring Analysis

**ACTION: Classify refactoring and plan atomic steps**

**Refactoring Type:**
- [ ] Extract method/class
- [ ] Rename/move
- [ ] Simplify conditionals
- [ ] Introduce abstraction
- [ ] Remove duplication
- [ ] Performance optimization
- [ ] Architecture change

**Risk Assessment:**
| Factor | Value | Notes |
|--------|-------|-------|
| Risk level | [Low/Med/High] | |
| Files affected | [N] | |
| Breaking changes | [Yes/No] | |
| Reversible | [Yes/No] | |

**Atomic Refactoring Steps:**
Each step must be small enough that:
- Tests can run after it
- It can be reverted independently

| Step | Description | Files | Risk |
|------|-------------|-------|------|
| 1 | [atomic change] | [file] | Low |
| 2 | [atomic change] | [file] | Low |
| 3 | [atomic change] | [file] | Med |

**Invariants to Preserve (⚡ categorical-property-testing):**
| Property | Description | How to Test |
|----------|-------------|-------------|
| [prop1] | [what must stay true] | [assertion] |
| [prop2] | [what must stay true] | [assertion] |

---

## STAGE 3: Incremental Refactoring

**ACTION: Apply each step, test, then proceed**

### Step 1: [Description]
```
BEFORE:
[code before change]

AFTER:
[code after change]

WHY: [reason for this change]
```

**Test after Step 1:**
```bash
Command: [test command]
Result: [PASS/FAIL]
```
- [ ] Tests pass → Proceed to Step 2
- [ ] Tests fail → Revert and debug

### Step 2: [Description]
```
BEFORE:
[code before change]

AFTER:
[code after change]
```

**Test after Step 2:**
```bash
Result: [PASS/FAIL]
```

### Step N: [Continue pattern...]

**Progress Tracker:**
| Step | Applied | Tested | Status |
|------|---------|--------|--------|
| 1 | [ ] | [ ] | |
| 2 | [ ] | [ ] | |
| 3 | [ ] | [ ] | |

**If Any Step Fails:**
```
@if:tests:red
1. Revert the change: git checkout [file]
2. /debug to analyze failure
3. Revise approach and retry
```

---

## STAGE 4: Behavior Verification

**ACTION: Verify refactoring preserved behavior**

**API Comparison (Before vs After):**
| Interface | Before | After | Breaking? |
|-----------|--------|-------|-----------|
| [func_a] | [signature] | [signature] | No |
| [func_b] | [signature] | [signature] | No |

**Property Tests:**
| Property | Status |
|----------|--------|
| [prop1] | PASS/FAIL |
| [prop2] | PASS/FAIL |

**Performance Check:**
| Metric | Before | After | Acceptable? |
|--------|--------|-------|-------------|
| [Time for X] | [value] | [value] | Yes/No |
| [Memory for Y] | [value] | [value] | Yes/No |

---

## STAGE 5: Review

**ACTION: /meta-review the refactored code**

Focus on:
- [ ] Correctness: Same behavior as before?
- [ ] Maintainability: Improved readability?
- [ ] Performance: No degradation?

**Review Verdict:** [APPROVE / REQUEST CHANGES]

---

## Refactoring Summary

| Metric | Before | After | Δ |
|--------|--------|-------|---|
| Lines of Code | | | |
| Cyclomatic Complexity | | | |
| Duplication | | | |
| Test Coverage | | | |

**Files Changed:**
```
[path/file1.py] - [description of change]
[path/file2.py] - [description of change]
```

**Invariants Verified:** ✓ All properties preserved

**Final Status:** [SUCCESS / PARTIAL / ROLLED BACK]

**Commit Message (if successful):**
```
refactor: [brief description]

[Detailed description of what was refactored and why]

- [Change 1]
- [Change 2]

Tested: All tests pass, behavior verified
```
