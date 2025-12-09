# Categorical Meta-Prompting: Complete Guide

**Version**: 2.1
**Status**: Production Ready
**Date**: 2025-12-08
**Foundation**: Category Theory (F, M, W, [0,1]-Enriched)

---

## Table of Contents

1. [Visual Cheatsheet](#visual-cheatsheet)
2. [Interactive Examples](#interactive-examples)
3. [Deep Dive: Categorical Foundations](#deep-dive-categorical-foundations)
4. [Advanced Techniques](#advanced-techniques)
5. [Reference](#reference)

---

# Visual Cheatsheet

## Core Concept

```
Task ──[F: Functor]──> Prompt ──[M: Monad]──> Refined ──[W: Comonad]──> Output
        Structure        │        Iteration      │        Context
        Preserving       │        & Refinement   │        Extraction
                        │                        │
                 ┌──────▼────────┐      ┌───────▼────────┐
                 │ Quality [0,1] │      │ Token Budget   │
                 │ Enrichment    │      │ Tracking       │
                 └───────────────┘      └────────────────┘
```

## Unified Syntax

```bash
/<command> @modifier:value [composition] "task description"
─────────  ───────────────  ─────────────  ──────────────────
    │             │                 │              │
Command      Modifiers        Operators        Task
```

**Example:**
```bash
/meta @mode:active @tier:L5 [R→D→I→T] "build auth system"
```

## Modifiers Reference

| Modifier | Values | Default | Description |
|----------|--------|---------|-------------|
| `@mode:` | active \| iterative \| dry-run \| spec | active | Execution mode |
| `@quality:` | 0.0 - 1.0 | 0.8 | Quality threshold |
| `@tier:` | L1-L7 | auto | Complexity tier |
| `@budget:` | integer \| [array] \| auto | auto | Token budget |
| `@max_iterations:` | 1-10 | 5 | Max RMP iterations |
| `@domain:` | ALGORITHM \| SECURITY \| API \| DEBUG \| TESTING | auto | Domain classification |
| `@template:` | {context}+{mode}+{format} | auto | Template components |
| `@skills:` | discover() \| compose() \| list | auto | Skill resolution |

### Mode Details

**@mode:active** (Default)
- Execute immediately
- Auto-detection of domain, tier, template
- Best for: Quick tasks, standard workflows

**@mode:iterative**
- Enable RMP (Recursive Meta-Prompting) loop
- Refine until quality threshold met
- Best for: Complex tasks requiring refinement

**@mode:dry-run**
- Preview execution plan without executing
- Shows stages, operators, budget
- Best for: Planning, validation

**@mode:spec**
- Generate YAML specification
- Complete categorical structure
- Best for: Documentation, reproducibility

### Tier Levels

| Tier | Complexity | Example Use Cases |
|------|------------|-------------------|
| L1-L2 | Simple | Bug fixes, code formatting, quick searches |
| L3-L4 | Moderate | Feature implementation, refactoring |
| L5-L6 | Advanced | System design, multi-component features |
| L7 | Expert | Research-grade, novel architectures |

## Composition Operators

| Operator | Unicode | Meaning | Quality Rule | Example |
|----------|---------|---------|--------------|---------|
| `→` | U+2192 | Sequential | `min(q₁, q₂)` | `[A→B→C]` |
| `\|\|` | - | Parallel | `mean(q₁, q₂, ...)` | `[A\|\|B\|\|C]` |
| `⊗` | U+2297 | Tensor | `min(q₁, q₂)` | `[A⊗B]` |
| `>=>` | - | Kleisli | improves iteratively | `[A>=>B>=>C]` |

### Operator Details

**Sequential (→)**
```bash
/chain [/analyze→/design→/implement→/test] "build feature"

Execution:
1. /analyze "build feature" → analysis output
2. /design [analysis output] → design output
3. /implement [design output] → implementation
4. /test [implementation] → final result

Quality: min(q_analyze, q_design, q_implement, q_test)
```

**Parallel (||)**
```bash
/chain [/approach-a || /approach-b || /approach-c] "evaluate options"

Execution:
- All three approaches run concurrently
- Results aggregated/compared
- Quality: mean(q_a, q_b, q_c)
```

**Mixed Composition**
```bash
/meta @tier:L5 [R→(D||F)→I→T] "full-stack feature"

Execution:
1. R (Research) → research output
2. (D||F) (Design parallel with Frontend) → both outputs
3. I (Implement) → implementation
4. T (Test) → final result

Quality: min(q_R, mean(q_D, q_F), q_I, q_T)
```

**Kleisli (>=>)**
```bash
/rmp @quality:0.85 [analyze>=>design>=>implement] "build auth"

Each stage:
1. Execute stage
2. Assess quality
3. If quality < 0.85: refine before continuing
4. Pass refined output to next stage

Quality: Improves iteratively until threshold met
```

## Core Commands

### /meta - Categorical Meta-Prompting

Auto-detects domain, tier, and template for optimal prompt generation.

```bash
# Simple usage
/meta "implement rate limiter"

# With modifiers
/meta @tier:L5 @domain:API "build REST API"

# With composition
/meta @mode:active [R→D→I] "authentication system"
```

**When to use:**
- Standard tasks with clear requirements
- Need auto-detection of complexity
- Want optimal prompt construction

### /rmp - Recursive Meta-Prompting

Quality-gated iteration loop for refinement.

```bash
# Basic quality threshold
/rmp @quality:0.85 "optimize algorithm"

# Custom iterations
/rmp @max_iterations:7 @quality:0.9 "refactor codebase"

# With composition
/rmp @quality:0.85 [analyze>=>design>=>implement] "feature"
```

**When to use:**
- Complex tasks requiring multiple refinements
- Quality is critical
- Willing to iterate for better results

### /chain - Command Composition

Compose multiple commands with operators.

```bash
# Sequential pipeline
/chain [/debug→/fix→/test] "TypeError in auth.py"

# Parallel exploration
/chain [/approach-a || /approach-b || /approach-c] "compare solutions"

# Mixed composition
/chain [/analyze→(/design||/prototype)→/evaluate] "new feature"
```

**When to use:**
- Multi-step workflows
- Need to combine different approaches
- Want explicit control over execution order

### /review - Domain-Aware Review

Intelligent code review with domain classification.

```bash
# Auto-detect domain
/review "api/auth.py"

# Explicit domain
/review @domain:SECURITY "auth.py"

# Multiple files
/review @domain:API "api/*.py"
```

### /debug - Systematic Debugging

Hypothesis-driven debugging workflow.

```bash
# Basic debugging
/debug "connection timeout in API"

# With context
/debug "TypeError in auth.py:42"
```

## Orchestration Commands

Pre-built workflows for common development tasks.

### /meta-build
**Full build workflow:** Research → Design → Implement → Test

```bash
/meta-build "implement authentication system"
/meta-build @tier:L6 "microservices gateway"
```

### /meta-refactor
**Refactoring workflow:** Analyze → Plan → Refactor → Verify

```bash
/meta-refactor "extract payment logic to service"
```

### /meta-review
**Multi-pass parallel review:** Security, Performance, Style

```bash
/meta-review "api/auth.py"
```

### /meta-test
**Comprehensive testing:** Unit, Integration, E2E

```bash
/meta-test "authentication module"
```

### /meta-fix
**Bug fix workflow:** Debug → Analyze → Fix → Verify

```bash
/meta-fix "memory leak in WebSocket handler"
```

### /meta-deploy
**Deployment workflow:** Validate → Stage → Deploy → Monitor

```bash
/meta-deploy @environment:production "v2.0.0"
```

## Quality Assessment

### Multi-Dimensional Vector

Every output is assessed across four dimensions:

| Dimension | Weight | Question |
|-----------|--------|----------|
| **Correctness** | 40% | Does it solve the problem? |
| **Clarity** | 25% | Is it understandable? |
| **Completeness** | 20% | Are edge cases handled? |
| **Efficiency** | 15% | Is it well-designed? |

### Calculation

```
aggregate = 0.40 × correctness +
            0.25 × clarity +
            0.20 × completeness +
            0.15 × efficiency
```

### Thresholds

| Score | Status | Action |
|-------|--------|--------|
| ≥0.9 | Excellent | ✓ Stop, success |
| 0.8-0.9 | Good | ✓ Stop, success |
| 0.7-0.8 | Acceptable | → Continue if iterative |
| 0.6-0.7 | Poor | ⟳ Refine |
| <0.6 | Failed | ✗ Abort or restructure |

## RMP Iteration Loop

```
┌─────────────────────────────────────────────────────────────┐
│ START: Initial prompt                                       │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│ 1. Generate/Refine Output                                   │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│ 2. Evaluate Quality → [0,1]                                 │
│    • Correctness (40%)                                      │
│    • Clarity (25%)                                          │
│    • Completeness (20%)                                     │
│    • Efficiency (15%)                                       │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│ 3. Check Convergence                                        │
│    quality ≥ @quality? OR max_iterations reached?           │
└────┬──────────────────────────────────────────────┬─────────┘
     │ YES                                           │ NO
     │                                               │
┌────▼──────────────────┐              ┌────────────▼─────────┐
│ CONVERGE: Success ✓   │              │ 4. Extract improvement│
│ Output final result   │              │    direction from     │
└───────────────────────┘              │    quality assessment │
                                       └────────────┬──────────┘
                                                    │
                                       ┌────────────▼──────────┐
                                       │ 5. Apply >=> (Kleisli)│
                                       │    Refine prompt      │
                                       └────────────┬──────────┘
                                                    │
                                       ┌────────────▼──────────┐
                                       │ Next Iteration        │
                                       │ iteration = n + 1     │
                                       └────────────┬──────────┘
                                                    │
                                        ────────────┘
                                       (Loop back to step 1)
```

## Checkpoint Format

Every command outputs standardized checkpoints for tracking:

```yaml
CHECKPOINT_RMP_3:
  command: /rmp
  iteration: 3
  quality:
    correctness: 0.90
    clarity: 0.85
    completeness: 0.88
    efficiency: 0.82
    aggregate: 0.87
  quality_delta: +0.08
  budget:
    used: 12450
    remaining: 5550
    variance: 15%
  status: CONTINUE
```

## Quick Recipes

### 1️⃣ Quick Fix
```bash
/debug "TypeError in auth.py:42"
```

### 2️⃣ Quality-Assured Implementation
```bash
/rmp @quality:0.9 @max_iterations:5 "implement rate limiter"
```

### 3️⃣ Full Feature Pipeline
```bash
/chain [/meta→/rmp→/review] "build authentication system"
```

### 4️⃣ Parallel Exploration
```bash
/chain [/approach-a || /approach-b || /approach-c] "compare solutions"
```

### 5️⃣ Complex Orchestration
```bash
/meta-build @tier:L6 [R→(D||F)→I→T] "full-stack feature"
```

### 6️⃣ Preview Before Execution
```bash
/chain @mode:dry-run [/analyze→/design→/implement] "new feature"
```

## Categorical Laws

These laws **must be satisfied** by all operations:

### Functor Laws
```
F(id) = id                    # Identity preservation
F(g ∘ f) = F(g) ∘ F(f)        # Composition preservation
```

### Monad Laws
```
return >=> f = f              # Left identity
f >=> return = f              # Right identity
(f >=> g) >=> h = f >=> (g >=> h)   # Associativity
```

### Quality Laws
```
quality(A ⊗ B) ≤ min(q(A), q(B))    # Tensor degradation
quality(A || B) = mean(q(A), q(B))  # Parallel aggregation
quality(A → B) = min(q(A), q(B))    # Sequential minimum
```

## Troubleshooting

### Quality not improving

**Check quality trend in checkpoints:**
- **PLATEAU**: Fixed-point reached, accept result
- **DEGRADING**: Restructure approach

```bash
# Reduce complexity or adjust strategy
/meta @tier:L4 "simplified approach"
```

### Budget exceeded

**Reduce tier or adjust budget:**

```bash
/meta @tier:L4 @budget:15000 "simpler approach"
```

### Unknown modifier

**Valid modifiers:**
- `@mode:` active, iterative, dry-run, spec
- `@quality:` 0.0-1.0
- `@tier:` L1-L7
- `@budget:` integer, [array], auto
- `@variance:` percentage
- `@max_iterations:` 1-10
- `@template:` {context}+{mode}+{format}
- `@domain:` ALGORITHM, SECURITY, API, DEBUG, TESTING
- `@skills:` discover(), compose(), list

---

# Interactive Examples

## Example 1: Building an Authentication System

**Scenario:** You need to implement a complete authentication system with JWT tokens, refresh tokens, and password hashing.

### Approach 1: Simple /meta
```bash
/meta "implement authentication system with JWT"
```

**What happens:**
- Auto-detects `@tier:L5` (complex multi-component feature)
- Auto-detects `@domain:SECURITY` (security-critical)
- Generates comprehensive prompt with security best practices
- Single-pass execution

**Result:**
- Complete implementation
- Quality: ~0.75-0.85 (good, but may miss edge cases)

### Approach 2: Quality-Gated /rmp
```bash
/rmp @quality:0.9 @max_iterations:5 "implement authentication system with JWT"
```

**What happens:**
```
Iteration 1: Initial implementation
  ├─ Correctness: 0.80
  ├─ Clarity: 0.75
  ├─ Completeness: 0.70  ← Missing edge cases
  ├─ Efficiency: 0.80
  └─ Aggregate: 0.77 < 0.90 → CONTINUE

Iteration 2: Refine to add edge cases
  ├─ Correctness: 0.85
  ├─ Clarity: 0.82
  ├─ Completeness: 0.85  ← Improved!
  ├─ Efficiency: 0.82
  └─ Aggregate: 0.84 < 0.90 → CONTINUE

Iteration 3: Polish error handling and docs
  ├─ Correctness: 0.92
  ├─ Clarity: 0.90
  ├─ Completeness: 0.90
  ├─ Efficiency: 0.85
  └─ Aggregate: 0.90 ≥ 0.90 → CONVERGE ✓
```

**Result:**
- Production-ready implementation
- Comprehensive edge case handling
- Clear documentation
- Quality: 0.90 (excellent)

### Approach 3: Full /meta-build Workflow
```bash
/meta-build @tier:L6 "authentication system with JWT, refresh tokens, password hashing"
```

**What happens:**
```
[R] Research Phase
  ├─ Survey JWT best practices
  ├─ Review OWASP authentication guidelines
  ├─ Analyze refresh token strategies
  └─ Output: Research document → quality: 0.88

[D] Design Phase
  ├─ Architecture: Token service, Auth middleware
  ├─ Database schema: users, refresh_tokens tables
  ├─ Security: bcrypt hashing, token rotation
  └─ Output: Design document → quality: 0.90

[I] Implementation Phase
  ├─ Token service (generate, verify, refresh)
  ├─ Auth middleware (protect routes)
  ├─ Password hashing utilities
  ├─ Error handling
  └─ Output: Implementation → quality: 0.85

[T] Testing Phase
  ├─ Unit tests: Token generation/verification
  ├─ Integration tests: Auth flows
  ├─ Security tests: Token expiry, refresh rotation
  └─ Output: Test suite → quality: 0.92

Overall Quality: min(0.88, 0.90, 0.85, 0.92) = 0.85
```

**Result:**
- Complete R→D→I→T pipeline
- Documented at every stage
- Tested and production-ready
- Quality: 0.85 (excellent, with full traceability)

## Example 2: Debugging a Complex Issue

**Scenario:** Production API experiencing intermittent 500 errors, no clear pattern in logs.

### Approach 1: Direct /debug
```bash
/debug "intermittent 500 errors in API, no pattern in logs"
```

**What happens:**
```
Systematic Debugging:
1. Hypothesis Generation
   H1: Database connection timeout
   H2: Race condition in concurrent requests
   H3: Memory leak causing OOM

2. Evidence Collection
   ├─ Check connection pool metrics
   ├─ Analyze request timing patterns
   └─ Review memory usage over time

3. Hypothesis Testing
   H1: Connection pool shows saturation during errors ← Evidence!
   H2: No correlation with concurrent requests
   H3: Memory stable

4. Root Cause
   Database connection pool too small for load spikes

5. Fix
   Increase pool size + add connection retry logic
```

### Approach 2: Full /meta-fix Workflow
```bash
/meta-fix "intermittent 500 errors in production API"
```

**What happens:**
```
[Debug] Phase
  ├─ Generate hypotheses (H1: connections, H2: race, H3: memory)
  ├─ Collect evidence (metrics, logs, timing)
  ├─ Test hypotheses → H1 confirmed
  └─ Output: Root cause analysis → quality: 0.90

[Analyze] Phase
  ├─ Impact analysis: 15% of requests failing during spikes
  ├─ Risk assessment: Connection pool increase safe
  ├─ Solution design: Pool size 20→50, retry logic
  └─ Output: Fix plan → quality: 0.88

[Fix] Phase
  ├─ Update connection pool configuration
  ├─ Implement retry logic with exponential backoff
  ├─ Add connection pool metrics monitoring
  └─ Output: Implementation → quality: 0.85

[Verify] Phase
  ├─ Unit tests: Retry logic behavior
  ├─ Load tests: Pool handles spikes
  ├─ Monitor production: 0% errors after deploy
  └─ Output: Verification report → quality: 0.95

Overall Quality: min(0.90, 0.88, 0.85, 0.95) = 0.85
```

**Result:**
- Root cause identified
- Fix implemented and tested
- Production verified
- Documented for future reference

## Example 3: Parallel Approach Evaluation

**Scenario:** Need to choose the best caching strategy for a high-traffic API.

### Using Parallel Composition
```bash
/chain [/redis-approach || /in-memory-approach || /cdn-approach] "evaluate caching strategies for API"
```

**What happens:**
```
Parallel Execution:

[Branch 1: Redis]
├─ Architecture: Centralized Redis cluster
├─ Pros: Shared across instances, persistent
├─ Cons: Network latency, single point of failure
├─ Cost: $200/month (managed Redis)
├─ Complexity: Medium
└─ Quality: 0.82

[Branch 2: In-Memory]
├─ Architecture: Local LRU cache per instance
├─ Pros: Zero latency, simple
├─ Cons: Cache warming on deploy, memory overhead
├─ Cost: $0 (included in app servers)
├─ Complexity: Low
└─ Quality: 0.75

[Branch 3: CDN]
├─ Architecture: CloudFront edge caching
├─ Pros: Global distribution, DDoS protection
├─ Cons: Cache invalidation complexity
├─ Cost: $50/month (CloudFront)
├─ Complexity: Medium-High
└─ Quality: 0.85

Aggregation (mean):
Quality: (0.82 + 0.75 + 0.85) / 3 = 0.81

Recommendation:
CDN approach (highest quality 0.85) for public endpoints,
Redis for session/user data (0.82),
In-memory for computed results (0.75)
```

**Result:**
- All three approaches evaluated in parallel
- Comparative analysis provided
- Hybrid recommendation based on use case
- Quality: 0.81 (good overall, excellent best option)

## Example 4: Quality-Gated Pipeline

**Scenario:** Implement a payment processing feature where every stage must meet quality standards.

### Using Kleisli Composition
```bash
/rmp @quality:0.85 [analyze>=>design>=>implement>=>test] "payment processing with Stripe"
```

**What happens:**
```
[Analyze] Stage
  Initial:
    ├─ Requirements: Stripe integration, webhooks, refunds
    ├─ Security: PCI compliance, no card storage
    ├─ Edge cases: Failed payments, duplicate charges
    └─ Quality: 0.78 < 0.85 → REFINE

  Refined:
    ├─ Added: Idempotency keys, webhook verification
    ├─ Added: Comprehensive error scenarios
    └─ Quality: 0.87 ≥ 0.85 → PASS to design

[Design] Stage (receives refined analysis)
  Initial:
    ├─ Architecture: Payment service, webhook handler
    ├─ Database: payments, transactions tables
    ├─ API: /charge, /refund, /webhook endpoints
    └─ Quality: 0.82 < 0.85 → REFINE

  Refined:
    ├─ Added: Retry queue for failed webhooks
    ├─ Added: Audit logging for all transactions
    ├─ Added: State machine for payment status
    └─ Quality: 0.88 ≥ 0.85 → PASS to implement

[Implement] Stage (receives refined design)
  Initial:
    ├─ Payment service with Stripe SDK
    ├─ Webhook endpoint with signature verification
    ├─ Database models and migrations
    └─ Quality: 0.80 < 0.85 → REFINE

  Refined:
    ├─ Added: Comprehensive error handling
    ├─ Added: Logging and monitoring
    ├─ Added: Graceful degradation
    └─ Quality: 0.86 ≥ 0.85 → PASS to test

[Test] Stage (receives refined implementation)
  Initial:
    ├─ Unit tests: Payment creation, refunds
    ├─ Integration tests: Stripe API mocking
    └─ Quality: 0.83 < 0.85 → REFINE

  Refined:
    ├─ Added: Webhook delivery tests
    ├─ Added: Idempotency tests
    ├─ Added: Error scenario tests
    └─ Quality: 0.90 ≥ 0.85 → CONVERGE ✓

Overall Quality: min(0.87, 0.88, 0.86, 0.90) = 0.86
Total Iterations: 7 (4 stages × avg 1.75 iterations/stage)
```

**Result:**
- Every stage refined to meet quality threshold
- High confidence in production readiness
- Quality: 0.86 (excellent, battle-tested)
- Trade-off: More iterations (7 vs typical 3-4), but higher quality

## Example 5: Dry-Run Mode for Planning

**Scenario:** Want to preview execution before committing to a large refactoring.

### Using @mode:dry-run
```bash
/chain @mode:dry-run [/analyze→/plan→/refactor→/verify] "extract payment logic to microservice"
```

**What happens:**
```yaml
DRY RUN PLAN
─────────────────────────────────────────────────────────

Composition: [/analyze→/plan→/refactor→/verify]
Operators: → (sequential)
Quality Rule: min(q_analyze, q_plan, q_refactor, q_verify)

Stages:
  1. /analyze "extract payment logic to microservice"
     ├─ Domain: ARCHITECTURE
     ├─ Tier: L5 (multi-component, service boundary change)
     ├─ Estimated tokens: 4000
     ├─ Outputs: Current architecture analysis, dependencies
     └─ Expected quality: 0.80-0.85

  2. /plan [analysis output]
     ├─ Domain: ARCHITECTURE
     ├─ Tier: L5
     ├─ Estimated tokens: 4500
     ├─ Outputs: Migration plan, API contracts, data flow
     └─ Expected quality: 0.82-0.88

  3. /refactor [plan output]
     ├─ Domain: ARCHITECTURE
     ├─ Tier: L5
     ├─ Estimated tokens: 6000
     ├─ Outputs: New service code, updated monolith, migrations
     └─ Expected quality: 0.75-0.85

  4. /verify [refactor output]
     ├─ Domain: TESTING
     ├─ Tier: L4
     ├─ Estimated tokens: 3500
     ├─ Outputs: Test suite, verification report
     └─ Expected quality: 0.85-0.92

Budget Estimate:
  ├─ Total: 18,000 tokens
  ├─ Breakdown: [4000, 4500, 6000, 3500]
  └─ Quality: min(0.80, 0.82, 0.75, 0.85) ≈ 0.75-0.80

Data Flow:
  analyze → {dependencies, current_state}
         ↓
  plan → {migration_steps, api_contracts}
         ↓
  refactor → {new_service, updated_monolith}
         ↓
  verify → {test_results, verification}

Execute? (y/n)
```

**Result:**
- Complete preview without execution
- Budget and quality estimates
- Opportunity to adjust before running
- Can modify to `/chain @mode:active @tier:L6` if estimates look good

## Example 6: Spec Mode for Documentation

**Scenario:** Generate a reproducible specification for a complex workflow.

### Using @mode:spec
```bash
/rmp @mode:spec @quality:0.9 @max_iterations:5 "implement multi-tenant SaaS authentication"
```

**What happens:**
```yaml
# Generated Specification
# Command: /rmp
# Generated: 2025-12-08T14:30:00Z

meta:
  command: /rmp
  mode: spec
  task: "implement multi-tenant SaaS authentication"

config:
  quality:
    threshold: 0.9
    dimensions:
      correctness: 0.40
      clarity: 0.25
      completeness: 0.20
      efficiency: 0.15
  iterations:
    max: 5
  budget:
    total: auto
    variance_threshold: 0.20

categorical_structure:
  functor: Task → Prompt
    mapping: "multi-tenant SaaS auth" → {
      domain: SECURITY,
      tier: L6,
      template: {
        context: expert_saas_security,
        mode: chain_of_thought,
        format: implementation_with_tests
      }
    }

  monad: Prompt → Refined_Prompt
    kleisli_chain:
      - analyze_requirements
      - design_schema
      - implement_auth
      - test_multi_tenancy
    bind_operator: >=>

  comonad: History → Context
    extract:
      - previous_iteration_quality
      - improvement_directions
      - converged_patterns

  enrichment: [0, 1] Quality Metric
    aggregate: weighted_sum
    weights: [0.40, 0.25, 0.20, 0.15]

execution_plan:
  stage_1:
    name: analyze_requirements
    domain: SECURITY
    tier: L6
    input: "implement multi-tenant SaaS authentication"
    expected_output:
      - tenant isolation requirements
      - authentication schemes (JWT, OAuth)
      - authorization model (RBAC, tenant-scoped)
    quality_threshold: 0.85

  stage_2:
    name: design_schema
    domain: ARCHITECTURE
    tier: L6
    input: [stage_1.output]
    expected_output:
      - database schema (tenants, users, roles)
      - API design (tenant resolution, auth endpoints)
      - security model (encryption, isolation)
    quality_threshold: 0.88

  stage_3:
    name: implement_auth
    domain: SECURITY
    tier: L6
    input: [stage_2.output]
    expected_output:
      - tenant middleware
      - JWT service with tenant claims
      - permission checking
    quality_threshold: 0.85

  stage_4:
    name: test_multi_tenancy
    domain: TESTING
    tier: L5
    input: [stage_3.output]
    expected_output:
      - unit tests (isolation, auth)
      - integration tests (cross-tenant access)
      - security tests (privilege escalation)
    quality_threshold: 0.90

convergence:
  method: rmp_loop
  condition: quality ≥ 0.9 OR iterations ≥ 5
  fallback:
    if_plateau: accept_best_iteration
    if_degrading: abort_and_restructure

checkpoints:
  format: yaml
  frequency: per_iteration
  fields:
    - iteration
    - quality_vector
    - quality_aggregate
    - quality_delta
    - budget_used
    - budget_remaining
    - status

output:
  format: implementation_with_docs
  includes:
    - source_code
    - database_migrations
    - test_suite
    - deployment_guide
    - security_audit_checklist
```

**Result:**
- Complete YAML specification
- Reproducible workflow
- Can be version controlled
- Can be executed with `/execute-spec spec.yaml`

---

# Deep Dive: Categorical Foundations

## Why Category Theory?

Traditional prompt engineering treats prompts as isolated text strings. Categorical meta-prompting treats them as **mathematical objects** that compose predictably according to laws.

### The Problem with Traditional Prompting

```python
# Traditional approach
prompt1 = "Implement authentication"
prompt2 = "Add error handling"
combined = prompt1 + "\n\n" + prompt2  # Naive concatenation

# Problems:
# 1. No quality tracking
# 2. No composition rules
# 3. No refinement mechanism
# 4. No context awareness
```

### The Categorical Solution

```python
# Categorical approach
task1 = Task("implement authentication")
task2 = Task("add error handling")

# Functor F: Task → Prompt
prompt1 = F(task1)  # Structure-preserving transformation

# Monad M: Prompt → Refined_Prompt
refined = prompt1.bind(refine_quality)  # Kleisli (>=>)

# Comonad W: History → Context
context = W.extract(conversation_history)

# Composition (Sequential →)
combined = prompt1 >> prompt2  # Obeys laws!
```

**Benefits:**
1. **Predictable composition**: `(A >> B) >> C = A >> (B >> C)` (associativity)
2. **Quality tracking**: Every operation updates quality metric
3. **Refinement**: Monadic bind enables iteration
4. **Context awareness**: Comonad extracts relevant context

## The Three Core Abstractions

### 1. Functor F: Task → Prompt

**Purpose:** Transform user tasks into well-structured prompts while preserving structure.

**Laws:**
```
F(id) = id                    # Identity: Functor preserves do-nothing
F(g ∘ f) = F(g) ∘ F(f)        # Composition: Functor preserves composition
```

**Example:**
```python
# Task composition
task_composed = analyze_task ∘ design_task  # Compose tasks

# Functor application
F(task_composed) = F(analyze_task) ∘ F(design_task)  # Prompts compose too!

# Concrete:
task = "implement auth" ∘ "add logging"
F(task) = "Implement authentication system with comprehensive logging"
        = "Implement authentication system" ∘ "Add comprehensive logging"
```

**Why this matters:**
If tasks compose in a certain way, their prompts **must** compose the same way. This ensures predictability.

### 2. Monad M: Prompt → Refined_Prompt

**Purpose:** Iterative refinement with quality-gating.

**Laws:**
```
return >=> f = f              # Left identity: return is transparent
f >=> return = f              # Right identity: return is transparent
(f >=> g) >=> h = f >=> (g >=> h)   # Associativity: order doesn't matter
```

**Kleisli operator (>=>):**
```python
# Traditional function composition: (g ∘ f)(x) = g(f(x))
# Kleisli composition: (g >=> f)(x) = f(x).bind(g)

# Example:
analyze = lambda task: Prompt(task, quality=0.75)
design = lambda prompt: refine(prompt, quality=0.85)
implement = lambda prompt: refine(prompt, quality=0.90)

# Kleisli chain:
result = (analyze >=> design >=> implement)(task)

# Execution:
# 1. analyze(task) → Prompt with quality 0.75
# 2. If 0.75 < threshold: refine before passing to design
# 3. design(refined_prompt) → Prompt with quality 0.85
# 4. If 0.85 < threshold: refine before passing to implement
# 5. implement(refined_prompt) → Final prompt with quality 0.90
```

**Why this matters:**
Monadic composition allows us to thread quality assessment through every step, refining when needed.

### 3. Comonad W: History → Context

**Purpose:** Extract relevant context from conversation history.

**Operations:**
```
extract: W → A                # Get value from context
duplicate: W → W<W>           # Create nested context (meta-observation)
extend: (W → B) → (W → W<B>)  # Apply context-aware transformation
```

**Example:**
```python
# Context structure
W = ConversationHistory([
  Message("implement auth"),
  Message("use JWT tokens"),
  Message("add refresh tokens")
])

# Extract current focus
current_task = W.extract()  # "add refresh tokens"

# Duplicate for meta-analysis
meta_context = W.duplicate()  # W<W>: context about context
# Useful for analyzing conversation patterns, quality trends

# Extend with quality assessment
quality_aware = W.extend(assess_quality)
# For each message, assess quality in context of all previous messages
```

**Why this matters:**
Comonads let us **extract** context (what's relevant now) and **extend** operations (apply transformations that are aware of full context).

## Quality Enrichment: [0,1]-Enriched Category

**Traditional category:** Objects and morphisms (arrows between objects).

**Enriched category:** Arrows have **distance/cost/quality** values from [0,1].

```
      f
  A ───────> B
    q(f)=0.85
```

**Composition rule:**
```
A ──f──> B ──g──> C
  0.85     0.90

quality(g ∘ f) = min(0.85, 0.90) = 0.85
```

**Parallel rule:**
```
  ┌── f ──┐
A ┤       ├> C
  └── g ──┘
   0.85  0.90

quality(f || g) = mean(0.85, 0.90) = 0.875
```

**Why this matters:**
Every composition automatically tracks quality degradation (sequential) or aggregation (parallel).

## Practical Example: Full Pipeline

```bash
/meta @mode:iterative @tier:L5 [R→(D||F)→I→T] "build e-commerce checkout"
```

**Categorical breakdown:**

### 1. Functor F: Task → Prompt

```python
task = Task("build e-commerce checkout")

# F application:
prompt = F(task)
# → domain: ECOMMERCE
# → tier: L5 (multi-component feature)
# → template: {
#     context: "expert_ecommerce_patterns",
#     mode: "research_design_implement_test",
#     format: "full_stack_implementation"
#   }
```

### 2. Composition Structure: [R→(D||F)→I→T]

```
R: Research
├─ Survey checkout best practices
├─ Analyze payment gateway options
└─ Quality: 0.88

(D||F): Parallel Design + Frontend
├─ D: Backend design (API, database)
│   └─ Quality: 0.85
├─ F: Frontend design (UI/UX, flows)
│   └─ Quality: 0.90
└─ Combined quality: mean(0.85, 0.90) = 0.875

I: Implement
├─ Input quality: min(0.88, 0.875) = 0.875
├─ Implementation quality: 0.82
└─ Output quality: 0.82

T: Test
├─ Input quality: 0.82
├─ Test quality: 0.92
└─ Output quality: min(0.82, 0.92) = 0.82

Overall: min(0.88, 0.875, 0.82, 0.82) = 0.82
```

### 3. Monad M: Iterative Refinement

```python
# mode:iterative enables RMP loop

iteration_1:
  quality: 0.75 < 0.80 threshold
  → bind(refine)

iteration_2:
  quality: 0.80 < 0.80 threshold (marginal)
  → bind(refine)

iteration_3:
  quality: 0.85 ≥ 0.80 threshold
  → return (converge)
```

### 4. Comonad W: Context Extraction

```python
# At each stage, extract relevant context:

R stage:
  W.extract(previous_ecommerce_implementations)
  → "Similar checkout built for client X, used Stripe"

D||F stage:
  W.extract(research_outputs + user_requirements)
  → "Research indicates Stripe best for MVP"
  → "User wants guest checkout + saved cards"

I stage:
  W.extract(design_outputs)
  → API contracts, database schema

T stage:
  W.extract(implementation)
  → Test coverage areas, edge cases
```

## Mathematical Properties in Practice

### Associativity

```bash
# These are equivalent:
/chain [[A→B]→C]
/chain [A→[B→C]]
/chain [A→B→C]

# All produce same result with same quality
```

**Why:** Monad associativity law `(f >=> g) >=> h = f >=> (g >=> h)`

### Identity

```bash
# These are equivalent:
/chain [/meta→id]
/chain [id→/meta]
/chain [/meta]

# id = "do nothing" operation
```

**Why:** Monad identity laws `return >=> f = f` and `f >=> return = f`

### Commutativity (Parallel)

```bash
# These produce same combined output (order-independent):
/chain [A||B]
/chain [B||A]

# Both: quality = mean(q_A, q_B)
```

**Why:** Parallel execution has no ordering constraints.

## Quality Algebra

### Tensor Product (⊗)

```bash
# A⊗B means "both A and B required"
[security⊗performance]

# Quality: must satisfy both
quality(security⊗performance) = min(q_security, q_performance)
```

**Use case:** Feature requires both security *and* performance.

### Parallel (||)

```bash
# A||B means "explore both A and B"
[approach_a||approach_b]

# Quality: average of both
quality(approach_a||approach_b) = mean(q_a, q_b)
```

**Use case:** Comparing multiple approaches.

### Sequential (→)

```bash
# A→B means "A then B"
[analyze→implement]

# Quality: limited by weakest link
quality(analyze→implement) = min(q_analyze, q_implement)
```

**Use case:** Pipeline where each stage depends on previous.

### Kleisli (>=>)

```bash
# A>=>B means "A then B, with refinement"
[analyze>=>implement]

# Quality: iteratively improved
# If q_analyze < threshold: refine before implement
# If q_implement < threshold: refine
```

**Use case:** Quality-critical pipeline.

## Advanced: Functorial Data Migration

Inspired by David Spivak's work on categorical databases.

**Idea:** Schemas are categories, data migration is a functor.

```
Schema_A ──F──> Schema_B

# Example:
users_v1 (id, name, email)
  ↓
  F (add created_at, split name)
  ↓
users_v2 (id, first_name, last_name, email, created_at)

# F preserves:
# - Relationships (foreign keys)
# - Constraints (not null, unique)
```

**In meta-prompting:**

```bash
/transform @from:sequential @to:parallel "migrate prompt strategy"

# Transform functor:
F: SequentialPrompts → ParallelPrompts

# Preserves:
# - Task decomposition
# - Quality requirements
# - Output format

# Changes:
# - Execution model (sequential → parallel)
# - Quality aggregation (min → mean)
```

## Why This Framework is Powerful

### 1. Composability

```bash
# Build complex workflows from simple pieces
/chain [/debug→/fix→/test]  # Simple

# Compose with others
/chain [/debug→/fix→/test→/review]  # Extended

# Nest compositions
/chain [/debug→(/fix||/workaround)→/test]  # Branching
```

### 2. Predictability

```bash
# Know quality before execution
/chain @mode:dry-run [A→B→C]
# → quality ≈ min(q_A, q_B, q_C)
```

### 3. Refinement

```bash
# Automatic quality improvement
/rmp @quality:0.9 "complex task"
# → Iterates until quality ≥ 0.9
```

### 4. Context Awareness

```bash
# Automatically extracts relevant context
/meta "add feature X"
# W.extract(history) → knows about existing architecture
```

### 5. Mathematical Guarantees

- **Associativity**: Can regroup operations without changing result
- **Identity**: Can add/remove identity operations safely
- **Quality preservation**: Know how quality propagates

---

# Advanced Techniques

## Technique 1: Custom Quality Functions

While the default 4-dimensional quality vector works well, you can define custom quality functions for specialized domains.

### Example: Security-Focused Quality

```yaml
# Custom quality specification
quality:
  dimensions:
    - name: correctness
      weight: 0.30
      criteria:
        - solves_stated_problem
        - handles_edge_cases

    - name: security
      weight: 0.40  # Higher weight for security domain
      criteria:
        - owasp_top_10_addressed
        - input_validation
        - authentication_authorization
        - encryption_at_rest_in_transit
        - secrets_management

    - name: clarity
      weight: 0.15
      criteria:
        - readable_code
        - documentation

    - name: efficiency
      weight: 0.15
      criteria:
        - performance
        - resource_usage
```

**Usage:**
```bash
/meta @domain:SECURITY @quality:custom:security_focused "implement auth"
```

## Technique 2: Budget-Aware Composition

Control token budget distribution across pipeline stages.

### Example: Balanced Budget

```bash
/chain @budget:[4000,6000,3000,2000] [R→D→I→T] "feature"

# Budget distribution:
# R (Research): 4000 tokens (27%)
# D (Design): 6000 tokens (40%)  ← Most complex
# I (Implement): 3000 tokens (20%)
# T (Test): 2000 tokens (13%)
# Total: 15000 tokens
```

### Example: Front-Loaded Budget

```bash
/chain @budget:[8000,4000,2000,1000] [R→D→I→T] "feature"

# Budget distribution:
# R (Research): 8000 tokens (53%)  ← Deep research
# D (Design): 4000 tokens (27%)
# I (Implement): 2000 tokens (13%)
# T (Test): 1000 tokens (7%)
# Total: 15000 tokens
```

**Variance monitoring:**
```bash
/chain @budget:[4000,6000,3000,2000] @variance:15% [R→D→I→T] "feature"

# If any stage exceeds budget by >15%, halt with warning
```

## Technique 3: Conditional Branching

Use quality thresholds to conditionally branch execution.

```bash
/chain [
  analyze→
  if(quality≥0.85)→implement
  if(quality<0.85)→(redesign→implement)
] "complex feature"
```

**Execution:**
```
analyze → quality: 0.78 < 0.85
  ↓
redesign → quality: 0.88 ≥ 0.85
  ↓
implement
```

## Technique 4: Multi-Expert Consensus

Combine multiple approaches and use consensus for decision.

```bash
/chain [
  (expert_a || expert_b || expert_c)→
  consensus(threshold=0.75)→
  implement
] "architectural decision"
```

**Consensus function:**
```python
def consensus(approaches, threshold=0.75):
    """
    Require threshold agreement among experts.

    Example:
    expert_a: Use microservices (quality: 0.85)
    expert_b: Use microservices (quality: 0.82)
    expert_c: Use monolith (quality: 0.75)

    Agreement: 2/3 (66%) for microservices
    Threshold: 75%
    Result: No consensus, need more expert opinions or discussion
    """
    votes = count_votes(approaches)
    max_vote = max(votes.values())
    total = sum(votes.values())

    if max_vote / total >= threshold:
        return majority_approach
    else:
        return "consensus_not_reached_need_discussion"
```

## Technique 5: Temporal Composition

Compose across time with checkpointing.

```bash
# Day 1: Research and design
/chain [R→D] "large feature" → checkpoint_1.yaml

# Day 2: Implement using checkpoint
/chain @resume:checkpoint_1.yaml [I→T] "large feature"
```

**checkpoint_1.yaml:**
```yaml
state:
  completed_stages:
    - R:
        quality: 0.88
        outputs:
          - research_doc.md
          - requirements.yaml
    - D:
        quality: 0.85
        outputs:
          - architecture.md
          - api_spec.yaml
          - db_schema.sql

  next_stages:
    - I
    - T

  context:
    task: "large feature"
    domain: ARCHITECTURE
    tier: L6
```

## Technique 6: Quality Trend Analysis

Track quality over iterations to detect patterns.

```bash
/rmp @quality:0.85 @max_iterations:10 "complex task"
```

**Quality trend:**
```
Iteration 1: 0.70
Iteration 2: 0.75 (+0.05)
Iteration 3: 0.78 (+0.03)
Iteration 4: 0.80 (+0.02)
Iteration 5: 0.81 (+0.01)  ← Plateau detected
Iteration 6: 0.82 (+0.01)
Iteration 7: 0.82 (+0.00)  ← Fixed point

Status: PLATEAU_CONVERGE (quality 0.82 < target 0.85 but no improvement)
Action: Accept 0.82 as best achievable, or restructure approach
```

**Trend patterns:**
- **Linear improvement**: Steady delta → continue
- **Plateau**: Delta → 0 → fixed point reached
- **Oscillation**: Alternating +/− → instability, restructure
- **Degradation**: Negative delta → bug in refinement, abort

## Technique 7: Domain-Specific Templates

Create reusable templates for common domain patterns.

### Example: API Development Template

```yaml
# .claude/templates/api-development.yaml
name: API Development Template
domain: API
tier: L4-L5

structure:
  research:
    - RESTful best practices
    - Authentication strategy
    - Rate limiting approach

  design:
    - OpenAPI specification
    - Error handling patterns
    - Versioning strategy

  implement:
    - Route handlers
    - Middleware stack
    - Input validation
    - Error handling

  test:
    - Unit tests (handlers, middleware)
    - Integration tests (end-to-end flows)
    - Load tests (rate limiting, performance)

quality:
  dimensions:
    correctness: 0.35
    clarity: 0.25      # Documentation important for APIs
    completeness: 0.25  # All endpoints, error cases
    efficiency: 0.15

composition: [R→D→I→T]
```

**Usage:**
```bash
/meta @template:api-development "build user management API"
```

## Technique 8: Skill Discovery and Composition

Use the skill system for automatic capability discovery.

```bash
/meta @skills:discover(domain=API,relevance>0.8) "build GraphQL API"

# System discovers relevant skills:
# - graphql-api-development (relevance: 0.95)
# - api-security-patterns (relevance: 0.85)
# - typescript-backend (relevance: 0.82)

# Auto-composes into prompt with all three skill contexts
```

## Technique 9: Hierarchical Task Decomposition

Automatically decompose complex tasks into hierarchical stages.

```bash
/hekat @tier:L7 "build complete SaaS platform"
```

**Decomposition:**
```
L7: Build complete SaaS platform
├─ L6: Authentication & authorization system
│   ├─ L5: Multi-tenant user management
│   ├─ L5: RBAC with tenant isolation
│   └─ L4: JWT token service
├─ L6: Payment processing system
│   ├─ L5: Stripe integration
│   ├─ L5: Subscription management
│   └─ L4: Webhook handling
├─ L6: Admin dashboard
│   ├─ L5: Analytics & reporting
│   ├─ L4: Tenant management UI
│   └─ L4: User management UI
└─ L5: API gateway
    ├─ L4: Rate limiting
    ├─ L4: API versioning
    └─ L3: Request logging
```

## Technique 10: Cross-Language Composition

Compose prompts across different programming languages or tools.

```bash
/chain [
  /backend(lang=python)→
  /frontend(lang=typescript)→
  /infra(tool=terraform)
] "full-stack application"
```

**Each stage uses appropriate language context:**
- Backend: Python, FastAPI, SQLAlchemy
- Frontend: TypeScript, React, Vite
- Infrastructure: Terraform, AWS

---

# Reference

## Complete Modifier List

| Modifier | Type | Values | Default | Description |
|----------|------|--------|---------|-------------|
| `@mode:` | enum | active, iterative, dry-run, spec | active | Execution mode |
| `@quality:` | float | 0.0-1.0 | 0.8 | Quality convergence threshold |
| `@tier:` | enum | L1, L2, L3, L4, L5, L6, L7 | auto | Task complexity tier |
| `@budget:` | int/array | integer, [array], auto | auto | Token budget allocation |
| `@variance:` | percentage | 0-100% | 20% | Budget variance threshold |
| `@max_iterations:` | int | 1-10 | 5 | Maximum RMP loop iterations |
| `@template:` | string | {context}+{mode}+{format} | auto | Template component selection |
| `@domain:` | enum | ALGORITHM, SECURITY, API, DEBUG, TESTING, ARCHITECTURE | auto | Domain classification |
| `@skills:` | function | discover(), compose(), list | auto | Skill resolution strategy |
| `@resume:` | file | path/to/checkpoint.yaml | - | Resume from checkpoint |
| `@checkpoint:` | boolean | true, false | true | Enable checkpointing |
| `@parallel:` | int | 1-10 | 3 | Max parallel branches |

## Complete Operator List

| Operator | Symbol | Unicode | Type | Quality Rule | Associative | Commutative |
|----------|--------|---------|------|--------------|-------------|-------------|
| Sequential | `→` | U+2192 | Binary | `min(q₁, q₂)` | Yes | No |
| Parallel | `\|\|` | - | N-ary | `mean(q₁, ..., qₙ)` | Yes | Yes |
| Tensor | `⊗` | U+2297 | Binary | `min(q₁, q₂)` | Yes | Yes |
| Kleisli | `>=>` | - | Binary | Iterative improvement | Yes | No |
| Choice | `+` | - | Binary | `max(q₁, q₂)` | Yes | Yes |
| Conditional | `?:` | - | Ternary | Depends on condition | No | No |

## Complete Command List

### Core Commands
- `/meta` - Categorical meta-prompting with auto-detection
- `/rmp` - Recursive meta-prompting with quality loop
- `/chain` - Command composition with operators

### Review & Debug
- `/review` - Domain-aware code review
- `/debug` - Systematic debugging with hypothesis testing

### Prompt Engineering
- `/build-prompt` - Assemble prompt from templates
- `/route` - Dynamic routing based on task analysis
- `/list-prompts` - List available prompt templates
- `/select-prompt` - Select best prompt from registry
- `/compose` - Compose multi-step prompt pipeline

### Orchestration Workflows
- `/meta-build` - Research → Design → Implement → Test
- `/meta-refactor` - Analyze → Plan → Refactor → Verify
- `/meta-review` - Multi-pass parallel review
- `/meta-test` - Comprehensive testing workflow
- `/meta-fix` - Debug → Analyze → Fix → Verify
- `/meta-deploy` - Validate → Stage → Deploy → Monitor

### Utility
- `/context` - Extract context from history (comonad operation)
- `/transform` - Natural transformation between strategies
- `/blocks` - Compose atomic blocks into custom workflows

## Quality Dimension Details

### Correctness (40% weight)
**Evaluates:** Does it solve the stated problem?

**Criteria:**
- ✓ Solves the primary requirement
- ✓ Handles edge cases
- ✓ No logical errors
- ✓ Correct algorithm/approach

**Scoring:**
- 1.0: Perfect solution, all cases handled
- 0.8: Solves main cases, minor edge cases missed
- 0.6: Solves main case, several edge cases missed
- 0.4: Partial solution with gaps
- 0.2: Wrong approach but salvageable
- 0.0: Completely wrong

### Clarity (25% weight)
**Evaluates:** Is it understandable?

**Criteria:**
- ✓ Readable code/explanation
- ✓ Good naming conventions
- ✓ Appropriate documentation
- ✓ Clear structure

**Scoring:**
- 1.0: Exemplary clarity, anyone can understand
- 0.8: Clear with minor ambiguities
- 0.6: Understandable with effort
- 0.4: Confusing in places
- 0.2: Hard to understand
- 0.0: Incomprehensible

### Completeness (20% weight)
**Evaluates:** Are all aspects handled?

**Criteria:**
- ✓ All requirements addressed
- ✓ Error handling included
- ✓ Edge cases covered
- ✓ Documentation complete

**Scoring:**
- 1.0: Fully complete, production-ready
- 0.8: Complete with minor gaps
- 0.6: Core complete, peripherals missing
- 0.4: Partial implementation
- 0.2: Skeleton only
- 0.0: Incomplete

### Efficiency (15% weight)
**Evaluates:** Is it well-designed?

**Criteria:**
- ✓ Appropriate algorithms/data structures
- ✓ No obvious performance issues
- ✓ Resource-efficient
- ✓ Scalable design

**Scoring:**
- 1.0: Optimal design
- 0.8: Efficient with minor improvements possible
- 0.6: Acceptable efficiency
- 0.4: Inefficiencies present
- 0.2: Poor design choices
- 0.0: Severely inefficient

## Budget Guidelines

| Task Complexity | Estimated Tokens | Tier | Example |
|----------------|------------------|------|---------|
| Trivial | 500-1,000 | L1 | Fix typo, format code |
| Simple | 1,000-2,500 | L2 | Add validation, simple function |
| Moderate | 2,500-5,000 | L3 | Implement feature, refactor module |
| Complex | 5,000-10,000 | L4 | Multi-file feature, integration |
| Advanced | 10,000-20,000 | L5 | System component, service |
| Expert | 20,000-40,000 | L6 | Multi-component system |
| Research | 40,000+ | L7 | Novel architecture, research-grade |

## Checkpoint Schema

```yaml
checkpoint:
  meta:
    command: string
    timestamp: ISO8601
    version: semver

  state:
    iteration: int
    status: CONTINUE | CONVERGED | MAX_ITERATIONS | HALT | PLATEAU

  quality:
    correctness: float[0,1]
    clarity: float[0,1]
    completeness: float[0,1]
    efficiency: float[0,1]
    aggregate: float[0,1]
    delta: float[-1,1]

  budget:
    total: int
    used: int
    remaining: int
    variance_pct: float[0,100]

  outputs:
    - type: string
      path: string
      description: string

  next:
    recommended_action: string
    estimated_iterations_remaining: int
```

## Categorical Laws (Formal)

### Functor Laws
```
∀ id: A → A. F(id) = id                     (Identity)
∀ f: A → B, g: B → C. F(g ∘ f) = F(g) ∘ F(f) (Composition)
```

### Monad Laws
```
∀ a: A. return(a) >>= f = f(a)              (Left Identity)
∀ m: M A. m >>= return = m                  (Right Identity)
∀ m: M A, f: A → M B, g: B → M C.           (Associativity)
  (m >>= f) >>= g = m >>= (λx. f(x) >>= g)
```

### Comonad Laws
```
∀ w: W A. extract(duplicate(w)) = w         (Extract after duplicate)
∀ w: W A. fmap(extract)(duplicate(w)) = w   (Duplicate then extract)
∀ w: W A. duplicate(duplicate(w)) =         (Duplicate associativity)
           fmap(duplicate)(duplicate(w))
```

### Quality Enrichment Laws
```
∀ f: A → B, g: B → C.
  q(g ∘ f) ≤ min(q(g), q(f))                (Sequential degradation)

∀ f₁: A → B, ..., fₙ: A → B.
  q(f₁ || ... || fₙ) = mean(q(f₁), ..., q(fₙ)) (Parallel aggregation)

∀ f: A → B, g: A → B.
  q(f ⊗ g) ≤ min(q(f), q(g))                (Tensor degradation)
```

## Glossary

**Aggregate Quality**: Weighted sum of quality dimensions (correctness, clarity, completeness, efficiency).

**Associativity**: Property where `(a ∘ b) ∘ c = a ∘ (b ∘ c)`. Allows regrouping without changing result.

**Checkpoint**: Snapshot of execution state including quality, budget, outputs, and next actions.

**Comonad**: Mathematical structure for context extraction. Dual of monad.

**Composition**: Combining smaller operations into larger ones.

**Convergence**: Reaching quality threshold or fixed point in iterative refinement.

**Domain**: Task category (e.g., SECURITY, API, ALGORITHM) for specialized handling.

**Enrichment**: Adding structure (quality metric [0,1]) to categorical arrows.

**Functor**: Structure-preserving transformation (e.g., Task → Prompt).

**Kleisli Arrow**: Monadic composition operator `>=>` with refinement.

**Monad**: Mathematical structure for iterative refinement with bind operator.

**Modifier**: Parameter like `@quality:0.85` that configures command behavior.

**Operator**: Symbol like `→`, `||`, `⊗` that defines composition strategy.

**Plateau**: Quality improvement slowing to near-zero, indicating fixed point.

**Quality Vector**: Multi-dimensional assessment [correctness, clarity, completeness, efficiency].

**RMP**: Recursive Meta-Prompting, iterative refinement with quality-gating.

**Tensor Product**: Operator `⊗` meaning "both required", quality is minimum.

**Tier**: Complexity level L1-L7 from simple to research-grade.

---

## Further Reading

### Papers
- Spivak, D. I. (2012). "Functorial Data Migration"
- Milewski, B. (2018). "Category Theory for Programmers"
- Wadler, P. (1995). "Monads for functional programming"

### Documentation
- `docs/UNIFIED-SYNTAX-SPECIFICATION.md` - Complete grammar
- `docs/PATTERN-EXTRACTION-COMONADIC.md` - Comonad foundations
- `docs/ARCHITECTURE-UNIFIED.md` - System architecture
- `.claude/skills/meta-self/` - Master syntax reference

### Online Resources
- nLab: Category Theory https://ncatlab.org/
- Bartosz Milewski's Blog: https://bartoszmilewski.com/
- David Spivak's Work: https://math.mit.edu/~dspivak/

---

## Version History

**2.1** (2025-12-08)
- Complete visual cheatsheet
- Interactive examples with real scenarios
- Deep dive into categorical foundations
- Advanced techniques documentation

**2.0** (2025-11-30)
- Unified syntax specification
- Quality enrichment system
- RMP loop formalization
- Checkpoint standardization

**1.0** (2025-11-15)
- Initial categorical framework
- Basic commands (/meta, /rmp, /chain)
- Functor/Monad/Comonad structure

---

**Generated**: 2025-12-08
**Framework Version**: 2.1
**Status**: Production Ready

---

*This guide provides everything you need to master categorical meta-prompting, from quick reference to deep mathematical foundations. Use the cheatsheet for daily work, examples for learning patterns, and the deep dive for understanding the "why" behind the framework.*
