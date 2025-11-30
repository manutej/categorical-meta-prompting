---
description: Systematic debugging with hypothesis-driven approach
allowed-tools: Read, Grep, Glob, Bash(git diff:*), Bash(git log:*), Bash(python:*), Bash(node:*), Bash(npm test:*), Bash(pytest:*)
argument-hint: [error-or-symptom]
---

# Systematic Debug Protocol

## Symptom
$ARGUMENTS

## Phase 1: REPRODUCE

First, establish a reliable reproduction:

1. What exact steps trigger the issue?
2. Is it consistent or intermittent?
3. What's the exact error message/behavior?

If you have access to the error, show it. If not, ask for:
- Error message/stack trace
- Steps to reproduce
- Expected vs actual behavior

## Phase 2: ISOLATE

Narrow down the scope:

1. **When did it start?** Check recent changes:
   !`git log --oneline -10 2>/dev/null || echo "No git history available"`

2. **What changed?** Look at recent diffs if applicable

3. **Minimal case**: What's the smallest input that fails?

## Phase 3: HYPOTHESIZE

Generate ranked hypotheses:

| # | Hypothesis | Likelihood | How to Test |
|---|-----------|------------|-------------|
| 1 | [Most likely cause] | High | [Specific test] |
| 2 | [Second possibility] | Medium | [Specific test] |
| 3 | [Less likely cause] | Low | [Specific test] |

## Phase 4: TEST

For each hypothesis (starting with most likely):

1. Design a test that would confirm/refute it
2. Execute the test
3. Record the result
4. If confirmed → proceed to fix
5. If refuted → next hypothesis

## Phase 5: FIX

Once root cause is identified:

1. **Minimal fix**: What's the smallest change that fixes it?
2. **Side effects**: What else might this change affect?
3. **Test**: Does the fix actually work?
4. **Regression**: Add test to prevent recurrence

## Phase 6: DOCUMENT

```
## Root Cause
[What actually caused the issue]

## Fix Applied
[What was changed]

## Prevention
[How to avoid this in the future]
```

---

**Quality Check**: After completing, rate your debugging process:
- Did you find the actual root cause, or just a workaround?
- Is the fix minimal and targeted?
- Is there a test to prevent regression?
