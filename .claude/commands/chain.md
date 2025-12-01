---
description: Chain multiple slash commands together, passing output as input to next command
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite, Task
argument-hint: [/cmd1→/cmd2→/cmd3] @mode:[mode] [initial-input]
---

# Prompt Chain Executor

Execute a sequence of slash commands using categorical composition operators.

## Unified Syntax

```
/chain [/cmd1→/cmd2→/cmd3] @mode:active "initial input"
```

### Composition Operators

| Operator | Unicode | Meaning | Categorical Type |
|----------|---------|---------|------------------|
| `→` | U+2192 | Sequence (Kleisli) | Output of A → Input of B |
| `then` | - | Sequence (legacy) | Same as → |
| `\|\|` | - | Parallel | Execute concurrently |
| `>=>` | - | Kleisli refinement | Monadic with quality gates |

### Supported Modifiers

| Modifier | Default | Description |
|----------|---------|-------------|
| `@mode:` | active | Execution mode: active, dry-run, spec |
| `@budget:` | auto | Total token budget for chain |
| `@variance:` | 20% | Acceptable budget variance |
| `@quality:` | - | Quality gate between stages |
| `@quality:visualize` | false | Show quality flow visualization (Phase 5) |
| `@catch:` | halt | Error handling: halt, log, retry:N, skip, substitute:[cmd] |
| `@fallback:` | - | Fallback strategy: return-best, return-last, use-default:[val], empty |

---

## Chain Specification

**Arguments**: $ARGUMENTS

---

## Parse Chain

From your input, I detect the following chain structure:

### Operator Detection

```
Input: $ARGUMENTS

Detected Operators:
- → (sequence): Commands execute sequentially, output → input
- || (parallel): Commands execute concurrently
- >=> (Kleisli): Commands with quality-gated refinement
- "then" (legacy): Treated as →
```

### Chain Structure

| Position | Command | Input Source | Operator |
|----------|---------|--------------|----------|
| 1 | [first command] | [initial input] | (start) |
| 2 | [second command] | [output from 1] | → |
| 3 | [third command] | [output from 2] | → |
| ... | ... | ... | ... |

---

## Mode: Dry-Run

*If @mode:dry-run was specified, show plan and exit:*

```yaml
CHAIN_PLAN:
  stages: [/cmd1, /cmd2, /cmd3]
  operators: [→, →]
  categorical_structure: Kleisli composition
  estimated_budget: [total estimate]
  data_flow:
    - {stage: 1, input: "initial", output: "→ stage 2"}
    - {stage: 2, input: "from stage 1", output: "→ stage 3"}
    - {stage: 3, input: "from stage 2", output: "final"}
  exit: Plan generated, no execution
```

---

## Mode: Spec

*If @mode:spec was specified, generate specification and exit:*

```yaml
name: chain-[hash]
type: sequential_composition
categorical_structure:
  functor: F(Command) → Prompt
  composition: Kleisli (→)
  law: (f → g) → h = f → (g → h)  # Associativity
stages:
  - {name: stage_1, command: /cmd1, operator: start}
  - {name: stage_2, command: /cmd2, operator: →}
  - {name: stage_3, command: /cmd3, operator: →}
quality_gates: [if @quality: specified]
budget: [if @budget: specified]
```

---

## Mode: Active (Default)

### How Chaining Works (Categorical)

```
/cmd1 [input]
    │
    ↓ output becomes context (Kleisli →)
    │
/cmd2 [context from cmd1]
    │
    ↓ output becomes context (Kleisli →)
    │
/cmd3 [context from cmd2]
    │
    ↓
Final Result
```

**Categorical Law**: `(f → g) → h = f → (g → h)` (Associativity)

Each command is a morphism in the prompt category. Chaining them = Kleisli composition.

---

## Execute Chain

### Stage 1: [Command 1]

```
Input: [initial input]
Executing: /[command1]
Operator: (start)
```

[Execute first command here]

**Output from Stage 1:**
```
[capture output - this becomes input for stage 2]
```

**Checkpoint:**
```yaml
CHAIN_CHECKPOINT_1:
  command: /[cmd1]
  status: COMPLETE
  quality: [if assessed]
  tokens_used: [estimate]
  output_summary: [brief]
```

---

### Stage 2: [Command 2]

```
Input: [output from stage 1]
Executing: /[command2]
Operator: → (sequence)
```

[Execute second command with context from first]

**Output from Stage 2:**
```
[capture output - this becomes input for stage 3]
```

**Checkpoint:**
```yaml
CHAIN_CHECKPOINT_2:
  command: /[cmd2]
  status: COMPLETE
  quality: [if assessed]
  tokens_used: [estimate]
  output_summary: [brief]
```

---

### Stage 3: [Command 3] (if specified)

```
Input: [output from stage 2]
Executing: /[command3]
Operator: → (sequence)
```

[Execute third command with context from second]

**Output from Stage 3:**
```
[capture output - final result]
```

**Checkpoint:**
```yaml
CHAIN_CHECKPOINT_3:
  command: /[cmd3]
  status: COMPLETE
  quality: [if assessed]
  tokens_used: [estimate]
  output_summary: [brief]
```

---

## Parallel Execution (|| operator)

When `||` is detected, execute commands concurrently:

```
[/cmdA || /cmdB || /cmdC]
         ↓
    ┌────┼────┐
    ↓    ↓    ↓
  cmdA cmdB cmdC  (parallel)
    ↓    ↓    ↓
    └────┼────┘
         ↓
    [aggregate results]
```

**Aggregation Strategy**: Concatenate outputs with headers, or merge if structured.

---

## Kleisli Refinement (>=> operator)

When `>=>` is detected, apply quality-gated monadic composition:

```
[/analyze >=> /design >=> /implement]

Each stage:
1. Execute command
2. Assess quality
3. If quality < @quality: threshold, refine before continuing
4. Pass refined output to next stage
```

---

## Chain Summary

```
╔══════════════════════════════════════════════════════════════╗
║ CHAIN RESULT                                                  ║
╠══════════════════════════════════════════════════════════════╣
║ Chain: /cmd1 → /cmd2 → /cmd3                                  ║
║ Composition: Kleisli (→)                                      ║
║ Total Stages: N                                               ║
║ Status: [COMPLETE | PARTIAL | FAILED]                         ║
╚══════════════════════════════════════════════════════════════╝
```

| Stage | Command | Status | Quality | Output Summary |
|-------|---------|--------|---------|----------------|
| 1 | /cmd1 | ✅ | [score] | [brief] |
| 2 | /cmd2 | ✅ | [score] | [brief] |
| 3 | /cmd3 | ✅ | [score] | [brief] |

**Final Result:**
```
[last stage output]
```

---

## Usage Examples

### Sequential Composition (→)

```bash
# Using → operator (preferred)
/chain [/debug→/review] "TypeError in auth.py line 42"

# Using Unicode arrow
/chain [/build-prompt→/rmp] "implement rate limiter"

# Multiple stages
/chain [/analyze→/plan→/implement→/test] "add caching layer"
```

### Legacy Syntax (then)

```bash
# Still supported for backward compatibility
/chain "/debug then /review" "TypeError in auth.py"
/chain "/build-prompt then /rmp" "implement feature"
```

### Parallel Composition (||)

```bash
# Execute reviews in parallel
/chain [/review-security || /review-performance] "api/auth.py"

# Multiple parallel analyses
/chain [/analyze-frontend || /analyze-backend || /analyze-db] "audit system"
```

### Kleisli Refinement (>=>)

```bash
# Quality-gated chain
/chain @quality:0.85 [/analyze>=>/ design>=>/ implement] "build auth"

# Each stage refines until quality threshold before continuing
```

### With Modifiers

```bash
# Dry-run preview
/chain @mode:dry-run [/debug→/fix→/test] "error in payment.py"

# With budget
/chain @budget:20000 [/research→/design→/implement] "new feature"

# Generate spec only
/chain @mode:spec [/analyze→/plan] "refactoring project"
```

### Mixed Operators

```bash
# Sequential with parallel sub-chain
/chain [/research→(/frontend || /backend)→/integrate] "full-stack feature"

# Note: Parentheses group parallel operations within sequence
```

---

## Backward Compatibility

Old syntax still works:
```bash
/chain "/cmd1 then /cmd2 then /cmd3" "input"
```

New unified syntax is preferred:
```bash
/chain [/cmd1→/cmd2→/cmd3] "input"
```

Both produce identical Kleisli composition.

---

## Categorical Laws Verified

1. **Identity**: `id → f = f = f → id`
2. **Associativity**: `(f → g) → h = f → (g → h)`
3. **Quality Degradation**: `quality(f → g) <= min(quality(f), quality(g))`

---

## Error Handling (Exception Monad)

Phase 3 addition: Error handling via Exception Monad semantics.

### Categorical Foundation

Error handling is modeled using the **Exception Monad** (Either E A):

```
Either<E, A> = Left(E) | Right(A)

Where:
- Left(e): Error case containing error value e
- Right(a): Success case containing value a
```

**Type Signature**:
```
Command: Task → Either<Error, Result>
```

### Monad Operations

1. **return**: Pure success
   ```
   return(a) = Right(a)
   ```

2. **bind (>=>)**: Composition with error propagation
   ```
   m >>= f = case m of
     Left(e) → Left(e)        -- error propagates
     Right(a) → f(a)          -- continue on success
   ```

3. **catch**: Error recovery
   ```
   catch(m, handler) = case m of
     Left(e) → handler(e)     -- recover from error
     Right(a) → Right(a)      -- pass through success
   ```

### Error Handling Laws

1. **Catch Identity**: `catch(Right(a), h) = Right(a)`
   - Successful values pass through unchanged

2. **Catch Error**: `catch(Left(e), h) = h(e)`
   - Error handler is applied to errors

3. **Catch Composition**: `catch(catch(m, h1), h2) = catch(m, λe. catch(h1(e), h2))`
   - Handlers compose properly

4. **Associativity Preservation**: Error handling preserves Kleisli associativity
   ```
   ((f @catch:h1) → g) → h = (f @catch:h1) → (g → h)
   ```

---

### @catch: Modifier Behaviors

The `@catch:` modifier specifies what to do when a command fails:

| Behavior | Syntax | Description | Result Type |
|----------|--------|-------------|-------------|
| **halt** (default) | `@catch:halt` | Stop chain immediately on error | Left(error) |
| **log** | `@catch:log` | Log error, continue chain | Left(error) with logged info |
| **retry** | `@catch:retry:N` | Retry command N times before failing | Right(result) or Left(error) |
| **skip** | `@catch:skip` | Skip failed command, continue with empty | Right(empty) |
| **substitute** | `@catch:substitute:/alt` | Use alternative command on failure | Right(alt_result) or Left(error) |

**Error Propagation Rules**:

```
Chain: [/cmd1→/cmd2→/cmd3]

If @catch:halt (default):
  cmd1 fails → chain halts, return Left(error_cmd1)

If @catch:log:
  cmd1 fails → log error, cmd2 receives Left(error_cmd1)
  cmd2 must handle Left or propagate

If @catch:skip:
  cmd1 fails → cmd2 receives Right(empty)
  cmd2 executes normally

If @catch:retry:3:
  cmd1 fails → retry 3 times
  if all fail → Left(error_after_3_retries)
  if any succeeds → Right(result)
```

---

### @fallback: Modifier Strategies

The `@fallback:` modifier specifies recovery values when errors occur:

| Strategy | Syntax | Description | When Used |
|----------|--------|-------------|-----------|
| **return-best** | `@fallback:return-best` | Return highest quality result so far | Iterative refinement with /rmp |
| **return-last** | `@fallback:return-last` | Return last successful result | Prefer recency over quality |
| **use-default** | `@fallback:use-default:[val]` | Use specific default value | Known safe fallback |
| **empty** | `@fallback:empty` | Return empty/neutral value | Continue with minimal context |

**Quality Preservation**:
```
For @fallback:return-best:
  quality(fallback_result) >= quality(all_previous_results)
```

---

### Error Handling Examples

#### Example 1: Retry on API Failure
```bash
/chain @catch:retry:3 [/call-api→/process→/store] "fetch user data"
```

**Behavior**:
- `/call-api` fails → retry 3 times
- If all 3 retries fail → chain halts with Left(api_error)
- If any retry succeeds → continue to `/process` with Right(data)

**Diagram**:
```
/call-api (attempt 1) → Left(timeout)
          ↓ retry
/call-api (attempt 2) → Left(timeout)
          ↓ retry
/call-api (attempt 3) → Right(data) ✓
          ↓
/process (data)
```

---

#### Example 2: Graceful Degradation with Skip
```bash
/chain [/fetch-cache@catch:skip→/compute@catch:log→/save] "expensive query"
```

**Behavior**:
- `/fetch-cache` fails → skip, continue with empty cache
- `/compute` receives Right(empty) → computes fresh
- If `/compute` fails → log error but continue to `/save`

**Diagram**:
```
/fetch-cache → Left(cache_miss)
     ↓ skip (@catch:skip)
Right(empty) → /compute
     ↓
Right(computed_result) → /save
```

---

#### Example 3: Fallback to Alternative Command
```bash
/chain [/primary@catch:substitute:/backup→/process] "critical task"
```

**Behavior**:
- Try `/primary` first
- If `/primary` fails → automatically run `/backup` instead
- `/process` receives output from whichever succeeded

**Diagram**:
```
/primary → Left(primary_error)
     ↓ substitute
/backup → Right(backup_result) ✓
     ↓
/process(backup_result)
```

---

#### Example 4: Iterative Refinement with Fallback
```bash
/rmp @fallback:return-best @quality:0.9 @catch:retry:2 "complex analysis"
```

**Behavior**:
- Iterate refinement loop toward quality 0.9
- If iteration fails → retry 2 times
- If still fails after retries → return best result so far
- Prevents losing progress from partial refinement

**Quality Tracking**:
```
Iteration 1: quality=0.75 ✓ (cached as best)
Iteration 2: quality=0.82 ✓ (cached as best)
Iteration 3: Left(error)
     ↓ retry
Iteration 3 (retry 1): Left(error)
     ↓ retry
Iteration 3 (retry 2): Left(error)
     ↓ @fallback:return-best
Return: quality=0.82 (best cached)
```

---

#### Example 5: Per-Stage Error Handling
```bash
/chain [/risky@catch:skip→/safe@catch:log→/final@catch:halt] "multi-stage task"
```

**Behavior**:
- Each command has its own error handling
- `/risky`: Skip on failure → Right(empty)
- `/safe`: Log on failure → Left(error) logged
- `/final`: Halt on failure (default)

**Diagram**:
```
/risky → Left(error) @catch:skip → Right(empty)
     ↓
/safe(empty) → Left(safe_error) @catch:log → Left(safe_error) [logged]
     ↓
/final → receives Left(safe_error)
     ↓ @catch:halt
Chain halts with error report
```

---

### Error State Tracking

During chain execution, error state is tracked at each stage:

```yaml
CHAIN_CHECKPOINT_N:
  command: /[cmd]
  status: SUCCESS | ERROR | RECOVERED
  error_info:
    original_error: [if error occurred]
    catch_behavior: [halt|log|retry|skip|substitute]
    fallback_used: [if fallback applied]
    retry_count: [if retries occurred]
    recovery_result: [if recovered]
```

**Status Values**:
- `SUCCESS`: Right(result) - command succeeded
- `ERROR`: Left(error) - command failed, no recovery
- `RECOVERED`: Right(result) - command failed but recovered via @catch/@fallback

---

### Usage Patterns

#### Pattern 1: Fail-Fast (Default)
```bash
/chain [/cmd1→/cmd2→/cmd3] "task"
# @catch:halt is default
```
Use when: Any failure should stop the chain immediately

#### Pattern 2: Resilient Pipeline
```bash
/chain @catch:log [/cmd1→/cmd2→/cmd3] "task"
```
Use when: Want to see all errors but continue processing

#### Pattern 3: Critical with Backup
```bash
/chain [/primary@catch:substitute:/backup→/process] "task"
```
Use when: Must succeed, have alternate path

#### Pattern 4: Best-Effort Refinement
```bash
/rmp @fallback:return-best @quality:0.85 "task"
```
Use when: Want high quality but accept best-so-far if can't reach threshold

---

### Backward Compatibility

- Existing chains without `@catch:` or `@fallback:` behave identically
- Default behavior is `@catch:halt` (fail-fast)
- No breaking changes to existing syntax

---

### Implementation Notes

Error handling integrates with existing operators:

**Sequential (→)**:
```
/cmd1→/cmd2 with errors:
  result1 = cmd1(input)
  result2 = case result1 of
    Left(e) → apply_catch_handler(e)
    Right(a) → cmd2(a)
```

**Parallel (||)**:
```
/cmd1 || /cmd2 with errors:
  Execute both concurrently
  Collect: [result1, result2]
  Each result is Either<E, A>
  Aggregate based on @catch behavior
```

**Kleisli (>=>)**:
```
/cmd1 >=> /cmd2 with quality gates:
  result1 = cmd1(input)
  if quality(result1) >= threshold:
    result2 = cmd2(result1)
  else:
    apply_fallback_strategy()
```

---

## Quality Visualization (Phase 5)

Phase 5 addition: Visual representation of quality flow through chains.

### Categorical Foundation

Quality visualization makes the **[0,1]-enriched category** structure observable:

```
Enriched Hom-Sets: Hom_Q(A, B) = [0,1]
Quality Tensor:    q1 ⊗ q2 = min(q1, q2)
Identity:          1 (perfect quality)
```

Each command in a chain has an associated quality score in [0,1], and the visualization shows how quality **flows** and **degrades** through composition.

**Type Signature**:
```
Command: Task → (Result, Quality ∈ [0,1])
Chain: (Task, Q₀) → ... → (Result, Qₙ)
  where Qᵢ₊₁ ≤ Qᵢ (quality monotonicity)
```

---

### @quality:visualize Modifier

**Syntax**: `/chain @quality:visualize [/cmd1→/cmd2→/cmd3] "task"`

**Effect**: Renders quality flow diagram after chain execution.

**Visualization Formats**:
1. **Bar Chart**: Quality levels per stage
2. **Flow Diagram**: Quality transitions with arrows
3. **Detailed**: Quality breakdown by component
4. **Summary**: Overall quality metrics

---

### Format 1: Bar Chart (Default)

**Example**:
```bash
/chain @quality:visualize [/analyze→/design→/implement] "build auth system"
```

**Output**:
```
┌────────────────────────────────────────────────────────────┐
│  QUALITY FLOW VISUALIZATION                                │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  /analyze     0.75  ███████████████░░░░░░░  75%           │
│                ↓                                            │
│  /design      0.82  ████████████████░░░░░░  82%  (+7%)    │
│                ↓                                            │
│  /implement   0.68  █████████████░░░░░░░░░  68%  (-14%)   │
│                                                             │
│  ─────────────────────────────────────────────────────     │
│  Initial:     0.75                                          │
│  Final:       0.68                                          │
│  Change:      -0.07  (-9.3%)                               │
│  Min Stage:   0.68  (/implement)                           │
│  Max Stage:   0.82  (/design)                              │
│  Volatility:  0.14  (moderate)                             │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**Interpretation**:
- **Initial → Design**: Quality improved by 7% (good refinement)
- **Design → Implement**: Quality dropped 14% (implementation complexity)
- **Overall**: Net 9.3% quality loss (acceptable for implementation phase)
- **Volatility**: 0.14 = moderate fluctuation (within normal range)

---

### Format 2: Flow Diagram

**Example**:
```bash
/chain @quality:visualize [/research→/prototype→/refine→/deploy] "feature"
```

**Output**:
```
┌────────────────────────────────────────────────────────────┐
│  QUALITY FLOW (Arrow Width = Quality)                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│   /research         /prototype       /refine       /deploy │
│      0.70              0.78            0.85          0.80   │
│       │                 │               │             │     │
│       │    Q: 0.70      │    Q: 0.78    │   Q: 0.85   │    │
│       ├════════════════▶├══════════════▶├════════════▶│    │
│       │    +8%          │    +7%        │   -5%       │    │
│       │                 │               │             │     │
│                                                             │
│  Legend:                                                    │
│    ═══▶  Strong quality (≥0.80)                            │
│    ───▶  Medium quality (0.60-0.79)                        │
│    ···▶  Weak quality (<0.60)                              │
│                                                             │
│  Quality Trend: ↗↗↘  (improve, improve, slight drop)      │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**Interpretation**:
- **Research → Prototype**: +8% quality (successful prototyping)
- **Prototype → Refine**: +7% quality (effective refinement)
- **Refine → Deploy**: -5% quality (deployment constraints acceptable)
- **Trend**: Overall upward with final minor drop (expected)

---

### Format 3: Detailed Breakdown

**Example**:
```bash
/chain @quality:visualize [/cmd1→/cmd2→/cmd3] "complex task"
```

**Output**:
```
┌────────────────────────────────────────────────────────────┐
│  DETAILED QUALITY BREAKDOWN                                │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Stage 1: /cmd1                                            │
│  ├─ Completeness:  0.80  ████████████████░░░░             │
│  ├─ Correctness:   0.75  ███████████████░░░░░             │
│  ├─ Clarity:       0.70  ██████████████░░░░░░             │
│  └─ Overall:       0.75  ███████████████░░░░░             │
│                                                             │
│  Stage 2: /cmd2                                            │
│  ├─ Completeness:  0.85  █████████████████░░░             │
│  ├─ Correctness:   0.82  ████████████████░░░░             │
│  ├─ Clarity:       0.78  ███████████████░░░░░             │
│  └─ Overall:       0.82  ████████████████░░░░   (+7%)     │
│                                                             │
│  Stage 3: /cmd3                                            │
│  ├─ Completeness:  0.90  ██████████████████░░             │
│  ├─ Correctness:   0.88  █████████████████░░░             │
│  ├─ Clarity:       0.85  █████████████████░░░             │
│  └─ Overall:       0.88  █████████████████░░░   (+6%)     │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  Quality Trajectory:  0.75 → 0.82 → 0.88                  │
│  Total Improvement:   +0.13  (+17.3%)                      │
│  Best Component:      Completeness (Stage 3: 0.90)        │
│  Weakest Component:   Clarity (Stage 1: 0.70)             │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**Interpretation**:
- **Stage 1**: Baseline (70-80% across components)
- **Stage 2**: Improvement (all components +5-7%)
- **Stage 3**: Strong finish (85-90% across board)
- **Overall**: 17.3% quality gain (excellent)

---

### Format 4: Compact Summary

**Example**:
```bash
/chain @quality:visualize [/A→/B→/C→/D→/E] "multi-stage"
```

**Output**:
```
Quality: 0.70 → 0.75 → 0.82 → 0.78 → 0.85 | Δ: +15% ↗
```

**Legend**:
- **Numbers**: Quality at each stage
- **Δ**: Overall change from start to finish
- **Arrow**: Overall trend (↗ up, → flat, ↘ down)

---

### Visualization Rules

#### Rule 1: Quality Monotonicity Display

Show when quality **must** degrade (tensor product):

```
/cmd1 → /cmd2  (parallel with ||)
  Q₁=0.80      Q₂=0.90

Combined Quality: min(0.80, 0.90) = 0.80  ⊗
```

**Display**:
```
/cmd1 (0.80) ─┐
               ├─▶ Combined (0.80) ⊗ [tensor product]
/cmd2 (0.90) ─┘
```

#### Rule 2: Quality Gate Indicators

Show when quality gates are active:

```
/chain @quality:0.85 @quality:visualize [/A→/B→/C] "task"
```

**Display**:
```
Stage    Quality    Gate (≥0.85)    Status
─────────────────────────────────────────────
/A       0.75       ✗ BELOW         Continue (no gate yet)
/B       0.82       ✗ BELOW         Refining... (attempting gate)
/C       0.88       ✓ PASS          Success!
```

#### Rule 3: Error Recovery Visualization

Show quality impact of error recovery:

```
/chain @quality:visualize @fallback:return-best [/A→/B→/C] "task"
```

**Display**:
```
Stage    Quality    Status         Note
──────────────────────────────────────────────────────
/A       0.75       SUCCESS
/B       0.82       SUCCESS
/C       ERROR      RECOVERED      Fallback to /B (0.82) ✓
Final:   0.82                      Best result preserved
```

---

### Usage Examples

#### Example 1: Basic Visualization

```bash
/chain @quality:visualize [/analyze→/design→/implement] "feature"
```

**When to Use**: Want to see quality flow through pipeline.

**Expected Output**: Bar chart showing quality at each stage.

---

#### Example 2: Visualization with Quality Gate

```bash
/chain @quality:0.85 @quality:visualize [/draft→/review→/publish] "article"
```

**When to Use**: Want to see how stages approach quality threshold.

**Expected Output**:
```
Stage        Quality    Gate (≥0.85)
───────────────────────────────────────
/draft       0.70       ✗ Below (-0.15)
/review      0.82       ✗ Below (-0.03)
/publish     0.88       ✓ Pass  (+0.03)
```

---

#### Example 3: Detailed Component Breakdown

```bash
/chain @quality:visualize:detailed [/research→/analyze→/synthesize] "report"
```

**When to Use**: Need to see which quality components improve/degrade.

**Expected Output**: Detailed breakdown per stage (completeness, correctness, clarity).

---

#### Example 4: Multi-Agent Quality Comparison

```bash
/chain @quality:visualize [/agent1 || /agent2 || /agent3 → /synthesize] "task"
```

**Expected Output**:
```
Parallel Agents:
  /agent1: 0.75 ███████████████░░░░░
  /agent2: 0.82 ████████████████░░░░
  /agent3: 0.70 ██████████████░░░░░░

Combined (tensor): min(0.75, 0.82, 0.70) = 0.70 ⊗

/synthesize: 0.85 █████████████████░░░  (+15%)
```

---

### Categorical Interpretation

**Quality as Enrichment**:
```
Hom_Q(A, B) = [0,1]

For f: A → B and g: B → C:
  quality(g ∘ f) ≤ min(quality(f), quality(g))
```

**Visualization Shows**:
1. **Individual morphism quality**: quality(f)
2. **Composition quality**: quality(g ∘ f)
3. **Tensor product**: q₁ ⊗ q₂ = min(q₁, q₂)
4. **Quality trajectory**: How quality evolves through chain

**Laws Visualized**:
- **Associativity**: `(f → g) → h = f → (g → h)` (quality same either way)
- **Monotonicity**: `quality(A → B → C) ≤ min(quality(A→B), quality(B→C))`
- **Identity**: `quality(id) = 1.0` (perfect quality preservation)

---

### Implementation Notes

**Quality Assessment**:
```
Each command returns: (Result, QualityScore)

QualityScore = {
  completeness: [0,1],  // How complete is the result
  correctness: [0,1],   // How correct is the result
  clarity: [0,1],       // How clear is the result
  overall: [0,1]        // Aggregate quality
}

overall = geometric_mean(completeness, correctness, clarity)
        = ∛(completeness × correctness × clarity)
```

**Visualization Trigger**:
```
if @quality:visualize detected:
  1. Track quality at each stage
  2. After chain completes:
     - Render visualization format
     - Show quality trajectory
     - Display metrics
```

**Performance**:
- Visualization adds minimal overhead (~50ms)
- Quality tracking happens anyway (enriched category)
- Just renders tracked data visually

---

### Backward Compatibility

- Existing chains work identically (no visualization)
- `@quality:visualize` is opt-in
- Quality tracking always active (enriched category requirement)
- No breaking changes

---

### Future Enhancements (Phase 6+)

Potential additions for later versions:

1. **Interactive Visualization**:
   ```bash
   /chain @quality:visualize:interactive [/A→/B→/C] "task"
   # Click stages to see details
   ```

2. **Quality Prediction**:
   ```bash
   /chain @quality:visualize:predict [/A→/B→/C] "task"
   # Show predicted quality before execution
   ```

3. **Quality Optimization**:
   ```bash
   /chain @quality:optimize @target:0.90 [/A→/B→/C] "task"
   # Automatically insert refinement stages
   ```

4. **Export Formats**:
   ```bash
   /chain @quality:visualize:json [/A→/B→/C] "task"
   # Export visualization data as JSON
   ```
