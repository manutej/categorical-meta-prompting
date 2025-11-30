"""
Reference Resolver: Dynamic {prompt_name} Syntax Resolution

Resolves references to registered prompts within meta-prompt templates.

Syntax Patterns:
    {prompt:name}     - Lookup and inline prompt 'name'
    {lookup:name}     - Alias for {prompt:name}
    {best:domain}     - Get best prompt for domain
    {var:name}        - Variable substitution (not a lookup)

Example:
    meta_prompt = '''
    You are solving: {var:problem}

    Step 1: Analyze the problem structure
    Step 2: {prompt:fibonacci}
    Step 3: Validate using {prompt:validator}
    '''

    resolver = ReferenceResolver(registry)
    resolved = resolver.resolve(meta_prompt, {"problem": "Find F(10)"})

This enables meta-prompts that dynamically compose well-tested sub-prompts.
"""

from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional, Any, Tuple
import re
from enum import Enum, auto


class ReferenceType(Enum):
    """Types of references in templates."""
    PROMPT = auto()      # {prompt:name} - lookup from registry
    LOOKUP = auto()      # {lookup:name} - alias for prompt
    BEST = auto()        # {best:domain} - best prompt for domain
    VARIABLE = auto()    # {var:name} - variable substitution
    PLAIN = auto()       # {name} - legacy/simple variable


@dataclass
class Reference:
    """A parsed reference from a template."""
    full_match: str      # The complete matched string
    ref_type: ReferenceType
    name: str            # The reference name/key
    start: int           # Start position in template
    end: int             # End position in template
    default: Optional[str] = None  # Optional default value


@dataclass
class ResolutionResult:
    """Result of resolving references in a template."""
    resolved: str                    # The resolved template
    resolved_refs: List[str]         # Names that were resolved
    unresolved_refs: List[str]       # Names that couldn't be resolved
    variables_used: Set[str]         # Variables that were substituted
    errors: List[str]                # Any errors encountered


@dataclass
class ReferenceResolver:
    """
    Resolves {prompt:name} references in meta-prompt templates.

    Provides the core mechanism for dynamic prompt composition:
    - Meta-prompts can reference sub-prompts by name
    - References are resolved at runtime against the registry
    - Supports variable substitution alongside prompt lookup
    - Tracks resolution for debugging/optimization

    Categorical Interpretation:
    - This is the "interpretation" function for the DSL
    - Maps symbolic references to concrete prompt content
    - Enables deferred resolution (references are symbolic until resolved)
    """

    registry: 'PromptRegistry'

    # Patterns for different reference types
    PATTERNS: Dict[ReferenceType, str] = field(default_factory=lambda: {
        ReferenceType.PROMPT: r'\{prompt:([a-zA-Z_][a-zA-Z0-9_]*)\}',
        ReferenceType.LOOKUP: r'\{lookup:([a-zA-Z_][a-zA-Z0-9_]*)\}',
        ReferenceType.BEST: r'\{best:([a-zA-Z_][a-zA-Z0-9_]*)\}',
        ReferenceType.VARIABLE: r'\{var:([a-zA-Z_][a-zA-Z0-9_]*)\}',
        ReferenceType.PLAIN: r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}',
    })

    def parse_references(self, template: str) -> List[Reference]:
        """
        Parse all references from a template.

        Returns list of Reference objects with positions.
        """
        references = []

        # Parse typed references first (prompt:, lookup:, best:, var:)
        for ref_type in [ReferenceType.PROMPT, ReferenceType.LOOKUP,
                         ReferenceType.BEST, ReferenceType.VARIABLE]:
            pattern = self.PATTERNS[ref_type]
            for match in re.finditer(pattern, template):
                references.append(Reference(
                    full_match=match.group(0),
                    ref_type=ref_type,
                    name=match.group(1),
                    start=match.start(),
                    end=match.end(),
                ))

        # Plain references {name} are treated as variables
        # But only if not already matched as typed reference
        typed_positions = {(r.start, r.end) for r in references}
        for match in re.finditer(self.PATTERNS[ReferenceType.PLAIN], template):
            if (match.start(), match.end()) not in typed_positions:
                references.append(Reference(
                    full_match=match.group(0),
                    ref_type=ReferenceType.PLAIN,
                    name=match.group(1),
                    start=match.start(),
                    end=match.end(),
                ))

        # Sort by position for sequential resolution
        references.sort(key=lambda r: r.start)
        return references

    def resolve(
        self,
        template: str,
        variables: Dict[str, Any] = None,
        recursive: bool = True,
        max_depth: int = 5
    ) -> ResolutionResult:
        """
        Resolve all references in a template.

        Args:
            template: Template with {prompt:name} references
            variables: Variables for {var:name} substitution
            recursive: Whether to resolve references in resolved prompts
            max_depth: Maximum recursion depth

        Returns:
            ResolutionResult with resolved template and metadata
        """
        variables = variables or {}
        resolved_refs = []
        unresolved_refs = []
        variables_used = set()
        errors = []

        result = template
        depth = 0

        while depth < max_depth:
            references = self.parse_references(result)
            if not references:
                break

            # Track if we made any changes this iteration
            changed = False

            # Resolve from end to start to preserve positions
            for ref in reversed(references):
                replacement = None

                if ref.ref_type in (ReferenceType.PROMPT, ReferenceType.LOOKUP):
                    # Lookup from registry
                    prompt = self.registry.get(ref.name)
                    if prompt:
                        replacement = prompt.template
                        resolved_refs.append(ref.name)
                    else:
                        unresolved_refs.append(ref.name)
                        errors.append(f"Prompt not found: {ref.name}")

                elif ref.ref_type == ReferenceType.BEST:
                    # Get best prompt for domain
                    from .registry import DomainTag
                    try:
                        domain = DomainTag[ref.name.upper()]
                        prompt = self.registry.get_best_for_domain(domain)
                        if prompt:
                            replacement = prompt.template
                            resolved_refs.append(f"best:{ref.name}")
                        else:
                            unresolved_refs.append(f"best:{ref.name}")
                    except KeyError:
                        errors.append(f"Unknown domain: {ref.name}")

                elif ref.ref_type == ReferenceType.VARIABLE:
                    # Variable substitution
                    if ref.name in variables:
                        replacement = str(variables[ref.name])
                        variables_used.add(ref.name)
                    else:
                        unresolved_refs.append(f"var:{ref.name}")

                elif ref.ref_type == ReferenceType.PLAIN:
                    # Plain variables (legacy support)
                    if ref.name in variables:
                        replacement = str(variables[ref.name])
                        variables_used.add(ref.name)
                    # Don't mark as unresolved - might be intentional

                if replacement is not None:
                    result = result[:ref.start] + replacement + result[ref.end:]
                    changed = True

            if not recursive or not changed:
                break
            depth += 1

        return ResolutionResult(
            resolved=result,
            resolved_refs=resolved_refs,
            unresolved_refs=unresolved_refs,
            variables_used=variables_used,
            errors=errors,
        )

    def resolve_to_queue(
        self,
        template: str,
        variables: Dict[str, Any] = None
    ) -> 'PromptQueue':
        """
        Convert template with references to a PromptQueue.

        Instead of inlining, creates Lookup steps for prompt references.
        This preserves the deferred nature for later interpretation.
        """
        from .queue import PromptQueue, Literal, Lookup

        variables = variables or {}
        queue = PromptQueue.empty()

        references = self.parse_references(template)
        last_end = 0

        for ref in references:
            # Add literal text before this reference
            if ref.start > last_end:
                text = template[last_end:ref.start]
                # Substitute plain variables in literals
                for var_name, var_value in variables.items():
                    text = text.replace(f"{{{var_name}}}", str(var_value))
                if text.strip():
                    queue = queue.then(Literal(text=text))

            # Add appropriate step for reference type
            if ref.ref_type in (ReferenceType.PROMPT, ReferenceType.LOOKUP):
                queue = queue.then(Lookup(name=ref.name))
            elif ref.ref_type == ReferenceType.VARIABLE:
                if ref.name in variables:
                    queue = queue.then(Literal(text=str(variables[ref.name])))
            elif ref.ref_type == ReferenceType.PLAIN:
                if ref.name in variables:
                    queue = queue.then(Literal(text=str(variables[ref.name])))

            last_end = ref.end

        # Add remaining literal text
        if last_end < len(template):
            text = template[last_end:]
            for var_name, var_value in variables.items():
                text = text.replace(f"{{{var_name}}}", str(var_value))
            if text.strip():
                queue = queue.then(Literal(text=text))

        return queue

    def get_dependencies(self, template: str) -> Set[str]:
        """
        Get all prompt dependencies in a template.

        Useful for:
        - Validation (ensure all deps exist)
        - Preloading/caching
        - Topological ordering
        """
        references = self.parse_references(template)
        return {
            ref.name for ref in references
            if ref.ref_type in (ReferenceType.PROMPT, ReferenceType.LOOKUP)
        }

    def validate(self, template: str) -> Tuple[bool, List[str]]:
        """
        Validate that all references can be resolved.

        Returns (is_valid, list_of_missing_refs)
        """
        deps = self.get_dependencies(template)
        missing = [name for name in deps if name not in self.registry]
        return (len(missing) == 0, missing)


# Convenience function

def resolve_references(
    template: str,
    registry: 'PromptRegistry',
    variables: Dict[str, Any] = None,
    recursive: bool = True
) -> str:
    """
    Convenience function to resolve references in a template.

    Args:
        template: Template with {prompt:name} references
        registry: PromptRegistry to lookup from
        variables: Variables for substitution
        recursive: Whether to resolve nested references

    Returns:
        Resolved template string
    """
    resolver = ReferenceResolver(registry=registry)
    result = resolver.resolve(template, variables, recursive)
    return result.resolved
