"""
Prompt Registry: Named Morphisms in the Prompt Category

Categorical Interpretation:
- Objects: Prompt types (Problem, Solution, Code, etc.)
- Morphisms: Named, stored prompt transformations
- Composition: Kleisli composition of registered prompts
- Enrichment: [0,1]-enriched with quality scores

This provides the "environment" that Reader monad accesses,
enabling dynamic prompt lookup at runtime via {prompt_name} syntax.

Example:
    registry = PromptRegistry()

    # Register domain-specific prompts with quality scores
    registry.register(
        name="fibonacci",
        prompt=Prompt(template="Solve fibonacci({n}) using DP..."),
        domain=DomainTag.ALGORITHMS,
        quality=0.95
    )

    # Lookup returns Reader monad for composition
    fib_reader = registry.lookup("fibonacci")
    prompt = fib_reader.run(registry)  # Resolve against registry
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Set, Callable, Any, TypeVar
from enum import Enum, auto
from datetime import datetime
import re

# Type variables for generic operations
A = TypeVar('A')
B = TypeVar('B')


class DomainTag(Enum):
    """
    Domain tags for organizing prompts.

    Enables domain-specific lookup and quality thresholds.
    """
    ALGORITHMS = auto()
    MATHEMATICS = auto()
    CODE_GENERATION = auto()
    CODE_REVIEW = auto()
    WRITING = auto()
    ANALYSIS = auto()
    REASONING = auto()
    EXTRACTION = auto()
    SUMMARIZATION = auto()
    TRANSLATION = auto()
    GENERAL = auto()


@dataclass
class QualityMetrics:
    """
    Quality metrics for a registered prompt.

    Tracks empirical performance across executions.
    """
    # Core quality score [0, 1]
    score: float = 0.0

    # Component scores
    correctness: float = 0.0
    clarity: float = 0.0
    efficiency: float = 0.0

    # Usage statistics
    execution_count: int = 0
    success_count: int = 0
    avg_latency_ms: float = 0.0

    # Verification status
    tested: bool = False
    verified: bool = False

    @property
    def success_rate(self) -> float:
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    def update(self, success: bool, latency_ms: float, quality: float):
        """Update metrics after execution."""
        self.execution_count += 1
        if success:
            self.success_count += 1

        # Exponential moving average for latency
        alpha = 0.1
        if self.avg_latency_ms == 0:
            self.avg_latency_ms = latency_ms
        else:
            self.avg_latency_ms = alpha * latency_ms + (1 - alpha) * self.avg_latency_ms

        # Update quality score (weighted average)
        if self.score == 0:
            self.score = quality
        else:
            self.score = alpha * quality + (1 - alpha) * self.score


@dataclass
class RegisteredPrompt:
    """
    A prompt registered in the registry.

    Contains the prompt template, metadata, and quality metrics.
    """
    # Identity
    name: str
    template: str

    # Classification
    domain: DomainTag = DomainTag.GENERAL
    tags: Set[str] = field(default_factory=set)

    # Type signature (for Kleisli composition)
    input_type: str = "Any"
    output_type: str = "Any"

    # Quality tracking
    quality: QualityMetrics = field(default_factory=QualityMetrics)

    # Metadata
    description: str = ""
    examples: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Dependencies (other prompts this references)
    dependencies: Set[str] = field(default_factory=set)

    def render(self, variables: Dict[str, Any]) -> str:
        """
        Render template with variables.

        Does NOT resolve {prompt_name} references - that's the resolver's job.
        """
        result = self.template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def get_variable_names(self) -> Set[str]:
        """Extract variable names from template."""
        # Match {name} but not {prompt_name} (which are for lookup)
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        return set(re.findall(pattern, self.template))


@dataclass
class PromptRegistry:
    """
    Registry of named prompts (morphisms in Prompt category).

    Categorical Structure:
    - This is the "environment" for Reader monad operations
    - Prompts are named morphisms that can be looked up and composed
    - Quality scores provide [0,1]-enriched structure

    Features:
    - Register prompts with domain tags and quality metrics
    - Lookup prompts by name (returns Reader monad)
    - Find prompts by domain or quality threshold
    - Compose prompts via Kleisli composition
    - Track dependencies between prompts
    """

    # Core storage
    prompts: Dict[str, RegisteredPrompt] = field(default_factory=dict)

    # Indices for efficient lookup
    _by_domain: Dict[DomainTag, Set[str]] = field(default_factory=dict)
    _by_tag: Dict[str, Set[str]] = field(default_factory=dict)

    # Quality thresholds by domain
    domain_thresholds: Dict[DomainTag, float] = field(default_factory=lambda: {
        DomainTag.ALGORITHMS: 0.90,
        DomainTag.MATHEMATICS: 0.90,
        DomainTag.CODE_GENERATION: 0.85,
        DomainTag.CODE_REVIEW: 0.85,
        DomainTag.WRITING: 0.80,
        DomainTag.ANALYSIS: 0.85,
        DomainTag.REASONING: 0.90,
        DomainTag.GENERAL: 0.75,
    })

    def register(
        self,
        name: str,
        template: str,
        domain: DomainTag = DomainTag.GENERAL,
        quality: float = 0.0,
        description: str = "",
        tags: Set[str] = None,
        input_type: str = "Any",
        output_type: str = "Any",
        examples: List[Dict[str, Any]] = None,
    ) -> RegisteredPrompt:
        """
        Register a named prompt in the registry.

        Args:
            name: Unique identifier for lookup
            template: Prompt template with {variable} placeholders
            domain: Domain classification
            quality: Initial quality score [0, 1]
            description: Human-readable description
            tags: Additional tags for discovery
            input_type: Type annotation for input
            output_type: Type annotation for output
            examples: Example inputs/outputs

        Returns:
            The registered prompt object
        """
        # Detect dependencies (references to other prompts)
        dependencies = self._detect_dependencies(template)

        prompt = RegisteredPrompt(
            name=name,
            template=template,
            domain=domain,
            tags=tags or set(),
            input_type=input_type,
            output_type=output_type,
            quality=QualityMetrics(score=quality, tested=quality > 0),
            description=description,
            examples=examples or [],
            dependencies=dependencies,
        )

        # Store prompt
        self.prompts[name] = prompt

        # Update indices
        if domain not in self._by_domain:
            self._by_domain[domain] = set()
        self._by_domain[domain].add(name)

        for tag in prompt.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = set()
            self._by_tag[tag].add(name)

        return prompt

    def _detect_dependencies(self, template: str) -> Set[str]:
        """
        Detect references to other prompts in template.

        Pattern: {prompt:name} or {lookup:name}
        """
        pattern = r'\{(?:prompt|lookup):([a-zA-Z_][a-zA-Z0-9_]*)\}'
        return set(re.findall(pattern, template))

    def get(self, name: str) -> Optional[RegisteredPrompt]:
        """Get prompt by name (direct access)."""
        return self.prompts.get(name)

    def lookup(self, name: str) -> 'Reader[PromptRegistry, Optional[RegisteredPrompt]]':
        """
        Lookup prompt by name (Reader monad).

        Returns a Reader that, when run against a registry,
        retrieves the named prompt.

        This enables composition:
            lookup("a") >>= (lambda a: lookup("b") >>= (lambda b: ...))
        """
        from .reader import Reader
        return Reader(lambda reg: reg.prompts.get(name))

    def find_by_domain(self, domain: DomainTag) -> List[RegisteredPrompt]:
        """Find all prompts in a domain."""
        names = self._by_domain.get(domain, set())
        return [self.prompts[n] for n in names if n in self.prompts]

    def find_by_tag(self, tag: str) -> List[RegisteredPrompt]:
        """Find all prompts with a tag."""
        names = self._by_tag.get(tag, set())
        return [self.prompts[n] for n in names if n in self.prompts]

    def find_by_quality(self, min_quality: float) -> List[RegisteredPrompt]:
        """Find prompts meeting quality threshold."""
        return [
            p for p in self.prompts.values()
            if p.quality.score >= min_quality
        ]

    def find_verified(self) -> List[RegisteredPrompt]:
        """Find all verified (tested) prompts."""
        return [
            p for p in self.prompts.values()
            if p.quality.verified
        ]

    def get_best_for_domain(self, domain: DomainTag) -> Optional[RegisteredPrompt]:
        """Get highest quality prompt for a domain."""
        domain_prompts = self.find_by_domain(domain)
        if not domain_prompts:
            return None
        return max(domain_prompts, key=lambda p: p.quality.score)

    def validate_dependencies(self, name: str) -> List[str]:
        """
        Check if all dependencies of a prompt are satisfied.

        Returns list of missing dependency names.
        """
        prompt = self.prompts.get(name)
        if not prompt:
            return [name]

        missing = []
        for dep in prompt.dependencies:
            if dep not in self.prompts:
                missing.append(dep)
        return missing

    def topological_order(self, name: str) -> List[str]:
        """
        Get prompts in dependency order (for execution).

        Returns prompts from leaves (no deps) to root.
        """
        visited = set()
        order = []

        def visit(n: str):
            if n in visited:
                return
            visited.add(n)
            prompt = self.prompts.get(n)
            if prompt:
                for dep in prompt.dependencies:
                    visit(dep)
            order.append(n)

        visit(name)
        return order

    def compose(self, *names: str) -> Optional[str]:
        """
        Compose multiple prompts into a single template.

        Kleisli composition: a >=> b >=> c
        """
        templates = []
        for name in names:
            prompt = self.prompts.get(name)
            if not prompt:
                return None
            templates.append(f"# Step: {name}\n{prompt.template}")

        return "\n\n".join(templates)

    def export(self) -> Dict[str, Any]:
        """Export registry to serializable format."""
        return {
            "version": "0.1.0",
            "prompts": {
                name: {
                    "template": p.template,
                    "domain": p.domain.name,
                    "quality": p.quality.score,
                    "description": p.description,
                    "tags": list(p.tags),
                    "input_type": p.input_type,
                    "output_type": p.output_type,
                }
                for name, p in self.prompts.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptRegistry':
        """Import registry from serialized format."""
        registry = cls()
        for name, pdata in data.get("prompts", {}).items():
            registry.register(
                name=name,
                template=pdata["template"],
                domain=DomainTag[pdata.get("domain", "GENERAL")],
                quality=pdata.get("quality", 0.0),
                description=pdata.get("description", ""),
                tags=set(pdata.get("tags", [])),
                input_type=pdata.get("input_type", "Any"),
                output_type=pdata.get("output_type", "Any"),
            )
        return registry

    def __contains__(self, name: str) -> bool:
        return name in self.prompts

    def __len__(self) -> int:
        return len(self.prompts)

    def __iter__(self):
        return iter(self.prompts.values())
