---
description: Domain-aware code review with automatic focus selection based on code type
allowed-tools: Read, Grep, Glob, Bash(git diff:*), Bash(git show:*)
argument-hint: [file-or-focus]
---

# Domain-Aware Code Review

## Target
$ARGUMENTS

## Step 1: Identify Code Domain

Read the target file(s) and classify the code:

| Domain | Indicators | Review Focus |
|--------|-----------|--------------|
| **Algorithm** | Loops, recursion, data structures, sorting/searching | Time/space complexity, edge cases, correctness |
| **API/Network** | HTTP, requests, endpoints, REST, GraphQL | Error handling, rate limiting, auth, validation |
| **Security** | Auth, crypto, passwords, tokens, user input | OWASP top 10, injection, data exposure |
| **Data** | SQL, ORM, database, queries, transactions | N+1, indexes, consistency, migrations |
| **UI/Frontend** | React, components, DOM, CSS, events | Accessibility, performance, state management |
| **Infrastructure** | Docker, K8s, CI/CD, configs, scripts | Security, idempotency, failure modes |

## Step 2: Apply Domain-Specific Review

Based on the detected domain, focus your review:

### For Algorithm Code:
1. **Correctness**: Does it solve the problem for all inputs?
2. **Complexity**: What's the Big-O? Can it be improved?
3. **Edge cases**: Empty, single, max-size inputs handled?
4. **Readability**: Are variable names and logic clear?

### For API/Network Code:
1. **Error handling**: What happens on timeout, 4xx, 5xx?
2. **Validation**: Is input validated before processing?
3. **Authentication**: Are endpoints properly protected?
4. **Rate limiting**: Is there protection against abuse?

### For Security-Sensitive Code:
1. **Input validation**: Is all user input sanitized?
2. **Injection risks**: SQL, command, XSS, template injection?
3. **Secrets**: Are credentials hardcoded or properly managed?
4. **Auth/authz**: Is access control properly enforced?

### For Data/Database Code:
1. **N+1 queries**: Are there loop-based queries?
2. **Transactions**: Are related operations atomic?
3. **Indexes**: Are queries using appropriate indexes?
4. **Migrations**: Are schema changes backward compatible?

## Step 3: Provide Structured Feedback

Format your review as:

```
## Summary
[1-2 sentence overview]

## Domain: [Detected Domain]

## Critical Issues (must fix)
- [ ] Issue 1: Description + suggestion

## Improvements (should fix)
- [ ] Issue 2: Description + suggestion

## Nitpicks (optional)
- [ ] Issue 3: Description + suggestion

## What's Good
- Positive observation 1
- Positive observation 2
```
