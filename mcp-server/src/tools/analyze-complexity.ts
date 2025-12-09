/**
 * analyze_complexity MCP tool
 *
 * Uses categorical complexity schema to classify tasks into tiers L1-L7
 */

import { createComplexitySchema } from '../schemas/index.js';

export interface ComplexityInput {
  task: string;
}

export interface ComplexityOutput {
  score: number; // 0.0-1.0
  tier: string; // L1-L7
  strategy: string;
  reasoning: string;
  suggested_iterations: number;
  estimated_tokens: number;
}

/**
 * Complexity indicators (features for scoring)
 */
function detectComplexityIndicators(task: string): Record<string, boolean> {
  const lower = task.toLowerCase();

  return {
    multi_component: /\b(and|plus|with|including|multiple)\b/i.test(task),
    architecture: /\b(design|architect|system|platform|infrastructure)\b/i.test(
      task
    ),
    fault_tolerance: /\b(self-healing|resilient|fault|recovery|ha|high.?availability)\b/i.test(
      task
    ),
    distributed: /\b(distributed|cluster|microservices|orchestrat)\b/i.test(task),
    observability: /\b(monitoring|observability|metrics|alerts|logging)\b/i.test(
      task
    ),
    security: /\b(security|auth|encryption|tls|rbac)\b/i.test(task),
    data_pipeline: /\b(pipeline|etl|stream|batch|data.?processing)\b/i.test(task),
    scale: /\b(scale|scalable|scaling|performance|throughput)\b/i.test(task),
    complexity_words: /\b(complex|complicated|sophisticated|advanced)\b/i.test(
      task
    ),
    implementation: /\b(implement|build|create|develop)\b/i.test(task),
  };
}

/**
 * Score complexity based on indicators
 */
function scoreComplexity(indicators: Record<string, boolean>): number {
  const weights = {
    multi_component: 0.1,
    architecture: 0.15,
    fault_tolerance: 0.12,
    distributed: 0.13,
    observability: 0.08,
    security: 0.08,
    data_pipeline: 0.1,
    scale: 0.09,
    complexity_words: 0.08,
    implementation: 0.07,
  };

  let score = 0;
  for (const [key, value] of Object.entries(indicators)) {
    if (value && key in weights) {
      score += weights[key as keyof typeof weights];
    }
  }

  return Math.min(score, 1.0);
}

/**
 * Map score to tier (L1-L7)
 */
function mapScoreToTier(score: number): string {
  if (score < 0.15) return 'L1';
  if (score < 0.3) return 'L2';
  if (score < 0.45) return 'L3';
  if (score < 0.6) return 'L4';
  if (score < 0.75) return 'L5';
  if (score < 0.9) return 'L6';
  return 'L7';
}

/**
 * Map tier to strategy
 */
function mapTierToStrategy(tier: string): string {
  const strategies: Record<string, string> = {
    L1: 'DIRECT',
    L2: 'DIRECT',
    L3: 'MULTI_APPROACH',
    L4: 'MULTI_APPROACH',
    L5: 'AUTONOMOUS_EVOLUTION',
    L6: 'AUTONOMOUS_EVOLUTION',
    L7: 'AUTONOMOUS_EVOLUTION',
  };

  return strategies[tier] || 'DIRECT';
}

/**
 * Estimate iterations based on tier
 */
function estimateIterations(tier: string): number {
  const iterations: Record<string, number> = {
    L1: 1,
    L2: 1,
    L3: 2,
    L4: 3,
    L5: 3,
    L6: 4,
    L7: 5,
  };

  return iterations[tier] || 1;
}

/**
 * Estimate token budget based on tier
 */
function estimateTokens(tier: string): number {
  const tokens: Record<string, number> = {
    L1: 900,
    L2: 2250,
    L3: 3500,
    L4: 4500,
    L5: 7250,
    L6: 10000,
    L7: 17000,
  };

  return tokens[tier] || 1000;
}

/**
 * Generate reasoning explanation
 */
function generateReasoning(indicators: Record<string, boolean>): string {
  const active = Object.entries(indicators)
    .filter(([_, value]) => value)
    .map(([key, _]) => key.replace(/_/g, ' '));

  if (active.length === 0) {
    return 'Simple task with no complexity indicators';
  }

  return `Detected indicators: ${active.join(', ')}`;
}

/**
 * Main analyze_complexity function
 */
export async function analyzeComplexity(
  input: ComplexityInput
): Promise<ComplexityOutput> {
  const schema = createComplexitySchema();

  // Δ: Task → Indicators (detect patterns)
  const indicators = detectComplexityIndicators(input.task);

  // Σ: Indicators → Score (aggregate via weighted sum)
  const score = scoreComplexity(indicators);

  // Functor: Score → Tier (classify)
  const tier = mapScoreToTier(score);

  // Functor: Tier → Strategy (select)
  const strategy = mapTierToStrategy(tier);

  return {
    score,
    tier,
    strategy,
    reasoning: generateReasoning(indicators),
    suggested_iterations: estimateIterations(tier),
    estimated_tokens: estimateTokens(tier),
  };
}
