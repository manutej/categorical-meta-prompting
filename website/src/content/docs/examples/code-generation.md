---
title: Code Generation
description: Real-world code generation with quality guarantees.
---

# Code Generation Example

See how categorical meta-prompting transforms code generation from trial-and-error to reliable, quality-assured output.

## Before vs After

### Traditional Prompting

```
Write a rate limiter in Python.
```

**Result after 3 attempts:**
- Missing thread safety
- No error handling
- No tests
- Inconsistent naming

### Categorical Meta-Prompting

```bash
/rmp @quality:0.9 "implement rate limiter with sliding window, thread safety, and tests"
```

**Result on first execution:**
```yaml
CHECKPOINT_RMP_2:
  quality:
    correctness: 0.93
    clarity: 0.89
    completeness: 0.88
    efficiency: 0.91
    aggregate: 0.91
  status: CONVERGED
```

## The Generated Code

```python
"""Rate Limiter with Sliding Window Algorithm

Thread-safe implementation with configurable thresholds.
"""

import threading
import time
from collections import deque
from typing import Optional

class RateLimiter:
    """Sliding window rate limiter with thread safety."""

    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: float = 60.0
    ):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Window duration in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: deque = deque()
        self._lock = threading.Lock()

    def allow(self) -> bool:
        """
        Check if request should be allowed.

        Returns:
            True if request is within limits, False otherwise
        """
        with self._lock:
            now = time.monotonic()
            cutoff = now - self.window_seconds

            # Remove expired requests
            while self._requests and self._requests[0] < cutoff:
                self._requests.popleft()

            # Check limit
            if len(self._requests) >= self.max_requests:
                return False

            self._requests.append(now)
            return True

    def remaining(self) -> int:
        """Return remaining requests in current window."""
        with self._lock:
            now = time.monotonic()
            cutoff = now - self.window_seconds

            while self._requests and self._requests[0] < cutoff:
                self._requests.popleft()

            return max(0, self.max_requests - len(self._requests))

    def reset_at(self) -> Optional[float]:
        """Return when the oldest request expires."""
        with self._lock:
            if not self._requests:
                return None
            return self._requests[0] + self.window_seconds
```

## The Generated Tests

```python
import pytest
import time
import threading
from rate_limiter import RateLimiter

class TestRateLimiter:
    def test_allows_requests_within_limit(self):
        limiter = RateLimiter(max_requests=5, window_seconds=1.0)
        for _ in range(5):
            assert limiter.allow() is True

    def test_blocks_requests_over_limit(self):
        limiter = RateLimiter(max_requests=3, window_seconds=1.0)
        for _ in range(3):
            limiter.allow()
        assert limiter.allow() is False

    def test_window_expiration(self):
        limiter = RateLimiter(max_requests=2, window_seconds=0.1)
        limiter.allow()
        limiter.allow()
        assert limiter.allow() is False

        time.sleep(0.15)
        assert limiter.allow() is True

    def test_remaining_count(self):
        limiter = RateLimiter(max_requests=5, window_seconds=1.0)
        assert limiter.remaining() == 5
        limiter.allow()
        assert limiter.remaining() == 4

    def test_thread_safety(self):
        limiter = RateLimiter(max_requests=100, window_seconds=1.0)
        results = []

        def make_requests():
            for _ in range(50):
                results.append(limiter.allow())

        threads = [threading.Thread(target=make_requests) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        allowed = sum(1 for r in results if r)
        assert allowed == 100  # Exactly 100 allowed

    def test_reset_at_returns_expiration(self):
        limiter = RateLimiter(max_requests=5, window_seconds=1.0)
        assert limiter.reset_at() is None
        limiter.allow()
        assert limiter.reset_at() is not None
```

## Quality Breakdown

| Dimension | Score | Why |
|-----------|-------|-----|
| Correctness | 0.93 | Algorithm verified, edge cases handled |
| Clarity | 0.89 | Clear naming, docstrings, type hints |
| Completeness | 0.88 | Tests, error handling, thread safety |
| Efficiency | 0.91 | O(1) operations, efficient cleanup |

## The Refinement Process

```yaml
CHECKPOINT_RMP_1:
  iteration: 1
  quality: 0.78
  issues:
    - Missing thread safety
    - No type hints
  status: CONTINUE

CHECKPOINT_RMP_2:
  iteration: 2
  quality: 0.91
  improvements:
    - Added threading.Lock
    - Added type hints
    - Added remaining() method
  status: CONVERGED
```

## Key Takeaways

1. **Quality threshold ensures completeness** — Tests, types, docs included
2. **Iterative refinement catches gaps** — Thread safety added on iteration 2
3. **Measurable output** — Know exactly what quality you got
4. **Reproducible** — Same command, same quality level
