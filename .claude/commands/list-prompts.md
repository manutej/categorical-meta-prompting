---
description: List available prompt templates from the registry with quality scores
allowed-tools: Bash(python:*), Read
argument-hint: [domain-filter]
---

# Prompt Registry Listing

## Filter
$ARGUMENTS

## Registry Contents

!`python3 /home/user/categorical-meta-prompting/extensions/dynamic-prompt-registry/cli.py list $ARGUMENTS 2>&1`

## Usage

To use a template:

1. **Select for problem**: `/select-prompt [problem description]`
2. **Apply meta-prompting**: `/meta [task description]`
3. **Debug systematically**: `/debug [error or symptom]`
4. **Run RMP loop**: `/rmp [task] [quality-threshold]`
