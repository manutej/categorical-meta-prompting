"""
Minimal Prompt Registry - Actually Works Edition

A simple dict-based registry for storing and retrieving prompts.
No categorical formalism. No over-engineering. Just works.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import json


class Domain(Enum):
    """Simple domain classification."""
    ALGORITHM = auto()
    SECURITY = auto()
    API = auto()
    DATABASE = auto()
    TESTING = auto()
    DEBUG = auto()
    GENERAL = auto()


@dataclass
class Prompt:
    """A stored prompt with metadata."""
    name: str
    template: str
    domain: Domain = Domain.GENERAL
    quality: float = 0.0  # 0.0 to 1.0, user-assigned
    tags: List[str] = field(default_factory=list)

    def render(self, **kwargs) -> str:
        """Render template with variables."""
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result


class PromptRegistry:
    """
    Simple prompt registry.

    Usage:
        registry = PromptRegistry()
        registry.register("greet", "Hello, {name}!")
        print(registry.get("greet").render(name="World"))
    """

    def __init__(self):
        self.prompts: Dict[str, Prompt] = {}

    def register(
        self,
        name: str,
        template: str,
        domain: Domain = Domain.GENERAL,
        quality: float = 0.0,
        tags: List[str] = None
    ) -> Prompt:
        """Register a prompt."""
        prompt = Prompt(
            name=name,
            template=template,
            domain=domain,
            quality=quality,
            tags=tags or []
        )
        self.prompts[name] = prompt
        return prompt

    def get(self, name: str) -> Optional[Prompt]:
        """Get a prompt by name."""
        return self.prompts.get(name)

    def list_all(self) -> List[Prompt]:
        """List all prompts."""
        return list(self.prompts.values())

    def find_by_domain(self, domain: Domain) -> List[Prompt]:
        """Find prompts by domain."""
        return [p for p in self.prompts.values() if p.domain == domain]

    def find_by_tag(self, tag: str) -> List[Prompt]:
        """Find prompts by tag."""
        return [p for p in self.prompts.values() if tag in p.tags]

    def find_by_quality(self, min_quality: float) -> List[Prompt]:
        """Find prompts meeting quality threshold."""
        return [p for p in self.prompts.values() if p.quality >= min_quality]

    def best_for_domain(self, domain: Domain) -> Optional[Prompt]:
        """Get highest quality prompt for a domain."""
        domain_prompts = self.find_by_domain(domain)
        if not domain_prompts:
            return None
        return max(domain_prompts, key=lambda p: p.quality)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dict."""
        return {
            name: {
                "template": p.template,
                "domain": p.domain.name,
                "quality": p.quality,
                "tags": p.tags
            }
            for name, p in self.prompts.items()
        }

    def save(self, path: str):
        """Save to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def load(self, path: str):
        """Load from JSON file."""
        with open(path) as f:
            data = json.load(f)
        for name, pdata in data.items():
            self.register(
                name=name,
                template=pdata["template"],
                domain=Domain[pdata.get("domain", "GENERAL")],
                quality=pdata.get("quality", 0.0),
                tags=pdata.get("tags", [])
            )

    def __len__(self):
        return len(self.prompts)

    def __contains__(self, name: str):
        return name in self.prompts


# Built-in prompts for common tasks
def create_default_registry() -> PromptRegistry:
    """Create registry with useful default prompts."""
    r = PromptRegistry()

    r.register(
        name="debug",
        template="""Debug this issue systematically:

Issue: {issue}

1. What is the exact error/symptom?
2. What's the minimal reproduction?
3. What are 2-3 likely causes?
4. How to test each hypothesis?
5. What's the fix?""",
        domain=Domain.DEBUG,
        quality=0.8,
        tags=["debug", "systematic"]
    )

    r.register(
        name="review_algorithm",
        template="""Review this code for algorithmic correctness:

{code}

Check:
1. Time complexity (Big-O)
2. Space complexity
3. Edge cases (empty, single, large)
4. Correctness for all inputs""",
        domain=Domain.ALGORITHM,
        quality=0.8,
        tags=["review", "algorithm", "complexity"]
    )

    r.register(
        name="review_security",
        template="""Review this code for security issues:

{code}

Check:
1. Input validation
2. Injection risks (SQL, command, XSS)
3. Authentication/authorization
4. Sensitive data exposure""",
        domain=Domain.SECURITY,
        quality=0.85,
        tags=["review", "security", "owasp"]
    )

    r.register(
        name="test_generate",
        template="""Generate tests for this code:

{code}

Include:
1. Happy path tests
2. Edge case tests
3. Error case tests

Use clear test names and assertions.""",
        domain=Domain.TESTING,
        quality=0.75,
        tags=["test", "generate"]
    )

    return r


if __name__ == "__main__":
    # Self-test
    r = create_default_registry()
    print(f"Registry has {len(r)} prompts")

    debug_prompt = r.get("debug")
    print(f"\nDebug prompt exists: {debug_prompt is not None}")

    rendered = debug_prompt.render(issue="TypeError in line 42")
    print(f"\nRendered (first 100 chars):\n{rendered[:100]}...")

    best_security = r.best_for_domain(Domain.SECURITY)
    print(f"\nBest security prompt: {best_security.name if best_security else 'None'}")

    print("\nSelf-test: PASSED")
