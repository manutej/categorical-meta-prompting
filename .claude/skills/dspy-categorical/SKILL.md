---
name: dspy-categorical
description: DSPy compositional prompt optimization with categorical signatures, module chaining, and automated prompt tuning. Use when building declarative LLM programs with typed signatures, composing multi-step reasoning modules (ChainOfThought, ReAct, ProgramOfThought), optimizing prompts with MIPROv2/BootstrapFewShot, or creating modular AI pipelines that separate program logic from prompt engineering.
---

# DSPy Categorical Prompt Optimization

DSPy provides categorical foundations for declarative LLM programming through typed signatures and compositional modules.

## Installation

```bash
pip install dspy-ai
```

## Core Categorical Concepts

DSPy maps cleanly to category theory:

- **Signature**: Morphism type `A → B` specifying input/output structure
- **Module**: Functor lifting signatures to executable programs
- **Optimizer**: Natural transformation improving module implementations
- **Composition**: Sequential/parallel module composition preserving types

## Configuration

```python
import dspy

# Configure language model
lm = dspy.LM('openai/gpt-4o', api_key='...')
dspy.configure(lm=lm)

# Alternative: Anthropic
lm = dspy.LM('anthropic/claude-sonnet-4-20250514', api_key='...')
```

## Signatures as Morphisms

### Inline Signatures

```python
# Signature: Question → Answer (morphism type)
qa = dspy.Predict('question -> answer')

# Signature with descriptions
summarize = dspy.Predict('document -> summary: concise 2-sentence summary')

# Multiple outputs (product type)
analyze = dspy.Predict('text -> sentiment, confidence, keywords')
```

### Class-Based Signatures

```python
class SentimentAnalysis(dspy.Signature):
    """Analyze the sentiment of the given text."""
    
    text = dspy.InputField(desc="text to analyze")
    sentiment = dspy.OutputField(desc="positive, negative, or neutral")
    confidence = dspy.OutputField(desc="confidence score 0-1")
    reasoning = dspy.OutputField(desc="explanation for the sentiment")
```

### Typed Signatures (Pydantic Integration)

```python
from pydantic import BaseModel
from typing import Literal

class SentimentOutput(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float
    keywords: list[str]

class TypedSentiment(dspy.Signature):
    """Analyze sentiment with structured output."""
    
    text: str = dspy.InputField()
    analysis: SentimentOutput = dspy.OutputField()
```

## Modules as Functors

### Predict (Identity Functor)

```python
# Direct signature execution
predict = dspy.Predict(SentimentAnalysis)
result = predict(text="I love this product!")
print(result.sentiment, result.confidence)
```

### ChainOfThought (Reasoning Functor)

```python
# Adds reasoning before output
cot = dspy.ChainOfThought('question -> answer')
result = cot(question="What is 15% of 240?")
print(result.reasoning)  # Step-by-step reasoning
print(result.answer)     # Final answer
```

### ProgramOfThought (Code Generation Functor)

```python
class MathProblem(dspy.Signature):
    """Solve mathematical problems with code."""
    question = dspy.InputField()
    answer = dspy.OutputField()

pot = dspy.ProgramOfThought(MathProblem, max_iters=3)
result = pot(question="Compute 12! / sum of primes between 1 and 30")
```

### ReAct (Action-Observation Functor)

```python
def search_tool(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

def calculator(expression: str) -> float:
    """Evaluate mathematical expression."""
    return eval(expression)

react = dspy.ReAct(
    'question -> answer',
    tools=[search_tool, calculator]
)
result = react(question="What is the population of Tokyo squared?")
```

## Module Composition

### Sequential Composition (Kleisli)

```python
class RAG(dspy.Module):
    """Retrieval-Augmented Generation as composed functors."""
    
    def __init__(self, num_passages=3):
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate = dspy.ChainOfThought('context, question -> answer')
    
    def forward(self, question):
        # Retrieve: Query → [Passage]
        context = self.retrieve(question).passages
        # Generate: (Context, Question) → Answer
        return self.generate(context=context, question=question)
```

### Multi-Hop Composition

```python
class MultiHop(dspy.Module):
    """Multi-hop reasoning through composed retrieval."""
    
    def __init__(self, num_hops=2):
        self.num_hops = num_hops
        self.generate_query = dspy.ChainOfThought('context, question -> query')
        self.retrieve = dspy.Retrieve(k=3)
        self.generate_answer = dspy.ChainOfThought('context, question -> answer')
    
    def forward(self, question):
        context = []
        for _ in range(self.num_hops):
            query = self.generate_query(
                context=context, 
                question=question
            ).query
            passages = self.retrieve(query).passages
            context = self.deduplicate(context + passages)
        
        return self.generate_answer(context=context, question=question)
    
    def deduplicate(self, passages):
        seen = set()
        return [p for p in passages if p not in seen and not seen.add(p)]
```

### Parallel Composition (Product)

```python
class ParallelAnalysis(dspy.Module):
    """Parallel execution forming product type."""
    
    def __init__(self):
        self.summarize = dspy.Predict('text -> summary')
        self.extract = dspy.Predict('text -> entities: list of named entities')
        self.classify = dspy.Predict('text -> category')
    
    def forward(self, text):
        # Execute in parallel (conceptually)
        summary = self.summarize(text=text)
        entities = self.extract(text=text)
        category = self.classify(text=text)
        
        return dspy.Prediction(
            summary=summary.summary,
            entities=entities.entities,
            category=category.category
        )
```

## Optimizers as Natural Transformations

### BootstrapFewShot

```python
from dspy.teleprompt import BootstrapFewShot

# Define metric
def exact_match(example, prediction, trace=None):
    return example.answer.lower() == prediction.answer.lower()

# Optimizer transforms module
optimizer = BootstrapFewShot(
    metric=exact_match,
    max_bootstrapped_demos=4,
    max_labeled_demos=4
)

# Compile: Module → OptimizedModule
optimized_rag = optimizer.compile(RAG(), trainset=train_examples)
```

### MIPROv2 (Advanced Optimizer)

```python
from dspy.teleprompt import MIPROv2

optimizer = MIPROv2(
    metric=dspy.SemanticF1(),
    auto="medium",  # light, medium, heavy
    num_threads=24
)

optimized = optimizer.compile(
    RAG(),
    trainset=train_examples,
    max_bootstrapped_demos=2,
    max_labeled_demos=2
)
```

### COPRO (Signature Optimizer)

```python
from dspy.teleprompt import COPRO

optimizer = COPRO(
    metric=exact_match,
    breadth=10,
    depth=3,
    init_temperature=1.4
)

optimized = optimizer.compile(
    student=RAG(),
    trainset=train_examples
)
```

## Categorical Patterns

### Functor Laws Verification

```python
def verify_functor_laws(module, input_data):
    """Verify module satisfies functor laws."""
    
    # Identity: F(id) = id
    result1 = module(input_data)
    result2 = module(input_data)
    assert result1.answer == result2.answer, "Identity law violated"
    
    # Composition: F(g ∘ f) = F(g) ∘ F(f)
    # Verified through module composition
    return True
```

### Natural Transformation Between Modules

```python
def transform_predict_to_cot(predict_module):
    """Natural transformation: Predict → ChainOfThought."""
    signature = predict_module.signature
    return dspy.ChainOfThought(signature)

# Usage
basic = dspy.Predict('question -> answer')
enhanced = transform_predict_to_cot(basic)
```

### Monad Structure in Optimization

```python
class OptimizationMonad:
    """Optimization as monad: bind chains optimizations."""
    
    @staticmethod
    def unit(module):
        """Lift module into optimization context."""
        return module
    
    @staticmethod
    def bind(optimized_module, optimizer, trainset):
        """Chain optimization transformations."""
        return optimizer.compile(optimized_module, trainset=trainset)

# Usage
module = RAG()
opt1 = BootstrapFewShot(metric=metric)
opt2 = MIPROv2(metric=metric, auto="light")

# Monadic chaining
step1 = OptimizationMonad.bind(module, opt1, trainset)
step2 = OptimizationMonad.bind(step1, opt2, trainset)
```

## Assertions and Constraints

```python
class ConstrainedQA(dspy.Module):
    """QA with categorical constraints (subobject classifier)."""
    
    def __init__(self):
        self.generate = dspy.ChainOfThought('question -> answer')
    
    def forward(self, question):
        response = self.generate(question=question)
        
        # Assertions as subobject constraints
        dspy.Assert(
            len(response.answer.split()) <= 50,
            "Answer must be concise (≤50 words)"
        )
        dspy.Assert(
            response.answer.endswith('.'),
            "Answer must be a complete sentence"
        )
        
        return response
```

## Evaluation Framework

```python
from dspy.evaluate import Evaluate

# Define comprehensive metric
def composite_metric(example, prediction, trace=None):
    exact = example.answer.lower() == prediction.answer.lower()
    semantic = dspy.SemanticF1()(example, prediction)
    return 0.5 * exact + 0.5 * semantic

# Evaluate
evaluator = Evaluate(
    devset=test_examples,
    metric=composite_metric,
    num_threads=4,
    display_progress=True
)

score = evaluator(optimized_rag)
print(f"Score: {score:.2%}")
```

## Best Practices

1. **Start Simple**: Begin with `Predict`, add complexity as needed
2. **Type Signatures**: Use Pydantic models for structured outputs
3. **Compose Modules**: Build complex pipelines from simple modules
4. **Optimize Iteratively**: Start with BootstrapFewShot, graduate to MIPROv2
5. **Validate Laws**: Test functor/monad laws in critical paths
6. **Use Assertions**: Constrain outputs with `dspy.Assert`
7. **Trace Execution**: Use `trace` parameter for debugging

## Categorical Guarantees

DSPy provides these categorical guarantees:

1. **Signature Preservation**: Optimizers preserve input/output types
2. **Compositional Semantics**: Module composition is associative
3. **Natural Transformations**: Optimizer upgrades preserve structure
4. **Typed Pipelines**: Pydantic integration ensures type safety
5. **Reproducibility**: Deterministic optimization with fixed seeds
