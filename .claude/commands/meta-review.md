---
description: Multi-pass parallel code review with specialized reviewers for different concerns
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [file-or-changeset]
---

# Meta-Review: Orchestrated Multi-Dimensional Review

Conduct a comprehensive code review with parallel specialized passes.

## Review Target
$ARGUMENTS

---

## Orchestration Plan

```
@orchestration
  @sequential[

    ═══════════════════════════════════════════════════════
    STAGE 1: READ & UNDERSTAND
    ═══════════════════════════════════════════════════════

    @run:now
    → Read all files/changes to review
    → Identify domain and complexity
    → Note key areas of concern

    ◆ context:understood

    ═══════════════════════════════════════════════════════
    STAGE 2: PARALLEL SPECIALIZED REVIEWS
    ═══════════════════════════════════════════════════════

    @parallel[
      → Correctness pass
      → Security pass
      → Performance pass
      → Maintainability pass
    ]

    ⚡ Skill: "categorical-property-testing" (if applicable)

    ◆ all:reviews:complete

    ═══════════════════════════════════════════════════════
    STAGE 3: SYNTHESIZE & PRIORITIZE
    ═══════════════════════════════════════════════════════

    @run:now
    → Merge findings, remove duplicates
    → Rank by severity
    → Resolve conflicts between reviewers

    ◆ findings:synthesized

    ═══════════════════════════════════════════════════════
    STAGE 4: DEEP DIVE (if critical issues)
    ═══════════════════════════════════════════════════════

    @if:critical_issues>0
      → /debug ${critical_issues}

    @if:security_issues>0
      ⚡ Skill: "security-analysis"

    ═══════════════════════════════════════════════════════
    STAGE 5: VERDICT
    ═══════════════════════════════════════════════════════

    @run:now
    → Decide: APPROVE / REQUEST CHANGES / REJECT
    → List required vs optional changes

    ◆ decision:made

  ]
@end
```

---

## STAGE 1: Read & Understand

**ACTION: Read all code under review**

```
1. Identify files to review:
   Use Glob/Read to examine: [file patterns or specific files]

2. For each file, note:
   - Purpose and responsibility
   - Key functions/classes
   - Dependencies and imports
   - Recent changes (if reviewing a diff)
```

**Files Under Review:**
| File | Lines | Purpose | Concern Level |
|------|-------|---------|---------------|
| [path] | [N] | [what it does] | [Low/Med/High] |

**Domain Classification:**
- Primary domain: [ALGORITHM|API|DATABASE|SECURITY|...]
- Language/Framework: [Python|TypeScript|Go|...]
- Test coverage: [exists|partial|missing]

**Initial Impressions:**
- [First observation about the code]
- [Second observation]
- [Areas that need closer examination]

---

## STAGE 2: Parallel Specialized Reviews

**ACTION: Run four review passes simultaneously**

### 2A. Correctness Review

**Question: Does the code work correctly?**

| Check | Status | Finding |
|-------|--------|---------|
| Logic errors | ✓/✗ | [specific issue or "None"] |
| Edge cases handled | ✓/✗ | [missing cases] |
| Error handling | ✓/✗ | [issues] |
| Null/undefined safety | ✓/✗ | [issues] |
| Type correctness | ✓/✗ | [issues] |
| Contract violations | ✓/✗ | [issues] |

**Correctness Findings:**
```
[file:line] - [severity] - [description]
[file:line] - [severity] - [description]
```

**Score:** [X]/10

---

### 2B. Security Review

**Question: Is the code secure?**

| OWASP Check | Status | Finding |
|-------------|--------|---------|
| Injection (SQL, Command, etc.) | ✓/✗ | |
| Broken Authentication | ✓/✗ | |
| Sensitive Data Exposure | ✓/✗ | |
| XXE | ✓/✗ | |
| Broken Access Control | ✓/✗ | |
| Security Misconfiguration | ✓/✗ | |
| XSS | ✓/✗ | |
| Insecure Deserialization | ✓/✗ | |
| Known Vulnerable Components | ✓/✗ | |
| Insufficient Logging | ✓/✗ | |

**Security Findings:**
```
[file:line] - [severity] - [vulnerability type] - [description]
```

**Score:** [X]/10

---

### 2C. Performance Review

**Question: Is the code efficient?**

| Check | Status | Finding |
|-------|--------|---------|
| Time complexity | O(?) | [assessment] |
| Space complexity | O(?) | [assessment] |
| N+1 queries | ✓/✗ | |
| Unnecessary computation | ✓/✗ | |
| Resource leaks | ✓/✗ | |
| Blocking operations | ✓/✗ | |
| Caching opportunities | ✓/✗ | |

**Performance Findings:**
```
[file:line] - [impact] - [description] - [suggested fix]
```

**Score:** [X]/10

---

### 2D. Maintainability Review

**Question: Is the code maintainable?**

| Check | Status | Finding |
|-------|--------|---------|
| Readability | ✓/✗ | |
| Naming clarity | ✓/✗ | |
| Function length (<30 lines) | ✓/✗ | |
| Single responsibility | ✓/✗ | |
| DRY violations | ✓/✗ | |
| Documentation | ✓/✗ | |
| Test coverage | ✓/✗ | |
| Modularity | ✓/✗ | |

**Maintainability Findings:**
```
[file:line] - [severity] - [issue] - [suggestion]
```

**Score:** [X]/10

---

### Property Testing (if applicable)

```
⚡ Skill: "categorical-property-testing"

Properties to verify:
- [ ] [Property 1]: [invariant that should hold]
- [ ] [Property 2]: [invariant that should hold]

Property test results:
- [Property 1]: [HOLDS / VIOLATED at file:line]
```

---

## STAGE 3: Synthesize & Prioritize

**ACTION: Merge all findings and prioritize**

**All Findings by Severity:**

🔴 **CRITICAL** (blocks approval):
| # | Category | File:Line | Issue | Required Fix |
|---|----------|-----------|-------|--------------|
| 1 | | | | |

🟠 **HIGH** (should fix before merge):
| # | Category | File:Line | Issue | Suggested Fix |
|---|----------|-----------|-------|---------------|
| 1 | | | | |

🟡 **MEDIUM** (nice to fix):
| # | Category | File:Line | Issue | Suggestion |
|---|----------|-----------|-------|------------|
| 1 | | | | |

🟢 **LOW** (optional improvements):
| # | Category | File:Line | Issue | Suggestion |
|---|----------|-----------|-------|------------|
| 1 | | | | |

**Conflicts Between Reviewers:**
```
If any: [e.g., "Performance suggests inlining but Maintainability prefers extraction"]
Resolution: [which to prefer and why]
```

---

## STAGE 4: Deep Dive (if needed)

**Triggered if critical or security issues found**

```
@if:critical_issues>0

Critical Issue Analysis:
Issue: [description]
Location: [file:line]
Impact: [what could go wrong]
Root cause: [why this happened]
Fix: [specific code change needed]
```

```
@if:security_issues>0
⚡ Skill: "security-analysis"

Security Deep Dive:
Vulnerability: [type]
Attack vector: [how it could be exploited]
Impact: [damage potential]
Remediation: [specific fix]
Additional hardening: [defense in depth recommendations]
```

---

## STAGE 5: Final Verdict

**Overall Scores:**
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Correctness | /10 | 40% | |
| Security | /10 | 30% | |
| Performance | /10 | 15% | |
| Maintainability | /10 | 15% | |
| **TOTAL** | | 100% | **/10** |

**Decision:**
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│   [ ] ✅ APPROVE - Ready to merge                               │
│                                                                  │
│   [ ] 🔄 REQUEST CHANGES - Fix issues below first               │
│                                                                  │
│   [ ] ❌ REJECT - Fundamental issues, needs redesign            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Required Changes (must fix):**
1. [Critical/High issue 1 with location and fix]
2. [Critical/High issue 2 with location and fix]

**Suggested Improvements (optional):**
1. [Medium/Low improvement 1]
2. [Medium/Low improvement 2]

---

## Review Summary

**Target:** $ARGUMENTS
**Decision:** [APPROVE / REQUEST CHANGES / REJECT]
**Composite Score:** [X]/10

**Key Issues:**
- [Most important finding 1]
- [Most important finding 2]

**Strengths:**
- [What the code does well]

**Skills Used:**
- ⚡ categorical-property-testing [if used]
- ⚡ security-analysis [if used]
