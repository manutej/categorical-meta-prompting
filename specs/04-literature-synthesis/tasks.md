# Task Breakdown: Literature Review Synthesis Engine

## Phase 1: Paper Retrieval

| ID | Task | Story | Files |
|----|------|-------|-------|
| T001 | Define Paper dataclass (id, title, authors, year, abstract, citations) | US1 | `types.py` |
| T002 | Implement SemanticScholarClient.search(query, limit) | US1 | `client.py` |
| T003 | Add rate limiting (100 req/5 min) | US1 | `client.py` |
| T004 | Add response caching (15 min TTL) | US1 | `client.py` |
| T005 | Implement mock data fallback | US1 | `client.py` |
| T006 | Write tests for API client | US1 | `tests/test_client.py` |

**Checkpoint**: Can search and retrieve papers.

---

## Phase 2: Finding Extraction (Functor)

| ID | Task | Story | Files |
|----|------|-------|-------|
| T010 | Define Finding dataclass (claim, evidence, source, quality, concepts) | US1 | `types.py` |
| T011 | Define QualityScore with citation/recency factors | US4 | `quality.py` |
| T012 | Implement compute_paper_quality(paper) | US4 | `quality.py` |
| T013 | Implement extract_concepts(text) with patterns | US1 | `extractor.py` |
| T014 | Implement extract_main_claim(title, abstract) | US1 | `extractor.py` |
| T015 | Implement FindingExtractor.extract(paper) → List[Finding] | US1 | `extractor.py` |
| T016 | Write test: functor preserves provenance | US3 | `tests/test_extractor.py` |
| T017 | Write test: quality scores in [0,1] | US4 | `tests/test_quality.py` |

**Checkpoint**: Functor extracts findings with quality.

---

## Phase 3: Clustering (Natural Transformation)

| ID | Task | Story | Files |
|----|------|-------|-------|
| T020 | Define Cluster dataclass (theme, findings, consensus) | US2 | `types.py` |
| T021 | Implement group_by_concepts(findings) | US2 | `clustering.py` |
| T022 | Implement compute_consensus(findings) | US2 | `clustering.py` |
| T023 | Implement cluster_findings(findings) → List[Cluster] | US2 | `clustering.py` |
| T024 | Detect contradictions within clusters | US2 | `clustering.py` |
| T025 | Write test: clustering groups related findings | US2 | `tests/test_clustering.py` |

**Checkpoint**: Natural transformation clusters findings.

---

## Phase 4: Synthesis (Colimit)

| ID | Task | Story | Files |
|----|------|-------|-------|
| T030 | Define Synthesis dataclass (clusters, provenance, confidence) | US4 | `types.py` |
| T031 | Build provenance graph (finding → paper mapping) | US3 | `provenance.py` |
| T032 | Implement synthesize(clusters) → Synthesis | US4 | `synthesis.py` |
| T033 | Compute overall confidence via geometric mean | US4 | `synthesis.py` |
| T034 | Generate narrative summary | US4 | `synthesis.py` |
| T035 | Write test: provenance is complete | US3 | `tests/test_synthesis.py` |

**Checkpoint**: Colimit produces synthesis with provenance.

---

## Phase 5: Comparison

| ID | Task | Story | Files |
|----|------|-------|-------|
| T040 | Implement compare_topics(topic1, topic2) | US5 | `comparison.py` |
| T041 | Compute relative research strength | US5 | `comparison.py` |
| T042 | Identify under-researched areas | US5 | `comparison.py` |
| T043 | Write tests for comparison | US5 | `tests/test_comparison.py` |

---

## Phase 6: Integration

| ID | Task | Story | Files |
|----|------|-------|-------|
| T050 | Create LiteratureSynthesisEngine main class | All | `engine.py` |
| T051 | Implement full workflow: search → extract → cluster → synthesize | All | `engine.py` |
| T052 | Add CLI interface | All | `cli.py` |
| T053 | Write integration tests | All | `tests/test_integration.py` |
| T054 | Create usage examples | All | `examples/` |

---

## Validation Checklist

- [ ] Functor preserves paper provenance
- [ ] Quality scores computed correctly
- [ ] Clusters are thematically coherent
- [ ] Synthesis includes all source papers
- [ ] Comparison identifies stronger topic
