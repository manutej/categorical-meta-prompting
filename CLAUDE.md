# CLAUDE.md - Categorical Meta-Prompting Unified Framework

**Version**: 2.0
**Status**: Production Ready
**Foundation**: Category Theory (F, M, W, [0,1]-Enriched)

---

## Vision

This framework implements **categorical meta-prompting** - a mathematically rigorous approach to prompt engineering where prompts compose like functions in category theory. The unified syntax ensures consistent, predictable behavior across all commands and skills.

```
Task → [F: Functor] → Prompt → [M: Monad] → Refined Prompt → [W: Comonad] → Contextualized Output
      ↑                       ↑                              ↑
   Structure-preserving    Iterative refinement         Context extraction
```

---

## Quick Start

```bash
# Simple task
/meta "implement rate limiter"

# Quality-gated iteration
/rmp @quality:0.85 "optimize algorithm"

# Multi-stage pipeline
/chain [/debug→/fix→/test] "TypeError in auth.py"

# Full unified syntax
/hekat @mode:active @tier:L5 @budget:18K [R→D→I→T] "build auth system"
```

---

## Categorical Structure

### Core Categories

| Symbol | Name | Purpose | Type Signature |
|--------|------|---------|----------------|
| **F** | Functor | Transform tasks to prompts | `Task → Prompt` |
| **M** | Monad | Iterative refinement | `Prompt →^n Prompt` |
| **W** | Comonad | Context extraction | `History → Context` |
| **[0,1]** | Enrichment | Quality tracking | `Quality → Quality` |

### Laws (Must Be Satisfied)

```
Functor:
  F(id) = id                           # Identity
  F(g ∘ f) = F(g) ∘ F(f)               # Composition

Monad:
  return >=> f = f                      # Left identity
  f >=> return = f                      # Right identity
  (f >=> g) >=> h = f >=> (g >=> h)    # Associativity

Quality:
  quality(A ⊗ B) ≤ min(q(A), q(B))     # Tensor degradation
  quality(A || B) = mean(q(A), q(B))   # Parallel aggregation
```

---

## Unified Syntax Reference

### Command Pattern

```
/<command> @modifier1:value @modifier2:value [composition] "task"
```

### Modifiers

| Modifier | Values | Default | Description |
|----------|--------|---------|-------------|
| `@mode:` | active, iterative, dry-run, spec | active | Execution mode |
| `@quality:` | 0.0-1.0 | 0.8 | Quality threshold |
| `@tier:` | L1-L7 | auto | Complexity tier |
| `@budget:` | integer, [array], auto | auto | Token budget |
| `@variance:` | percentage | 20% | Budget variance threshold |
| `@max_iterations:` | integer | 5 | Max RMP iterations |
| `@template:` | {context}+{mode}+{format} | auto | Template components |
| `@domain:` | ALGORITHM, SECURITY, API, DEBUG, TESTING | auto | Domain classification |
| `@skills:` | discover(), compose(), list | auto | Skill resolution |

### Composition Operators

| Operator | Unicode | Meaning | Quality Rule |
|----------|---------|---------|--------------|
| `→` | U+2192 | Sequence | `min(q₁, q₂)` |
| `\|\|` | - | Parallel | `mean(q₁, q₂, ...)` |
| `⊗` | U+2297 | Tensor | `min(q₁, q₂)` |
| `>=>` | - | Kleisli | improves iteratively |

---

## Available Commands

### Core Meta-Prompting

| Command | Description | Key Syntax |
|---------|-------------|------------|
| `/meta` | Categorical meta-prompting | `@mode:`, `@tier:`, `@template:` |
| `/rmp` | Recursive meta-prompting loop | `@quality:`, `@max_iterations:` |
| `/chain` | Command composition | `[/cmd1→/cmd2→/cmd3]` |

### Review & Debug

| Command | Description | Key Syntax |
|---------|-------------|------------|
| `/review` | Domain-aware code review | `@domain:` |
| `/debug` | Systematic debugging | hypothesis-driven |

### Prompt Engineering

| Command | Description | Key Syntax |
|---------|-------------|------------|
| `/build-prompt` | Template assembly | `@template:` |
| `/route` | Dynamic routing | auto-routes by domain |
| `/list-prompts` | List prompt registry | filter by domain |
| `/select-prompt` | Select best prompt | quality-based |

### Orchestration

| Command | Description | Key Syntax |
|---------|-------------|------------|
| `/meta-build` | Full build workflow | R→D→I→T pipeline |
| `/meta-refactor` | Refactoring workflow | analyze→plan→refactor |
| `/meta-review` | Multi-pass review | parallel reviewers |
| `/meta-test` | Comprehensive testing | multiple test types |
| `/meta-fix` | Bug fix workflow | debug→fix→verify |
| `/meta-deploy` | Deployment workflow | validate→stage→deploy |

---

## Available Skills

### Core Skills

| Skill | Purpose | Integration |
|-------|---------|-------------|
| `meta-self` | Master syntax reference | Self-reference protocol |
| `recursive-meta-prompting` | RMP implementation | `@mode:iterative` |
| `dynamic-prompt-registry` | Prompt lookup/composition | `@skills:`, `{prompt:}` |
| `quality-enriched-prompting` | Quality tracking | `@quality:` |

### Domain Skills

Organized in `.claude/skills/` with domain-specific knowledge for various frameworks and patterns.

---

## Execution Modes

### @mode:active (Default)

Execute immediately with auto-detection of domain, tier, and template.

```bash
/meta "implement rate limiter"
# Auto-detects: domain=API, tier=L3, template={context:expert}+{mode:cot}
```

### @mode:iterative

Enable RMP (Recursive Meta-Prompting) loop:

```bash
/rmp @mode:iterative @quality:0.85 "optimize algorithm"
# Iterate until quality ≥ 0.85 or max iterations
```

```
┌─────────────────────────────────────────┐
│ RMP Loop                                │
├─────────────────────────────────────────┤
│ 1. Generate/Refine                      │
│ 2. Evaluate Quality → [0,1]             │
│ 3. If quality ≥ @quality: CONVERGE      │
│ 4. Else: Extract improvement direction  │
│ 5. Apply >=> (Kleisli) → Next iteration │
└─────────────────────────────────────────┘
```

### @mode:dry-run

Preview execution plan without executing:

```bash
/chain @mode:dry-run [/debug→/fix→/test] "error"
# Shows: stages, operators, budget estimate, data flow
```

### @mode:spec

Generate YAML specification:

```bash
/rmp @mode:spec @quality:0.9 "complex task"
# Outputs: YAML spec with categorical structure, stages, config
```

---

## Composition Examples

### Sequential Pipeline (→)

```bash
/chain [/analyze→/design→/implement→/test] "build feature"

# Execution:
# 1. /analyze "build feature" → analysis output
# 2. /design [analysis output] → design output
# 3. /implement [design output] → implementation
# 4. /test [implementation] → final result
```

### Parallel Exploration (||)

```bash
/chain [/approach-a || /approach-b || /approach-c] "evaluate options"

# Execution:
# - All three approaches run concurrently
# - Results aggregated/compared
```

### Mixed Composition

```bash
/hekat @tier:L5 [R→(D||F)→I→T] "full-stack feature"

# Execution:
# 1. R (Research)
# 2. D||F (Design parallel with Frontend)
# 3. I (Implement)
# 4. T (Test)
```

### Quality-Gated Kleisli (>=>)

```bash
/rmp @quality:0.85 [analyze>=>design>=>implement] "build auth"

# Each stage:
# 1. Execute stage
# 2. Assess quality
# 3. If quality < 0.85: refine before continuing
# 4. Pass refined output to next stage
```

---

## Quality Assessment

### Multi-Dimensional Vector

| Dimension | Weight | Question |
|-----------|--------|----------|
| Correctness | 40% | Does it solve the problem? |
| Clarity | 25% | Is it understandable? |
| Completeness | 20% | Are edge cases handled? |
| Efficiency | 15% | Is it well-designed? |

### Aggregate Calculation

```
aggregate = 0.40×correctness + 0.25×clarity + 0.20×completeness + 0.15×efficiency
```

### Thresholds

| Score | Status | Action |
|-------|--------|--------|
| ≥0.9 | Excellent | Stop, success |
| 0.8-0.9 | Good | Stop, success |
| 0.7-0.8 | Acceptable | Continue if iterative |
| 0.6-0.7 | Poor | Refine |
| <0.6 | Failed | Abort or restructure |

---

## Checkpoint Format

All commands produce standardized checkpoints:

```yaml
CHECKPOINT_[type]_[n]:
  command: /[command]
  iteration: [n]
  quality:
    correctness: [0-1]
    clarity: [0-1]
    completeness: [0-1]
    efficiency: [0-1]
    aggregate: [0-1]
  quality_delta: [+/- from previous]
  budget:
    used: [tokens]
    remaining: [tokens]
    variance: [%]
  status: [CONTINUE | CONVERGED | MAX_ITERATIONS | HALT]
```

---

## Workflow Recipes

### Recipe 1: Quick Fix

```bash
/debug "TypeError in auth.py:42"
```

### Recipe 2: Quality-Assured Implementation

```bash
/rmp @quality:0.9 @max_iterations:5 "implement rate limiter"
```

### Recipe 3: Full Feature Pipeline

```bash
/chain [/meta→/rmp→/review] "build authentication system"
```

### Recipe 4: Parallel Code Review

```bash
/meta-review "api/auth.py"
# Runs security, performance, and style reviews in parallel
```

### Recipe 5: Complex Orchestration

```bash
/meta-build @tier:L6 "implement microservices gateway"
# Full R→D→I→T pipeline with hierarchical agents
```

### Recipe 6: Skill-Driven Command Creation

```bash
/meta-command @skills:discover(domain=API,relevance>0.8) "create endpoint testing command"
```

---

## Self-Reference Protocol

When executing any command:

1. **Parse modifiers**: Extract all `@modifier:value` pairs
2. **Apply defaults**: Fill unspecified modifiers with defaults
3. **Validate syntax**: Ensure operators and brackets match specification
4. **Reference meta-self**: Consult `skill:meta-self` for any syntax questions
5. **Execute**: Follow categorical laws at each step
6. **Checkpoint**: Output standardized checkpoint
7. **Quality assess**: Evaluate using multi-dimensional vector
8. **Decide**: CONTINUE, CONVERGE, or HALT based on rules

---

## Directory Structure

```
.claude/
├── commands/           # Slash commands
│   ├── meta.md         # @mode:, @tier:, @template:
│   ├── rmp.md          # @quality:, @max_iterations:
│   ├── chain.md        # [→, ||, >=>] operators
│   ├── review.md       # Domain-aware review
│   ├── debug.md        # Systematic debugging
│   ├── build-prompt.md # Template assembly
│   ├── route.md        # Dynamic routing
│   └── ...
│
├── skills/             # Domain knowledge
│   ├── meta-self/      # THIS REFERENCE
│   ├── recursive-meta-prompting/
│   ├── dynamic-prompt-registry/
│   ├── quality-enriched-prompting/
│   └── [domain-skills]/
│
└── settings.json       # Configuration
```

---

## Validation Checklist

Before executing, verify:

- [ ] Modifiers use `@name:value` syntax
- [ ] Operators: `→`, `||`, `⊗`, `>=>`
- [ ] Quality thresholds: [0,1]
- [ ] Tier values: L1-L7
- [ ] Mode values: active, iterative, dry-run, spec
- [ ] Composition brackets: `[...]`
- [ ] Task quoted: `"task"`

---

## Troubleshooting

### "Quality not improving"

```bash
# Check quality trend in checkpoints
# If PLATEAU: Fixed-point reached, accept result
# If DEGRADING: Restructure approach
```

### "Budget exceeded"

```bash
# Reduce tier or adjust @budget:
/meta @tier:L4 @budget:15000 "simpler approach"
```

### "Unknown modifier"

```bash
# Consult skill:meta-self for valid modifiers
# All modifiers: @mode:, @quality:, @tier:, @budget:, @variance:,
#                @max_iterations:, @template:, @domain:, @skills:
```

---

## Contributing

When adding new commands or skills:

1. Follow unified modifier syntax
2. Support at least: `@mode:`, `@quality:`
3. Output standardized checkpoints
4. Validate against categorical laws
5. Update CLAUDE.md with new additions
6. Reference `skill:meta-self` in documentation

---

## References

- `docs/UNIFIED-SYNTAX-SPECIFICATION.md` - Complete grammar
- `docs/PATTERN-EXTRACTION-COMONADIC.md` - Categorical foundations
- `docs/ARCHITECTURE-UNIFIED.md` - System architecture
- `.claude/skills/meta-self/skill.md` - Master syntax reference

---

**Framework Status**: Production Ready
**Backward Compatibility**: 100%
**Quality Score**: 0.92 (Excellent)
