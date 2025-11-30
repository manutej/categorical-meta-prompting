---
description: Meta-prompt that chains to domain-specific prompts based on task analysis
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [task-description]
---

# Dynamic Prompt Router

This meta-prompt implements **Functor F: Task → Prompt** to route tasks to specialized prompts.

```
F_route: Task → Domain → Prompt
       = analyze_task ∘ select_domain ∘ generate_prompt
```

**Functor Laws Preserved**:
- Identity: `F(id_task) = id_prompt` (trivial tasks route to direct execution)
- Composition: `F(g ∘ f) = F(g) ∘ F(f)` (composed tasks route to pipeline)

## Task
$ARGUMENTS

---

## Step 1: Functor F_analyze - Domain Classification

Apply **F_analyze: Task → Domain**:

| Pattern Detected | Domain | Route to | Categorical Justification |
|------------------|--------|----------|---------------------------|
| Bug, error, crash, fix | DEBUG | → `/debug` | F_debug preserves error structure |
| Review, quality, check | REVIEW | → `/review` | F_review preserves code structure |
| Build, implement, create | BUILD | → `/compose` | F_build via pipeline composition |
| Improve, refine, optimize | REFINE | → `/rmp` | M.bind for iterative improvement |
| Test, verify, validate | TEST | → `/meta-test` | Property verification |
| Simple, direct | SIMPLE | → Direct | F(id) = id |

---

## Step 2: Functor F_template - Dynamic Template Formation

Apply **F_template: Domain → Prompt** to construct the intermediary prompt:

```
F_template(domain) = {context} + {instructions} + {task} + {format} + {quality}
```

| Component | Categorical Role | Value |
|-----------|------------------|-------|
| `{context}` | F.context | Role and capabilities for domain |
| `{instructions}` | F.morphism | Domain-specific transformation |
| `{task}` | F.object | "$ARGUMENTS" |
| `{format}` | F.codomain | Expected output structure |
| `{quality}` | M.quality | Assessment criteria |

**Composed Template** (F ∘ G):
```
┌────────────────────────────────────────┐
│ {context}: [Expert/Teacher/Debugger]   │
│ {instructions}: [From routed /command] │
│ {task}: "$ARGUMENTS"                   │
│ {format}: [Code/Prose/Structured]      │
│ {quality}: [Correctness/Completeness]  │
└────────────────────────────────────────┘
```

---

## Step 3: Execute via Composition

Execute the routed command using categorical composition:

```
result = (F_route ∘ F_template ∘ Execute)(task)
```

[Now executing the selected command]

---

## Step 4: Comonad W.extract - Result

Apply **W.extract** to focus on the essential result:

| Trace | Value |
|-------|-------|
| F_route.domain | [Domain selected] |
| F_route.command | [Command routed to] |
| F_template.components | [Template summary] |
| Execute.quality | [Quality score if applicable] |

**Output** (W.extract):
[Result from the routed command]
