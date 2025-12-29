---
title: Quick Start
description: Run your first categorical meta-prompt in 5 minutes.
---

import { Steps, Aside, Code } from '@astrojs/starlight/components';

# Quick Start

Get up and running with categorical meta-prompting in 5 minutes.

## Prerequisites

- Python 3.9+
- An LLM API key (OpenAI, Anthropic, or compatible)

## Installation

<Steps>
1. **Clone the repository**

   ```bash
   git clone https://github.com/manutej/categorical-meta-prompting.git
   cd categorical-meta-prompting
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API key**

   ```bash
   export OPENAI_API_KEY="your-key-here"
   # or
   export ANTHROPIC_API_KEY="your-key-here"
   ```

</Steps>

## Your First Meta-Prompt

### Basic Usage

```python
from meta_prompting_engine.categorical import CategoricalEngine

# Initialize the engine
engine = CategoricalEngine()

# Run a simple task
result = engine.execute("implement a rate limiter in Python")

print(f"Quality: {result.quality}")
print(f"Output: {result.output}")
```

### With Quality Gate

```python
# Keep refining until quality reaches 0.85
result = engine.execute(
    task="implement rate limiter with sliding window",
    quality_threshold=0.85,
    max_iterations=5
)

# Check the quality scores
print(f"Final quality: {result.quality.aggregate}")
print(f"Iterations: {result.iterations}")
```

## Using Commands (Claude Code)

If you're using this with Claude Code, you get access to slash commands:

```bash
# Simple meta-prompt
/meta "implement rate limiter"

# With quality gate
/rmp @quality:0.85 "optimize algorithm"

# Chain commands
/chain [/analyze→/design→/implement] "build auth system"
```

<Aside type="tip" title="Pro Tip">
Start with `/meta` for simple tasks. Use `/rmp` when you need guaranteed quality. Use `/chain` for complex multi-step tasks.
</Aside>

## Understanding the Output

Every result includes:

```yaml
CHECKPOINT_RMP_3:
  command: /rmp
  iteration: 3
  quality:
    correctness: 0.92
    clarity: 0.88
    completeness: 0.85
    efficiency: 0.90
    aggregate: 0.89
  status: CONVERGED
```

| Field | Meaning |
|-------|---------|
| `correctness` | Does it solve the problem? (40% weight) |
| `clarity` | Is it understandable? (25% weight) |
| `completeness` | Are edge cases handled? (20% weight) |
| `efficiency` | Is it well-designed? (15% weight) |
| `aggregate` | Weighted average of all scores |

## What's Next?

- **[Core Concepts](/categorical-meta-prompting-oe/core-concepts/overview/)** — Understand the four pillars
- **[Commands Reference](/categorical-meta-prompting-oe/commands/overview/)** — All available commands
- **[Examples](/categorical-meta-prompting-oe/examples/game-of-24/)** — See real results
