# Feature Specification: Threat Model Compositional Builder

## Overview

**Product**: Categorical Threat Model Builder
**Version**: 1.0
**Status**: Draft
**Last Updated**: 2024-11-29

### Summary

Build a threat modeling system that represents attack paths as categorical compositions. System states are objects, attacks are morphisms, and attack chains compose to form complete threat models. Uses MITRE ATT&CK as the primary knowledge base for attack techniques.

### Problem Statement

Threat modeling is often ad-hoc, leading to missed attack paths. Security teams need:
- Systematic composition of attack chains
- Visualization of multi-stage attacks
- Complete coverage verification
- Integration with industry-standard frameworks (MITRE ATT&CK)

---

## User Scenarios

### US1: Build Attack Chain [P1]

**As a** security analyst
**I want to** compose attack techniques into complete attack paths
**So that** I can understand potential threat scenarios

**Given** a system architecture description
**When** I build a threat model
**Then** I see possible attack chains from initial access to impact
**And** each step shows the MITRE ATT&CK technique used
**And** the chain forms a valid categorical composition

**Acceptance Criteria**:
- [ ] Map system components to category objects (states)
- [ ] Attack techniques as morphisms between states
- [ ] Composition validates prerequisites are met
- [ ] Display chain as visual diagram

### US2: Coverage Analysis [P2]

**As a** security architect
**I want to** verify my defenses cover all attack paths
**So that** I can identify security gaps

**Given** a threat model and list of mitigations
**When** I run coverage analysis
**Then** I see which attack paths are blocked
**And** I see which paths remain viable
**And** gaps are prioritized by impact

**Acceptance Criteria**:
- [ ] Map mitigations to techniques they block
- [ ] Identify unblocked attack paths
- [ ] Rank gaps by potential impact
- [ ] Suggest additional mitigations

### US3: ATT&CK Integration [P1]

**As a** threat intelligence analyst
**I want to** use MITRE ATT&CK techniques directly
**So that** I use industry-standard terminology

**Given** the MITRE ATT&CK framework
**When** I browse available techniques
**Then** I see techniques organized by tactic
**And** I can search by technique ID or name
**And** I can add techniques to my model

**Acceptance Criteria**:
- [ ] Import full ATT&CK Enterprise matrix
- [ ] Support all 14 tactics (Reconnaissance to Impact)
- [ ] Include technique prerequisites
- [ ] Link to official ATT&CK documentation

### US4: Multi-Path Analysis [P2]

**As a** red team lead
**I want to** explore all possible attack paths
**So that** I can prioritize penetration testing

**Given** a system model
**When** I run path enumeration
**Then** I see all viable paths from entry to objective
**And** paths are ranked by feasibility
**And** critical chokepoints are identified

**Acceptance Criteria**:
- [ ] Enumerate paths up to configurable depth
- [ ] Score path feasibility based on technique difficulty
- [ ] Identify common chokepoints (defense priorities)
- [ ] Export paths for test planning

### US5: Threat Actor Profiling [P3]

**As a** threat intelligence manager
**I want to** model known threat actors
**So that** I can simulate their likely attack patterns

**Given** a threat actor profile (TTPs)
**When** I simulate their attack
**Then** I see the most likely attack chains
**And** chains use techniques from their known toolkit
**And** novel technique gaps are highlighted

**Acceptance Criteria**:
- [ ] Import actor profiles from CTI sources
- [ ] Filter techniques by actor's known TTPs
- [ ] Generate actor-specific attack trees
- [ ] Identify technique evolution opportunities

---

## Functional Requirements

### FR-001: State Category
The system SHALL model system states as:
- Objects: System states (initial, compromised, lateral, exfiltrated, etc.)
- Morphisms: Attacks that transition between states
- Identity: No-op (system remains in state)
- Composition: Multi-stage attack chains

### FR-002: Attack Morphisms
The system SHALL represent attacks as morphisms with:
- Source state: Prerequisites for the attack
- Target state: Result of successful attack
- Technique: MITRE ATT&CK technique reference
- Difficulty: Estimated effort (1-10)
- Impact: Potential damage (1-10)

### FR-003: Chain Composition
The system SHALL compose attack chains where:
- Composition validates state compatibility
- Chain impact = maximum individual impact
- Chain difficulty = sum of difficulties
- Invalid compositions (state mismatch) are rejected

### FR-004: ATT&CK Knowledge Base
The system SHALL integrate MITRE ATT&CK:
- All Enterprise techniques (600+)
- Technique relationships and prerequisites
- Tactic categorization
- Mitigation mappings

### FR-005: Visualization
The system SHALL generate diagrams showing:
- States as nodes
- Attacks as directed edges
- Chains as highlighted paths
- Critical chokepoints marked

---

## Non-Functional Requirements

### NFR-001: Performance
- Technique lookup: < 50ms
- Path enumeration (depth 5): < 5 seconds
- Full matrix visualization: < 3 seconds

### NFR-002: Completeness
- Cover 100% of ATT&CK Enterprise techniques
- Regular updates with ATT&CK releases
- Version tracking for reproducibility

### NFR-003: Extensibility
- Custom technique definitions
- Plugin architecture for new data sources
- API for integration with security tools

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Technique Coverage | 100% | All ATT&CK Enterprise techniques |
| Path Discovery | > 95% | Known attack paths identified |
| User Adoption | > 10 | Security teams using in production |
| Gap Detection | > 80% | Identified gaps are real vulnerabilities |

---

## Categorical Structures

### Category of System States

```
Objects: S = {Initial, UserAccess, AdminAccess, LateralMove, DataAccess, Exfil}

Morphisms:
  - Phishing: Initial → UserAccess
  - PrivEsc: UserAccess → AdminAccess
  - PassTheHash: AdminAccess → LateralMove
  - SQLi: LateralMove → DataAccess
  - C2Channel: DataAccess → Exfil

Composition:
  Phishing ; PrivEsc ; PassTheHash ; SQLi ; C2Channel
  = Complete attack chain from Initial to Exfil
```

### Attack Chain Diagram

```
Initial ──[T1566.001]──▶ UserAccess ──[T1548.002]──▶ AdminAccess
                                                          │
                                                    [T1550.002]
                                                          │
Exfil ◀──[T1041]── DataAccess ◀──[T1190]── LateralMove ◀─┘

Legend: [TXXXX] = MITRE ATT&CK Technique ID
```

### Composition Validation

```python
def can_compose(m1: Attack, m2: Attack) -> bool:
    """Check if two attacks can be composed."""
    return m1.target_state == m2.source_state

def compose(chain: List[Attack]) -> AttackPath:
    """Compose attack chain with validation."""
    for i in range(len(chain) - 1):
        if not can_compose(chain[i], chain[i+1]):
            raise CompositionError(
                f"Cannot compose: {chain[i].name} → {chain[i+1].name}"
            )
    return AttackPath(chain)
```

---

## Data Sources

### Primary: MITRE ATT&CK
- Enterprise Matrix v14+
- Technique descriptions
- Mitigations and detections
- Threat actor mappings

### Secondary: CVE Database
- Vulnerability-to-technique mappings
- Real-world exploit data
- Severity scores (CVSS)

### Tertiary: Threat Intelligence Feeds
- APT group profiles
- Emerging techniques
- Campaign data

---

## Open Questions

1. **NEEDS CLARIFICATION**: Should cloud and ICS matrices be included?
2. **NEEDS CLARIFICATION**: How to model probabilistic attack success?
3. **NEEDS CLARIFICATION**: Integration with SIEM/SOAR platforms?

---

## References

- MITRE ATT&CK Framework (https://attack.mitre.org/)
- Category Theory for Security (Goguen, Meseguer)
- Threat Modeling: Designing for Security (Shostack)
