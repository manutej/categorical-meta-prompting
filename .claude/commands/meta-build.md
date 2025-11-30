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
    STAGE 0: CODEBASE EXPLORATION (REQUIRED FIRST)
    ═══════════════════════════════════════════════════════

    @run:now
    → Explore codebase to understand existing patterns
    → Identify where new feature fits
    → Find similar implementations to reference

    ◆ context:gathered

    ═══════════════════════════════════════════════════════
    STAGE 1: ANALYSIS & PLANNING
    ═══════════════════════════════════════════════════════

    @run:now
    → /route {feature}
    → /build-prompt "design ${feature}"

    ◆ routing:complete

    ═══════════════════════════════════════════════════════
    STAGE 2: DESIGN (with synthesis)
    ═══════════════════════════════════════════════════════

    @parallel[
      → Design architecture
      → Design data model
      → Design interface
    ]
    → Synthesize into cohesive design
    → Validate design against existing patterns

    ◆ design:validated

    ═══════════════════════════════════════════════════════
    STAGE 3: IMPLEMENTATION
    ═══════════════════════════════════════════════════════

    @run:now
    → /compose analyze plan implement
    → Write code following project conventions

    ⚡ Skill: "categorical-property-testing"

    ◆ implementation:complete

    ═══════════════════════════════════════════════════════
    STAGE 4: QUALITY ASSURANCE
    ═══════════════════════════════════════════════════════

    @parallel[
      → /review ${files_changed}
      → /meta-test ${component}
    ]

    ◆ quality >= 7 AND tests:pass

    ═══════════════════════════════════════════════════════
    STAGE 5: REFINEMENT (max 3 iterations)
    ═══════════════════════════════════════════════════════

    @loop:until:quality>=8:max:3[
      → /rmp "improve ${weakness}" 8
    ]

    ◆ quality >= 8

  ]
@end
```

---

## STAGE 0: Codebase Exploration

**ACTION: Search for related patterns**
```
Use Glob to find: **/*.{py,ts,js,go} matching feature keywords
Use Grep to search: existing implementations of similar features
Use Read to examine: 2-3 most relevant files
```

**Exploration Results:**
| What | Where | Relevance |
|------|-------|-----------|
| Similar feature | [file:line] | [how it helps] |
| Pattern to follow | [file:line] | [convention to use] |
| Code to extend | [file:line] | [extension point] |

**Project Conventions Detected:**
- File structure: [pattern]
- Naming: [pattern]
- Testing: [pattern]

---

## STAGE 1: Analysis & Planning

**ACTION: Analyze feature requirements**
```
1. Parse the feature request for:
   - Core functionality needed
   - Inputs and outputs
   - Error cases
   - Edge cases

2. Classify:
   - Domain: [ALGORITHM|API|DATABASE|SECURITY|...]
   - Complexity: [Low|Medium|High]
   - Estimated scope: [files to create/modify]
```

**Feature Analysis:**
| Aspect | Value | Notes |
|--------|-------|-------|
| Domain | | |
| Complexity | | |
| New files needed | | |
| Files to modify | | |
| Dependencies | | |

**ABORT CONDITIONS:**
- Feature conflicts with existing code → Ask for clarification
- Scope too large → Break into smaller tasks
- Missing dependencies → List what's needed first

---

## STAGE 2: Design

**ACTION: Create design artifacts**

**Architecture:**
```
[Draw component diagram or describe structure]

Component A
    ↓ uses
Component B
    ↓ calls
Component C
```

**Data Model:**
```
[Define data structures]

class/type Name:
    field1: type
    field2: type
```

**Interface Contract:**
```
[Define public API]

function_name(param1: type, param2: type) -> return_type
    """What it does, when to use it"""
```

**Design Validation Checklist:**
- [ ] Follows existing patterns from Stage 0
- [ ] No circular dependencies
- [ ] Clear separation of concerns
- [ ] Testable components

---

## STAGE 3: Implementation

**ACTION: Write code**

**Files to Create:**
| File | Purpose | Template |
|------|---------|----------|
| [path/file.py] | [purpose] | [similar to existing X] |

**Files to Modify:**
| File | Changes | Lines |
|------|---------|-------|
| [path/file.py] | [what changes] | [approx] |

**Implementation Order:**
1. [First file - foundation]
2. [Second file - core logic]
3. [Third file - integration]
4. [Tests - verify each step]

**Property Invariants (⚡ categorical-property-testing):**
- [ ] [Property 1]: [description]
- [ ] [Property 2]: [description]

---

## STAGE 4: Quality Assurance

**ACTION: Run review and tests in parallel**

**Review Focus:**
- [ ] Correctness: Does it do what's requested?
- [ ] Security: Any vulnerabilities introduced?
- [ ] Performance: Any obvious inefficiencies?
- [ ] Style: Follows project conventions?

**Test Checklist:**
- [ ] Unit tests for new functions
- [ ] Integration test for feature flow
- [ ] Edge case coverage
- [ ] Existing tests still pass

**Quality Scores:**
| Dimension | Score | Issue Count |
|-----------|-------|-------------|
| Correctness | /10 | |
| Completeness | /10 | |
| Code Quality | /10 | |
| Test Coverage | /10 | |
| **Weighted** | /10 | |

---

## STAGE 5: Refinement

**ACTION: Iterate if quality < 8**

**Iteration 1:**
- Weakness identified: [what needs improvement]
- Fix applied: [what was changed]
- New score: [X]/10

**Iteration 2 (if needed):**
- Weakness identified: [what needs improvement]
- Fix applied: [what was changed]
- New score: [X]/10

**MAX ITERATIONS: 3** - If still < 8, document remaining issues

---

## Final Summary

| Stage | Status | Key Outputs |
|-------|--------|-------------|
| 0. Exploration | | [patterns found] |
| 1. Analysis | | [complexity, scope] |
| 2. Design | | [architecture decision] |
| 3. Implementation | | [files created/modified] |
| 4. QA | | [score, issues fixed] |
| 5. Refinement | | [iterations, final score] |

**Deliverables:**
```
Files created:
- [list with paths]

Files modified:
- [list with paths]

Tests added:
- [list with paths]
```

**Final Quality Score:** [X]/10

**Ready for commit:** [YES/NO - if NO, what's blocking]
