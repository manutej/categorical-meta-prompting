# Implementation Plan: Threat Model Compositional Builder

## Summary

Implement a categorical threat modeling system using Python, integrating MITRE ATT&CK as the knowledge base. Attack techniques form morphisms in a category of system states, with composition representing multi-stage attack chains.

---

## Technical Context

| Aspect | Decision |
|--------|----------|
| **Language** | Python 3.11+ |
| **Knowledge Base** | MITRE ATT&CK Enterprise (JSON/STIX) |
| **Graph Library** | NetworkX for path enumeration |
| **Visualization** | Graphviz/Mermaid for diagrams |
| **Framework** | Integrates with meta_prompting_engine |
| **Testing** | pytest with attack chain fixtures |

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Spec completeness | PASS | 5 user stories with acceptance criteria |
| Testability | PASS | Each story independently testable |
| Categorical rigor | PASS | State category with attack morphisms |
| Data availability | PASS | MITRE ATT&CK is open and free |

---

## Project Structure

```
meta_prompting_engine/
└── applications/
    └── threat_model/
        ├── __init__.py
        ├── states.py          # System state objects
        ├── attacks.py         # Attack morphisms (ATT&CK)
        ├── composition.py     # Chain composition
        ├── attck_loader.py    # MITRE ATT&CK integration
        ├── coverage.py        # Defense coverage analysis
        ├── visualization.py   # Diagram generation
        └── engine.py          # Main threat model engine
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Threat Model Engine                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ ATT&CK Loader│───▶│  State Cat   │───▶│  Composer    │  │
│  │  (600+ tech) │    │  (Objects)   │    │  (Morphisms) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Coverage   │    │    Paths     │    │    Visual    │  │
│  │   Analyzer   │◀──▶│  Enumerator  │───▶│   Output     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Algorithms

### Attack Chain Composition

```python
def compose_chain(attacks: List[Attack]) -> AttackPath:
    """Categorical composition of attack morphisms."""
    for i in range(len(attacks) - 1):
        if attacks[i].target_state != attacks[i+1].source_state:
            raise CompositionError("States don't match")

    return AttackPath(
        attacks=attacks,
        source=attacks[0].source_state,
        target=attacks[-1].target_state,
        total_difficulty=sum(a.difficulty for a in attacks),
        max_impact=max(a.impact for a in attacks)
    )
```

### Path Enumeration

```python
def enumerate_paths(graph: StateGraph, source: State, target: State, max_depth: int = 5) -> List[AttackPath]:
    """Find all attack paths from source to target."""
    paths = []
    for path in nx.all_simple_paths(graph, source, target, cutoff=max_depth):
        attacks = [graph.edges[path[i], path[i+1]]['attack'] for i in range(len(path)-1)]
        paths.append(compose_chain(attacks))
    return sorted(paths, key=lambda p: p.total_difficulty)
```

---

## Phase Breakdown

### Phase 1: Core Types & ATT&CK Integration
- State and Attack dataclasses
- MITRE ATT&CK JSON loader
- Technique-to-morphism mapping

### Phase 2: Composition Engine
- Chain composition with validation
- Path enumeration with NetworkX
- Difficulty and impact scoring

### Phase 3: Coverage Analysis
- Mitigation mapping
- Gap identification
- Defense prioritization

### Phase 4: Visualization & Export
- Graphviz diagram generation
- Mermaid markdown output
- JSON/STIX export

---

## Dependencies

```
networkx>=3.0
graphviz>=0.20
requests>=2.28  # For ATT&CK download
```

---

## Data Sources

- **MITRE ATT&CK Enterprise**: https://attack.mitre.org/
- **STIX/TAXII**: Structured threat data format
- **CVE Database**: Vulnerability mapping
