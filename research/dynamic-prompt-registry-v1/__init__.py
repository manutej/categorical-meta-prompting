"""
Dynamic Prompt Registry Extension

Extends the categorical meta-prompting framework with:
- PromptRegistry: Named morphisms with quality tracking
- Reader monad: Environment access for dynamic prompt lookup
- PromptQueue: Free Applicative for deferred prompt sequencing
- Reference resolution: {prompt_name} syntax in meta-prompts

Categorical Foundations:
- Reader[Registry, A]: Environment-dependent computations
- Free[F, A]: Deferred interpretation of prompt pipelines
- Kleisli[PromptM]: Composable prompt transformations

Usage:
    from extensions.dynamic_prompt_registry import (
        PromptRegistry,
        PromptQueue,
        Reader,
        Lookup
    )

    # Create registry with tested prompts
    registry = PromptRegistry()
    registry.register("fibonacci", fibonacci_prompt, quality=0.95)

    # Build meta-prompt with dynamic references
    meta = registry.resolve_references('''
        Analyze: {problem}
        Apply: {fibonacci}
        Validate result
    ''')

    # Build prompt queue
    queue = (PromptQueue.empty()
        .then(Literal("Analyze"))
        .then(Lookup("fibonacci"))
        .then(Apply("validate")))
"""

from .registry import (
    PromptRegistry,
    RegisteredPrompt,
    DomainTag,
)

from .reader import (
    Reader,
    ask,
    asks,
    local,
)

from .queue import (
    PromptQueue,
    QueueStep,
    Literal,
    Lookup,
    Apply,
    Conditional,
)

from .resolver import (
    ReferenceResolver,
    resolve_references,
)

from .selector import (
    AppropriatePromptSelector,
    ProblemFeatures,
    MatchScore,
    get_appropriate_prompt,
)

from .integration import (
    RegistryAwareFunctor,
    RegistryEnhancedEngine,
    RegistryContext,
    create_registry_enhanced_engine,
    extend_resolver_with_appropriate,
)

__all__ = [
    # Registry
    "PromptRegistry",
    "RegisteredPrompt",
    "DomainTag",
    # Reader Monad
    "Reader",
    "ask",
    "asks",
    "local",
    # Queue (Free Applicative)
    "PromptQueue",
    "QueueStep",
    "Literal",
    "Lookup",
    "Apply",
    "Conditional",
    # Resolver
    "ReferenceResolver",
    "resolve_references",
    # Selector (core insight: {get appropriate prompt})
    "AppropriatePromptSelector",
    "ProblemFeatures",
    "MatchScore",
    "get_appropriate_prompt",
    # Integration with CategoricalMetaPromptingEngine
    "RegistryAwareFunctor",
    "RegistryEnhancedEngine",
    "RegistryContext",
    "create_registry_enhanced_engine",
    "extend_resolver_with_appropriate",
]

__version__ = "0.1.0"
