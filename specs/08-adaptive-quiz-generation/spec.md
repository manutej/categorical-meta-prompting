# Feature Specification: Adaptive Quiz Generation with Mastery Convergence

## Overview

**Product**: Categorical Adaptive Learning System
**Version**: 1.0
**Status**: Draft
**Last Updated**: 2024-11-29

### Summary

Build an adaptive quiz system using RMP (Recursive Meta-Prompting) to generate questions until student mastery is detected. Uses comonadic context extraction to track learning history and enriched quality for mastery scoring.

### Problem Statement

Fixed quizzes don't adapt to student ability, leading to over/under-testing. Educators need:
- Dynamically adaptive question difficulty
- Mastery detection for early stopping
- Learning context tracking for personalization
- Convergence guarantees via categorical structures

---

## User Scenarios

### US1: Adaptive Quiz Session [P1]

**As a** student
**I want to** take a quiz that adapts to my level
**So that** I'm challenged appropriately

**Given** a topic and my learning history
**When** I start a quiz
**Then** question difficulty adjusts based on my answers
**And** the quiz ends when mastery is detected
**And** I see my final mastery score

**Acceptance Criteria**:
- [ ] Initial difficulty based on history
- [ ] Difficulty adjusts after each answer
- [ ] Quiz stops at mastery threshold (0.85)
- [ ] Maximum 20 questions per session

### US2: Mastery Tracking [P1]

**As a** teacher
**I want to** see student mastery progression
**So that** I can identify struggling students

**Given** class quiz history
**When** I view the dashboard
**Then** I see mastery scores per student per topic
**And** struggling students are flagged
**And** mastery trends are visible

**Acceptance Criteria**:
- [ ] Mastery score in [0,1] per topic
- [ ] Flag students below 0.5 mastery
- [ ] Show mastery over time
- [ ] Export to gradebook

### US3: Learning Context Extraction [P2]

**As an** adaptive learning researcher
**I want to** extract learning context from history
**So that** I can personalize the experience

**Given** a student's answer history
**When** the comonad extracts context
**Then** I see estimated knowledge level
**And** I see learning velocity
**And** I see concept prerequisites mastered

**Acceptance Criteria**:
- [ ] Knowledge level per concept
- [ ] Learning velocity (improvement rate)
- [ ] Prerequisite graph traversal
- [ ] Context updates after each answer

### US4: Question Generation [P2]

**As a** content author
**I want to** generate question variants at different difficulties
**So that** I have a rich question bank

**Given** a topic and difficulty level
**When** I generate questions
**Then** I get structurally similar questions
**And** difficulty is calibrated correctly
**And** I can review and edit generated questions

**Acceptance Criteria**:
- [ ] Generate 5-10 variants per template
- [ ] Difficulty levels 1-5
- [ ] Maintain question structure
- [ ] Allow manual editing

### US5: Curriculum Prerequisite Graph [P3]

**As a** curriculum designer
**I want to** define topic prerequisites
**So that** quizzes respect learning order

**Given** a curriculum with topics
**When** I define prerequisites
**Then** the graph is validated (no cycles)
**And** quiz order respects prerequisites
**And** mastery unlocks subsequent topics

**Acceptance Criteria**:
- [ ] Define topic dependencies
- [ ] Detect and prevent cycles
- [ ] Unlock topics based on mastery
- [ ] Visualize prerequisite graph

---

## Functional Requirements

### FR-001: RMP Quiz Loop
The system SHALL implement adaptive quizzing as:
- Monad: Question generation with difficulty context
- Quality threshold: Mastery level (0.85)
- Convergence: Stop when mastery detected or max questions

### FR-002: Comonadic Context
The system SHALL track learning context via:
- Extract: Current knowledge state
- Extend: Update context with new answer
- History: Full learning trajectory

### FR-003: Mastery Computation
The system SHALL compute mastery using:
- Correct/incorrect answer weighting
- Difficulty adjustment factor
- Recency weighting

### FR-004: Question Bank
The system SHALL maintain questions with:
- Topic categorization
- Difficulty level (1-5)
- Prerequisite concepts
- Answer validation

### FR-005: Prerequisite Graph
The system SHALL enforce prerequisites:
- Directed acyclic graph of topics
- Mastery unlocking
- Learning path optimization

---

## Non-Functional Requirements

### NFR-001: Performance
- Question generation: < 500ms
- Mastery computation: < 100ms
- Context extraction: < 50ms

### NFR-002: Accuracy
- Mastery correlation with assessments: > 0.8
- Difficulty calibration: Validated by experts
- No premature mastery detection

### NFR-003: Engagement
- Session length: 5-15 minutes
- Appropriate challenge: Neither too easy nor hard
- Clear progress feedback

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Mastery Correlation | > 0.8 | vs. expert assessment |
| Engagement | > 80% | Session completion rate |
| Learning Gains | > 15% | Pre/post improvement |
| Efficiency | > 30% | Fewer questions to mastery |

---

## Categorical Structures

### RMP Monad for Quiz Loop

```
unit: Question → QuizState
bind: QuizState → (Answer → QuizState) → QuizState

Loop terminates when:
- quality >= mastery_threshold (0.85)
- OR iterations >= max_questions (20)
```

### Comonad for Context

```
extract: LearningContext → KnowledgeState
extend: (LearningContext → A) → LearningContext → LearningContext[A]

Used for:
- Extracting current mastery estimate
- Updating context with new information
```

### Enriched Category for Mastery

```
Objects: Knowledge states
Hom(K₁, K₂) ∈ [0,1]: Mastery transition probability
Composition: Learning path quality
```

### Mastery Diagram

```
Question₁ ──answer──▶ Context₁ ──extract──▶ Mastery: 0.4
     │                    │
     │                    │ extend
     │                    ▼
Question₂ ──answer──▶ Context₂ ──extract──▶ Mastery: 0.6
     │                    │
     │                    │ extend
     │                    ▼
Question₃ ──answer──▶ Context₃ ──extract──▶ Mastery: 0.87 ✓ STOP
```

---

## Data Sources

- **EdNet**: 100M+ student interactions
- **ASSISTments**: Math tutoring data
- **Junyi Academy**: Video + quiz data
- **Custom**: Institution question banks

---

## Open Questions

1. **NEEDS CLARIFICATION**: Support for open-ended questions?
2. **NEEDS CLARIFICATION**: How to handle guessing?
3. **NEEDS CLARIFICATION**: Multi-concept questions?
