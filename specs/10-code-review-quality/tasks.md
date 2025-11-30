# Task Breakdown: Code Review with Compositional Quality

## Phase 1: Core Types

| ID | Task | Story | Files |
|----|------|-------|-------|
| T001 | Define Check (name, run_fn, weight) | US1 | `types.py` |
| T002 | Define Score (value, details, check_name) | US1 | `types.py` |
| T003 | Define Profile (name, checks, threshold) | US2 | `types.py` |
| T004 | Define CodeChange (files, diff, metadata) | US1 | `types.py` |
| T005 | Write tests for types | US1 | `tests/test_types.py` |

**Checkpoint**: Core types defined.

---

## Phase 2: Built-in Checks

| ID | Task | Story | Files |
|----|------|-------|-------|
| T010 | Implement StyleCheck (pylint/flake8) | US1 | `checks/style.py` |
| T011 | Implement ComplexityCheck (cyclomatic) | US1 | `checks/complexity.py` |
| T012 | Implement CoverageCheck (coverage.py) | US1 | `checks/coverage.py` |
| T013 | Implement DocCheck (pydocstyle) | US1 | `checks/docs.py` |
| T014 | Implement SecurityCheck (bandit) | US1 | `checks/security.py` |
| T015 | Implement TypeCheck (mypy) | US1 | `checks/types.py` |
| T016 | Write tests for each check | US1 | `tests/test_checks.py` |

**Checkpoint**: All built-in checks working.

---

## Phase 3: Monoidal Composition

| ID | Task | Story | Files |
|----|------|-------|-------|
| T020 | Implement compose_checks(c1, c2) → ComposedCheck | US2 | `composition.py` |
| T021 | Implement score_compose(scores) → aggregate | US1 | `composition.py` |
| T022 | Verify associativity: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C) | US2 | `tests/test_composition.py` |
| T023 | Verify identity: id ⊗ C = C | US2 | `tests/test_composition.py` |
| T024 | Detect check conflicts | US2 | `composition.py` |

**Checkpoint**: Monoidal composition verified.

---

## Phase 4: Profile Management

| ID | Task | Story | Files |
|----|------|-------|-------|
| T030 | Implement create_profile(name, checks) | US2 | `profiles.py` |
| T031 | Implement save_profile(profile, path) | US2 | `profiles.py` |
| T032 | Implement load_profile(path) | US2 | `profiles.py` |
| T033 | Support YAML configuration | US2 | `config.py` |
| T034 | Write tests for profiles | US2 | `tests/test_profiles.py` |

---

## Phase 5: CI Integration

| ID | Task | Story | Files |
|----|------|-------|-------|
| T040 | Implement GitHub webhook handler | US3 | `integrations/github.py` |
| T041 | Post results as PR comment | US3 | `integrations/github.py` |
| T042 | Set PR status check | US3 | `integrations/github.py` |
| T043 | Implement GitLab integration | US3 | `integrations/gitlab.py` |
| T044 | GitHub Action YAML template | US3 | `action/` |
| T045 | Write tests for integration | US3 | `tests/test_integration.py` |

**Checkpoint**: CI integration working.

---

## Phase 6: Dashboard & Trends

| ID | Task | Story | Files |
|----|------|-------|-------|
| T050 | Store historical check results | US4 | `storage.py` |
| T051 | Implement quality_trend(repo, timeframe) | US4 | `trends.py` |
| T052 | Implement top_failing_checks(repo) | US4 | `trends.py` |
| T053 | Create dashboard API endpoints | US4 | `api.py` |
| T054 | Write tests for trends | US4 | `tests/test_trends.py` |

---

## Phase 7: Custom Checks

| ID | Task | Story | Files |
|----|------|-------|-------|
| T060 | Define check plugin interface | US5 | `plugins.py` |
| T061 | Implement load_custom_check(path) | US5 | `plugins.py` |
| T062 | Validate custom check conformance | US5 | `plugins.py` |
| T063 | Document custom check API | US5 | `docs/` |
| T064 | Write tests for plugins | US5 | `tests/test_plugins.py` |

---

## Phase 8: Integration

| ID | Task | Story | Files |
|----|------|-------|-------|
| T070 | Create CodeReviewEngine main class | All | `engine.py` |
| T071 | Add CLI interface | All | `cli.py` |
| T072 | Write integration tests | All | `tests/test_integration.py` |
| T073 | Create sample profiles | All | `examples/` |
| T074 | Write README and docs | All | `README.md` |

---

## Validation Checklist

- [ ] Monoidal laws verified
- [ ] All built-in checks pass on clean code
- [ ] CI integration posts comments
- [ ] Trends correctly computed
- [ ] Custom checks can be loaded
