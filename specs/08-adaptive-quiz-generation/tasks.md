# Task Breakdown: Adaptive Quiz Generation

## Phase 1: Core Types

| ID | Task | Story | Files |
|----|------|-------|-------|
| T001 | Define Question (id, text, difficulty, topic, answers) | US1 | `types.py` |
| T002 | Define QuizState (questions, answers, mastery, iteration) | US1 | `types.py` |
| T003 | Define LearningContext (history, knowledge_levels) | US3 | `types.py` |
| T004 | Implement compute_mastery(answers, difficulties) | US2 | `mastery.py` |
| T005 | Write tests for mastery computation | US2 | `tests/test_mastery.py` |

**Checkpoint**: Core types and mastery scoring working.

---

## Phase 2: RMP Quiz Loop

| ID | Task | Story | Files |
|----|------|-------|-------|
| T010 | Define QuizMonad with unit method | US1 | `rmp.py` |
| T011 | Implement QuizMonad.bind(answer_fn) | US1 | `rmp.py` |
| T012 | Implement rmp_quiz_loop with early stopping | US1 | `rmp.py` |
| T013 | Add mastery threshold check (0.85) | US1 | `rmp.py` |
| T014 | Add max questions limit (20) | US1 | `rmp.py` |
| T015 | Write tests for RMP loop | US1 | `tests/test_rmp.py` |

**Checkpoint**: RMP loop converges to mastery.

---

## Phase 3: Comonadic Context

| ID | Task | Story | Files |
|----|------|-------|-------|
| T020 | Implement LearningContext.extract() → KnowledgeState | US3 | `comonad.py` |
| T021 | Implement LearningContext.extend(f) | US3 | `comonad.py` |
| T022 | Track answer history in context | US3 | `comonad.py` |
| T023 | Compute learning velocity from history | US3 | `comonad.py` |
| T024 | Write tests for comonad laws | US3 | `tests/test_comonad.py` |

**Checkpoint**: Context extraction and update working.

---

## Phase 4: Question Selection

| ID | Task | Story | Files |
|----|------|-------|-------|
| T030 | Implement difficulty_selector(context, topic) | US1 | `selector.py` |
| T031 | Balance topic coverage in selection | US1 | `selector.py` |
| T032 | Enforce prerequisite mastery | US5 | `selector.py` |
| T033 | Implement question bank loader | US4 | `bank.py` |
| T034 | Write tests for selection | US1 | `tests/test_selector.py` |

**Checkpoint**: Adaptive question selection working.

---

## Phase 5: Prerequisite Graph

| ID | Task | Story | Files |
|----|------|-------|-------|
| T040 | Define Topic and PrerequisiteGraph | US5 | `prerequisites.py` |
| T041 | Implement cycle detection | US5 | `prerequisites.py` |
| T042 | Implement mastery unlock logic | US5 | `prerequisites.py` |
| T043 | Visualize prerequisite graph | US5 | `prerequisites.py` |
| T044 | Write tests for prerequisites | US5 | `tests/test_prereqs.py` |

---

## Phase 6: Integration

| ID | Task | Story | Files |
|----|------|-------|-------|
| T050 | Create AdaptiveQuizEngine main class | All | `engine.py` |
| T051 | Implement REST API with FastAPI | All | `api.py` |
| T052 | Add teacher dashboard endpoints | US2 | `api.py` |
| T053 | Write integration tests | All | `tests/test_integration.py` |
| T054 | Create sample quiz scenarios | All | `examples/` |

---

## Validation Checklist

- [ ] RMP loop converges to mastery
- [ ] Comonad laws verified
- [ ] Difficulty adapts correctly
- [ ] Prerequisites enforced
- [ ] Mastery correlates with assessment
