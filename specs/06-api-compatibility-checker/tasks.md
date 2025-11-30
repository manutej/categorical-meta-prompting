# Task Breakdown: API Compatibility Evolution Checker

## Phase 1: OpenAPI Parsing

| ID | Task | Story | Files |
|----|------|-------|-------|
| T001 | Define APIVersion dataclass (version, paths, schemas) | US1 | `types.py` |
| T002 | Implement parse_openapi(spec_path) | US1 | `parser.py` |
| T003 | Handle $ref resolution | US1 | `parser.py` |
| T004 | Support JSON and YAML formats | US1 | `parser.py` |
| T005 | Write tests for parsing | US1 | `tests/test_parser.py` |

**Checkpoint**: Can parse OpenAPI specs.

---

## Phase 2: Change Detection

| ID | Task | Story | Files |
|----|------|-------|-------|
| T010 | Define Change dataclass (type, path, severity, description) | US1 | `types.py` |
| T011 | Detect removed endpoints | US1 | `detector.py` |
| T012 | Detect added required parameters | US1 | `detector.py` |
| T013 | Detect response type changes | US1 | `detector.py` |
| T014 | Detect authentication changes | US1 | `detector.py` |
| T015 | Classify severity (breaking/deprecated/info) | US1 | `detector.py` |
| T016 | Write tests for change detection | US1 | `tests/test_detector.py` |

**Checkpoint**: Can detect all breaking changes.

---

## Phase 3: Migration Category

| ID | Task | Story | Files |
|----|------|-------|-------|
| T020 | Define Migration dataclass (source, target, changes) | US2 | `types.py` |
| T021 | Implement find_migration(v1, v2) | US1 | `category.py` |
| T022 | Implement compose(m1, m2) for multi-version | US2 | `category.py` |
| T023 | Track change provenance (which version) | US2 | `category.py` |
| T024 | Write test: composition is associative | US2 | `tests/test_category.py` |
| T025 | Write test: identity migration | US2 | `tests/test_category.py` |

**Checkpoint**: Can compose migration paths.

---

## Phase 4: Pre-Release Validation

| ID | Task | Story | Files |
|----|------|-------|-------|
| T030 | Implement check_proposed_change(current, proposed) | US3 | `validator.py` |
| T031 | Suggest non-breaking alternatives | US3 | `validator.py` |
| T032 | Support intentional break annotation | US3 | `validator.py` |
| T033 | Git pre-commit hook integration | US3 | `hooks/` |
| T034 | Write tests for validation | US3 | `tests/test_validator.py` |

---

## Phase 5: Reporting

| ID | Task | Story | Files |
|----|------|-------|-------|
| T040 | Generate compatibility report | US1 | `report.py` |
| T041 | Recommend semantic version bump | US1 | `report.py` |
| T042 | Generate migration guide | US2 | `report.py` |
| T043 | Output formats: JSON, Markdown, HTML | All | `report.py` |
| T044 | Write tests for reporting | All | `tests/test_report.py` |

---

## Phase 6: Integration

| ID | Task | Story | Files |
|----|------|-------|-------|
| T050 | Create APICompatibilityEngine main class | All | `engine.py` |
| T051 | Add CLI interface | All | `cli.py` |
| T052 | GitHub Action wrapper | All | `action/` |
| T053 | Write integration tests | All | `tests/test_integration.py` |
| T054 | Create sample API specs | All | `examples/` |

---

## Validation Checklist

- [ ] No false negatives for breaking changes
- [ ] Composition is associative
- [ ] Pre-commit hook works
- [ ] Reports are actionable
- [ ] Semver recommendations correct
