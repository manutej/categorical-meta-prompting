---
description: Full orchestrated build workflow - analyze, plan, implement, test, review in coordinated stages
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [feature-description]
---

# Meta-Build: Orchestrated Feature Construction

Build a feature with full prompt orchestration, coordinating multiple commands and skills.

## Feature Request
$ARGUMENTS

---

## Orchestration Plan

```
@orchestration
  @sequential[

    ═══════════════════════════════════════════════════════
    STAGE 1: ANALYSIS & PLANNING
    ═══════════════════════════════════════════════════════

    @run:now
    → /route {feature}
    # Analyze task type and complexity

    ◆ routing:complete

    @run:now
    → /build-prompt "design ${feature}"
    # Construct optimal prompt for design phase

    ═══════════════════════════════════════════════════════
    STAGE 2: PARALLEL DESIGN EXPLORATION
    ═══════════════════════════════════════════════════════

    @parallel[
      → /template "architecture for ${feature}"
      → /template "data model for ${feature}"
      → /template "interface contract for ${feature}"
    ]
    # Explore design dimensions concurrently

    ◆ all:templates:complete

    ═══════════════════════════════════════════════════════
    STAGE 3: IMPLEMENTATION
    ═══════════════════════════════════════════════════════

    @run:now
    → /compose analyze plan implement
    # Execute implementation pipeline

    ⚡ Skill: "categorical-property-testing"
    # Ensure type-safe properties during implementation

    ◆ implementation:complete

    ═══════════════════════════════════════════════════════
    STAGE 4: QUALITY ASSURANCE (PARALLEL)
    ═══════════════════════════════════════════════════════

    @parallel[
      → /review ${implementation}
      → /meta-test ${implementation}
    ]
    # Run review and testing concurrently

    ◆ quality >= 7 AND tests:pass

    ═══════════════════════════════════════════════════════
    STAGE 5: REFINEMENT LOOP
    ═══════════════════════════════════════════════════════

    @loop:until:quality>=8[
      @if:quality<7
        → /rmp ${implementation} 8
      @if:tests:failing
        → /debug ${test_failures}
    ]

    ◆ quality >= 8
    ◆ tests:pass
    ◆ review:approved

  ]
@end
```

---

## Execution Trace

### Stage 1: Analysis & Planning
```
┌─────────────────────────────────────────────┐
│ @run:now → /route                           │
│                                             │
│ Task Type: [detected]                       │
│ Complexity: [low/medium/high]               │
│ Domain: [detected domain]                   │
│ Routed Strategy: [selected approach]        │
└─────────────────────────────────────────────┘
```

[Execute /route analysis here]

```
┌─────────────────────────────────────────────┐
│ @run:now → /build-prompt                    │
│                                             │
│ Context: {context:expert}                   │
│ Mode: {mode:multi}                          │
│ Format: {format:structured}                 │
│ Quality: {quality:completeness}             │
└─────────────────────────────────────────────┘
```

[Execute /build-prompt here]

---

### Stage 2: Parallel Design Exploration

```
┌───────────────────┬───────────────────┬───────────────────┐
│ @parallel[1/3]    │ @parallel[2/3]    │ @parallel[3/3]    │
│                   │                   │                   │
│ Architecture      │ Data Model        │ Interface         │
│ Template          │ Template          │ Template          │
│                   │                   │                   │
│ [running...]      │ [running...]      │ [running...]      │
└───────────────────┴───────────────────┴───────────────────┘
```

[Execute three /template calls in parallel here]

**Synthesized Design:**
- Architecture: [result]
- Data Model: [result]
- Interface: [result]

---

### Stage 3: Implementation

```
┌─────────────────────────────────────────────┐
│ @run:now → /compose analyze plan implement  │
│                                             │
│ Pipeline: analyze → plan → implement        │
│                                             │
│ ⚡ Skill: "categorical-property-testing"    │
│    Ensuring type-safe construction          │
└─────────────────────────────────────────────┘
```

[Execute /compose pipeline here]

---

### Stage 4: Quality Assurance

```
┌─────────────────────────┬─────────────────────────┐
│ @parallel[1/2]          │ @parallel[2/2]          │
│                         │                         │
│ → /review               │ → /meta-test            │
│                         │                         │
│ Code quality check      │ Test coverage check     │
│ Security review         │ Property verification   │
│ Style conformance       │ Edge case handling      │
└─────────────────────────┴─────────────────────────┘
```

[Execute /review and /meta-test in parallel here]

**Quality Gate:**
| Check | Status | Score |
|-------|--------|-------|
| Review | | |
| Tests | | |
| Quality | | /10 |

---

### Stage 5: Refinement (if needed)

```
@loop:until:quality>=8
┌─────────────────────────────────────────────┐
│ Iteration ${loop.iteration}                 │
│                                             │
│ Current Quality: ${quality.score}           │
│ Target Quality: 8                           │
│                                             │
│ @if:quality<7 → /rmp refinement             │
│ @if:tests:failing → /debug failures         │
└─────────────────────────────────────────────┘
```

[Execute refinement loop if quality < 8]

---

## Final Summary

| Stage | Commands Used | Status | Time |
|-------|---------------|--------|------|
| Analysis | /route, /build-prompt | | |
| Design | /template ×3 (parallel) | | |
| Implementation | /compose | | |
| QA | /review, /meta-test (parallel) | | |
| Refinement | /rmp, /debug (as needed) | | |

**Skills Invoked:**
- ⚡ categorical-property-testing

**Final Quality Score:** [X]/10

**Deliverables:**
- [List of files created/modified]
- [Tests added]
- [Documentation updated]
