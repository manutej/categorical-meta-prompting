# Categorical MCP Server: Dependency Map & Build Order

**Purpose**: Map all dependencies and establish optimal build order for MVP
**Methodology**: Topological sort of dependency DAG

---

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CATEGORICAL MCP SERVER DEPENDENCIES                      │
└─────────────────────────────────────────────────────────────────────────────┘

LEVEL 0: No Dependencies (Foundation)
┌──────────────────────────────────────────────────────────────────────────────┐
│ ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                 │
│ │  TypeScript    │  │    Node.js     │  │   MCP SDK      │                 │
│ │   Runtime      │  │   v18+ LTS     │  │  @modelcontext │                 │
│ └────────────────┘  └────────────────┘  └────────────────┘                 │
└──────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
LEVEL 1: Core Abstractions
┌──────────────────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │  Category<Obj, Mor>                                                     │ │
│ │  • objects: Set<Obj>                                                    │ │
│ │  • morphisms: Set<Mor>                                                  │ │
│ │  • compose(f, g): Mor                                                   │ │
│ │  • identity(obj): Mor                                                   │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │  Functor<C, D>                                                          │ │
│ │  • source: Category<C>                                                  │ │
│ │  • target: Category<D>                                                  │ │
│ │  • onObjects(obj: C.Obj): D.Obj                                         │ │
│ │  • onMorphisms(mor: C.Mor): D.Mor                                       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │  SetFunctor<C>  (Database Instance)                                     │ │
│ │  • schema: Category<C>                                                  │ │
│ │  • objects(obj: C.Obj): Set<any>                                        │ │
│ │  • morphisms(mor: C.Mor): Function                                      │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
LEVEL 2: Data Migration Functors (Depends on Level 1)
┌──────────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐│
│ │  Delta (Δ)           │  │  Sigma (Σ)           │  │  Pi (Π)              ││
│ │  Pullback/Reindex    │  │  Left Adjoint        │  │  Right Adjoint       ││
│ │                      │  │  (Colimit/Union)     │  │  (Limit/Intersection)││
│ │  Δ_F: Set^D → Set^C  │  │  Σ_F: Set^C → Set^D  │  │  Π_F: Set^C → Set^D  ││
│ └──────────────────────┘  └──────────────────────┘  └──────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│                         ┌──────────────────────────┐                        │
│                         │  Adjunction Laws         │                        │
│                         │  Σ ⊣ Δ ⊣ Π               │                        │
│                         └──────────────────────────┘                        │
└──────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
LEVEL 3: Domain Models (Depends on Level 1 & 2)
┌──────────────────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │  PromptSchema: Category                                                 │ │
│ │  • Objects: [Task, Context, Mode, Format, Output]                       │ │
│ │  • Morphisms: [analyze, select_strategy, apply_template, generate]     │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │  QualitySchema: Category                                                │ │
│ │  • Objects: [Correctness, Clarity, Completeness, Efficiency, Aggregate]│ │
│ │  • Morphisms: [weight, aggregate]                                       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │  ComplexitySchema: Category                                             │ │
│ │  • Objects: [Task, Indicators, Score, Tier, Strategy]                  │ │
│ │  • Morphisms: [detect, score, classify]                                │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
LEVEL 4: Template Registry (Depends on Level 3)
┌──────────────────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │  CategoricalDatabase                                                    │ │
│ │  • schemas: Map<string, Category>                                       │ │
│ │  • instances: Map<string, SetFunctor>                                   │ │
│ │  • migrations: Map<string, Functor>                                     │ │
│ │                                                                         │ │
│ │  Methods:                                                               │ │
│ │  • getTemplate(id: string): SetFunctor                                  │ │
│ │  • migrateTemplate(from, to, functor): SetFunctor                       │ │
│ │  • registerTemplate(id, instance): void                                 │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
LEVEL 5: MCP Tools (Depends on Level 4)
┌──────────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────┐  ┌────────────────────────────────────┐│
│ │  analyze_complexity              │  │  iterate_prompt                    ││
│ │                                  │  │                                    ││
│ │  Input: Task description         │  │  Input: Task, threshold, max_iter  ││
│ │  Uses: ComplexitySchema          │  │  Uses: PromptSchema, QualitySchema ││
│ │  Migration: Σ (aggregate scores) │  │  Migration: Δ (template reuse),    ││
│ │  Output: Complexity analysis     │  │              Σ (quality aggregate) ││
│ └──────────────────────────────────┘  └────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
LEVEL 6: MCP Server (Depends on Level 5)
┌──────────────────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │  MCPServer (@modelcontext/sdk/server)                                   │ │
│ │                                                                         │ │
│ │  Tools:                                                                 │ │
│ │  • analyze_complexity                                                   │ │
│ │  • iterate_prompt                                                       │ │
│ │                                                                         │ │
│ │  Resources:                                                             │ │
│ │  • prompt://templates/{id}                                              │ │
│ │                                                                         │ │
│ │  Transport:                                                             │ │
│ │  • stdio (for Claude Code integration)                                  │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Build Order (Topological Sort)

### Phase 1: Foundation (Level 0-1)
**Duration**: 2 hours

```
1. Project setup
   ├── package.json (dependencies)
   ├── tsconfig.json (TypeScript config)
   └── src/ directory structure

2. Core category theory types
   ├── src/category/Category.ts
   ├── src/category/Functor.ts
   └── src/category/SetFunctor.ts
```

**Dependencies**: None
**Blockers**: None

---

### Phase 2: Data Migration (Level 2)
**Duration**: 2 hours

```
3. Data migration functors
   ├── src/migration/Delta.ts
   ├── src/migration/Sigma.ts
   ├── src/migration/Pi.ts
   └── src/migration/Adjunction.ts (verification)
```

**Dependencies**: Phase 1 (Category, Functor, SetFunctor)
**Blockers**: Must complete Category abstractions first

---

### Phase 3: Domain Schemas (Level 3)
**Duration**: 1.5 hours

```
4. Prompt schema
   └── src/schemas/PromptSchema.ts

5. Quality schema
   └── src/schemas/QualitySchema.ts

6. Complexity schema
   └── src/schemas/ComplexitySchema.ts
```

**Dependencies**: Phase 1 (Category)
**Blockers**: Can run in parallel with Phase 2, but needs Category types

---

### Phase 4: Template Registry (Level 4)
**Duration**: 1.5 hours

```
7. Categorical database
   └── src/registry/CategoricalDatabase.ts

8. Template instances
   ├── templates/algorithm-review.json
   ├── templates/security-review.json
   └── templates/debug-systematic.json
```

**Dependencies**: Phase 2 (migrations), Phase 3 (schemas)
**Blockers**: Needs both migration functors and domain schemas

---

### Phase 5: MCP Tools (Level 5)
**Duration**: 2 hours

```
9. analyze_complexity tool
   └── src/tools/analyze-complexity.ts

10. iterate_prompt tool
    └── src/tools/iterate-prompt.ts
```

**Dependencies**: Phase 4 (template registry)
**Blockers**: Needs database and schemas

---

### Phase 6: MCP Server (Level 6)
**Duration**: 1 hour

```
11. MCP server setup
    └── src/index.ts (server entry point)

12. Tool registration
    └── src/server/registerTools.ts

13. Resource handlers
    └── src/server/registerResources.ts
```

**Dependencies**: Phase 5 (tools)
**Blockers**: Needs all tools implemented

---

## Critical Path Analysis

**Longest dependency chain**:
```
Foundation → Migration → Schemas → Registry → Tools → Server
(2h)          (2h)       (1.5h)    (1.5h)     (2h)     (1h)
= 10 hours total
```

**Parallelizable work**:
- Phase 2 & 3 can overlap (both depend on Phase 1 only)
- Template files can be written anytime
- Testing can happen incrementally

---

## Simplified Dependency DAG

```
          ┌──────────────┐
          │  Foundation  │
          │   (Level 0-1)│
          └───────┬──────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│  Migration    │   │   Schemas     │
│   (Level 2)   │   │   (Level 3)   │
└───────┬───────┘   └───────┬───────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
          ┌───────────────┐
          │   Registry    │
          │   (Level 4)   │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │     Tools     │
          │   (Level 5)   │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │  MCP Server   │
          │   (Level 6)   │
          └───────────────┘
```

---

## Package Dependencies

### Runtime Dependencies
```json
{
  "@modelcontext/sdk": "^0.5.0",
  "zod": "^3.22.0"  // Schema validation
}
```

### Dev Dependencies
```json
{
  "typescript": "^5.3.0",
  "tsx": "^4.7.0",
  "@types/node": "^20.0.0",
  "vitest": "^1.0.0"  // Testing
}
```

### Optional (Future)
```json
{
  "fp-ts": "^2.16.0",  // Functional programming utilities
  "io-ts": "^2.2.0"    // Runtime type checking
}
```

---

## Risk Analysis

### High Risk Dependencies
1. **@modelcontext/sdk**: External package (must be compatible)
   - **Mitigation**: Pin version, test early

2. **Category/Functor abstractions**: Complex types
   - **Mitigation**: Start simple, iterate

### Medium Risk Dependencies
3. **Data migration correctness**: Math must be right
   - **Mitigation**: Property-based testing, adjunction verification

4. **Template schema design**: Must be flexible
   - **Mitigation**: Start with minimal schema, extend later

### Low Risk Dependencies
5. **MCP protocol**: Well-documented
   - **Mitigation**: Follow official examples

---

## Build Strategy

### Strategy 1: Bottom-Up (Recommended for MVP)
```
Foundation → Migration → Schemas → Registry → Tools → Server
```
**Pros**: Each layer fully tested before next
**Cons**: Slower to see working prototype

### Strategy 2: Top-Down (Faster feedback)
```
Server stub → Tool stubs → Fill in implementations backward
```
**Pros**: Working server quickly, fill in details
**Cons**: Risk of rework if abstractions wrong

### Strategy 3: Middle-Out (Balanced)
```
Schemas → Tools (simplified) → Server → Add migrations later
```
**Pros**: Working MVP without full categorical machinery
**Cons**: Less elegant, harder to add migrations later

**Recommendation**: **Strategy 1 (Bottom-Up)** for mathematical correctness

---

## Testing Strategy

### Unit Tests (Each Level)
```typescript
// Level 1: Category laws
describe('Category', () => {
  it('should satisfy identity law', () => {
    expect(cat.compose(cat.identity(a), f)).toEqual(f);
  });

  it('should satisfy associativity', () => {
    expect(cat.compose(f, cat.compose(g, h)))
      .toEqual(cat.compose(cat.compose(f, g), h));
  });
});

// Level 2: Adjunction
describe('Adjunction', () => {
  it('should satisfy Σ ⊣ Δ', () => {
    // Hom(Σ_F(I), J) ≅ Hom(I, Δ_F(J))
    expect(hom(Sigma(F, I), J)).toBeIsomorphicTo(hom(I, Delta(F, J)));
  });
});
```

### Integration Tests (Tools)
```typescript
describe('analyze_complexity', () => {
  it('should classify simple task as L1', async () => {
    const result = await analyzeComplexity({ task: "explain JWT" });
    expect(result.tier).toBe("L1");
  });
});
```

### E2E Tests (MCP Protocol)
```typescript
describe('MCP Server', () => {
  it('should respond to tools/list request', async () => {
    const response = await mcpClient.request('tools/list');
    expect(response.tools).toContainEqual(
      expect.objectContaining({ name: 'analyze_complexity' })
    );
  });
});
```

---

## Next Step: Generate MVP

With dependencies mapped, I'll now generate the MVP starting from Level 0-1 (Foundation).

**Build Order**:
1. ✅ Project structure + package.json
2. ✅ Core category types (Category, Functor, SetFunctor)
3. ✅ Data migration functors (Δ, Σ, Π)
4. ✅ Domain schemas (Prompt, Quality, Complexity)
5. ✅ Template registry
6. ✅ MCP tools (analyze_complexity, iterate_prompt)
7. ✅ MCP server

Estimated time: **10 hours** (can be compressed to 6-8 hours by skipping tests initially)

Ready to generate the MVP code?
