---
description: Select the best prompt template from the registry for a given problem
allowed-tools: Bash(python:*), Read
argument-hint: [problem-description]
---

# Dynamic Prompt Selection

## Problem Description
$ARGUMENTS

## Registry Query

!`python3 /home/user/categorical-meta-prompting/extensions/dynamic-prompt-registry/cli.py select "$ARGUMENTS" --explain 2>&1`

## Apply Selected Template

Based on the selection above, apply the template to solve the problem.
If no suitable prompt was found, use your best judgment to approach the problem.
