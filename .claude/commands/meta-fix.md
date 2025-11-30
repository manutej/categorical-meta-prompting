---
description: Full orchestrated bug fix workflow - debug, analyze root cause, fix, verify, review
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [error-or-symptom]
---

# Meta-Fix: Orchestrated Bug Resolution

Fix a bug with full prompt orchestration, coordinating debugging, fixing, and verification.

## Bug/Error
$ARGUMENTS

---

## Orchestration Plan

```
@orchestration
  @sequential[

    ═══════════════════════════════════════════════════════
    STAGE 1: LOCATE & TRIAGE
    ═══════════════════════════════════════════════════════

    @run:now
    → Parse error message/symptoms
    → Search codebase for error location
    → Read relevant files

    ◆ location:found

    ═══════════════════════════════════════════════════════
    STAGE 2: REPRODUCE & ISOLATE
    ═══════════════════════════════════════════════════════

    @run:now
    → /debug {error}
    → Create minimal reproduction case

    ◆ reproduction:confirmed OR escalate

    ═══════════════════════════════════════════════════════
    STAGE 3: ROOT CAUSE ANALYSIS
    ═══════════════════════════════════════════════════════

    @parallel[
      → Trace code path
      → Trace data flow
      → Check state transitions
    ]
    → Synthesize into root cause

    ◆ root_cause:identified

    ═══════════════════════════════════════════════════════
    STAGE 4: FIX IMPLEMENTATION
    ═══════════════════════════════════════════════════════

    @run:now
    → Implement minimal fix
    → Add regression test BEFORE running

    @if:security-related
      ⚡ Skill: "security-analysis"

    ◆ fix:implemented

    ═══════════════════════════════════════════════════════
    STAGE 5: VERIFICATION
    ═══════════════════════════════════════════════════════

    @sequential[
      → Confirm bug no longer reproduces
      → Run full test suite
      → Verify no regressions
    ]

    ◆ verified OR @fallback → /rmp

    ═══════════════════════════════════════════════════════
    STAGE 6: REVIEW & COMMIT
    ═══════════════════════════════════════════════════════

    @run:now
    → /review ${changes}
    → Prepare commit message

    ◆ review:approved

  ]
@end
```

---

## STAGE 1: Locate & Triage

**ACTION: Parse the error and find its location**

```
1. Extract from error message:
   - Error type (e.g., TypeError, ValueError, crash)
   - File and line number (if in traceback)
   - Key error text to search for

2. Search codebase:
   Use Grep: "error message text" or exception type
   Use Glob: find related files by name pattern
   Use Read: examine the file where error occurs
```

**Error Parsing:**
| Field | Extracted Value |
|-------|-----------------|
| Error Type | |
| Location (file:line) | |
| Key Message | |
| Trigger Condition | |

**Files to Examine:**
1. [Primary file where error occurs]
2. [Callers of the failing function]
3. [Related test files]

**ABORT CONDITIONS:**
- Cannot find error location → Ask for more context (stack trace, logs)
- Error in third-party code → Focus on our code that calls it
- Multiple unrelated errors → Triage and fix one at a time

---

## STAGE 2: Reproduce & Isolate

**ACTION: Confirm the bug and create minimal reproduction**

**Reproduction Steps:**
```
1. [Step to set up environment/state]
2. [Step to trigger the bug]
3. [Expected vs actual result]
```

**Minimal Reproduction:**
```python
# Smallest code that triggers the bug
[code snippet]
```

**Isolation Questions:**
- [ ] Does it happen every time or intermittently?
- [ ] Does it depend on specific input?
- [ ] Does it depend on environment/config?
- [ ] When did it start? (recent change?)

**Reproduction Status:**
- [ ] **Consistently reproducible** → Proceed to Stage 3
- [ ] **Intermittent** → Add logging, gather more data
- [ ] **Cannot reproduce** → Need more information (HALT)

---

## STAGE 3: Root Cause Analysis

**ACTION: Analyze from three perspectives in parallel**

**Code Path Analysis:**
```
Function call chain:
caller()
  → function_a()
    → function_b() [ERROR HERE]
      → function_c()

At function_b line X, the issue is:
[description of what goes wrong]
```

**Data Flow Analysis:**
```
Input: [what data comes in]
Transform: [what happens to it]
At point X: [data becomes invalid because...]
Output: [wrong/missing/corrupted]
```

**State Analysis:**
```
Expected state: [what should be true]
Actual state: [what is actually true]
Discrepancy: [why they differ]
```

**Root Cause Synthesis:**
| Hypothesis | Evidence | Confidence |
|------------|----------|------------|
| [Most likely] | [specific evidence] | HIGH |
| [Alternative 1] | [evidence] | MEDIUM |
| [Alternative 2] | [evidence] | LOW |

**Selected Root Cause:**
```
The bug occurs because [X] when [condition],
causing [Y] instead of [expected Z].
```

---

## STAGE 4: Fix Implementation

**ACTION: Implement minimal fix and add regression test**

**Fix Strategy:**
- [ ] Direct fix at root cause
- [ ] Add input validation
- [ ] Add null/error check
- [ ] Fix data transformation
- [ ] Fix state management

**The Fix:**
```
File: [path/to/file.py]
Line: [N]

BEFORE:
[old code]

AFTER:
[new code]

WHY: [explanation of why this fixes the root cause]
```

**Regression Test (ADD FIRST):**
```python
def test_regression_[bug_description]():
    """Regression test for [bug description].

    Previously, [what went wrong].
    This test ensures [what should happen].
    """
    # Arrange
    [setup that triggers the bug]

    # Act
    [action that used to fail]

    # Assert
    [verification that bug is fixed]
```

**Security Check (if applicable):**
```
@if:security-related
⚡ Skill: "security-analysis"

- [ ] Injection vectors checked
- [ ] Auth/authz implications reviewed
- [ ] Data exposure risk assessed
- [ ] Error messages sanitized
```

---

## STAGE 5: Verification

**ACTION: Verify the fix works and nothing else broke**

**Step 1: Bug No Longer Reproduces**
```
Running reproduction steps...
Command: [reproduction command]
Result: [PASS - bug does not occur / FAIL - still occurs]
```

**Step 2: Regression Test Passes**
```
Running new test...
Command: pytest [test_file]::[test_name] -v
Result: [PASS / FAIL]
```

**Step 3: Full Test Suite**
```
Running all tests...
Command: [test command]
Results:
  Passed: [N]
  Failed: [N]
  Skipped: [N]
Status: [PASS - all green / FAIL - regressions found]
```

**If Verification Fails:**
```
@fallback:verification_failed
→ /rmp "alternative fix for [error]" 8

Attempting alternative approach...
[document what alternative was tried]
```

---

## STAGE 6: Review & Commit

**ACTION: Review changes and prepare commit**

**Changes Summary:**
| File | Type | Lines Changed |
|------|------|---------------|
| [file] | FIX | +X -Y |
| [file] | TEST | +X |

**Review Checklist:**
- [ ] Fix addresses root cause (not just symptoms)
- [ ] No unintended side effects
- [ ] Test covers the specific bug
- [ ] Code follows project conventions
- [ ] No debug code left in

**Commit Message:**
```
fix: [brief description of what was fixed]

[Longer description of the bug and fix]

Root cause: [what caused the bug]
Fix: [what was changed to fix it]

Tested: [how it was verified]
```

---

## Fix Summary

| Stage | Status | Key Finding |
|-------|--------|-------------|
| 1. Locate | | [file:line] |
| 2. Reproduce | | [reproducible?] |
| 3. Root Cause | | [the cause] |
| 4. Fix | | [the solution] |
| 5. Verify | | [tests pass?] |
| 6. Review | | [approved?] |

**Files Changed:**
```
[path/file.py] - [description of change]
[path/test_file.py] - Added regression test
```

**Confidence:** [HIGH/MEDIUM/LOW] - [why]
**Risk:** [LOW/MEDIUM/HIGH] - [potential side effects]

**Ready for commit:** [YES/NO]
