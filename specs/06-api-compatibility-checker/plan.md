# Implementation Plan: API Compatibility Evolution Checker

## Summary

Implement an API compatibility system where versions are category objects, migrations are morphisms, and composition enables multi-version compatibility analysis. Supports OpenAPI 3.x specifications.

---

## Technical Context

| Aspect | Decision |
|--------|----------|
| **Language** | Python 3.11+ |
| **Spec Format** | OpenAPI 3.0/3.1 |
| **Parsing** | openapi-spec-validator, prance |
| **Diff Engine** | Custom with semantic analysis |
| **Framework** | Integrates with meta_prompting_engine |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                API Compatibility Engine                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   OpenAPI    │───▶│   Version    │───▶│  Migration   │  │
│  │    Parser    │    │   Category   │    │  Composer    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Change     │◀──▶│   Breaking   │───▶│   Report     │  │
│  │   Detector   │    │   Analyzer   │    │  Generator   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Algorithms

### Migration Composition

```python
def compose(m1: Migration, m2: Migration) -> Migration:
    """Categorical composition: v1→v2 ; v2→v3 = v1→v3."""
    assert m1.target == m2.source
    return Migration(
        source=m1.source,
        target=m2.target,
        breaking_changes=m1.breaking_changes + m2.breaking_changes,
        deprecations=m1.deprecations + m2.deprecations
    )
```

### Breaking Change Detection

```python
def detect_breaking(old: OpenAPI, new: OpenAPI) -> List[Change]:
    breaking = []
    # Removed endpoints
    for path in old.paths:
        if path not in new.paths:
            breaking.append(Change("REMOVED_ENDPOINT", path))
    # Changed types
    for path, methods in old.paths.items():
        for method, spec in methods.items():
            if path in new.paths and method in new.paths[path]:
                if not types_compatible(spec.response, new.paths[path][method].response):
                    breaking.append(Change("TYPE_CHANGE", f"{path}.{method}"))
    return breaking
```

---

## Phase Breakdown

### Phase 1: OpenAPI Parsing
- Parse OpenAPI 3.x specs
- Normalize to internal representation
- Handle $ref resolution

### Phase 2: Change Detection
- Endpoint additions/removals
- Type compatibility checking
- Parameter changes

### Phase 3: Migration Category
- Version objects
- Migration morphisms
- Composition implementation

### Phase 4: Reporting
- Breaking vs non-breaking classification
- Migration guide generation
- Semver recommendation

---

## Dependencies

```
openapi-spec-validator>=0.5
prance>=0.22
pyyaml>=6.0
```
