"""
Meta-Prompting Enhancement Loop
===============================

This is META-PROMPTING IN ACTION:
Using the categorical framework to improve descriptions of its own applications!

We take the 50 application ideas and run them through an RMP (Recursive Meta-Prompting)
loop to iteratively improve their descriptions until they meet quality thresholds.

This demonstrates:
1. RMP monad for iterative text refinement
2. Quality-enriched categories for multi-dimensional scoring
3. Pareto optimization for selecting best improvements
4. Comonad for extracting context from improvement history

The framework improves itself - true meta-level recursion!
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable
from enum import Enum
import re


# =============================================================================
# QUALITY DIMENSIONS FOR APPLICATION DESCRIPTIONS
# =============================================================================

@dataclass
class DescriptionQuality:
    """
    Quality vector in [0,1]^5 for application descriptions.

    Dimensions:
    - clarity: How clear and understandable is the description?
    - actionability: Can someone immediately start implementing?
    - categorical_depth: How well does it explain categorical concepts?
    - problem_specificity: How concrete is the problem statement?
    - data_concreteness: How specific is the data source?
    """
    clarity: float = 0.0
    actionability: float = 0.0
    categorical_depth: float = 0.0
    problem_specificity: float = 0.0
    data_concreteness: float = 0.0

    def __post_init__(self):
        for f in ['clarity', 'actionability', 'categorical_depth',
                  'problem_specificity', 'data_concreteness']:
            val = getattr(self, f)
            assert 0 <= val <= 1, f"{f} must be in [0,1]"

    def aggregate(self) -> float:
        """Weighted aggregate quality score."""
        weights = {
            'clarity': 0.25,
            'actionability': 0.20,
            'categorical_depth': 0.25,
            'problem_specificity': 0.15,
            'data_concreteness': 0.15
        }
        return sum(weights[k] * getattr(self, k) for k in weights)

    def weakest_dimension(self) -> str:
        """Find the dimension most in need of improvement."""
        dims = ['clarity', 'actionability', 'categorical_depth',
                'problem_specificity', 'data_concreteness']
        return min(dims, key=lambda d: getattr(self, d))


@dataclass
class ApplicationDescription:
    """Application description as an object in our category."""
    name: str
    domain: str
    description: str
    problem: str
    categorical_approach: str
    data_source: str


@dataclass
class MonadDescription:
    """
    Monad wrapper for description in RMP context.

    Captures iteration history and quality trajectory.
    """
    description: ApplicationDescription
    quality: DescriptionQuality
    iteration: int = 0
    history: List['MonadDescription'] = field(default_factory=list)

    @staticmethod
    def unit(desc: ApplicationDescription, quality: DescriptionQuality) -> 'MonadDescription':
        """Return: lift description into monad."""
        return MonadDescription(description=desc, quality=quality)

    def bind(self, f: Callable[[ApplicationDescription], 'MonadDescription']) -> 'MonadDescription':
        """Bind: apply improvement function."""
        improved = f(self.description)
        improved.iteration = self.iteration + 1
        improved.history = self.history + [self]
        return improved


# =============================================================================
# QUALITY EVALUATION (Enriched Category Morphism)
# =============================================================================

class QualityEvaluator:
    """
    Evaluates description quality using heuristic scoring.

    In production, this would use an LLM for evaluation.
    Here we use pattern-based heuristics for demonstration.
    """

    def __init__(self):
        # Patterns that indicate quality
        self.clarity_patterns = [
            r'\b(specifically|precisely|exactly|concretely)\b',
            r'\b(step by step|first|then|finally)\b',
            r'\b(for example|e\.g\.|such as|like)\b',
        ]
        self.actionability_patterns = [
            r'\b(implement|build|create|develop|use)\b',
            r'\b(install|configure|setup|run)\b',
            r'\b(API|library|package|tool)\b',
        ]
        self.categorical_patterns = [
            r'\b(functor|monad|comonad|morphism)\b',
            r'\b(composition|compose|tensor)\b',
            r'\b(category|categorical|enriched)\b',
            r'\b(natural transformation|Kleisli)\b',
        ]
        self.problem_patterns = [
            r'\b(problem|challenge|issue|difficulty)\b',
            r'\b(currently|traditionally|existing)\b',
            r'\b(fail|error|incorrect|suboptimal)\b',
        ]
        self.data_patterns = [
            r'\b(dataset|database|API|source)\b',
            r'\b(CSV|JSON|SQL|REST)\b',
            r'\bhttp[s]?://\b',
            r'\b(Kaggle|GitHub|UCI|arXiv)\b',
        ]

    def evaluate(self, desc: ApplicationDescription) -> DescriptionQuality:
        """Evaluate description quality across all dimensions."""
        full_text = f"{desc.description} {desc.problem} {desc.categorical_approach} {desc.data_source}"
        full_text_lower = full_text.lower()

        # Score each dimension
        clarity = self._score_dimension(full_text, self.clarity_patterns)
        clarity += 0.2 * min(1.0, len(desc.description) / 200)  # Bonus for length

        actionability = self._score_dimension(full_text, self.actionability_patterns)
        actionability += 0.2 * (1 if desc.data_source else 0)

        categorical_depth = self._score_dimension(full_text, self.categorical_patterns)
        categorical_depth *= 1.5  # Weight categorical terms higher

        problem_specificity = self._score_dimension(full_text, self.problem_patterns)
        problem_specificity += 0.3 * min(1.0, len(desc.problem) / 100)

        data_concreteness = self._score_dimension(full_text, self.data_patterns)
        data_concreteness += 0.3 * (1 if 'http' in full_text_lower or 'api' in full_text_lower else 0)

        return DescriptionQuality(
            clarity=min(1.0, clarity),
            actionability=min(1.0, actionability),
            categorical_depth=min(1.0, categorical_depth),
            problem_specificity=min(1.0, problem_specificity),
            data_concreteness=min(1.0, data_concreteness)
        )

    def _score_dimension(self, text: str, patterns: List[str]) -> float:
        """Score a single dimension based on pattern matches."""
        text_lower = text.lower()
        matches = sum(1 for p in patterns if re.search(p, text_lower))
        return min(1.0, matches / len(patterns) * 0.8)


# =============================================================================
# IMPROVEMENT FUNCTIONS (Kleisli Arrows)
# =============================================================================

class DescriptionImprover:
    """
    Improves descriptions targeting specific quality dimensions.

    Each method is a Kleisli arrow: Description → MonadDescription
    """

    def __init__(self, evaluator: QualityEvaluator):
        self.evaluator = evaluator

    def improve_clarity(self, desc: ApplicationDescription) -> MonadDescription:
        """Add clarity to description."""
        enhanced = ApplicationDescription(
            name=desc.name,
            domain=desc.domain,
            description=desc.description + " Specifically, this provides step-by-step methodology for implementation.",
            problem=desc.problem,
            categorical_approach=desc.categorical_approach + " For example, each transformation is precisely defined.",
            data_source=desc.data_source
        )
        quality = self.evaluator.evaluate(enhanced)
        return MonadDescription.unit(enhanced, quality)

    def improve_actionability(self, desc: ApplicationDescription) -> MonadDescription:
        """Add actionability to description."""
        enhanced = ApplicationDescription(
            name=desc.name,
            domain=desc.domain,
            description=desc.description + " Users can implement this using standard Python libraries.",
            problem=desc.problem,
            categorical_approach=desc.categorical_approach,
            data_source=desc.data_source + " (install via pip and configure API keys)"
        )
        quality = self.evaluator.evaluate(enhanced)
        return MonadDescription.unit(enhanced, quality)

    def improve_categorical_depth(self, desc: ApplicationDescription) -> MonadDescription:
        """Add categorical depth to description."""
        enhanced = ApplicationDescription(
            name=desc.name,
            domain=desc.domain,
            description=desc.description,
            problem=desc.problem,
            categorical_approach=desc.categorical_approach +
                " The functor preserves structure through composition, and the monad enables Kleisli composition for iterative refinement.",
            data_source=desc.data_source
        )
        quality = self.evaluator.evaluate(enhanced)
        return MonadDescription.unit(enhanced, quality)

    def improve_problem_specificity(self, desc: ApplicationDescription) -> MonadDescription:
        """Add problem specificity."""
        enhanced = ApplicationDescription(
            name=desc.name,
            domain=desc.domain,
            description=desc.description,
            problem=desc.problem + " Currently, existing solutions fail to address this systematically, leading to suboptimal outcomes.",
            categorical_approach=desc.categorical_approach,
            data_source=desc.data_source
        )
        quality = self.evaluator.evaluate(enhanced)
        return MonadDescription.unit(enhanced, quality)

    def improve_data_concreteness(self, desc: ApplicationDescription) -> MonadDescription:
        """Add data source concreteness."""
        # Add specific data source suggestions based on domain
        domain_data_sources = {
            "finance": "Available via REST API at https://api.example.com/finance",
            "healthcare": "Download from Kaggle healthcare datasets collection",
            "science": "Query via Semantic Scholar API (free, no key required)",
            "education": "EdNet dataset available at https://github.com/riiid/ednet",
            "security": "MITRE ATT&CK available at https://attack.mitre.org/",
            "legal": "CUAD dataset on Hugging Face datasets",
            "engineering": "GitHub API with public repository access",
            "data": "dbt sample projects on GitHub",
        }

        domain_lower = desc.domain.lower()
        extra_source = domain_data_sources.get(domain_lower, "Available via public API")

        enhanced = ApplicationDescription(
            name=desc.name,
            domain=desc.domain,
            description=desc.description,
            problem=desc.problem,
            categorical_approach=desc.categorical_approach,
            data_source=desc.data_source + f". {extra_source}"
        )
        quality = self.evaluator.evaluate(enhanced)
        return MonadDescription.unit(enhanced, quality)

    def targeted_improvement(self, desc: ApplicationDescription) -> MonadDescription:
        """Improve the weakest dimension."""
        current_quality = self.evaluator.evaluate(desc)
        weakest = current_quality.weakest_dimension()

        if weakest == 'clarity':
            return self.improve_clarity(desc)
        elif weakest == 'actionability':
            return self.improve_actionability(desc)
        elif weakest == 'categorical_depth':
            return self.improve_categorical_depth(desc)
        elif weakest == 'problem_specificity':
            return self.improve_problem_specificity(desc)
        else:
            return self.improve_data_concreteness(desc)


# =============================================================================
# RMP ENGINE FOR DESCRIPTION ENHANCEMENT
# =============================================================================

class MetaEnhancementEngine:
    """
    Meta-Prompting Engine for enhancing application descriptions.

    Uses RMP loop to iteratively improve descriptions until
    quality threshold is met.
    """

    def __init__(
        self,
        quality_threshold: float = 0.75,
        max_iterations: int = 5
    ):
        self.quality_threshold = quality_threshold
        self.max_iterations = max_iterations
        self.evaluator = QualityEvaluator()
        self.improver = DescriptionImprover(self.evaluator)

    def enhance(self, desc: ApplicationDescription) -> Tuple[ApplicationDescription, List[MonadDescription]]:
        """
        Run RMP loop on description until quality threshold met.

        Returns:
            - Enhanced description
            - Full improvement history
        """
        initial_quality = self.evaluator.evaluate(desc)
        current = MonadDescription.unit(desc, initial_quality)
        history = [current]

        for i in range(self.max_iterations):
            if current.quality.aggregate() >= self.quality_threshold:
                break

            # Apply targeted improvement (Kleisli arrow)
            current = current.bind(self.improver.targeted_improvement)
            history.append(current)

        return current.description, history

    def enhance_batch(
        self,
        descriptions: List[ApplicationDescription]
    ) -> List[Tuple[ApplicationDescription, List[MonadDescription]]]:
        """Enhance a batch of descriptions."""
        return [self.enhance(desc) for desc in descriptions]


# =============================================================================
# SAMPLE APPLICATION DATA
# =============================================================================

SAMPLE_APPLICATIONS = [
    ApplicationDescription(
        name="Drug Interaction Checker",
        domain="Healthcare",
        description="Check drug interactions using categorical composition",
        problem="Drug combinations complex",
        categorical_approach="Monoidal category with tensor product",
        data_source="DrugBank"
    ),
    ApplicationDescription(
        name="Portfolio Optimization",
        domain="Finance",
        description="Optimize portfolios with iterative refinement",
        problem="One-shot optimization insufficient",
        categorical_approach="RMP monad for iteration",
        data_source="Yahoo Finance"
    ),
    ApplicationDescription(
        name="Literature Synthesis",
        domain="Science",
        description="Synthesize findings from papers",
        problem="Manual review slow",
        categorical_approach="Functor from papers to findings",
        data_source="Semantic Scholar"
    ),
    ApplicationDescription(
        name="Threat Model Builder",
        domain="Security",
        description="Build threat models compositionally",
        problem="Attack paths missed",
        categorical_approach="Category of states with attack morphisms",
        data_source="MITRE ATT&CK"
    ),
    ApplicationDescription(
        name="Contract Clause Composer",
        domain="Legal",
        description="Compose contract clauses safely",
        problem="Clause conflicts",
        categorical_approach="Monoidal category of clauses",
        data_source="CUAD dataset"
    ),
]


# =============================================================================
# MAIN: RUN META-ENHANCEMENT
# =============================================================================

def main():
    """
    Demonstrate meta-prompting enhancement loop.

    This is the framework improving itself!
    """
    print("="*70)
    print("META-PROMPTING ENHANCEMENT LOOP")
    print("="*70)
    print("\nUsing the categorical framework to improve its own applications!")
    print("This is true meta-level recursion.\n")

    engine = MetaEnhancementEngine(quality_threshold=0.70, max_iterations=5)

    for app in SAMPLE_APPLICATIONS:
        print(f"\n{'-'*70}")
        print(f"ENHANCING: {app.name} ({app.domain})")
        print(f"{'-'*70}")

        enhanced, history = engine.enhance(app)

        print(f"\nIteration history:")
        for i, h in enumerate(history):
            quality = h.quality.aggregate()
            bar_len = int(quality * 30)
            bar = "█" * bar_len + "░" * (30 - bar_len)

            if i == 0:
                print(f"  {i}: [{bar}] {quality:.3f} (initial)")
            else:
                weakest = history[i-1].quality.weakest_dimension()
                print(f"  {i}: [{bar}] {quality:.3f} (improved {weakest})")

        print(f"\nBEFORE:")
        print(f"  Description: {app.description}")
        print(f"  Categorical: {app.categorical_approach}")
        print(f"  Data: {app.data_source}")

        print(f"\nAFTER (iteration {len(history)-1}):")
        print(f"  Description: {enhanced.description[:100]}...")
        print(f"  Categorical: {enhanced.categorical_approach[:100]}...")
        print(f"  Data: {enhanced.data_source}")

        print(f"\nQuality improvement: {history[0].quality.aggregate():.3f} → {history[-1].quality.aggregate():.3f}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    total_improvement = 0
    for app in SAMPLE_APPLICATIONS:
        _, history = engine.enhance(app)
        improvement = history[-1].quality.aggregate() - history[0].quality.aggregate()
        total_improvement += improvement
        print(f"  {app.name}: +{improvement:.3f}")

    print(f"\n  Average improvement: +{total_improvement/len(SAMPLE_APPLICATIONS):.3f}")
    print(f"  Target threshold: {engine.quality_threshold}")

    return engine


if __name__ == "__main__":
    engine = main()
