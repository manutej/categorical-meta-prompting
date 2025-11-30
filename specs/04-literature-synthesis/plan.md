# Implementation Plan: Literature Review Synthesis Engine

## Summary

Implement a literature synthesis system using functorial extraction (Paper → Findings), natural transformations for clustering, and colimits for synthesis. Integrates with Semantic Scholar API for real academic data with quality-enriched confidence tracking.

---

## Technical Context

| Aspect | Decision |
|--------|----------|
| **Language** | Python 3.11+ |
| **API** | Semantic Scholar (free, 200M+ papers) |
| **NLP** | spaCy for concept extraction |
| **Clustering** | scikit-learn for semantic grouping |
| **Framework** | Integrates with meta_prompting_engine |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               Literature Synthesis Engine                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Semantic   │───▶│   Functor    │───▶│   Natural    │  │
│  │   Scholar    │    │  (Extract)   │    │   Transform  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Provenance  │◀──▶│   Quality    │───▶│   Colimit    │  │
│  │    Graph     │    │  Enrichment  │    │  (Synthesis) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Algorithms

### Functor: Paper → Findings

```python
def extract_findings(paper: Paper) -> List[Finding]:
    """Functor F: Paper → List[Finding]."""
    base_quality = compute_paper_quality(paper)
    main_claim = extract_main_claim(paper.title, paper.abstract)
    concepts = extract_concepts(paper.abstract)

    findings = [Finding(
        claim=main_claim,
        evidence=paper.abstract[:200],
        source=paper,
        quality=base_quality,
        concepts=concepts
    )]
    return findings
```

### Natural Transformation: Clustering

```python
def cluster_findings(findings: List[Finding]) -> List[Cluster]:
    """Natural transformation η: List[Finding] → List[Cluster]."""
    concept_groups = group_by_concepts(findings)
    clusters = []
    for concept, group in concept_groups.items():
        consensus = compute_consensus(group)
        clusters.append(Cluster(theme=concept, findings=group, consensus=consensus))
    return clusters
```

---

## Phase Breakdown

### Phase 1: Paper Retrieval
- Semantic Scholar API client
- Paper dataclass with metadata
- Rate limiting and caching

### Phase 2: Finding Extraction (Functor)
- Quality computation from citations/venue/year
- Concept extraction with spaCy
- Claim extraction from title/abstract

### Phase 3: Clustering (Natural Transformation)
- Concept-based grouping
- Consensus computation
- Conflict detection

### Phase 4: Synthesis (Colimit)
- Narrative generation
- Confidence aggregation
- Provenance tracking

---

## Dependencies

```
requests>=2.28
spacy>=3.0
scikit-learn>=1.0
```

---

## Data Sources

- **Semantic Scholar**: 200M+ papers, free API
- **arXiv**: Preprints with abstracts
- **PubMed**: Biomedical literature
