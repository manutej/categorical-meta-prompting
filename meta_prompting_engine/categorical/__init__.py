"""
Categorical structures for meta-prompting with verified laws.

This module provides the core categorical abstractions:
- Functor: Structure-preserving mappings (Tasks → Prompts)
- Monad: Recursive improvement with composition
- Comonad: Context extraction and observation
- GradedComonad: Resource-indexed context extraction (Pattern 1)
- Quality enrichment: [0,1]-valued morphisms

All structures come with property-based tests verifying categorical laws.
"""

from .functor import Functor, create_task_to_prompt_functor
from .monad import Monad, MonadPrompt, create_recursive_meta_monad
from .comonad import Comonad, Observation, create_context_comonad
from .graded_comonad import (
    Tier,
    GradedObservation,
    GradedComonad,
    create_graded_comonad,
    infer_tier_from_complexity,
    infer_tier_from_tokens,
)
from .engine import (
    CategoricalMetaPromptingEngine,
    CategoricalExecutionResult,
    CategoricalMetaPromptingConfig,
    create_categorical_engine
)

__all__ = [
    # Functor
    "Functor",
    "create_task_to_prompt_functor",
    # Monad
    "Monad",
    "MonadPrompt",
    "create_recursive_meta_monad",
    # Comonad
    "Comonad",
    "Observation",
    "create_context_comonad",
    # Graded Comonad (Pattern 1)
    "Tier",
    "GradedObservation",
    "GradedComonad",
    "create_graded_comonad",
    "infer_tier_from_complexity",
    "infer_tier_from_tokens",
    # Engine
    "CategoricalMetaPromptingEngine",
    "CategoricalExecutionResult",
    "CategoricalMetaPromptingConfig",
    "create_categorical_engine",
]
