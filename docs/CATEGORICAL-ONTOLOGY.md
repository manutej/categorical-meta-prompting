# Categorical Meta-Prompting: Hierarchical Ontology

**Version**: 1.0 | **Generated**: 2025-12-01

---

## 1. NESTED CONCEPTUAL HIERARCHY

```
CATEGORICAL META-PROMPTING ONTOLOGY
═══════════════════════════════════════════════════════════════════════════════

                        ┌───────────────────────────────────────┐
                        │     LEVEL 0: UNIVERSE                 │
                        │     Categorical Meta-Prompting        │
                        └───────────────────┬───────────────────┘
                                            │
        ┌───────────────────────────────────┼───────────────────────────────────┐
        │                                   │                                   │
        ▼                                   ▼                                   ▼
┌───────────────────┐             ┌───────────────────┐             ┌───────────────────┐
│ LEVEL 1: CATEGORY │             │ LEVEL 1: CATEGORY │             │ LEVEL 1: CATEGORY │
│    STRUCTURES     │             │     EXECUTION     │             │      QUALITY      │
│                   │             │                   │             │                   │
│ ┌───────────────┐ │             │ ┌───────────────┐ │             │ ┌───────────────┐ │
│ │ F: Functor    │ │             │ │ Commands      │ │             │ │ Assessment    │ │
│ │ M: Monad      │ │             │ │ Workflows     │ │             │ │ Propagation   │ │
│ │ W: Comonad    │ │             │ │ Prompts       │ │             │ │ Laws          │ │
│ │ α: NatTrans   │ │             │ │ Skills        │ │             │ │ Thresholds    │ │
│ └───────────────┘ │             │ └───────────────┘ │             │ └───────────────┘ │
└─────────┬─────────┘             └─────────┬─────────┘             └─────────┬─────────┘
          │                                 │                                 │
    ┌─────┴─────┐                     ┌─────┴─────┐                     ┌─────┴─────┐
    │           │                     │           │                     │           │
    ▼           ▼                     ▼           ▼                     ▼           ▼
┌───────┐   ┌───────┐           ┌───────┐   ┌───────┐           ┌───────┐   ┌───────┐
│LEVEL 2│   │LEVEL 2│           │LEVEL 2│   │LEVEL 2│           │LEVEL 2│   │LEVEL 2│
│Objects│   │Morphs │           │ Core  │   │Orchest│           │Metrics│   │ Rules │
│       │   │       │           │       │   │ration │           │       │   │       │
│ Task  │   │ →     │           │ /meta │   │/build │           │ corr  │   │ → min │
│Prompt │   │ ||    │           │ /rmp  │   │/review│           │ clar  │   │ || avg│
│Context│   │ ⊗     │           │ /chain│   │/test  │           │ comp  │   │ ⊗ min │
│Quality│   │ >=>   │           │ /ctx  │   │/fix   │           │ effi  │   │>=>conv│
└───────┘   └───────┘           └───────┘   └───────┘           └───────┘   └───────┘

```

---

## 2. FUNCTIONAL DECOMPOSITION

### 2.1 FUNCTOR F: Task → Prompt

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          F: Task → Prompt                                    │
│                       (Structure-Preserving Map)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INPUT SPACE (Task)                    OUTPUT SPACE (Prompt)                │
│  ══════════════════                    ═════════════════════                │
│                                                                              │
│  ┌─────────────────┐                   ┌─────────────────────────┐          │
│  │ task_text       │                   │ {context:X}             │          │
│  │ @modifiers      │  ────F────▶       │ {mode:Y}                │          │
│  │ [operators]     │                   │ {format:Z}              │          │
│  └─────────────────┘                   │ domain_prompt           │          │
│                                        └─────────────────────────┘          │
│                                                                              │
│  FUNCTORIAL COMPONENTS:                                                     │
│  ══════════════════════                                                     │
│                                                                              │
│     F = F_domain ∘ F_tier ∘ F_template                                      │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │ F_domain    │───▶│ F_tier      │───▶│ F_template  │                     │
│  │             │    │             │    │             │                     │
│  │ Keywords→   │    │ Complexity→ │    │ Components→ │                     │
│  │ Domain      │    │ L1-L7       │    │ Assembled   │                     │
│  └─────────────┘    └─────────────┘    └─────────────┘                     │
│                                                                              │
│  LAWS:                                                                      │
│  ═════                                                                      │
│  • F(id_task) = id_prompt           (identity preserved)                    │
│  • F(g ∘ f) = F(g) ∘ F(f)           (composition preserved)                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 MONAD M: Prompt →ⁿ Prompt

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        M: Prompt →ⁿ Prompt                                   │
│                      (Iterative Refinement)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  MONAD OPERATIONS:                                                          │
│  ═════════════════                                                          │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   unit: A → M(A)                return: lift into monad             │   │
│  │   ────────────────────────────────────────────────────────────      │   │
│  │                                                                     │   │
│  │        a ────────▶ M(a, q=initial)                                  │   │
│  │                                                                     │   │
│  │                                                                     │   │
│  │   bind: M(A) → (A → M(B)) → M(B)   chain with refinement            │   │
│  │   ────────────────────────────────────────────────────────────      │   │
│  │                                                                     │   │
│  │   M(a, q₀) ─────▶ f ─────▶ M(b, q₁)                                │   │
│  │                    │                                                │   │
│  │                    └───▶ assess quality                             │   │
│  │                         └───▶ if q < θ: refine                     │   │
│  │                                                                     │   │
│  │                                                                     │   │
│  │   join: M(M(A)) → M(A)         flatten nested monads                │   │
│  │   ────────────────────────────────────────────────────────────      │   │
│  │                                                                     │   │
│  │   M(M(a)) ─────────▶ M(a)      (unwrap one layer)                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ITERATION TRAJECTORY:                                                      │
│  ═════════════════════                                                      │
│                                                                              │
│     q₀ ─────▶ q₁ ─────▶ q₂ ─────▶ ... ─────▶ qₙ ≥ θ                        │
│        Δq₁       Δq₂       Δq₃                  CONVERGE                    │
│                                                                              │
│  LAWS:                                                                      │
│  ═════                                                                      │
│  • unit(a) >>= f = f(a)                   (left identity)                   │
│  • m >>= unit = m                          (right identity)                  │
│  • (m >>= f) >>= g = m >>= (λx. f(x) >>= g)  (associativity)               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 COMONAD W: History → Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        W: History → Context                                  │
│                       (Context Extraction)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  COMONAD OPERATIONS:                                                        │
│  ═══════════════════                                                        │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   extract: W(A) → A              counit ε: focus on current         │   │
│  │   ────────────────────────────────────────────────────────────      │   │
│  │                                                                     │   │
│  │   W(history) ────────▶ focused_context                              │   │
│  │       │                      │                                      │   │
│  │       │                      └───▶ most relevant subset             │   │
│  │       └───▶ full history                                            │   │
│  │                                                                     │   │
│  │                                                                     │   │
│  │   duplicate: W(A) → W(W(A))      comult δ: meta-observation         │   │
│  │   ────────────────────────────────────────────────────────────      │   │
│  │                                                                     │   │
│  │   W(a) ─────────▶ W(W(a))                                          │   │
│  │                        │                                            │   │
│  │                        └───▶ context of context                     │   │
│  │                              (what was focused/filtered)            │   │
│  │                                                                     │   │
│  │                                                                     │   │
│  │   extend: (W(A)→B) → W(A) → W(B)   cobind: transform with context  │   │
│  │   ────────────────────────────────────────────────────────────      │   │
│  │                                                                     │   │
│  │   W(a) + f ────────▶ W(f(W(a)))                                    │   │
│  │             │              │                                        │   │
│  │             │              └───▶ apply f at each position          │   │
│  │             └───▶ transformation function                           │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  FOCUS TARGETS (@focus:):                                                   │
│  ════════════════════════                                                   │
│                                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   recent   │  │    all     │  │    file    │  │conversation│            │
│  │ (last N)   │  │ (full)     │  │ (specific) │  │ (flow)     │            │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘            │
│                                                                              │
│  LAWS:                                                                      │
│  ═════                                                                      │
│  • extract ∘ duplicate = id                                                 │
│  • fmap extract ∘ duplicate = id                                            │
│  • duplicate ∘ duplicate = fmap duplicate ∘ duplicate                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 NATURAL TRANSFORMATION α: F ⇒ G

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          α: F ⇒ G                                            │
│                  (Strategy Transformation)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  NATURALITY SQUARE (must commute):                                          │
│  ═════════════════════════════════                                          │
│                                                                              │
│                        F(f)                                                  │
│                 F(A) ───────▶ F(B)                                          │
│                   │            │                                             │
│                α_A│            │α_B                                          │
│                   ▼            ▼                                             │
│                 G(A) ───────▶ G(B)                                          │
│                        G(f)                                                  │
│                                                                              │
│  Condition: α_B ∘ F(f) = G(f) ∘ α_A                                         │
│                                                                              │
│                                                                              │
│  STRATEGY FUNCTORS:                                                         │
│  ══════════════════                                                         │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  F_ZS  ─────▶ DirectPrompt        Zero-Shot       q = 0.65          │  │
│  │                                                                      │  │
│  │  F_FS  ─────▶ ExemplarPrompt      Few-Shot        q = 0.78          │  │
│  │                                                                      │  │
│  │  F_CoT ─────▶ ReasoningPrompt     Chain-of-Thought q = 0.85         │  │
│  │                                                                      │  │
│  │  F_ToT ─────▶ BranchingPrompt     Tree-of-Thought  q = 0.88         │  │
│  │                                                                      │  │
│  │  F_Meta ────▶ MetaPrompt          Meta-Prompting   q = 0.90         │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│                                                                              │
│  TRANSFORMATION RULES:                                                      │
│  ═════════════════════                                                      │
│                                                                              │
│     α[ZS→CoT]:  ADD "step by step"                                         │
│     α[FS→CoT]:  TRANSFORM examples → reasoning traces                       │
│     α[CoT→ToT]: ADD branching + backtracking                                │
│     α[*→Meta]:  WRAP with strategy selection layer                          │
│                                                                              │
│  QUALITY IMPACT:                                                            │
│  ═══════════════                                                            │
│                                                                              │
│     q(α[from→to](x)) = transform_factor × q(x)                              │
│                                                                              │
│     where transform_factor = matrix[from][to]                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. COMPOSITION ALGEBRA

### 3.1 Operators as Morphisms

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPOSITION OPERATORS AS MORPHISMS                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  OPERATOR SEMANTICS:                                                        │
│  ═══════════════════                                                        │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  → (SEQUENCE)                       || (PARALLEL)                   │   │
│  │  ─────────────                      ─────────────                   │   │
│  │                                                                     │   │
│  │  Type: A → B → C                    Type: A → (B × C × D)           │   │
│  │                                                                     │   │
│  │       ┌───┐    ┌───┐                    ┌───┐                       │   │
│  │  ────▶│ A │───▶│ B │───▶          ┌───▶│ B │───┐                   │   │
│  │       └───┘    └───┘              │    └───┘   │                   │   │
│  │                              ────▶├───▶│ C │───┼───▶               │   │
│  │  Quality: min(qₐ, qᵦ)             │    └───┘   │                   │   │
│  │                                   └───▶│ D │───┘                   │   │
│  │                                        └───┘                       │   │
│  │                                                                     │   │
│  │                                   Quality: mean(qᵦ, qᵧ, qᵨ)        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ⊗ (TENSOR)                         >=> (KLEISLI)                   │   │
│  │  ──────────                         ─────────────                   │   │
│  │                                                                     │   │
│  │  Type: (A × B) → C                  Type: A →ᵐ B →ᵐ C               │   │
│  │                                                                     │   │
│  │  ┌───┐                                   ┌───┐                      │   │
│  │  │ A │                              ────▶│ A │                      │   │
│  │  │ ⊗ │───▶ combined                      └─┬─┘                      │   │
│  │  │ B │                                    │ q≥θ?                    │   │
│  │  └───┘                                    ├─YES─▶┌───┐              │   │
│  │                                           │      │ B │───▶          │   │
│  │  Quality: min(qₐ, qᵦ)                     │      └───┘              │   │
│  │                                           └─NO──▶ refine            │   │
│  │                                                  └───▶ retry        │   │
│  │                                                                     │   │
│  │                                   Quality: converges iteratively    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Quality Lattice

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QUALITY LATTICE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                            1.0 (PERFECT)                                    │
│                                 │                                            │
│                                 │                                            │
│              ┌──────────────────┼──────────────────┐                        │
│              │                  │                  │                        │
│              ▼                  ▼                  ▼                        │
│          ┌───────┐         ┌───────┐         ┌───────┐                     │
│          │ 0.95  │         │ 0.92  │         │ 0.90  │   EXCELLENT          │
│          │ Meta  │         │ ToT   │         │ CoT   │   [0.90, 1.0]        │
│          └───┬───┘         └───┬───┘         └───┬───┘                     │
│              │                 │                 │                          │
│              └─────────────────┼─────────────────┘                          │
│                                │                                            │
│              ┌─────────────────┼─────────────────┐                          │
│              │                 │                 │                          │
│              ▼                 ▼                 ▼                          │
│          ┌───────┐         ┌───────┐         ┌───────┐                     │
│          │ 0.85  │         │ 0.82  │         │ 0.80  │   GOOD               │
│          │ multi │         │ iter  │         │ FS    │   [0.80, 0.90)       │
│          └───┬───┘         └───┬───┘         └───┬───┘                     │
│              │                 │                 │                          │
│              └─────────────────┼─────────────────┘                          │
│                                │                                            │
│              ┌─────────────────┼─────────────────┐                          │
│              │                 │                 │                          │
│              ▼                 ▼                 ▼                          │
│          ┌───────┐         ┌───────┐         ┌───────┐                     │
│          │ 0.75  │         │ 0.72  │         │ 0.70  │   ACCEPTABLE         │
│          │ cot   │         │struct │         │ rev   │   [0.70, 0.80)       │
│          └───┬───┘         └───┬───┘         └───┬───┘                     │
│              │                 │                 │                          │
│              └─────────────────┼─────────────────┘                          │
│                                │                                            │
│                                ▼                                            │
│                           ┌───────┐                                         │
│                           │ 0.65  │   POOR [0.60, 0.70)                     │
│                           │ direct│                                         │
│                           └───┬───┘                                         │
│                               │                                             │
│                               ▼                                             │
│                            0.0 (FAILED)  [0.0, 0.60)                        │
│                                                                              │
│  LATTICE OPERATIONS:                                                        │
│  ═══════════════════                                                        │
│  • meet (∧): min(a, b)  - tensor/sequence composition                       │
│  • join (∨): max(a, b)  - best of alternatives                              │
│  • avg:      mean(a,b)  - parallel composition                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. CORE IDEAS SUMMARY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CORE IDEAS: EXECUTIVE SUMMARY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  1. PROMPTS AS MATHEMATICAL OBJECTS                                    ║ │
│  ╠═══════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                        ║ │
│  ║  Tasks and prompts live in categories with structure-preserving maps.  ║ │
│  ║  This enables:                                                         ║ │
│  ║  • Predictable composition (laws guarantee behavior)                   ║ │
│  ║  • Quality tracking (enrichment over [0,1])                           ║ │
│  ║  • Strategy switching (natural transformations)                        ║ │
│  ║                                                                        ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  2. FOUR CATEGORICAL STRUCTURES                                        ║ │
│  ╠═══════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                        ║ │
│  ║  F (Functor):  Task → Prompt    "What strategy to use"                 ║ │
│  ║  M (Monad):    Prompt →ⁿ Prompt "How to refine iteratively"           ║ │
│  ║  W (Comonad):  History → Context "What context to extract"            ║ │
│  ║  α (NatTrans): F ⇒ G           "How to switch strategies"             ║ │
│  ║                                                                        ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  3. QUALITY AS FIRST-CLASS CITIZEN                                     ║ │
│  ╠═══════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                        ║ │
│  ║  Quality is not an afterthought—it's baked into the mathematics:       ║ │
│  ║  • Multi-dimensional: correctness, clarity, completeness, efficiency   ║ │
│  ║  • Propagates through composition: min for →, mean for ||              ║ │
│  ║  • Gates iteration: converge when q ≥ θ                               ║ │
│  ║  • Enriches the category: morphisms have quality values                ║ │
│  ║                                                                        ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  4. UNIFIED SYNTAX = PREDICTABLE BEHAVIOR                              ║ │
│  ╠═══════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                        ║ │
│  ║  Every command follows the same pattern:                               ║ │
│  ║                                                                        ║ │
│  ║    /<cmd> @mod1:val @mod2:val [operators] "task"                       ║ │
│  ║                                                                        ║ │
│  ║  This enables:                                                         ║ │
│  ║  • Composability: commands chain via operators                         ║ │
│  ║  • Consistency: same modifiers work everywhere                         ║ │
│  ║  • Predictability: know what will happen from syntax                   ║ │
│  ║                                                                        ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗ │
│  ║  5. ORCHESTRATION = CATEGORICAL COMPOSITION                            ║ │
│  ╠═══════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                        ║ │
│  ║  Complex workflows are just compositions of simpler operations:        ║ │
│  ║                                                                        ║ │
│  ║  /meta-build   = W → F → M → (Review || Test) → M                      ║ │
│  ║  /meta-review  = Read → (Corr || Sec || Perf || Maint) → Synth        ║ │
│  ║  /meta-deploy  = (Test || Review || Prereq) → Build → Stage → Prod    ║ │
│  ║                                                                        ║ │
│  ║  Each stage preserves categorical laws.                                ║ │
│  ║                                                                        ║ │
│  ╚═══════════════════════════════════════════════════════════════════════╝ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. VISUAL ONTOLOGY MAP

```
═══════════════════════════════════════════════════════════════════════════════
                    CATEGORICAL META-PROMPTING ONTOLOGY
═══════════════════════════════════════════════════════════════════════════════

                              ┌─────────────────────┐
                              │  CATEGORICAL THEORY │
                              │  ═════════════════  │
                              │  F, M, W, α, [0,1]  │
                              └──────────┬──────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         ▼                               ▼                               ▼
┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
│   STRUCTURES    │           │   EXECUTION     │           │    QUALITY      │
│   ═══════════   │           │   ═════════     │           │    ═══════      │
└────────┬────────┘           └────────┬────────┘           └────────┬────────┘
         │                             │                             │
    ┌────┴────┐                   ┌────┴────┐                   ┌────┴────┐
    │         │                   │         │                   │         │
    ▼         ▼                   ▼         ▼                   ▼         ▼
┌───────┐ ┌───────┐         ┌───────┐ ┌───────┐         ┌───────┐ ┌───────┐
│Objects│ │Morphs │         │Commands│ │Skills │         │Metrics│ │ Laws  │
├───────┤ ├───────┤         ├───────┤ ├───────┤         ├───────┤ ├───────┤
│Task   │ │ →     │         │/meta  │ │meta-  │         │corr   │ │→ min  │
│Prompt │ │ ||    │         │/rmp   │ │ self  │         │clar   │ │|| avg │
│Context│ │ ⊗     │         │/chain │ │rmp    │         │comp   │ │⊗ min  │
│Quality│ │ >=>   │         │/ctx   │ │quality│         │effi   │ │>=>conv│
└───────┘ └───────┘         │/trans │ │prompt │         └───────┘ └───────┘
                            │/debug │ │ reg   │
                            │/review│ └───────┘
                            └───┬───┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
               ▼                ▼                ▼
         ┌───────────┐   ┌───────────┐   ┌───────────┐
         │/meta-build│   │/meta-     │   │/meta-     │
         │/meta-fix  │   │ review    │   │ deploy    │
         │/meta-     │   │/meta-test │   │/meta-     │
         │ refactor  │   │           │   │ ...       │
         └───────────┘   └───────────┘   └───────────┘
              ▲                ▲                ▲
              │                │                │
              └────────────────┴────────────────┘
                              │
                   ┌──────────┴──────────┐
                   │   PROMPT LIBRARY    │
                   │   ══════════════    │
                   │                     │
                   │  {context:X}        │
                   │  {mode:Y}           │
                   │  {format:Z}         │
                   │  {prompt:NAME}      │
                   │                     │
                   │  Domain templates   │
                   │  Quality scores     │
                   └─────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
LEGEND:
  F = Functor (strategy selection)
  M = Monad (iterative refinement)
  W = Comonad (context extraction)
  α = Natural Transformation (strategy switching)
  [0,1] = Quality enrichment category
═══════════════════════════════════════════════════════════════════════════════
```

---

## 6. KNOWLEDGE DENSITY COMPRESSION

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MAXIMUM COMPRESSION: ONE-PAGE SUMMARY                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  WHAT: Prompts compose like functions in category theory                    │
│                                                                              │
│  WHY:  Predictable behavior, quality tracking, strategy switching           │
│                                                                              │
│  HOW:  F→M→W→α pipeline with [0,1]-enriched quality                        │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  F: Task → Prompt         "Select strategy based on domain & complexity"    │
│  M: Prompt →ⁿ Prompt      "Refine until quality ≥ threshold"               │
│  W: History → Context     "Extract relevant context from execution"         │
│  α: F ⇒ G                 "Switch between prompting strategies"             │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  OPERATORS:  →  sequential (min)   ||  parallel (avg)                       │
│              ⊗  tensor (min)       >=> kleisli (converges)                  │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  QUALITY:    q = 0.40×corr + 0.25×clar + 0.20×comp + 0.15×effi             │
│                                                                              │
│  THRESHOLDS: ≥0.90 excellent │ ≥0.80 good │ ≥0.70 ok │ <0.60 fail          │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                              │
│  SYNTAX:     /<cmd> @mode:X @quality:Y [ops] "task"                         │
│                                                                              │
│  EXAMPLE:    /rmp @quality:0.85 [/analyze→/design→/implement] "feature"     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*Generated via W.extract(parallel_research) | 4 concurrent streams synthesized*
