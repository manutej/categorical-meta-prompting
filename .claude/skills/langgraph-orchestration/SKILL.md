---
name: langgraph-orchestration
description: LangGraph stateful multi-agent graphs with categorical coordination patterns and cyclic workflows. Use when building stateful AI agent systems, implementing multi-agent orchestration with conditional routing, creating cyclic workflows with persistence, or designing graph-based AI pipelines with checkpointing and human-in-the-loop patterns.
---

# LangGraph Stateful Multi-Agent Orchestration

LangGraph provides categorical graph-based orchestration for stateful multi-agent AI systems.

## Installation

```bash
pip install langgraph langchain-openai
```

## Core Categorical Concepts

LangGraph maps to category theory:

- **StateGraph**: Category with states as objects
- **Nodes**: Morphisms `State → State`
- **Edges**: Composition of morphisms
- **Conditional Edges**: Coproduct (sum type) routing
- **Cycles**: Fixed-point iteration

## Basic Graph Structure

### Defining State (Object)

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    context: str
    iteration: int
```

### Creating Nodes (Morphisms)

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

def chatbot(state: AgentState) -> AgentState:
    """Node morphism: State → State."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def researcher(state: AgentState) -> AgentState:
    """Research node morphism."""
    query = state["messages"][-1].content
    # Perform research...
    return {"context": f"Research results for: {query}"}
```

### Building the Graph

```python
graph = StateGraph(AgentState)

# Add nodes (morphisms)
graph.add_node("chatbot", chatbot)
graph.add_node("researcher", researcher)

# Add edges (composition)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", "researcher")
graph.add_edge("researcher", END)

# Compile
app = graph.compile()
```

## Conditional Routing (Coproduct)

### Router Function

```python
from typing import Literal

def route_query(state: AgentState) -> Literal["research", "respond", "clarify"]:
    """Coproduct selector: determines which branch to take."""
    last_message = state["messages"][-1].content.lower()
    
    if "search" in last_message or "find" in last_message:
        return "research"
    elif "?" in last_message:
        return "clarify"
    else:
        return "respond"

# Add conditional edge
graph.add_conditional_edges(
    "chatbot",
    route_query,
    {
        "research": "researcher",
        "respond": "responder",
        "clarify": "clarifier"
    }
)
```

### Type-Safe Routing

```python
from pydantic import BaseModel

class RouteDecision(BaseModel):
    route: Literal["agent_a", "agent_b", "agent_c"]
    confidence: float

def smart_router(state: AgentState) -> str:
    """LLM-based routing decision."""
    decision = llm.with_structured_output(RouteDecision).invoke(
        f"Route this query: {state['messages'][-1].content}"
    )
    return decision.route
```

## Cyclic Workflows (Fixed Points)

### Iterative Refinement

```python
def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """Fixed-point termination condition."""
    if state["iteration"] >= 3:
        return "end"
    if "DONE" in state["messages"][-1].content:
        return "end"
    return "continue"

def increment_iteration(state: AgentState) -> AgentState:
    return {"iteration": state["iteration"] + 1}

# Create cycle
graph.add_node("refine", refine_response)
graph.add_node("evaluate", evaluate_quality)
graph.add_node("increment", increment_iteration)

graph.add_edge("refine", "evaluate")
graph.add_conditional_edges(
    "evaluate",
    should_continue,
    {
        "continue": "increment",
        "end": END
    }
)
graph.add_edge("increment", "refine")  # Back edge creates cycle
```

## Multi-Agent Patterns

### Supervisor Pattern (Orchestrator)

```python
class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str
    task_complete: bool

def supervisor(state: SupervisorState) -> SupervisorState:
    """Supervisor decides which agent to invoke."""
    response = llm.with_structured_output(SupervisorDecision).invoke([
        SystemMessage("You are a supervisor. Route to: researcher, writer, or reviewer."),
        *state["messages"]
    ])
    return {"next_agent": response.next_agent}

def route_to_agent(state: SupervisorState) -> str:
    return state["next_agent"]

# Build supervisor graph
supervisor_graph = StateGraph(SupervisorState)
supervisor_graph.add_node("supervisor", supervisor)
supervisor_graph.add_node("researcher", researcher_agent)
supervisor_graph.add_node("writer", writer_agent)
supervisor_graph.add_node("reviewer", reviewer_agent)

supervisor_graph.add_edge(START, "supervisor")
supervisor_graph.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {
        "researcher": "researcher",
        "writer": "writer",
        "reviewer": "reviewer",
        "FINISH": END
    }
)

# All agents return to supervisor
for agent in ["researcher", "writer", "reviewer"]:
    supervisor_graph.add_edge(agent, "supervisor")
```

### Parallel Execution (Product)

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class ParallelState(TypedDict):
    query: str
    result_a: str
    result_b: str
    combined: str

def branch_a(state: ParallelState) -> ParallelState:
    return {"result_a": f"Analysis A: {state['query']}"}

def branch_b(state: ParallelState) -> ParallelState:
    return {"result_b": f"Analysis B: {state['query']}"}

def combine_results(state: ParallelState) -> ParallelState:
    return {"combined": f"{state['result_a']} + {state['result_b']}"}

# Parallel branches
graph = StateGraph(ParallelState)
graph.add_node("branch_a", branch_a)
graph.add_node("branch_b", branch_b)
graph.add_node("combine", combine_results)

# Fan-out
graph.add_edge(START, "branch_a")
graph.add_edge(START, "branch_b")

# Fan-in
graph.add_edge("branch_a", "combine")
graph.add_edge("branch_b", "combine")
graph.add_edge("combine", END)
```

## Persistence and Checkpointing

### Memory Checkpointer

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# Run with thread ID for persistence
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke({"messages": [HumanMessage("Hello")]}, config)

# Continue conversation (loads from checkpoint)
result2 = app.invoke({"messages": [HumanMessage("Tell me more")]}, config)
```

### SQLite Persistence

```python
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    app = graph.compile(checkpointer=checkpointer)
    # Checkpoints persist across restarts
```

## Human-in-the-Loop

### Interrupt Before Node

```python
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["sensitive_action"]
)

# Run until interrupt
result = app.invoke(initial_state, config)

# Human reviews state...
# Resume execution
result = app.invoke(None, config)  # Continues from checkpoint
```

### Interrupt After Node

```python
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_after=["draft_response"]
)

# Run until after draft
result = app.invoke(initial_state, config)

# Human can modify state
app.update_state(
    config,
    {"messages": [HumanMessage("Please revise to be more formal")]}
)

# Continue with modified state
result = app.invoke(None, config)
```

## Tool Integration

```python
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

@tool
def calculate(expression: str) -> float:
    """Evaluate mathematical expression."""
    return eval(expression)

tools = [search_web, calculate]
llm_with_tools = llm.bind_tools(tools)

def agent_with_tools(state: AgentState) -> AgentState:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def tool_executor(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls
    
    results = []
    for call in tool_calls:
        tool = {"search_web": search_web, "calculate": calculate}[call["name"]]
        result = tool.invoke(call["args"])
        results.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    
    return {"messages": results}
```

## Categorical Composition

### Subgraph Embedding

```python
# Create subgraph
subgraph = StateGraph(AgentState)
subgraph.add_node("step1", step1_fn)
subgraph.add_node("step2", step2_fn)
subgraph.add_edge(START, "step1")
subgraph.add_edge("step1", "step2")
subgraph.add_edge("step2", END)

compiled_subgraph = subgraph.compile()

# Embed in parent graph
parent_graph = StateGraph(AgentState)
parent_graph.add_node("preprocess", preprocess_fn)
parent_graph.add_node("subworkflow", compiled_subgraph)
parent_graph.add_node("postprocess", postprocess_fn)

parent_graph.add_edge(START, "preprocess")
parent_graph.add_edge("preprocess", "subworkflow")
parent_graph.add_edge("subworkflow", "postprocess")
parent_graph.add_edge("postprocess", END)
```

## Streaming

```python
# Stream node outputs
for event in app.stream(initial_state, config):
    for node, output in event.items():
        print(f"Node {node}: {output}")

# Stream with mode
async for event in app.astream(initial_state, config, stream_mode="values"):
    print(event)
```

## Categorical Guarantees

LangGraph provides these categorical properties:

1. **State Preservation**: Nodes are pure morphisms on state
2. **Composition**: Edge composition is associative
3. **Determinism**: Same state + same nodes = same result
4. **Checkpoint Recovery**: State can be restored from any point
5. **Type Safety**: TypedDict ensures state schema consistency
