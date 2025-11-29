---
name: polynomial-functors
description: Spivak-Niu polynomial functor implementations for learner composition and dynamical systems. Use when modeling learning systems as categorical structures, composing machine learning components with polynomial functors, implementing the categorical framework from Polynomial Functors - A Mathematical Theory of Interaction, or building compositional dynamical systems with lenses and charts.
---

# Polynomial Functors for Learner Composition

Implementation of Spivak-Niu polynomial functor framework for compositional learning systems.

## Core Concepts

Polynomial functors model systems with:
- **Position**: Internal state space
- **Direction**: Interface/interaction type
- **Lens**: Bidirectional data flow (get/put)
- **Chart**: Dynamical update rules

## Basic Polynomial Structure

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable, Tuple

S = TypeVar('S')  # State
A = TypeVar('A')  # Input
B = TypeVar('B')  # Output

@dataclass
class Polynomial(Generic[S, A, B]):
    """
    Polynomial functor p(y) = Σ_{s∈S} y^{A(s)}
    
    Represents a system with:
    - Positions S (internal states)
    - Directions A(s) → B (interface at each state)
    """
    positions: set  # S
    directions: Callable[[S], Tuple[type, type]]  # s ↦ (A(s), B(s))
```

## Lenses as Morphisms

```python
@dataclass
class Lens(Generic[S, A, B]):
    """
    Lens: bidirectional transformation.
    
    get: S → A (forward/observation)
    put: S × B → S (backward/update)
    """
    get: Callable[[S], A]
    put: Callable[[S, B], S]
    
    def compose(self, other: 'Lens[A, C, D]') -> 'Lens[S, C, D]':
        """Lens composition (Kleisli-like)."""
        return Lens(
            get=lambda s: other.get(self.get(s)),
            put=lambda s, d: self.put(s, other.put(self.get(s), d))
        )

# Example: Neural network layer as lens
@dataclass
class LayerLens:
    weights: 'np.ndarray'
    
    def forward(self, x: 'np.ndarray') -> 'np.ndarray':
        return self.weights @ x
    
    def backward(self, x: 'np.ndarray', grad: 'np.ndarray') -> Tuple['np.ndarray', 'np.ndarray']:
        weight_grad = np.outer(grad, x)
        input_grad = self.weights.T @ grad
        return weight_grad, input_grad
```

## Learners as Polynomial Coalgebras

```python
@dataclass
class Learner(Generic[S, A, B]):
    """
    Learner in the sense of Spivak-Niu.
    
    A learner is a lens equipped with:
    - Parameter space P
    - Implementation: P × A → B
    - Update: P × A × B → P
    """
    param_space: type
    implement: Callable  # (P, A) → B
    update: Callable     # (P, A, B) → P
    request: Callable    # (P, A) → A (optional, for backprop)

def compose_learners(l1: Learner, l2: Learner) -> Learner:
    """
    Compose learners sequentially.
    
    l1: A → B with params P1
    l2: B → C with params P2
    Result: A → C with params (P1, P2)
    """
    return Learner(
        param_space=(l1.param_space, l2.param_space),
        implement=lambda p, a: l2.implement(p[1], l1.implement(p[0], a)),
        update=lambda p, a, c: (
            l1.update(p[0], a, l2.request(p[1], l1.implement(p[0], a))),
            l2.update(p[1], l1.implement(p[0], a), c)
        ),
        request=lambda p, a: l1.request(p[0], a)
    )
```

## Charts for Dynamical Systems

```python
@dataclass
class Chart(Generic[S, A, B]):
    """
    Chart: dynamical system on polynomial.
    
    A chart assigns to each position a way to:
    - Observe output from state
    - Update state given input
    """
    readout: Callable[[S], B]      # Observe
    update: Callable[[S, A], S]    # Transition
    
    def run(self, initial: S, inputs: list) -> list:
        """Execute dynamical system."""
        state = initial
        outputs = []
        for inp in inputs:
            outputs.append(self.readout(state))
            state = self.update(state, inp)
        return outputs
```

## Wiring Diagrams

```python
@dataclass
class WiringDiagram:
    """
    Wiring diagram: composition pattern for polynomials.
    
    Specifies how outputs connect to inputs across components.
    """
    boxes: list  # Component polynomials
    wires: list  # Connections (box_idx, port) → (box_idx, port)
    
    def compose(self) -> 'Polynomial':
        """Evaluate wiring diagram to single polynomial."""
        # Trace through connections
        pass

# Example: Feedback loop
def feedback(p: Polynomial) -> Polynomial:
    """Create feedback loop: connect output to input."""
    return WiringDiagram(
        boxes=[p],
        wires=[(0, 'out', 0, 'in')]  # Connect output back to input
    ).compose()
```

## Neural Network as Polynomial

```python
import numpy as np

class NeuralLearner:
    """Neural network layer as polynomial functor learner."""
    
    def __init__(self, in_dim: int, out_dim: int):
        self.weights = np.random.randn(out_dim, in_dim) * 0.01
        self.bias = np.zeros(out_dim)
    
    def implement(self, x: np.ndarray) -> np.ndarray:
        """Forward pass."""
        return np.tanh(self.weights @ x + self.bias)
    
    def request(self, x: np.ndarray, grad_out: np.ndarray) -> np.ndarray:
        """Backward pass - compute gradient request."""
        output = self.implement(x)
        dtanh = 1 - output ** 2
        return self.weights.T @ (grad_out * dtanh)
    
    def update(self, x: np.ndarray, grad_out: np.ndarray, lr: float = 0.01):
        """Parameter update."""
        output = self.implement(x)
        dtanh = 1 - output ** 2
        delta = grad_out * dtanh
        self.weights -= lr * np.outer(delta, x)
        self.bias -= lr * delta

def compose_layers(layers: list) -> 'ComposedNetwork':
    """Compose neural layers as polynomial functor composition."""
    class ComposedNetwork:
        def __init__(self, layers):
            self.layers = layers
        
        def forward(self, x):
            for layer in self.layers:
                x = layer.implement(x)
            return x
        
        def backward(self, x, grad):
            # Store activations
            activations = [x]
            for layer in self.layers:
                x = layer.implement(x)
                activations.append(x)
            
            # Backpropagate
            for i, layer in reversed(list(enumerate(self.layers))):
                grad = layer.request(activations[i], grad)
                layer.update(activations[i], grad)
    
    return ComposedNetwork(layers)
```

## Categorical Properties

```python
def verify_lens_laws(lens: Lens, s, b):
    """Verify lens satisfies get-put and put-get laws."""
    # Get-Put: put(s, get(s)) = s
    assert lens.put(s, lens.get(s)) == s, "Get-Put law violated"
    
    # Put-Get: get(put(s, b)) = b
    assert lens.get(lens.put(s, b)) == b, "Put-Get law violated"

def verify_composition_associativity(l1, l2, l3, s, d):
    """Verify lens composition is associative."""
    left = l1.compose(l2).compose(l3)
    right = l1.compose(l2.compose(l3))
    
    assert left.get(s) == right.get(s), "Associativity violated (get)"
    assert left.put(s, d) == right.put(s, d), "Associativity violated (put)"
```

## Categorical Guarantees

Polynomial functors provide:

1. **Compositionality**: Learners compose via lens composition
2. **Bidirectionality**: Forward/backward passes as lens get/put
3. **Modularity**: Wiring diagrams specify composition patterns
4. **Dynamical Semantics**: Charts model system evolution
5. **Type Safety**: Polynomial types ensure interface compatibility
