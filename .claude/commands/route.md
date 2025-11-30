---
description: Meta-prompt that chains to domain-specific prompts based on task analysis
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [task-description]
---

# Dynamic Prompt Router

This meta-prompt analyzes your task and routes to the appropriate specialized prompt.

## Task
$ARGUMENTS

---

## Step 1: Analyze & Route

Based on the task, I will select and invoke the appropriate specialized command:

| If task involves... | Route to | Why |
|---------------------|----------|-----|
| Fixing bugs, errors, crashes | → `/debug` | Systematic debugging protocol |
| Reviewing code quality | → `/review` | Domain-aware code review |
| Complex multi-step work | → `/compose analyze plan implement test` | Pipeline composition |
| Iterative refinement needed | → `/rmp` | Recursive meta-prompting loop |
| Simple direct request | → Direct execution | No routing overhead |

---

## Step 2: Dynamic Template Formation

For this specific task, I'm constructing an intermediary prompt:

```
Task Type: [detected type]
Complexity: [low/medium/high]
Domain: [detected domain]

Constructed Template:
┌────────────────────────────────────────┐
│ {system_context}                       │
│ {domain_specific_instructions}         │
│ {task_description}                     │
│ {output_format}                        │
│ {quality_criteria}                     │
└────────────────────────────────────────┘
```

Where:
- `{system_context}` = Role and capabilities for this domain
- `{domain_specific_instructions}` = Pulled from appropriate /command
- `{task_description}` = Your original task: "$ARGUMENTS"
- `{output_format}` = Expected structure of response
- `{quality_criteria}` = How to assess the result

---

## Step 3: Execute Routed Command

[Now executing the selected command with the constructed template]

---

## Step 4: Result

**Routing Decision**: [which command was selected]
**Template Used**: [constructed template summary]
**Output**: [result from the routed command]
