# Categorical Meta-Prompting Examples Library

**Purpose**: Practical, validated examples for each categorical structure and their compositions.
**Status**: Living document - examples validated through use
**Version**: 1.0

---

## Table of Contents

1. [Functor F Examples](#1-functor-f-examples) - Task → Prompt
2. [Monad M Examples](#2-monad-m-examples) - Iterative Refinement
3. [Comonad W Examples](#3-comonad-w-examples) - Context Extraction
4. [Natural Transformation α Examples](#4-natural-transformation-α-examples) - Strategy Switching
5. [Composite Examples](#5-composite-examples) - Combining Structures
6. [Real-World Workflows](#6-real-world-workflows) - Production Patterns

---

## 1. Functor F Examples

**Structure**: F: Task → Prompt (structure-preserving transformation)
**Command**: `/meta`
**Key Property**: Preserves task structure while transforming to appropriate prompt

### Example 1.1: Simple Task Transformation

**Use Case**: Convert a user's informal request into a well-structured prompt

```bash
/meta "fix the login bug"
```

**Input Task**: "fix the login bug"

**F(Task) → Prompt**:
```
I need to fix a login bug. Let me approach this systematically:

1. First, I'll identify the symptoms and error messages
2. Then, I'll locate the relevant code in the authentication flow
3. Next, I'll diagnose the root cause
4. Finally, I'll implement and verify the fix

Let me start by examining the login-related code...
```

**Why it's a Functor**: The transformation preserves the "fix bug" structure while adding systematic approach.

---

### Example 1.2: Domain-Specific Transformation

**Use Case**: Transform task with explicit domain routing

```bash
/meta @domain:SECURITY "review the API endpoints"
```

**Input Task**: "review the API endpoints" + domain=SECURITY

**F(Task) → Prompt**:
```
Security Review: API Endpoints

I'll conduct a security-focused review of the API endpoints, checking for:

□ Authentication & Authorization
  - Are all endpoints properly authenticated?
  - Is role-based access control implemented?
  - Are there any unprotected admin routes?

□ Input Validation
  - SQL injection vulnerabilities
  - XSS attack vectors
  - Command injection risks

□ Data Exposure
  - Sensitive data in responses
  - Proper error message handling
  - Information leakage in headers

□ Rate Limiting & DoS Protection
  - Request throttling
  - Resource exhaustion prevention

Let me examine each endpoint...
```

**Why it's a Functor**: Domain modifier changes the "lens" but preserves review structure.

---

### Example 1.3: Tier-Based Complexity Scaling

**Use Case**: Same task at different complexity tiers

```bash
# Simple version
/meta @tier:L2 "implement caching"

# Complex version
/meta @tier:L5 "implement caching"
```

**L2 Output** (simple):
```
Implement basic caching for the application.

Approach:
1. Identify frequently accessed data
2. Add in-memory cache (e.g., Map or simple object)
3. Set TTL for cache entries
4. Add cache invalidation on updates
```

**L5 Output** (complex):
```
Implement comprehensive caching strategy.

Architecture Analysis:
├── Cache Layers
│   ├── L1: In-memory (fastest, limited size)
│   ├── L2: Redis/Memcached (shared, scalable)
│   └── L3: CDN edge (geographic distribution)
│
├── Cache Strategies by Data Type
│   ├── User sessions → Redis with TTL
│   ├── API responses → HTTP cache headers + CDN
│   ├── Database queries → Query result cache
│   └── Computed values → Memoization
│
├── Invalidation Patterns
│   ├── Time-based (TTL)
│   ├── Event-based (pub/sub)
│   └── Version-based (cache keys with version)
│
└── Monitoring
    ├── Hit/miss ratios
    ├── Memory usage
    └── Latency metrics

Implementation Plan:
[Detailed multi-phase plan...]
```

**Why it's a Functor**: Tier parameter scales complexity while preserving caching intent.

---

### Example 1.4: Template-Driven Transformation

**Use Case**: Apply specific context + mode + format

```bash
/meta @template:{context:expert}+{mode:cot}+{format:code} "implement rate limiter"
```

**F(Task) → Prompt**:
```python
"""
Rate Limiter Implementation - Expert Analysis

Let me think through this step by step as a systems expert:

Step 1: Algorithm Selection
- Token bucket: Good for bursty traffic, allows temporary spikes
- Sliding window: More accurate, but more complex
- Fixed window: Simple but has boundary issues

For most API use cases, token bucket provides the best balance.

Step 2: Core Implementation
"""

from dataclasses import dataclass
from time import time
from threading import Lock

@dataclass
class RateLimiter:
    """Token bucket rate limiter."""

    capacity: int          # Max tokens
    refill_rate: float     # Tokens per second
    tokens: float = None
    last_refill: float = None
    _lock: Lock = None

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time()
        self._lock = Lock()

    def allow(self) -> bool:
        """Check if request is allowed and consume token."""
        with self._lock:
            self._refill()
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now

# Step 3: Usage example
limiter = RateLimiter(capacity=100, refill_rate=10)  # 100 tokens, 10/sec refill

if limiter.allow():
    process_request()
else:
    return_429_too_many_requests()
```

**Why it's a Functor**: Template components compose to transform task into expert CoT code.

---

## 2. Monad M Examples

**Structure**: M: Prompt →^n Prompt (iterative refinement)
**Command**: `/rmp`
**Key Property**: Kleisli composition with quality tracking

### Example 2.1: Quality-Gated Iteration

**Use Case**: Refine implementation until quality threshold met

```bash
/rmp @quality:0.85 "implement password validation"
```

**Iteration 1** (quality: 0.65):
```python
def validate_password(password):
    if len(password) < 8:
        return False
    return True
```

**Quality Assessment**:
- Correctness: 0.5 (too basic)
- Completeness: 0.3 (missing many checks)
- → Aggregate: 0.65 → CONTINUE

**Iteration 2** (quality: 0.78):
```python
import re

def validate_password(password: str) -> tuple[bool, list[str]]:
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain lowercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain a digit")

    return len(errors) == 0, errors
```

**Quality Assessment**:
- Correctness: 0.8 (good basics)
- Completeness: 0.7 (missing special chars, common password check)
- → Aggregate: 0.78 → CONTINUE

**Iteration 3** (quality: 0.88):
```python
import re
from typing import NamedTuple

class ValidationResult(NamedTuple):
    valid: bool
    errors: list[str]
    strength: str  # weak, medium, strong

# Common passwords to reject (in practice, use larger list)
COMMON_PASSWORDS = {'password', '12345678', 'qwerty123', 'letmein'}

def validate_password(password: str) -> ValidationResult:
    """
    Validate password strength and return detailed result.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Not a common password
    """
    errors = []

    if len(password) < 8:
        errors.append("Minimum 8 characters required")
    if len(password) > 128:
        errors.append("Maximum 128 characters allowed")
    if not re.search(r'[A-Z]', password):
        errors.append("At least one uppercase letter required")
    if not re.search(r'[a-z]', password):
        errors.append("At least one lowercase letter required")
    if not re.search(r'\d', password):
        errors.append("At least one digit required")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("At least one special character required")
    if password.lower() in COMMON_PASSWORDS:
        errors.append("Password is too common")

    # Calculate strength
    strength_score = sum([
        len(password) >= 12,
        len(password) >= 16,
        bool(re.search(r'[A-Z].*[A-Z]', password)),  # Multiple uppercase
        bool(re.search(r'\d.*\d', password)),         # Multiple digits
        bool(re.search(r'[!@#$%^&*].*[!@#$%^&*]', password)),  # Multiple special
    ])

    strength = 'weak' if strength_score < 2 else 'medium' if strength_score < 4 else 'strong'

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        strength=strength
    )
```

**Quality Assessment**:
- Correctness: 0.9
- Completeness: 0.85
- Clarity: 0.9
- → Aggregate: 0.88 → CONVERGED ✓

---

### Example 2.2: Algorithm Optimization Loop

**Use Case**: Optimize algorithm performance iteratively

```bash
/rmp @quality:0.9 @max_iterations:5 "optimize this sorting function for large datasets"
```

**Iteration 1**: Basic optimization (quality: 0.72)
```python
# Start: Bubble sort O(n²)
# Improvement: Use built-in sort
def sort_data(data):
    return sorted(data)  # Timsort O(n log n)
```

**Iteration 2**: Memory optimization (quality: 0.81)
```python
def sort_data(data):
    # In-place sort to reduce memory
    data.sort()
    return data

# For very large datasets, consider chunked processing
def sort_large_dataset(data, chunk_size=1_000_000):
    if len(data) <= chunk_size:
        data.sort()
        return data
    # External merge sort for huge datasets
    return external_merge_sort(data, chunk_size)
```

**Iteration 3**: Full optimization (quality: 0.91)
```python
from typing import TypeVar, Callable, Iterator
import heapq
from functools import partial

T = TypeVar('T')

def sort_data(
    data: list[T],
    key: Callable[[T], any] = None,
    reverse: bool = False,
    memory_limit_mb: int = 100
) -> list[T]:
    """
    Optimized sorting with automatic strategy selection.

    - Small datasets: In-place Timsort
    - Large datasets: External merge sort
    - Partial sorts: Heapq for top-k
    """
    estimated_size_mb = len(data) * 64 / (1024 * 1024)  # Rough estimate

    if estimated_size_mb < memory_limit_mb:
        # Fast path: in-memory sort
        data.sort(key=key, reverse=reverse)
        return data
    else:
        # Memory-efficient path: chunked external sort
        return _external_merge_sort(data, key, reverse, memory_limit_mb)

def top_k(data: list[T], k: int, key: Callable[[T], any] = None) -> list[T]:
    """Efficient top-k selection without full sort. O(n log k)"""
    if key:
        return heapq.nlargest(k, data, key=key)
    return heapq.nlargest(k, data)
```

→ CONVERGED at quality 0.91 ✓

---

### Example 2.3: Documentation Refinement

**Use Case**: Iteratively improve documentation quality

```bash
/rmp @quality:0.85 "document the authentication flow"
```

Iterates through:
1. Basic description → 2. Added diagrams → 3. Added examples → 4. Added edge cases

---

## 3. Comonad W Examples

**Structure**: W: History → Context (context extraction)
**Command**: `/context`
**Key Property**: Extract, duplicate, extend operations on context

### Example 3.1: Extract Recent Context

**Use Case**: Get focused summary of recent work

```bash
/context @mode:extract @focus:recent @depth:5 "what have we accomplished?"
```

**W.extract(history) → Context**:
```yaml
EXTRACTED_CONTEXT:
  focus: recent_5_interactions

  summary: |
    In this session, we've been building a categorical meta-prompting framework.

  key_accomplishments:
    - Implemented Comonad W operations (/context command)
    - Added Natural Transformation α (/transform command)
    - Created property-based tests for categorical laws
    - Updated framework to v2.2

  current_state:
    - Framework has F, M, W, α coverage
    - Overall coverage at 85%
    - Tests written but pytest not installed

  active_files:
    - .claude/commands/transform.md
    - .claude/commands/context.md
    - tests/test_natural_transformation_laws.py

  next_likely_action: "Create examples and populate prompt registry"
```

---

### Example 3.2: File-Focused Context

**Use Case**: Get context relevant to a specific file

```bash
/context @mode:extract @focus:file "src/auth/login.ts"
```

**W.extract(history, file_filter) → Context**:
```yaml
EXTRACTED_CONTEXT:
  focus: file
  file: src/auth/login.ts

  relevant_history:
    - "Fixed login bug in session handling" (3 interactions ago)
    - "Added rate limiting to login endpoint" (7 interactions ago)
    - "Reviewed login security" (12 interactions ago)

  file_context:
    purpose: "Handles user authentication flow"
    dependencies: ["src/auth/session.ts", "src/db/users.ts"]
    recent_changes: ["Session timeout fix", "Rate limit integration"]

  related_decisions:
    - "Using JWT for stateless auth"
    - "Redis for session storage"
    - "Bcrypt for password hashing"
```

---

### Example 3.3: Meta-Observation (Duplicate)

**Use Case**: Debug why a prompt approach isn't working

```bash
/context @mode:duplicate "why did the last implementation fail?"
```

**W.duplicate(history) → W(W(history))**:
```yaml
META_OBSERVATION:
  level: 2  # Observing the observation

  what_was_focused:
    - Task: "implement caching"
    - Approach: Direct implementation
    - Context used: File structure only

  what_was_missed:
    - Existing cache utilities in utils/cache.ts
    - Project convention for caching (Redis, not in-memory)
    - Related PR #42 that added cache infrastructure

  why_it_failed:
    - Insufficient context gathering before implementation
    - Didn't search for existing patterns
    - Assumed in-memory cache when project uses Redis

  recommendation:
    - Before implementing: "/context @focus:all" to gather full context
    - Search for existing patterns: "grep cache"
    - Check recent PRs for infrastructure changes

  meta_insight: |
    The context extraction was too narrow. When implementing infrastructure
    (caching, logging, auth), always expand context to project-wide first.
```

---

### Example 3.4: Context-Aware Transformation (Extend)

**Use Case**: Summarize with full context awareness

```bash
/context @mode:extend @transform:summarize "create executive summary of session"
```

**W.extend(summarize)(history) → W(Summary)**:
```yaml
CONTEXTUALIZED_SUMMARY:
  transformation: summarize
  context_depth: full_session

  executive_summary: |
    ## Session: Categorical Meta-Prompting Framework Development

    **Objective**: Build a mathematically rigorous prompt engineering framework
    based on category theory.

    **Approach**: Implemented core categorical structures as Claude Code commands:
    - Functor F → /meta (task transformation)
    - Monad M → /rmp (iterative refinement)
    - Comonad W → /context (context extraction)
    - Natural Transformation α → /transform (strategy switching)

    **Key Deliverables**:
    1. 4 new commands with full documentation
    2. Property-based tests verifying categorical laws
    3. Framework documentation and examples

    **Quality Metrics**:
    - Categorical coverage: 85%
    - Test coverage: Comonad + Nat. Trans. laws
    - Documentation: Comprehensive

    **Next Steps**: Validate with practical examples, populate prompt registry

  context_factors_considered:
    - Full conversation history
    - Files created and modified
    - Quality assessments
    - User feedback and direction
```

---

## 4. Natural Transformation α Examples

**Structure**: α: F ⇒ G (transformation between functors/strategies)
**Command**: `/transform`
**Key Property**: Naturality - α_B ∘ F(f) = G(f) ∘ α_A

### Example 4.1: Zero-Shot → Chain-of-Thought

**Use Case**: Upgrade a simple prompt to reasoning format

```bash
/transform @from:zero-shot @to:chain-of-thought "explain binary search"
```

**F_ZS(Task)**:
```
Explain binary search.
```

**α[ZS→CoT]: F_ZS(Task) → F_CoT(Task)**:
```
Explain binary search.

Let me think through this step by step:

1. **What is binary search?**
   Binary search is an efficient algorithm for finding an element in a sorted array.

2. **How does it work?**
   - Start with the middle element
   - If target equals middle, we're done
   - If target < middle, search left half
   - If target > middle, search right half
   - Repeat until found or exhausted

3. **Why is it efficient?**
   Each step eliminates half the remaining elements.
   For n elements: log₂(n) comparisons maximum.

   Example: 1 million elements → only 20 comparisons!

4. **Key requirement**
   The array MUST be sorted. Unsorted arrays require linear search.

5. **Code example**
   ```python
   def binary_search(arr, target):
       left, right = 0, len(arr) - 1
       while left <= right:
           mid = (left + right) // 2
           if arr[mid] == target:
               return mid
           elif arr[mid] < target:
               left = mid + 1
           else:
               right = mid - 1
       return -1
   ```

Therefore, binary search is O(log n) - one of the most efficient search algorithms
for sorted data.
```

**Quality Factor**: 1.25 (ZS baseline 0.65 → CoT 0.81)

---

### Example 4.2: Few-Shot → Chain-of-Thought

**Use Case**: Convert example-based prompt to reasoning-based

```bash
/transform @from:few-shot @to:chain-of-thought "classify sentiment"
```

**F_FS(Task)**:
```
Example 1:
Input: "This product is amazing!"
Output: Positive

Example 2:
Input: "Terrible experience, never again."
Output: Negative

Example 3:
Input: "It's okay, nothing special."
Output: Neutral

Now classify: "The quality exceeded my expectations but shipping was slow."
```

**α[FS→CoT]: F_FS(Task) → F_CoT(Task)**:
```
I need to classify the sentiment of: "The quality exceeded my expectations but shipping was slow."

Let me analyze this step by step:

1. **Identify sentiment-bearing phrases**:
   - "quality exceeded my expectations" → Positive sentiment
   - "shipping was slow" → Negative sentiment

2. **Assess intensity**:
   - "exceeded expectations" is strongly positive
   - "slow" is mildly negative

3. **Consider the conjunction**:
   - "but" typically signals contrast
   - The structure is: [positive point] but [negative point]

4. **Weigh the overall sentiment**:
   - Product quality (core value) → Positive
   - Shipping speed (logistics) → Negative
   - Quality often weighs more than logistics for product reviews

5. **Apply patterns from examples**:
   - "amazing" (Ex 1) ≈ "exceeded expectations" → both strongly positive
   - "terrible" (Ex 2) ≠ "slow" → different intensity levels
   - Not neutral like Ex 3 - has clear positive and negative elements

6. **Final classification**:
   The positive sentiment about the core product outweighs the negative
   sentiment about shipping. However, it's not purely positive.

Output: **Mixed (leaning Positive)** or if binary required: **Positive**

Confidence: 75% - the "but" clause introduces genuine negativity
```

---

### Example 4.3: Strategy Comparison

**Use Case**: Compare how different strategies handle same task

```bash
/transform @mode:compare @from:zero-shot @to:tree-of-thought "solve: find shortest path"
```

**Output**:
```yaml
STRATEGY_COMPARISON:
  task: "find shortest path"

  zero_shot:
    approach: Direct answer
    output: |
      Use Dijkstra's algorithm for weighted graphs or BFS for unweighted.
    quality: 0.65
    tokens: ~50
    best_for: "Quick answers, simple queries"

  tree_of_thought:
    approach: Explore multiple solution paths
    output: |
      Branch A: Graph-based algorithms
        ├── Dijkstra's (weighted, non-negative)
        │   Evaluation: Best for road networks, GPS
        ├── Bellman-Ford (handles negative weights)
        │   Evaluation: Slower but more general
        └── A* (heuristic-guided)
            Evaluation: Best for spatial problems

      Branch B: Dynamic Programming
        ├── Floyd-Warshall (all pairs)
        │   Evaluation: Good for dense graphs, precomputation
        └── Matrix exponentiation
            Evaluation: Specific use cases

      Branch C: Specialized approaches
        ├── BFS (unweighted)
        │   Evaluation: Simplest, O(V+E)
        └── Bidirectional search
            Evaluation: 2x speedup for point-to-point

      BEST PATH: Branch A → A* for most practical applications
    quality: 0.88
    tokens: ~400
    best_for: "Complex decisions, exploring trade-offs"

  recommendation: |
    Use Zero-Shot for simple "what algorithm" questions.
    Use Tree-of-Thought when comparing approaches or making architectural decisions.

  quality_improvement: +0.23 (35% better)
  cost_increase: +350 tokens (8x more)
```

---

### Example 4.4: Auto-Analyze Best Strategy

**Use Case**: Let the system recommend optimal strategy

```bash
/transform @mode:analyze "debug intermittent test failure"
```

**Output**:
```yaml
STRATEGY_ANALYSIS:
  task: "debug intermittent test failure"

  task_classification:
    type: debugging
    complexity: high
    uncertainty: high (intermittent = non-deterministic)

  strategy_evaluation:
    zero_shot:
      score: 0.40
      reason: "Intermittent issues need systematic exploration"

    few_shot:
      score: 0.55
      reason: "Examples help but each intermittent bug is unique"

    chain_of_thought:
      score: 0.82
      reason: "Step-by-step reasoning good for debugging"

    tree_of_thought:
      score: 0.78
      reason: "Multiple hypotheses useful but may be overkill"

    self_consistency:
      score: 0.85
      reason: "Multiple reasoning paths help catch flaky causes"

  recommendation:
    primary: self_consistency
    fallback: chain_of_thought

  suggested_prompt: |
    /transform @from:zero-shot @to:self-consistency "debug: {details}"

    This will generate multiple independent analyses of the intermittent
    failure, then synthesize common findings. Intermittent bugs often have
    multiple contributing factors that single-path reasoning might miss.
```

---

## 5. Composite Examples

### Example 5.1: F → M (Transform then Refine)

**Use Case**: Generate implementation then refine to quality threshold

```bash
/chain [/meta @tier:L3 → /rmp @quality:0.85] "implement LRU cache"
```

**Stage 1: F(Task) → Prompt**
```python
# Initial implementation from /meta
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, key):
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return -1

    def put(self, key, value):
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.order.append(key)
```

**Stage 2: M(Prompt) →^n Prompt** (quality: 0.68 → 0.87)
```python
from collections import OrderedDict
from threading import Lock
from typing import TypeVar, Generic, Optional

K = TypeVar('K')
V = TypeVar('V')

class LRUCache(Generic[K, V]):
    """
    Thread-safe LRU Cache with O(1) operations.

    Uses OrderedDict for efficient order tracking.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache: OrderedDict[K, V] = OrderedDict()
        self._lock = Lock()

    def get(self, key: K) -> Optional[V]:
        """Get value and mark as recently used. O(1)"""
        with self._lock:
            if key not in self.cache:
                return None
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: K, value: V) -> None:
        """Add/update value. Evicts LRU if at capacity. O(1)"""
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.capacity:
                    # Remove oldest (first item)
                    self.cache.popitem(last=False)
            self.cache[key] = value

    def __len__(self) -> int:
        return len(self.cache)

    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self.cache.clear()
```

**Quality Journey**: 0.68 → 0.75 → 0.87 ✓

---

### Example 5.2: W → F (Context then Transform)

**Use Case**: Extract context before generating implementation

```bash
/chain [/context @mode:extract @focus:file → /meta] "add validation to user model"
```

**Stage 1: W.extract(history) → Context**
```yaml
CONTEXT:
  file_focus: "src/models/user.ts"

  existing_patterns:
    - Uses class-validator decorators
    - Follows DTO pattern
    - Has existing email validation

  related_code:
    - "src/models/base.ts" - BaseEntity with common fields
    - "src/validators/custom.ts" - Custom validators

  project_conventions:
    - Zod for runtime validation
    - class-validator for DTOs
    - Custom error messages required
```

**Stage 2: F(Task + Context) → Prompt**
```typescript
// Context-aware implementation following project patterns
import { IsEmail, IsString, MinLength, Matches, IsOptional } from 'class-validator';
import { z } from 'zod';

// DTO with class-validator (following existing pattern)
export class CreateUserDto {
  @IsEmail({}, { message: 'Please provide a valid email address' })
  email: string;

  @IsString()
  @MinLength(8, { message: 'Password must be at least 8 characters' })
  @Matches(/^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)/, {
    message: 'Password must contain uppercase, lowercase, and number'
  })
  password: string;

  @IsString()
  @MinLength(2, { message: 'Name must be at least 2 characters' })
  name: string;

  @IsOptional()
  @Matches(/^\+?[1-9]\d{1,14}$/, { message: 'Invalid phone number format' })
  phone?: string;
}

// Zod schema for runtime validation (following project pattern)
export const UserSchema = z.object({
  email: z.string().email('Please provide a valid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)/,
      'Password must contain uppercase, lowercase, and number'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
  phone: z.string().regex(/^\+?[1-9]\d{1,14}$/).optional(),
});
```

**Key**: Context extraction ensured we followed existing project patterns!

---

### Example 5.3: α → M (Transform Strategy then Refine)

**Use Case**: Switch to better strategy then refine

```bash
/chain [/transform @from:zero-shot @to:chain-of-thought → /rmp @quality:0.9] "design database schema for blog"
```

**Stage 1: α[ZS→CoT]** - Upgrade to reasoning
```
Let me design a database schema for a blog step by step...
[Initial CoT schema design]
```

**Stage 2: M(Prompt) →^n Prompt** - Refine until 0.9
```sql
-- Iteration 3: Final refined schema (quality: 0.91)

-- Users table with proper indexing
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    bio TEXT,
    avatar_url VARCHAR(500),
    role VARCHAR(20) DEFAULT 'author' CHECK (role IN ('admin', 'author', 'reader')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);

-- Posts with full-text search support
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(220) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    excerpt VARCHAR(500),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- Full-text search vector
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'B')
    ) STORED
);
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_slug ON posts(slug);
CREATE INDEX idx_posts_status ON posts(status) WHERE status = 'published';
CREATE INDEX idx_posts_search ON posts USING GIN(search_vector);

-- Tags with many-to-many relationship
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE post_tags (
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);
CREATE INDEX idx_post_tags_tag ON post_tags(tag_id);

-- Comments with threading support
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'spam')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_comments_post ON comments(post_id);
CREATE INDEX idx_comments_parent ON comments(parent_id);
```

---

### Example 5.4: Full Pipeline (W → α → F → M)

**Use Case**: Complete workflow for complex feature

```bash
/chain [
  /context @mode:extract @focus:all →
  /transform @mode:analyze →
  /meta @tier:L4 →
  /rmp @quality:0.88
] "implement real-time notifications"
```

**Stage 1**: Extract project context
**Stage 2**: Analyze and select optimal strategy (→ CoT recommended)
**Stage 3**: Transform task to structured prompt with CoT
**Stage 4**: Refine until quality 0.88

**Final Output**: Production-ready notification system matching project patterns.

---

## 6. Real-World Workflows

### Workflow 6.1: Bug Fix Pipeline

```bash
/chain [
  /context @mode:extract @focus:file →
  /debug →
  /transform @to:chain-of-thought →
  /meta @domain:DEBUG →
  /rmp @quality:0.85
] "fix: users can't reset password"
```

### Workflow 6.2: Code Review Pipeline

```bash
/chain [
  /context @mode:extract →
  /transform @mode:analyze →
  /meta @template:{context:reviewer}+{mode:multi} →
  /review @domain:SECURITY || /review @domain:PERFORMANCE
] "review PR #123"
```

### Workflow 6.3: Feature Implementation Pipeline

```bash
/chain [
  /context @mode:extract @focus:all →
  /transform @to:tree-of-thought →
  /meta @tier:L5 →
  /rmp @quality:0.9 @max_iterations:5
] "implement OAuth2 authentication"
```

### Workflow 6.4: Documentation Pipeline

```bash
/chain [
  /context @mode:extend @transform:analyze →
  /transform @to:chain-of-thought →
  /meta @template:{context:teacher}+{format:structured} →
  /rmp @quality:0.85
] "document the API"
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CATEGORICAL PROMPT PATTERNS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  SIMPLE TASKS                                                                │
│  ─────────────                                                               │
│  /meta "task"                          Basic transformation                  │
│  /meta @tier:L3 "task"                 Complexity-scaled                     │
│  /meta @domain:X "task"                Domain-focused                        │
│                                                                              │
│  QUALITY-CRITICAL                                                            │
│  ────────────────                                                            │
│  /rmp @quality:0.85 "task"             Iterate until quality                 │
│  /chain [/meta → /rmp] "task"          Generate then refine                  │
│                                                                              │
│  CONTEXT-AWARE                                                               │
│  ─────────────                                                               │
│  /context @mode:extract → /meta        Context first                         │
│  /context @mode:duplicate              Debug prompt issues                   │
│                                                                              │
│  STRATEGY OPTIMIZATION                                                       │
│  ────────────────────                                                        │
│  /transform @to:chain-of-thought       Add reasoning                         │
│  /transform @mode:analyze              Find best strategy                    │
│  /transform @from:X @to:Y              Explicit switch                       │
│                                                                              │
│  FULL PIPELINES                                                              │
│  ─────────────                                                               │
│  /chain [W→α→F→M] "complex task"       Complete workflow                     │
│  /chain [F || F || F] "explore"        Parallel exploration                  │
│  /chain [F → M → F] "iterate"          Multi-stage refinement                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Document Version**: 1.0
**Last Updated**: 2025-12-01
**Examples Validated**: In progress
**Next**: Add these to prompt registry with quality scores
