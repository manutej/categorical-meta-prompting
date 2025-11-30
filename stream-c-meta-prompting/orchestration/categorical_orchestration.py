"""
Categorical Orchestration for Multi-Agent Meta-Prompting

This module implements orchestration patterns using categorical structures,
enabling coordination of multiple agents/models in meta-prompting workflows.

Key Patterns:
1. Monoidal Composition: Parallel agent execution with tensor products
2. Functor Chains: Sequential transformation pipelines
3. Comonadic Coordination: Context-sharing between agents
4. Natural Transformation Routing: Strategy selection between approaches

Inspired by:
- LangGraph: State machine orchestration
- VoltAgent: Multi-agent patterns
- Category theory: Monoidal categories and string diagrams

References:
- Spivak & Niu (2021) - Polynomial Functors and Lenses
- Gavranović et al. (2024) - Categorical Deep Learning
"""

from typing import TypeVar, Generic, Callable, List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time


# Type variables
A = TypeVar('A')
B = TypeVar('B')
S = TypeVar('S')  # State


class AgentType(Enum):
    """Types of agents in the orchestration"""
    OBSERVER = "observer"      # W (Comonad) - context extraction
    REASONER = "reasoner"      # F (Functor) - task analysis
    CREATOR = "creator"        # M (Monad) - prompt generation
    VERIFIER = "verifier"      # Property testing
    ORCHESTRATOR = "orchestrator"  # Coordinates others


@dataclass
class AgentState(Generic[S]):
    """
    State carried by an agent.

    In categorical terms, this is an object in the state category.
    Agents are endofunctors on this category.
    """
    data: S
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[S] = field(default_factory=list)
    quality: float = 0.5

    def update(self, new_data: S) -> 'AgentState[S]':
        """Create new state with history"""
        return AgentState(
            data=new_data,
            metadata=self.metadata,
            history=self.history + [self.data],
            quality=self.quality
        )


@dataclass
class Agent(ABC, Generic[A, B]):
    """
    Base class for categorical agents.

    Each agent is a morphism in the appropriate category:
    - Observer: W(A) → A (comonad extract)
    - Reasoner: T → P (functor map)
    - Creator: P → M(P) (monad operations)
    - Verifier: A → Bool (property checking)
    """
    name: str
    agent_type: AgentType
    config: Dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    async def execute(self, input_state: AgentState[A]) -> AgentState[B]:
        """Execute the agent on input state"""
        pass


@dataclass
class ObserverAgent(Agent[Any, Dict[str, Any]]):
    """
    Observer agent implementing comonad extract.

    Extracts focused observations from rich context.
    Corresponds to CC2.0 OBSERVE function.
    """
    agent_type: AgentType = AgentType.OBSERVER
    focus_keys: List[str] = field(default_factory=list)

    async def execute(self, input_state: AgentState[Any]) -> AgentState[Dict[str, Any]]:
        """Extract focused observations"""
        # Comonad extract: W(A) → A
        data = input_state.data

        # Focus on specific aspects
        if isinstance(data, dict):
            focused = {k: data.get(k) for k in self.focus_keys if k in data}
        else:
            focused = {"raw": data}

        # Add observation metadata
        focused["_observation_time"] = time.time()
        focused["_history_depth"] = len(input_state.history)

        return input_state.update(focused)


@dataclass
class ReasonerAgent(Agent[Dict[str, Any], Dict[str, Any]]):
    """
    Reasoner agent implementing functor map.

    Analyzes tasks and transforms understanding.
    Corresponds to CC2.0 REASON function.
    """
    agent_type: AgentType = AgentType.REASONER
    analysis_func: Optional[Callable[[Dict], Dict]] = None

    async def execute(self, input_state: AgentState[Dict[str, Any]]) -> AgentState[Dict[str, Any]]:
        """Apply reasoning transformation"""
        # Functor map: F(f) where f is analysis
        data = input_state.data

        if self.analysis_func:
            analyzed = self.analysis_func(data)
        else:
            # Default analysis
            analyzed = {
                **data,
                "_complexity": self._estimate_complexity(data),
                "_strategy": self._select_strategy(data),
                "_reasoning_applied": True
            }

        return input_state.update(analyzed)

    def _estimate_complexity(self, data: Dict) -> float:
        """Estimate task complexity"""
        # Simple heuristic based on data size
        return min(len(str(data)) / 1000, 1.0)

    def _select_strategy(self, data: Dict) -> str:
        """Select strategy based on complexity"""
        complexity = self._estimate_complexity(data)
        if complexity < 0.3:
            return "direct"
        elif complexity < 0.7:
            return "chain_of_thought"
        else:
            return "tree_of_thoughts"


@dataclass
class CreatorAgent(Agent[Dict[str, Any], str]):
    """
    Creator agent implementing monad operations.

    Generates prompts and content with recursive improvement.
    Corresponds to CC2.0 CREATE function.
    """
    agent_type: AgentType = AgentType.CREATOR
    template: str = ""
    quality_threshold: float = 0.8

    async def execute(self, input_state: AgentState[Dict[str, Any]]) -> AgentState[str]:
        """Generate content via monadic operations"""
        data = input_state.data

        # Monad unit: lift to M(P)
        prompt = self._generate_prompt(data)

        # Monad bind: recursive improvement until threshold
        quality = self._assess_quality(prompt, data)
        iterations = 0

        while quality < self.quality_threshold and iterations < 5:
            prompt = self._improve_prompt(prompt, data)
            quality = self._assess_quality(prompt, data)
            iterations += 1

        new_state = input_state.update(prompt)
        new_state.quality = quality
        new_state.metadata["iterations"] = iterations

        return new_state

    def _generate_prompt(self, data: Dict) -> str:
        """Generate initial prompt"""
        if self.template:
            return self.template.format(**data)
        return f"Task: {data.get('task', 'unknown')}\nContext: {data}"

    def _assess_quality(self, prompt: str, data: Dict) -> float:
        """Assess prompt quality"""
        # Simple heuristic
        has_task = "task" in prompt.lower()
        has_context = len(prompt) > 50
        is_structured = "\n" in prompt
        return (has_task * 0.4 + has_context * 0.3 + is_structured * 0.3)

    def _improve_prompt(self, prompt: str, data: Dict) -> str:
        """Improve prompt quality"""
        improvements = []
        if "step" not in prompt.lower():
            improvements.append("\nApproach this step by step:")
        if "verify" not in prompt.lower():
            improvements.append("\nVerify your answer.")
        return prompt + "".join(improvements)


@dataclass
class VerifierAgent(Agent[str, Tuple[bool, str]]):
    """
    Verifier agent implementing property checking.

    Validates outputs against specifications.
    Corresponds to CC2.0 VERIFY function.
    """
    agent_type: AgentType = AgentType.VERIFIER
    validators: List[Callable[[str], Tuple[bool, str]]] = field(default_factory=list)

    async def execute(self, input_state: AgentState[str]) -> AgentState[Tuple[bool, str]]:
        """Verify content against validators"""
        content = input_state.data
        all_passed = True
        messages = []

        for validator in self.validators:
            passed, message = validator(content)
            if not passed:
                all_passed = False
                messages.append(message)

        result = (all_passed, "; ".join(messages) if messages else "All validations passed")
        return input_state.update(result)


# =============================================================================
# MONOIDAL COMPOSITION (Parallel Execution)
# =============================================================================

@dataclass
class TensorProduct(Generic[A, B]):
    """
    Tensor product for parallel agent execution.

    In a monoidal category, A ⊗ B represents parallel composition.
    For agents, this means running them concurrently on shared state.
    """
    left: AgentState[A]
    right: AgentState[B]

    def combine(self) -> AgentState[Tuple[A, B]]:
        """Combine tensor product into single state"""
        return AgentState(
            data=(self.left.data, self.right.data),
            metadata={**self.left.metadata, **self.right.metadata},
            history=[],
            quality=(self.left.quality + self.right.quality) / 2
        )


async def parallel_execute(
    agents: List[Agent],
    state: AgentState
) -> List[AgentState]:
    """
    Execute agents in parallel (monoidal tensor).

    Corresponds to the tensor product in a monoidal category.
    """
    tasks = [agent.execute(state) for agent in agents]
    results = await asyncio.gather(*tasks)
    return list(results)


# =============================================================================
# FUNCTOR CHAINS (Sequential Pipelines)
# =============================================================================

@dataclass
class AgentChain:
    """
    Chain of agents forming a functor composition.

    F₁ ; F₂ ; ... ; Fₙ = Fₙ ∘ ... ∘ F₂ ∘ F₁
    """
    agents: List[Agent]
    name: str = "chain"

    async def execute(self, initial_state: AgentState) -> AgentState:
        """Execute chain sequentially"""
        current_state = initial_state

        for agent in self.agents:
            current_state = await agent.execute(current_state)

        return current_state

    def compose(self, other: 'AgentChain') -> 'AgentChain':
        """Compose two chains"""
        return AgentChain(
            agents=self.agents + other.agents,
            name=f"{self.name};{other.name}"
        )


# =============================================================================
# NATURAL TRANSFORMATION ROUTING
# =============================================================================

class StrategyRouter:
    """
    Router that selects between agent strategies.

    Implements natural transformation α: F ⇒ G
    where F and G are different prompting strategies.
    """

    def __init__(self):
        self.strategies: Dict[str, AgentChain] = {}
        self.selector: Optional[Callable[[AgentState], str]] = None

    def register_strategy(self, name: str, chain: AgentChain):
        """Register a strategy"""
        self.strategies[name] = chain

    def set_selector(self, selector: Callable[[AgentState], str]):
        """Set strategy selection function"""
        self.selector = selector

    async def route(self, state: AgentState) -> AgentState:
        """Route to appropriate strategy"""
        if not self.selector:
            # Default: use first strategy
            strategy_name = list(self.strategies.keys())[0]
        else:
            strategy_name = self.selector(state)

        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        chain = self.strategies[strategy_name]
        return await chain.execute(state)


# =============================================================================
# ORCHESTRATION PATTERNS
# =============================================================================

@dataclass
class OrchestrationPattern:
    """Base class for orchestration patterns"""
    name: str

    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        pass


@dataclass
class MapReducePattern(OrchestrationPattern):
    """
    Map-Reduce pattern using categorical structure.

    Map: Apply functor F to each element (parallel)
    Reduce: Fold results using monoidal operation
    """
    name: str = "map_reduce"
    mapper: Agent = None
    reducer: Callable[[List[Any]], Any] = None

    async def execute(self, state: AgentState) -> AgentState:
        if not isinstance(state.data, list):
            state = AgentState(data=[state.data], metadata=state.metadata)

        # Map phase (parallel)
        map_tasks = [self.mapper.execute(AgentState(data=item)) for item in state.data]
        mapped_states = await asyncio.gather(*map_tasks)

        # Reduce phase
        results = [s.data for s in mapped_states]
        reduced = self.reducer(results) if self.reducer else results

        return state.update(reduced)


@dataclass
class ScatterGatherPattern(OrchestrationPattern):
    """
    Scatter-Gather pattern for exploring multiple approaches.

    Scatter: Send to multiple agents (tensor product)
    Gather: Collect and synthesize results
    """
    name: str = "scatter_gather"
    scatter_agents: List[Agent] = field(default_factory=list)
    gather_func: Callable[[List[Any]], Any] = None

    async def execute(self, state: AgentState) -> AgentState:
        # Scatter (parallel execution)
        results = await parallel_execute(self.scatter_agents, state)

        # Gather (synthesis)
        gathered_data = [r.data for r in results]
        if self.gather_func:
            final = self.gather_func(gathered_data)
        else:
            # Default: concatenate
            final = gathered_data

        return state.update(final)


@dataclass
class RecursiveRefinementPattern(OrchestrationPattern):
    """
    Recursive refinement pattern using monad structure.

    Repeatedly apply improvement until convergence.
    Corresponds to monad >>= with quality-based termination.
    """
    name: str = "recursive_refinement"
    refiner: Agent = None
    quality_threshold: float = 0.9
    max_iterations: int = 10

    async def execute(self, state: AgentState) -> AgentState:
        current = state
        iteration = 0

        while current.quality < self.quality_threshold and iteration < self.max_iterations:
            current = await self.refiner.execute(current)
            iteration += 1
            current.metadata["refinement_iteration"] = iteration

        return current


@dataclass
class ContextualCoordinationPattern(OrchestrationPattern):
    """
    Contextual coordination using comonad structure.

    Agents share and extend context through comonadic operations.
    """
    name: str = "contextual_coordination"
    agents: List[Agent] = field(default_factory=list)

    async def execute(self, state: AgentState) -> AgentState:
        # Comonad duplicate: add meta-context layer
        enriched_state = AgentState(
            data=state.data,
            metadata={
                **state.metadata,
                "_coordination_context": {
                    "agent_count": len(self.agents),
                    "coordination_start": time.time()
                }
            },
            history=state.history,
            quality=state.quality
        )

        # Execute agents with shared context
        current = enriched_state
        for agent in self.agents:
            result = await agent.execute(current)
            # Extend context with agent's output
            current = AgentState(
                data=result.data,
                metadata={
                    **current.metadata,
                    f"_{agent.name}_output": result.data
                },
                history=current.history + [current.data],
                quality=result.quality
            )

        return current


# =============================================================================
# COMPLETE ORCHESTRATOR
# =============================================================================

class CategoricalOrchestrator:
    """
    Main orchestrator combining all patterns.

    Provides a high-level interface for multi-agent coordination
    using categorical composition principles.
    """

    def __init__(self, name: str = "orchestrator"):
        self.name = name
        self.agents: Dict[str, Agent] = {}
        self.chains: Dict[str, AgentChain] = {}
        self.patterns: Dict[str, OrchestrationPattern] = {}
        self.router = StrategyRouter()

    def register_agent(self, agent: Agent):
        """Register an agent"""
        self.agents[agent.name] = agent

    def register_chain(self, name: str, agent_names: List[str]):
        """Create and register an agent chain"""
        agents = [self.agents[n] for n in agent_names if n in self.agents]
        self.chains[name] = AgentChain(agents=agents, name=name)

    def register_pattern(self, pattern: OrchestrationPattern):
        """Register an orchestration pattern"""
        self.patterns[pattern.name] = pattern

    async def execute_chain(self, chain_name: str, initial_data: Any) -> AgentState:
        """Execute a named chain"""
        if chain_name not in self.chains:
            raise ValueError(f"Unknown chain: {chain_name}")

        state = AgentState(data=initial_data)
        return await self.chains[chain_name].execute(state)

    async def execute_pattern(self, pattern_name: str, initial_data: Any) -> AgentState:
        """Execute a named pattern"""
        if pattern_name not in self.patterns:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        state = AgentState(data=initial_data)
        return await self.patterns[pattern_name].execute(state)


# =============================================================================
# EXAMPLE: GAME OF 24 ORCHESTRATION
# =============================================================================

async def game_of_24_orchestration():
    """
    Example orchestration for solving Game of 24.

    Uses:
    - Observer: Extract card numbers and constraints
    - Reasoner: Analyze possible approaches
    - Creator: Generate solution attempts
    - Verifier: Check mathematical correctness
    """
    # Create orchestrator
    orch = CategoricalOrchestrator("game_24")

    # Register agents
    orch.register_agent(ObserverAgent(
        name="card_observer",
        focus_keys=["numbers", "target", "operators"]
    ))

    orch.register_agent(ReasonerAgent(
        name="strategy_analyzer"
    ))

    orch.register_agent(CreatorAgent(
        name="solution_generator",
        template="Find: {numbers} → {target}\nOperators: {operators}\nSolution:"
    ))

    def check_equals_24(content: str) -> Tuple[bool, str]:
        """Verify solution equals 24"""
        # Simplified check
        if "= 24" in content or "=24" in content:
            return True, "Solution yields 24"
        return False, "Solution does not yield 24"

    orch.register_agent(VerifierAgent(
        name="math_verifier",
        validators=[check_equals_24]
    ))

    # Create chain
    orch.register_chain("full_solve", [
        "card_observer",
        "strategy_analyzer",
        "solution_generator",
        "math_verifier"
    ])

    # Execute
    initial = {
        "numbers": [3, 3, 8, 8],
        "target": 24,
        "operators": ["+", "-", "*", "/"]
    }

    result = await orch.execute_chain("full_solve", initial)

    print(f"Orchestration Result:")
    print(f"  Data: {result.data}")
    print(f"  Quality: {result.quality}")
    print(f"  Metadata: {result.metadata}")

    return result


if __name__ == "__main__":
    asyncio.run(game_of_24_orchestration())
