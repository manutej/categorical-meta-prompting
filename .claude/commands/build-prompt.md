---
description: Dynamically construct a prompt from template components for a specific task
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob
argument-hint: [task-description]
---

# Dynamic Prompt Builder

Construct an optimized prompt by assembling template components.

## Task
$ARGUMENTS

---

## Template Components Library

### System Contexts
```
{context:expert} = "You are an expert in this domain with deep knowledge."
{context:teacher} = "You are a patient teacher explaining step by step."
{context:reviewer} = "You are a critical reviewer looking for issues."
{context:debugger} = "You are a systematic debugger isolating problems."
```

### Reasoning Modes
```
{mode:direct} = "Provide a direct, concise answer."
{mode:cot} = "Think step by step before answering."
{mode:multi} = "Consider multiple approaches, then synthesize."
{mode:iterative} = "Attempt, assess, refine until quality threshold met."
```

### Output Formats
```
{format:prose} = "Write in clear paragraphs."
{format:structured} = "Use headers, lists, and tables."
{format:code} = "Provide working code with comments."
{format:checklist} = "Provide actionable checklist items."
```

### Quality Criteria
```
{quality:correctness} = "Must solve the problem correctly."
{quality:completeness} = "Must handle edge cases."
{quality:clarity} = "Must be understandable."
{quality:efficiency} = "Must be reasonably efficient."
```

---

## Step 1: Analyze Task Requirements

| Aspect | Detection | Selected Component |
|--------|-----------|-------------------|
| Domain expertise needed? | | {context:?} |
| Reasoning complexity? | | {mode:?} |
| Output type expected? | | {format:?} |
| Key quality criteria? | | {quality:?} |

---

## Step 2: Assemble Template

Based on analysis, constructing:

```
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM: {selected_context}                                  │
│                                                             │
│ APPROACH: {selected_mode}                                   │
│                                                             │
│ TASK: $ARGUMENTS                                            │
│                                                             │
│ FORMAT: {selected_format}                                   │
│                                                             │
│ QUALITY: {selected_quality}                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 3: Execute Constructed Prompt

[Executing with the assembled template]

---

## Step 4: Assess Result

| Quality Dimension | Score (1-10) | Notes |
|-------------------|--------------|-------|
| Correctness | | |
| Completeness | | |
| Clarity | | |
| Format adherence | | |

**If score < 7**: Reconstruct with {mode:iterative} and retry.

---

## Final Output

**Template Used**:
- Context: {selected}
- Mode: {selected}
- Format: {selected}
- Quality: {selected}

**Result**:
[output]
