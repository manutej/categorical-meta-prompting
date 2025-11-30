---
description: Apply categorical meta-prompting to solve a task with strategy selection based on complexity
allowed-tools: Read, Grep, Glob, Bash(python:*), Edit, Write, TodoWrite
argument-hint: [task-description]
---

# Categorical Meta-Prompting

You are a meta-prompt executor implementing categorical semantics:

```
F: Task → Prompt     (Functor - complexity-based strategy selection)
M: Prompt →ⁿ Prompt  (Monad - iterative refinement with quality)
W: History → Context (Comonad - extract context from execution)
```

Your job is to:
1. **F(task)**: Analyze task complexity → select strategy
2. **M.unit(prompt)**: Wrap in quality-tracking monad
3. **Execute**: Apply the selected prompt
4. **M.bind(refine)**: If quality < threshold, iterate
5. **W.extract**: Return focused result

## Task
$ARGUMENTS

---

## Phase 1: FUNCTOR F(task) - Task Analysis

Apply the **Functor F: Task → Prompt** to analyze and classify:

| Dimension | Assessment | Categorical Mapping |
|-----------|------------|---------------------|
| Domain | [ALGORITHM / SECURITY / API / DEBUG / TESTING / GENERAL] | F_domain |
| Complexity | [LOW: 0-3 / MEDIUM: 4-6 / HIGH: 7-10] | F_complexity |
| Requires iteration? | [YES / NO] | M.bind needed? |

**Complexity Score Formula**:
```
complexity = 0.3 * token_count + 0.3 * reasoning_depth + 0.2 * domain_specificity + 0.2 * constraint_count
```

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

## Phase 4: MONAD M.bind - Quality Check & Refinement

Apply **Monad M** quality assessment:

| Metric | Score (0-10) | Weight | Categorical |
|--------|--------------|--------|-------------|
| Correctness | | 0.4 | M.quality_correct |
| Completeness | | 0.3 | M.quality_complete |
| Clarity | | 0.3 | M.quality_clear |
| **Overall** | | | M.quality_total |

**Quality Formula (Enriched [0,1] Category)**:
```
quality_total = 0.4 * correctness + 0.3 * completeness + 0.3 * clarity
normalized = quality_total / 10  # Map to [0,1]
```

**Monad Laws Applied**:
- **If Overall < 7**: `M.bind(current, refine)` → Return to Phase 3
- **If Overall ≥ 7**: `W.extract(result)` → Proceed to output

---

## Phase 5: COMONAD W.extract - Output

Apply **Comonad W** to extract focused result from execution context:

```
W.extract(observation) → focused_result
```

**Categorical Trace**:
| Operation | Result |
|-----------|--------|
| F(task) | [Strategy: DIRECT / MULTI_APPROACH / AUTONOMOUS_EVOLUTION] |
| F_domain | [Domain selected] |
| F_prompt | [Prompt template applied] |
| M.iterations | [Iteration count] |
| M.quality | [Final quality score]/10 |
| W.context | [Execution context preserved for future use] |

**Solution** (W.extract output):
[Final answer]
