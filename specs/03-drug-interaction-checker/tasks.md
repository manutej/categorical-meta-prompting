# Task Breakdown: Drug Interaction Compositional Checker

## Phase 1: Core Types & Data

| ID | Task | Story | Files |
|----|------|-------|-------|
| T001 | Define Drug dataclass (id, name, class, uses) | US1 | `types.py` |
| T002 | Define SafetyScore with [0,1] validation | US2 | `types.py` |
| T003 | Define Interaction (drug1, drug2, safety, mechanism) | US1 | `types.py` |
| T004 | Define DrugCombination (drugs, interactions, composite_safety) | US1 | `types.py` |
| T005 | Create curated interaction database (50+ pairs) | US1 | `data/interactions.json` |
| T006 | Implement Drug.from_id() lookup | US1 | `types.py` |
| T007 | Write tests for all types | US1 | `tests/test_types.py` |

**Checkpoint**: Core types working with test data.

---

## Phase 2: Monoidal Category Structure

| ID | Task | Story | Files |
|----|------|-------|-------|
| T010 | Implement DrugCategory.unit() → empty combination | US2 | `category.py` |
| T011 | Implement DrugCategory.tensor(combo, drug) | US2 | `category.py` |
| T012 | Write test: unit ⊗ drug = drug | US2 | `tests/test_category.py` |
| T013 | Write test: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C) associativity | US2 | `tests/test_category.py` |
| T014 | Write test: A ⊗ B = B ⊗ A symmetry | US2 | `tests/test_category.py` |
| T015 | Implement get_interaction(drug1, drug2) symmetric lookup | US1 | `category.py` |
| T016 | Write test: safety composition is multiplicative | US2 | `tests/test_category.py` |

**Checkpoint**: Monoidal laws verified.

---

## Phase 3: Safety Analysis

| ID | Task | Story | Files |
|----|------|-------|-------|
| T020 | Implement check_combination(drug_ids) → DrugCombination | US1 | `analyzer.py` |
| T021 | Implement classify_severity(safety) → Severity | US1 | `analyzer.py` |
| T022 | Display safety composition chain | US2 | `analyzer.py` |
| T023 | Identify "weakest link" interaction | US2 | `analyzer.py` |
| T024 | Generate recommendations based on severity | US1 | `analyzer.py` |
| T025 | Write test: known contraindicated pairs | US1 | `tests/test_analyzer.py` |
| T026 | Write test: safe combinations score > 0.9 | US1 | `tests/test_analyzer.py` |

**Checkpoint**: Can analyze drug combinations with recommendations.

---

## Phase 4: Alternatives & Comparison

| ID | Task | Story | Files |
|----|------|-------|-------|
| T030 | Define therapeutic class mappings | US3 | `alternatives.py` |
| T031 | Implement find_alternatives(drug, class) | US3 | `alternatives.py` |
| T032 | Implement find_safest_alternative(regimen, problem_drug) | US3 | `alternatives.py` |
| T033 | Implement compare_regimens(regimen1, regimen2) | US4 | `comparison.py` |
| T034 | Write test: alternatives improve safety | US3 | `tests/test_alternatives.py` |
| T035 | Write test: comparison correctly identifies safer | US4 | `tests/test_comparison.py` |

**Checkpoint**: Can suggest alternatives and compare regimens.

---

## Phase 5: Batch Processing

| ID | Task | Story | Files |
|----|------|-------|-------|
| T040 | Implement batch_analyze(patient_regimens) | US5 | `batch.py` |
| T041 | Rank patients by risk (ascending safety) | US5 | `batch.py` |
| T042 | Generate summary statistics | US5 | `batch.py` |
| T043 | Export results to CSV/JSON | US5 | `export.py` |
| T044 | Write tests for batch processing | US5 | `tests/test_batch.py` |

---

## Phase 6: Integration & Polish

| ID | Task | Story | Files |
|----|------|-------|-------|
| T050 | Create DrugInteractionEngine main class | All | `engine.py` |
| T051 | Add CLI with argparse | All | `cli.py` |
| T052 | Rich terminal output with severity symbols | All | `output.py` |
| T053 | Write integration tests with real scenarios | All | `tests/test_integration.py` |
| T054 | Add docstrings and type hints | All | All files |
| T055 | Create clinical scenario examples | All | `examples/` |

---

## Validation Checklist

- [ ] Monoidal laws (unit, associativity, symmetry) verified
- [ ] Safety composition is multiplicative
- [ ] All known contraindicated pairs detected
- [ ] Alternatives are therapeutically appropriate
- [ ] Batch processing handles 100+ patients
