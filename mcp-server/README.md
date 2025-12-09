# Categorical Meta-Prompting MCP Server

**Version**: 0.1.0 (MVP)
**Foundation**: Spivak's Functorial Data Migration + Category Theory

---

## Overview

This MCP server implements **categorical meta-prompting** using functorial data migration. It provides tools for analyzing task complexity and routing to appropriate meta-prompting strategies.

### Core Innovation

Prompt templates are modeled as **categorical databases** where:
- **Schemas = Categories** (objects = types, morphisms = constraints)
- **Instances = Functors** (C → Set, mapping types to data)
- **Transformations = Data Migration** (Δ, Σ, Π functors)

---

## Installation

```bash
npm install
npm run build
```

---

## Usage

### Configure in Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "categorical-meta-prompting": {
      "command": "node",
      "args": ["/path/to/categorical-meta-prompting-mcp/dist/index.js"]
    }
  }
}
```

### Tools Available

#### `analyze_complexity`

Analyzes task complexity using categorical schema:

```typescript
Input: { task: string }

Output: {
  score: 0.0-1.0,          // Complexity score via Σ aggregation
  tier: "L1" | ... | "L7", // Classification via functor
  strategy: string,         // Recommended strategy
  reasoning: string,        // Explanation
  suggested_iterations: number,
  estimated_tokens: number
}
```

**Example**:

```
User: "Build a self-healing Apache Spark pipeline on Kubernetes"

MCP Tool Call: analyze_complexity
{
  "task": "Build a self-healing Apache Spark pipeline on Kubernetes"
}

Result:
{
  "score": 0.77,
  "tier": "L5",
  "strategy": "AUTONOMOUS_EVOLUTION",
  "reasoning": "Detected indicators: multi component, architecture, fault tolerance, distributed, observability, data pipeline, scale, implementation",
  "suggested_iterations": 3,
  "estimated_tokens": 7250
}
```

---

## Categorical Architecture

### Data Migration Functors

```
Δ (Delta): Pullback    - Pull templates to specialized contexts
Σ (Sigma): Colimit     - Aggregate quality scores (weighted average)
Π (Pi):    Limit       - Filter prompts meeting all criteria
```

### Adjunction Chain

```
Σ ⊣ Δ ⊣ Π

Guarantees:
- Hom(Σ_F(I), J) ≅ Hom(I, Δ_F(J))  (Σ left adjoint to Δ)
- Hom(Δ_F(J), K) ≅ Hom(J, Π_F(K))  (Δ left adjoint to Π)
```

### Example: Complexity Analysis Flow

```
Task (string)
  │
  ▼ Δ: detect patterns
Indicators (Set<boolean>)
  │
  ▼ Σ: weighted aggregation (colimit)
Score (0.0-1.0)
  │
  ▼ Functor: classify
Tier (L1-L7)
  │
  ▼ Functor: select strategy
Strategy (DIRECT | MULTI_APPROACH | AUTONOMOUS_EVOLUTION)
```

---

## Testing

```bash
npm test
```

**Test Categories**:
- Category laws (identity, associativity)
- Functor laws (preserves identity, composition)
- Adjunction verification (Σ ⊣ Δ ⊣ Π)
- Tool integration (analyze_complexity)

---

## Project Structure

```
src/
├── category/
│   ├── Category.ts       # Core category abstraction
│   └── Functor.ts        # Functors and SetFunctors
├── migration/
│   └── DataMigration.ts  # Δ, Σ, Π functors
├── schemas/
│   └── index.ts          # Domain schemas (Complexity, Quality, Prompt)
├── tools/
│   └── analyze-complexity.ts  # MCP tool implementation
└── index.ts              # MCP server entry point
```

---

## Mathematical Foundations

### Category

```typescript
interface Category<Obj, Mor> {
  objects: Set<Obj>;
  morphisms: Set<Mor>;
  compose(f: Mor, g: Mor): Mor;  // g ∘ f
  identity(obj: Obj): Mor;       // id_obj
}

Laws:
  f ∘ id_A = f = id_B ∘ f        (Identity)
  (h ∘ g) ∘ f = h ∘ (g ∘ f)      (Associativity)
```

### Functor

```typescript
interface Functor<C, D> {
  onObjects(obj: C.Obj): D.Obj;
  onMorphisms(mor: C.Mor): D.Mor;
}

Laws:
  F(id_A) = id_{F(A)}            (Preserves identity)
  F(g ∘ f) = F(g) ∘ F(f)         (Preserves composition)
```

### Data Migration

```typescript
Δ_F(I)(c) = I(F(c))              // Pullback
Σ_F(I)(d) = colim_{F(c)=d} I(c)  // Colimit (union/aggregation)
Π_F(I)(d) = lim_{F(c)=d} I(c)    // Limit (intersection/filtering)
```

---

## Future Enhancements

### Phase 2: Extended Tools
- `iterate_prompt`: Quality-driven iteration with Σ aggregation
- `assess_quality`: Multi-dimensional quality functor
- `extract_context`: Comonad W extraction

### Phase 3: Polynomial Functors
- Tool composition: `p ∘ q`
- Wiring diagrams for orchestration

### Phase 4: State Management
- SQLite storage for quality history
- Learning from past iterations

---

## References

1. Spivak, D. I. (2012). **Functorial Data Migration**. arXiv:1009.1166
2. Fong, B., & Spivak, D. I. (2018). **Seven Sketches in Compositionality**
3. Spivak, D. I. (2014). **Category Theory for the Sciences**. MIT Press

---

## License

MIT

---

## Author

Manu Tej ([@manutej](https://github.com/manutej))

---

**Status**: MVP Complete ✅
**Categorical Foundations**: Implemented ✅
**MCP Integration**: Ready for Testing ⏳
