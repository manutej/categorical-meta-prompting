---
name: prompt-benchmark
description: Systematic prompt evaluation framework with MATH, GSM8K, and Game of 24 benchmarks. Use when evaluating prompt effectiveness on standard benchmarks, comparing meta-prompting strategies quantitatively, measuring prompt quality improvements, or validating categorical prompt optimizations against ground truth datasets.
---

# Prompt Benchmark Framework

Systematic evaluation of prompts against standard AI benchmarks.

## Core Benchmarks

| Benchmark | Domain | Metric | Baseline | Meta-Prompt Target |
|-----------|--------|--------|----------|-------------------|
| MATH | Mathematics | Accuracy | ~50% | ≥70% |
| GSM8K | Grade School Math | Accuracy | ~80% | ≥90% |
| Game of 24 | Arithmetic Reasoning | Success Rate | ~30% | ≥90% |
| HumanEval | Code Generation | pass@1 | ~67% | ≥80% |
| MMLU | Knowledge | Accuracy | ~70% | ≥80% |

## Benchmark Implementation

### Game of 24

```typescript
import * as E from 'fp-ts/Either';
import * as A from 'fp-ts/Array';
import * as O from 'fp-ts/Option';
import { pipe, flow } from 'fp-ts/function';

interface Game24Problem {
  numbers: [number, number, number, number];
  target: 24;
}

interface Game24Result {
  problem: Game24Problem;
  expression: string;
  evaluation: number;
  correct: boolean;
  reasoning?: string;
}

// Verify solution
const evaluateExpression = (expr: string): E.Either<string, number> => {
  try {
    // Safe eval with only arithmetic operators
    const sanitized = expr.replace(/[^0-9+\-*/().]/g, '');
    const result = Function(`"use strict"; return (${sanitized})`)();
    return E.right(result);
  } catch (e) {
    return E.left(`Invalid expression: ${expr}`);
  }
};

const verifyGame24 = (
  problem: Game24Problem,
  expression: string
): E.Either<string, Game24Result> => {
  return pipe(
    evaluateExpression(expression),
    E.chain(result => {
      const correct = Math.abs(result - 24) < 0.0001;
      
      // Verify all numbers used exactly once
      const usedNumbers = expression.match(/\d+/g)?.map(Number) ?? [];
      const numbersMatch = pipe(
        usedNumbers,
        A.sort((a, b) => a - b),
        sorted => JSON.stringify(sorted) === JSON.stringify([...problem.numbers].sort((a, b) => a - b))
      );
      
      if (!numbersMatch) {
        return E.left('Must use each number exactly once');
      }
      
      return E.right({
        problem,
        expression,
        evaluation: result,
        correct
      });
    })
  );
};

// Sample problems
const game24Problems: Game24Problem[] = [
  { numbers: [1, 2, 3, 4], target: 24 },
  { numbers: [2, 3, 4, 5], target: 24 },
  { numbers: [1, 5, 5, 5], target: 24 },
  { numbers: [3, 3, 8, 8], target: 24 },
  { numbers: [1, 2, 7, 7], target: 24 }
];
```

### GSM8K Evaluation

```typescript
interface GSM8KProblem {
  question: string;
  answer: number;
  reasoning?: string;
}

interface GSM8KResult {
  problem: GSM8KProblem;
  predicted: number;
  correct: boolean;
  extractedReasoning?: string;
}

// Extract final number from response
const extractAnswer = (response: string): O.Option<number> => {
  // Look for patterns like "#### 42" or "The answer is 42"
  const patterns = [
    /####\s*(\d+(?:\.\d+)?)/,
    /answer\s*(?:is|=|:)\s*(\d+(?:\.\d+)?)/i,
    /(\d+(?:\.\d+)?)\s*(?:dollars?|items?|people|units?)?\s*$/
  ];
  
  for (const pattern of patterns) {
    const match = response.match(pattern);
    if (match) {
      return O.some(parseFloat(match[1]));
    }
  }
  
  return O.none;
};

const evaluateGSM8K = (
  problem: GSM8KProblem,
  response: string
): GSM8KResult => {
  const predicted = pipe(
    extractAnswer(response),
    O.getOrElse(() => NaN)
  );
  
  return {
    problem,
    predicted,
    correct: Math.abs(predicted - problem.answer) < 0.01,
    extractedReasoning: response
  };
};
```

### MATH Benchmark

```typescript
interface MATHProblem {
  problem: string;
  level: 1 | 2 | 3 | 4 | 5;
  type: 'algebra' | 'geometry' | 'number_theory' | 'calculus' | 'probability';
  solution: string;
  answer: string; // LaTeX or numeric
}

// Normalize mathematical expressions
const normalizeMathAnswer = (answer: string): string => {
  return answer
    .replace(/\\frac{(\d+)}{(\d+)}/g, (_, n, d) => `${n}/${d}`)
    .replace(/\s+/g, '')
    .toLowerCase();
};

const evaluateMATH = (
  problem: MATHProblem,
  response: string
): { correct: boolean; similarity: number } => {
  const normalizedExpected = normalizeMathAnswer(problem.answer);
  const normalizedResponse = normalizeMathAnswer(response);
  
  const exact = normalizedExpected === normalizedResponse;
  
  // Fuzzy matching for equivalent expressions
  const similarity = exact ? 1.0 : computeSimilarity(normalizedExpected, normalizedResponse);
  
  return { correct: exact || similarity > 0.95, similarity };
};
```

## Benchmark Runner

```typescript
import * as TE from 'fp-ts/TaskEither';
import * as T from 'fp-ts/Task';
import { pipe } from 'fp-ts/function';

interface BenchmarkConfig {
  name: string;
  problems: readonly unknown[];
  evaluator: (problem: unknown, response: string) => { correct: boolean };
  prompt: (problem: unknown) => string;
}

interface BenchmarkResults {
  name: string;
  total: number;
  correct: number;
  accuracy: number;
  perProblem: Array<{
    problem: unknown;
    response: string;
    correct: boolean;
    latencyMs: number;
  }>;
}

const runBenchmark = (
  config: BenchmarkConfig,
  generateFn: (prompt: string) => TE.TaskEither<Error, string>
): T.Task<BenchmarkResults> => {
  return async () => {
    const results: BenchmarkResults['perProblem'] = [];
    
    for (const problem of config.problems) {
      const prompt = config.prompt(problem);
      const start = Date.now();
      
      const response = await pipe(
        generateFn(prompt),
        TE.getOrElse(() => T.of('ERROR'))
      )();
      
      const latencyMs = Date.now() - start;
      const { correct } = config.evaluator(problem, response);
      
      results.push({ problem, response, correct, latencyMs });
    }
    
    const correct = results.filter(r => r.correct).length;
    
    return {
      name: config.name,
      total: config.problems.length,
      correct,
      accuracy: correct / config.problems.length,
      perProblem: results
    };
  };
};
```

## Prompt Strategies

### Chain-of-Thought Prompt

```typescript
const cotPrompt = (problem: Game24Problem): string => `
Use the numbers ${problem.numbers.join(', ')} to make 24.
Each number must be used exactly once.
You can use +, -, *, / and parentheses.

Let's think step by step:
1. First, consider what operations might give us factors of 24
2. Try different combinations systematically
3. Verify the solution uses each number once

After reasoning, provide your answer in the format:
SOLUTION: <expression>
`;
```

### Tree-of-Thought Prompt

```typescript
const totPrompt = (problem: Game24Problem): string => `
Use ${problem.numbers.join(', ')} to make 24.

Explore multiple reasoning paths:

PATH A: Try multiplication first
- What pairs multiply to give factors of 24?

PATH B: Try addition/subtraction first  
- Can we make numbers that combine to 24?

PATH C: Look for special patterns
- Are there any numbers that divide evenly?

Evaluate each path and select the most promising.

SOLUTION: <expression>
`;
```

### Meta-Prompt for Game of 24

```typescript
const metaPromptGame24 = (problem: Game24Problem): string => `
<task>
Solve Game of 24: Use ${problem.numbers.join(', ')} to make exactly 24.
Rules: Use each number exactly once. Use +, -, *, / and parentheses.
</task>

<strategy>
1. ANALYZE: Identify useful number relationships
2. ENUMERATE: List candidate expressions systematically  
3. VERIFY: Check each candidate
4. REFINE: If no solution, reconsider assumptions
</strategy>

<quality_threshold>
Only output a solution after verifying it equals 24.
</quality_threshold>

<output_format>
REASONING: <step-by-step thought process>
VERIFICATION: <show the calculation equals 24>
SOLUTION: <final expression>
</output_format>
`;
```

## Comparative Analysis

```typescript
interface PromptComparison {
  promptName: string;
  results: BenchmarkResults;
}

const comparePrompts = async (
  prompts: Array<{ name: string; template: (p: unknown) => string }>,
  benchmark: BenchmarkConfig,
  generateFn: (prompt: string) => TE.TaskEither<Error, string>
): Promise<PromptComparison[]> => {
  const comparisons: PromptComparison[] = [];
  
  for (const { name, template } of prompts) {
    const config = { ...benchmark, prompt: template };
    const results = await runBenchmark(config, generateFn)();
    comparisons.push({ promptName: name, results });
  }
  
  return comparisons.sort((a, b) => b.results.accuracy - a.results.accuracy);
};

// Usage
const comparison = await comparePrompts(
  [
    { name: 'baseline', template: baselinePrompt },
    { name: 'cot', template: cotPrompt },
    { name: 'tot', template: totPrompt },
    { name: 'meta', template: metaPromptGame24 }
  ],
  game24Benchmark,
  openaiGenerate
);

console.table(comparison.map(c => ({
  prompt: c.promptName,
  accuracy: `${(c.results.accuracy * 100).toFixed(1)}%`,
  correct: `${c.results.correct}/${c.results.total}`
})));
```

## Statistical Analysis

```typescript
import * as A from 'fp-ts/Array';
import * as N from 'fp-ts/number';

interface StatisticalSummary {
  mean: number;
  stdDev: number;
  ci95: [number, number];
  min: number;
  max: number;
}

const computeStats = (accuracies: number[]): StatisticalSummary => {
  const n = accuracies.length;
  const mean = A.reduce(0, (acc, x: number) => acc + x)(accuracies) / n;
  
  const variance = accuracies.reduce(
    (acc, x) => acc + Math.pow(x - mean, 2), 0
  ) / (n - 1);
  
  const stdDev = Math.sqrt(variance);
  const stderr = stdDev / Math.sqrt(n);
  const ci95: [number, number] = [mean - 1.96 * stderr, mean + 1.96 * stderr];
  
  return {
    mean,
    stdDev,
    ci95,
    min: Math.min(...accuracies),
    max: Math.max(...accuracies)
  };
};

// Bootstrap confidence interval
const bootstrapCI = (
  results: boolean[],
  nBootstrap: number = 1000
): [number, number] => {
  const accuracies: number[] = [];
  
  for (let i = 0; i < nBootstrap; i++) {
    const sample = A.map(() => results[Math.floor(Math.random() * results.length)])(
      Array(results.length).fill(null)
    );
    const acc = sample.filter(Boolean).length / sample.length;
    accuracies.push(acc);
  }
  
  accuracies.sort((a, b) => a - b);
  return [accuracies[Math.floor(0.025 * nBootstrap)], accuracies[Math.floor(0.975 * nBootstrap)]];
};
```

## Categorical Guarantees

The benchmark framework ensures:

1. **Reproducibility**: Fixed problems with deterministic evaluation
2. **Comparability**: Same metrics across prompt strategies
3. **Statistical Rigor**: Confidence intervals for accuracy claims
4. **Type Safety**: Typed problem/result structures with fp-ts
5. **Composability**: Benchmarks compose for meta-analysis
