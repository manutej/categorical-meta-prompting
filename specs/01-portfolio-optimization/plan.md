# Implementation Plan: Recursive Portfolio Optimization

## Summary

Implement an RMP-based portfolio optimizer using Python, leveraging categorical structures for quality tracking and iterative refinement. The system fetches real market data and applies monadic composition to improve portfolio allocations until quality thresholds are met.

---

## Technical Context

| Aspect | Decision |
|--------|----------|
| **Language** | Python 3.11+ |
| **Data Source** | yfinance (Yahoo Finance API) |
| **Numerical Computing** | NumPy, Pandas |
| **Framework** | Standalone (integrates with meta_prompting_engine) |
| **Testing** | pytest with property-based testing (hypothesis) |
| **Type Checking** | mypy with strict mode |

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Spec completeness | PASS | All user stories have acceptance criteria |
| Testability | PASS | Each story is independently testable |
| Categorical rigor | PASS | Monad laws verified in tests |
| Data availability | PASS | Yahoo Finance API is free and reliable |

---

## Project Structure

### Documentation

```
specs/01-portfolio-optimization/
├── spec.md           # This specification
├── plan.md           # This implementation plan
├── tasks.md          # Task breakdown
└── CHANGELOG.md      # Version history
```

### Source Code

```
examples/real_data_applications/
└── 01_portfolio_optimization.py   # Main implementation (exists)

meta_prompting_engine/
├── categorical/
│   ├── monad.py                   # RMP monad (exists)
│   ├── comonad.py                 # Context extraction (exists)
│   └── types.py                   # Core types (exists)
└── applications/
    └── portfolio/                 # NEW: Portfolio-specific module
        ├── __init__.py
        ├── data.py                # Data fetching and caching
        ├── quality.py             # Quality scoring functions
        ├── improvement.py         # Kleisli arrows for optimization
        ├── context.py             # Comonadic context extraction
        └── engine.py              # Main RMP engine
```

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Portfolio RMP Engine                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Data Layer  │───▶│ Quality Eval │───▶│  Improvers   │  │
│  │  (yfinance)  │    │  (Enriched)  │    │  (Kleisli)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Context    │    │    Monad     │    │    Output    │  │
│  │  (Comonad)   │───▶│  (RMP Loop)  │───▶│  (Results)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input**: List of ticker symbols
2. **Fetch**: Historical prices from Yahoo Finance
3. **Context**: Comonad extracts market state
4. **Initialize**: Create equal-weight portfolio
5. **Loop**: RMP monad iterates until quality threshold
6. **Output**: Final portfolio with metrics and history

---

## Key Algorithms

### Quality Score Computation

```python
def compute_quality(portfolio, context) -> QualityScore:
    # 1. Sharpe ratio (normalized to [0,1])
    sharpe = (expected_return - risk_free) / volatility
    sharpe_normalized = clip((sharpe + 1) / 4, 0, 1)

    # 2. Diversification (entropy of weights)
    entropy = -sum(w * log(w) for w in weights if w > 0)
    diversification = entropy / log(n_assets)

    # 3. Volatility alignment
    vol_diff = abs(portfolio_vol - target_vol)
    vol_alignment = max(0, 1 - vol_diff / target_vol)

    # Weighted aggregate
    return 0.5 * sharpe_normalized + 0.3 * diversification + 0.2 * vol_alignment
```

### RMP Iteration

```python
def rmp_optimize(initial, quality_threshold, max_iter):
    current = Monad.unit(initial)

    for i in range(max_iter):
        if current.quality >= quality_threshold:
            break

        # Compose improvements via Kleisli composition
        current = current.bind(improve_sharpe)
        current = current.bind(improve_diversification)
        current = current.bind(improve_volatility)

    return current
```

---

## Complexity Tracking

| Decision | Complexity | Justification |
|----------|------------|---------------|
| Single Python module | Low | Self-contained, no external dependencies beyond data |
| yfinance for data | Low | Well-maintained, free, covers all major markets |
| NumPy for computation | Low | Industry standard, performant |
| No database | Low | In-memory computation, no persistence needed |
| ASCII visualization | Low | Terminal-friendly, no GUI dependencies |

---

## Phase Breakdown

### Phase 0: Research (Complete)
- [x] Categorical foundations defined
- [x] Data source validated (yfinance works)
- [x] Algorithm designed

### Phase 1: Core Implementation
- [ ] Data fetching with caching
- [ ] Quality scoring functions
- [ ] RMP monad integration
- [ ] Comonadic context extraction

### Phase 2: Improvement Functions
- [ ] Sharpe optimization Kleisli arrow
- [ ] Diversification Kleisli arrow
- [ ] Volatility targeting Kleisli arrow
- [ ] Combined improvement function

### Phase 3: Testing & Validation
- [ ] Unit tests for quality scoring
- [ ] Property tests for monad laws
- [ ] Integration tests with real data
- [ ] Performance benchmarks

### Phase 4: Polish
- [ ] CLI interface with argparse
- [ ] Rich terminal output
- [ ] Comprehensive error handling
- [ ] Documentation

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Yahoo Finance API downtime | Low | Medium | Mock data fallback |
| Invalid ticker symbols | Medium | Low | Skip with warning, continue |
| Non-convergence | Low | Medium | Max iteration limit |
| Numerical instability | Low | High | Use NumPy stable operations |

---

## Dependencies

```
# requirements.txt additions
yfinance>=0.2.0
pandas>=2.0.0
numpy>=1.24.0
pytest>=7.0.0
hypothesis>=6.0.0
```

---

## Next Steps

1. Generate detailed tasks via `/speckit.tasks`
2. Implement Phase 1 (core functionality)
3. Validate with test cases from US1/US2
4. Iterate based on test results
