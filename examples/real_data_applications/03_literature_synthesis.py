"""
Example 3: Literature Review Synthesis Engine
=============================================

This example demonstrates:
- Monoidal category for composing research findings
- Functor mapping papers to structured findings
- Enriched quality for evidence strength
- Real data from Semantic Scholar API

Categorical Structures Used:
- Functor: Paper → List[Finding] (structure-preserving extraction)
- Monoidal Category: Findings compose with provenance preservation
- Enriched Category: Citation strength and confidence tracking
- Comonad: Extract synthesis context from paper collection

Data Source: Semantic Scholar API (free academic search)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set, Optional, Callable
from datetime import datetime
from enum import Enum
import json
import hashlib

# For real API calls - install with: pip install requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Note: Install requests for API calls: pip install requests")


# =============================================================================
# CATEGORICAL FOUNDATIONS
# =============================================================================

class EvidenceStrength(Enum):
    """Evidence strength levels for enriched category."""
    META_ANALYSIS = 1.0      # Highest quality
    RCT = 0.9                # Randomized controlled trial
    COHORT = 0.75            # Cohort study
    CASE_CONTROL = 0.6       # Case-control study
    CASE_SERIES = 0.4        # Case series
    OPINION = 0.2            # Expert opinion


@dataclass
class QualityScore:
    """
    Quality in [0,1]-enriched category for evidence.

    Composition uses minimum (pessimistic) for evidence chains.
    """
    value: float
    citation_count: int = 0
    evidence_type: str = "unknown"
    year: int = 2024

    def __post_init__(self):
        assert 0 <= self.value <= 1, f"Quality must be in [0,1]"

    def tensor(self, other: 'QualityScore') -> 'QualityScore':
        """
        Tensor product: combine quality scores.

        Uses geometric mean to balance both sources.
        """
        import math
        combined = math.sqrt(self.value * other.value)
        return QualityScore(
            value=combined,
            citation_count=self.citation_count + other.citation_count,
            evidence_type="synthesized"
        )


@dataclass
class Paper:
    """
    Paper as an object in our category.

    Represents a single research paper with metadata.
    """
    paper_id: str
    title: str
    authors: List[str]
    year: int
    abstract: str
    citation_count: int
    venue: str = ""
    fields: List[str] = field(default_factory=list)

    @property
    def citation_key(self) -> str:
        """Generate citation key."""
        first_author = self.authors[0].split()[-1] if self.authors else "Unknown"
        return f"{first_author}{self.year}"


@dataclass
class Finding:
    """
    Research finding as a morphism in our category.

    Findings are extracted from papers and can be composed.
    """
    finding_id: str
    claim: str
    evidence: str
    source_paper: Paper
    quality: QualityScore
    related_concepts: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.finding_id:
            # Generate deterministic ID
            content = f"{self.claim}:{self.source_paper.paper_id}"
            self.finding_id = hashlib.md5(content.encode()).hexdigest()[:12]


@dataclass
class FindingCluster:
    """
    Cluster of related findings (natural transformation result).

    Groups findings that support, contradict, or extend each other.
    """
    cluster_id: str
    theme: str
    findings: List[Finding]
    consensus_strength: float
    conflicts: List[Tuple[Finding, Finding]] = field(default_factory=list)

    @property
    def composite_quality(self) -> float:
        """Compute cluster quality via tensor product."""
        if not self.findings:
            return 0.0
        # Geometric mean of all finding qualities
        import math
        product = 1.0
        for f in self.findings:
            product *= f.quality.value
        return product ** (1.0 / len(self.findings))


@dataclass
class Synthesis:
    """
    Final synthesis result as the colimit of findings.

    Represents the categorical composition of all findings.
    """
    clusters: List[FindingCluster]
    provenance_graph: Dict[str, List[str]]  # finding_id -> [paper_ids]
    total_papers: int
    total_findings: int
    overall_confidence: float


# =============================================================================
# SEMANTIC SCHOLAR API CLIENT
# =============================================================================

class SemanticScholarClient:
    """Client for Semantic Scholar API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self):
        self.session = requests.Session() if HAS_REQUESTS else None

    def search_papers(
        self,
        query: str,
        limit: int = 20,
        fields: str = "paperId,title,authors,year,abstract,citationCount,venue,fieldsOfStudy"
    ) -> List[Paper]:
        """Search for papers by query."""
        if not HAS_REQUESTS:
            return self._mock_papers(query, limit)

        url = f"{self.BASE_URL}/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": fields
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            papers = []
            for item in data.get("data", []):
                if item.get("abstract"):  # Only papers with abstracts
                    papers.append(Paper(
                        paper_id=item.get("paperId", ""),
                        title=item.get("title", ""),
                        authors=[a.get("name", "") for a in item.get("authors", [])],
                        year=item.get("year", 2024),
                        abstract=item.get("abstract", ""),
                        citation_count=item.get("citationCount", 0),
                        venue=item.get("venue", ""),
                        fields=[f.get("category", "") for f in item.get("fieldsOfStudy", [])]
                    ))
            return papers

        except Exception as e:
            print(f"API error: {e}, using mock data")
            return self._mock_papers(query, limit)

    def _mock_papers(self, query: str, limit: int) -> List[Paper]:
        """Generate mock papers for demonstration."""
        mock_data = [
            Paper(
                paper_id="abc123",
                title="Categorical Foundations of Machine Learning",
                authors=["Bruno Gavranović", "Paul Wilson"],
                year=2024,
                abstract="We present a categorical framework for understanding machine learning systems as compositional structures. Our approach uses functors to map between data spaces and model spaces, preserving essential structure.",
                citation_count=45,
                venue="ICML 2024",
                fields=["Machine Learning", "Category Theory"]
            ),
            Paper(
                paper_id="def456",
                title="Meta-Prompting: Enhancing LLMs with Recursive Self-Improvement",
                authors=["Yifan Zhang", "John Doe"],
                year=2024,
                abstract="We introduce meta-prompting, a technique where language models iteratively improve their own prompts. Our method achieves 100% accuracy on Game of 24 and significant improvements on mathematical reasoning.",
                citation_count=128,
                venue="arXiv",
                fields=["Natural Language Processing", "Machine Learning"]
            ),
            Paper(
                paper_id="ghi789",
                title="Compositional Semantics for Neural Networks",
                authors=["Jane Smith", "Adrian de Wynter"],
                year=2023,
                abstract="This paper develops compositional semantics for neural network architectures using string diagrams. We show how attention mechanisms can be understood as natural transformations.",
                citation_count=89,
                venue="NeurIPS 2023",
                fields=["Machine Learning", "Formal Methods"]
            ),
            Paper(
                paper_id="jkl012",
                title="Enriched Categories in AI: A Practical Guide",
                authors=["Category Theory Group", "ML Lab"],
                year=2024,
                abstract="We demonstrate practical applications of enriched category theory in AI systems. Quality-enriched categories provide natural frameworks for uncertainty quantification in neural networks.",
                citation_count=32,
                venue="ICLR 2024",
                fields=["Machine Learning", "Category Theory"]
            ),
            Paper(
                paper_id="mno345",
                title="Monoidal Structures in Large Language Models",
                authors=["Research Team A"],
                year=2024,
                abstract="Large language models exhibit monoidal structure when composing prompts. We formalize this structure and show how tensor products of prompts preserve semantic relationships.",
                citation_count=67,
                venue="ACL 2024",
                fields=["Natural Language Processing"]
            ),
            Paper(
                paper_id="pqr678",
                title="Fixed Points and Language Model Convergence",
                authors=["Theoretical ML Group"],
                year=2023,
                abstract="We analyze the fixed-point behavior of iterative prompting strategies. Under certain conditions, prompt refinement converges to locally optimal solutions with provable guarantees.",
                citation_count=54,
                venue="TMLR",
                fields=["Machine Learning Theory"]
            ),
            Paper(
                paper_id="stu901",
                title="DisCoPy: A Toolkit for Categorical NLP",
                authors=["Alexis Toumi", "Giovanni de Felice"],
                year=2021,
                abstract="DisCoPy implements categorical compositional semantics for natural language processing. The library provides string diagrams, functors, and natural transformations for NLP pipelines.",
                citation_count=156,
                venue="ACL System Demo",
                fields=["Natural Language Processing", "Software"]
            ),
            Paper(
                paper_id="vwx234",
                title="Quality Metrics for Prompt Engineering",
                authors=["Prompt Engineering Lab"],
                year=2024,
                abstract="We propose a comprehensive quality framework for evaluating prompts. Our metrics include clarity, specificity, and task alignment, enabling systematic prompt optimization.",
                citation_count=41,
                venue="EMNLP 2024",
                fields=["Natural Language Processing"]
            ),
        ]
        return mock_data[:min(limit, len(mock_data))]


# =============================================================================
# CATEGORICAL LITERATURE SYNTHESIS ENGINE
# =============================================================================

class FindingExtractor:
    """
    Functor: Paper → List[Finding]

    Extracts structured findings from papers while preserving provenance.
    """

    def __init__(self):
        self.concept_patterns = [
            "categorical", "functor", "monad", "composition",
            "neural", "language model", "prompting", "meta",
            "quality", "enriched", "monoidal", "tensor"
        ]

    def extract(self, paper: Paper) -> List[Finding]:
        """
        Functor map: extract findings from a paper.

        Preserves structure: paper citations map to finding provenances.
        """
        findings = []

        # Calculate base quality from paper metrics
        citation_quality = min(1.0, paper.citation_count / 200)  # Cap at 200 citations
        recency_factor = max(0.5, 1 - (2024 - paper.year) * 0.1)  # Decay by 10% per year
        base_quality = (citation_quality * 0.6 + recency_factor * 0.4)

        # Extract concepts mentioned
        abstract_lower = paper.abstract.lower()
        mentioned_concepts = [c for c in self.concept_patterns if c in abstract_lower]

        # Create main finding from abstract
        main_finding = Finding(
            finding_id="",
            claim=self._extract_main_claim(paper),
            evidence=paper.abstract[:200] + "...",
            source_paper=paper,
            quality=QualityScore(
                value=base_quality,
                citation_count=paper.citation_count,
                evidence_type="empirical" if "experiment" in abstract_lower else "theoretical",
                year=paper.year
            ),
            related_concepts=mentioned_concepts
        )
        findings.append(main_finding)

        # Extract secondary findings if paper discusses multiple topics
        if len(mentioned_concepts) > 2:
            for concept in mentioned_concepts[:2]:
                secondary = Finding(
                    finding_id="",
                    claim=f"Paper discusses {concept} in context of {paper.title[:50]}",
                    evidence=f"Mentioned in abstract with {len(mentioned_concepts)} related concepts",
                    source_paper=paper,
                    quality=QualityScore(
                        value=base_quality * 0.8,  # Lower confidence for secondary findings
                        citation_count=paper.citation_count,
                        year=paper.year
                    ),
                    related_concepts=[concept]
                )
                findings.append(secondary)

        return findings

    def _extract_main_claim(self, paper: Paper) -> str:
        """Extract main claim from paper title and abstract."""
        # Simple extraction: use title as claim
        if ":" in paper.title:
            return paper.title.split(":")[0].strip()
        return paper.title


class LiteratureSynthesisEngine:
    """
    Categorical engine for literature synthesis.

    Uses monoidal composition to combine findings and
    natural transformations to cluster related work.
    """

    def __init__(self):
        self.client = SemanticScholarClient()
        self.extractor = FindingExtractor()

    def search_and_extract(
        self,
        query: str,
        max_papers: int = 10
    ) -> Tuple[List[Paper], List[Finding]]:
        """
        Search papers and extract findings via functor.
        """
        papers = self.client.search_papers(query, limit=max_papers)

        all_findings = []
        for paper in papers:
            findings = self.extractor.extract(paper)
            all_findings.extend(findings)

        return papers, all_findings

    def cluster_findings(
        self,
        findings: List[Finding]
    ) -> List[FindingCluster]:
        """
        Natural transformation: group related findings.

        This is a natural transformation from List[Finding] to List[Cluster].
        """
        # Group by overlapping concepts
        concept_to_findings: Dict[str, List[Finding]] = {}

        for finding in findings:
            for concept in finding.related_concepts:
                if concept not in concept_to_findings:
                    concept_to_findings[concept] = []
                concept_to_findings[concept].append(finding)

        clusters = []
        for concept, cluster_findings in concept_to_findings.items():
            if len(cluster_findings) >= 2:  # Only create clusters with 2+ findings
                # Compute consensus (how much findings agree)
                qualities = [f.quality.value for f in cluster_findings]
                consensus = sum(qualities) / len(qualities)

                cluster = FindingCluster(
                    cluster_id=f"cluster_{concept}",
                    theme=concept,
                    findings=cluster_findings,
                    consensus_strength=consensus
                )
                clusters.append(cluster)

        return sorted(clusters, key=lambda c: c.consensus_strength, reverse=True)

    def build_provenance(
        self,
        findings: List[Finding]
    ) -> Dict[str, List[str]]:
        """
        Build provenance graph for findings.

        Maps each finding to its source papers (morphism tracking).
        """
        provenance = {}
        for finding in findings:
            provenance[finding.finding_id] = [finding.source_paper.paper_id]
        return provenance

    def synthesize(
        self,
        query: str,
        max_papers: int = 10
    ) -> Synthesis:
        """
        Full synthesis pipeline using categorical composition.
        """
        print(f"\n{'='*70}")
        print("CATEGORICAL LITERATURE SYNTHESIS ENGINE")
        print(f"{'='*70}")
        print(f"\nQuery: {query}")
        print(f"Max papers: {max_papers}")

        # Phase 1: Search and extract (Functor application)
        print(f"\n{'-'*70}")
        print("Phase 1: FUNCTOR - Paper → Findings")
        print(f"{'-'*70}")

        papers, findings = self.search_and_extract(query, max_papers)

        print(f"\nFound {len(papers)} papers")
        print(f"Extracted {len(findings)} findings")

        for paper in papers[:5]:
            print(f"\n  [{paper.citation_key}] {paper.title[:60]}...")
            print(f"      Citations: {paper.citation_count} | Year: {paper.year}")

        # Phase 2: Cluster findings (Natural transformation)
        print(f"\n{'-'*70}")
        print("Phase 2: NATURAL TRANSFORMATION - Clustering")
        print(f"{'-'*70}")

        clusters = self.cluster_findings(findings)

        print(f"\nCreated {len(clusters)} thematic clusters:")
        for cluster in clusters[:5]:
            print(f"\n  Theme: {cluster.theme}")
            print(f"  Findings: {len(cluster.findings)}")
            print(f"  Consensus: {cluster.consensus_strength:.3f}")
            print(f"  Quality: {cluster.composite_quality:.3f}")

        # Phase 3: Build synthesis (Colimit)
        print(f"\n{'-'*70}")
        print("Phase 3: SYNTHESIS (Categorical Colimit)")
        print(f"{'-'*70}")

        provenance = self.build_provenance(findings)

        # Compute overall confidence via tensor product
        overall = 1.0
        for cluster in clusters:
            overall = (overall * cluster.composite_quality) ** 0.5  # Geometric mean

        synthesis = Synthesis(
            clusters=clusters,
            provenance_graph=provenance,
            total_papers=len(papers),
            total_findings=len(findings),
            overall_confidence=overall
        )

        print(f"\nSynthesis Statistics:")
        print(f"  Total papers: {synthesis.total_papers}")
        print(f"  Total findings: {synthesis.total_findings}")
        print(f"  Thematic clusters: {len(synthesis.clusters)}")
        print(f"  Overall confidence: {synthesis.overall_confidence:.4f}")

        # Generate narrative summary
        print(f"\n{'-'*70}")
        print("SYNTHESIZED NARRATIVE")
        print(f"{'-'*70}")

        self._generate_narrative(synthesis)

        return synthesis

    def _generate_narrative(self, synthesis: Synthesis):
        """Generate narrative summary from synthesis."""
        if not synthesis.clusters:
            print("\nInsufficient findings for narrative synthesis.")
            return

        print(f"\nBased on {synthesis.total_papers} papers and {synthesis.total_findings} findings:\n")

        # Report on top themes
        for i, cluster in enumerate(synthesis.clusters[:3], 1):
            print(f"{i}. Theme: {cluster.theme.upper()}")
            print(f"   Support: {len(cluster.findings)} findings")
            print(f"   Confidence: {cluster.composite_quality:.2%}")

            # List supporting papers
            papers = set(f.source_paper.citation_key for f in cluster.findings)
            print(f"   Sources: {', '.join(list(papers)[:3])}")

            # Sample finding
            if cluster.findings:
                sample = cluster.findings[0]
                print(f"   Key claim: \"{sample.claim[:80]}...\"")
            print()

        # Overall assessment
        if synthesis.overall_confidence > 0.7:
            print("SYNTHESIS ASSESSMENT: Strong consensus across literature.")
        elif synthesis.overall_confidence > 0.4:
            print("SYNTHESIS ASSESSMENT: Moderate agreement with some variation.")
        else:
            print("SYNTHESIS ASSESSMENT: Limited or conflicting evidence.")


# =============================================================================
# COMPARISON ENGINE (Enriched Category Ordering)
# =============================================================================

class LiteratureComparison:
    """Compare different research areas using enriched categories."""

    def __init__(self):
        self.engine = LiteratureSynthesisEngine()

    def compare_topics(
        self,
        topic1: str,
        topic2: str,
        papers_per_topic: int = 8
    ) -> Dict:
        """
        Compare two research topics by their literature strength.
        """
        print(f"\n{'='*70}")
        print("ENRICHED CATEGORY COMPARISON")
        print(f"{'='*70}")

        syn1 = self.engine.synthesize(topic1, papers_per_topic)
        syn2 = self.engine.synthesize(topic2, papers_per_topic)

        print(f"\n{'-'*70}")
        print("COMPARISON RESULTS")
        print(f"{'-'*70}")

        print(f"\nTopic 1: {topic1}")
        print(f"  Papers: {syn1.total_papers}")
        print(f"  Confidence: {syn1.overall_confidence:.4f}")

        print(f"\nTopic 2: {topic2}")
        print(f"  Papers: {syn2.total_papers}")
        print(f"  Confidence: {syn2.overall_confidence:.4f}")

        # Enriched comparison
        if syn1.overall_confidence > syn2.overall_confidence:
            stronger = topic1
            diff = syn1.overall_confidence - syn2.overall_confidence
        else:
            stronger = topic2
            diff = syn2.overall_confidence - syn1.overall_confidence

        print(f"\n→ '{stronger}' has stronger literature support by {diff:.4f}")

        return {
            "topic1": {"topic": topic1, "confidence": syn1.overall_confidence},
            "topic2": {"topic": topic2, "confidence": syn2.overall_confidence},
            "stronger": stronger
        }


# =============================================================================
# MAIN: Run synthesis with real data
# =============================================================================

def main():
    """
    Demonstrate categorical literature synthesis.
    """
    engine = LiteratureSynthesisEngine()

    # Example 1: Meta-prompting research
    print("\n" + "="*70)
    print("EXAMPLE 1: Meta-Prompting Research Synthesis")
    print("="*70)

    synthesis1 = engine.synthesize(
        query="meta-prompting language models recursive improvement",
        max_papers=8
    )

    # Example 2: Category theory in ML
    print("\n" + "="*70)
    print("EXAMPLE 2: Category Theory in Machine Learning")
    print("="*70)

    synthesis2 = engine.synthesize(
        query="category theory machine learning functors neural networks",
        max_papers=8
    )

    # Example 3: Compare topics
    print("\n" + "="*70)
    print("EXAMPLE 3: Topic Comparison")
    print("="*70)

    comparison = LiteratureComparison()
    comparison_result = comparison.compare_topics(
        "prompt engineering optimization",
        "neural network interpretability",
        papers_per_topic=6
    )

    return {
        "synthesis1": synthesis1,
        "synthesis2": synthesis2,
        "comparison": comparison_result
    }


if __name__ == "__main__":
    results = main()
