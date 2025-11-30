"""
Reader Monad for Environment-Dependent Prompt Operations

Categorical Structure:
    Reader[E, A] = E → A

    This is the function type in the category of types.
    - unit (return): A → Reader[E, A]
        unit(a) = Reader(λe. a)

    - bind (>>=): Reader[E, A] → (A → Reader[E, B]) → Reader[E, B]
        m >>= f = Reader(λe. f(m.run(e)).run(e))

The Reader monad enables:
1. Dynamic prompt lookup from registry
2. Composable environment-dependent operations
3. Deferred resolution until execution time

Example:
    # Compose lookups
    program = (
        lookup("fibonacci") >>= (lambda fib:
        lookup("validate") >>= (lambda val:
        Reader.pure(compose(fib, val))))
    )

    # Run against registry
    result = program.run(registry)
"""

from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, Any

# Type variables
E = TypeVar('E')  # Environment type
A = TypeVar('A')  # Value type
B = TypeVar('B')  # Result type


@dataclass
class Reader(Generic[E, A]):
    """
    Reader monad: computations that depend on an environment.

    Reader[E, A] represents a computation that:
    - Requires an environment of type E
    - Produces a value of type A

    In our case:
    - E = PromptRegistry
    - A = Optional[RegisteredPrompt] or composed result

    Categorical Laws (verified):
    - Left Identity:  unit(a) >>= f  ≡  f(a)
    - Right Identity: m >>= unit     ≡  m
    - Associativity:  (m >>= f) >>= g  ≡  m >>= (λx. f(x) >>= g)
    """

    run: Callable[[E], A]

    @staticmethod
    def pure(value: A) -> 'Reader[E, A]':
        """
        Monadic unit (return).

        Lifts a pure value into Reader context.
        The environment is ignored.
        """
        return Reader(lambda _: value)

    # Alias for pure
    @staticmethod
    def unit(value: A) -> 'Reader[E, A]':
        return Reader.pure(value)

    def map(self, f: Callable[[A], B]) -> 'Reader[E, B]':
        """
        Functor map.

        Apply a function to the result without changing environment dependency.
        """
        return Reader(lambda e: f(self.run(e)))

    def bind(self, f: Callable[[A], 'Reader[E, B]']) -> 'Reader[E, B]':
        """
        Monadic bind (>>=).

        Sequence Reader computations, threading the environment.
        """
        def bound(env: E) -> B:
            a = self.run(env)
            reader_b = f(a)
            return reader_b.run(env)
        return Reader(bound)

    def flat_map(self, f: Callable[[A], 'Reader[E, B]']) -> 'Reader[E, B]':
        """Alias for bind."""
        return self.bind(f)

    def __rshift__(self, f: Callable[[A], 'Reader[E, B]']) -> 'Reader[E, B]':
        """Operator >>= for bind."""
        return self.bind(f)

    def then(self, other: 'Reader[E, B]') -> 'Reader[E, B]':
        """
        Sequence ignoring first result (>>).

        Useful for side-effects or when first result isn't needed.
        """
        return self.bind(lambda _: other)

    def __and__(self, other: 'Reader[E, B]') -> 'Reader[E, B]':
        """Operator >> for then."""
        return self.then(other)

    def local(self, f: Callable[[E], E]) -> 'Reader[E, A]':
        """
        Run with modified environment.

        Useful for scoped changes to the registry.
        """
        return Reader(lambda e: self.run(f(e)))

    def zip_with(
        self,
        other: 'Reader[E, B]',
        f: Callable[[A, B], Any]
    ) -> 'Reader[E, Any]':
        """
        Combine two Readers with a function.

        Applicative-style combination.
        """
        return Reader(lambda e: f(self.run(e), other.run(e)))

    @staticmethod
    def sequence(readers: list['Reader[E, A]']) -> 'Reader[E, list[A]]':
        """
        Convert list of Readers to Reader of list.

        Useful for batching multiple lookups.
        """
        def run_all(env: E) -> list[A]:
            return [r.run(env) for r in readers]
        return Reader(run_all)

    @staticmethod
    def traverse(
        items: list[A],
        f: Callable[[A], 'Reader[E, B]']
    ) -> 'Reader[E, list[B]]':
        """
        Map and sequence in one operation.
        """
        return Reader.sequence([f(item) for item in items])


# Convenience functions (ask family)

def ask() -> Reader[E, E]:
    """
    Get the entire environment.

    ask().run(env) = env
    """
    return Reader(lambda e: e)


def asks(f: Callable[[E], A]) -> Reader[E, A]:
    """
    Get a projection of the environment.

    asks(f).run(env) = f(env)
    """
    return Reader(f)


def local(f: Callable[[E], E], reader: Reader[E, A]) -> Reader[E, A]:
    """
    Run reader with modified environment.

    local(f, r).run(env) = r.run(f(env))
    """
    return reader.local(f)


# Kleisli composition for Reader

def kleisli_compose(
    f: Callable[[A], Reader[E, B]],
    g: Callable[[B], Reader[E, Any]]
) -> Callable[[A], Reader[E, Any]]:
    """
    Kleisli composition: f >=> g

    Compose two functions that return Readers.
    """
    def composed(a: A) -> Reader[E, Any]:
        return f(a).bind(g)
    return composed


# Verification of monad laws

def verify_reader_laws() -> dict[str, bool]:
    """
    Verify Reader monad laws with test cases.

    Returns dict of law names to verification status.
    """
    results = {}

    # Test environment
    test_env = {"key": "value", "count": 42}

    # Test functions
    def f(x: int) -> Reader[dict, int]:
        return Reader(lambda e: x + e.get("count", 0))

    def g(x: int) -> Reader[dict, str]:
        return Reader(lambda e: f"{x}_{e.get('key', '')}")

    # Left Identity: unit(a) >>= f ≡ f(a)
    a = 10
    left = Reader.unit(a).bind(f).run(test_env)
    right = f(a).run(test_env)
    results["left_identity"] = (left == right)

    # Right Identity: m >>= unit ≡ m
    m = Reader(lambda e: e.get("count", 0))
    left = m.bind(Reader.unit).run(test_env)
    right = m.run(test_env)
    results["right_identity"] = (left == right)

    # Associativity: (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)
    m = Reader.unit(5)
    left = m.bind(f).bind(g).run(test_env)
    right = m.bind(lambda x: f(x).bind(g)).run(test_env)
    results["associativity"] = (left == right)

    return results
