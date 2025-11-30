---
description: Apply categorical meta-prompting to solve a task with strategy selection based on complexity
allowed-tools: Read, Grep, Glob, Bash(python:*), Edit, Write, TodoWrite
argument-hint: @mode:[mode] @tier:[L1-L7] @template:[components] [task-description]
---

# Categorical Meta-Prompting

You are a meta-prompt executor implementing the categorical framework:

```
F: Task → Prompt      (Functor - structure-preserving transformation)
M: Prompt →^n Prompt  (Monad - iterative refinement)
W: History → Context  (Comonad - context extraction)
```

## Unified Syntax

```
/meta @mode:active @tier:L5 @template:{context:expert}+{mode:cot} "task description"
```

### Supported Modifiers

| Modifier | Default | Description |
|----------|---------|-------------|
| `@mode:` | active | Execution mode: active, iterative, dry-run, spec |
| `@tier:` | auto | Complexity tier: L1-L7 (auto-detected if not specified) |
| `@template:` | auto | Template components: {context}+{mode}+{format} |
| `@quality:` | 0.7 | Quality threshold for iterative mode |
| `@budget:` | auto | Token budget |
| `@domain:` | auto | Force domain: ALGORITHM, SECURITY, API, DEBUG, TESTING |

---

## Task

$ARGUMENTS

---

## Mode Handling

### @mode:active (Default)

Execute with automatic domain detection and strategy selection.

### @mode:iterative

Enable RMP loop - iterate until @quality: threshold met.

### @mode:dry-run

Preview execution plan without running:

```yaml
META_PLAN:
  task: [task]
  detected_domain: [domain]
  detected_tier: [L1-L7]
  strategy: [DIRECT | MULTI_APPROACH | AUTONOMOUS_EVOLUTION]
  template: [assembled template]
  estimated_quality: [baseline]
  exit: Plan generated, no execution
```

### @mode:spec

Generate meta-prompt specification:

```yaml
name: meta-[task-hash]
type: categorical_meta_prompting
structure:
  functor: F(Task) → Prompt
  monad: M(Prompt) with @mode:iterative
  comonad: W(History) → Context
domain: [detected]
tier: [L1-L7]
template:
  context: [component]
  mode: [component]
  format: [component]
quality_threshold: [value]
```

---

## Phase 1: TASK ANALYSIS (Functor F)

Analyze the task via categorical functor F: Task → Analysis

| Dimension | Detection | Value |
|-----------|-----------|-------|
| Domain | [auto or @domain:] | [ALGORITHM / SECURITY / API / DEBUG / TESTING / GENERAL] |
| Complexity | [auto or @tier:] | [L1-L7] |
| Requires iteration? | [based on complexity] | [YES / NO] |

### Tier Classification (from Unified Syntax)

| Tier | Tokens | Pattern | Strategy |
|------|--------|---------|----------|
| L1 | 600-1200 | Single operation | DIRECT |
| L2 | 1500-3000 | A → B sequence | DIRECT |
| L3 | 2500-4500 | design → implement → test | MULTI_APPROACH |
| L4 | 3000-6000 | Parallel consensus (\|\|) | MULTI_APPROACH |
| L5 | 5500-9000 | Hierarchical with oversight | AUTONOMOUS_EVOLUTION |
| L6 | 8000-12000 | Iterative loops | AUTONOMOUS_EVOLUTION |
| L7 | 12000-22000 | Full ensemble | AUTONOMOUS_EVOLUTION |

---

## Phase 2: PROMPT SELECTION (Template Assembly)

Based on analysis, assemble template from components:

### Template Component Library

**Context Components** (@template:{context:X}):
```
{context:expert}   = "You are an expert in this domain with deep knowledge."
{context:teacher}  = "You are a patient teacher explaining step by step."
{context:reviewer} = "You are a critical reviewer looking for issues."
{context:debugger} = "You are a systematic debugger isolating problems."
```

**Mode Components** (@template:{mode:X}):
```
{mode:direct}    = "Provide a direct, concise answer."
{mode:cot}       = "Think step by step before answering."
{mode:multi}     = "Consider multiple approaches, then synthesize."
{mode:iterative} = "Attempt, assess, refine until quality threshold met."
```

**Format Components** (@template:{format:X}):
```
{format:prose}      = "Write in clear paragraphs."
{format:structured} = "Use headers, lists, and tables."
{format:code}       = "Provide working code with comments."
{format:checklist}  = "Provide actionable checklist items."
```

### Domain-Specific Prompts

#### If @domain:ALGORITHM (or detected):
```
{prompt:review_algorithm}
Review this code for algorithmic correctness:
- Time complexity (Big-O analysis)
- Space complexity
- Edge cases (empty, single, large inputs)
- Correctness for all valid inputs
```

#### If @domain:SECURITY (or detected):
```
{prompt:review_security}
Review this code for security issues:
- Input validation and sanitization
- Injection risks (SQL, command, XSS)
- Authentication/authorization flaws
- Sensitive data exposure
```

#### If @domain:DEBUG (or detected):
```
{prompt:debug}
Debug this issue systematically:
1. What is the exact error/symptom?
2. What's the minimal reproduction?
3. What are 2-3 likely root causes?
4. How to test each hypothesis?
5. What's the fix?
```

#### If @domain:TESTING (or detected):
```
{prompt:test_generate}
Generate comprehensive tests:
- Happy path tests
- Edge case tests (boundary values, empty inputs)
- Error case tests (invalid inputs, failures)
- Property-based tests if applicable
```

#### If @domain:API (or detected):
```
{prompt:review_api}
Review this API implementation:
- Endpoint design (RESTful conventions)
- Error handling (4xx, 5xx responses)
- Input validation
- Rate limiting and security
```

---

## Phase 3: STRATEGY SELECTION

### If Complexity = LOW (L1-L2) or @tier:L1-L2:
**Strategy: DIRECT**
```
Execute directly. No overhead.
Single-pass execution with focused output.
```

### If Complexity = MEDIUM (L3-L4) or @tier:L3-L4:
**Strategy: MULTI_APPROACH**
```
1. Generate 2-3 distinct approaches
2. Compare trade-offs for each
3. Synthesize best solution
```

### If Complexity = HIGH (L5-L7) or @tier:L5-L7:
**Strategy: AUTONOMOUS_EVOLUTION**
```
1. Analysis → Strategy → Implementation
2. Meta-Reflection on approach
3. Synthesis of results
4. Iterate until quality >= @quality: threshold (if @mode:iterative)
```

---

## Phase 4: EXECUTE (Monad M Application)

### Assembled Template

```
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM: {context:___}                                       │
│                                                             │
│ DOMAIN: {domain-specific-prompt}                            │
│                                                             │
│ APPROACH: {mode:___}                                        │
│                                                             │
│ TASK: $ARGUMENTS                                            │
│                                                             │
│ FORMAT: {format:___}                                        │
│                                                             │
│ QUALITY TARGET: @quality: value                             │
└─────────────────────────────────────────────────────────────┘
```

[Execute with assembled template]

---

## Phase 5: QUALITY CHECK ([0,1]-Enriched Assessment)

Assess quality as vector in product category:

| Metric | Score (0-1) | Weight | Notes |
|--------|-------------|--------|-------|
| Correctness | /1.0 | 40% | Does it solve the problem? |
| Completeness | /1.0 | 20% | Are edge cases handled? |
| Clarity | /1.0 | 25% | Is it understandable? |
| Efficiency | /1.0 | 15% | Is it well-designed? |
| **Aggregate** | /1.0 | 100% | Weighted sum |

### Convergence Decision

**If @mode:iterative AND Aggregate < @quality:**
→ Return to Phase 4 with refinement focus on lowest dimension

**If Aggregate >= @quality: OR NOT @mode:iterative:**
→ Proceed to output

---

## Phase 6: OUTPUT

```
╔══════════════════════════════════════════════════════════════╗
║ META-PROMPTING RESULT                                         ║
╠══════════════════════════════════════════════════════════════╣
║ Domain: [detected/specified domain]                           ║
║ Tier: [L1-L7]                                                 ║
║ Strategy: [DIRECT | MULTI_APPROACH | AUTONOMOUS_EVOLUTION]    ║
║ Template: {context:X}+{mode:X}+{format:X}                     ║
║ Iterations: [count if @mode:iterative]                        ║
║ Final Quality: [score]/1.0                                    ║
╚══════════════════════════════════════════════════════════════╝
```

**Solution:**
[final answer]

---

## Usage Examples

```bash
# Basic - auto-detect everything
/meta "implement rate limiter"

# Explicit domain
/meta @domain:ALGORITHM "optimize sorting function"

# Explicit tier
/meta @tier:L5 "design microservices architecture"

# With template components
/meta @template:{context:expert}+{mode:cot}+{format:code} "implement auth"

# Iterative mode with quality threshold
/meta @mode:iterative @quality:0.85 "build robust API client"

# Dry-run preview
/meta @mode:dry-run "complex multi-step task"

# Generate specification
/meta @mode:spec @tier:L6 "orchestration system"

# Full unified syntax
/meta @mode:iterative @tier:L5 @quality:0.9 @template:{context:expert}+{mode:cot} "build production system"
```

---

## Backward Compatibility

Old syntax still works:
```bash
/meta "task description"
```

New unified syntax is preferred:
```bash
/meta @mode:active @tier:L5 "task description"
```

---

## Categorical Laws Verified

1. **Functor Identity**: F(id_task) = id_prompt
2. **Functor Composition**: F(g ∘ f) = F(g) ∘ F(f)
3. **Monad Associativity**: (f >=> g) >=> h = f >=> (g >=> h)
4. **Quality Monotonicity**: quality(A ⊗ B) <= min(quality(A), quality(B))
