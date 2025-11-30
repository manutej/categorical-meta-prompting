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
│                    OBJECT COMMAND LAYER                         │
│   /debug  /review  /compose  /rmp  /select-prompt  /list-prompts│
│                                                                 │
│   These commands DO THE WORK on specific tasks                  │
├─────────────────────────────────────────────────────────────────┤
│                    SKILL LAYER                                  │
│   ⚡ categorical-property-testing                                │
│   ⚡ security-analysis                                           │
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

1. **Concurrency** - `@parallel` blocks spawn concurrent sub-agents
2. **Coordination** - Quality gates synchronize agent progress
3. **Context** - `${}` variables share context between agents
4. **Skills** - `⚡` invocations access specialized capabilities
5. **Rollback** - `@fallback` enables recovery on failure

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                       │
│                                                              │
│  Interprets @orchestration blocks                            │
│  Spawns sub-agents for @parallel                             │
│  Enforces ◆ quality gates                                    │
│  Routes to ⚡ skills when needed                             │
│                                                              │
├──────────────────┬──────────────────┬───────────────────────┤
│   SUB-AGENT 1    │   SUB-AGENT 2    │   SUB-AGENT 3         │
│                  │                  │                        │
│   → /review      │   → /test        │   → /analyze           │
│                  │                  │                        │
│   [running]      │   [running]      │   [completed]          │
└──────────────────┴──────────────────┴───────────────────────┘
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
