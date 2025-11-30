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
    STAGE 1: TRIAGE & REPRODUCTION
    ═══════════════════════════════════════════════════════

    @run:now
    → /debug {error}
    # Systematic debugging: reproduce → isolate → hypothesize

    ◆ reproduction:confirmed OR reproduction:intermittent

    ═══════════════════════════════════════════════════════
    STAGE 2: ROOT CAUSE ANALYSIS (PARALLEL HYPOTHESES)
    ═══════════════════════════════════════════════════════

    @parallel[
      → /build-prompt "analyze code path for ${error}"
      → /build-prompt "analyze data flow for ${error}"
      → /build-prompt "analyze state transitions for ${error}"
    ]
    # Generate multiple analysis perspectives

    ◆ root_cause:identified

    ═══════════════════════════════════════════════════════
    STAGE 3: FIX IMPLEMENTATION
    ═══════════════════════════════════════════════════════

    @run:now
    → /template "fix for ${root_cause}"
    # Construct fix with visible steps

    @if:security-related
      ⚡ Skill: "security-analysis"
      # Extra scrutiny for security bugs

    ◆ fix:implemented

    ═══════════════════════════════════════════════════════
    STAGE 4: VERIFICATION (SEQUENTIAL - ORDER MATTERS)
    ═══════════════════════════════════════════════════════

    @sequential[
      @run:now
      → Reproduce original bug
      ◆ bug:no-longer-reproduces

      @run:now
      → Run existing tests
      ◆ tests:pass

      @run:now
      → Add regression test for this bug
      ◆ regression_test:added
    ]

    ═══════════════════════════════════════════════════════
    STAGE 5: REVIEW & CONFIRM
    ═══════════════════════════════════════════════════════

    @run:now
    → /review ${fix}
    # Domain-aware review of the fix

    ◆ review:approved
    ◆ no:regressions

    ═══════════════════════════════════════════════════════
    STAGE 6: FALLBACK - ESCALATE IF STUCK
    ═══════════════════════════════════════════════════════

    @fallback:verification_failed
      @run:now
      → /rmp "alternative approach to fix ${error}" 8
      # If verification fails, use RMP for alternative

  ]
@end
```

---

## Execution Trace

### Stage 1: Triage & Reproduction

```
┌─────────────────────────────────────────────┐
│ @run:now → /debug                           │
│                                             │
│ PHASE 1: REPRODUCE                          │
│ - Exact reproduction steps                  │
│ - Environment conditions                    │
│ - Input that triggers bug                   │
│                                             │
│ PHASE 2: ISOLATE                            │
│ - Minimal reproduction case                 │
│ - Component isolation                       │
│                                             │
│ PHASE 3: HYPOTHESIZE                        │
│ - Likely causes ranked                      │
└─────────────────────────────────────────────┘
```

[Execute /debug command here]

**Reproduction Status:**
- [ ] Consistently reproducible
- [ ] Intermittently reproducible
- [ ] Cannot reproduce (need more info)

---

### Stage 2: Root Cause Analysis

```
┌───────────────────┬───────────────────┬───────────────────┐
│ @parallel[1/3]    │ @parallel[2/3]    │ @parallel[3/3]    │
│                   │                   │                   │
│ Code Path         │ Data Flow         │ State             │
│ Analysis          │ Analysis          │ Transitions       │
│                   │                   │                   │
│ Where does        │ What data is      │ What state        │
│ execution go?     │ corrupted/wrong?  │ is unexpected?    │
└───────────────────┴───────────────────┴───────────────────┘
```

[Execute three parallel analyses here]

**Root Cause Synthesis:**
| Hypothesis | Evidence | Confidence |
|------------|----------|------------|
| [Cause 1] | | High/Med/Low |
| [Cause 2] | | High/Med/Low |
| [Cause 3] | | High/Med/Low |

**Selected Root Cause:** [Most likely cause with reasoning]

---

### Stage 3: Fix Implementation

```
┌─────────────────────────────────────────────┐
│ @run:now → /template "fix for ${root_cause}"│
│                                             │
│ Template v0: [empty]                        │
│     ↓                                       │
│ Template v1: [add fix approach]             │
│     ↓                                       │
│ Template v2: [add edge case handling]       │
│     ↓                                       │
│ Template v3: [add error handling]           │
│     ↓                                       │
│ Final Fix: [complete implementation]        │
└─────────────────────────────────────────────┘
```

[Execute /template for fix construction here]

**Security Check:**
```
@if:security-related
⚡ Skill: "security-analysis"
```
- [ ] Injection prevention
- [ ] Authentication/Authorization
- [ ] Data validation
- [ ] Error disclosure

---

### Stage 4: Verification

```
@sequential[
  ┌─────────────────────────────────────────┐
  │ Step 1: Reproduce original bug          │
  │                                         │
  │ [Execute reproduction steps]            │
  │                                         │
  │ Expected: Bug should NOT reproduce      │
  │ Result: [PASS/FAIL]                     │
  └─────────────────────────────────────────┘
          ↓ ◆ bug:no-longer-reproduces
  ┌─────────────────────────────────────────┐
  │ Step 2: Run existing tests              │
  │                                         │
  │ [Execute test suite]                    │
  │                                         │
  │ Expected: All tests pass                │
  │ Result: [PASS/FAIL]                     │
  └─────────────────────────────────────────┘
          ↓ ◆ tests:pass
  ┌─────────────────────────────────────────┐
  │ Step 3: Add regression test             │
  │                                         │
  │ Test Name: test_regression_{bug_id}     │
  │ Test Location: [file path]              │
  │                                         │
  │ Result: [ADDED]                         │
  └─────────────────────────────────────────┘
]
```

[Execute verification sequence here]

---

### Stage 5: Review

```
┌─────────────────────────────────────────────┐
│ @run:now → /review                          │
│                                             │
│ Focus Areas:                                │
│ - Fix correctness                           │
│ - Side effects                              │
│ - Performance impact                        │
│ - Code style                                │
│                                             │
│ Review Status: [PENDING/APPROVED/CHANGES]   │
└─────────────────────────────────────────────┘
```

[Execute /review here]

---

### Stage 6: Fallback (if needed)

```
@fallback:verification_failed
┌─────────────────────────────────────────────┐
│ Verification failed - trying alternative    │
│                                             │
│ → /rmp "alternative fix approach" 8         │
│                                             │
│ RMP will iterate until quality >= 8         │
└─────────────────────────────────────────────┘
```

[Execute /rmp fallback if verification fails]

---

## Fix Summary

| Stage | Status | Details |
|-------|--------|---------|
| Reproduction | | |
| Root Cause | | |
| Fix | | |
| Verification | | |
| Review | | |

**Files Changed:**
- [file1.py]: [what changed]
- [file2.py]: [what changed]

**Regression Test Added:**
- [test location and name]

**Confidence Level:** [High/Medium/Low]
**Risk Assessment:** [Low/Medium/High]
