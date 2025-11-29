---
name: categorical-property-testing
description: Property-based testing for functor laws, monad laws, and naturality conditions using fp-ts and fast-check. Use when validating categorical implementations in TypeScript, testing algebraic laws in functional code, verifying functor/monad/applicative instances, or building test suites for categorical abstractions.
---

# Categorical Property Testing

Property-based testing framework for validating categorical laws using fp-ts and fast-check.

## Installation

```bash
npm install fp-ts fast-check
npm install -D vitest @types/node
```

## Core Laws

### Functor Laws

```
1. Identity:    F.map(fa, identity) ≡ fa
2. Composition: F.map(fa, x => g(f(x))) ≡ F.map(F.map(fa, f), g)
```

### Monad Laws

```
1. Left identity:  F.chain(F.of(a), f) ≡ f(a)
2. Right identity: F.chain(fa, F.of) ≡ fa
3. Associativity:  F.chain(F.chain(fa, f), g) ≡ F.chain(fa, a => F.chain(f(a), g))
```

### Natural Transformation (Naturality)

```
For α: F ⇒ G and f: A → B:
α_B ∘ F.map(f) ≡ G.map(f) ∘ α_A
```

## Test Utilities

```typescript
import * as fc from 'fast-check';
import { pipe, identity } from 'fp-ts/function';
import * as O from 'fp-ts/Option';
import * as E from 'fp-ts/Either';
import * as A from 'fp-ts/Array';
import * as T from 'fp-ts/Task';
import * as TE from 'fp-ts/TaskEither';

// Equivalence checker for fp-ts types
const optionEq = <A>(eqA: (a: A, b: A) => boolean) => 
  (fa: O.Option<A>, fb: O.Option<A>): boolean =>
    O.isNone(fa) && O.isNone(fb) ||
    (O.isSome(fa) && O.isSome(fb) && eqA(fa.value, fb.value));

const eitherEq = <E, A>(eqE: (a: E, b: E) => boolean, eqA: (a: A, b: A) => boolean) =>
  (fa: E.Either<E, A>, fb: E.Either<E, A>): boolean =>
    (E.isLeft(fa) && E.isLeft(fb) && eqE(fa.left, fb.left)) ||
    (E.isRight(fa) && E.isRight(fb) && eqA(fa.right, fb.right));

// Arbitrary generators for fp-ts types
const optionArb = <A>(arbA: fc.Arbitrary<A>): fc.Arbitrary<O.Option<A>> =>
  fc.oneof(
    fc.constant(O.none),
    arbA.map(O.some)
  );

const eitherArb = <E, A>(
  arbE: fc.Arbitrary<E>,
  arbA: fc.Arbitrary<A>
): fc.Arbitrary<E.Either<E, A>> =>
  fc.oneof(
    arbE.map(E.left),
    arbA.map(E.right)
  );

// Function generators
const intEndoArb: fc.Arbitrary<(n: number) => number> = fc.constantFrom(
  (n: number) => n + 1,
  (n: number) => n * 2,
  (n: number) => n * n,
  (n: number) => Math.abs(n),
  (n: number) => -n
);
```

## Option Functor Laws

```typescript
import { describe, it, expect } from 'vitest';

describe('Option Functor Laws', () => {
  const eq = optionEq<number>((a, b) => a === b);
  
  it('satisfies identity law: map(fa, id) ≡ fa', () => {
    fc.assert(
      fc.property(optionArb(fc.integer()), (fa) => {
        const left = pipe(fa, O.map(identity));
        const right = fa;
        return eq(left, right);
      })
    );
  });
  
  it('satisfies composition law: map(fa, g ∘ f) ≡ map(map(fa, f), g)', () => {
    fc.assert(
      fc.property(
        optionArb(fc.integer()),
        intEndoArb,
        intEndoArb,
        (fa, f, g) => {
          const composed = (x: number) => g(f(x));
          const left = pipe(fa, O.map(composed));
          const right = pipe(fa, O.map(f), O.map(g));
          return eq(left, right);
        }
      )
    );
  });
});
```

## Option Monad Laws

```typescript
describe('Option Monad Laws', () => {
  const eq = optionEq<number>((a, b) => a === b);
  
  // Kleisli arrow generator: number → Option<number>
  const kleisliArb: fc.Arbitrary<(n: number) => O.Option<number>> = fc.constantFrom(
    (n: number) => O.some(n + 1),
    (n: number) => O.some(n * 2),
    (n: number) => n > 0 ? O.some(n) : O.none,
    (_: number) => O.none
  );
  
  it('satisfies left identity: chain(of(a), f) ≡ f(a)', () => {
    fc.assert(
      fc.property(fc.integer(), kleisliArb, (a, f) => {
        const left = pipe(O.of(a), O.chain(f));
        const right = f(a);
        return eq(left, right);
      })
    );
  });
  
  it('satisfies right identity: chain(fa, of) ≡ fa', () => {
    fc.assert(
      fc.property(optionArb(fc.integer()), (fa) => {
        const left = pipe(fa, O.chain(O.of));
        const right = fa;
        return eq(left, right);
      })
    );
  });
  
  it('satisfies associativity: chain(chain(fa, f), g) ≡ chain(fa, a => chain(f(a), g))', () => {
    fc.assert(
      fc.property(
        optionArb(fc.integer()),
        kleisliArb,
        kleisliArb,
        (fa, f, g) => {
          const left = pipe(fa, O.chain(f), O.chain(g));
          const right = pipe(fa, O.chain(a => pipe(f(a), O.chain(g))));
          return eq(left, right);
        }
      )
    );
  });
});
```

## Either Functor and Monad Laws

```typescript
describe('Either Functor Laws', () => {
  const eq = eitherEq<string, number>(
    (a, b) => a === b,
    (a, b) => a === b
  );
  
  it('satisfies identity law', () => {
    fc.assert(
      fc.property(eitherArb(fc.string(), fc.integer()), (fa) => {
        const left = pipe(fa, E.map(identity));
        return eq(left, fa);
      })
    );
  });
  
  it('satisfies composition law', () => {
    fc.assert(
      fc.property(
        eitherArb(fc.string(), fc.integer()),
        intEndoArb,
        intEndoArb,
        (fa, f, g) => {
          const left = pipe(fa, E.map(x => g(f(x))));
          const right = pipe(fa, E.map(f), E.map(g));
          return eq(left, right);
        }
      )
    );
  });
});

describe('Either Monad Laws', () => {
  const eq = eitherEq<string, number>(
    (a, b) => a === b,
    (a, b) => a === b
  );
  
  const kleisliArb: fc.Arbitrary<(n: number) => E.Either<string, number>> = fc.constantFrom(
    (n: number) => E.right(n + 1),
    (n: number) => E.right(n * 2),
    (n: number) => n > 0 ? E.right(n) : E.left('negative'),
    (_: number) => E.left('error')
  );
  
  it('satisfies left identity', () => {
    fc.assert(
      fc.property(fc.integer(), kleisliArb, (a, f) => {
        const left = pipe(E.of<string, number>(a), E.chain(f));
        const right = f(a);
        return eq(left, right);
      })
    );
  });
  
  it('satisfies right identity', () => {
    fc.assert(
      fc.property(eitherArb(fc.string(), fc.integer()), (fa) => {
        const left = pipe(fa, E.chain(E.of));
        return eq(left, fa);
      })
    );
  });
  
  it('satisfies associativity', () => {
    fc.assert(
      fc.property(
        eitherArb(fc.string(), fc.integer()),
        kleisliArb,
        kleisliArb,
        (fa, f, g) => {
          const left = pipe(fa, E.chain(f), E.chain(g));
          const right = pipe(fa, E.chain(a => pipe(f(a), E.chain(g))));
          return eq(left, right);
        }
      )
    );
  });
});
```

## Natural Transformation Testing

```typescript
describe('Natural Transformation Laws', () => {
  // α: Array ⇒ Option (head)
  const head = <A>(as: A[]): O.Option<A> =>
    as.length > 0 ? O.some(as[0]) : O.none;
  
  it('head is natural: head ∘ A.map(f) ≡ O.map(f) ∘ head', () => {
    fc.assert(
      fc.property(
        fc.array(fc.integer()),
        intEndoArb,
        (fa, f) => {
          // Left: map then transform
          const left = head(pipe(fa, A.map(f)));
          
          // Right: transform then map
          const right = pipe(head(fa), O.map(f));
          
          return optionEq<number>((a, b) => a === b)(left, right);
        }
      )
    );
  });
  
  // α: Option ⇒ Array (toArray)
  const toArray = <A>(oa: O.Option<A>): A[] =>
    O.isSome(oa) ? [oa.value] : [];
  
  it('toArray is natural: toArray ∘ O.map(f) ≡ A.map(f) ∘ toArray', () => {
    fc.assert(
      fc.property(
        optionArb(fc.integer()),
        intEndoArb,
        (fa, f) => {
          const left = toArray(pipe(fa, O.map(f)));
          const right = pipe(toArray(fa), A.map(f));
          
          return left.length === right.length &&
            left.every((x, i) => x === right[i]);
        }
      )
    );
  });
});
```

## TaskEither Async Laws

```typescript
describe('TaskEither Monad Laws', async () => {
  const runAndCompare = async <E, A>(
    left: TE.TaskEither<E, A>,
    right: TE.TaskEither<E, A>,
    eq: (a: E.Either<E, A>, b: E.Either<E, A>) => boolean
  ): Promise<boolean> => {
    const [l, r] = await Promise.all([left(), right()]);
    return eq(l, r);
  };
  
  const eq = eitherEq<string, number>(
    (a, b) => a === b,
    (a, b) => a === b
  );
  
  const kleisliArb: fc.Arbitrary<(n: number) => TE.TaskEither<string, number>> = 
    fc.constantFrom(
      (n: number) => TE.right(n + 1),
      (n: number) => TE.right(n * 2),
      (n: number) => n > 0 ? TE.right(n) : TE.left('negative')
    );
  
  it('satisfies left identity', async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer(), kleisliArb, async (a, f) => {
        const left = pipe(TE.of<string, number>(a), TE.chain(f));
        const right = f(a);
        return runAndCompare(left, right, eq);
      })
    );
  });
});
```

## Generic Law Testing Framework

```typescript
import { HKT, Kind, URIS } from 'fp-ts/HKT';
import { Functor1 } from 'fp-ts/Functor';
import { Monad1 } from 'fp-ts/Monad';

// Generic functor law test
const testFunctorLaws = <F extends URIS>(
  F: Functor1<F>,
  arb: <A>(arbA: fc.Arbitrary<A>) => fc.Arbitrary<Kind<F, A>>,
  eq: <A>(eqA: (a: A, b: A) => boolean) => (fa: Kind<F, A>, fb: Kind<F, A>) => boolean
) => {
  describe(`${F.URI} Functor Laws`, () => {
    it('identity', () => {
      fc.assert(
        fc.property(arb(fc.integer()), (fa) => {
          const left = F.map(fa, identity);
          return eq<number>((a, b) => a === b)(left, fa);
        })
      );
    });
    
    it('composition', () => {
      fc.assert(
        fc.property(arb(fc.integer()), intEndoArb, intEndoArb, (fa, f, g) => {
          const left = F.map(fa, x => g(f(x)));
          const right = F.map(F.map(fa, f), g);
          return eq<number>((a, b) => a === b)(left, right);
        })
      );
    });
  });
};

// Usage
testFunctorLaws(O.Functor, optionArb, optionEq);
testFunctorLaws(E.Functor, (arb) => eitherArb(fc.string(), arb), 
  (eqA) => eitherEq((a, b) => a === b, eqA));
```

## Categorical Guarantees

This testing framework validates:

1. **Functor Laws**: Identity and composition preservation
2. **Monad Laws**: Left/right identity and associativity
3. **Naturality**: Transformations commute with mapping
4. **Parametricity**: Laws hold for all types via generics
5. **Async Safety**: TaskEither laws verified asynchronously
