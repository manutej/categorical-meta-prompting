# Task Breakdown: Threat Model Compositional Builder

## Phase 1: Core Types & ATT&CK Integration

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T001 | Define SystemState dataclass with id, name, description | US1 | Pending | `states.py` |
| T002 | Define Attack dataclass with source/target state, technique | US1 | Pending | `attacks.py` |
| T003 | Create ATT&CK technique loader from JSON | US3 | Pending | `attck_loader.py` |
| T004 | Map techniques to state transitions | US3 | Pending | `attck_loader.py` |
| T005 | Write tests for state/attack types | US1 | Pending | `tests/test_types.py` |
| T006 | Define standard state templates (Initial, User, Admin, etc.) | US1 | Pending | `states.py` |

**Checkpoint**: Can load ATT&CK and create attack morphisms.

---

## Phase 2: Composition Engine

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T010 | Implement compose_chain with state validation | US1 | Pending | `composition.py` |
| T011 | Write test: valid chain composition | US1 | Pending | `tests/test_composition.py` |
| T012 | Write test: invalid chain raises CompositionError | US1 | Pending | `tests/test_composition.py` |
| T013 | Build state graph from attacks using NetworkX | US4 | Pending | `composition.py` |
| T014 | Implement path enumeration with depth limit | US4 | Pending | `composition.py` |
| T015 | Score paths by difficulty and impact | US4 | Pending | `composition.py` |
| T016 | Write test: path enumeration finds all paths | US4 | Pending | `tests/test_composition.py` |

**Checkpoint**: Can compose chains and enumerate paths.

---

## Phase 3: Coverage Analysis

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T020 | Load ATT&CK mitigations | US2 | Pending | `coverage.py` |
| T021 | Map mitigations to techniques they block | US2 | Pending | `coverage.py` |
| T022 | Compute blocked paths given mitigation set | US2 | Pending | `coverage.py` |
| T023 | Identify unblocked (gap) paths | US2 | Pending | `coverage.py` |
| T024 | Rank gaps by impact | US2 | Pending | `coverage.py` |
| T025 | Suggest additional mitigations | US2 | Pending | `coverage.py` |
| T026 | Write tests for coverage analysis | US2 | Pending | `tests/test_coverage.py` |

**Checkpoint**: Can analyze defense coverage and gaps.

---

## Phase 4: Threat Actor Profiling

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T030 | Define ThreatActor dataclass with known TTPs | US5 | Pending | `actors.py` |
| T031 | Filter techniques by actor's toolkit | US5 | Pending | `actors.py` |
| T032 | Generate actor-specific attack trees | US5 | Pending | `actors.py` |
| T033 | Identify technique evolution opportunities | US5 | Pending | `actors.py` |
| T034 | Write tests for actor profiling | US5 | Pending | `tests/test_actors.py` |

**Checkpoint**: Can simulate threat actor behavior.

---

## Phase 5: Visualization & Export

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T040 | Generate Graphviz DOT from attack graph | US1 | Pending | `visualization.py` |
| T041 | Render to PNG/SVG | US1 | Pending | `visualization.py` |
| T042 | Generate Mermaid markdown | US1 | Pending | `visualization.py` |
| T043 | Export to STIX format | US1 | Pending | `export.py` |
| T044 | Export to JSON | US1 | Pending | `export.py` |
| T045 | Write tests for export formats | US1 | Pending | `tests/test_export.py` |

**Checkpoint**: Can visualize and export threat models.

---

## Phase 6: Integration

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T050 | Create ThreatModelEngine main class | All | Pending | `engine.py` |
| T051 | Implement full workflow: load → build → analyze → export | All | Pending | `engine.py` |
| T052 | Add CLI with argparse | All | Pending | `cli.py` |
| T053 | Write integration tests | All | Pending | `tests/test_integration.py` |
| T054 | Add comprehensive docstrings | All | Pending | All files |
| T055 | Create usage examples | All | Pending | `examples/` |

---

## Execution Strategy

### MVP Path
1. T001-T006 (Core types)
2. T010-T016 (Composition)
3. T040-T042 (Basic visualization)
4. T050-T051 (Engine)

### Parallel Opportunities
- T003-T004 (ATT&CK) || T001-T002 (Types)
- T020-T026 (Coverage) || T030-T034 (Actors)
- T040-T042 (Visual) || T043-T044 (Export)

---

## Validation Checklist

- [ ] All ATT&CK Enterprise techniques loadable
- [ ] Chain composition validates state compatibility
- [ ] Path enumeration completes in < 5 seconds (depth 5)
- [ ] Coverage analysis identifies real gaps
- [ ] Visualizations render correctly
