# Stream C: Meta-Prompting Frameworks

**Status:** Phase 2 Complete
**Last Updated:** 2025-01-15

## Overview

Stream C provides the meta-prompting framework implementations that bridge categorical theory (Stream A) with practical TypeScript/Python implementations (Stream B). This stream focuses on:

1. **Categorical DSL**: A domain-specific language for expressing meta-prompting operations
2. **Orchestration Patterns**: Multi-agent coordination using categorical composition
3. **Adjunctions & Higher Categories**: Advanced categorical structures for meta-prompting

## Directory Structure

```
stream-c-meta-prompting/
├── categorical/
│   └── adjunctions.py      # Adjunctions, Kan extensions, 2-categories
├── dsl/
│   └── categorical_dsl.py  # DSL for meta-prompting pipelines
├── orchestration/
│   └── categorical_orchestration.py  # Multi-agent patterns
└── README.md               # This file
```

## Components

### 1. Categorical DSL (`dsl/categorical_dsl.py`)

A domain-specific language for building meta-prompting pipelines with categorical semantics.

**Features:**
- Declarative syntax close to mathematical notation
- Type-safe composition of operations
- Automatic categorical law verification
- Integration with LMQL/DSPy constraints

**Example:**
```python
from stream_c_meta_prompting.dsl.categorical_dsl import *

# Build a pipeline using pipe operator
pipeline = (
    task("Solve Game of 24: 3,3,8,8")
    | FMap(analyze_complexity)
    | Bind(generate_prompt)
    | RecursiveImprove(refine, quality_threshold=0.9)
    | Extract()
)

# Execute
result = pipeline.run()

# Verify categorical laws
laws = pipeline.verify_laws()
```

**Operations:**
- `FMap(f)`: Functor map - lift function to categorical context
- `Bind(f)`: Monad bind - chain computations
- `Unit()`: Monad unit - wrap value in monadic context
- `Join()`: Monad join - flatten nested monads
- `Extract()`: Comonad extract - focus on current value
- `Duplicate()`: Comonad duplicate - create meta-observation
- `Extend(f)`: Comonad extend - context-aware transformation
- `WithConstraints([...])`: Apply LMQL-style constraints

### 2. Adjunctions (`categorical/adjunctions.py`)

Advanced categorical structures for meta-prompting.

**Features:**
- F ⊣ U Adjunction (Tasks ⊣ Prompts)
- Kan Extensions for prompt generalization
- 2-Category structure for meta-meta-prompting
- Ends and Coends for universal constructions

**Example:**
```python
from stream_c_meta_prompting.categorical.adjunctions import *

# Create task-prompt adjunction
adj = create_task_prompt_adjunction(
    generate_prompt=functor.map_object,
    reconstruct_task=functor.reconstruct_task
)

# Verify triangle identities
left_tri, right_tri = adj.verify_triangle_identities(task, prompt)

# Create 2-category for strategy reasoning
meta_2cat = create_meta_prompting_2_category()
# 0-cells: ZeroShot, FewShot, ChainOfThought, TreeOfThoughts, MetaPrompting
# 1-cells: Translation functors between paradigms
# 2-cells: Natural transformations (refinements)
```

### 3. Orchestration (`orchestration/categorical_orchestration.py`)

Multi-agent coordination using categorical composition patterns.

**Patterns:**
- **Map-Reduce**: Parallel functor application with monoidal fold
- **Scatter-Gather**: Tensor product execution with synthesis
- **Recursive Refinement**: Monadic improvement until convergence
- **Contextual Coordination**: Comonadic context sharing

**Example:**
```python
from stream_c_meta_prompting.orchestration.categorical_orchestration import *

# Create orchestrator
orch = CategoricalOrchestrator("game_24")

# Register agents (each is a categorical morphism)
orch.register_agent(ObserverAgent(name="observer", focus_keys=["numbers"]))
orch.register_agent(ReasonerAgent(name="reasoner"))
orch.register_agent(CreatorAgent(name="creator", template=TEMPLATE))
orch.register_agent(VerifierAgent(name="verifier", validators=[check_24]))

# Create chain (functor composition)
orch.register_chain("solve", ["observer", "reasoner", "creator", "verifier"])

# Execute
result = await orch.execute_chain("solve", {"numbers": [3,3,8,8]})
```

**Agent Types:**
- `ObserverAgent`: Comonad extract - focus observations
- `ReasonerAgent`: Functor map - analyze and transform
- `CreatorAgent`: Monad operations - generate with quality
- `VerifierAgent`: Property checking - validate outputs

## Integration with Other Streams

### Stream A (Theory)
Stream C implements the categorical structures defined in Stream A's theoretical analysis:
- Functor F: Tasks → Prompts (from Zhang et al. analysis)
- Monad M: Recursive improvement
- Comonad W: Context extraction

### Stream B (Implementation)
Stream C provides the orchestration layer that Stream B's Effect-TS and DSPy implementations use:
- DSL pipelines compile to Effect-TS computations
- Orchestration patterns map to LangGraph workflows

### Stream D (Patterns)
Stream C uses patterns extracted from DisCoPy:
- Monoidal composition for parallel execution
- String diagram semantics for pipeline visualization

## Usage

### Installation

```bash
# From repository root
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/path/to/categorical-meta-prompting
```

### Quick Start

```python
# Import DSL
from stream_c_meta_prompting.dsl.categorical_dsl import task, FMap, Bind, Extract

# Create simple pipeline
pipeline = task("Your task here") | FMap(analyze) | Bind(improve)

# Run
result = pipeline.run()
```

### Running Examples

```bash
# DSL example
python stream-c-meta-prompting/dsl/categorical_dsl.py

# Orchestration example
python stream-c-meta-prompting/orchestration/categorical_orchestration.py

# Adjunctions demo
python stream-c-meta-prompting/categorical/adjunctions.py
```

## Categorical Laws Verified

All Stream C components verify categorical laws at construction time:

| Component | Law | Verification |
|-----------|-----|--------------|
| DSL Pipeline | Functor identity | `pipeline.verify_laws()["functor_present"]` |
| DSL Pipeline | Monad well-formed | `pipeline.verify_laws()["monad_well_formed"]` |
| Adjunction | Triangle identities | `adj.verify_triangle_identities(task, prompt)` |
| 2-Category | Interchange law | `meta_2cat.interchange_law(...)` |

## References

1. Zhang et al. (2023) - "Meta-Prompting: Enhancing Language Models with Task-Agnostic Scaffolding"
2. de Wynter et al. (2025) - "Categorical Meta-Prompting Theory"
3. Spivak & Niu (2021) - "Polynomial Functors and Lenses"
4. Gavranović et al. (2024) - "Categorical Deep Learning"
5. LangGraph Documentation - State machine orchestration
6. DSPy Documentation - Declarative prompt optimization

## Contributing

Stream C welcomes contributions in:
- New DSL operations
- Additional orchestration patterns
- Formal verification of laws
- Performance optimizations

See CONTRIBUTING.md for guidelines.
