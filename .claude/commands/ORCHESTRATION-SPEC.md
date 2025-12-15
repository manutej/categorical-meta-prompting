---
description: Orchestration specification for meta-commands - defines execution modes, command references, and skill invocations
---

# Meta-Command Orchestration Specification

This document defines the Domain-Specific Language (DSL) for orchestrating meta-commands.
Meta-commands are prompts that call other prompts, enabling sophisticated workflows.

**Categorical Foundation**: This DSL implements category theory constructs:
- **Functor F**: Task → Prompt (structure-preserving transformation)
- **Monad M**: Iterative refinement with quality tracking
- **Comonad W**: Context extraction from execution history
- **Natural Transformation α**: Strategy switching (F ⇒ G)
- **[0,1]-Enriched**: Quality degradation tracking

---

## Command Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    META-COMMAND LAYER                           │
│   /meta-build  /meta-fix  /meta-review  /meta-test  /meta-*    │
│                                                                 │
│   These commands ORCHESTRATE other commands using this DSL      │
├─────────────────────────────────────────────────────────────────┤
│                    ROUTING LAYER                                │
│   /route  /chain  /build-prompt  /template                      │
│                                                                 │
│   These commands COMPOSE and SELECT other commands dynamically  │
├─────────────────────────────────────────────────────────────────┤
│                    CATEGORICAL LAYER (F, M, W, α)               │
│   /meta (Functor)  /rmp (Monad)  /context (Comonad)            │
│   /transform (Natural Transformation)                           │
│                                                                 │
│   Core categorical operations: routing, refinement, context,    │
│   strategy switching                                            │
├─────────────────────────────────────────────────────────────────┤
│                    OBJECT COMMAND LAYER                         │
│   /debug  /review  /compose  /select-prompt  /list-prompts     │
│                                                                 │
│   These commands DO THE WORK on specific tasks                  │
├─────────────────────────────────────────────────────────────────┤
│                    SKILL LAYER                                  │
│   ⚡ categorical-property-testing                                │
│   ⚡ categorical-structure-builder                               │
│   ⚡ recursive-meta-prompting                                    │
│                                                                 │
│   Skills provide SPECIALIZED KNOWLEDGE when needed              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Meta-Command Registry

| Command | Purpose | Orchestration Pattern |
|---------|---------|----------------------|
| `/meta-build` | Full feature construction | Sequential stages with parallel design |
| `/meta-fix` | Bug resolution workflow | Debug → Analyze → Fix → Verify |
| `/meta-review` | Multi-dimensional review | Parallel specialized reviewers |
| `/meta-test` | Comprehensive testing | Parallel generation, sequential execution |
| `/meta-refactor` | Safe refactoring | Incremental with verification |
| `/meta-deploy` | Deployment workflow | Staged with rollback support |

---

## Execution Modes

Commands can specify WHEN and HOW to execute referenced commands/skills:

### Timing Modes
```
@run:now              Execute immediately, block until complete
@run:background       Start execution, continue without waiting
@run:after:/cmd       Execute after /cmd completes
@run:before:/cmd      Execute before /cmd starts
@run:with:/cmd        Execute together with /cmd (co-routine)
```

### Parallelism Modes
```
@parallel[/cmd1, /cmd2, /cmd3]    Execute all in parallel, wait for all
@sequential[/cmd1, /cmd2, /cmd3]  Execute in order, each waits for previous
@race[/cmd1, /cmd2]               Execute in parallel, use first to complete
@pipeline[/cmd1 | /cmd2 | /cmd3]  Chain outputs: cmd1.out → cmd2.in → cmd3.in
```

### Conditional Modes
```
@if:condition:/cmd              Execute /cmd only if condition true
@unless:condition:/cmd          Execute /cmd only if condition false
@retry:3:/cmd                   Retry /cmd up to 3 times on failure
@timeout:30s:/cmd               Fail if /cmd takes longer than 30s
@fallback:/cmd1:/cmd2           Try /cmd1, if fails use /cmd2
```

### Loop Modes
```
@loop:until:quality>=8:/cmd     Repeat /cmd until quality threshold
@loop:times:3:/cmd              Repeat /cmd exactly 3 times
@loop:while:errors>0:/cmd       Repeat while condition holds
@loop:for-each:items:/cmd       Iterate over collection
```

---

## Categorical Operators

The DSL implements four categorical operators with verified laws:

### Sequence (→) - Kleisli Composition
```
A → B → C
```
**Semantics**: Sequential execution. Output of A becomes input of B.
**Category**: Morphism composition in Kleisli category
**Quality**: `quality(A → B) = min(quality(A), quality(B))`

### Parallel (||) - Tensor Product
```
A || B || C
```
**Semantics**: Execute all simultaneously, aggregate results.
**Category**: Monoidal tensor product ⊗
**Quality**: `quality(A || B) = mean(quality(A), quality(B))`

### Tensor (⊗) - Resource Combination
```
A ⊗ B
```
**Semantics**: Combine resources/skills with quality degradation.
**Category**: [0,1]-enriched tensor product
**Quality**: `quality(A ⊗ B) ≤ min(quality(A), quality(B))`

### Kleisli (>=>) - Monadic Composition
```
A >=> B >=> C
```
**Semantics**: Composition with iterative refinement.
**Category**: Kleisli arrow composition
**Quality**: Improves monotonically with iterations

---

## Comonad Operations (W)

The `/context` command implements Comonad W for context extraction:

### Extract (ε) - Focus on Current
```
/context @mode:extract @focus:recent "task"
```
**Semantics**: Extract focused context from history.
**Category**: Counit ε: W(A) → A
**Quality**: `quality(extract(W)) ≤ quality(W)`

### Duplicate (δ) - Meta-Observation
```
/context @mode:duplicate "meta-observe"
```
**Semantics**: Create observation of the observation process.
**Category**: Comultiplication δ: W(A) → W(W(A))
**Quality**: `quality(duplicate(W)) = quality(W)`

### Extend - Context-Aware Transform
```
/context @mode:extend @transform:summarize "apply"
```
**Semantics**: Apply transformation with full context access.
**Category**: extend: (W(A) → B) → W(A) → W(B)
**Quality**: `quality(extend(f)(W)) = quality(f(W))`

### Comonad Laws (Enforced)
```
1. extract ∘ duplicate = id
2. fmap extract ∘ duplicate = id
3. duplicate ∘ duplicate = fmap duplicate ∘ duplicate
```

### Context Focus Targets
```
@focus:recent       Most recent N interactions
@focus:all          Entire available history
@focus:file         File-specific context
@focus:conversation Conversation flow context
```

### Context Command References
```
→ /context @mode:extract    Extract focused context
→ /context @mode:duplicate  Create meta-observation
→ /context @mode:extend     Context-aware transformation
→ /extract                  Alias for extract mode
→ /focus                    Alias for extract @depth:1
```

---

## Natural Transformation Operations (α)

The `/transform` command implements Natural Transformations α: F ⇒ G for strategy switching:

### Transform - Strategy Switch
```
/transform @from:zero-shot @to:chain-of-thought "task"
```
**Semantics**: Convert prompting strategy while preserving task semantics.
**Category**: Natural transformation α_A: F(A) → G(A)
**Quality**: `quality(α(x)) = transform_factor × quality(x)`

### Naturality Condition (Enforced)
```
For all f: A → B:
  α_B ∘ F(f) = G(f) ∘ α_A

Diagram:
      F(f)
  F(A) ──────▶ F(B)
    │            │
  α_A          α_B
    ▼            ▼
  G(A) ──────▶ G(B)
      G(f)
```

### Strategy Registry (Functors)

| Strategy | Functor | Quality Baseline | Token Cost |
|----------|---------|------------------|------------|
| `zero-shot` | F_ZS | 0.65 | Low |
| `few-shot` | F_FS | 0.78 | Medium |
| `chain-of-thought` | F_CoT | 0.85 | Medium-High |
| `tree-of-thought` | F_ToT | 0.88 | High |
| `meta-prompting` | F_Meta | 0.90 | Variable |
| `self-consistency` | F_SC | 0.82 | High |
| `react` | F_ReAct | 0.84 | Variable |

### Transformation Quality Matrix

Transformation factor (row → column):

| From \ To | ZS | FS | CoT | ToT | Meta |
|-----------|-----|-----|------|------|-------|
| **ZS** | 1.0 | 1.15 | 1.25 | 1.30 | 1.35 |
| **FS** | 0.85 | 1.0 | 1.10 | 1.15 | 1.20 |
| **CoT** | 0.75 | 0.90 | 1.0 | 1.05 | 1.10 |
| **ToT** | 0.70 | 0.85 | 0.95 | 1.0 | 1.05 |

### Transform Modes
```
@mode:transform    Apply transformation (default)
@mode:compare      Compare strategies side-by-side
@mode:analyze      Recommend optimal transformation
```

### Transform Command References
```
→ /transform @from:ZS @to:CoT    Zero-shot to Chain-of-Thought
→ /transform @mode:compare       Compare strategies
→ /transform @mode:analyze       Analyze optimal strategy
→ /cot                           Alias for @to:chain-of-thought
→ /tot                           Alias for @to:tree-of-thought
```

### Transformation Composition

Natural transformations compose vertically:
```
α: F ⇒ G
β: G ⇒ H
───────
β ∘ α: F ⇒ H
```

Example:
```bash
/chain [/transform @from:ZS @to:CoT → /transform @from:CoT @to:ToT] "task"
# Equivalent to:
/transform @from:zero-shot @to:tree-of-thought "task"
```

---

## Symbols Reference

| Symbol | Meaning | Usage |
|--------|---------|-------|
| `@` | Orchestration directive | `@run:now`, `@parallel[]` |
| `→` | Sequence composition | `A → B → C` |
| `\|\|` | Parallel composition | `A \|\| B \|\| C` |
| `⊗` | Tensor product | `A ⊗ B` |
| `>=>` | Kleisli composition | `A >=> B >=> C` |
| `⚡` | Skill invocation | `⚡ Skill: "name"` |
| `◆` | Quality gate | `◆ tests:pass` |
| `${}` | Variable reference | `${previous.output}` |
| `{}` | Template placeholder | `{task}`, `{context:expert}` |

---

## Command References

Reference other commands inline:
```
→ /debug              Invoke /debug command
→ /review {output}    Invoke /review with previous output
→ /compose [steps]    Invoke /compose with arguments
→ /chain "/a then /b" Invoke /chain with command sequence
```

---

## Skill References

Reference skills when specialized knowledge needed:
```
⚡ Skill: "categorical-meta-prompting"    Invoke categorical framework
⚡ Skill: "recursive-meta-prompting"      Invoke RMP skill
⚡ Skill: "categorical-property-testing"  Invoke testing skill
⚡ Skill: "security-analysis"             Invoke security skill
```

**Available Skills:**
- `categorical-meta-prompting` - Full categorical framework (F, M, W, [0,1])
- `categorical-property-testing` - Type-safe property verification
- `security-analysis` - Security vulnerability analysis
- `recursive-meta-prompting` - Iterative refinement loops

**Categorical Integration:**
The `categorical-meta-prompting` skill provides:
- **Functor F**: `analyze_complexity(task) → prompt_strategy`
- **Monad M**: `bind(prompt, improve) → refined_prompt` with quality
- **Comonad W**: `extract(observation) → focused_result`
- **Quality**: Track degradation via `quality(A ⊗ B) ≤ min(A, B)`

---

## Quality Gates

Checkpoints that must pass before continuing:
```
◆ quality >= 7        Must achieve quality score
◆ tests:pass          All tests must pass
◆ review:approved     Review must approve
◆ no:critical-issues  No critical issues found
◆ coverage >= 80      Coverage threshold
◆ staging:healthy     Environment health check
```

**Gate Operators:**
- `AND` - Both conditions must pass
- `OR` - Either condition passes
- `>=`, `<=`, `>`, `<` - Numeric comparison
- `:` - Boolean state check

---

## Context Passing

How to pass data between commands:
```
${previous.output}    Output from previous command
${cmd.result}         Result from specific command
${parallel.all}       Combined results from parallel execution
${loop.iteration}     Current loop iteration number
${quality.score}      Current quality assessment
${error}              Current error/failure info
${target}             Original target parameter
```

---

## Template Components

Dynamic template assembly (used by /build-prompt):
```
{context:expert}      Expert persona context
{context:teacher}     Teaching persona context
{context:reviewer}    Reviewer persona context
{context:debugger}    Debugger persona context

{mode:direct}         Direct answer mode
{mode:cot}            Chain-of-thought mode
{mode:multi}          Multi-perspective mode
{mode:iterative}      Iterative refinement mode

{format:prose}        Prose output format
{format:structured}   Structured with headers/lists
{format:code}         Code with comments
{format:checklist}    Actionable checklist

{quality:correctness} Correctness focus
{quality:completeness} Completeness focus
{quality:clarity}     Clarity focus
{quality:efficiency}  Efficiency focus
```

---

## Example Orchestration Patterns

### Pattern 1: Sequential with Gates
```
@orchestration
  @sequential[
    → /analyze {task}
    ◆ quality >= 6
    → /implement ${analysis}
    ◆ tests:pass
    → /review ${implementation}
    ◆ review:approved
  ]
@end
```

### Pattern 2: Parallel with Synthesis
```
@orchestration
  @parallel[
    → /review:correctness ${code}
    → /review:security ${code}
    → /review:performance ${code}
  ]
  → Synthesize ${parallel.all}
@end
```

### Pattern 3: Pipeline (Output Chaining)
```
@orchestration
  @pipeline[
    → /route {task}
    | → /build-prompt ${routed}
    | → /rmp ${prompt} 8
  ]
@end
```

### Pattern 4: Retry with Fallback
```
@orchestration
  @retry:3
    → /deploy ${artifact}
  @fallback:failed
    → /rollback ${previous_state}
    → /debug ${failure}
@end
```

### Pattern 5: Loop Until Quality
```
@orchestration
  @loop:until:quality>=8[
    → /rmp ${current} ${target_quality}
    ◆ quality >= ${target_quality}
  ]
@end
```

### Pattern 6: Conditional Execution
```
@orchestration
  @if:security_issues>0
    ⚡ Skill: "security-analysis"
    → /debug ${security_issues}

  @if:tests:failing
    → /meta-fix ${failures}
@end
```

---

## Full Example: Meta-Build Orchestration

```
@orchestration
  @sequential[

    ═══════ STAGE 1: ANALYSIS ═══════
    @run:now
    → /route {feature}
    ◆ routing:complete

    @run:now
    → /build-prompt "design ${feature}"

    ═══════ STAGE 2: PARALLEL DESIGN ═══════
    @parallel[
      → /template "architecture for ${feature}"
      → /template "data model for ${feature}"
      → /template "interface for ${feature}"
    ]
    ◆ all:templates:complete

    ═══════ STAGE 3: IMPLEMENTATION ═══════
    @run:now
    → /compose analyze plan implement

    ⚡ Skill: "categorical-property-testing"

    ◆ implementation:complete

    ═══════ STAGE 4: QUALITY ASSURANCE ═══════
    @parallel[
      → /meta-review ${implementation}
      → /meta-test ${implementation}
    ]
    ◆ quality >= 7 AND tests:pass

    ═══════ STAGE 5: REFINEMENT ═══════
    @loop:until:quality>=8[
      @if:quality<7
        → /rmp ${implementation} 8
      @if:tests:failing
        → /debug ${test_failures}
    ]
    ◆ quality >= 8

  ]
@end
```

---

## Agentic Execution Model

When meta-commands are executed by agents:

1. **Concurrency** - `@parallel` blocks spawn concurrent sub-agents via **Task tool**
2. **Coordination** - Quality gates synchronize agent progress
3. **Context** - `${}` variables share context between agents
4. **Skills** - `⚡` invocations access specialized capabilities
5. **Rollback** - `@fallback` enables recovery on failure

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                       │
│                                                              │
│  Interprets @orchestration blocks                            │
│  Spawns sub-agents for @parallel via Task tool               │
│  Enforces ◆ quality gates                                    │
│  Routes to ⚡ skills when needed                             │
│                                                              │
├──────────────────┬──────────────────┬───────────────────────┤
│   SUB-AGENT 1    │   SUB-AGENT 2    │   SUB-AGENT 3         │
│   (Task tool)    │   (Task tool)    │   (Task tool)         │
│   → /review      │   → /test        │   → /analyze           │
│                  │                  │                        │
│   [running]      │   [running]      │   [completed]          │
└──────────────────┴──────────────────┴───────────────────────┘
```

---

## CRITICAL: True Parallel Execution Protocol

**Discovery (2025-12-01)**: The `@parallel` and `||` operators achieve true concurrent execution
through the **Task tool**. Multiple Task invocations in a SINGLE message execute in parallel.

### Implementation Pattern

When encountering `@parallel[...]` or `||` operator:

```markdown
### Step 1: Parse parallel branches
Identify each independent item in the parallel block.

### Step 2: Map to Task tool calls
For each branch, create a Task invocation:
- subagent_type: Map command to agent (see table below)
- prompt: Include branch command + shared context
- description: "Parallel: [branch name]"

### Step 3: Execute ALL Task calls in ONE message
**CRITICAL**: All Task invocations MUST be in the same assistant message.
This triggers true parallel execution. Do NOT wait between calls.

### Step 4: Aggregate results
- Quality: mean(branch_qualities)
- Content: Merge with headers
- Status: ALL_COMPLETE when all return
```

### Command-to-Agent Mapping

| Command Pattern | Subagent Type |
|-----------------|---------------|
| `/review-*`, `/analyze-*` | `Explore` |
| `/debug`, `/fix` | `debug-detective` |
| `/research`, `/deep-*` | `deep-researcher` |
| `/test-*` | `test-engineer` |
| `/design`, `/architect` | `api-architect` |
| `/mercurio-*` | `mercurio-*` agents |
| General | `general-purpose` |

### Example: @parallel Block Execution

**Orchestration spec:**
```
@parallel[
  → Correctness review
  → Security review
  → Performance review
]
```

**Resolves to (in ONE message):**
```
Task(subagent_type="Explore", description="Parallel: Correctness",
     prompt="Review code for correctness: [context]")

Task(subagent_type="Explore", description="Parallel: Security",
     prompt="Review code for security: [context]")

Task(subagent_type="Explore", description="Parallel: Performance",
     prompt="Review code for performance: [context]")
```

### Quality Aggregation (Categorical Product)

```yaml
PARALLEL_CHECKPOINT:
  operator: "@parallel" | "||"
  branches:
    - {name: branch_1, quality: 0.85, status: COMPLETE}
    - {name: branch_2, quality: 0.82, status: COMPLETE}
    - {name: branch_3, quality: 0.88, status: COMPLETE}
  aggregate:
    quality: 0.85  # mean(0.85, 0.82, 0.88)
    status: ALL_COMPLETE
```

---

## Best Practices

1. **Start with /route** - Let routing determine optimal command path
2. **Use parallel for independent work** - Maximize throughput
3. **Gate before proceeding** - Fail fast with quality gates
4. **Include fallbacks** - Plan for failure with @fallback
5. **Invoke skills sparingly** - Only when specialized knowledge needed
6. **Keep stages visible** - Use ═══ separators for clarity
7. **Test incrementally** - Verify each step before continuing
