"""
Categorical structures for meta-prompting with verified laws.

This module provides the core categorical abstractions:
- Functor: Structure-preserving mappings (Tasks → Prompts)
- Monad: Recursive improvement with composition
- Comonad: Context extraction and observation
- Quality enrichment: [0,1]-valued morphisms

All structures come with property-based tests verifying categorical laws.
"""

from .functor import Functor, create_task_to_prompt_functor
from .monad import Monad, MonadPrompt, create_recursive_meta_monad
from .comonad import Comonad, Observation, create_context_comonad
from .engine import (
    CategoricalMetaPromptingEngine,
    CategoricalExecutionResult,
    CategoricalMetaPromptingConfig,
    create_categorical_engine
)

__all__ = [
    "Functor",
    "create_task_to_prompt_functor",
    "Monad",
    "MonadPrompt",
    "create_recursive_meta_monad",
    "Comonad",
    "Observation",
    "create_context_comonad",
    "CategoricalMetaPromptingEngine",
    "CategoricalExecutionResult",
    "CategoricalMetaPromptingConfig",
    "create_categorical_engine",
]
