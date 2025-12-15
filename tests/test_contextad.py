"""
Tests for Contextad (Pattern 8)

Tests verify:
1. Comonadic operations (extract, duplicate, extend)
2. Actegory operations (act, use_tool, retrieve)
3. Unified operations (augment)
4. Tool and knowledge integration
5. Categorical laws

Reference: arXiv:2410.21889 (Contextads as Wreaths)
"""

import pytest

from meta_prompting_engine.categorical.contextad import (
    Contextad,
    ContextadObservation,
    ExternalContext,
    Tool,
    KnowledgeBase,
    create_contextad,
    create_contextad_with_tools,
    create_mcp_tool,
    summarize_action,
    enhance_with_knowledge_action,
)
from meta_prompting_engine.categorical.graded_comonad import Tier


class TestTool:
    """Tests for Tool class."""

    def test_create_tool(self):
        """Should create tool with properties."""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            parameters={"input": "str"}
        )
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"

    def test_tool_execute(self):
        """Should execute tool function."""
        tool = Tool(
            name="adder",
            description="Adds numbers",
            execute=lambda kwargs: kwargs.get("a", 0) + kwargs.get("b", 0)
        )
        result = tool(a=2, b=3)
        assert result == 5

    def test_tool_default_execute(self):
        """Should have default execution."""
        tool = Tool(name="echo", description="Echo tool")
        result = tool(message="hello")
        assert "echo" in result.lower()
        assert "hello" in result


class TestKnowledgeBase:
    """Tests for KnowledgeBase class."""

    def test_create_knowledge_base(self):
        """Should create KB with documents."""
        kb = KnowledgeBase(
            name="test_kb",
            documents=["Python is a language", "JavaScript is also a language"]
        )
        assert kb.name == "test_kb"
        assert len(kb.documents) == 2

    def test_retrieve_by_keyword(self):
        """Should retrieve relevant documents."""
        kb = KnowledgeBase(
            name="languages",
            documents=[
                "Python is great for data science",
                "JavaScript powers the web",
                "Rust is memory safe",
            ]
        )
        results = kb.retrieve("Python data", k=2)
        assert len(results) <= 2
        # Python doc should be most relevant
        assert "Python" in results[0]

    def test_custom_retriever(self):
        """Should use custom retriever."""
        def always_return_hello(query):
            return ["hello", "world"]

        kb = KnowledgeBase(name="custom", retriever=always_return_hello)
        results = kb.retrieve("any query")
        assert results == ["hello", "world"]


class TestExternalContext:
    """Tests for ExternalContext class."""

    @pytest.fixture
    def context(self):
        ctx = ExternalContext()
        ctx.add_tool(Tool("tool1", "First tool"))
        ctx.add_tool(Tool("tool2", "Second tool"))
        ctx.add_knowledge(KnowledgeBase("kb1", documents=["doc1", "doc2"]))
        return ctx

    def test_add_tool(self, context):
        """Should add tools."""
        assert len(context.tools) == 2
        assert "tool1" in context.tools

    def test_get_tool(self, context):
        """Should retrieve tool by name."""
        tool = context.get_tool("tool1")
        assert tool is not None
        assert tool.name == "tool1"

    def test_get_missing_tool(self, context):
        """Should return None for missing tool."""
        tool = context.get_tool("nonexistent")
        assert tool is None

    def test_add_knowledge(self, context):
        """Should add knowledge bases."""
        assert len(context.knowledge) == 1
        assert "kb1" in context.knowledge

    def test_retrieve_from_specific_kb(self, context):
        """Should retrieve from specific KB."""
        results = context.retrieve_knowledge("doc", kb_name="kb1")
        assert len(results) > 0


class TestContextadObservation:
    """Tests for ContextadObservation."""

    def test_create_observation(self):
        """Should create observation with value and grade."""
        obs = ContextadObservation(
            value="test value",
            grade=Tier.L3
        )
        assert obs.value == "test value"
        assert obs.grade == Tier.L3

    def test_observation_properties(self):
        """Should compute properties correctly."""
        external = ExternalContext()
        external.add_tool(Tool("t1", "tool"))
        external.add_knowledge(KnowledgeBase("k1"))

        obs = ContextadObservation(
            value="test",
            grade=Tier.L4,
            history=[ContextadObservation("prev", Tier.L3)],
            external=external
        )

        assert obs.history_depth == 1
        assert obs.available_tools == ["t1"]
        assert obs.available_knowledge == ["k1"]

    def test_observation_str(self):
        """Should have informative string."""
        obs = ContextadObservation(value="hello", grade=Tier.L5)
        s = str(obs)
        assert "L5" in s
        assert "hello" in s


class TestContextadComonadicOperations:
    """Tests for comonadic operations."""

    @pytest.fixture
    def contextad(self):
        return create_contextad()

    @pytest.fixture
    def observation(self, contextad):
        return contextad.create("test value", Tier.L4)

    def test_extract(self, contextad, observation):
        """Extract should return focused value."""
        extracted = contextad.extract(observation)
        assert extracted == "test value"

    def test_extract_truncates_by_grade(self, contextad):
        """Extract should respect grade bounds."""
        long_value = "x" * 10000
        obs = contextad.create(long_value, Tier.L1)
        extracted = contextad.extract(obs)
        # L1 has 1200 tokens ≈ 4800 chars
        assert len(extracted) <= 4800

    def test_duplicate(self, contextad, observation):
        """Duplicate should create meta-observation."""
        dup = contextad.duplicate(observation)

        assert isinstance(dup.value, ContextadObservation)
        assert dup.value.value == "test value"
        assert dup.grade == observation.grade

    def test_duplicate_preserves_external(self, contextad):
        """Duplicate should preserve external context."""
        external = ExternalContext()
        external.add_tool(Tool("test_tool", "A tool"))

        obs = contextad.create("value", Tier.L3, external=external)
        dup = contextad.duplicate(obs)

        assert "test_tool" in dup.external.tools

    def test_extend(self, contextad, observation):
        """Extend should apply context-aware function."""
        def uppercase_with_grade(ctx):
            return f"{ctx.value.upper()} [Grade: {ctx.grade.name}]"

        extended = contextad.extend(uppercase_with_grade, observation)

        assert "TEST VALUE" in extended.value
        assert "L4" in extended.value

    def test_extend_preserves_context(self, contextad):
        """Extend should preserve full context."""
        external = ExternalContext()
        external.add_tool(Tool("tool", "desc"))

        obs = contextad.create("value", Tier.L5, external=external)
        extended = contextad.extend(lambda ctx: ctx.value * 2, obs)

        assert extended.external == obs.external
        assert extended.grade == obs.grade


class TestContextadActegoryOperations:
    """Tests for actegory operations."""

    @pytest.fixture
    def contextad(self):
        return create_contextad()

    @pytest.fixture
    def obs_with_tools(self, contextad):
        external = ExternalContext()
        external.add_tool(Tool(
            "formatter",
            "Formats text",
            execute=lambda kw: f"FORMATTED: {kw.get('text', '')}"
        ))
        return contextad.create("raw text", Tier.L3, external=external)

    def test_act(self, contextad, obs_with_tools):
        """Act should apply action."""
        def uppercase_action(external, value):
            return value.upper()

        acted = contextad.act(obs_with_tools, uppercase_action, "uppercase")

        assert acted.value == "RAW TEXT"
        assert "uppercase" in acted.actions_applied

    def test_act_preserves_structure(self, contextad, obs_with_tools):
        """Act should preserve observation structure."""
        def identity_action(external, value):
            return value

        acted = contextad.act(obs_with_tools, identity_action, "id")

        assert acted.grade == obs_with_tools.grade
        assert acted.external == obs_with_tools.external

    def test_use_tool(self, contextad, obs_with_tools):
        """Should use specific tool."""
        result = contextad.use_tool(obs_with_tools, "formatter", text="hello")

        assert "FORMATTED" in result.value
        assert "tool:formatter" in result.actions_applied

    def test_use_missing_tool(self, contextad, obs_with_tools):
        """Should handle missing tool gracefully."""
        result = contextad.use_tool(obs_with_tools, "nonexistent")
        # Should return original value
        assert result.value == obs_with_tools.value


class TestContextadKnowledgeRetrieval:
    """Tests for knowledge retrieval (RAG pattern)."""

    @pytest.fixture
    def contextad(self):
        return create_contextad()

    @pytest.fixture
    def obs_with_knowledge(self, contextad):
        external = ExternalContext()
        kb = KnowledgeBase(
            "facts",
            documents=[
                "Python is a programming language",
                "Category theory is branch of mathematics",
                "Comonads extract context",
            ]
        )
        external.add_knowledge(kb)
        return contextad.create("Tell me about Python", Tier.L4, external=external)

    def test_retrieve_and_augment(self, contextad, obs_with_knowledge):
        """Should augment with retrieved knowledge."""
        augmented = contextad.retrieve_and_augment(obs_with_knowledge)

        assert "Retrieved knowledge" in augmented.value
        assert "Python" in augmented.value

    def test_retrieve_with_query(self, contextad, obs_with_knowledge):
        """Should use custom query."""
        augmented = contextad.retrieve_and_augment(
            obs_with_knowledge,
            query="mathematics category"
        )

        assert "mathematics" in augmented.value.lower()


class TestContextadUnifiedOperations:
    """Tests for unified comonad + actegory operations."""

    @pytest.fixture
    def contextad(self):
        return create_contextad()

    @pytest.fixture
    def full_context_obs(self, contextad):
        external = ExternalContext()
        external.add_tool(Tool("enhance", "Enhances text",
                               execute=lambda kw: f"ENHANCED: {kw.get('text', '')}"))
        external.add_knowledge(KnowledgeBase("kb", documents=["fact 1", "fact 2"]))
        return contextad.create("initial value", Tier.L4, external=external)

    def test_augment(self, contextad, full_context_obs):
        """Augment should combine comonadic and actegory."""
        def comonadic_fn(ctx):
            return f"Processed: {ctx.value}"

        def actegory_action(external, value):
            return f"{value} [with external]"

        result = contextad.augment(full_context_obs, comonadic_fn, actegory_action)

        assert "Processed" in result.value
        assert "with external" in result.value

    def test_upgrade_with_tools(self, contextad):
        """Should upgrade grade and add tools."""
        obs = contextad.create("value", Tier.L2)
        new_tool = Tool("new_tool", "New functionality")

        upgraded = contextad.upgrade_with_tools(obs, Tier.L5, [new_tool])

        assert upgraded.grade == Tier.L5
        assert "new_tool" in upgraded.external.tools


class TestContextadLaws:
    """Tests for categorical laws."""

    @pytest.fixture
    def contextad(self):
        return create_contextad()

    @pytest.fixture
    def observation(self, contextad):
        external = ExternalContext()
        external.add_tool(Tool("t", "desc"))
        return contextad.create("test", Tier.L4, external=external)

    def test_comonad_laws(self, contextad, observation):
        """Should satisfy comonad laws."""
        laws = contextad.verify_comonad_laws(observation)

        assert laws['left_identity']
        assert laws['right_identity']
        assert laws['associativity']

    def test_actegory_laws(self, contextad, observation):
        """Should satisfy actegory laws."""
        action1 = lambda ext, val: val + "_a1"
        action2 = lambda ext, val: val + "_a2"

        laws = contextad.verify_actegory_laws(observation, action1, action2)

        assert laws['identity_action']
        assert laws['action_composition']


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_contextad(self):
        """Should create basic contextad."""
        ctx = create_contextad()
        assert isinstance(ctx, Contextad)

    def test_create_contextad_with_tools(self):
        """Should create contextad with pre-configured tools."""
        tools = [
            Tool("t1", "Tool 1"),
            Tool("t2", "Tool 2"),
        ]
        contextad, external = create_contextad_with_tools(tools)

        assert len(external.tools) == 2
        assert "t1" in external.tools

    def test_create_mcp_tool(self):
        """Should create MCP-style tool."""
        tool = create_mcp_tool(
            "echo",
            "Echoes input",
            lambda kw: kw.get("message", "")
        )

        assert tool.name == "echo"
        assert tool(message="hello") == "hello"


class TestPrebuiltActions:
    """Tests for pre-built actions."""

    def test_enhance_with_knowledge_action(self):
        """Should enhance with knowledge."""
        external = ExternalContext()
        external.add_knowledge(KnowledgeBase(
            "kb",
            documents=["relevant fact"]
        ))

        result = enhance_with_knowledge_action(external, "query text")
        assert "Relevant context" in result
        assert "relevant fact" in result


class TestIntegrationScenarios:
    """Integration tests with realistic scenarios."""

    def test_rag_pipeline(self):
        """Test RAG-style pipeline."""
        contextad = create_contextad()

        # Set up knowledge
        external = ExternalContext()
        external.add_knowledge(KnowledgeBase(
            "docs",
            documents=[
                "Comonads provide context extraction via extract operation",
                "Actegories allow external actions on data",
                "Contextads unify comonads and actegories",
            ]
        ))

        # Create observation
        obs = contextad.create(
            "Explain how contextads work",
            Tier.L4,
            external=external
        )

        # Retrieve and augment
        augmented = contextad.retrieve_and_augment(obs)

        # Extend with processing
        processed = contextad.extend(
            lambda ctx: f"Answer: {ctx.value}",
            augmented
        )

        assert "Contextads" in processed.value or "contextads" in processed.value.lower()

    def test_multi_tool_workflow(self):
        """Test workflow with multiple tools."""
        contextad = create_contextad()

        external = ExternalContext()
        external.add_tool(Tool(
            "analyze",
            "Analyzes text",
            execute=lambda kw: f"Analysis of: {kw.get('text', '')[:20]}..."
        ))
        external.add_tool(Tool(
            "summarize",
            "Summarizes text",
            execute=lambda kw: f"Summary: {len(kw.get('text', ''))} chars"
        ))

        obs = contextad.create("Long text to process", Tier.L5, external=external)

        # Apply multiple tools
        analyzed = contextad.use_tool(obs, "analyze", text=obs.value)
        summarized = contextad.use_tool(analyzed, "summarize", text=analyzed.value)

        assert len(summarized.actions_applied) == 2
        assert "tool:analyze" in summarized.actions_applied
        assert "tool:summarize" in summarized.actions_applied


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
