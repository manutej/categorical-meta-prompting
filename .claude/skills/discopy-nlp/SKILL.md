---
name: discopy-nlp
description: DisCoPy categorical quantum NLP for string diagrams, monoidal categories, and compositional semantics in Python. Use when implementing compositional distributional semantics, building string diagram computations, working with monoidal category theory in code, creating quantum-inspired NLP models, or applying categorical semantics to natural language processing.
---

# DisCoPy Categorical Quantum NLP

DisCoPy provides Python implementations of string diagrams and monoidal categories for compositional NLP.

## Installation

```bash
pip install discopy
```

## Core Categorical Structures

### Types and Morphisms

```python
from discopy import Ty, Box, Id, Diagram

# Types (objects in monoidal category)
n = Ty('n')  # noun
s = Ty('s')  # sentence

# Morphisms (boxes between types)
john = Box('John', Ty(), n)       # John: I → n
sleeps = Box('sleeps', n, s)      # sleeps: n → s
```

### Composition and Tensor

```python
# Sequential composition (;)
john_sleeps = john >> sleeps  # John sleeps: I → s

# Parallel composition (⊗)
mary = Box('Mary', Ty(), n)
john_and_mary = john @ mary  # John ⊗ Mary: I → n ⊗ n
```

## String Diagrams

```python
# Create and draw diagram
diagram = john >> sleeps
diagram.draw()

# Export formats
diagram.draw(path="diagram.png")
```

## Pregroup Grammar

```python
from discopy.grammar.pregroup import Ty, Word, Cup, Id

# Pregroup types with adjoints
n = Ty('n')
s = Ty('s')
n_r = n.r  # right adjoint
n_l = n.l  # left adjoint

# Words with grammatical types
john = Word('John', n)
sleeps = Word('sleeps', n.r @ s)
loves = Word('loves', n.r @ s @ n.l)

# Parse "John sleeps"
sentence = john @ sleeps >> Cup(n, n.r) @ Id(s)
```

## Functorial Semantics

```python
import numpy as np
from discopy.tensor import Tensor, Dim

# Meaning functor: Grammar → Vect
d = Dim(2)

john_vec = Tensor(dom=Dim(1), cod=d, array=np.array([1, 0]))
sleeps_mat = Tensor(dom=d, cod=Dim(1), array=np.array([0.8, 0.2]))

# Compose to get sentence meaning
result = john_vec >> sleeps_mat
```

## Quantum Circuit Semantics

```python
from discopy.quantum import Circuit, Ket, Bra, H, CX

# Map words to quantum circuits
john_circuit = Ket(0)
mary_circuit = Ket(1)
entangle = CX >> (H @ Circuit.id(1))
```

## Categorical Guarantees

DisCoPy ensures:

1. **Monoidal Laws**: Associativity and unit laws for ⊗
2. **Functoriality**: Semantic maps preserve composition
3. **String Diagram Correctness**: Diagrams represent valid morphisms
4. **Type Safety**: Composition only when types match
