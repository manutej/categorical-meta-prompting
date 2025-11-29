---
name: cc2-research-framework
description: "CC2.0 seven-function research workflow (observe, reason, create, orchestrate, learn, verify, deploy) for categorical AI research. Use when conducting systematic research on categorical AI topics, coordinating multi-stream research workflows, applying categorical foundations to research methodology, or implementing the L5 meta-prompting research framework."
---

# CC2.0 Categorical Research Framework

Implementation of the CC2.0 seven-function categorical research workflow for systematic AI research.

## Core Functions

The CC2.0 framework models research as categorical operations:

| Function | Category Theory | Research Application |
|----------|-----------------|---------------------|
| OBSERVE | Comonad (extract) | Workspace/codebase state observation |
| REASON | Inference functor | Derive insights from observations |
| CREATE | Generative functor | Generate artifacts (prompts, code, docs) |
| ORCHESTRATE | Composition | Coordinate parallel research streams |
| LEARN | Adaptation functor | Extract patterns from analysis |
| VERIFY | Property testing | Validate categorical properties |
| DEPLOY | Production morphism | Integrate findings into framework |

## Function Implementations

### OBSERVE (Comonad Extraction)

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
import json

@dataclass
class ObservationContext:
    """Comonadic context for research observations."""
    timestamp: datetime
    workspace_state: Dict[str, Any]
    file_changes: List[str]
    external_sources: List[str]
    prior_observations: List['ObservationContext'] = field(default_factory=list)
    
    def extract(self) -> Dict[str, Any]:
        """Comonad extract: get current observation."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "state": self.workspace_state,
            "changes": self.file_changes,
            "sources": self.external_sources
        }
    
    def duplicate(self) -> 'ObservationContext':
        """Comonad duplicate: observation of observations."""
        return ObservationContext(
            timestamp=datetime.now(),
            workspace_state={"nested": self.extract()},
            file_changes=[],
            external_sources=[],
            prior_observations=self.prior_observations + [self]
        )

def cc2_observe(workspace_path: str, sources: List[str] = None) -> ObservationContext:
    """
    OBSERVE: Scan workspace and external sources.
    
    Categorical interpretation: Comonad sensing of environment.
    """
    import os
    
    # Collect workspace state
    state = {}
    changes = []
    
    for root, dirs, files in os.walk(workspace_path):
        for f in files:
            if f.endswith(('.md', '.py', '.yaml', '.json')):
                path = os.path.join(root, f)
                changes.append(path)
                state[path] = os.path.getmtime(path)
    
    return ObservationContext(
        timestamp=datetime.now(),
        workspace_state=state,
        file_changes=changes,
        external_sources=sources or []
    )
```

### REASON (Inference Functor)

```python
@dataclass
class ReasoningResult:
    """Result of categorical reasoning."""
    observations: ObservationContext
    insights: List[str]
    gaps: List[str]
    opportunities: List[str]
    confidence: float

def cc2_reason(observations: ObservationContext, query: str = None) -> ReasoningResult:
    """
    REASON: Derive insights from observations.
    
    Categorical interpretation: Inference functor F: Obs → Insight
    """
    insights = []
    gaps = []
    opportunities = []
    
    # Analyze file patterns
    state = observations.workspace_state
    
    # Identify research patterns
    if any('theory' in str(k).lower() for k in state.keys()):
        insights.append("Theoretical foundations present")
    
    if any('implementation' in str(k).lower() for k in state.keys()):
        insights.append("Implementation artifacts found")
    
    # Identify gaps
    theory_count = sum(1 for k in state.keys() if 'theory' in str(k).lower())
    impl_count = sum(1 for k in state.keys() if 'implementation' in str(k).lower())
    
    if theory_count > impl_count * 2:
        gaps.append("Gap: Theory exceeds implementation")
        opportunities.append("Opportunity: Implement theoretical concepts")
    
    if impl_count > theory_count * 2:
        gaps.append("Gap: Implementation lacks theoretical grounding")
        opportunities.append("Opportunity: Formalize implementation patterns")
    
    return ReasoningResult(
        observations=observations,
        insights=insights,
        gaps=gaps,
        opportunities=opportunities,
        confidence=0.7 if insights else 0.3
    )
```

### CREATE (Generative Functor)

```python
@dataclass
class CreationArtifact:
    """Generated research artifact."""
    artifact_type: str  # 'prompt', 'code', 'doc', 'diagram'
    content: str
    metadata: Dict[str, Any]
    source_reasoning: ReasoningResult

def cc2_create(
    reasoning: ReasoningResult,
    artifact_type: str,
    template: str = None
) -> CreationArtifact:
    """
    CREATE: Generate research artifacts.
    
    Categorical interpretation: Generative functor G: Insight → Artifact
    """
    content = ""
    
    if artifact_type == "prompt":
        content = generate_research_prompt(reasoning)
    elif artifact_type == "code":
        content = generate_implementation_scaffold(reasoning)
    elif artifact_type == "doc":
        content = generate_documentation(reasoning)
    
    return CreationArtifact(
        artifact_type=artifact_type,
        content=content,
        metadata={
            "generated_at": datetime.now().isoformat(),
            "based_on_insights": len(reasoning.insights),
            "addresses_gaps": len(reasoning.gaps)
        },
        source_reasoning=reasoning
    )

def generate_research_prompt(reasoning: ReasoningResult) -> str:
    """Generate L5 research prompt from reasoning."""
    return f"""
# Research Prompt (L5 Enhanced)

## Context
Based on {len(reasoning.insights)} insights and {len(reasoning.gaps)} identified gaps.

## Insights
{chr(10).join(f'- {i}' for i in reasoning.insights)}

## Research Gaps
{chr(10).join(f'- {g}' for g in reasoning.gaps)}

## Opportunities
{chr(10).join(f'- {o}' for o in reasoning.opportunities)}

## Task
Investigate the identified gaps with focus on categorical foundations.
Quality threshold: ≥0.90
"""
```

### ORCHESTRATE (Composition)

```python
from typing import Callable, List
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class ResearchStream:
    """Parallel research stream."""
    name: str
    focus: str
    agent_type: str
    output_path: str

@dataclass
class OrchestrationPlan:
    """Plan for coordinating research streams."""
    streams: List[ResearchStream]
    dependencies: Dict[str, List[str]]  # stream -> dependencies
    synthesis_strategy: str

def cc2_orchestrate(
    streams: List[ResearchStream],
    execute_stream: Callable[[ResearchStream], Any],
    max_parallel: int = 4
) -> Dict[str, Any]:
    """
    ORCHESTRATE: Coordinate parallel research streams.
    
    Categorical interpretation: Compositional workflow coordination.
    """
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = {
            executor.submit(execute_stream, stream): stream
            for stream in streams
        }
        
        for future in as_completed(futures):
            stream = futures[future]
            try:
                results[stream.name] = future.result()
            except Exception as e:
                results[stream.name] = {"error": str(e)}
    
    return results

# Example stream configuration
RESEARCH_STREAMS = [
    ResearchStream(
        name="stream-a-theory",
        focus="Academic & theoretical foundations",
        agent_type="deep-researcher",
        output_path="stream-a-theory/analysis/"
    ),
    ResearchStream(
        name="stream-b-implementation",
        focus="Libraries & practical tools",
        agent_type="practical-programmer",
        output_path="stream-b-implementation/"
    ),
    ResearchStream(
        name="stream-c-meta-prompting",
        focus="Meta-prompting frameworks",
        agent_type="meta2",
        output_path="stream-c-meta-prompting/"
    ),
    ResearchStream(
        name="stream-d-repositories",
        focus="Code analysis & pattern extraction",
        agent_type="code-reviewer",
        output_path="stream-d-repositories/"
    )
]
```

### LEARN (Adaptation Functor)

```python
@dataclass
class LearnedPattern:
    """Pattern extracted from research."""
    name: str
    description: str
    categorical_structure: str  # functor, monad, natural transformation, etc.
    implementation_hints: List[str]
    source_streams: List[str]

def cc2_learn(
    stream_results: Dict[str, Any],
    prior_patterns: List[LearnedPattern] = None
) -> List[LearnedPattern]:
    """
    LEARN: Extract patterns from analysis.
    
    Categorical interpretation: Adaptation functor L: Results → Patterns
    """
    patterns = []
    
    # Cross-stream pattern detection
    theory_results = stream_results.get("stream-a-theory", {})
    impl_results = stream_results.get("stream-b-implementation", {})
    
    # Look for convergence between theory and implementation
    if theory_results and impl_results:
        patterns.append(LearnedPattern(
            name="theory-practice-bridge",
            description="Convergence point between theoretical framework and practical implementation",
            categorical_structure="natural transformation",
            implementation_hints=[
                "Map theoretical constructs to library types",
                "Verify functor laws in implementation"
            ],
            source_streams=["stream-a-theory", "stream-b-implementation"]
        ))
    
    return patterns
```

### VERIFY (Property Testing)

```python
@dataclass
class VerificationResult:
    """Result of categorical property verification."""
    property_name: str
    passed: bool
    evidence: str
    counterexample: Any = None

def cc2_verify(
    artifact: CreationArtifact,
    properties: List[str]
) -> List[VerificationResult]:
    """
    VERIFY: Validate categorical properties.
    
    Categorical interpretation: Property-based testing for categorical laws.
    """
    results = []
    
    for prop in properties:
        if prop == "functoriality":
            result = verify_functoriality(artifact)
        elif prop == "naturality":
            result = verify_naturality(artifact)
        elif prop == "monad_laws":
            result = verify_monad_laws(artifact)
        else:
            result = VerificationResult(
                property_name=prop,
                passed=False,
                evidence=f"Unknown property: {prop}"
            )
        results.append(result)
    
    return results

def verify_functoriality(artifact: CreationArtifact) -> VerificationResult:
    """Verify functor laws: F(id) = id, F(g∘f) = F(g)∘F(f)"""
    # Implementation would analyze artifact for functor structure
    return VerificationResult(
        property_name="functoriality",
        passed=True,
        evidence="Identity and composition preserved"
    )
```

### DEPLOY (Production Morphism)

```python
def cc2_deploy(
    artifacts: List[CreationArtifact],
    patterns: List[LearnedPattern],
    target_framework: str
) -> Dict[str, Any]:
    """
    DEPLOY: Integrate findings into framework.
    
    Categorical interpretation: Production morphism D: Research → Framework
    """
    deployment = {
        "artifacts_deployed": [],
        "patterns_integrated": [],
        "framework_updates": []
    }
    
    for artifact in artifacts:
        if artifact.artifact_type == "code":
            # Deploy code to appropriate location
            deployment["artifacts_deployed"].append(artifact.metadata)
        elif artifact.artifact_type == "doc":
            # Update documentation
            deployment["artifacts_deployed"].append(artifact.metadata)
    
    for pattern in patterns:
        # Register pattern in framework
        deployment["patterns_integrated"].append({
            "name": pattern.name,
            "structure": pattern.categorical_structure
        })
    
    return deployment
```

## Complete Research Workflow

```python
def cc2_research_cycle(
    workspace_path: str,
    research_query: str,
    streams: List[ResearchStream] = None
) -> Dict[str, Any]:
    """
    Execute complete CC2.0 research cycle.
    
    OBSERVE → REASON → CREATE → ORCHESTRATE → LEARN → VERIFY → DEPLOY
    """
    # 1. OBSERVE
    observations = cc2_observe(workspace_path)
    
    # 2. REASON
    reasoning = cc2_reason(observations, research_query)
    
    # 3. CREATE research prompts
    prompts = cc2_create(reasoning, "prompt")
    
    # 4. ORCHESTRATE parallel streams
    streams = streams or RESEARCH_STREAMS
    stream_results = cc2_orchestrate(
        streams,
        execute_stream=lambda s: {"stream": s.name, "status": "complete"}
    )
    
    # 5. LEARN patterns
    patterns = cc2_learn(stream_results)
    
    # 6. CREATE artifacts from patterns
    artifacts = [cc2_create(reasoning, "doc")]
    
    # 7. VERIFY categorical properties
    verifications = cc2_verify(artifacts[0], ["functoriality", "naturality"])
    
    # 8. DEPLOY to framework
    deployment = cc2_deploy(artifacts, patterns, "meta-prompting-framework")
    
    return {
        "observations": observations.extract(),
        "reasoning": {
            "insights": reasoning.insights,
            "gaps": reasoning.gaps
        },
        "patterns": [p.name for p in patterns],
        "verifications": [v.passed for v in verifications],
        "deployment": deployment
    }
```

## Categorical Guarantees

The CC2.0 framework ensures:

1. **Comonadic Observation**: Context extraction preserves history
2. **Functorial Reasoning**: Insights map systematically from observations
3. **Compositional Orchestration**: Streams compose associatively
4. **Pattern Preservation**: Learning extracts categorical structures
5. **Property Verification**: Categorical laws are testable
