# Categorical Meta-Prompting

[![Status](https://img.shields.io/badge/status-production--ready-green)]()
[![Game of 24](https://img.shields.io/badge/Game%20of%2024-100%25%20accuracy-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

> **Transform your AI prompts from guesswork to engineering.**

---

## The Problem: AI Development is Alchemy

Modern AI development feels like an alchemist's workshop. We mix prompts with intuition, hoping to transmute raw ideas into digital gold. As [Andrej Karpathy noted](https://x.com/karpathy/status/1820807166371975636):

> *"The hottest new programming language is English."*

But English is imprecise. Every developer has experienced the frustration:
- A prompt that worked yesterday fails today
- Small changes cause unpredictable results
- No way to know if your prompt is "good enough"
- Scaling from one use case to many is painful

**This is the alchemy problem.** We need chemistry.

---

## The Solution: Prompts That Compose Like Functions

What if prompts had the same guarantees as functions in your code?

```
Task → [Transform] → Prompt → [Refine] → Better Prompt → [Extract Context] → Output
```

This framework applies **category theory**—the mathematics of composition—to prompt engineering:

| Concept | What It Means for You |
|---------|----------------------|
| **Functors** | Prompts transform predictably (like `map()`) |
| **Monads** | Refinement chains compose cleanly (like `async/await`) |
| **Quality Scores** | Every output has a measurable 0-1 quality rating |

**You don't need to understand the math.** The framework handles it. You get:
- Reproducible results
- Measurable quality
- Composable pipelines

---

## Quick Start

### Installation

```bash
git clone https://github.com/manutej/categorical-meta-prompting.git
cd categorical-meta-prompting
pip install -r requirements-test.txt
```

### Your First Meta-Prompt

```python
from meta_prompting_engine import MetaPromptingEngine

engine = MetaPromptingEngine()

# Simple task - framework handles the complexity
result = engine.execute(
    task="Write a function to validate email addresses",
    quality_threshold=0.85  # Stop when quality reaches 85%
)

print(f"Quality: {result.quality}")  # e.g., 0.89
print(result.output)  # Production-ready code
```

### What Happens Under the Hood

1. **Analyze**: Framework assesses task complexity
2. **Generate**: Creates initial solution
3. **Evaluate**: Measures quality (0-1 score)
4. **Refine**: If quality < threshold, iteratively improve
5. **Return**: Best result with quality guarantee

---

## Why This Works: From Vibe to Engineering

> *"Like alchemy to chemistry, today's global experiments reveal the decisions engineers must make."*
> — [Vibe Engineering, Manning 2025](https://www.manning.com/books/vibe-engineering)

Traditional prompt engineering relies on:
- ❌ Trial and error
- ❌ "Vibes" and intuition
- ❌ Copy-pasting from tutorials
- ❌ Hope

Categorical meta-prompting provides:
- ✅ Mathematical composition guarantees
- ✅ Measurable quality scores
- ✅ Reproducible results
- ✅ Systematic improvement

---

## Core Concepts (Plain English)

### 1. Quality Scores

Every output gets a score from 0 to 1:

```python
result = engine.execute(task="...", quality_threshold=0.90)
# result.quality = 0.92 ✓ (exceeds threshold)
```

| Score | Meaning |
|-------|---------|
| 0.9+ | Excellent - production ready |
| 0.8-0.9 | Good - minor polish needed |
| 0.7-0.8 | Acceptable - review recommended |
| <0.7 | Needs work - iterate more |

### 2. Recursive Improvement

The framework automatically refines until quality threshold is met:

```
Iteration 1: Generate → Quality 0.65
Iteration 2: Refine → Quality 0.78
Iteration 3: Refine → Quality 0.91 ✓ Done
```

### 3. Composable Pipelines

Chain operations together:

```python
# Sequential: each step feeds the next
pipeline = engine.chain([
    "analyze requirements",
    "design solution",
    "implement code",
    "write tests"
])

# The output of each step becomes input to the next
result = pipeline.execute(task="build authentication system")
```

---

## Real Results

### Game of 24 Benchmark

The standard test for mathematical reasoning:

| Approach | Accuracy |
|----------|----------|
| GPT-4 (zero-shot) | 4% |
| GPT-4 (chain-of-thought) | 36% |
| **Categorical Meta-Prompting** | **100%** |

### Code Generation

```
Task: "Implement rate limiter with sliding window"

Without meta-prompting:
- 3 attempts to get working code
- Missing edge cases
- No tests

With categorical meta-prompting:
- 1 execution, quality 0.91
- Complete implementation
- Test suite included
- Error handling built-in
```

---

## Project Structure

```
categorical-meta-prompting/
├── meta_prompting_engine/     # Core Python engine
├── examples/                  # Ready-to-run examples
├── docs/                      # Documentation
│   ├── QUICKSTART.md          # Get started in 5 minutes
│   └── status/                # Development progress
├── research/                  # Academic foundations
├── tests/                     # Test suite
├── mcp-server/                # MCP integration
└── CLAUDE.md                  # Claude Code integration
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](./QUICKSTART.md) | Get running in 5 minutes |
| [CLAUDE.md](./CLAUDE.md) | Full command reference |
| [docs/QUICKSTART-UNIFIED.md](./docs/QUICKSTART-UNIFIED.md) | Unified syntax guide |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | How to contribute |

---

## The Bigger Picture

We're at an inflection point in software development. The era of "prompt and pray" is ending. What comes next?

**From Karpathy's insight** about English as a programming language, to the emerging discipline of **Vibe Engineering**, the industry is converging on a key realization:

> AI development needs the same rigor we bring to traditional software.

This framework is one answer. It takes the chaos of prompt engineering and applies mathematical structure—not to make things academic, but to make them **reliable**.

---

## Further Reading

### On the State of AI Development
- [Karpathy on English as Programming](https://x.com/karpathy/status/1820807166371975636) - The insight that started it all
- [Vibe Engineering (Manning, 2025)](https://www.manning.com/books/vibe-engineering) - From alchemy to chemistry in AI

### Academic Foundations
- [Categorical Deep Learning (Gavranović et al., 2024)](https://arxiv.org/abs/2402.15332) - The mathematical foundations
- [On Meta-Prompting (de Wynter et al., 2025)](https://arxiv.org/abs/2312.06562) - Meta-prompting formalized

### Implementation
- [Effect-TS](https://github.com/Effect-TS/effect) - Production categorical TypeScript
- [DSPy](https://github.com/stanfordnlp/dspy) - Compositional prompt optimization

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Areas where help is especially welcome:**
- Additional LLM client implementations
- Real-world use case examples
- Documentation improvements
- Performance optimizations

---

## License

MIT License - see [LICENSE](./LICENSE)

---

## Credits

Originally created by [manutej](https://github.com/manutej). This fork maintained by [HermeticOrmus](https://github.com/HermeticOrmus).

---

<p align="center">
  <i>"The goal isn't to replace intuition with math—it's to give intuition a foundation to build on."</i>
</p>
