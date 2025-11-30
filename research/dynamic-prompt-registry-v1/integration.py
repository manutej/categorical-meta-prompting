"""
Integration with CategoricalMetaPromptingEngine

This module bridges the dynamic prompt registry with the existing
categorical meta-prompting engine, enabling:

1. Registry-aware Functor: Task → Prompt using stored prompts
2. Enhanced strategy selection with prompt lookup
3. {get:appropriate} resolution in meta-prompts

Categorical Structure:
    Enhanced F: Task × Registry → Prompt

    The functor now operates in a product category,
    taking both the task and registry as input.

Usage:
    from extensions.dynamic_prompt_registry.integration import (
        create_registry_enhanced_engine,
        RegistryAwareFunctor
    )

    # Create enhanced engine
    engine = create_registry_enhanced_engine(llm_client, registry)

    # Execute with registry-backed prompt selection
    result = engine.execute(task)
"""

from dataclasses import dataclass
from typing import Optional, Any, Callable

# Import from main engine (relative import for integration)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .registry import PromptRegistry, RegisteredPrompt, DomainTag
from .selector import AppropriatePromptSelector, ProblemFeatures
from .resolver import ReferenceResolver


@dataclass
class RegistryContext:
    """
    Context for registry-enhanced operations.

    Passed through the categorical pipeline.
    """
    registry: PromptRegistry
    selector: AppropriatePromptSelector
    resolver: ReferenceResolver

    # Tracking
    prompts_used: list = None
    selection_explanations: list = None

    def __post_init__(self):
        self.prompts_used = self.prompts_used or []
        self.selection_explanations = self.selection_explanations or []


class RegistryAwareFunctor:
    """
    Enhanced Functor: Task × Registry → Prompt

    This functor first attempts to select an appropriate prompt
    from the registry. Falls back to generation if no match.

    Categorical Properties:
    - Preserves identity when registry is empty
    - Composition with base functor when no match found
    - Quality-preserving selection
    """

    def __init__(
        self,
        registry: PromptRegistry,
        base_functor: Any = None,  # Original Task→Prompt functor
        min_quality: float = 0.7,
        min_match_score: float = 0.5
    ):
        self.registry = registry
        self.base_functor = base_functor
        self.selector = AppropriatePromptSelector(
            min_quality_threshold=min_quality,
            min_match_threshold=min_match_score
        )

    def map_object(self, task: 'Task') -> 'Prompt':
        """
        Map task to prompt, using registry when appropriate.

        Algorithm:
        1. Try to select from registry
        2. If good match found, use it
        3. Otherwise, fall back to base functor
        """
        # Try registry selection
        selected = self.selector.select(
            problem=task.description,
            registry=self.registry
        )

        if selected:
            # Found good match in registry
            from meta_prompting_engine.categorical.types import Prompt

            # Render template with task context
            variables = {
                "problem": task.description,
                "task": task.description,
                **task.metadata
            }

            rendered = selected.render(variables)

            return Prompt(
                template=rendered,
                variables=variables,
                context={
                    "source": "registry",
                    "prompt_name": selected.name,
                    "prompt_quality": selected.quality.score,
                    "domain": selected.domain.name
                },
                meta_level=0
            )

        # Fall back to base functor
        if self.base_functor:
            return self.base_functor.map_object(task)

        # Generate basic prompt if no base functor
        from meta_prompting_engine.categorical.types import Prompt
        return Prompt(
            template=f"Please solve the following:\n\n{task.description}",
            variables={"task": task.description},
            context={"source": "generated"},
            meta_level=0
        )

    def map_morphism(
        self,
        f: Callable[['Task'], 'Task']
    ) -> Callable[['Prompt'], 'Prompt']:
        """
        Map task morphism to prompt morphism.

        Preserves functor laws through registry.
        """
        def prompt_morphism(prompt: 'Prompt') -> 'Prompt':
            # Reconstruct task from prompt
            task_desc = prompt.context.get("task", prompt.template)
            from meta_prompting_engine.categorical.types import Task
            task = Task(description=task_desc)

            # Apply task transformation
            transformed_task = f(task)

            # Re-map through functor
            return self.map_object(transformed_task)

        return prompt_morphism


class RegistryEnhancedEngine:
    """
    Wrapper around CategoricalMetaPromptingEngine with registry support.

    Adds:
    - {get:appropriate} syntax in prompts
    - Registry-backed prompt selection
    - Quality tracking from registry
    """

    def __init__(
        self,
        base_engine: Any,
        registry: PromptRegistry
    ):
        self.base_engine = base_engine
        self.registry = registry
        self.resolver = ReferenceResolver(registry)
        self.selector = AppropriatePromptSelector()

        # Replace functor with registry-aware version
        self._original_functor = base_engine.functor
        base_engine.functor = RegistryAwareFunctor(
            registry=registry,
            base_functor=self._original_functor
        )

    def execute(self, task: 'Task', **kwargs) -> 'CategoricalExecutionResult':
        """
        Execute task with registry enhancement.
        """
        # Pre-process: resolve any references in task description
        if "{prompt:" in task.description or "{get:" in task.description:
            resolved = self.resolver.resolve(
                task.description,
                variables=task.metadata
            )
            task.description = resolved.resolved

        # Execute through base engine
        result = self.base_engine.execute(task, **kwargs)

        # Post-process: add registry metadata to result
        result.metadata["registry_prompts_available"] = len(self.registry)

        return result

    def get_prompt_recommendation(self, task_description: str) -> str:
        """
        Get explanation of which prompt would be selected.

        Useful for debugging and understanding selection.
        """
        return self.selector.explain_selection(task_description, self.registry)


def create_registry_enhanced_engine(
    llm_client: Any,
    registry: PromptRegistry,
    **config_kwargs
) -> RegistryEnhancedEngine:
    """
    Factory function to create registry-enhanced engine.

    Usage:
        registry = PromptRegistry()
        registry.register("fibonacci", ...)
        registry.register("sorting", ...)

        engine = create_registry_enhanced_engine(llm_client, registry)
        result = engine.execute(Task(description="Solve F(10)"))
    """
    try:
        from meta_prompting_engine.categorical.engine import (
            CategoricalMetaPromptingEngine,
            CategoricalMetaPromptingConfig
        )

        config = CategoricalMetaPromptingConfig(**config_kwargs)
        base_engine = CategoricalMetaPromptingEngine(llm_client, config)

        return RegistryEnhancedEngine(base_engine, registry)
    except ImportError:
        raise ImportError(
            "Could not import CategoricalMetaPromptingEngine. "
            "Ensure meta_prompting_engine is installed."
        )


# Extension to resolver for {get:appropriate} syntax
def extend_resolver_with_appropriate(resolver: ReferenceResolver):
    """
    Extend resolver to handle {get:appropriate} syntax.

    This enables:
        {get:appropriate}  → Best prompt for current context
        {appropriate:domain} → Best prompt for specific domain
    """
    original_resolve = resolver.resolve

    def enhanced_resolve(template, variables=None, recursive=True, max_depth=5):
        # Handle {get:appropriate} before standard resolution
        import re

        def replace_appropriate(match):
            domain_hint = match.group(1) if match.group(1) else None
            if domain_hint:
                try:
                    domain = DomainTag[domain_hint.upper()]
                except KeyError:
                    domain = None
            else:
                domain = None

            # Get problem context from variables
            problem = variables.get("problem", variables.get("task", "")) if variables else ""

            selector = AppropriatePromptSelector()
            best = selector.select(problem, resolver.registry, domain)

            if best:
                return best.template
            return match.group(0)  # Keep unresolved

        # Pattern for {get:appropriate} or {appropriate:domain}
        pattern = r'\{(?:get:appropriate|appropriate:([a-zA-Z_]+))\}'
        template = re.sub(pattern, replace_appropriate, template)

        # Continue with standard resolution
        return original_resolve(template, variables, recursive, max_depth)

    resolver.resolve = enhanced_resolve
    return resolver
