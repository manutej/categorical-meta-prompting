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
    STAGE 1: CONTEXT GATHERING
    ═══════════════════════════════════════════════════════

    @run:now
    → /route {target}
    # Determine domain and appropriate review focus

    ◆ domain:identified

    ═══════════════════════════════════════════════════════
    STAGE 2: PARALLEL SPECIALIZED REVIEWS
    ═══════════════════════════════════════════════════════

    @parallel[
      → /review:correctness ${target}
      → /review:security ${target}
      → /review:performance ${target}
      → /review:maintainability ${target}
    ]
    # Four specialized reviewers working simultaneously

    ⚡ Skill: "categorical-property-testing"
    # Verify type-level properties

    ◆ all:reviews:complete

    ═══════════════════════════════════════════════════════
    STAGE 3: SYNTHESIS & PRIORITIZATION
    ═══════════════════════════════════════════════════════

    @run:now
    → Synthesize findings from all reviewers
    → Prioritize by severity: Critical > High > Medium > Low
    → Identify conflicts between reviewer recommendations

    ◆ findings:synthesized

    ═══════════════════════════════════════════════════════
    STAGE 4: CONDITIONAL DEEP DIVES
    ═══════════════════════════════════════════════════════

    @if:critical_issues>0
      @run:now
      → /debug ${critical_issues}
      # Deep dive into critical issues

    @if:security_issues>0
      ⚡ Skill: "security-analysis"
      # Security-focused deep analysis

    ═══════════════════════════════════════════════════════
    STAGE 5: FINAL VERDICT
    ═══════════════════════════════════════════════════════

    @run:now
    → Compile final review decision

    ◆ decision:approve OR decision:request_changes OR decision:reject

  ]
@end
```

---

## Execution Trace

### Stage 1: Context Gathering

```
┌─────────────────────────────────────────────┐
│ @run:now → /route                           │
│                                             │
│ Target: ${target}                           │
│ Detected Domain: [domain]                   │
│ Review Focus: [based on domain]             │
│                                             │
│ File Type: [language/framework]             │
│ Change Size: [lines/files affected]         │
└─────────────────────────────────────────────┘
```

[Analyze target and determine review focus]

---

### Stage 2: Parallel Specialized Reviews

```
@parallel[
┌────────────────────┬────────────────────┬────────────────────┬────────────────────┐
│ CORRECTNESS        │ SECURITY           │ PERFORMANCE        │ MAINTAINABILITY    │
│ REVIEWER           │ REVIEWER           │ REVIEWER           │ REVIEWER           │
├────────────────────┼────────────────────┼────────────────────┼────────────────────┤
│                    │                    │                    │                    │
│ □ Logic errors     │ □ Injection        │ □ Time complexity  │ □ Readability      │
│ □ Edge cases       │ □ Auth bypass      │ □ Space complexity │ □ DRY violations   │
│ □ Type safety      │ □ Data exposure    │ □ Resource leaks   │ □ Naming           │
│ □ Error handling   │ □ Input validation │ □ N+1 queries      │ □ Documentation    │
│ □ Contract         │ □ Crypto issues    │ □ Caching          │ □ Test coverage    │
│   violations       │ □ OWASP Top 10     │ □ Async issues     │ □ Modularity       │
│                    │                    │                    │                    │
│ Score: /10         │ Score: /10         │ Score: /10         │ Score: /10         │
└────────────────────┴────────────────────┴────────────────────┴────────────────────┘
]

⚡ Skill: "categorical-property-testing"
   - Functor laws preserved?
   - Monad laws preserved?
   - Type invariants maintained?
```

#### Correctness Review
```
┌─────────────────────────────────────────────┐
│ {context:reviewer}                          │
│ Focus: Does the code do what it should?     │
│                                             │
│ Checking:                                   │
│ - [ ] Logic correctness                     │
│ - [ ] Edge case handling                    │
│ - [ ] Error scenarios                       │
│ - [ ] Contract adherence                    │
│                                             │
│ Findings:                                   │
│ - [finding 1]                               │
│ - [finding 2]                               │
│                                             │
│ Score: [X]/10                               │
└─────────────────────────────────────────────┘
```

#### Security Review
```
┌─────────────────────────────────────────────┐
│ {context:security-expert}                   │
│ Focus: Is the code secure?                  │
│                                             │
│ Checking:                                   │
│ - [ ] Injection vulnerabilities             │
│ - [ ] Authentication/Authorization          │
│ - [ ] Data validation                       │
│ - [ ] Sensitive data handling               │
│ - [ ] OWASP Top 10                          │
│                                             │
│ Findings:                                   │
│ - [finding 1]                               │
│ - [finding 2]                               │
│                                             │
│ Score: [X]/10                               │
└─────────────────────────────────────────────┘
```

#### Performance Review
```
┌─────────────────────────────────────────────┐
│ {context:performance-expert}                │
│ Focus: Is the code efficient?               │
│                                             │
│ Checking:                                   │
│ - [ ] Time complexity                       │
│ - [ ] Space complexity                      │
│ - [ ] Resource management                   │
│ - [ ] Async/concurrent correctness          │
│ - [ ] Database query efficiency             │
│                                             │
│ Findings:                                   │
│ - [finding 1]                               │
│ - [finding 2]                               │
│                                             │
│ Score: [X]/10                               │
└─────────────────────────────────────────────┘
```

#### Maintainability Review
```
┌─────────────────────────────────────────────┐
│ {context:maintainability-expert}            │
│ Focus: Is the code maintainable?            │
│                                             │
│ Checking:                                   │
│ - [ ] Readability                           │
│ - [ ] DRY principle                         │
│ - [ ] Naming conventions                    │
│ - [ ] Documentation                         │
│ - [ ] Test coverage                         │
│ - [ ] Modularity                            │
│                                             │
│ Findings:                                   │
│ - [finding 1]                               │
│ - [finding 2]                               │
│                                             │
│ Score: [X]/10                               │
└─────────────────────────────────────────────┘
```

---

### Stage 3: Synthesis & Prioritization

```
┌─────────────────────────────────────────────┐
│ SYNTHESIZING REVIEW FINDINGS                │
│                                             │
│ Total Findings: [N]                         │
│                                             │
│ By Severity:                                │
│ 🔴 Critical: [count]                        │
│ 🟠 High:     [count]                        │
│ 🟡 Medium:   [count]                        │
│ 🟢 Low:      [count]                        │
│                                             │
│ By Category:                                │
│ - Correctness: [count]                      │
│ - Security:    [count]                      │
│ - Performance: [count]                      │
│ - Maintainability: [count]                  │
└─────────────────────────────────────────────┘
```

**Prioritized Findings:**

| # | Severity | Category | Finding | Recommendation |
|---|----------|----------|---------|----------------|
| 1 | 🔴 Critical | | | |
| 2 | 🟠 High | | | |
| 3 | 🟡 Medium | | | |

**Conflicts Between Reviewers:**
- [If performance says X but maintainability says Y]

---

### Stage 4: Conditional Deep Dives

```
@if:critical_issues>0
┌─────────────────────────────────────────────┐
│ Critical issues found - deep dive required  │
│                                             │
│ → /debug ${critical_issues}                 │
│                                             │
│ Deep analysis of:                           │
│ - [critical issue 1]                        │
│ - [critical issue 2]                        │
└─────────────────────────────────────────────┘

@if:security_issues>0
┌─────────────────────────────────────────────┐
│ Security issues found - specialist required │
│                                             │
│ ⚡ Skill: "security-analysis"               │
│                                             │
│ Security deep dive:                         │
│ - Exploitation analysis                     │
│ - Remediation recommendations               │
│ - Defense in depth suggestions              │
└─────────────────────────────────────────────┘
```

[Execute conditional deep dives if triggered]

---

### Stage 5: Final Verdict

```
┌─────────────────────────────────────────────────────────────────┐
│                       REVIEW DECISION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  □ APPROVE         □ REQUEST CHANGES        □ REJECT            │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Overall Scores:                                                  │
│                                                                  │
│ Correctness:      [██████████] X/10                             │
│ Security:         [██████████] X/10                             │
│ Performance:      [██████████] X/10                             │
│ Maintainability:  [██████████] X/10                             │
│ ─────────────────────────────────                               │
│ COMPOSITE:        [██████████] X/10                             │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│ Required Changes Before Approval:                                │
│ - [change 1]                                                     │
│ - [change 2]                                                     │
│                                                                  │
│ Suggested Improvements (Optional):                               │
│ - [improvement 1]                                                │
│ - [improvement 2]                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Review Summary

| Dimension | Score | Critical Issues | Action Items |
|-----------|-------|-----------------|--------------|
| Correctness | /10 | | |
| Security | /10 | | |
| Performance | /10 | | |
| Maintainability | /10 | | |
| **Overall** | /10 | | |

**Decision:** [APPROVE / REQUEST CHANGES / REJECT]

**Skills Used:**
- ⚡ categorical-property-testing
- ⚡ security-analysis (if triggered)
