# Spec-Kit Specifications for Categorical Meta-Prompting Applications

This directory contains product specifications, implementation plans, and task breakdowns for the top 10 applications of the categorical meta-prompting framework, following the [GitHub Spec-Kit](https://github.com/github/spec-kit) methodology.

## Spec-Kit Framework

Each application follows the spec-driven development workflow:

1. **Constitution** → Establish governing principles
2. **Specification** → Define requirements and user stories
3. **Plan** → Technical implementation strategy
4. **Tasks** → Granular development tasks
5. **Implement** → Execute tasks systematically

## Top 10 Applications

| # | Application | Domain | Quality Score | Status |
|---|-------------|--------|---------------|--------|
| 1 | [Portfolio Optimization](./01-portfolio-optimization/) | Finance | 0.901 | Spec Complete |
| 2 | [Threat Model Builder](./02-threat-model-builder/) | Security | 0.896 | Spec Complete |
| 3 | [Drug Interaction Checker](./03-drug-interaction-checker/) | Healthcare | 0.887 | Spec Complete |
| 4 | [Literature Synthesis](./04-literature-synthesis/) | Science | 0.885 | Spec Complete |
| 5 | [Contract Clause Composer](./05-contract-clause-composer/) | Legal | 0.878 | In Progress |
| 6 | [API Compatibility Checker](./06-api-compatibility-checker/) | Engineering | 0.874 | In Progress |
| 7 | [Data Pipeline Optimizer](./07-data-pipeline-optimizer/) | Data | 0.873 | Planned |
| 8 | [Adaptive Quiz Generation](./08-adaptive-quiz-generation/) | Education | 0.866 | Planned |
| 9 | [Fraud Detection](./09-fraud-detection/) | Finance | 0.865 | Planned |
| 10 | [Code Review Quality](./10-code-review-quality/) | Engineering | 0.865 | Planned |

## Categorical Structures by Application

| Application | Functor | Monad | Comonad | Enriched | Monoidal |
|-------------|---------|-------|---------|----------|----------|
| Portfolio | ✓ | ✓ (RMP) | ✓ (Context) | ✓ [0,1] | - |
| Threat Model | ✓ | - | - | - | ✓ (Composition) |
| Drug Interaction | ✓ | - | - | ✓ [0,1] | ✓ (Tensor) |
| Literature | ✓ (Extract) | - | - | ✓ [0,1] | ✓ (Colimit) |
| Contract | - | - | - | - | ✓ (Clauses) |
| API Compat | ✓ (Version) | - | - | - | ✓ (Migration) |
| Pipeline | ✓ | ✓ | - | ✓ [0,1] | ✓ (Stages) |
| Quiz | - | ✓ (RMP) | ✓ (Student) | ✓ [0,1] | - |
| Fraud | ✓ | - | - | ✓ [0,1] | - |
| Code Review | ✓ | - | - | ✓ [0,1] | ✓ (Checks) |

## Directory Structure

```
specs/
├── README.md                        # This file
├── 01-portfolio-optimization/
│   ├── spec.md                      # Feature specification
│   ├── plan.md                      # Implementation plan
│   └── tasks.md                     # Task breakdown
├── 02-threat-model-builder/
│   └── spec.md
├── 03-drug-interaction-checker/
│   └── spec.md
├── 04-literature-synthesis/
│   └── spec.md
├── 05-contract-clause-composer/
│   └── spec.md
├── 06-api-compatibility-checker/
│   └── spec.md
├── 07-data-pipeline-optimizer/
├── 08-adaptive-quiz-generation/
├── 09-fraud-detection/
└── 10-code-review-quality/
```

## Specification Template

Each `spec.md` follows this structure:

```markdown
# Feature Specification: [Name]

## Overview
- Product, Version, Status
- Summary (1-2 paragraphs)
- Problem Statement

## User Scenarios
- US1: [Story Name] [Priority]
  - As a [role], I want [goal], So that [benefit]
  - Given/When/Then acceptance criteria

## Functional Requirements
- FR-001: [Requirement]
- FR-002: [Requirement]

## Non-Functional Requirements
- NFR-001: Performance
- NFR-002: Reliability

## Success Criteria
| Metric | Target | Measurement |

## Categorical Structures
- Monad/Functor/Comonad definitions
- Composition laws
- Diagrams

## Data Sources
- Primary, Secondary sources

## Open Questions
- NEEDS CLARIFICATION items
```

## Quality Metrics

Specifications are evaluated on five dimensions (from meta-prompting):

| Dimension | Description | Target |
|-----------|-------------|--------|
| Clarity | Clear, unambiguous language | ≥ 0.8 |
| Actionability | Implementation path clear | ≥ 0.7 |
| Categorical Depth | Proper categorical foundations | ≥ 0.8 |
| Problem Specificity | Concrete problem definition | ≥ 0.7 |
| Data Concreteness | Specific data sources | ≥ 0.7 |

## Getting Started

1. **Read a spec**: Start with `01-portfolio-optimization/spec.md`
2. **Review the plan**: See `01-portfolio-optimization/plan.md`
3. **Pick up tasks**: Use `01-portfolio-optimization/tasks.md`
4. **Implement**: Follow task breakdown in order

## Meta-Prompting Application

These specs themselves were refined using the categorical meta-prompting framework:

```python
# Generate 50 ideas → Filter with Pareto optimization → Select top 10
top_10 = select_top_10_with_quality_enrichment(all_50_ideas)

# For each application, refine spec with RMP loop
for app in top_10:
    spec = generate_spec(app)
    while spec.quality < threshold:
        spec = improve_weakest_dimension(spec)
```

## References

- [GitHub Spec-Kit](https://github.com/github/spec-kit)
- [Categorical Meta-Prompting Framework](../README.md)
- [50 Applications Analysis](../examples/50_applications_meta_filtered.py)
