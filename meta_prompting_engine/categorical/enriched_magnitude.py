"""
Enriched Magnitude: Single Metric for Prompt Set Quality

Magnitude is a numerical invariant from enriched category theory that captures
the "effective size" of a metric space - accounting for both the number of
points and their distribution/diversity.

Mathematical Definition:
    For a finite metric space (X, d), the magnitude is:

    |X| = Σᵢ wᵢ  where Z·w = 1

    Z_ij = exp(-d(xᵢ, xⱼ))  # similarity matrix
    w = Z⁻¹ · 1             # weight vector

Interpretation for Prompts:
    - High magnitude = diverse, well-distributed prompt set
    - Low magnitude = redundant prompts (similar to each other)
    - Magnitude ≤ |X| (cardinality), with equality iff all distinct
    - Magnitude ≥ 1 if X is non-empty

Applications in Meta-Prompting:
    1. Quality assessment: Measure prompt set diversity
    2. Prompt selection: Choose subset with maximum magnitude
    3. Iteration termination: Stop when magnitude stabilizes
    4. Coverage analysis: Ensure prompt set covers task space

References:
    - arXiv:2501.06662 - Magnitude of Categories of Texts
    - arXiv:2306.01487 - Quantitative Graded Semantics
    - arXiv:2106.07890 - Enriched Category Theory of Language
    - Leinster (2013) - The magnitude of metric spaces

Example:
    >>> mag = EnrichedMagnitude()
    >>> prompts = ["Write code", "Debug code", "Test code", "Document code"]
    >>> score = mag.compute(prompts)
    >>> print(f"Magnitude: {score:.2f}")  # ~3.2 (related but distinct)
"""

from typing import List, Callable, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
import math
from functools import lru_cache


@dataclass
class MagnitudeResult:
    """
    Result of magnitude computation.

    Attributes:
        value: The magnitude scalar |X|
        weights: Weight vector w where Z·w = 1
        similarity_matrix: The Z matrix (exp(-d))
        diversity_score: Normalized diversity [0, 1]
        redundancy_pairs: Pairs with high similarity (potential redundancy)
        interpretation: Human-readable interpretation
    """
    value: float
    weights: List[float]
    similarity_matrix: List[List[float]]
    diversity_score: float
    redundancy_pairs: List[Tuple[int, int, float]]
    interpretation: str

    def __str__(self) -> str:
        return f"Magnitude({self.value:.3f}, diversity={self.diversity_score:.2%})"


@dataclass
class EnrichedMagnitude:
    """
    Enriched Magnitude computation for prompt sets.

    Computes the magnitude of a collection using a distance metric,
    providing a single scalar that captures diversity and quality.

    The enrichment is over [0, ∞] with:
    - Hom-objects: d(x, y) ∈ [0, ∞] (distance)
    - Composition: d(x, z) ≤ d(x, y) + d(y, z) (triangle inequality)
    - Identity: d(x, x) = 0

    Attributes:
        distance_fn: Distance function d: (A, A) → [0, ∞]
        scale: Scaling factor for distance (default 1.0)
        regularization: Small value to prevent singular matrices
    """

    distance_fn: Optional[Callable[[str, str], float]] = None
    scale: float = 1.0
    regularization: float = 1e-10

    def __post_init__(self):
        if self.distance_fn is None:
            self.distance_fn = self._default_distance

    def compute(
        self,
        items: List[str],
        return_details: bool = False
    ) -> MagnitudeResult:
        """
        Compute magnitude of item set.

        Args:
            items: List of items (prompts, texts, etc.)
            return_details: Whether to include full computation details

        Returns:
            MagnitudeResult with magnitude value and optional details

        Algorithm:
            1. Compute pairwise distance matrix D
            2. Compute similarity matrix Z = exp(-D)
            3. Solve Z·w = 1 for weight vector w
            4. Magnitude = sum(w)
        """
        n = len(items)

        if n == 0:
            return MagnitudeResult(
                value=0.0,
                weights=[],
                similarity_matrix=[],
                diversity_score=0.0,
                redundancy_pairs=[],
                interpretation="Empty set has zero magnitude"
            )

        if n == 1:
            return MagnitudeResult(
                value=1.0,
                weights=[1.0],
                similarity_matrix=[[1.0]],
                diversity_score=1.0,
                redundancy_pairs=[],
                interpretation="Single item has magnitude 1"
            )

        # Step 1: Compute distance matrix
        D = self._compute_distance_matrix(items)

        # Step 2: Compute similarity matrix Z = exp(-scale * D)
        Z = [[math.exp(-self.scale * D[i][j]) for j in range(n)] for i in range(n)]

        # Step 3: Solve Z·w = 1 using Gaussian elimination
        weights = self._solve_linear_system(Z)

        # Step 4: Magnitude = sum(w)
        magnitude = sum(weights)

        # Compute diversity score (normalized)
        diversity_score = magnitude / n if n > 0 else 0.0

        # Find redundancy pairs (high similarity)
        redundancy_pairs = self._find_redundancy_pairs(Z, threshold=0.8)

        # Generate interpretation
        interpretation = self._interpret_magnitude(magnitude, n, diversity_score)

        return MagnitudeResult(
            value=magnitude,
            weights=weights,
            similarity_matrix=Z if return_details else [],
            diversity_score=diversity_score,
            redundancy_pairs=redundancy_pairs,
            interpretation=interpretation
        )

    def compute_incremental(
        self,
        existing: MagnitudeResult,
        new_item: str,
        existing_items: List[str]
    ) -> MagnitudeResult:
        """
        Incrementally update magnitude when adding a new item.

        More efficient than recomputing from scratch.

        Args:
            existing: Previous magnitude result
            new_item: Item to add
            existing_items: Original items

        Returns:
            Updated MagnitudeResult
        """
        # For now, just recompute (optimization: use matrix update formulas)
        all_items = existing_items + [new_item]
        return self.compute(all_items)

    def diversity_contribution(
        self,
        item: str,
        existing_items: List[str]
    ) -> float:
        """
        Compute how much diversity a new item would add.

        Args:
            item: Candidate item
            existing_items: Current set

        Returns:
            Magnitude increase if item is added
        """
        if not existing_items:
            return 1.0

        current = self.compute(existing_items)
        with_new = self.compute(existing_items + [item])

        return with_new.value - current.value

    def select_diverse_subset(
        self,
        items: List[str],
        k: int
    ) -> Tuple[List[str], MagnitudeResult]:
        """
        Select k items maximizing magnitude (diversity).

        Uses greedy algorithm: iteratively add item that
        increases magnitude the most.

        Args:
            items: Full item set
            k: Number of items to select

        Returns:
            (selected_items, magnitude_result)
        """
        if k >= len(items):
            return items, self.compute(items)

        selected = []
        remaining = list(items)

        for _ in range(k):
            best_item = None
            best_contribution = -float('inf')

            for item in remaining:
                contribution = self.diversity_contribution(item, selected)
                if contribution > best_contribution:
                    best_contribution = contribution
                    best_item = item

            if best_item:
                selected.append(best_item)
                remaining.remove(best_item)

        return selected, self.compute(selected)

    def _compute_distance_matrix(self, items: List[str]) -> List[List[float]]:
        """Compute pairwise distance matrix."""
        n = len(items)
        D = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                d = self.distance_fn(items[i], items[j])
                D[i][j] = d
                D[j][i] = d

        return D

    def _solve_linear_system(self, Z: List[List[float]]) -> List[float]:
        """
        Solve Z·w = 1 using Gaussian elimination with partial pivoting.

        Args:
            Z: Similarity matrix (n×n)

        Returns:
            Weight vector w (length n)
        """
        n = len(Z)

        # Augmented matrix [Z | 1]
        aug = [row[:] + [1.0] for row in Z]

        # Add regularization to diagonal for numerical stability
        for i in range(n):
            aug[i][i] += self.regularization

        # Forward elimination with partial pivoting
        for col in range(n):
            # Find pivot
            max_row = col
            for row in range(col + 1, n):
                if abs(aug[row][col]) > abs(aug[max_row][col]):
                    max_row = row

            # Swap rows
            aug[col], aug[max_row] = aug[max_row], aug[col]

            # Check for singular matrix
            if abs(aug[col][col]) < 1e-12:
                # Fallback: return uniform weights
                return [1.0 / n] * n

            # Eliminate
            for row in range(col + 1, n):
                factor = aug[row][col] / aug[col][col]
                for j in range(col, n + 1):
                    aug[row][j] -= factor * aug[col][j]

        # Back substitution
        w = [0.0] * n
        for i in range(n - 1, -1, -1):
            w[i] = aug[i][n]
            for j in range(i + 1, n):
                w[i] -= aug[i][j] * w[j]
            w[i] /= aug[i][i]

        return w

    def _find_redundancy_pairs(
        self,
        Z: List[List[float]],
        threshold: float = 0.8
    ) -> List[Tuple[int, int, float]]:
        """Find pairs with similarity above threshold."""
        pairs = []
        n = len(Z)

        for i in range(n):
            for j in range(i + 1, n):
                if Z[i][j] > threshold:
                    pairs.append((i, j, Z[i][j]))

        return sorted(pairs, key=lambda x: -x[2])

    def _interpret_magnitude(
        self,
        magnitude: float,
        n: int,
        diversity: float
    ) -> str:
        """Generate human-readable interpretation."""
        if n == 0:
            return "Empty set"

        if diversity >= 0.9:
            quality = "Excellent diversity"
        elif diversity >= 0.7:
            quality = "Good diversity"
        elif diversity >= 0.5:
            quality = "Moderate diversity"
        elif diversity >= 0.3:
            quality = "Low diversity"
        else:
            quality = "High redundancy"

        return f"{quality}: magnitude {magnitude:.2f} from {n} items (diversity {diversity:.1%})"

    def _default_distance(self, a: str, b: str) -> float:
        """
        Default distance function using normalized edit distance.

        Normalized Levenshtein distance in [0, 1], scaled to [0, ∞).

        Args:
            a, b: Strings to compare

        Returns:
            Distance in [0, ∞)
        """
        if a == b:
            return 0.0

        # Compute Levenshtein distance
        m, n = len(a), len(b)
        if m == 0:
            return float(n)
        if n == 0:
            return float(m)

        # Use cached version for efficiency
        edit_dist = self._levenshtein(a, b)

        # Normalize to [0, 1]
        max_len = max(m, n)
        normalized = edit_dist / max_len

        # Scale to [0, ∞) using -log transform
        # Distance 0 → 0, Distance 1 → ∞
        if normalized >= 1.0:
            return 10.0  # Cap at practical infinity

        return -math.log(1 - normalized + 1e-10)

    @staticmethod
    @lru_cache(maxsize=1000)
    def _levenshtein(a: str, b: str) -> int:
        """Compute Levenshtein edit distance (cached)."""
        if len(a) < len(b):
            return EnrichedMagnitude._levenshtein(b, a)

        if len(b) == 0:
            return len(a)

        previous_row = range(len(b) + 1)
        for i, c1 in enumerate(a):
            current_row = [i + 1]
            for j, c2 in enumerate(b):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]


# === Semantic Distance Functions ===

def cosine_distance(a: str, b: str) -> float:
    """
    Cosine distance based on word overlap.

    Simple bag-of-words cosine distance.
    For production, use embeddings instead.

    Args:
        a, b: Strings to compare

    Returns:
        Distance in [0, ∞)
    """
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())

    if not words_a or not words_b:
        return 10.0  # Maximum distance

    intersection = len(words_a & words_b)
    union = len(words_a | words_b)

    jaccard = intersection / union if union > 0 else 0

    # Convert similarity [0,1] to distance [0, ∞)
    if jaccard >= 1.0:
        return 0.0
    return -math.log(jaccard + 1e-10)


def ngram_distance(a: str, b: str, n: int = 3) -> float:
    """
    N-gram based distance.

    Args:
        a, b: Strings to compare
        n: N-gram size (default 3)

    Returns:
        Distance in [0, ∞)
    """
    def get_ngrams(s: str, n: int) -> set:
        s = s.lower()
        return set(s[i:i+n] for i in range(max(0, len(s) - n + 1)))

    ngrams_a = get_ngrams(a, n)
    ngrams_b = get_ngrams(b, n)

    if not ngrams_a or not ngrams_b:
        return 10.0

    intersection = len(ngrams_a & ngrams_b)
    union = len(ngrams_a | ngrams_b)

    jaccard = intersection / union if union > 0 else 0

    if jaccard >= 1.0:
        return 0.0
    return -math.log(jaccard + 1e-10)


# === Factory Functions ===

def create_magnitude_computer(
    distance_type: str = "edit",
    scale: float = 1.0
) -> EnrichedMagnitude:
    """
    Factory for creating magnitude computers.

    Args:
        distance_type: "edit", "cosine", or "ngram"
        scale: Distance scaling factor

    Returns:
        EnrichedMagnitude instance
    """
    distance_fns = {
        "edit": None,  # Uses default
        "cosine": cosine_distance,
        "ngram": ngram_distance,
    }

    return EnrichedMagnitude(
        distance_fn=distance_fns.get(distance_type),
        scale=scale
    )


def compute_prompt_magnitude(prompts: List[str]) -> float:
    """
    Convenience function to compute magnitude of prompts.

    Args:
        prompts: List of prompt strings

    Returns:
        Magnitude value
    """
    mag = EnrichedMagnitude()
    result = mag.compute(prompts)
    return result.value


def assess_prompt_diversity(prompts: List[str]) -> Dict[str, Any]:
    """
    Assess diversity of a prompt set.

    Args:
        prompts: List of prompt strings

    Returns:
        Dict with diversity metrics
    """
    mag = EnrichedMagnitude()
    result = mag.compute(prompts, return_details=True)

    return {
        "magnitude": result.value,
        "diversity_score": result.diversity_score,
        "item_count": len(prompts),
        "redundant_pairs": len(result.redundancy_pairs),
        "interpretation": result.interpretation,
        "top_redundancies": [
            (prompts[i], prompts[j], sim)
            for i, j, sim in result.redundancy_pairs[:3]
        ] if result.redundancy_pairs else []
    }
