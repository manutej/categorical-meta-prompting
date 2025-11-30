# Implementation Plan: Drug Interaction Compositional Checker

## Summary

Implement a drug interaction system using monoidal category structure where drugs are objects, the tensor product combines drugs, and safety scores form a [0,1]-enriched category. Safety degrades multiplicatively through composition, correctly modeling compounding risk.

---

## Technical Context

| Aspect | Decision |
|--------|----------|
| **Language** | Python 3.11+ |
| **Data Source** | DrugBank Open Data, FDA Interactions |
| **Enrichment** | [0,1]-category with multiplicative tensor |
| **Framework** | Integrates with meta_prompting_engine |
| **Testing** | pytest with clinical validation cases |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Drug Interaction Engine                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  DrugBank    │───▶│  Monoidal    │───▶│  Safety      │  │
│  │   Loader     │    │   Category   │    │  Enrichment  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Alternatives │◀──▶│   Tensor     │───▶│  Severity    │  │
│  │   Finder     │    │   Product    │    │  Classifier  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Algorithms

### Tensor Product (Drug Combination)

```python
def tensor(combo: DrugCombination, new_drug: Drug) -> DrugCombination:
    """Monoidal tensor product: add drug to combination."""
    new_interactions = []
    for existing in combo.drugs:
        interaction = lookup_interaction(existing, new_drug)
        if interaction:
            new_interactions.append(interaction)

    # Safety composition via multiplication
    new_safety = combo.safety
    for interaction in new_interactions:
        new_safety = new_safety * interaction.safety

    return DrugCombination(
        drugs=combo.drugs + [new_drug],
        interactions=combo.interactions + new_interactions,
        safety=SafetyScore(new_safety)
    )
```

### Severity Classification

```python
def classify_severity(safety: float) -> Severity:
    if safety < 0.2: return Severity.CONTRAINDICATED
    if safety < 0.4: return Severity.MAJOR
    if safety < 0.7: return Severity.MODERATE
    if safety < 0.9: return Severity.MINOR
    return Severity.NONE
```

---

## Phase Breakdown

### Phase 1: Core Types & Data
- Drug, Interaction, SafetyScore dataclasses
- DrugBank loader (open data subset)
- Interaction database with mechanisms

### Phase 2: Monoidal Structure
- Unit (empty prescription, safety=1.0)
- Tensor product implementation
- Associativity verification

### Phase 3: Safety Analysis
- Composite safety computation
- Severity classification
- Mechanism explanations

### Phase 4: Alternatives & Comparison
- Therapeutic class mapping
- Alternative finding algorithm
- Regimen comparison

---

## Dependencies

```
pandas>=2.0  # Data handling
requests>=2.28  # API calls (optional)
```

---

## Data Sources

- **DrugBank**: 13,000+ drugs, interactions
- **FDA**: Official drug interaction warnings
- **SIDER**: Side effect database
