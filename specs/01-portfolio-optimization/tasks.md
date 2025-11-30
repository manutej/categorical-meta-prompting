# Task Breakdown: Recursive Portfolio Optimization

## Overview

This document breaks down the implementation into actionable tasks organized by user story and phase. Each task is designed to be independently completable and testable.

---

## Phase 0: Setup

| ID | Task | Story | Status |
|----|------|-------|--------|
| T001 | Create portfolio module directory structure | Setup | Done |
| T002 | Add dependencies to requirements.txt | Setup | Done |
| T003 | Create __init__.py with exports | Setup | Pending |

---

## Phase 1: Foundational

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T010 | [P] Define Portfolio dataclass with weights, metrics | US1 | Pending | `portfolio/types.py` |
| T011 | [P] Define QualityScore dataclass with components | US2 | Pending | `portfolio/types.py` |
| T012 | [P] Define MarketContext dataclass for comonad | US3 | Pending | `portfolio/types.py` |
| T013 | Implement data fetching with yfinance | US1 | Pending | `portfolio/data.py` |
| T014 | Add mock data fallback for offline use | US1 | Pending | `portfolio/data.py` |
| T015 | Implement 15-minute caching for API responses | US1 | Pending | `portfolio/data.py` |

**Checkpoint**: After Phase 1, we can fetch data and have core types defined.

---

## Phase 2: User Story 1 - Basic Portfolio Optimization

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T020 | Write test: equal weight portfolio creation | US1 | Pending | `tests/test_portfolio.py` |
| T021 | Implement Portfolio.from_tickers(tickers) | US1 | Pending | `portfolio/types.py` |
| T022 | Write test: weight normalization sums to 1.0 | US1 | Pending | `tests/test_portfolio.py` |
| T023 | Write test: Sharpe ratio calculation | US1 | Pending | `tests/test_quality.py` |
| T024 | Implement Sharpe ratio normalized to [0,1] | US1 | Pending | `portfolio/quality.py` |
| T025 | Write test: diversification entropy calculation | US1 | Pending | `tests/test_quality.py` |
| T026 | Implement diversification score | US1 | Pending | `portfolio/quality.py` |
| T027 | Write test: volatility alignment score | US1 | Pending | `tests/test_quality.py` |
| T028 | Implement volatility alignment to target | US1 | Pending | `portfolio/quality.py` |
| T029 | Write test: aggregate quality score | US1 | Pending | `tests/test_quality.py` |
| T030 | Implement QualityScore.aggregate() method | US1 | Pending | `portfolio/quality.py` |

**Checkpoint**: Run `pytest tests/test_portfolio.py tests/test_quality.py` - all tests should pass.

---

## Phase 3: User Story 2 - RMP Convergence Tracking

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T040 | Write test: MonadPortfolio.unit creates wrapper | US2 | Pending | `tests/test_rmp.py` |
| T041 | Implement MonadPortfolio with unit method | US2 | Pending | `portfolio/monad.py` |
| T042 | Write test: MonadPortfolio.bind applies function | US2 | Pending | `tests/test_rmp.py` |
| T043 | Implement MonadPortfolio.bind with history | US2 | Pending | `portfolio/monad.py` |
| T044 | Write property test: left identity law | US2 | Pending | `tests/test_rmp.py` |
| T045 | Write property test: right identity law | US2 | Pending | `tests/test_rmp.py` |
| T046 | Write property test: associativity law | US2 | Pending | `tests/test_rmp.py` |
| T047 | Write test: RMP loop terminates at threshold | US2 | Pending | `tests/test_rmp.py` |
| T048 | Implement RMP loop with early stopping | US2 | Pending | `portfolio/engine.py` |
| T049 | Write test: RMP loop respects max iterations | US2 | Pending | `tests/test_rmp.py` |
| T050 | Implement max iteration safety limit | US2 | Pending | `portfolio/engine.py` |
| T051 | Write test: iteration history is tracked | US2 | Pending | `tests/test_rmp.py` |
| T052 | Implement history tracking in MonadPortfolio | US2 | Pending | `portfolio/monad.py` |

**Checkpoint**: Run `pytest tests/test_rmp.py` - all tests including property tests should pass.

---

## Phase 4: User Story 3 - Market Context Extraction

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T060 | Write test: market regime detection | US3 | Pending | `tests/test_context.py` |
| T061 | Implement regime detection (bull/bear/neutral) | US3 | Pending | `portfolio/context.py` |
| T062 | Write test: volatility extraction | US3 | Pending | `tests/test_context.py` |
| T063 | Implement per-asset volatility calculation | US3 | Pending | `portfolio/context.py` |
| T064 | Write test: correlation matrix computation | US3 | Pending | `tests/test_context.py` |
| T065 | Implement correlation matrix from returns | US3 | Pending | `portfolio/context.py` |
| T066 | Write test: comonad extract method | US3 | Pending | `tests/test_context.py` |
| T067 | Implement MarketContext.extract() | US3 | Pending | `portfolio/context.py` |
| T068 | Write test: comonad extend method | US3 | Pending | `tests/test_context.py` |
| T069 | Implement MarketContext.extend(f) | US3 | Pending | `portfolio/context.py` |

**Checkpoint**: Run `pytest tests/test_context.py` - comonad operations verified.

---

## Phase 5: Improvement Functions (Kleisli Arrows)

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T070 | Write test: Sharpe improvement shifts weights | US1 | Pending | `tests/test_improve.py` |
| T071 | Implement improve_for_sharpe Kleisli arrow | US1 | Pending | `portfolio/improvement.py` |
| T072 | Write test: diversification moves toward equal | US1 | Pending | `tests/test_improve.py` |
| T073 | Implement improve_for_diversification | US1 | Pending | `portfolio/improvement.py` |
| T074 | Write test: volatility targeting scales weights | US1 | Pending | `tests/test_improve.py` |
| T075 | Implement improve_for_volatility_target | US1 | Pending | `portfolio/improvement.py` |
| T076 | Write test: combined improvement composition | US1 | Pending | `tests/test_improve.py` |
| T077 | Implement combined_improve via Kleisli compose | US1 | Pending | `portfolio/improvement.py` |

**Checkpoint**: Individual improvement functions verified independently.

---

## Phase 6: Integration

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T080 | Write integration test: full optimization flow | All | Pending | `tests/test_integration.py` |
| T081 | Implement PortfolioRMPEngine.optimize() | All | Pending | `portfolio/engine.py` |
| T082 | Write test: optimization with real data | All | Pending | `tests/test_integration.py` |
| T083 | Verify quality improvement > 0.3 on test data | All | Pending | `tests/test_integration.py` |
| T084 | Write test: graceful handling of bad tickers | US1 | Pending | `tests/test_integration.py` |
| T085 | Implement ticker validation with skip | US1 | Pending | `portfolio/data.py` |

**Checkpoint**: Full system works end-to-end with real Yahoo Finance data.

---

## Phase 7: Polish

| ID | Task | Story | Status | Files |
|----|------|-------|--------|-------|
| T090 | Add CLI argument parsing with argparse | All | Pending | `portfolio/cli.py` |
| T091 | Implement ASCII progress bar visualization | US2 | Pending | `portfolio/output.py` |
| T092 | Add rich terminal formatting for results | All | Pending | `portfolio/output.py` |
| T093 | Implement structured JSON output option | All | Pending | `portfolio/output.py` |
| T094 | Add comprehensive error messages | All | Pending | `portfolio/errors.py` |
| T095 | Write README with usage examples | All | Pending | `portfolio/README.md` |
| T096 | Add docstrings to all public functions | All | Pending | All files |

---

## Execution Strategy

### Recommended: MVP-First

1. Complete Phase 0-2 first (Setup + Foundational + US1)
2. Verify basic optimization works with mock data
3. Add RMP tracking (Phase 3)
4. Add context extraction (Phase 4)
5. Polish and document (Phase 7)

### Parallel Work Opportunities

Tasks marked `[P]` can be done in parallel:
- T010, T011, T012 (type definitions)
- T024, T026, T028 (quality components)
- T071, T073, T075 (improvement functions)

### Dependencies

```
T013 (data fetch) → T021 (portfolio creation)
T024-T028 (quality) → T030 (aggregate)
T041-T043 (monad) → T048-T052 (RMP loop)
T061-T065 (context) → T067-T069 (comonad)
T071-T077 (improve) → T081 (engine)
```

---

## Validation Checklist

After each phase:
- [ ] All tests pass
- [ ] Type checking passes (mypy)
- [ ] Code formatted (black)
- [ ] No linting errors (ruff)
- [ ] Documentation updated
