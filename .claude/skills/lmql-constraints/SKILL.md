---
name: lmql-constraints
description: LMQL constraint-guided generation DSL for type-safe prompting with grammar constraints and logical conditions. Use when building structured LLM outputs with guaranteed format compliance, implementing constrained decoding with logical operators, creating type-safe prompt templates, or combining neural generation with symbolic constraints for reliable AI outputs.
---

# LMQL Constraint-Guided Generation

LMQL (Language Model Query Language) from ETH Zurich provides categorical constraint-based generation for LLMs.

## Installation

```bash
pip install lmql
```

## Core Concepts

LMQL maps to categorical structures:

- **Query**: Morphism `Context → ConstrainedOutput`
- **Constraints**: Subobject classifier restricting output space
- **Variables**: Typed placeholders forming product types
- **Distributions**: Probability monad over token sequences

## Basic Queries

### Simple Constrained Generation

```python
import lmql

@lmql.query
def greet(name):
    '''lmql
    "Hello, [GREETING]" where len(GREETING) < 50
    return GREETING
    '''

result = greet("Alice")
```

### Multiple Variables (Product Type)

```python
@lmql.query
def analyze_sentiment():
    '''lmql
    "Analyze: 'I love this product!'\n"
    "Sentiment: [SENTIMENT]\n" where SENTIMENT in ["positive", "negative", "neutral"]
    "Confidence: [CONFIDENCE]\n" where CONFIDENCE in ["low", "medium", "high"]
    return {"sentiment": SENTIMENT, "confidence": CONFIDENCE}
    '''
```

## Constraint Types

### Length Constraints

```python
@lmql.query
def constrained_summary(text):
    '''lmql
    "Summarize in exactly 3 sentences:\n{text}\n"
    "Summary: [SUMMARY]" where len(SUMMARY.split('.')) == 3
    return SUMMARY
    '''
```

### Choice Constraints (Coproduct)

```python
@lmql.query
def classify_intent():
    '''lmql
    "User: I want to book a flight\n"
    "Intent: [INTENT]" where INTENT in [
        "booking", "cancellation", "inquiry", "complaint"
    ]
    return INTENT
    '''
```

### Regex Constraints

```python
import re

@lmql.query
def extract_email():
    '''lmql
    "Contact: john.doe@example.com\n"
    "Extracted email: [EMAIL]" where re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', EMAIL)
    return EMAIL
    '''
```

### Numeric Constraints

```python
@lmql.query
def rate_quality():
    '''lmql
    "Rate the quality (1-10): [RATING]" where int(RATING) >= 1 and int(RATING) <= 10
    return int(RATING)
    '''
```

## Logical Operators

### Conjunction (AND)

```python
@lmql.query
def structured_response():
    '''lmql
    "Response: [TEXT]" where (
        len(TEXT) >= 50 and 
        len(TEXT) <= 200 and
        TEXT[0].isupper() and
        TEXT.endswith('.')
    )
    return TEXT
    '''
```

### Disjunction (OR)

```python
@lmql.query
def flexible_format():
    '''lmql
    "Answer: [ANSWER]" where (
        ANSWER in ["yes", "no"] or
        ANSWER.startswith("Maybe")
    )
    return ANSWER
    '''
```

### Negation

```python
@lmql.query
def safe_generation():
    '''lmql
    "Story: [STORY]" where not any(
        word in STORY.lower() 
        for word in ["violence", "harm", "danger"]
    )
    return STORY
    '''
```

## Distribution Control

### Temperature and Sampling

```python
@lmql.query(model="gpt-4", temperature=0.7, max_tokens=100)
def creative_generation():
    '''lmql
    "Write a creative opening: [OPENING]"
    return OPENING
    '''
```

### Beam Search

```python
@lmql.query(decoder="beam", n=3)
def multiple_options():
    '''lmql
    "Suggest: [SUGGESTION]" where len(SUGGESTION) < 50
    return SUGGESTION
    '''
```

## Structured Output Patterns

### JSON Generation

```python
@lmql.query
def generate_json():
    '''lmql
    "{"
    "  \"name\": \"[NAME]\","  where len(NAME) < 30
    "  \"age\": [AGE],"        where int(AGE) > 0 and int(AGE) < 150
    "  \"city\": \"[CITY]\""   where len(CITY) < 50
    "}"
    return {"name": NAME, "age": int(AGE), "city": CITY}
    '''
```

### List Generation

```python
@lmql.query
def generate_list(n: int):
    '''lmql
    "List {n} items:\n"
    for i in range(n):
        "- [ITEM]\n" where len(ITEM) < 30
    return [ITEM for _ in range(n)]
    '''
```

## Categorical Patterns

### Functor: Mapping Over Constrained Outputs

```python
def map_constraint(query_fn, transform):
    """Functor mapping over constrained generation."""
    @lmql.query
    def mapped_query(*args, **kwargs):
        result = query_fn(*args, **kwargs)
        return transform(result)
    return mapped_query

# Usage
upper_greet = map_constraint(greet, str.upper)
```

### Monad: Sequencing Constrained Generations

```python
@lmql.query
def chained_generation(topic):
    '''lmql
    "Topic: {topic}\n"
    "First, generate an outline:\n[OUTLINE]" where len(OUTLINE) < 200
    "\nNow expand the first point:\n[EXPANSION]" where len(EXPANSION) < 500
    return {"outline": OUTLINE, "expansion": EXPANSION}
    '''
```

### Natural Transformation: Constraint Lifting

```python
def lift_to_list(single_query, n):
    """Natural transformation: single → list of n."""
    @lmql.query
    def list_query(*args, **kwargs):
        results = []
        for _ in range(n):
            result = single_query(*args, **kwargs)
            results.append(result)
        return results
    return list_query
```

## Integration with Python

### Type Hints

```python
from typing import Literal
from pydantic import BaseModel

class SentimentResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    score: float

@lmql.query
def typed_sentiment(text: str) -> SentimentResult:
    '''lmql
    "Analyze: {text}\n"
    "Sentiment: [SENT]" where SENT in ["positive", "negative", "neutral"]
    "Score: [SCORE]" where float(SCORE) >= 0 and float(SCORE) <= 1
    return SentimentResult(sentiment=SENT, score=float(SCORE))
    '''
```

### Async Queries

```python
import asyncio

@lmql.query
async def async_classify(texts: list[str]):
    '''lmql
    results = []
    for text in texts:
        "Classify '{text}': [LABEL]" where LABEL in ["spam", "ham"]
        results.append(LABEL)
    return results
    '''

# Usage
results = asyncio.run(async_classify(["hello", "buy now!!!"]))
```

## Debugging Constraints

```python
@lmql.query(debug=True)
def debug_query():
    '''lmql
    "Generate: [OUTPUT]" where (
        len(OUTPUT) > 10 and
        OUTPUT.startswith("The")
    )
    return OUTPUT
    '''
```

## Model Configuration

```python
import lmql

# OpenAI
lmql.model("openai/gpt-4", api_key="...")

# Anthropic
lmql.model("anthropic/claude-3-opus", api_key="...")

# Local models
lmql.model("local:llama-7b", endpoint="http://localhost:8000")
```

## Categorical Guarantees

LMQL provides these categorical guarantees:

1. **Constraint Satisfaction**: Output always satisfies declared constraints
2. **Type Safety**: Variables respect declared types
3. **Compositionality**: Queries compose preserving constraints
4. **Determinism**: Same constraints yield same output space
5. **Subobject Classification**: Constraints define precise output subsets
