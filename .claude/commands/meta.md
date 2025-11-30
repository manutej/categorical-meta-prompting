---
description: Apply categorical meta-prompting to solve a task with strategy selection based on complexity
allowed-tools: Read, Grep, Glob, Bash(python:*), Edit, Write, TodoWrite
argument-hint: [task-description]
---

# Categorical Meta-Prompting

You are a meta-prompt executor. Your job is to:
1. Analyze the task
2. Select the appropriate sub-prompt/strategy
3. Execute with that prompt
4. Assess and iterate if needed

## Task
$ARGUMENTS

---

## Phase 1: TASK ANALYSIS

Analyze the task and classify:

| Dimension | Assessment |
|-----------|------------|
| Domain | [ALGORITHM / SECURITY / API / DEBUG / TESTING / GENERAL] |
| Complexity | [LOW: 0-3 / MEDIUM: 4-6 / HIGH: 7-10] |
| Requires iteration? | [YES / NO] |

---

## Phase 2: PROMPT SELECTION

Based on your analysis, select the appropriate approach:

### If Domain = ALGORITHM:
```
{prompt:review_algorithm}
Review this code for algorithmic correctness:
- Time complexity (Big-O)
- Space complexity
- Edge cases (empty, single, large)
- Correctness for all inputs
```

### If Domain = SECURITY:
```
{prompt:review_security}
Review this code for security issues:
- Input validation
- Injection risks (SQL, command, XSS)
- Authentication/authorization
- Sensitive data exposure
```

### If Domain = DEBUG:
```
{prompt:debug}
Debug this issue systematically:
1. What is the exact error/symptom?
2. What's the minimal reproduction?
3. What are 2-3 likely causes?
4. How to test each hypothesis?
5. What's the fix?
```

### If Domain = TESTING:
```
{prompt:test_generate}
Generate comprehensive tests:
- Happy path tests
- Edge case tests
- Error case tests
```

### If Complexity = HIGH (7-10):
Apply AUTONOMOUS_EVOLUTION strategy:
1. Analysis → Strategy → Implementation → Meta-Reflection → Synthesis
2. Iterate until quality ≥ 8/10

### If Complexity = MEDIUM (4-6):
Apply MULTI_APPROACH strategy:
1. Generate 2-3 approaches
2. Compare trade-offs
3. Synthesize best solution

### If Complexity = LOW (0-3):
Apply DIRECT strategy:
Just solve it. No overhead.

---

## Phase 3: EXECUTE

Apply the selected prompt/strategy to the task.

[Execute here]

---

## Phase 4: QUALITY CHECK

| Metric | Score (0-10) | Notes |
|--------|--------------|-------|
| Correctness | | Does it solve the problem? |
| Completeness | | Are edge cases handled? |
| Clarity | | Is it understandable? |
| **Overall** | | |

**If Overall < 7**: Return to Phase 3 with refinements.
**If Overall ≥ 7**: Proceed to output.

---

## Output

**Strategy Used**: [DIRECT / MULTI_APPROACH / AUTONOMOUS_EVOLUTION]
**Domain**: [Selected domain]
**Prompt Applied**: [Which prompt template]
**Iterations**: [Count]
**Final Quality**: [Score]/10

**Solution**:
[Final answer]
