---
name: hasktorch-typed
description: Hasktorch type-safe tensor operations with categorical structure preservation. Use when implementing type-safe deep learning in Haskell, leveraging dependent types for tensor shape verification, applying categorical abstractions to neural network design, or building formally verified ML pipelines with strong type guarantees.
---

# Hasktorch Type-Safe Tensor Operations

Hasktorch provides type-safe PyTorch bindings for Haskell with categorical structure.

## Installation

```bash
# In stack.yaml or cabal
extra-deps:
  - hasktorch-0.2.0.0
  - libtorch-ffi-0.2.0.0
```

## Core Categorical Concepts

Hasktorch embodies category theory:

- **Tensor[shape, dtype]**: Dependent type with shape as type parameter
- **Linear**: Functor between vector space categories
- **Composition**: Type-safe layer stacking
- **Backprop**: Automatic differentiation as reverse-mode AD functor

## Type-Safe Tensors

```haskell
{-# LANGUAGE DataKinds #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}

import Torch
import Torch.Typed

-- Tensor with shape in type
type BatchSize = 32
type InputDim = 784
type HiddenDim = 256
type OutputDim = 10

-- Shape-indexed tensor
input :: Tensor '[BatchSize, InputDim] Float
input = zeros

-- Type error if shapes don't match!
-- badMul = matmul input input  -- Won't compile: shape mismatch

-- Correct matrix multiplication
weights :: Tensor '[InputDim, HiddenDim] Float
weights = randn

output :: Tensor '[BatchSize, HiddenDim] Float
output = matmul input weights  -- Compiles: shapes align
```

## Typed Neural Network Layers

```haskell
{-# LANGUAGE TypeApplications #-}
{-# LANGUAGE ScopedTypeVariables #-}

-- Linear layer as morphism: R^in → R^out
data Linear (inputDim :: Nat) (outputDim :: Nat) where
  Linear :: 
    { weight :: Tensor '[outputDim, inputDim] Float
    , bias   :: Tensor '[outputDim] Float
    } -> Linear inputDim outputDim

-- Forward pass preserves type
forward :: 
  forall batchSize inputDim outputDim.
  Linear inputDim outputDim -> 
  Tensor '[batchSize, inputDim] Float -> 
  Tensor '[batchSize, outputDim] Float
forward (Linear w b) x = 
  matmul x (transpose w) `add` broadcast b

-- Initialize with Kaiming
mkLinear :: 
  forall inputDim outputDim.
  (KnownNat inputDim, KnownNat outputDim) =>
  IO (Linear inputDim outputDim)
mkLinear = do
  w <- kaimingUniform @'[outputDim, inputDim]
  b <- zeros @'[outputDim]
  pure $ Linear w b
```

## Composable Network Architecture

```haskell
-- Sequential composition of layers
data Sequential layers where
  SNil  :: Sequential '[]
  SCons :: layer -> Sequential layers -> Sequential (layer ': layers)

-- Type-safe forward through sequence
class Forward layers input output where
  seqForward :: Sequential layers -> input -> output

instance Forward '[] a a where
  seqForward SNil x = x

instance 
  (Forward layers mid output, ForwardLayer layer input mid) => 
  Forward (layer ': layers) input output where
  seqForward (SCons layer rest) x = 
    seqForward rest (forwardLayer layer x)

-- Example: MLP with type-safe dimensions
type MLP = Sequential
  '[ Linear 784 256
   , ReLU
   , Linear 256 128
   , ReLU
   , Linear 128 10
   , Softmax
   ]

mlp :: MLP
mlp = SCons linear1 
    $ SCons ReLU 
    $ SCons linear2 
    $ SCons ReLU 
    $ SCons linear3 
    $ SCons Softmax 
    $ SNil
```

## Functor Structure

```haskell
-- Tensor as Functor over element type
instance Functor (Tensor shape) where
  fmap f tensor = map f tensor

-- Verify functor laws
-- fmap id tensor == tensor
-- fmap (g . f) tensor == fmap g (fmap f tensor)

-- Applicative for element-wise operations
instance Applicative (Tensor shape) where
  pure = fill
  (<*>) = zipWith ($)

-- Monad for dependent computations
instance Monad (Tensor shape) where
  tensor >>= f = join (fmap f tensor)
```

## Automatic Differentiation

```haskell
import Torch.Autograd

-- Gradient computation as reverse-mode AD
computeGradient :: 
  (Tensor '[n] Float -> Tensor '[] Float) ->  -- Loss function
  Tensor '[n] Float ->                         -- Input
  Tensor '[n] Float                            -- Gradient
computeGradient loss x = 
  let y = loss x
      grads = grad y [x]
  in head grads

-- Training step with typed gradients
trainStep ::
  forall inputDim outputDim.
  Linear inputDim outputDim ->
  Tensor '[BatchSize, inputDim] Float ->
  Tensor '[BatchSize, outputDim] Float ->
  Float ->
  Linear inputDim outputDim
trainStep layer input target lr =
  let output = forward layer input
      loss = mse output target
      (gradW, gradB) = grad loss [weight layer, bias layer]
  in Linear 
       { weight = weight layer - lr `scale` gradW
       , bias = bias layer - lr `scale` gradB
       }
```

## Shape Arithmetic

```haskell
{-# LANGUAGE TypeOperators #-}
{-# LANGUAGE UndecidableInstances #-}

import GHC.TypeLits

-- Type-level shape operations
type family MatMulShape (a :: [Nat]) (b :: [Nat]) :: [Nat] where
  MatMulShape '[m, k] '[k, n] = '[m, n]
  MatMulShape '[b, m, k] '[k, n] = '[b, m, n]

-- Compile-time shape verification
matmul :: 
  Tensor a dtype -> 
  Tensor b dtype -> 
  Tensor (MatMulShape a b) dtype

-- Type-level broadcasting
type family Broadcast (a :: [Nat]) (b :: [Nat]) :: [Nat] where
  Broadcast '[] b = b
  Broadcast a '[] = a
  Broadcast (a ': as) (b ': bs) = Max a b ': Broadcast as bs

type family Max (a :: Nat) (b :: Nat) :: Nat where
  Max 1 b = b
  Max a 1 = a
  Max a a = a
```

## Categorical Deep Learning Patterns

```haskell
-- Neural network as Para morphism (Gavranović et al.)
newtype Para p a b = Para { runPara :: p -> a -> b }

instance Category (Para p) where
  id = Para $ \_ x -> x
  (Para g) . (Para f) = Para $ \p x -> g p (f p x)

-- Linear layer in Para
linearPara :: 
  Linear inputDim outputDim -> 
  Para (Linear inputDim outputDim) 
       (Tensor '[batch, inputDim] Float) 
       (Tensor '[batch, outputDim] Float)
linearPara _ = Para forward

-- Lens for backpropagation (bidirectional)
data Lens s t a b = Lens
  { view :: s -> a
  , update :: s -> b -> t
  }

-- Backprop as lens composition
backpropLens ::
  Lens param param (Tensor shape Float) (Tensor shape Float)
backpropLens = Lens
  { view = \p -> forward p input
  , update = \p grad -> p - lr `scale` grad
  }
```

## Training Loop

```haskell
import Control.Monad (foldM)

trainEpoch ::
  forall inputDim outputDim.
  Linear inputDim outputDim ->
  [(Tensor '[BatchSize, inputDim] Float, Tensor '[BatchSize, outputDim] Float)] ->
  Float ->
  IO (Linear inputDim outputDim)
trainEpoch model batches lr =
  foldM step model batches
  where
    step m (x, y) = pure $ trainStep m x y lr

train ::
  forall inputDim outputDim.
  Linear inputDim outputDim ->
  Dataset ->
  Int ->    -- epochs
  Float ->  -- learning rate
  IO (Linear inputDim outputDim)
train model dataset epochs lr = do
  batches <- toBatches dataset
  foldM (\m _ -> trainEpoch m batches lr) model [1..epochs]
```

## Categorical Guarantees

Hasktorch provides:

1. **Shape Safety**: Tensor shapes verified at compile time
2. **Type-Safe Composition**: Layers compose only if shapes match
3. **Functor Laws**: Tensor operations preserve categorical structure
4. **Dependent Types**: Rich type-level computation for shapes
5. **Para Structure**: Networks as parameterized morphisms
