# Real Data Applications of Categorical Meta-Prompting

This directory contains **working examples** demonstrating the categorical meta-prompting framework on **non-trivial, real-world problems** with actual data sources.

## Overview

Each example demonstrates key categorical structures:

| Structure | Description | Example Application |
|-----------|-------------|---------------------|
| **Functor** | Structure-preserving mapping | Paper → Findings extraction |
| **Monad** | Recursive refinement with composition | Portfolio optimization iterations |
| **Comonad** | Context extraction from history | Market state extraction |
| **Enriched Category** | Quality tracking in [0,1] | Safety score degradation |
| **Monoidal Category** | Tensor product composition | Drug combination checking |

## Examples

### 1. Portfolio Optimization (`01_portfolio_optimization.py`)

**Problem**: Traditional portfolio optimization is one-shot. Markets change, requiring continuous refinement.

**Categorical Approach**:
- **Monad**: RMP loop for iterative portfolio improvement via Kleisli composition
- **Enriched Category**: [0,1] quality tracking through Sharpe ratio normalization
- **Comonad**: Extract market context (regime, volatility) from historical data

**Data Source**: Yahoo Finance API (free)

```bash
pip install yfinance pandas numpy
python 01_portfolio_optimization.py
```

**Key Insight**: Quality converges through monadic bind operations, each improving the portfolio by adjusting weights based on risk-return metrics.

---

### 2. Drug Interaction Checker (`02_drug_interaction_checker.py`)

**Problem**: Drug combinations have complex interactions with combinatorial explosion of possibilities.

**Categorical Approach**:
- **Monoidal Category**: Drugs as objects, tensor product for combinations
- **Enriched Category**: Safety scores in [0,1] that degrade multiplicatively
- **Functor**: Maps drug pairs to interaction severity

**Data Source**: DrugBank/FDA interaction database (curated subset)

```bash
python 02_drug_interaction_checker.py
```

**Key Insight**: Safety degrades through composition (tensor product). A combination of 3 drugs with individual pairwise safeties of 0.3, 0.4, 0.5 yields composite safety of 0.06 - correctly modeling compounding risk.

---

### 3. Literature Synthesis (`03_literature_synthesis.py`)

**Problem**: Literature reviews are manual and incomplete; cross-paper synthesis is difficult.

**Categorical Approach**:
- **Functor**: Paper → List[Finding] (structure-preserving extraction)
- **Natural Transformation**: Cluster related findings across papers
- **Colimit**: Synthesize findings into unified narrative
- **Enriched Category**: Evidence strength tracking

**Data Source**: Semantic Scholar API (free)

```bash
pip install requests
python 03_literature_synthesis.py
```

**Key Insight**: The functor preserves citation provenance, allowing every claim to be traced back to its source. Natural transformations group related findings across papers.

---

## Categorical Structures Demonstrated

### Monad (RMP Loop)

```
          ┌─────────────────────────┐
          │                         │
          ▼                         │
    ┌─────────┐    evaluate    ┌─────────┐    improve    ┌─────────┐
    │  unit   │───────────────▶│ quality │──────────────▶│  bind   │
    │ (init)  │                │  check  │               │ (next)  │
    └─────────┘                └─────────┘               └────┬────┘
                                    │                         │
                               threshold                      │
                                  met?                        │
                                    │                         │
                                    ▼                         │
                              ┌─────────┐                     │
                              │  DONE   │◀────────────────────┘
                              └─────────┘      (converged)
```

### Enriched Category Composition

```
Drug A ──(0.7)──▶ Drug B ──(0.8)──▶ Drug C
                       │
                       ▼
        Composite Safety = 0.7 × 0.8 = 0.56
        (tensor product in [0,1])
```

### Functor (Structure Preservation)

```
         F: Papers → Findings

Paper₁ ────────────────────▶ [Finding₁, Finding₂]
   │                              │
   │ citation                     │ provenance
   │                              │
   ▼                              ▼
Paper₂ ────────────────────▶ [Finding₃, Finding₄]
         (preserves structure)
```

## Running All Examples

```bash
# Run all examples
python 01_portfolio_optimization.py
python 02_drug_interaction_checker.py
python 03_literature_synthesis.py

# Or use the top-level runner
cd ..
python 50_applications_meta_filtered.py
```

## Quality Metrics

All examples track quality using [0,1]-enriched categories:

| Example | Quality Metric | Threshold | Typical Convergence |
|---------|---------------|-----------|---------------------|
| Portfolio | Sharpe-based | 0.85 | 5-10 iterations |
| Drug Checker | Safety score | 0.70 | Single composition |
| Literature | Evidence strength | 0.60 | N/A (colimit) |

## Dependencies

```bash
# Core (all examples)
pip install numpy

# Portfolio optimization
pip install yfinance pandas

# Literature synthesis
pip install requests
```

## References

1. Gavranović et al. (2024) - Categorical Foundations of Learning
2. Zhang et al. (2024) - Meta-Prompting for 100% Game of 24
3. de Wynter et al. (2025) - Categorical Foundations of LLMs
4. Bradley - Enriched Category Theory for AI
