"""
Appropriate Prompt Selector: Problem → Best(Prompt)

This is the core of the user's insight:
    "do {get appropriate prompt} to do the given problem in most efficient way possible"

The selector automatically chooses the best prompt from the registry
based on problem characteristics, domain matching, and quality scores.

Categorical Interpretation:
    Selector: Problem × Registry → Prompt

    This is a morphism in a product category that:
    1. Projects problem features
    2. Matches against registered prompt signatures
    3. Returns quality-weighted best match

Integration:
    - Used by enhanced Functor for registry-aware prompt generation
    - Used by {get:appropriate} syntax in meta-prompts
    - Used by PromptQueue for dynamic dispatch
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any, Set
from enum import Enum
import re

from .registry import PromptRegistry, RegisteredPrompt, DomainTag, QualityMetrics


@dataclass
class ProblemFeatures:
    """
    Extracted features from a problem description.

    Used for matching against registered prompts.
    """
    # Primary classification
    domain: DomainTag = DomainTag.GENERAL
    domain_confidence: float = 0.5

    # Problem characteristics
    keywords: Set[str] = field(default_factory=set)
    complexity_indicators: Set[str] = field(default_factory=set)

    # Structural features
    has_examples: bool = False
    has_constraints: bool = False
    requires_step_by_step: bool = False
    requires_code: bool = False

    # Inferred requirements
    needs_chain_of_thought: bool = False
    needs_few_shot: bool = False
    needs_structured_output: bool = False


@dataclass
class MatchScore:
    """
    Score representing how well a prompt matches a problem.

    Combines multiple factors with quality weighting.
    """
    # Component scores [0, 1]
    domain_match: float = 0.0
    keyword_overlap: float = 0.0
    type_compatibility: float = 0.0
    complexity_fit: float = 0.0

    # Quality from registry
    prompt_quality: float = 0.0

    # Weights for aggregation
    weights: Dict[str, float] = field(default_factory=lambda: {
        "domain_match": 0.30,
        "keyword_overlap": 0.20,
        "type_compatibility": 0.15,
        "complexity_fit": 0.10,
        "prompt_quality": 0.25,  # Quality matters!
    })

    @property
    def total(self) -> float:
        """Weighted aggregate score."""
        return (
            self.weights["domain_match"] * self.domain_match +
            self.weights["keyword_overlap"] * self.keyword_overlap +
            self.weights["type_compatibility"] * self.type_compatibility +
            self.weights["complexity_fit"] * self.complexity_fit +
            self.weights["prompt_quality"] * self.prompt_quality
        )

    def __lt__(self, other: 'MatchScore') -> bool:
        return self.total < other.total


class AppropriatePromptSelector:
    """
    Selects the most appropriate prompt from registry for a given problem.

    This implements the core insight:
        {get appropriate prompt} → Best matching, quality-weighted prompt

    Algorithm:
    1. Extract features from problem
    2. For each candidate prompt:
       - Compute domain match score
       - Compute keyword overlap
       - Check type compatibility
       - Factor in prompt quality
    3. Return highest scoring prompt

    Categorical Properties:
    - Deterministic: Same problem + registry → Same selection
    - Quality-preserving: Higher quality prompts preferred
    - Domain-aware: Respects prompt categorization
    """

    # Domain classification keywords
    DOMAIN_KEYWORDS: Dict[DomainTag, Set[str]] = {
        DomainTag.ALGORITHMS: {
            "algorithm", "sort", "search", "tree", "graph", "dynamic programming",
            "recursion", "iteration", "complexity", "O(n)", "big-o", "fibonacci",
            "binary search", "merge sort", "quick sort", "bfs", "dfs", "dijkstra"
        },
        DomainTag.MATHEMATICS: {
            "prove", "theorem", "equation", "calculate", "derivative", "integral",
            "matrix", "vector", "probability", "statistics", "algebra", "geometry",
            "calculus", "number theory", "combinatorics"
        },
        DomainTag.CODE_GENERATION: {
            "write code", "implement", "function", "class", "method", "api",
            "program", "script", "generate code", "create function"
        },
        DomainTag.CODE_REVIEW: {
            "review", "bug", "error", "fix", "improve", "refactor", "optimize",
            "code quality", "best practices", "code smell"
        },
        DomainTag.WRITING: {
            "write", "essay", "article", "blog", "story", "creative", "narrative",
            "compose", "draft", "edit text"
        },
        DomainTag.ANALYSIS: {
            "analyze", "evaluate", "compare", "contrast", "assess", "examine",
            "investigate", "study", "research"
        },
        DomainTag.REASONING: {
            "reason", "logic", "deduce", "infer", "conclude", "argument",
            "think through", "step by step", "chain of thought"
        },
        DomainTag.EXTRACTION: {
            "extract", "parse", "find", "identify", "locate", "pull out",
            "get information", "retrieve"
        },
        DomainTag.SUMMARIZATION: {
            "summarize", "summary", "brief", "condense", "tldr", "key points",
            "main ideas", "overview"
        },
        DomainTag.TRANSLATION: {
            "translate", "convert", "transform", "language", "format",
            "from X to Y", "in other words"
        },
    }

    def __init__(
        self,
        min_quality_threshold: float = 0.5,
        min_match_threshold: float = 0.3,
    ):
        """
        Initialize selector.

        Args:
            min_quality_threshold: Minimum prompt quality to consider
            min_match_threshold: Minimum match score to return
        """
        self.min_quality = min_quality_threshold
        self.min_match = min_match_threshold

    def extract_features(self, problem: str) -> ProblemFeatures:
        """
        Extract features from problem description.

        This is the first step in appropriate prompt selection.
        """
        problem_lower = problem.lower()
        features = ProblemFeatures()

        # Classify domain
        domain_scores: Dict[DomainTag, float] = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in problem_lower)
            if score > 0:
                domain_scores[domain] = score / len(keywords)

        if domain_scores:
            best_domain = max(domain_scores.items(), key=lambda x: x[1])
            features.domain = best_domain[0]
            features.domain_confidence = min(best_domain[1] * 3, 1.0)  # Scale up

        # Extract keywords (simple tokenization)
        words = set(re.findall(r'\b[a-z]{3,}\b', problem_lower))
        features.keywords = words

        # Detect complexity indicators
        complexity_words = {"complex", "difficult", "advanced", "nested", "recursive"}
        features.complexity_indicators = words & complexity_words

        # Structural features
        features.has_examples = "example" in problem_lower or "e.g." in problem_lower
        features.has_constraints = "constraint" in problem_lower or "must" in problem_lower
        features.requires_step_by_step = (
            "step by step" in problem_lower or
            "explain" in problem_lower or
            "how to" in problem_lower
        )
        features.requires_code = (
            "code" in problem_lower or
            "implement" in problem_lower or
            "function" in problem_lower
        )

        # Inferred requirements
        features.needs_chain_of_thought = features.requires_step_by_step
        features.needs_few_shot = features.has_examples
        features.needs_structured_output = "json" in problem_lower or "format" in problem_lower

        return features

    def score_prompt(
        self,
        problem_features: ProblemFeatures,
        prompt: RegisteredPrompt
    ) -> MatchScore:
        """
        Score how well a prompt matches problem features.
        """
        score = MatchScore()

        # Domain match
        if prompt.domain == problem_features.domain:
            score.domain_match = 1.0
        elif prompt.domain == DomainTag.GENERAL:
            score.domain_match = 0.5  # General prompts partially match
        else:
            score.domain_match = 0.1

        # Keyword overlap
        prompt_words = set(re.findall(r'\b[a-z]{3,}\b', prompt.template.lower()))
        if problem_features.keywords and prompt_words:
            overlap = len(problem_features.keywords & prompt_words)
            score.keyword_overlap = min(overlap / 5, 1.0)  # Cap at 5 matches

        # Type compatibility
        # If problem requires code and prompt generates code, good match
        if problem_features.requires_code and "code" in prompt.output_type.lower():
            score.type_compatibility = 1.0
        elif not problem_features.requires_code and "code" not in prompt.output_type.lower():
            score.type_compatibility = 0.8
        else:
            score.type_compatibility = 0.4

        # Complexity fit
        is_complex_problem = len(problem_features.complexity_indicators) > 0
        is_detailed_prompt = len(prompt.template) > 200 or "step" in prompt.template.lower()
        if is_complex_problem == is_detailed_prompt:
            score.complexity_fit = 1.0
        else:
            score.complexity_fit = 0.5

        # Quality from registry
        score.prompt_quality = prompt.quality.score

        return score

    def select(
        self,
        problem: str,
        registry: PromptRegistry,
        domain_hint: DomainTag = None
    ) -> Optional[RegisteredPrompt]:
        """
        Select the most appropriate prompt for a problem.

        This is the core method implementing:
            {get appropriate prompt} → Best match

        Args:
            problem: Problem description
            registry: Prompt registry to search
            domain_hint: Optional domain to prefer

        Returns:
            Best matching prompt, or None if no good match
        """
        if not registry or len(registry) == 0:
            return None

        # Extract problem features
        features = self.extract_features(problem)

        # Override domain if hint provided
        if domain_hint:
            features.domain = domain_hint
            features.domain_confidence = 1.0

        # Get candidates (filter by minimum quality)
        candidates = [
            p for p in registry
            if p.quality.score >= self.min_quality
        ]

        if not candidates:
            return None

        # Score all candidates
        scored: List[Tuple[MatchScore, RegisteredPrompt]] = [
            (self.score_prompt(features, prompt), prompt)
            for prompt in candidates
        ]

        # Sort by score descending
        scored.sort(key=lambda x: x[0].total, reverse=True)

        # Return best if above threshold
        best_score, best_prompt = scored[0]
        if best_score.total >= self.min_match:
            return best_prompt

        return None

    def select_top_k(
        self,
        problem: str,
        registry: PromptRegistry,
        k: int = 3
    ) -> List[Tuple[MatchScore, RegisteredPrompt]]:
        """
        Select top-k matching prompts.

        Useful for:
        - Beam search in RMP
        - A/B testing
        - User selection from options
        """
        if not registry or len(registry) == 0:
            return []

        features = self.extract_features(problem)

        candidates = [
            p for p in registry
            if p.quality.score >= self.min_quality
        ]

        scored = [
            (self.score_prompt(features, prompt), prompt)
            for prompt in candidates
        ]

        scored.sort(key=lambda x: x[0].total, reverse=True)

        return scored[:k]

    def explain_selection(
        self,
        problem: str,
        registry: PromptRegistry
    ) -> str:
        """
        Explain why a prompt was selected.

        Useful for debugging and transparency.
        """
        features = self.extract_features(problem)
        top_k = self.select_top_k(problem, registry, k=3)

        lines = [
            f"Problem Analysis:",
            f"  Domain: {features.domain.name} (confidence: {features.domain_confidence:.2f})",
            f"  Keywords: {', '.join(list(features.keywords)[:5])}",
            f"  Requires code: {features.requires_code}",
            f"  Needs step-by-step: {features.requires_step_by_step}",
            "",
            "Top Matches:"
        ]

        for i, (score, prompt) in enumerate(top_k, 1):
            lines.extend([
                f"  {i}. {prompt.name} (total: {score.total:.3f})",
                f"     Domain match: {score.domain_match:.2f}",
                f"     Keyword overlap: {score.keyword_overlap:.2f}",
                f"     Quality: {score.prompt_quality:.2f}",
            ])

        if top_k:
            lines.append(f"\nSelected: {top_k[0][1].name}")
        else:
            lines.append("\nNo suitable prompt found.")

        return "\n".join(lines)


# Convenience function for {get:appropriate} syntax
def get_appropriate_prompt(
    problem: str,
    registry: PromptRegistry,
    domain_hint: DomainTag = None
) -> Optional[str]:
    """
    Get the most appropriate prompt template for a problem.

    This is the function called when resolving:
        {get:appropriate} or {appropriate:problem_domain}

    Returns the template string, or None if no match.
    """
    selector = AppropriatePromptSelector()
    prompt = selector.select(problem, registry, domain_hint)
    return prompt.template if prompt else None
