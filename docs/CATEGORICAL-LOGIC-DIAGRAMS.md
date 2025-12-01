# Categorical Meta-Prompting: Logic Diagrams

**Version**: 1.0 | **Generated**: 2025-12-01 | **Synthesis**: W.extract(parallel research)

---

## 1. MASTER ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CATEGORICAL META-PROMPTING SYSTEM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   INPUT                   CATEGORICAL PIPELINE                    OUTPUT    │
│   ═════                   ══════════════════                      ══════    │
│                                                                              │
│   ┌─────────┐    ┌───┐    ┌───┐    ┌───┐    ┌───┐    ┌───────────────┐    │
│   │  Task   │───▶│ F │───▶│ M │───▶│ W │───▶│ α │───▶│  Quality[0,1] │    │
│   │ + mods  │    └───┘    └───┘    └───┘    └───┘    │  Result       │    │
│   └─────────┘    Functor  Monad   Comonad  NatTrans  └───────────────┘    │
│                                                                              │
│   F: Task → Prompt        (strategy selection)                              │
│   M: Prompt →ⁿ Prompt     (iterative refinement)                            │
│   W: History → Context    (context extraction)                              │
│   α: F ⇒ G                (strategy transformation)                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. CORE COMMANDS LOGIC FLOW

### 2.1 `/meta` - Categorical Meta-Prompting

```
INPUT: /meta @mode:X @tier:Y @template:Z "task"
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│ PHASE 1: F(task) - FUNCTOR APPLICATION                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐     ┌────────────────┐                   │
│   │ @domain:?   │────▶│ AUTO-DETECT    │                   │
│   │ specified?  │ NO  │ via keywords   │                   │
│   └─────────────┘     └────────────────┘                   │
│         │ YES                │                              │
│         ▼                    ▼                              │
│   ┌─────────────────────────────┐                          │
│   │ Domain ∈ {ALGORITHM,        │                          │
│   │   SECURITY, API, DEBUG,     │                          │
│   │   TESTING, GENERAL}         │                          │
│   └─────────────────────────────┘                          │
│                   │                                         │
│                   ▼                                         │
│   ┌─────────────────────────────────────┐                  │
│   │ TIER CLASSIFICATION                  │                  │
│   ├─────────────────────────────────────┤                  │
│   │ L1-L2 → STRATEGY: DIRECT            │                  │
│   │ L3-L4 → STRATEGY: MULTI_APPROACH    │                  │
│   │ L5-L7 → STRATEGY: AUTONOMOUS_EVOL   │                  │
│   └─────────────────────────────────────┘                  │
└────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│ PHASE 2: MODE DISPATCH                                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│   @mode:active ─────────▶ Execute immediately               │
│         │                                                   │
│   @mode:iterative ──────▶ Enable RMP loop (M.bind)         │
│         │                                                   │
│   @mode:dry-run ────────▶ Output plan → EXIT               │
│         │                                                   │
│   @mode:spec ───────────▶ Output YAML spec → EXIT          │
│                                                             │
└────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│ PHASE 3: TEMPLATE ASSEMBLY                                  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│   @template:{context:X}+{mode:Y}+{format:Z}                │
│             │            │          │                       │
│             ▼            ▼          ▼                       │
│   ┌─────────────┐ ┌──────────┐ ┌──────────┐               │
│   │ expert      │ │ direct   │ │ prose    │               │
│   │ teacher     │ │ cot      │ │ struct   │               │
│   │ reviewer    │ │ multi    │ │ code     │               │
│   │ debugger    │ │ iterative│ │ checklist│               │
│   └─────────────┘ └──────────┘ └──────────┘               │
│                                                             │
│   ASSEMBLED PROMPT = render(context, mode, format, task)   │
│                                                             │
└────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│ PHASE 4-6: EXECUTE → QUALITY → OUTPUT                       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│   Execute ───▶ Assess Quality ───▶ @mode:iterative? ──┐    │
│      │              │                    │ YES         │    │
│      │              ▼                    ▼             │    │
│      │    ┌─────────────────┐   ┌──────────────┐     │    │
│      │    │ correctness 40% │   │ q < threshold │─────┘    │
│      │    │ clarity     25% │   │      ↓        │          │
│      │    │ completeness20% │   │ M.bind(refine)│          │
│      │    │ efficiency  15% │   └──────────────┘          │
│      │    └─────────────────┘            │ NO              │
│      │              │                    ▼                 │
│      │              └───────────▶ W.extract(result)        │
│      │                                   │                 │
│      └───────────────────────────────────┘                 │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 2.2 `/rmp` - Recursive Meta-Prompting

```
INPUT: /rmp @quality:0.85 @max_iterations:5 "task"
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                 RMP MONAD ITERATION LOOP                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   M.unit(p₀) ─────────────────────────────────────┐         │
│        │                                           │         │
│        ▼                                           │         │
│   ┌─────────────────────────────────────────────┐ │         │
│   │           ITERATION n                        │ │         │
│   ├─────────────────────────────────────────────┤ │         │
│   │                                              │ │         │
│   │  ┌───────────────┐                          │ │         │
│   │  │ GENERATE/     │                          │ │         │
│   │  │ REFINE OUTPUT │                          │ │         │
│   │  └───────┬───────┘                          │ │         │
│   │          │                                   │ │         │
│   │          ▼                                   │ │         │
│   │  ┌───────────────────────────┐              │ │         │
│   │  │ ASSESS QUALITY            │              │ │         │
│   │  │ ─────────────────────     │              │ │         │
│   │  │ correctness:  0.XX        │              │ │         │
│   │  │ clarity:      0.XX        │              │ │         │
│   │  │ completeness: 0.XX        │              │ │         │
│   │  │ efficiency:   0.XX        │              │ │         │
│   │  │ ─────────────────────     │              │ │         │
│   │  │ AGGREGATE:    0.XX        │              │ │         │
│   │  └───────┬───────────────────┘              │ │         │
│   │          │                                   │ │         │
│   │          ▼                                   │ │         │
│   │  ┌───────────────────────────────┐          │ │         │
│   │  │ CONVERGENCE CHECK             │          │ │         │
│   │  ├───────────────────────────────┤          │ │         │
│   │  │                               │          │ │         │
│   │  │  q ≥ @quality? ─────YES────▶ CONVERGE    │ │         │
│   │  │       │                       │          │ │         │
│   │  │      NO                       │          │ │         │
│   │  │       │                       │          │ │         │
│   │  │       ▼                       │          │ │         │
│   │  │  n ≥ max? ──────YES────────▶ MAX_ITER   │ │         │
│   │  │       │                       │          │ │         │
│   │  │      NO                       │          │ │         │
│   │  │       │                       │          │ │         │
│   │  │       ▼                       │          │ │         │
│   │  │  Δq < 0.02? ────YES────────▶ PLATEAU    │ │         │
│   │  │       │                       │          │ │         │
│   │  │      NO                       │          │ │         │
│   │  │       │                       │          │ │         │
│   │  │       ▼                       │          │ │         │
│   │  │    CONTINUE ──────────────────┼──────────┘ │         │
│   │  │                               │            │         │
│   │  └───────────────────────────────┘            │         │
│   │                                                │         │
│   └────────────────────────────────────────────────┘         │
│                            │                                 │
│                            ▼                                 │
│   M.return(pₙ, qₙ) ────▶ OUTPUT with checkpoint              │
│                                                              │
└─────────────────────────────────────────────────────────────┘

QUALITY TRAJECTORY: [q₀] →[Δq₁]→ [q₁] →[Δq₂]→ [q₂] →...→ [qₙ]
```

### 2.3 `/chain` - Composition Operators

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPOSITION OPERATOR SEMANTICS                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  SEQUENTIAL (→)                    PARALLEL (||)                            │
│  ═══════════════                   ═════════════                            │
│                                                                              │
│  /chain [A → B → C]                /chain [A || B || C]                     │
│                                                                              │
│       ┌───┐                             ┌───┐                               │
│  ────▶│ A │────┐                   ┌───▶│ A │───┐                           │
│       └───┘    │                   │    └───┘   │                           │
│                ▼                   │             │                           │
│           ┌───┐                    │    ┌───┐   │                           │
│           │ B │────┐          ────▶├───▶│ B │───┼───▶ AGGREGATE             │
│           └───┘    │               │    └───┘   │                           │
│                    ▼               │             │                           │
│               ┌───┐                │    ┌───┐   │                           │
│               │ C │───▶            └───▶│ C │───┘                           │
│               └───┘                     └───┘                               │
│                                                                              │
│  Quality: min(qA, qB, qC)          Quality: mean(qA, qB, qC)                │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  KLEISLI (>=>)                     TENSOR (⊗)                               │
│  ═════════════                     ══════════                               │
│                                                                              │
│  /rmp [A >=> B >=> C]              /chain [A ⊗ B]                           │
│                                                                              │
│       ┌───┐  q≥θ?  ┌───┐                ┌───┐                               │
│  ────▶│ A │──YES──▶│ B │───▶            │ A │                               │
│       └───┘   │    └───┘           ────▶│ ⊗ │───▶ COMBINED                  │
│               │NO                       │ B │                               │
│               ▼                         └───┘                               │
│          ┌────────┐                                                         │
│          │ REFINE │                                                         │
│          └───┬────┘                                                         │
│              └─────▶                                                        │
│                                                                              │
│  Quality: improves iteratively     Quality: min(qA, qB)                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 `/context` - Comonad W Operations

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        COMONAD W: CONTEXT EXTRACTION                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   @mode:extract (DEFAULT)          @mode:duplicate                         │
│   ══════════════════════           ════════════════                        │
│                                                                             │
│   W(History)                       W(History)                              │
│       │                                │                                    │
│       ▼                                ▼                                    │
│   ┌─────────────────┐            ┌─────────────────────┐                   │
│   │ ε: W(A) → A     │            │ δ: W(A) → W(W(A))   │                   │
│   │ (counit)        │            │ (comultiplication)  │                   │
│   └────────┬────────┘            └──────────┬──────────┘                   │
│            │                                │                               │
│            ▼                                ▼                               │
│   ┌─────────────────┐            ┌─────────────────────┐                   │
│   │ Focused Result  │            │ Meta-Observation    │                   │
│   │ (most relevant) │            │ (context of context)│                   │
│   └─────────────────┘            └─────────────────────┘                   │
│                                                                             │
│   @mode:extend                                                              │
│   ════════════                                                              │
│                                                                             │
│   W(History) + f: W(A) → B                                                 │
│       │                                                                     │
│       ▼                                                                     │
│   ┌─────────────────────────────┐                                          │
│   │ extend(f)(W(A)) = W(B)      │                                          │
│   │ Apply f with full context   │                                          │
│   └─────────────┬───────────────┘                                          │
│                 │                                                           │
│                 ▼                                                           │
│   ┌─────────────────────────────┐                                          │
│   │ Transformed Result          │                                          │
│   │ (summarize/analyze/synth)   │                                          │
│   └─────────────────────────────┘                                          │
│                                                                             │
│   COMONAD LAWS:                                                            │
│   ├─ extract ∘ duplicate = id                                              │
│   ├─ fmap extract ∘ duplicate = id                                         │
│   └─ duplicate ∘ duplicate = fmap duplicate ∘ duplicate                    │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### 2.5 `/transform` - Natural Transformation α

```
┌────────────────────────────────────────────────────────────────────────────┐
│                  NATURAL TRANSFORMATION α: F ⇒ G                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   STRATEGY FUNCTORS:                                                        │
│   ══════════════════                                                        │
│                                                                             │
│   F_ZS  : Task → DirectPrompt       (Zero-Shot)      q=0.65                │
│   F_FS  : Task → ExemplarPrompt     (Few-Shot)       q=0.78                │
│   F_CoT : Task → ReasoningPrompt    (Chain-of-Thought) q=0.85              │
│   F_ToT : Task → BranchingPrompt    (Tree-of-Thought) q=0.88               │
│   F_Meta: Task → MetaPrompt         (Meta-Prompting) q=0.90                │
│                                                                             │
│   TRANSFORMATION DIAGRAM:                                                   │
│   ══════════════════════                                                    │
│                                                                             │
│                      F(f)                                                   │
│               F(A) ───────▶ F(B)                                           │
│                 │            │                                              │
│              α_A│            │α_B                                           │
│                 ▼            ▼                                              │
│               G(A) ───────▶ G(B)                                           │
│                      G(f)                                                   │
│                                                                             │
│   NATURALITY: α_B ∘ F(f) = G(f) ∘ α_A                                      │
│                                                                             │
│   TRANSFORMATION MATRIX (quality multiplier):                               │
│   ═══════════════════════════════════════════                              │
│                                                                             │
│         │ ZS    FS    CoT   ToT   Meta                                     │
│   ──────┼─────────────────────────────                                     │
│   ZS    │ 1.0   1.15  1.25  1.30  1.35                                     │
│   FS    │ 0.85  1.0   1.10  1.15  1.20                                     │
│   CoT   │ 0.75  0.90  1.0   1.05  1.10                                     │
│   ToT   │ 0.70  0.85  0.95  1.0   1.05                                     │
│   Meta  │ 0.70  0.85  0.92  0.98  1.0                                      │
│                                                                             │
│   q(α[from→to]) = matrix[from][to] × q(source)                             │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. ORCHESTRATION WORKFLOWS

### 3.1 `/meta-build` - Feature Construction Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        META-BUILD: R → D → I → T                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STAGE 0               STAGE 1               STAGE 2 (PARALLEL)             │
│  EXPLORE              ANALYZE                DESIGN                         │
│  ══════════           ════════               ═══════════════                │
│                                                                              │
│  ┌──────────┐        ┌──────────┐           ┌────────────────┐             │
│  │ Read     │        │ /route   │           │ ┌────────────┐ │             │
│  │ codebase │───────▶│ feature  │──────────▶│ │ ARCH DESIGN│ │             │
│  │ patterns │        └──────────┘           │ ├────────────┤ │             │
│  └──────────┘               │               │ │ DATA DESIGN│ │             │
│       │                     ▼               │ ├────────────┤ │             │
│       │              ┌──────────┐           │ │ UI DESIGN  │ │             │
│       │              │ /build-  │           │ └────────────┘ │             │
│       │              │ prompt   │           └───────┬────────┘             │
│       │              └──────────┘                   │                       │
│       │                                             ▼                       │
│  ◆ context:gathered   ◆ routing:complete      ◆ design:validated           │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STAGE 3               STAGE 4 (PARALLEL)      STAGE 5 (LOOP)              │
│  IMPLEMENT            QA                        REFINE                      │
│  ══════════           ═══════════════          ════════════                 │
│                                                                              │
│  ┌──────────┐        ┌────────────────┐       ┌──────────────┐             │
│  │ /compose │        │ ┌────────────┐ │       │  q < 8?      │             │
│  │ analyze  │        │ │  /review   │ │       │     │        │             │
│  │ plan     │───────▶│ ├────────────┤ │──────▶│    YES       │             │
│  │ implement│        │ │ /meta-test │ │       │     │        │             │
│  └──────────┘        │ └────────────┘ │       │     ▼        │             │
│       │              └───────┬────────┘       │ /rmp q≥8     │──┐          │
│       │                      │                │     │        │  │          │
│       │                      ▼                │    NO        │  │          │
│       │              ┌──────────────┐         │     │        │  │max 3     │
│       │              │ q≥7 AND      │         │     ▼        │  │          │
│       │              │ tests:pass?  │         │  DONE        │◀─┘          │
│       │              └──────────────┘         └──────────────┘             │
│       │                                                                     │
│  ◆ impl:complete      ◆ qa:passed              ◆ quality≥8                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 `/meta-review` - Parallel Multi-Pass Review

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    META-REVIEW: 4-PASS PARALLEL REVIEW                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   STAGE 1: READ                    STAGE 2: PARALLEL REVIEWS                │
│   ════════════                     ═══════════════════════                  │
│                                                                              │
│   ┌──────────────┐                ┌─────────────────────────────────────┐   │
│   │ Read code    │                │                                     │   │
│   │ Identify     │                │  ┌───────────┐    ┌───────────┐    │   │
│   │ domain       │───────────────▶│  │CORRECTNESS│    │ SECURITY  │    │   │
│   │ Note areas   │                │  │  Pass     │    │   Pass    │    │   │
│   └──────────────┘                │  │  /10      │    │   /10     │    │   │
│         │                         │  └───────────┘    └───────────┘    │   │
│         │                         │                                     │   │
│         ▼                         │  ┌───────────┐    ┌───────────┐    │   │
│   ◆ context:                      │  │PERFORMANCE│    │MAINTAIN-  │    │   │
│     understood                    │  │  Pass     │    │ ABILITY   │    │   │
│                                   │  │  /10      │    │   /10     │    │   │
│                                   │  └───────────┘    └───────────┘    │   │
│                                   │                                     │   │
│                                   └──────────────────┬──────────────────┘   │
│                                                      │                      │
│                                                      ▼                      │
│                                              ◆ all:reviews:complete         │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   STAGE 3: SYNTHESIZE              STAGE 4-5: DEEP DIVE & VERDICT          │
│   ═══════════════════              ═══════════════════════════             │
│                                                                              │
│   ┌──────────────────┐            ┌────────────────────────────┐           │
│   │ Merge findings   │            │ @if critical_issues > 0:   │           │
│   │ Remove duplicates│            │    /debug critical_issues  │           │
│   │ Rank by severity │───────────▶│                            │           │
│   │ Resolve conflicts│            │ @if security_issues > 0:   │           │
│   └──────────────────┘            │    ⚡security-analysis     │           │
│         │                         └─────────────┬──────────────┘           │
│         │                                       │                           │
│         ▼                                       ▼                           │
│   ◆ findings:                          ┌──────────────────────┐            │
│     synthesized                        │ VERDICT:              │            │
│                                        │ ├─ ≥8.0 → APPROVE     │            │
│   SCORING:                             │ ├─ ≥6.0 → REQ CHANGES│            │
│   40% correctness                      │ └─ <6.0 → REJECT     │            │
│   30% security                         └──────────────────────┘            │
│   15% performance                                                           │
│   15% maintainability                                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 `/meta-deploy` - Safe Deployment with Rollback

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              META-DEPLOY: VALIDATION → BUILD → STAGE → PROD                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STAGE 1 (PARALLEL)                STAGE 2                STAGE 3          │
│  PRE-VALIDATION                    BUILD                  STAGING          │
│  ═══════════════                   ═════                  ═══════          │
│                                                                              │
│  ┌───────────────────┐            ┌──────────┐          ┌──────────┐       │
│  │ ┌──────────────┐  │            │ Build    │          │ Deploy   │       │
│  │ │ /meta-test   │  │            │ artifact │          │ staging  │       │
│  │ ├──────────────┤  │            │          │──────────│          │       │
│  │ │ /meta-review │  │───────────▶│ Verify   │          │ Smoke    │       │
│  │ ├──────────────┤  │            │ integrity│          │ tests    │       │
│  │ │ Prerequisites│  │            └──────────┘          └────┬─────┘       │
│  │ └──────────────┘  │                  │                    │             │
│  └───────────────────┘                  │                    ▼             │
│         │                               │              ┌──────────┐        │
│         ▼                               │              │ PASS?    │        │
│  ┌──────────────┐                       │              └────┬─────┘        │
│  │ ALL PASS?    │                       │                   │              │
│  │  YES → cont  │                       │              YES  │  NO          │
│  │  NO → ABORT  │                       │                   │   │          │
│  └──────────────┘                       │                   │   ▼          │
│                                         │                   │ ABORT        │
│  ◆ validated                     ◆ built               ◆ staging:healthy   │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STAGE 4                                STAGE 5 (PARALLEL)                  │
│  PRODUCTION                             POST-VERIFICATION (10 min)          │
│  ══════════                             ══════════════════════              │
│                                                                              │
│  ┌────────────────────────┐            ┌─────────────────────────────┐     │
│  │ 1. Capture snapshot    │            │ ┌─────────┐ ┌─────────────┐ │     │
│  │    (rollback point)    │            │ │ Error   │ │ Key Metrics │ │     │
│  │                        │            │ │ Rates   │ │ Latency/CPU │ │     │
│  │ 2. Deploy production   │───────────▶│ └─────────┘ └─────────────┘ │     │
│  │                        │            │                             │     │
│  │ 3. Health check (60s)  │            │ ┌─────────────────────────┐ │     │
│  │    └─ FAIL → ROLLBACK  │            │ │ Production Smoke Tests  │ │     │
│  └────────────────────────┘            │ └─────────────────────────┘ │     │
│         │                              └──────────────┬──────────────┘     │
│         │                                             │                    │
│         ▼                                             ▼                    │
│  ◆ production:healthy                         ┌──────────────┐            │
│                                               │ ANOMALY?     │            │
│  🚨 AUTO-ROLLBACK:                            │  YES → 🚨    │            │
│  If health fails OR                           │  NO → ✓      │            │
│  anomaly detected                             └──────────────┘            │
│                                                                            │
│                                               STAGE 6: Tag & Finalize     │
│                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. PROMPT REGISTRY & TEMPLATE SYSTEM

### 4.1 Template Component Algebra

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TEMPLATE COMPOSITION ALGEBRA                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  COMPONENT TYPES:                                                           │
│  ═══════════════                                                            │
│                                                                              │
│  {context:X}          {mode:X}            {format:X}                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │ expert  q=1.0│    │ direct  q=1.0│    │ prose   q=1.0│                  │
│  │ teacher q=.95│    │ cot     q=1.2│    │ struct  q=1.0│                  │
│  │ reviewer q=.9│    │ multi   q=1.3│    │ code    q=1.0│                  │
│  │ debugger q=.9│    │ iterate q=1.3│    │ check   q=.95│                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│                                                                              │
│  COMPOSITION (+):                                                           │
│  ════════════════                                                           │
│                                                                              │
│  @template:{context:expert}+{mode:cot}+{format:code}                        │
│                                                                              │
│  QUALITY CALCULATION:                                                       │
│  ════════════════════                                                       │
│                                                                              │
│  q_final = q_base × q_context × q_mode × q_format                          │
│          = 0.80   × 1.0       × 1.2    × 1.0                               │
│          = 0.96                                                             │
│                                                                              │
│  MONOID STRUCTURE:                                                          │
│  ═════════════════                                                          │
│                                                                              │
│  Identity: {context:expert}+{mode:direct}+{format:prose}                    │
│  Associativity: (T₁ + T₂) + T₃ = T₁ + (T₂ + T₃)                            │
│  Closure: T₁ + T₂ ∈ Template                                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Domain Routing & Selection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROMPT SELECTION ALGORITHM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INPUT: task_text                                                           │
│      │                                                                       │
│      ▼                                                                       │
│  ┌───────────────────────────────────────┐                                  │
│  │ DOMAIN CLASSIFICATION (keyword match) │                                  │
│  ├───────────────────────────────────────┤                                  │
│  │                                       │                                  │
│  │  ALGORITHM: loop, sort, O(n), tree   │                                  │
│  │  SECURITY:  auth, token, injection   │                                  │
│  │  API:       endpoint, REST, HTTP     │                                  │
│  │  DEBUG:     error, bug, crash        │                                  │
│  │  TESTING:   test, mock, assert       │                                  │
│  │  GENERAL:   (no keywords match)      │                                  │
│  │                                       │                                  │
│  └───────────────────┬───────────────────┘                                  │
│                      │                                                       │
│                      ▼                                                       │
│  ┌───────────────────────────────────────┐                                  │
│  │ SELECT FROM REGISTRY                  │                                  │
│  ├───────────────────────────────────────┤                                  │
│  │                                       │                                  │
│  │  candidates = registry.by_domain(D)  │                                  │
│  │  filtered = [p for p if p.q ≥ min_q] │                                  │
│  │  selected = max(filtered, key=q)     │                                  │
│  │                                       │                                  │
│  └───────────────────┬───────────────────┘                                  │
│                      │                                                       │
│                      ▼                                                       │
│  OUTPUT: selected_prompt with quality score                                 │
│                                                                              │
│  REGISTRY PROMPTS:                                                          │
│  ═════════════════                                                          │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────┐              │
│  │ Name                  │ Domain    │ Quality │ Tags       │              │
│  ├──────────────────────────────────────────────────────────┤              │
│  │ debug                 │ DEBUG     │ 0.80    │ systematic │              │
│  │ review_algorithm      │ ALGORITHM │ 0.80    │ complexity │              │
│  │ review_security       │ SECURITY  │ 0.85    │ owasp      │              │
│  │ test_generate         │ TESTING   │ 0.75    │ coverage   │              │
│  │ categorical-structure │ FRAMEWORK │ 0.92    │ category   │              │
│  │ functor-transform     │ CORE      │ 0.90    │ functor    │              │
│  │ monad-refine          │ CORE      │ 0.92    │ monad      │              │
│  │ comonad-extract       │ CORE      │ 0.88    │ comonad    │              │
│  │ pipeline-compose      │ WORKFLOW  │ 0.91    │ kleisli    │              │
│  └──────────────────────────────────────────────────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. QUALITY ENRICHMENT ([0,1]-CATEGORY)

### 5.1 Quality Propagation Laws

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QUALITY LAWS ([0,1]-ENRICHED CATEGORY)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  COMPOSITION RULES:                                                         │
│  ══════════════════                                                         │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                                                                    │    │
│  │  SEQUENTIAL (→):   q(A → B) = min(qₐ, qᵦ)                         │    │
│  │                    Bottleneck at weakest link                      │    │
│  │                                                                    │    │
│  │  PARALLEL (||):    q(A || B || C) = mean(qₐ, qᵦ, qᵧ)              │    │
│  │                    Average of concurrent paths                     │    │
│  │                                                                    │    │
│  │  TENSOR (⊗):       q(A ⊗ B) = min(qₐ, qᵦ)                         │    │
│  │                    System reliability = weakest component          │    │
│  │                                                                    │    │
│  │  KLEISLI (>=>):    q(A >=> B) ≈ converges to max(qₐ, qᵦ)          │    │
│  │                    Quality-gated iteration improves over time      │    │
│  │                                                                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  CATEGORICAL LAWS:                                                          │
│  ═════════════════                                                          │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                                                                    │    │
│  │  FUNCTOR:                                                          │    │
│  │    F(id) = id                    (identity preserved)              │    │
│  │    F(g ∘ f) = F(g) ∘ F(f)        (composition preserved)           │    │
│  │                                                                    │    │
│  │  MONAD:                                                            │    │
│  │    return >=> f = f              (left identity)                   │    │
│  │    f >=> return = f              (right identity)                  │    │
│  │    (f >=> g) >=> h = f >=> (g >=> h)  (associativity)             │    │
│  │                                                                    │    │
│  │  COMONAD:                                                          │    │
│  │    extract ∘ duplicate = id      (left identity)                   │    │
│  │    fmap extract ∘ duplicate = id (right identity)                  │    │
│  │    duplicate ∘ duplicate = fmap duplicate ∘ duplicate              │    │
│  │                                                                    │    │
│  │  QUALITY:                                                          │    │
│  │    q(A ⊗ B) ≤ min(q(A), q(B))   (monotonicity)                    │    │
│  │    q(id) = 1.0                   (identity preserves quality)     │    │
│  │                                                                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Quality Assessment Vector

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MULTI-DIMENSIONAL QUALITY ASSESSMENT                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   DIMENSIONS:                                                               │
│   ═══════════                                                               │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                                                                 │      │
│   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │      │
│   │  │ CORRECTNESS │ │   CLARITY   │ │COMPLETENESS │ │EFFICIENCY │ │      │
│   │  │    40%      │ │    25%      │ │    20%      │ │   15%     │ │      │
│   │  ├─────────────┤ ├─────────────┤ ├─────────────┤ ├───────────┤ │      │
│   │  │ Solves the  │ │ Understand- │ │ Edge cases  │ │ Well-     │ │      │
│   │  │ problem?    │ │ able?       │ │ handled?    │ │ designed? │ │      │
│   │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │      │
│   │                                                                 │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                              │
│   AGGREGATE FORMULA:                                                        │
│   ══════════════════                                                        │
│                                                                              │
│   q_aggregate = 0.40×correctness + 0.25×clarity +                           │
│                 0.20×completeness + 0.15×efficiency                         │
│                                                                              │
│   THRESHOLDS:                                                               │
│   ═══════════                                                               │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │ Score Range │ Status     │ Action              │ Iteration     │     │
│   ├──────────────────────────────────────────────────────────────────┤     │
│   │ [0.90, 1.0] │ EXCELLENT  │ ACCEPT              │ STOP          │     │
│   │ [0.80, 0.90)│ GOOD       │ ACCEPT              │ STOP          │     │
│   │ [0.70, 0.80)│ ACCEPTABLE │ CONTINUE_IF_ITER    │ REFINE        │     │
│   │ [0.60, 0.70)│ POOR       │ REFINE              │ IMPROVE       │     │
│   │ [0.00, 0.60)│ FAILED     │ ABORT/RESTRUCTURE   │ HALT          │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. UNIFIED SYNTAX REFERENCE

### 6.1 Command Syntax Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED SYNTAX PATTERN                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TEMPLATE:                                                                  │
│  ═════════                                                                  │
│                                                                              │
│  /<command> @mod1:val1 @mod2:val2 [composition] "task"                      │
│                                                                              │
│                                                                              │
│  MODIFIERS:                                                                 │
│  ══════════                                                                 │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ Modifier       │ Values                │ Default │ Purpose        │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │ @mode:         │ active,iterative,     │ active  │ Execution mode │    │
│  │                │ dry-run,spec          │         │                │    │
│  │ @quality:      │ [0.0, 1.0]            │ 0.8     │ Threshold      │    │
│  │ @tier:         │ L1-L7                 │ auto    │ Complexity     │    │
│  │ @template:     │ {ctx}+{mode}+{fmt}    │ auto    │ Components     │    │
│  │ @domain:       │ ALGORITHM,SECURITY... │ auto    │ Force domain   │    │
│  │ @max_iterations│ ℕ                     │ 5       │ Iteration cap  │    │
│  │ @budget:       │ ℕ or auto             │ auto    │ Token budget   │    │
│  │ @catch:        │ halt,log,retry:N,skip │ halt    │ Error handling │    │
│  │ @fallback:     │ return-best,empty...  │ best    │ Recovery       │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  OPERATORS:                                                                 │
│  ══════════                                                                 │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │ Symbol │ Unicode │ Name      │ Quality Rule     │ Example         │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │   →    │ U+2192  │ Sequence  │ min(q₁, q₂)      │ /a→/b→/c       │    │
│  │   ||   │ -       │ Parallel  │ mean(q₁,q₂,...)  │ /a||/b||/c     │    │
│  │   ⊗    │ U+2297  │ Tensor    │ min(q₁, q₂)      │ /a⊗/b         │    │
│  │  >=>   │ -       │ Kleisli   │ converges        │ /a>=>/b>=>/c   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Checkpoint Format

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     STANDARDIZED CHECKPOINT FORMAT                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CHECKPOINT_[TYPE]_[N]:                                                     │
│  ══════════════════════                                                     │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ command: /[command_name]                                              │  │
│  │ iteration: [n]                                                        │  │
│  │                                                                       │  │
│  │ quality:                                                              │  │
│  │   correctness:  [0-1]                                                 │  │
│  │   clarity:      [0-1]                                                 │  │
│  │   completeness: [0-1]                                                 │  │
│  │   efficiency:   [0-1]                                                 │  │
│  │   aggregate:    [0-1]                                                 │  │
│  │                                                                       │  │
│  │ quality_delta: [+/- from previous]                                    │  │
│  │ trend: [RAPID_IMPROVEMENT | STEADY | PLATEAU | DEGRADING]             │  │
│  │                                                                       │  │
│  │ budget:                                                               │  │
│  │   used: [tokens]                                                      │  │
│  │   remaining: [tokens]                                                 │  │
│  │   variance: [%]                                                       │  │
│  │                                                                       │  │
│  │ status: [CONTINUE | CONVERGED | MAX_ITERATIONS | HALT]                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. CROSS-SYSTEM INTEGRATION MAP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INTEGRATION ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              ┌─────────────────┐                            │
│                              │   USER INPUT    │                            │
│                              │  /cmd @mods     │                            │
│                              └────────┬────────┘                            │
│                                       │                                      │
│                                       ▼                                      │
│                          ┌────────────────────────┐                         │
│                          │    META-SELF PARSER    │                         │
│                          │  (syntax validation)   │                         │
│                          └────────────┬───────────┘                         │
│                                       │                                      │
│           ┌───────────────────────────┼───────────────────────────┐         │
│           │                           │                           │         │
│           ▼                           ▼                           ▼         │
│  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐   │
│  │  CORE COMMANDS  │       │  ORCHESTRATION  │       │    PROMPTS      │   │
│  ├─────────────────┤       ├─────────────────┤       ├─────────────────┤   │
│  │ /meta           │       │ /meta-build     │       │ /build-prompt   │   │
│  │ /rmp            │       │ /meta-review    │       │ /select-prompt  │   │
│  │ /chain          │       │ /meta-test      │       │ /compose        │   │
│  │ /context        │       │ /meta-fix       │       │ /route          │   │
│  │ /transform      │       │ /meta-deploy    │       │ /template       │   │
│  │ /review         │       │ /meta-refactor  │       │ /list-prompts   │   │
│  │ /debug          │       │                 │       │                 │   │
│  └────────┬────────┘       └────────┬────────┘       └────────┬────────┘   │
│           │                         │                         │             │
│           └─────────────────────────┼─────────────────────────┘             │
│                                     │                                        │
│                                     ▼                                        │
│                          ┌─────────────────────┐                            │
│                          │   SKILL LAYER       │                            │
│                          ├─────────────────────┤                            │
│                          │ meta-self           │                            │
│                          │ recursive-meta-prom │                            │
│                          │ quality-enriched    │                            │
│                          │ dynamic-prompt-reg  │                            │
│                          │ categorical-prop    │                            │
│                          └─────────┬───────────┘                            │
│                                    │                                         │
│                                    ▼                                         │
│                          ┌─────────────────────┐                            │
│                          │  EXECUTION CONTEXT  │                            │
│                          │  (shared state)     │                            │
│                          │  ├─ iteration_count │                            │
│                          │  ├─ quality_history │                            │
│                          │  ├─ budget_tracking │                            │
│                          │  └─ checkpoints     │                            │
│                          └─────────┬───────────┘                            │
│                                    │                                         │
│                                    ▼                                         │
│                          ┌─────────────────────┐                            │
│                          │      OUTPUT         │                            │
│                          │  Result + Quality   │                            │
│                          │  + Checkpoint       │                            │
│                          └─────────────────────┘                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. QUICK REFERENCE CARD

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CATEGORICAL META-PROMPTING                            │
│                          QUICK REFERENCE CARD                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CATEGORICAL STRUCTURES:                                                    │
│  ════════════════════════                                                   │
│  F: Task → Prompt       Functor (strategy selection)                        │
│  M: Prompt →ⁿ Prompt    Monad (iterative refinement)                        │
│  W: History → Context   Comonad (context extraction)                        │
│  α: F ⇒ G               Natural transformation (strategy switch)            │
│                                                                              │
│  COMPOSITION OPERATORS:                                                     │
│  ══════════════════════                                                     │
│  →   Sequential         q = min(q₁, q₂)                                     │
│  ||  Parallel           q = mean(q₁, q₂, ...)                               │
│  ⊗   Tensor             q = min(q₁, q₂)                                     │
│  >=> Kleisli            q converges iteratively                             │
│                                                                              │
│  QUALITY FORMULA:                                                           │
│  ════════════════                                                           │
│  q = 0.40×correctness + 0.25×clarity + 0.20×completeness + 0.15×efficiency │
│                                                                              │
│  COMMON RECIPES:                                                            │
│  ═══════════════                                                            │
│  /meta "task"                           Simple execution                    │
│  /rmp @quality:0.85 "task"              Quality-gated iteration             │
│  /chain [/a→/b→/c] "task"               Sequential pipeline                 │
│  /chain [/a||/b||/c] "task"             Parallel execution                  │
│  /meta-build "feature"                  Full build workflow                 │
│  /meta-review "file.py"                 Multi-pass code review              │
│                                                                              │
│  TIER GUIDE:                                                                │
│  ═══════════                                                                │
│  L1-L2: Simple tasks      DIRECT strategy        600-3000 tokens            │
│  L3-L4: Medium tasks      MULTI_APPROACH         2500-6000 tokens           │
│  L5-L7: Complex tasks     AUTONOMOUS_EVOLUTION   5500-22000 tokens          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*Generated via W.extract(parallel_research_streams) from 4 concurrent Explore agents*
