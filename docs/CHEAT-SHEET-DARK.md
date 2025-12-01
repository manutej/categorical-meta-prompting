# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║          CATEGORICAL META-PROMPTING · TERMINAL CHEAT SHEET · v2.2           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# Optimized for dark terminals · Print with: cat docs/CHEAT-SHEET-DARK.md

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                           THE FOUR PILLARS                                    ┃
┣━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┫
┃   FUNCTOR F     ┃    MONAD M      ┃   COMONAD W     ┃   NAT. TRANS. α        ┃
┃   ───────────   ┃   ──────────    ┃   ───────────   ┃   ──────────────       ┃
┃   Task → Prompt ┃   Prompt →ⁿ    ┃   History →     ┃   F ⇒ G                ┃
┃                 ┃   Prompt        ┃   Context       ┃                        ┃
┃   /meta         ┃   /rmp          ┃   /context      ┃   /transform           ┃
┗━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## ══════════════════════════════════════════════════════════════════════════════
##  QUICK COMMANDS
## ══════════════════════════════════════════════════════════════════════════════

```bash
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ FUNCTOR F · /meta                                                           │
# └─────────────────────────────────────────────────────────────────────────────┘

/meta "fix the login bug"                              # basic
/meta @domain:SECURITY "review API"                    # domain routing
/meta @domain:DEBUG "investigate error"                # debug focus
/meta @tier:L5 "design microservices"                  # high complexity
/meta @template:{context:expert}+{mode:cot} "impl"     # custom template

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ MONAD M · /rmp                                                              │
# └─────────────────────────────────────────────────────────────────────────────┘

/rmp @quality:0.85 "implement validation"              # iterate until 0.85
/rmp @quality:0.90 @max_iterations:5 "optimize"        # with max iterations
/rmp @mode:verbose @quality:0.80 "refine"              # show all iterations

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ COMONAD W · /context                                                        │
# └─────────────────────────────────────────────────────────────────────────────┘

/context @mode:extract @focus:recent @depth:5 "status" # recent context
/context @mode:extract @focus:file "src/auth.ts"       # file-focused
/context @mode:duplicate "why did this fail?"          # meta-observation
/context @mode:extend @transform:summarize "summary"   # context-aware

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ NAT. TRANS. α · /transform                                                  │
# └─────────────────────────────────────────────────────────────────────────────┘

/transform @from:zero-shot @to:chain-of-thought "explain"   # strategy switch
/transform @mode:compare @from:ZS @to:ToT "evaluate"        # compare
/transform @mode:analyze "debug intermittent bug"           # auto-select
```

## ══════════════════════════════════════════════════════════════════════════════
##  COMPOSITION OPERATORS
## ══════════════════════════════════════════════════════════════════════════════

```
┌──────────┬────────┬─────────────────────────┬─────────────────────────────────┐
│ OPERATOR │ SYMBOL │ MEANING                 │ QUALITY RULE                    │
├──────────┼────────┼─────────────────────────┼─────────────────────────────────┤
│ Sequence │   →    │ Output A feeds Input B  │ min(q₁, q₂)                     │
│ Parallel │  ||    │ Run concurrently        │ mean(q₁, q₂, ...)               │
│ Tensor   │   ⊗    │ Combine structures      │ min(q₁, q₂)                     │
│ Kleisli  │  >=>   │ Quality-gated chain     │ monotonically improves          │
└──────────┴────────┴─────────────────────────┴─────────────────────────────────┘
```

```bash
# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ CHAIN EXAMPLES                                                              │
# └─────────────────────────────────────────────────────────────────────────────┘

# Sequential (→)
/chain [/meta → /rmp @quality:0.85] "implement cache"

# Parallel (||)
/chain [/review @domain:SECURITY || /review @domain:PERFORMANCE] "audit"

# Kleisli refinement (>=>)
/chain [/analyze >=> /design >=> /implement] @quality:0.85 "feature"

# Multi-stage pipeline
/chain [/context → /transform @to:cot → /meta → /rmp] "full workflow"
```

## ══════════════════════════════════════════════════════════════════════════════
##  MODIFIERS REFERENCE
## ══════════════════════════════════════════════════════════════════════════════

```
┌────────────────────┬────────────────────────────────────┬───────────┬─────────┐
│ MODIFIER           │ VALUES                             │ DEFAULT   │ COMMAND │
├────────────────────┼────────────────────────────────────┼───────────┼─────────┤
│ @mode:             │ active, iterative, dry-run, spec   │ active    │ all     │
│ @quality:          │ 0.0 - 1.0                          │ 0.7-0.8   │ /rmp    │
│ @tier:             │ L1, L2, L3, L4, L5, L6, L7         │ auto      │ /meta   │
│ @domain:           │ ALGORITHM, SECURITY, API, DEBUG    │ auto      │ /meta   │
│ @template:         │ {context}+{mode}+{format}          │ auto      │ /meta   │
│ @focus:            │ recent, all, file, conversation    │ recent    │ /context│
│ @depth:            │ 1 - 10                             │ 3         │ /context│
│ @from: / @to:      │ zero-shot, few-shot, cot, tot      │ -         │ /transf │
│ @max_iterations:   │ 1 - 10                             │ 5         │ /rmp    │
└────────────────────┴────────────────────────────────────┴───────────┴─────────┘
```

## ══════════════════════════════════════════════════════════════════════════════
##  TIER CLASSIFICATION (L1-L7)
## ══════════════════════════════════════════════════════════════════════════════

```
┌──────┬────────────┬──────────────────────────────┬────────────────────────────┐
│ TIER │ TOKENS     │ PATTERN                      │ STRATEGY                   │
├──────┼────────────┼──────────────────────────────┼────────────────────────────┤
│  L1  │  600-1200  │ Single operation             │ DIRECT                     │
│  L2  │ 1500-3000  │ A → B sequence               │ DIRECT                     │
│  L3  │ 2500-4500  │ design → implement → test    │ MULTI_APPROACH             │
│  L4  │ 3000-6000  │ Parallel consensus (||)      │ MULTI_APPROACH             │
│  L5  │ 5500-9000  │ Hierarchical with oversight  │ AUTONOMOUS_EVOLUTION       │
│  L6  │ 8000-12000 │ Iterative loops              │ AUTONOMOUS_EVOLUTION       │
│  L7  │ 12000-22K  │ Full ensemble                │ AUTONOMOUS_EVOLUTION       │
└──────┴────────────┴──────────────────────────────┴────────────────────────────┘
```

## ══════════════════════════════════════════════════════════════════════════════
##  QUALITY ASSESSMENT
## ══════════════════════════════════════════════════════════════════════════════

```
┌─────────────────┬────────┬─────────────────────────────────────────────────────┐
│ DIMENSION       │ WEIGHT │ QUESTION                                            │
├─────────────────┼────────┼─────────────────────────────────────────────────────┤
│ Correctness     │  40%   │ Does it solve the problem?                          │
│ Clarity         │  25%   │ Is it understandable?                               │
│ Completeness    │  20%   │ Are edge cases handled?                             │
│ Efficiency      │  15%   │ Is it well-designed?                                │
├─────────────────┴────────┴─────────────────────────────────────────────────────┤
│ FORMULA: q = 0.40×correctness + 0.25×clarity + 0.20×completeness + 0.15×eff   │
└────────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬─────────────────────────────────────────────────────────────────┐
│ THRESHOLD    │ ACTION                                                          │
├──────────────┼─────────────────────────────────────────────────────────────────┤
│  ≥ 0.90      │ ✓ EXCELLENT · Stop, success                                     │
│  0.80-0.90   │ ✓ GOOD · Stop, success                                          │
│  0.70-0.80   │ ◐ OK · Continue if iterative                                    │
│  0.60-0.70   │ ✗ POOR · Refine                                                 │
│  < 0.60      │ ✗ FAILED · Abort or restructure                                 │
└──────────────┴─────────────────────────────────────────────────────────────────┘
```

## ══════════════════════════════════════════════════════════════════════════════
##  COMMON WORKFLOWS
## ══════════════════════════════════════════════════════════════════════════════

```bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ BUG FIX PIPELINE · W → F → F                                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
/chain [/context @mode:extract → /debug → /meta @domain:DEBUG] "TypeError"

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ CODE REVIEW · F || F || F || F                                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
/meta-review "src/auth/login.ts"

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ FEATURE IMPLEMENTATION · W → α → F → M                                    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
/chain [/context → /transform @mode:analyze → /meta @tier:L4 → /rmp @quality:0.88] "OAuth2"

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ GENERATE + REFINE · F → M                                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
/chain [/meta @tier:L3 → /rmp @quality:0.85] "implement LRU cache"

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ CONTEXT-AWARE · W → F                                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
/chain [/context @mode:extract → /meta] "follow project patterns"

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ STRATEGY + REFINE · α → M                                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
/chain [/transform @to:chain-of-thought → /rmp @quality:0.85] "design schema"
```

## ══════════════════════════════════════════════════════════════════════════════
##  TEMPLATE COMPONENTS
## ══════════════════════════════════════════════════════════════════════════════

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT                                                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ {context:expert}   │ "You are an expert with deep knowledge"                    │
│ {context:teacher}  │ "You are a patient teacher explaining step by step"        │
│ {context:reviewer} │ "You are a critical reviewer looking for issues"           │
│ {context:debugger} │ "You are a systematic debugger isolating problems"         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ MODE                                                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│ {mode:direct}      │ "Provide a direct, concise answer"                         │
│ {mode:cot}         │ "Think step by step before answering"                      │
│ {mode:multi}       │ "Consider multiple approaches, then synthesize"            │
│ {mode:iterative}   │ "Attempt, assess, refine until quality met"                │
├─────────────────────────────────────────────────────────────────────────────────┤
│ FORMAT                                                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ {format:prose}     │ "Write in clear paragraphs"                                │
│ {format:structured}│ "Use headers, lists, and tables"                           │
│ {format:code}      │ "Provide working code with comments"                       │
│ {format:checklist} │ "Provide actionable checklist items"                       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## ══════════════════════════════════════════════════════════════════════════════
##  STRATEGY REGISTRY
## ══════════════════════════════════════════════════════════════════════════════

```
┌───────────────────┬──────────┬────────────┬────────────────────────────────────┐
│ STRATEGY          │ QUALITY  │ COST       │ BEST FOR                           │
├───────────────────┼──────────┼────────────┼────────────────────────────────────┤
│ zero-shot         │   0.65   │ Low        │ Simple queries                     │
│ few-shot          │   0.78   │ Medium     │ Pattern matching                   │
│ chain-of-thought  │   0.85   │ Med-High   │ Reasoning tasks                    │
│ tree-of-thought   │   0.88   │ High       │ Search/exploration                 │
│ self-consistency  │   0.82   │ High       │ Robustness                         │
│ meta-prompting    │   0.90   │ Variable   │ Adaptive tasks                     │
└───────────────────┴──────────┴────────────┴────────────────────────────────────┘
```

## ══════════════════════════════════════════════════════════════════════════════
##  QUICK RECIPES (ONE-LINERS)
## ══════════════════════════════════════════════════════════════════════════════

```bash
# Quick fix
/meta "fix bug"

# Quality implementation
/rmp @quality:0.85 "implement feature"

# Context-aware
/chain [/context → /meta] "task"

# Strategy upgrade
/transform @to:chain-of-thought "complex problem"

# Full pipeline
/chain [/context → /transform → /meta → /rmp] "feature"

# Code review
/meta-review "file.ts"

# Debug issue
/chain [/context → /debug → /meta @domain:DEBUG] "error"

# Compare approaches
/chain [/approach-a || /approach-b] "problem"

# Dry-run preview
/chain @mode:dry-run [/meta → /rmp] "task"
```

## ══════════════════════════════════════════════════════════════════════════════
##  CATEGORICAL LAWS
## ══════════════════════════════════════════════════════════════════════════════

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FUNCTOR                                                                         │
│   F(id) = id                              Identity                              │
│   F(g ∘ f) = F(g) ∘ F(f)                  Composition                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│ MONAD                                                                           │
│   return >=> f = f                        Left identity                         │
│   f >=> return = f                        Right identity                        │
│   (f >=> g) >=> h = f >=> (g >=> h)       Associativity                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ COMONAD                                                                         │
│   extract ∘ duplicate = id                Left identity                         │
│   fmap extract ∘ duplicate = id           Right identity                        │
│   duplicate ∘ duplicate = fmap dup ∘ dup  Associativity                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ NATURAL TRANSFORMATION                                                          │
│   α_B ∘ F(f) = G(f) ∘ α_A                 Naturality condition                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## ══════════════════════════════════════════════════════════════════════════════
##  TROUBLESHOOTING
## ══════════════════════════════════════════════════════════════════════════════

```
┌─────────────────────────────┬───────────────────────────────────────────────────┐
│ ISSUE                       │ SOLUTION                                          │
├─────────────────────────────┼───────────────────────────────────────────────────┤
│ Quality not improving       │ Fixed-point reached; accept or restructure        │
│ Budget exceeded             │ Reduce tier: /meta @tier:L4 @budget:15000         │
│ Unknown modifier            │ Check modifiers table above                       │
│ Not converging              │ Lower threshold or increase @max_iterations       │
│ Wrong strategy              │ Use /transform @mode:analyze                      │
│ Context too broad           │ Use @focus:file or reduce @depth                  │
│ Parallel not aggregating    │ Check || syntax, ensure commands compatible       │
└─────────────────────────────┴───────────────────────────────────────────────────┘
```

## ══════════════════════════════════════════════════════════════════════════════
##  CHECKPOINT FORMAT
## ══════════════════════════════════════════════════════════════════════════════

```yaml
CHECKPOINT_[TYPE]_[N]:
  command: /[command]
  iteration: [n]
  quality:
    correctness: [0-1]
    clarity: [0-1]
    completeness: [0-1]
    efficiency: [0-1]
    aggregate: [0-1]
  quality_delta: [+/- from previous]
  status: [CONTINUE | CONVERGED | MAX_ITERATIONS | HALT]
```

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  v2.2 · 10/10 Tests Passed · 85% Coverage · Production Ready                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
```
