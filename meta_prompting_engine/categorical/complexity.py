"""
Task complexity analysis for functor object mapping.

Analyzes tasks to determine their complexity (0.0-1.0), which
drives strategy selection in the F: Tasks → Prompts functor.
"""

from .types import Task, ComplexityAnalysis
import re


def analyze_complexity(task: Task) -> ComplexityAnalysis:
    """
    Analyze task complexity across multiple dimensions.

    Complexity Dimensions:
    - Algorithmic: Problem-solving complexity
    - Domain: Required domain knowledge
    - Ambiguity: Clarity of task specification
    - Scale: Input/output size

    Args:
        task: Input task to analyze

    Returns:
        ComplexityAnalysis with overall score [0.0, 1.0]

    Example:
        >>> task = Task("Find maximum in [3,1,4,1,5,9]")
        >>> analysis = analyze_complexity(task)
        >>> assert 0.2 <= analysis.overall <= 0.4  # Low complexity
    """
    dimensions = {}

    # Algorithmic complexity (based on keywords and structure)
    dimensions['algorithmic'] = _analyze_algorithmic_complexity(task)

    # Domain knowledge requirement
    dimensions['domain'] = _analyze_domain_complexity(task)

    # Ambiguity in specification
    dimensions['ambiguity'] = _analyze_ambiguity(task)

    # Scale (input/output size)
    dimensions['scale'] = _analyze_scale(task)

    # Overall = weighted average
    weights = {
        'algorithmic': 0.4,
        'domain': 0.3,
        'ambiguity': 0.2,
        'scale': 0.1
    }

    overall = sum(dimensions[k] * weights[k] for k in dimensions)

    return ComplexityAnalysis(
        overall=overall,
        dimensions=dimensions,
        confidence=0.85  # Heuristic-based, moderate confidence
    )


def _analyze_algorithmic_complexity(task: Task) -> float:
    """
    Analyze algorithmic complexity based on task description keywords.

    Complexity Indicators:
    - High: optimize, minimize, maximize, recursive, dynamic, backtrack
    - Medium: search, sort, filter, transform
    - Low: find, count, sum, max, min

    Args:
        task: Input task

    Returns:
        Algorithmic complexity [0.0, 1.0]
    """
    desc_lower = task.description.lower()

    # High complexity keywords
    high_keywords = [
        'optimize', 'minimize', 'maximum', 'recursive',
        'dynamic programming', 'backtrack', 'np-hard',
        'algorithm', 'complexity', 'efficient'
    ]

    # Medium complexity keywords
    medium_keywords = [
        'search', 'sort', 'filter', 'transform',
        'group', 'aggregate', 'merge', 'split'
    ]

    # Low complexity keywords
    low_keywords = [
        'find', 'count', 'sum', 'max', 'min',
        'first', 'last', 'get', 'list'
    ]

    # Count keyword matches
    high_count = sum(1 for kw in high_keywords if kw in desc_lower)
    medium_count = sum(1 for kw in medium_keywords if kw in desc_lower)
    low_count = sum(1 for kw in low_keywords if kw in desc_lower)

    # Compute score
    if high_count > 0:
        return 0.8 + (0.2 * min(high_count / 3, 1.0))
    elif medium_count > 0:
        return 0.4 + (0.4 * min(medium_count / 3, 1.0))
    elif low_count > 0:
        return 0.1 + (0.3 * min(low_count / 3, 1.0))
    else:
        return 0.5  # Default if no keywords match


def _analyze_domain_complexity(task: Task) -> float:
    """
    Analyze domain knowledge requirement.

    Domain Indicators:
    - High: specialized terminology, domain-specific task type
    - Medium: general programming concepts
    - Low: basic operations

    Args:
        task: Input task

    Returns:
        Domain complexity [0.0, 1.0]
    """
    # Domain-specific task types
    high_domain_types = ['quantum', 'biology', 'finance', 'medical', 'legal']
    medium_domain_types = ['coding', 'math', 'data', 'analysis']
    low_domain_types = ['general', 'text', 'simple']

    task_type = task.type.lower()

    if any(d in task_type for d in high_domain_types):
        return 0.8
    elif any(d in task_type for d in medium_domain_types):
        return 0.4
    else:
        return 0.2


def _analyze_ambiguity(task: Task) -> float:
    """
    Analyze ambiguity in task specification.

    Ambiguity Indicators:
    - High: vague language, missing constraints
    - Medium: some specification but open-ended
    - Low: clear, specific, with examples

    Args:
        task: Input task

    Returns:
        Ambiguity score [0.0, 1.0]
    """
    # Low ambiguity: has examples and constraints
    if task.examples and task.constraints:
        return 0.2

    # Medium ambiguity: has either examples or constraints
    if task.examples or task.constraints:
        return 0.5

    # High ambiguity: vague language
    vague_words = ['somehow', 'maybe', 'kind of', 'sort of', 'approximately']
    desc_lower = task.description.lower()

    if any(word in desc_lower for word in vague_words):
        return 0.9

    # Check for question marks (often indicates ambiguity)
    if '?' in task.description and len(task.description.split('?')) > 2:
        return 0.7

    return 0.6  # Default moderate ambiguity


def _analyze_scale(task: Task) -> float:
    """
    Analyze input/output scale.

    Scale Indicators:
    - High: mentions of "large", "millions", "streaming"
    - Medium: typical data sizes
    - Low: small inputs

    Args:
        task: Input task

    Returns:
        Scale complexity [0.0, 1.0]
    """
    desc_lower = task.description.lower()

    # Large scale indicators
    large_keywords = ['million', 'billion', 'large', 'huge', 'massive', 'stream', 'big data']

    # Extract numbers from description
    numbers = re.findall(r'\d+', task.description)

    # Check for large scale keywords
    if any(kw in desc_lower for kw in large_keywords):
        return 0.9

    # Check for large numbers
    if numbers:
        max_num = max(int(n) for n in numbers)
        if max_num > 1_000_000:
            return 0.9
        elif max_num > 10_000:
            return 0.6
        elif max_num > 1_000:
            return 0.3

    return 0.2  # Default small scale
