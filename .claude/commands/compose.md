---
description: Compose a multi-step prompt pipeline from registry templates
allowed-tools: Read, Bash(*), Write, Edit, Grep, Glob
argument-hint: [step1] [step2] [step3...]
---

# Prompt Pipeline Composition

Execute a sequence of prompts, passing context between them.

## Requested Pipeline
$ARGUMENTS

---

## Available Prompt Templates

### {prompt:analyze}
```
Analyze this problem:
1. What is the core challenge?
2. What are the inputs and expected outputs?
3. What constraints exist?
4. What approaches might work?
```

### {prompt:plan}
```
Create an implementation plan:
1. Break into discrete steps
2. Identify dependencies between steps
3. Note potential risks at each step
4. Estimate complexity of each step
```

### {prompt:implement}
```
Implement the solution:
1. Follow the plan step by step
2. Write clean, documented code
3. Handle edge cases
4. Test as you go
```

### {prompt:review}
```
Review for issues:
1. Correctness: Does it solve the problem?
2. Edge cases: Are boundaries handled?
3. Performance: Is it efficient enough?
4. Maintainability: Is it readable?
```

### {prompt:test}
```
Verify correctness:
1. Test happy path
2. Test edge cases
3. Test error conditions
4. Confirm all requirements met
```

### {prompt:refine}
```
Improve based on feedback:
1. What issues were identified?
2. What's the minimal fix for each?
3. Apply fixes
4. Re-verify
```

### {prompt:document}
```
Document the solution:
1. What problem was solved?
2. How does the solution work?
3. How to use it?
4. Any known limitations?
```

---

## Pipeline Execution

I will now execute each step in sequence, carrying context forward:

### Step 1: Parse Pipeline
Requested: `$ARGUMENTS`

### Step 2: Execute Each Stage

For each step in the pipeline:

```
┌─────────────────────────────────────┐
│ Stage N: {prompt:step_name}         │
├─────────────────────────────────────┤
│ Input: [context from previous]      │
│ Executing template...               │
│ Output: [result]                    │
│ Quality: [0-10]                     │
└─────────────────────────────────────┘
          ↓ (pass context)
```

### Step 3: Quality Gate

After each stage, check:
- If quality ≥ 7: Continue to next stage
- If quality < 7: Apply {prompt:refine} before continuing

---

## Execute Now

[Begin pipeline execution with the requested steps]

---

## Pipeline Summary

| Stage | Prompt | Quality | Notes |
|-------|--------|---------|-------|
| 1 | | | |
| 2 | | | |
| ... | | | |

**Pipeline**: [step1] >> [step2] >> [step3]
**Total Stages**: N
**Min Quality**: X/10
**Final Output**: [result]
