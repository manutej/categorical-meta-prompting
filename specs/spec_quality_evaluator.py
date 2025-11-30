"""
Spec Quality Evaluator using Categorical Meta-Prompting
========================================================

This module evaluates spec-kit specifications using the categorical
meta-prompting framework. It demonstrates meta-prompting applied to
its own artifacts - using RMP to improve spec quality.

Quality Dimensions (from spec-kit philosophy):
1. Completeness: All required sections present
2. Testability: User stories are independently testable
3. Clarity: Language is unambiguous
4. Categorical Rigor: Proper categorical foundations
5. Actionability: Implementation path is clear
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import re


@dataclass
class SpecQuality:
    """
    Quality vector in [0,1]^5 for spec evaluation.

    Each dimension maps to spec-kit requirements.
    """
    completeness: float = 0.0      # Required sections present
    testability: float = 0.0       # User stories are testable
    clarity: float = 0.0           # Unambiguous language
    categorical_rigor: float = 0.0 # Proper categorical structures
    actionability: float = 0.0     # Clear implementation path

    def aggregate(self) -> float:
        """Weighted aggregate score."""
        weights = {
            'completeness': 0.25,
            'testability': 0.20,
            'clarity': 0.20,
            'categorical_rigor': 0.20,
            'actionability': 0.15
        }
        return sum(weights[k] * getattr(self, k) for k in weights)

    def weakest(self) -> str:
        """Find weakest dimension."""
        dims = ['completeness', 'testability', 'clarity',
                'categorical_rigor', 'actionability']
        return min(dims, key=lambda d: getattr(self, d))

    def __str__(self) -> str:
        return (
            f"Completeness: {self.completeness:.2f} | "
            f"Testability: {self.testability:.2f} | "
            f"Clarity: {self.clarity:.2f} | "
            f"Categorical: {self.categorical_rigor:.2f} | "
            f"Actionable: {self.actionability:.2f} | "
            f"Aggregate: {self.aggregate():.3f}"
        )


class SpecEvaluator:
    """
    Evaluates spec.md files against spec-kit quality criteria.

    Uses pattern matching for heuristic evaluation.
    In production, would use LLM for deeper semantic analysis.
    """

    # Required sections for a complete spec
    REQUIRED_SECTIONS = [
        "## Overview",
        "## User Scenarios",
        "## Functional Requirements",
        "## Non-Functional Requirements",
        "## Success Criteria",
    ]

    # Optional but valuable sections
    BONUS_SECTIONS = [
        "## Categorical Structures",
        "## Data Sources",
        "## Open Questions",
        "## References",
    ]

    # Patterns indicating testable user stories
    TESTABILITY_PATTERNS = [
        r'\*\*Given\*\*.*\*\*When\*\*.*\*\*Then\*\*',
        r'Acceptance Criteria',
        r'\[[ x]\]',  # Checkbox
        r'\[P[123]\]',  # Priority markers
    ]

    # Patterns indicating clarity
    CLARITY_PATTERNS = [
        r'\bSHALL\b',
        r'\bMUST\b',
        r'\bSHOULD\b',
        r'< \d+ (seconds?|ms)',  # Specific metrics
        r'> \d+%',  # Specific percentages
    ]

    # Patterns indicating categorical rigor
    CATEGORICAL_PATTERNS = [
        r'\b(functor|Functor)\b',
        r'\b(monad|Monad)\b',
        r'\b(comonad|Comonad)\b',
        r'\b(morphism|Morphism)\b',
        r'\b(composition|compose)\b',
        r'\b(category|Category)\b',
        r'\b(tensor|⊗)\b',
        r'\b(enriched|Enriched)\b',
        r'```.*(?:Laws|Axioms)',
    ]

    # Patterns indicating actionability
    ACTIONABILITY_PATTERNS = [
        r'## Data Sources',
        r'https?://',
        r'\b(API|endpoint|database)\b',
        r'\b(install|pip|npm)\b',
        r'\b(FR-\d+|NFR-\d+)\b',
    ]

    def evaluate(self, spec_content: str) -> SpecQuality:
        """Evaluate a spec file content."""

        # Completeness: Check for required sections
        sections_found = sum(
            1 for s in self.REQUIRED_SECTIONS
            if s in spec_content
        )
        bonus_found = sum(
            1 for s in self.BONUS_SECTIONS
            if s in spec_content
        )
        completeness = (
            sections_found / len(self.REQUIRED_SECTIONS) * 0.8 +
            bonus_found / len(self.BONUS_SECTIONS) * 0.2
        )

        # Testability: Check for Given/When/Then and checkboxes
        testability_matches = sum(
            1 for p in self.TESTABILITY_PATTERNS
            if re.search(p, spec_content, re.IGNORECASE | re.DOTALL)
        )
        testability = min(1.0, testability_matches / len(self.TESTABILITY_PATTERNS))

        # Clarity: Check for specific language
        clarity_matches = sum(
            1 for p in self.CLARITY_PATTERNS
            if re.search(p, spec_content)
        )
        clarity = min(1.0, clarity_matches / len(self.CLARITY_PATTERNS))

        # Categorical Rigor: Check for categorical concepts
        categorical_matches = sum(
            1 for p in self.CATEGORICAL_PATTERNS
            if re.search(p, spec_content, re.IGNORECASE)
        )
        categorical_rigor = min(1.0, categorical_matches / len(self.CATEGORICAL_PATTERNS))

        # Actionability: Check for implementation details
        action_matches = sum(
            1 for p in self.ACTIONABILITY_PATTERNS
            if re.search(p, spec_content, re.IGNORECASE)
        )
        actionability = min(1.0, action_matches / len(self.ACTIONABILITY_PATTERNS))

        return SpecQuality(
            completeness=completeness,
            testability=testability,
            clarity=clarity,
            categorical_rigor=categorical_rigor,
            actionability=actionability
        )

    def evaluate_file(self, path: Path) -> Tuple[str, SpecQuality]:
        """Evaluate a spec file by path."""
        content = path.read_text()
        quality = self.evaluate(content)
        return path.name, quality


class SpecRMPImprover:
    """
    RMP-based spec improvement using categorical meta-prompting.

    Iteratively improves specs by targeting weakest dimension.
    """

    def __init__(self, evaluator: SpecEvaluator, threshold: float = 0.85):
        self.evaluator = evaluator
        self.threshold = threshold

    def suggest_improvement(self, spec_content: str, quality: SpecQuality) -> str:
        """Generate improvement suggestion for weakest dimension."""
        weakest = quality.weakest()

        suggestions = {
            'completeness': self._suggest_completeness,
            'testability': self._suggest_testability,
            'clarity': self._suggest_clarity,
            'categorical_rigor': self._suggest_categorical,
            'actionability': self._suggest_actionability,
        }

        return suggestions[weakest](spec_content)

    def _suggest_completeness(self, spec: str) -> str:
        missing = [s for s in SpecEvaluator.REQUIRED_SECTIONS if s not in spec]
        if missing:
            return f"ADD SECTIONS: {', '.join(missing)}"
        missing_bonus = [s for s in SpecEvaluator.BONUS_SECTIONS if s not in spec]
        if missing_bonus:
            return f"CONSIDER ADDING: {', '.join(missing_bonus[:2])}"
        return "Spec is complete."

    def _suggest_testability(self, spec: str) -> str:
        if "Given" not in spec:
            return "ADD Given/When/Then format to user stories"
        if "Acceptance Criteria" not in spec:
            return "ADD Acceptance Criteria with checkboxes to each user story"
        if "[P1]" not in spec:
            return "ADD Priority markers [P1], [P2], [P3] to user stories"
        return "User stories are testable."

    def _suggest_clarity(self, spec: str) -> str:
        if "SHALL" not in spec:
            return "USE 'SHALL' in Functional Requirements for precision"
        if not re.search(r'< \d+', spec):
            return "ADD specific metrics (e.g., '< 5 seconds', '> 95%')"
        return "Language is sufficiently clear."

    def _suggest_categorical(self, spec: str) -> str:
        terms = ['Functor', 'Monad', 'Comonad', 'Morphism', 'Composition']
        missing = [t for t in terms if t.lower() not in spec.lower()]
        if 'Categorical Structures' not in spec:
            return "ADD '## Categorical Structures' section with formal definitions"
        if missing:
            return f"CONSIDER: Add {missing[0]} structure to formalization"
        return "Categorical foundations are solid."

    def _suggest_actionability(self, spec: str) -> str:
        if "Data Sources" not in spec:
            return "ADD '## Data Sources' section with specific sources"
        if "http" not in spec.lower():
            return "ADD specific URLs/APIs to data sources"
        return "Implementation path is clear."


def evaluate_all_specs(specs_dir: Path) -> Dict[str, SpecQuality]:
    """Evaluate all spec.md files in a directory tree."""
    evaluator = SpecEvaluator()
    results = {}

    for spec_path in specs_dir.rglob("spec.md"):
        name = spec_path.parent.name
        _, quality = evaluator.evaluate_file(spec_path)
        results[name] = quality

    return results


def main():
    """Evaluate all specs and report quality."""
    specs_dir = Path(__file__).parent
    evaluator = SpecEvaluator()
    improver = SpecRMPImprover(evaluator)

    print("=" * 70)
    print("SPEC QUALITY EVALUATION (Categorical Meta-Prompting)")
    print("=" * 70)

    # Find all spec.md files
    specs = list(specs_dir.rglob("spec.md"))
    print(f"\nFound {len(specs)} specifications to evaluate\n")

    results = []
    for spec_path in sorted(specs):
        name = spec_path.parent.name
        content = spec_path.read_text()
        quality = evaluator.evaluate(content)
        suggestion = improver.suggest_improvement(content, quality)

        results.append((name, quality, suggestion))

    # Print results sorted by aggregate quality
    results.sort(key=lambda x: x[1].aggregate(), reverse=True)

    print(f"{'Spec':<35} {'Aggregate':>10} {'Weakest':<20} {'Suggestion'}")
    print("-" * 100)

    for name, quality, suggestion in results:
        aggregate = quality.aggregate()
        weakest = quality.weakest()

        # Color coding via symbols
        if aggregate >= 0.8:
            symbol = "✓"
        elif aggregate >= 0.6:
            symbol = "◐"
        else:
            symbol = "○"

        print(f"{symbol} {name:<33} {aggregate:>9.3f} {weakest:<20} {suggestion[:40]}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    avg_quality = sum(r[1].aggregate() for r in results) / len(results)
    print(f"\nAverage quality: {avg_quality:.3f}")
    print(f"Specs above threshold (0.85): {sum(1 for r in results if r[1].aggregate() >= 0.85)}/{len(results)}")

    # Quality distribution
    print("\nQuality distribution:")
    for r in results:
        name, quality, _ = r
        bar_len = int(quality.aggregate() * 40)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"  {name[:25]:<25} [{bar}] {quality.aggregate():.3f}")

    return results


if __name__ == "__main__":
    results = main()
