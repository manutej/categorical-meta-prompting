# Task Breakdown: Fraud Detection with Compositional Patterns

## Phase 1: Core Types

| ID | Task | Story | Files |
|----|------|-------|-------|
| T001 | Define Transaction (id, amount, entities, timestamp) | US1 | `types.py` |
| T002 | Define Entity (id, type, attributes) | US4 | `types.py` |
| T003 | Define Pattern (name, matcher, score_fn) | US2 | `types.py` |
| T004 | Define TransactionGraph using NetworkX | US4 | `graph.py` |
| T005 | Write tests for types | US1 | `tests/test_types.py` |

**Checkpoint**: Core types defined.

---

## Phase 2: Functor (Pattern Extraction)

| ID | Task | Story | Files |
|----|------|-------|-------|
| T010 | Implement build_graph(transactions) | US4 | `graph.py` |
| T011 | Implement extract_features(graph) | US1 | `functor.py` |
| T012 | Implement map_to_pattern_space(features) | US1 | `functor.py` |
| T013 | Write tests for functor | US1 | `tests/test_functor.py` |

**Checkpoint**: Can map transactions to pattern space.

---

## Phase 3: Pattern Matching & Composition

| ID | Task | Story | Files |
|----|------|-------|-------|
| T020 | Implement pattern_match(pattern, transaction) → score | US1 | `matcher.py` |
| T021 | Implement pattern_compose(p1, p2, op='and') | US2 | `composition.py` |
| T022 | Implement score_compose(scores) → aggregate | US1 | `composition.py` |
| T023 | Write tests for composition | US2 | `tests/test_composition.py` |

**Checkpoint**: Can compose and match patterns.

---

## Phase 4: Learning (Natural Transformation)

| ID | Task | Story | Files |
|----|------|-------|-------|
| T030 | Define PatternSet with version | US3 | `learning.py` |
| T031 | Implement update_patterns(old, new_data) | US3 | `learning.py` |
| T032 | Verify natural transformation preserves semantics | US3 | `learning.py` |
| T033 | Implement A/B test framework | US3 | `testing.py` |
| T034 | Write tests for learning | US3 | `tests/test_learning.py` |

**Checkpoint**: Can update patterns incrementally.

---

## Phase 5: Scoring & Real-Time

| ID | Task | Story | Files |
|----|------|-------|-------|
| T040 | Implement score_transaction(t) → FraudScore | US1 | `scorer.py` |
| T041 | Add pattern explanation to score | US1 | `scorer.py` |
| T042 | Implement alert_if_high_risk(score, threshold) | US1 | `alerts.py` |
| T043 | Write tests for scoring | US1 | `tests/test_scorer.py` |

---

## Phase 6: Graph Analysis

| ID | Task | Story | Files |
|----|------|-------|-------|
| T050 | Implement cluster_detection(graph) | US4 | `analysis.py` |
| T051 | Implement highlight_suspicious(clusters) | US4 | `analysis.py` |
| T052 | Create graph visualization | US4 | `viz.py` |
| T053 | Write tests for analysis | US4 | `tests/test_analysis.py` |

---

## Phase 7: Integration

| ID | Task | Story | Files |
|----|------|-------|-------|
| T060 | Create FraudDetectionEngine main class | All | `engine.py` |
| T061 | Add REST API for scoring | All | `api.py` |
| T062 | Create alert dashboard | US5 | `dashboard.py` |
| T063 | Write integration tests | All | `tests/test_integration.py` |
| T064 | Create sample fraud scenarios | All | `examples/` |

---

## Validation Checklist

- [ ] Functor preserves graph structure
- [ ] Pattern composition is associative
- [ ] Natural transformation preserves semantics
- [ ] Scoring latency < 100ms
- [ ] Precision > 90%
