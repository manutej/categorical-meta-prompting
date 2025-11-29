---
name: guidance-grammars
description: Guidance library grammar-constrained generation with categorical structure. Use when implementing structured LLM outputs with grammar constraints, building template-based generation with guaranteed formats, creating type-safe prompt templates with interleaved computation, or applying categorical grammar theory to constrained generation.
---

# Guidance Grammar-Constrained Generation

Microsoft's Guidance library for grammar-constrained LLM generation with categorical structure.

## Installation

```bash
pip install guidance
```

## Core Concepts

Guidance maps to categorical structures:

- **Grammar**: Regular/context-free language as object
- **Generation**: Morphism `Grammar → TokenSequence`
- **Composition**: Sequential grammar combination
- **Select**: Coproduct (sum type) over alternatives
- **Capture**: Named binding creating product type

## Basic Usage

```python
import guidance
from guidance import models, gen, select, capture

# Load model
lm = models.OpenAI("gpt-4o")

# Simple constrained generation
@guidance
def greeting(lm):
    lm += "Hello, my name is "
    lm += gen(name="name", max_tokens=10, stop=".")
    lm += "."
    return lm

result = lm + greeting()
print(result["name"])
```

## Grammar Primitives

### gen() - Token Generation

```python
@guidance
def controlled_gen(lm, topic: str):
    lm += f"Write about {topic}:\n"
    lm += gen(
        name="content",
        max_tokens=100,
        stop=["\n\n", "---"],
        temperature=0.7
    )
    return lm
```

### select() - Coproduct/Choice

```python
@guidance  
def classify_sentiment(lm, text: str):
    lm += f"Text: {text}\n"
    lm += "Sentiment: "
    lm += select(
        ["positive", "negative", "neutral"],
        name="sentiment"
    )
    return lm

result = lm + classify_sentiment("I love this!")
assert result["sentiment"] in ["positive", "negative", "neutral"]
```

### Regex Constraints

```python
@guidance
def extract_email(lm, text: str):
    lm += f"Extract email from: {text}\n"
    lm += "Email: "
    lm += gen(
        name="email",
        regex=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    )
    return lm
```

## Compositional Patterns

### Sequential Composition

```python
@guidance
def qa_chain(lm, question: str):
    # First: generate reasoning
    lm += f"Question: {question}\n"
    lm += "Let me think step by step:\n"
    lm += gen(name="reasoning", max_tokens=200, stop="\n\n")
    
    # Second: generate answer (depends on reasoning)
    lm += "\n\nTherefore, the answer is: "
    lm += gen(name="answer", max_tokens=50, stop=".")
    lm += "."
    
    return lm
```

### Parallel Composition (Product)

```python
@guidance
def multi_analysis(lm, text: str):
    lm += f"Analyze: {text}\n\n"
    
    # Product of multiple extractions
    lm += "Summary: "
    lm += gen(name="summary", max_tokens=50, stop="\n")
    
    lm += "\nSentiment: "
    lm += select(["positive", "negative", "neutral"], name="sentiment")
    
    lm += "\nConfidence: "
    lm += select(["high", "medium", "low"], name="confidence")
    
    lm += "\nKeywords: "
    lm += gen(name="keywords", max_tokens=30, stop="\n")
    
    return lm

result = lm + multi_analysis("Great product, highly recommend!")
# result is product type: {summary, sentiment, confidence, keywords}
```

### Recursive Grammars

```python
@guidance
def json_value(lm):
    """Recursive JSON grammar."""
    lm += select([
        gen(regex=r'"[^"]*"'),  # string
        gen(regex=r'-?\d+(\.\d+)?'),  # number
        "true",
        "false",
        "null",
        json_array,  # recursive
        json_object  # recursive
    ], name="value")
    return lm

@guidance
def json_array(lm):
    lm += "["
    lm += optional(
        json_value() + 
        zero_or_more(", " + json_value())
    )
    lm += "]"
    return lm

@guidance
def json_object(lm):
    lm += "{"
    lm += optional(
        gen(regex=r'"[^"]*"') + ": " + json_value() +
        zero_or_more(", " + gen(regex=r'"[^"]*"') + ": " + json_value())
    )
    lm += "}"
    return lm
```

## Categorical Structure

### Grammar as Functor

```python
from typing import TypeVar, Generic, Callable

T = TypeVar('T')
U = TypeVar('U')

class GrammarFunctor(Generic[T]):
    """Grammar with functorial mapping over captured values."""
    
    def __init__(self, program: Callable):
        self.program = program
    
    def map(self, f: Callable[[T], U]) -> 'GrammarFunctor[U]':
        """Functor map: transform captured values."""
        @guidance
        def mapped(lm):
            lm = self.program(lm)
            # Transform result
            for key in lm.variables():
                lm[key] = f(lm[key])
            return lm
        return GrammarFunctor(mapped)

# Usage
sentiment_grammar = GrammarFunctor(classify_sentiment)
uppercase_sentiment = sentiment_grammar.map(str.upper)
```

### Natural Transformation: Grammar → Schema

```python
from pydantic import BaseModel
from typing import Literal

class SentimentResult(BaseModel):
    text: str
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float

def grammar_to_schema(grammar_result: dict) -> SentimentResult:
    """Natural transformation: Grammar captures → Pydantic model."""
    return SentimentResult(
        text=grammar_result.get("text", ""),
        sentiment=grammar_result["sentiment"],
        confidence={"high": 0.9, "medium": 0.7, "low": 0.5}[
            grammar_result.get("confidence", "medium")
        ]
    )
```

## Advanced Patterns

### Conditional Generation

```python
@guidance
def conditional_response(lm, query: str):
    lm += f"Query: {query}\n"
    lm += "Type: "
    lm += select(["question", "command", "statement"], name="type")
    
    # Conditional based on captured value
    if lm["type"] == "question":
        lm += "\nAnswer: "
        lm += gen(name="response", max_tokens=100)
    elif lm["type"] == "command":
        lm += "\nAction: "
        lm += gen(name="response", max_tokens=50)
    else:
        lm += "\nAcknowledgment: "
        lm += gen(name="response", max_tokens=30)
    
    return lm
```

### Iterative Refinement

```python
@guidance
def iterative_improve(lm, draft: str, iterations: int = 3):
    lm += f"Original: {draft}\n\n"
    
    current = draft
    for i in range(iterations):
        lm += f"Improvement {i+1}:\n"
        lm += "Issues: "
        lm += gen(name=f"issues_{i}", max_tokens=50, stop="\n")
        lm += "\nImproved: "
        lm += gen(name=f"improved_{i}", max_tokens=100, stop="\n\n")
        current = lm[f"improved_{i}"]
    
    return lm
```

### Tool Use Pattern

```python
@guidance
def tool_use(lm, query: str, tools: list[str]):
    lm += f"Query: {query}\n"
    lm += "Available tools: " + ", ".join(tools) + "\n\n"
    
    lm += "Selected tool: "
    lm += select(tools, name="tool")
    
    lm += "\nTool input: "
    lm += gen(name="tool_input", max_tokens=50, stop="\n")
    
    # Would execute tool here and continue
    lm += "\nTool output: [TOOL_RESULT]\n"
    
    lm += "Final response: "
    lm += gen(name="response", max_tokens=100)
    
    return lm
```

## Integration with fp-ts Concepts

```typescript
// TypeScript conceptual mapping
import * as O from 'fp-ts/Option';
import * as E from 'fp-ts/Either';

// Grammar result as Either (success/failure)
type GrammarResult<A> = E.Either<string, A>;

// Constrained generation as Kleisli arrow
type ConstrainedGen<A, B> = (a: A) => GrammarResult<B>;

// Compose constrained generations
const composeGrammar = <A, B, C>(
  f: ConstrainedGen<A, B>,
  g: ConstrainedGen<B, C>
): ConstrainedGen<A, C> =>
  (a: A) => E.chain(g)(f(a));
```

## Categorical Guarantees

Guidance provides these categorical properties:

1. **Grammar Closure**: Compositions produce valid grammars
2. **Type Safety**: Select constrains to specified options
3. **Determinism**: Same grammar + seed = same output
4. **Composability**: Grammars compose sequentially
5. **Capture Coherence**: Named captures form product type
