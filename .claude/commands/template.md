---
description: Build a prompt template step by step with visible intermediate states
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob
argument-hint: [goal-description]
---

# Template Builder with Visible Steps

Construct a prompt template incrementally, showing each intermediate state.

## Goal
$ARGUMENTS

---

## Intermediate Step 1: Base Template

Starting with empty template:
```
Template v0:
┌────────────────────────────────┐
│                                │
└────────────────────────────────┘
```

---

## Intermediate Step 2: Add Role

What role/persona is needed for this goal?

```
Template v1:
┌────────────────────────────────┐
│ You are {role}.                │
│                                │
└────────────────────────────────┘
```

Selected role: [based on goal analysis]

---

## Intermediate Step 3: Add Context

What background context is relevant?

```
Template v2:
┌────────────────────────────────┐
│ You are {role}.                │
│                                │
│ Context:                       │
│ {relevant_context}             │
│                                │
└────────────────────────────────┘
```

Added context: [based on goal]

---

## Intermediate Step 4: Add Task Specification

What exactly needs to be done?

```
Template v3:
┌────────────────────────────────┐
│ You are {role}.                │
│                                │
│ Context:                       │
│ {relevant_context}             │
│                                │
│ Task:                          │
│ {task_specification}           │
│                                │
└────────────────────────────────┘
```

Task spec: [derived from goal]

---

## Intermediate Step 5: Add Constraints

What constraints or requirements apply?

```
Template v4:
┌────────────────────────────────┐
│ You are {role}.                │
│                                │
│ Context:                       │
│ {relevant_context}             │
│                                │
│ Task:                          │
│ {task_specification}           │
│                                │
│ Constraints:                   │
│ - {constraint_1}               │
│ - {constraint_2}               │
│                                │
└────────────────────────────────┘
```

Constraints: [based on goal analysis]

---

## Intermediate Step 6: Add Output Format

What format should the response take?

```
Template v5:
┌────────────────────────────────┐
│ You are {role}.                │
│                                │
│ Context:                       │
│ {relevant_context}             │
│                                │
│ Task:                          │
│ {task_specification}           │
│                                │
│ Constraints:                   │
│ - {constraint_1}               │
│ - {constraint_2}               │
│                                │
│ Output Format:                 │
│ {expected_format}              │
└────────────────────────────────┘
```

Format: [appropriate for goal]

---

## Final Template

```
┌────────────────────────────────────────────────────────────┐
│ [Complete template with all placeholders filled]           │
└────────────────────────────────────────────────────────────┘
```

---

## Template Metadata

| Component | Value | Reasoning |
|-----------|-------|-----------|
| Role | | |
| Context | | |
| Task | | |
| Constraints | | |
| Format | | |

---

## Execute Template

Now executing the constructed template against the original goal...

[Result]
