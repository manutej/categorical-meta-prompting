"""
Contextad: Unified Comonad + Actegory for Context Management

A contextad unifies two complementary structures:
1. Comonad (W): For history-based context (extract, duplicate, extend)
2. Actegory (⊛): For external tool/knowledge actions

Mathematical Definition:
    Contextad = Comonad W ⋊ Actegory A (wreath/semidirect product)

    Where:
    - W provides historical context via comonadic operations
    - A provides external context via action morphisms
    - The wreath product unifies them coherently

Wreath Product Structure:
    For comonad (W, ε, δ) and actegory (A, ⊛):
    - Objects: W(A) with action structure
    - Morphisms: Comonad morphisms + actegory actions
    - Laws: Coherence between W operations and A actions

Applications in Meta-Prompting:
    1. Unified context: History + tools + knowledge in one structure
    2. MCP integration: Tools become actegory actions
    3. RAG context: Knowledge retrieval as actegory
    4. Conversation flow: History as comonad, tools as actegory

References:
    - arXiv:2410.21889 - Contextads as Wreaths
    - arXiv:1912.13477 - Monad-Comonad Interaction Laws
    - arXiv:2501.14550 - Bean: Graded Coeffect Comonads

Example:
    >>> contextad = Contextad(history=conversation, tools=mcp_tools)
    >>> result = contextad.extract()  # Get focused context
    >>> augmented = contextad.act(tool_action)  # Apply tool
    >>> refined = contextad.extend(analyze_with_full_context)
"""

from typing import TypeVar, Callable, Generic, Any, Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

from .graded_comonad import Tier, GradedObservation, GradedComonad, create_graded_comonad

# Type variables
A = TypeVar('A')  # Value type
E = TypeVar('E')  # External context type (tools, knowledge)
B = TypeVar('B')  # Result type


class Action(Protocol[E, A]):
    """Protocol for actegory actions."""

    def __call__(self, external: E, value: A) -> A:
        """Apply action from external context to value."""
        ...


@dataclass
class Tool:
    """
    Representation of an external tool (MCP-style).

    Attributes:
        name: Tool identifier
        description: What the tool does
        parameters: Expected parameters
        execute: Function to execute the tool
    """
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    execute: Callable[[Dict[str, Any]], Any] = None

    def __call__(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        if self.execute:
            return self.execute(kwargs)
        return f"[Tool:{self.name}] executed with {kwargs}"


@dataclass
class KnowledgeBase:
    """
    Representation of external knowledge (RAG-style).

    Attributes:
        name: Knowledge base identifier
        retriever: Function to retrieve relevant knowledge
        documents: Stored documents/facts
    """
    name: str
    retriever: Callable[[str], List[str]] = None
    documents: List[str] = field(default_factory=list)

    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """Retrieve relevant knowledge."""
        if self.retriever:
            return self.retriever(query)[:k]

        # Default: keyword matching
        query_words = set(query.lower().split())
        scored = []
        for doc in self.documents:
            doc_words = set(doc.lower().split())
            score = len(query_words & doc_words)
            scored.append((score, doc))

        return [doc for _, doc in sorted(scored, reverse=True)[:k]]


@dataclass
class ExternalContext:
    """
    External context containing tools and knowledge.

    This is the actegory part of the contextad.

    Attributes:
        tools: Available tools (MCP-style)
        knowledge: Knowledge bases (RAG-style)
        metadata: Additional external context
    """
    tools: Dict[str, Tool] = field(default_factory=dict)
    knowledge: Dict[str, KnowledgeBase] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_tool(self, tool: Tool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool

    def add_knowledge(self, kb: KnowledgeBase) -> None:
        """Register a knowledge base."""
        self.knowledge[kb.name] = kb

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name."""
        return self.tools.get(name)

    def retrieve_knowledge(self, query: str, kb_name: Optional[str] = None) -> List[str]:
        """Retrieve from knowledge bases."""
        if kb_name:
            kb = self.knowledge.get(kb_name)
            return kb.retrieve(query) if kb else []

        # Search all knowledge bases
        results = []
        for kb in self.knowledge.values():
            results.extend(kb.retrieve(query, k=2))
        return results


@dataclass
class ContextadObservation(Generic[A]):
    """
    Observation in a contextad - unifying comonadic and actegory context.

    This is the wreath product W ⋊ A applied to a value.

    Attributes:
        value: Current focused value
        grade: Resource tier (from graded comonad)
        history: Historical context (comonadic)
        external: External context (actegory)
        actions_applied: Log of actions applied
        metadata: Additional metadata
    """
    value: A
    grade: Tier
    history: List['ContextadObservation'] = field(default_factory=list)
    external: ExternalContext = field(default_factory=ExternalContext)
    actions_applied: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def history_depth(self) -> int:
        """Depth of historical context."""
        return len(self.history)

    @property
    def available_tools(self) -> List[str]:
        """List of available tool names."""
        return list(self.external.tools.keys())

    @property
    def available_knowledge(self) -> List[str]:
        """List of available knowledge base names."""
        return list(self.external.knowledge.keys())

    def __str__(self) -> str:
        return (
            f"Contextad[{self.grade.name}]("
            f"value={str(self.value)[:30]}..., "
            f"history={self.history_depth}, "
            f"tools={len(self.available_tools)}, "
            f"knowledge={len(self.available_knowledge)})"
        )


@dataclass
class Contextad:
    """
    Contextad: Unified Comonad + Actegory.

    Combines:
    - GradedComonad W_g for historical context with resource bounds
    - Actegory A for external tools and knowledge

    The wreath product W ⋊ A ensures coherent interaction.

    Operations:
    - extract: Get focused value (comonadic)
    - duplicate: Create meta-observation (comonadic)
    - extend: Context-aware transformation (comonadic)
    - act: Apply external action (actegory)
    - augment: Combine comonadic and actegory operations

    Attributes:
        graded_comonad: Underlying graded comonad
    """

    graded_comonad: GradedComonad = field(default_factory=create_graded_comonad)

    def create(
        self,
        value: A,
        grade: Tier,
        external: Optional[ExternalContext] = None,
        history: Optional[List[ContextadObservation]] = None
    ) -> ContextadObservation[A]:
        """
        Create a contextad observation.

        Args:
            value: Initial value
            grade: Resource tier
            external: External context (tools, knowledge)
            history: Optional historical context

        Returns:
            ContextadObservation wrapping the value
        """
        return ContextadObservation(
            value=value,
            grade=grade,
            history=history or [],
            external=external or ExternalContext(),
        )

    # === Comonadic Operations ===

    def extract(self, ctx: ContextadObservation[A]) -> A:
        """
        ε : W_g ⋊ A → 1

        Extract focused value (comonadic operation).
        Respects grade bounds on extraction.

        Args:
            ctx: Contextad observation

        Returns:
            Focused value (possibly truncated by grade)
        """
        # Delegate to graded comonad for grade-bounded extraction
        graded_obs = GradedObservation(
            current=ctx.value,
            grade=ctx.grade,
        )
        return self.graded_comonad.extract(graded_obs)

    def duplicate(
        self,
        ctx: ContextadObservation[A]
    ) -> ContextadObservation[ContextadObservation[A]]:
        """
        δ : W_g ⋊ A → (W_g ⋊ A)(W_g ⋊ A)

        Create meta-observation (comonadic operation).
        The external context is preserved in both layers.

        Args:
            ctx: Contextad observation

        Returns:
            Meta-observation (contextad of contextad)
        """
        return ContextadObservation(
            value=ctx,
            grade=ctx.grade,
            history=[ctx] + ctx.history[:5],
            external=ctx.external,  # Preserve external context
            actions_applied=ctx.actions_applied,
            metadata={
                'meta_level': ctx.metadata.get('meta_level', 0) + 1,
                'original_grade': ctx.grade.name,
            }
        )

    def extend(
        self,
        f: Callable[[ContextadObservation[A]], B],
        ctx: ContextadObservation[A]
    ) -> ContextadObservation[B]:
        """
        extend : (W_g ⋊ A → B) → W_g ⋊ A → W_g ⋊ A(B)

        Context-aware transformation (comonadic operation).
        Function has access to full contextad including external context.

        Args:
            f: Function with access to full context
            ctx: Contextad observation

        Returns:
            Transformed observation preserving context
        """
        result = f(ctx)

        return ContextadObservation(
            value=result,
            grade=ctx.grade,
            history=ctx.history,
            external=ctx.external,
            actions_applied=ctx.actions_applied,
            metadata={
                **ctx.metadata,
                'extended': True,
                'transformation': getattr(f, '__name__', 'lambda'),
            }
        )

    # === Actegory Operations ===

    def act(
        self,
        ctx: ContextadObservation[A],
        action: Callable[[ExternalContext, A], A],
        action_name: str = "unnamed_action"
    ) -> ContextadObservation[A]:
        """
        ⊛ : A × (W_g ⋊ A) → W_g ⋊ A

        Apply external action (actegory operation).
        The action has access to external context and current value.

        Args:
            ctx: Contextad observation
            action: Function (external, value) → value
            action_name: Name for logging

        Returns:
            Observation with action applied
        """
        new_value = action(ctx.external, ctx.value)

        return ContextadObservation(
            value=new_value,
            grade=ctx.grade,
            history=ctx.history,  # Preserve history
            external=ctx.external,  # Preserve external context
            actions_applied=ctx.actions_applied + [action_name],
            metadata={
                **ctx.metadata,
                'last_action': action_name,
            }
        )

    def use_tool(
        self,
        ctx: ContextadObservation[str],
        tool_name: str,
        **kwargs
    ) -> ContextadObservation[str]:
        """
        Apply a specific tool to augment the value.

        Convenience method for common actegory action.

        Args:
            ctx: Contextad observation (string value)
            tool_name: Name of tool to use
            **kwargs: Tool parameters

        Returns:
            Observation augmented with tool result
        """
        def tool_action(external: ExternalContext, value: str) -> str:
            tool = external.get_tool(tool_name)
            if tool:
                result = tool(**kwargs)
                return f"{value}\n\n[{tool_name}]: {result}"
            return value

        return self.act(ctx, tool_action, f"tool:{tool_name}")

    def retrieve_and_augment(
        self,
        ctx: ContextadObservation[str],
        query: Optional[str] = None,
        kb_name: Optional[str] = None
    ) -> ContextadObservation[str]:
        """
        Retrieve knowledge and augment value (RAG pattern).

        Convenience method for knowledge retrieval action.

        Args:
            ctx: Contextad observation
            query: Search query (uses value if not provided)
            kb_name: Specific knowledge base (all if not provided)

        Returns:
            Observation augmented with retrieved knowledge
        """
        def retrieve_action(external: ExternalContext, value: str) -> str:
            search_query = query or value
            retrieved = external.retrieve_knowledge(search_query, kb_name)

            if retrieved:
                knowledge_text = "\n".join(f"- {doc}" for doc in retrieved)
                return f"{value}\n\nRetrieved knowledge:\n{knowledge_text}"
            return value

        return self.act(ctx, retrieve_action, f"retrieve:{kb_name or 'all'}")

    # === Unified Operations ===

    def augment(
        self,
        ctx: ContextadObservation[A],
        comonadic_fn: Callable[[ContextadObservation[A]], B],
        actegory_action: Callable[[ExternalContext, B], B]
    ) -> ContextadObservation[B]:
        """
        Unified operation combining comonadic extend and actegory action.

        First applies comonadic transformation, then actegory action.
        This is the key operation of the contextad wreath product.

        Args:
            ctx: Contextad observation
            comonadic_fn: Context-aware transformation
            actegory_action: External action

        Returns:
            Observation with both transformations applied
        """
        # First: comonadic extend
        extended = self.extend(comonadic_fn, ctx)

        # Then: actegory action
        acted = self.act(extended, actegory_action, "unified_augment")

        return acted

    def upgrade_with_tools(
        self,
        ctx: ContextadObservation[A],
        new_grade: Tier,
        additional_tools: List[Tool]
    ) -> ContextadObservation[A]:
        """
        Upgrade both grade and tool set.

        Unified operation for expanding context capacity.

        Args:
            ctx: Current observation
            new_grade: Target grade
            additional_tools: Tools to add

        Returns:
            Upgraded observation
        """
        # Upgrade grade
        upgraded = ContextadObservation(
            value=ctx.value,
            grade=new_grade,
            history=ctx.history,
            external=ExternalContext(
                tools={**ctx.external.tools},
                knowledge={**ctx.external.knowledge},
                metadata={**ctx.external.metadata},
            ),
            actions_applied=ctx.actions_applied,
            metadata={
                **ctx.metadata,
                'upgraded_from': ctx.grade.name,
            }
        )

        # Add new tools
        for tool in additional_tools:
            upgraded.external.add_tool(tool)

        return upgraded

    # === Law Verification ===

    def verify_comonad_laws(self, ctx: ContextadObservation[A]) -> Dict[str, bool]:
        """
        Verify comonad laws for contextad.

        Laws:
        1. Left identity: extract ∘ duplicate = id
        2. Right identity: (fmap extract) ∘ duplicate = id
        3. Associativity: duplicate ∘ duplicate = (fmap duplicate) ∘ duplicate
        """
        # Left identity
        duplicated = self.duplicate(ctx)
        extracted = self.extract(duplicated)
        left_identity = str(extracted.value) == str(ctx.value)

        # Right identity (structural check)
        duplicated = self.duplicate(ctx)
        right_identity = duplicated.value.value == ctx.value

        # Associativity (structural check)
        dup_dup = self.duplicate(self.duplicate(ctx))
        associativity = isinstance(dup_dup.value.value, ContextadObservation)

        return {
            'left_identity': left_identity,
            'right_identity': right_identity,
            'associativity': associativity,
        }

    def verify_actegory_laws(
        self,
        ctx: ContextadObservation[A],
        action1: Callable[[ExternalContext, A], A],
        action2: Callable[[ExternalContext, A], A]
    ) -> Dict[str, bool]:
        """
        Verify actegory laws for contextad.

        Laws:
        1. Identity action: act(id_action) = id
        2. Action composition: act(a1) ∘ act(a2) = act(a1 ∘ a2)
        """
        # Identity action
        identity_action = lambda ext, val: val
        acted_id = self.act(ctx, identity_action, "identity")
        identity_law = acted_id.value == ctx.value

        # Composition (structural check)
        acted_1_then_2 = self.act(self.act(ctx, action1, "a1"), action2, "a2")
        composed_action = lambda ext, val: action2(ext, action1(ext, val))
        acted_composed = self.act(ctx, composed_action, "composed")
        composition_law = acted_1_then_2.value == acted_composed.value

        return {
            'identity_action': identity_law,
            'action_composition': composition_law,
        }


# === Factory Functions ===

def create_contextad() -> Contextad:
    """
    Factory for creating a Contextad instance.

    Returns:
        Contextad ready for use
    """
    return Contextad()


def create_contextad_with_tools(tools: List[Tool]) -> Tuple[Contextad, ExternalContext]:
    """
    Create contextad with pre-configured tools.

    Args:
        tools: Tools to include

    Returns:
        (Contextad, ExternalContext) tuple
    """
    contextad = Contextad()
    external = ExternalContext()

    for tool in tools:
        external.add_tool(tool)

    return contextad, external


def create_mcp_tool(
    name: str,
    description: str,
    handler: Callable[[Dict[str, Any]], Any]
) -> Tool:
    """
    Create an MCP-style tool.

    Args:
        name: Tool name
        description: Tool description
        handler: Function to handle tool calls

    Returns:
        Tool instance
    """
    return Tool(name=name, description=description, execute=handler)


# === Pre-built Actions ===

def summarize_action(external: ExternalContext, value: str) -> str:
    """Action that summarizes value using available tools."""
    summarizer = external.get_tool("summarize")
    if summarizer:
        summary = summarizer(text=value)
        return f"Summary: {summary}\n\nOriginal: {value}"
    return value


def enhance_with_knowledge_action(external: ExternalContext, value: str) -> str:
    """Action that enhances value with relevant knowledge."""
    knowledge = external.retrieve_knowledge(value)
    if knowledge:
        return f"{value}\n\nRelevant context:\n" + "\n".join(f"• {k}" for k in knowledge)
    return value
