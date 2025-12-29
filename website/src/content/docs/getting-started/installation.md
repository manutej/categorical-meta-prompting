---
title: Installation
description: Detailed installation guide for categorical meta-prompting.
---

import { Tabs, TabItem, Aside } from '@astrojs/starlight/components';

# Installation

## Requirements

- **Python**: 3.9 or higher
- **LLM API**: OpenAI, Anthropic, or compatible provider
- **Optional**: Claude Code for slash commands

## Install from Source

```bash
# Clone the repository
git clone https://github.com/manutej/categorical-meta-prompting.git
cd categorical-meta-prompting

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### API Keys

<Tabs>
  <TabItem label="OpenAI">
    ```bash
    export OPENAI_API_KEY="sk-..."
    ```
  </TabItem>
  <TabItem label="Anthropic">
    ```bash
    export ANTHROPIC_API_KEY="sk-ant-..."
    ```
  </TabItem>
  <TabItem label=".env file">
    Create a `.env` file in the project root:
    ```
    OPENAI_API_KEY=sk-...
    ANTHROPIC_API_KEY=sk-ant-...
    ```
  </TabItem>
</Tabs>

### Default Settings

Create `config.yaml` for custom defaults:

```yaml
quality:
  default_threshold: 0.8
  max_iterations: 5

engine:
  model: "gpt-4"  # or "claude-3-opus"
  temperature: 0.7

logging:
  level: INFO
  checkpoints: true
```

## Claude Code Integration

If using with Claude Code, install as a skill:

```bash
# Copy skills to Claude directory
cp -r .claude/skills/* ~/.claude/skills/
cp -r .claude/commands/* ~/.claude/commands/
```

Then in Claude Code:
```bash
/meta "test the installation"
```

<Aside type="caution">
Make sure your Claude Code version supports custom skills. Check with `/help` in Claude Code.
</Aside>

## Verify Installation

```python
from meta_prompting_engine.categorical import CategoricalEngine

engine = CategoricalEngine()
result = engine.health_check()

print(f"Status: {result.status}")
print(f"Version: {result.version}")
```

Expected output:
```
Status: healthy
Version: 2.1.0
```

## Troubleshooting

### "Module not found" error

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### API key issues

```bash
# Verify key is set
echo $OPENAI_API_KEY

# Test API connection
python -c "from meta_prompting_engine import test_connection; test_connection()"
```

### Permission errors on Windows

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Next Steps

- **[Quick Start](/categorical-meta-prompting-oe/getting-started/quickstart/)** — Run your first meta-prompt
- **[Core Concepts](/categorical-meta-prompting-oe/core-concepts/overview/)** — Understand how it works
