---
name: prompt-dsl
description: Domain-specific language for categorical prompt composition with functor combinators and natural transformation operators. Use when building composable prompt templates, implementing typed prompt algebras, creating reusable prompt patterns with categorical structure, or designing prompt DSLs that preserve composition properties.
---

# Categorical Prompt DSL

A domain-specific language for composable prompt engineering with categorical foundations.

## Core Algebraic Structure

The Prompt DSL treats prompts as objects in a category:

- **Objects**: Prompt types (system, user, context, etc.)
- **Morphisms**: Prompt transformations
- **Composition**: Sequential prompt chaining
- **Tensor**: Parallel prompt combination
- **Exponential**: Prompt templates (parameterized prompts)

## Basic DSL Primitives

```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, List
from abc import ABC, abstractmethod

T = TypeVar('T')
U = TypeVar('U')

@dataclass
class Prompt:
    """Base prompt type - object in Prompt category."""
    content: str
    role: str = "user"
    metadata: dict = None
    
    def __post_init__(self):
        self.metadata = self.metadata or {}

# Prompt constructors
def system(content: str) -> Prompt:
    return Prompt(content=content, role="system")

def user(content: str) -> Prompt:
    return Prompt(content=content, role="user")

def assistant(content: str) -> Prompt:
    return Prompt(content=content, role="assistant")

def context(content: str) -> Prompt:
    return Prompt(content=content, role="context", metadata={"type": "context"})
```

## Composition Operators

```python
class PromptExpr(ABC):
    """Abstract prompt expression in the DSL."""
    
    @abstractmethod
    def render(self, ctx: dict = None) -> List[Prompt]:
        pass
    
    # Sequential composition: p1 >> p2
    def __rshift__(self, other: 'PromptExpr') -> 'PromptExpr':
        return Sequence(self, other)
    
    # Parallel composition: p1 | p2
    def __or__(self, other: 'PromptExpr') -> 'PromptExpr':
        return Parallel(self, other)
    
    # Repetition: p * n
    def __mul__(self, n: int) -> 'PromptExpr':
        return Repeat(self, n)
    
    # Conditional: p.when(predicate)
    def when(self, predicate: Callable[[dict], bool]) -> 'PromptExpr':
        return Conditional(self, predicate)

@dataclass
class Literal(PromptExpr):
    """Literal prompt value."""
    prompt: Prompt
    
    def render(self, ctx: dict = None) -> List[Prompt]:
        return [self.prompt]

@dataclass
class Sequence(PromptExpr):
    """Sequential composition: first >> second."""
    first: PromptExpr
    second: PromptExpr
    
    def render(self, ctx: dict = None) -> List[Prompt]:
        return self.first.render(ctx) + self.second.render(ctx)

@dataclass
class Parallel(PromptExpr):
    """Parallel composition: left | right."""
    left: PromptExpr
    right: PromptExpr
    
    def render(self, ctx: dict = None) -> List[Prompt]:
        # Interleave prompts
        l = self.left.render(ctx)
        r = self.right.render(ctx)
        result = []
        for i in range(max(len(l), len(r))):
            if i < len(l): result.append(l[i])
            if i < len(r): result.append(r[i])
        return result

@dataclass
class Repeat(PromptExpr):
    """Repetition: expr * count."""
    expr: PromptExpr
    count: int
    
    def render(self, ctx: dict = None) -> List[Prompt]:
        result = []
        for _ in range(self.count):
            result.extend(self.expr.render(ctx))
        return result

@dataclass
class Conditional(PromptExpr):
    """Conditional: expr.when(predicate)."""
    expr: PromptExpr
    predicate: Callable[[dict], bool]
    
    def render(self, ctx: dict = None) -> List[Prompt]:
        if self.predicate(ctx or {}):
            return self.expr.render(ctx)
        return []
```

## Template System (Exponential Objects)

```python
@dataclass
class Template(PromptExpr):
    """
    Parameterized prompt template.
    
    Represents exponential object: Context → Prompt
    """
    template_str: str
    role: str = "user"
    
    def render(self, ctx: dict = None) -> List[Prompt]:
        ctx = ctx or {}
        content = self.template_str.format(**ctx)
        return [Prompt(content=content, role=self.role)]
    
    # Curry: fix some parameters
    def partial(self, **kwargs) -> 'Template':
        """Partial application of template parameters."""
        new_template = self.template_str
        for k, v in kwargs.items():
            new_template = new_template.replace(f"{{{k}}}", str(v))
        return Template(new_template, self.role)

# Template constructors
def template(content: str, role: str = "user") -> Template:
    return Template(content, role)

def system_template(content: str) -> Template:
    return Template(content, "system")

# Example templates
qa_template = template(
    "Question: {question}\nProvide a detailed answer."
)

analysis_template = template(
    "Analyze the following {subject}:\n{content}\n\nFocus on: {focus}"
)
```

## Functor Operations

```python
def fmap(f: Callable[[str], str], expr: PromptExpr) -> PromptExpr:
    """
    Functor map: apply transformation to prompt content.
    
    Preserves structure: fmap(id) = id, fmap(g . f) = fmap(g) . fmap(f)
    """
    @dataclass
    class Mapped(PromptExpr):
        original: PromptExpr
        transform: Callable[[str], str]
        
        def render(self, ctx: dict = None) -> List[Prompt]:
            prompts = self.original.render(ctx)
            return [
                Prompt(
                    content=self.transform(p.content),
                    role=p.role,
                    metadata=p.metadata
                )
                for p in prompts
            ]
    
    return Mapped(expr, f)

# Example transformations
uppercase = lambda expr: fmap(str.upper, expr)
prefix = lambda pre: lambda expr: fmap(lambda s: f"{pre}\n{s}", expr)
suffix = lambda suf: lambda expr: fmap(lambda s: f"{s}\n{suf}", expr)
```

## Natural Transformations

```python
def role_transform(from_role: str, to_role: str) -> Callable[[PromptExpr], PromptExpr]:
    """
    Natural transformation changing prompt roles.
    
    Naturality: role_transform commutes with fmap.
    """
    @dataclass
    class RoleTransformed(PromptExpr):
        original: PromptExpr
        from_role: str
        to_role: str
        
        def render(self, ctx: dict = None) -> List[Prompt]:
            prompts = self.original.render(ctx)
            return [
                Prompt(
                    content=p.content,
                    role=self.to_role if p.role == self.from_role else p.role,
                    metadata=p.metadata
                )
                for p in prompts
            ]
    
    return lambda expr: RoleTransformed(expr, from_role, to_role)

# Transform user prompts to system prompts
user_to_system = role_transform("user", "system")
```

## Monad Structure

```python
@dataclass
class PromptM(Generic[T]):
    """
    Prompt monad for sequencing prompt effects.
    
    return: T → PromptM[T]
    bind: PromptM[T] → (T → PromptM[U]) → PromptM[U]
    """
    value: T
    prompts: List[Prompt]
    
    @staticmethod
    def pure(value: T) -> 'PromptM[T]':
        """Monadic return."""
        return PromptM(value=value, prompts=[])
    
    def bind(self, f: Callable[[T], 'PromptM[U]']) -> 'PromptM[U]':
        """Monadic bind (>>=)."""
        result = f(self.value)
        return PromptM(
            value=result.value,
            prompts=self.prompts + result.prompts
        )
    
    def map(self, f: Callable[[T], U]) -> 'PromptM[U]':
        """Functor map."""
        return PromptM(value=f(self.value), prompts=self.prompts)
    
    # Syntactic sugar
    def __rshift__(self, f: Callable[[T], 'PromptM[U]']) -> 'PromptM[U]':
        return self.bind(f)

def emit(prompt: Prompt) -> PromptM[None]:
    """Emit a prompt in the monad."""
    return PromptM(value=None, prompts=[prompt])

def emit_user(content: str) -> PromptM[None]:
    return emit(user(content))

def emit_system(content: str) -> PromptM[None]:
    return emit(system(content))
```

## DSL Combinators

```python
# Choice combinator: try first, fallback to second
def choice(primary: PromptExpr, fallback: PromptExpr) -> PromptExpr:
    @dataclass
    class Choice(PromptExpr):
        primary: PromptExpr
        fallback: PromptExpr
        
        def render(self, ctx: dict = None) -> List[Prompt]:
            result = self.primary.render(ctx)
            return result if result else self.fallback.render(ctx)
    
    return Choice(primary, fallback)

# Optional combinator
def optional(expr: PromptExpr) -> PromptExpr:
    return choice(expr, Literal(Prompt("")))

# Many combinator: zero or more
def many(expr: PromptExpr, separator: str = "\n") -> PromptExpr:
    @dataclass
    class Many(PromptExpr):
        expr: PromptExpr
        items_key: str = "items"
        separator: str = "\n"
        
        def render(self, ctx: dict = None) -> List[Prompt]:
            ctx = ctx or {}
            items = ctx.get(self.items_key, [])
            result = []
            for item in items:
                item_ctx = {**ctx, "item": item}
                result.extend(self.expr.render(item_ctx))
            return result
    
    return Many(expr, separator=separator)
```

## Complete Example

```python
# Build a complex prompt using the DSL
analysis_prompt = (
    Literal(system("You are an expert analyst."))
    >> Template("Analyze the following {topic}:", role="user")
    >> Template("{content}", role="context")
    >> Literal(user("Provide:"))
    >> (
        Literal(user("1. Key insights"))
        >> Literal(user("2. Potential issues"))
        >> Literal(user("3. Recommendations"))
    ).when(lambda ctx: ctx.get("detailed", False))
)

# Render with context
prompts = analysis_prompt.render({
    "topic": "market trends",
    "content": "Q4 sales increased 15%...",
    "detailed": True
})

# Convert to API format
messages = [{"role": p.role, "content": p.content} for p in prompts]
```

## Categorical Guarantees

The Prompt DSL ensures:

1. **Associativity**: `(a >> b) >> c = a >> (b >> c)`
2. **Identity**: Empty prompt is identity for composition
3. **Functor Laws**: `fmap` preserves identity and composition
4. **Naturality**: Role transforms commute with content maps
5. **Monad Laws**: `pure` and `bind` satisfy left/right identity and associativity
