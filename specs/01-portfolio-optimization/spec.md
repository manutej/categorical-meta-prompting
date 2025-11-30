# Feature Specification: Recursive Portfolio Optimization

## Overview

**Product**: Categorical Meta-Prompting Portfolio Optimizer
**Version**: 1.0
**Status**: Draft
**Last Updated**: 2024-11-29

### Summary

Build a portfolio optimization system that uses Recursive Meta-Prompting (RMP) to iteratively refine portfolio allocations. The system applies categorical structures (monads, comonads, enriched categories) to track quality through optimization iterations, extracting market context to inform each refinement step.

### Problem Statement

Traditional portfolio optimization is a one-shot process that fails to adapt to changing market conditions. Investors need a system that:
- Iteratively refines allocations based on feedback
- Tracks quality through the optimization process
- Extracts relevant market context for each decision
- Provides convergence guarantees via categorical structures

---

## User Scenarios

### US1: Basic Portfolio Optimization [P1]

**As a** retail investor
**I want to** input my stock tickers and get an optimized allocation
**So that** I can maximize risk-adjusted returns

**Given** a list of stock tickers (e.g., SPY, QQQ, TLT, GLD)
**When** I run the portfolio optimizer
**Then** I receive weight allocations that sum to 100%
**And** the portfolio's Sharpe ratio is displayed
**And** the optimization history shows quality improvement trajectory

**Acceptance Criteria**:
- [ ] Supports 2-20 stock tickers
- [ ] Weights are between 1% and 50% per asset
- [ ] Sharpe ratio calculation uses 252 trading days annualization
- [ ] Risk-free rate defaults to current 3-month T-bill

### US2: RMP Convergence Tracking [P1]

**As a** quantitative analyst
**I want to** see the iterative improvement process
**So that** I understand how the optimization converged

**Given** an initial equal-weight portfolio
**When** the RMP loop executes
**Then** I see quality scores for each iteration
**And** the loop terminates when quality threshold (0.85) is reached
**And** maximum iterations (15) prevents infinite loops

**Acceptance Criteria**:
- [ ] Quality score displayed as [0,1] value
- [ ] Quality components (Sharpe, diversification, volatility) shown separately
- [ ] Iteration count and convergence reason displayed
- [ ] Historical trajectory visualizable as progress bar

### US3: Market Context Extraction [P2]

**As a** portfolio manager
**I want to** see the market context that informed each decision
**So that** I can validate the optimization rationale

**Given** historical price data for selected assets
**When** the comonad extracts context
**Then** I see the current market regime (bull/bear/neutral)
**And** individual asset volatilities are displayed
**And** correlation matrix is available for review

**Acceptance Criteria**:
- [ ] Market regime based on 30-day momentum
- [ ] Volatilities annualized using √252 scaling
- [ ] Correlation matrix updated with each data fetch

### US4: Alternative Strategy Comparison [P2]

**As an** investment advisor
**I want to** compare different optimization strategies
**So that** I can recommend the best approach to clients

**Given** multiple optimization configurations
**When** I run comparative analysis
**Then** I see side-by-side portfolio metrics
**And** the Pareto-optimal portfolio is highlighted

**Acceptance Criteria**:
- [ ] Supports at least 3 strategy variants
- [ ] Comparison includes return, volatility, Sharpe, max drawdown
- [ ] Clear recommendation with rationale provided

### US5: Custom Constraints [P3]

**As an** institutional investor
**I want to** specify allocation constraints
**So that** the portfolio meets regulatory requirements

**Given** minimum/maximum weight constraints per asset
**When** optimization runs
**Then** final weights respect all constraints
**And** constraint violations are flagged during iteration

**Acceptance Criteria**:
- [ ] Per-asset min/max weight constraints
- [ ] Sector exposure limits (if sectors provided)
- [ ] Warning when constraints make optimization infeasible

---

## Functional Requirements

### FR-001: Data Ingestion
The system SHALL fetch historical price data for specified tickers from Yahoo Finance API.
- Default period: 2 years of daily data
- Fallback to mock data if API unavailable
- Cache data for 15 minutes to reduce API calls

### FR-002: Quality Scoring
The system SHALL compute quality scores in [0,1] using:
- Risk-adjusted return: Sharpe ratio normalized to [0,1]
- Diversification: Entropy of portfolio weights
- Volatility alignment: Distance from target volatility (15%)

### FR-003: RMP Iteration
The system SHALL implement the Recursive Meta-Prompting loop:
- Monadic bind for composing improvement functions
- Early stopping when quality threshold reached
- Maximum iteration limit for safety

### FR-004: Context Extraction
The system SHALL use comonadic structure to extract:
- Current market state (regime, volatility levels)
- Historical context (past allocations, quality trajectory)
- Asset relationships (correlations, beta values)

### FR-005: Improvement Functions
The system SHALL provide Kleisli arrows for:
- Sharpe ratio improvement (shift toward high-Sharpe assets)
- Diversification improvement (move toward equal weights)
- Volatility targeting (scale positions for target vol)

---

## Non-Functional Requirements

### NFR-001: Performance
- Data fetch: < 5 seconds for up to 20 tickers
- Single optimization iteration: < 100ms
- Full optimization (15 iterations): < 2 seconds

### NFR-002: Reliability
- Graceful degradation when API unavailable (use mock data)
- No crashes on invalid ticker symbols (skip with warning)
- Deterministic results given same random seed

### NFR-003: Usability
- Clear terminal output with progress indicators
- Quality trajectory visualized with ASCII progress bars
- Detailed logging available for debugging

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Quality Improvement | > 0.3 | Final - Initial quality score |
| Convergence Rate | > 80% | Percentage reaching threshold in max iterations |
| Sharpe Ratio | > 0.5 | Annualized risk-adjusted return |
| User Satisfaction | > 4/5 | Post-use survey rating |

---

## Categorical Structures

### Monad: RMP Refinement Loop

```
unit: Portfolio → MonadPortfolio
bind: MonadPortfolio → (Portfolio → MonadPortfolio) → MonadPortfolio

Laws:
- Left identity: unit(a).bind(f) = f(a)
- Right identity: m.bind(unit) = m
- Associativity: m.bind(f).bind(g) = m.bind(x → f(x).bind(g))
```

### Enriched Category: Quality Tracking

```
Objects: Portfolios
Hom(P1, P2): Quality score in [0,1] for transformation P1 → P2
Composition: Quality degrades via multiplication
Identity: Perfect quality (1.0)
```

### Comonad: Context Extraction

```
extract: Context → MarketState
extend: (Context → A) → Context → Context[A]

Used for: Extracting market regime, volatility context from historical data
```

---

## Open Questions

1. **NEEDS CLARIFICATION**: Should the system support real-time data updates during market hours?
2. **NEEDS CLARIFICATION**: What is the appropriate risk-free rate source for international users?
3. **NEEDS CLARIFICATION**: Should sector constraints be inferred from ticker metadata?

---

## References

- Zhang et al. (2024): Meta-Prompting for Language Models
- Gavranović et al. (2024): Categorical Foundations of Machine Learning
- Modern Portfolio Theory (Markowitz, 1952)
