---
description: Chain multiple slash commands together, passing output as input to next command
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [/cmd1 then /cmd2 then /cmd3] [initial-input]
---

# Prompt Chain Executor

Execute a sequence of slash commands, passing each output as context to the next.

## Chain Specification
$ARGUMENTS

---

## How Chaining Works

```
/cmd1 [input]
    ↓ output becomes context
/cmd2 [context from cmd1]
    ↓ output becomes context
/cmd3 [context from cmd2]
    ↓
Final Result
```

Each command is a prompt. Chaining them = prompts calling prompts.

---

## Parse Chain

From your input, extracting:

| Position | Command | Input |
|----------|---------|-------|
| 1 | [first command] | [initial input] |
| 2 | [second command] | [output from 1] |
| 3 | [third command] | [output from 2] |
| ... | ... | ... |

---

## Execute Chain

### Stage 1: [Command 1]
```
Input: [initial input]
Executing: /[command1]
```

[Execute first command here]

**Output from Stage 1:**
[capture output]

---

### Stage 2: [Command 2]
```
Input: [output from stage 1]
Executing: /[command2]
```

[Execute second command with context from first]

**Output from Stage 2:**
[capture output]

---

### Stage 3: [Command 3] (if specified)
```
Input: [output from stage 2]
Executing: /[command3]
```

[Execute third command with context from second]

**Output from Stage 3:**
[capture output]

---

## Chain Summary

| Stage | Command | Quality | Key Output |
|-------|---------|---------|------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

**Chain**: /cmd1 → /cmd2 → /cmd3
**Total Stages**: N
**Final Result**: [last stage output]

---

## Example Chains

```
/chain "/debug then /review" "TypeError in auth.py line 42"
→ First debugs the error, then reviews the fix

/chain "/build-prompt then /rmp" "implement rate limiter"
→ First constructs optimal prompt, then iteratively refines

/chain "/analyze then /plan then /implement" "add caching layer"
→ Full development pipeline
```
