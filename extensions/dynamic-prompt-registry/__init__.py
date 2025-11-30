"""
Dynamic Prompt Registry - Minimal Working Edition

Simple prompt storage and retrieval. No over-engineering.

Usage:
    from extensions.dynamic_prompt_registry import PromptRegistry, Domain

    registry = PromptRegistry()
    registry.register("greet", "Hello, {name}!", domain=Domain.GENERAL)
    print(registry.get("greet").render(name="World"))

CLI:
    python -m extensions.dynamic_prompt_registry.cli list
    python -m extensions.dynamic_prompt_registry.cli select "your problem"
"""

from .registry import PromptRegistry, Prompt, Domain, create_default_registry
from .selector import select_prompt, classify_domain, explain_selection

__all__ = [
    "PromptRegistry",
    "Prompt",
    "Domain",
    "create_default_registry",
    "select_prompt",
    "classify_domain",
    "explain_selection",
]

__version__ = "2.0.0"  # Minimal working edition
