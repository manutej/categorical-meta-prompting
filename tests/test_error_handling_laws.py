"""
Property-based tests for Phase 3 Error Handling (Exception Monad)

Tests verify that error handling via @catch: and @fallback: modifiers
preserves categorical laws while providing error recovery.

Based on Exception Monad (Either E A) semantics:
- Left(e): Error case
- Right(a): Success case
- catch: Error recovery operation
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import Union, Callable, TypeVar, Generic, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Type variables
E = TypeVar('E')  # Error type
A = TypeVar('A')  # Success type
B = TypeVar('B')

class CatchBehavior(Enum):
    """@catch: modifier behaviors"""
    HALT = "halt"
    LOG = "log"
    RETRY = "retry"
    SKIP = "skip"
    SUBSTITUTE = "substitute"

class FallbackStrategy(Enum):
    """@fallback: modifier strategies"""
    RETURN_BEST = "return-best"
    RETURN_LAST = "return-last"
    USE_DEFAULT = "use-default"
    EMPTY = "empty"

@dataclass
class ErrorInfo:
    """Error information with context"""
    message: str
    command: str
    stage: int
    retry_count: int = 0

# Exception Monad (Either E A)
class Either(Generic[E, A]):
    """
    Either<E, A> = Left(E) | Right(A)

    The Exception Monad for representing computations that may fail.
    """

    def __init__(self, value: Union[E, A], is_error: bool):
        self._value = value
        self._is_error = is_error

    @staticmethod
    def left(error: E) -> 'Either[E, A]':
        """Create error case: Left(e)"""
        return Either(error, True)

    @staticmethod
    def right(value: A) -> 'Either[E, A]':
        """Create success case: Right(a)"""
        return Either(value, False)

    @staticmethod
    def pure(value: A) -> 'Either[E, A]':
        """Monad return: a → Right(a)"""
        return Either.right(value)

    def is_left(self) -> bool:
        """Check if this is an error"""
        return self._is_error

    def is_right(self) -> bool:
        """Check if this is a success"""
        return not self._is_error

    def get_left(self) -> E:
        """Extract error value (unsafe)"""
        if not self._is_error:
            raise ValueError("Called get_left on Right")
        return self._value

    def get_right(self) -> A:
        """Extract success value (unsafe)"""
        if self._is_error:
            raise ValueError("Called get_right on Left")
        return self._value

    def bind(self, f: Callable[[A], 'Either[E, B]']) -> 'Either[E, B]':
        """
        Monadic bind (>>=):
        m >>= f = case m of
            Left(e) → Left(e)
            Right(a) → f(a)
        """
        if self._is_error:
            return Either.left(self._value)
        else:
            return f(self._value)

    def catch(self, handler: Callable[[E], 'Either[E, A]']) -> 'Either[E, A]':
        """
        Error recovery:
        catch(m, h) = case m of
            Left(e) → h(e)
            Right(a) → Right(a)
        """
        if self._is_error:
            return handler(self._value)
        else:
            return self

    def map(self, f: Callable[[A], B]) -> 'Either[E, B]':
        """
        Functor map:
        fmap f (Left e) = Left e
        fmap f (Right a) = Right (f a)
        """
        if self._is_error:
            return Either.left(self._value)
        else:
            return Either.right(f(self._value))

    def __eq__(self, other):
        if not isinstance(other, Either):
            return False
        return (self._is_error == other._is_error and
                self._value == other._value)

    def __repr__(self):
        if self._is_error:
            return f"Left({self._value})"
        else:
            return f"Right({self._value})"


# ============================================================================
# Test 1: Exception Monad Laws
# ============================================================================

@given(st.integers())
@settings(max_examples=100)
def test_either_left_identity(a):
    """
    Monad Left Identity Law:
    return(a) >>= f = f(a)
    """
    f = lambda x: Either.right(x * 2)

    # return(a) >>= f
    left_side = Either.pure(a).bind(f)

    # f(a)
    right_side = f(a)

    assert left_side == right_side, \
        f"Left identity failed: return({a}) >>= f ≠ f({a})"


@given(st.integers())
@settings(max_examples=100)
def test_either_right_identity(a):
    """
    Monad Right Identity Law:
    m >>= return = m
    """
    m = Either.right(a)

    # m >>= return
    result = m.bind(Either.pure)

    assert result == m, \
        f"Right identity failed: m >>= return ≠ m"


@given(st.integers())
@settings(max_examples=100)
def test_either_associativity(a):
    """
    Monad Associativity Law:
    (m >>= f) >>= g = m >>= (λx. f(x) >>= g)
    """
    m = Either.right(a)
    f = lambda x: Either.right(x * 2)
    g = lambda x: Either.right(x + 10)

    # (m >>= f) >>= g
    left_side = m.bind(f).bind(g)

    # m >>= (λx. f(x) >>= g)
    right_side = m.bind(lambda x: f(x).bind(g))

    assert left_side == right_side, \
        f"Associativity failed: (m >>= f) >>= g ≠ m >>= (λx. f(x) >>= g)"


# ============================================================================
# Test 2: Catch Laws
# ============================================================================

@given(st.integers())
@settings(max_examples=100)
def test_catch_identity_law(a):
    """
    Catch Identity Law:
    catch(Right(a), h) = Right(a)

    Successful values pass through unchanged.
    """
    h = lambda e: Either.left(f"Handled: {e}")

    m = Either.right(a)
    result = m.catch(h)

    assert result == m, \
        f"Catch identity failed: catch(Right({a}), h) ≠ Right({a})"


@given(st.text())
@settings(max_examples=100)
def test_catch_error_law(error_msg):
    """
    Catch Error Law:
    catch(Left(e), h) = h(e)

    Error handler is applied to errors.
    """
    h = lambda e: Either.right(f"Recovered from: {e}")

    m = Either.left(error_msg)
    result = m.catch(h)
    expected = h(error_msg)

    assert result == expected, \
        f"Catch error failed: catch(Left(e), h) ≠ h(e)"


@given(st.text())
@settings(max_examples=100)
def test_catch_composition_law(error_msg):
    """
    Catch Composition Law:
    catch(catch(m, h1), h2) = catch(m, λe. catch(h1(e), h2))

    Handlers compose properly.
    """
    h1 = lambda e: Either.left(f"h1({e})")
    h2 = lambda e: Either.right(f"h2({e})")

    m = Either.left(error_msg)

    # catch(catch(m, h1), h2)
    left_side = m.catch(h1).catch(h2)

    # catch(m, λe. catch(h1(e), h2))
    right_side = m.catch(lambda e: h1(e).catch(h2))

    assert left_side == right_side, \
        f"Catch composition failed"


# ============================================================================
# Test 3: Error Propagation Through Chains
# ============================================================================

@given(st.integers(), st.booleans())
@settings(max_examples=100)
def test_error_propagates_through_bind(a, fail_first):
    """
    Errors propagate automatically through >>= (bind):
    Left(e) >>= f = Left(e)  (error propagates)
    Right(a) >>= f = f(a)    (success continues)
    """
    f = lambda x: Either.right(x * 2)

    if fail_first:
        m = Either.left("error")
        result = m.bind(f)
        assert result.is_left(), "Error should propagate"
        assert result.get_left() == "error"
    else:
        m = Either.right(a)
        result = m.bind(f)
        assert result.is_right(), "Success should continue"
        assert result.get_right() == a * 2


@given(st.integers())
@settings(max_examples=100)
def test_chain_halts_on_error_with_catch_halt(a):
    """
    @catch:halt behavior:
    Chain stops immediately on error, no further execution.
    """
    # Simulate chain: cmd1 → cmd2 → cmd3
    cmd1 = lambda x: Either.right(x + 1)
    cmd2 = lambda x: Either.left("cmd2 failed")  # This fails
    cmd3 = lambda x: Either.right(x * 10)  # Should never execute

    # Execute chain
    result = Either.right(a).bind(cmd1).bind(cmd2).bind(cmd3)

    # Should halt at cmd2
    assert result.is_left(), "Chain should halt on error"
    assert result.get_left() == "cmd2 failed"


# ============================================================================
# Test 4: Retry Behavior (@catch:retry:N)
# ============================================================================

def simulate_retry(attempts: int, succeed_on: int) -> Callable[[int], Either[str, int]]:
    """
    Simulate command that fails `succeed_on - 1` times, then succeeds.
    """
    state = {"count": 0}

    def cmd(x):
        state["count"] += 1
        if state["count"] < succeed_on:
            return Either.left(f"Attempt {state['count']} failed")
        else:
            return Either.right(x * 2)

    return cmd


@given(st.integers(min_value=1, max_value=5))
@settings(max_examples=20)
def test_retry_succeeds_within_limit(succeed_on):
    """
    @catch:retry:N succeeds if command succeeds within N retries.
    """
    max_retries = 5
    assume(succeed_on <= max_retries)

    cmd = simulate_retry(max_retries, succeed_on)

    # Simulate retry logic
    result = Either.right(10)
    for _ in range(max_retries):
        result = result.bind(cmd)
        if result.is_right():
            break

    assert result.is_right(), \
        f"Should succeed on attempt {succeed_on} within {max_retries} retries"


@given(st.integers(min_value=1, max_value=10))
@settings(max_examples=20)
def test_retry_fails_after_limit(a):
    """
    @catch:retry:N fails if all N retries fail.
    """
    max_retries = 3
    cmd = lambda x: Either.left("persistent error")

    # Simulate retry logic
    result = Either.right(a)
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        result = result.bind(cmd)
        if result.is_right():
            break

    assert result.is_left(), \
        f"Should fail after {max_retries} retries"


# ============================================================================
# Test 5: Fallback Quality Preservation (@fallback:return-best)
# ============================================================================

@dataclass
class QualityResult:
    """Result with quality score"""
    value: int
    quality: float

def test_fallback_return_best_preserves_quality():
    """
    @fallback:return-best ensures:
    quality(fallback_result) >= quality(all_previous_results)
    """
    results = [
        Either.right(QualityResult(1, 0.75)),
        Either.right(QualityResult(2, 0.82)),  # Best so far
        Either.left("iteration_3_failed"),
        Either.right(QualityResult(3, 0.70)),  # Lower quality
    ]

    best_result = None
    for result in results:
        if result.is_right():
            current = result.get_right()
            if best_result is None or current.quality > best_result.quality:
                best_result = current

    # After fallback, should return best (quality=0.82)
    assert best_result.quality == 0.82, \
        "Fallback should return highest quality result"
    assert best_result.value == 2


# ============================================================================
# Test 6: Associativity Preservation with Error Handling
# ============================================================================

@given(st.integers())
@settings(max_examples=50)
def test_error_handling_preserves_associativity(a):
    """
    Error handling should not break Kleisli associativity:
    ((f @catch:h1) → g) → h = (f @catch:h1) → (g → h)
    """
    f = lambda x: Either.right(x + 1) if x >= 0 else Either.left("negative")
    g = lambda x: Either.right(x * 2)
    h = lambda x: Either.right(x + 10)
    handler = lambda e: Either.right(0)  # Recover with 0

    m = Either.right(a)

    # ((f @catch:h) >>= g) >>= h
    left_side = m.bind(f).catch(handler).bind(g).bind(h)

    # (f @catch:h) >>= (λx. g(x) >>= h)
    right_side = m.bind(f).catch(handler).bind(lambda x: g(x).bind(h))

    assert left_side == right_side, \
        "Error handling should preserve associativity"


# ============================================================================
# Test 7: Skip Behavior (@catch:skip)
# ============================================================================

@given(st.integers())
@settings(max_examples=50)
def test_skip_converts_error_to_empty(a):
    """
    @catch:skip behavior:
    Failed command → Right(empty) (continue with empty value)
    """
    cmd_fail = lambda x: Either.left("error")
    cmd_process = lambda x: Either.right(x if x else 999)  # Process or use default

    # Simulate: /risky@catch:skip → /process
    result = Either.right(a).bind(cmd_fail).catch(lambda e: Either.right(None)).bind(cmd_process)

    assert result.is_right(), "Skip should recover"
    assert result.get_right() == 999, "Should use default for empty"


# ============================================================================
# Test 8: Substitute Behavior (@catch:substitute:/backup)
# ============================================================================

@given(st.integers())
@settings(max_examples=50)
def test_substitute_uses_backup_command(a):
    """
    @catch:substitute:/backup behavior:
    Primary fails → Run backup instead
    """
    primary = lambda x: Either.left("primary_error")
    backup = lambda x: Either.right(x * 100)

    # Simulate: /primary@catch:substitute:/backup
    result = Either.right(a).bind(primary).catch(lambda e: backup(a))

    assert result.is_right(), "Backup should succeed"
    assert result.get_right() == a * 100, "Should use backup result"


# ============================================================================
# Test 9: Functor Laws Still Hold
# ============================================================================

@given(st.integers())
@settings(max_examples=100)
def test_functor_identity_with_either(a):
    """
    Functor Identity: fmap id = id
    """
    m = Either.right(a)
    result = m.map(lambda x: x)

    assert result == m, "Functor identity must hold"


@given(st.integers())
@settings(max_examples=100)
def test_functor_composition_with_either(a):
    """
    Functor Composition: fmap (g . f) = fmap g . fmap f
    """
    m = Either.right(a)
    f = lambda x: x * 2
    g = lambda x: x + 10

    # fmap (g . f)
    left_side = m.map(lambda x: g(f(x)))

    # fmap g . fmap f
    right_side = m.map(f).map(g)

    assert left_side == right_side, "Functor composition must hold"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
