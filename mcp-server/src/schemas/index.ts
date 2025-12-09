/**
 * Domain schemas for meta-prompting
 */

import { SimpleCategory, Morphism } from '../category/Category.js';

/**
 * Complexity Schema: Task → Complexity analysis
 */
export function createComplexitySchema(): SimpleCategory {
  const objects = new Set(['Task', 'Indicators', 'Score', 'Tier', 'Strategy']);
  const morphisms = new Set<Morphism<string, string>>([
    { source: 'Task', target: 'Indicators', name: 'detect' },
    { source: 'Indicators', target: 'Score', name: 'score' },
    { source: 'Score', target: 'Tier', name: 'classify' },
    { source: 'Tier', target: 'Strategy', name: 'select' },
  ]);

  return new SimpleCategory(objects, morphisms);
}

/**
 * Quality Schema: Multiple dimensions → Aggregate
 */
export function createQualitySchema(): SimpleCategory {
  const objects = new Set([
    'Correctness',
    'Clarity',
    'Completeness',
    'Efficiency',
    'Aggregate',
  ]);
  const morphisms = new Set<Morphism<string, string>>([
    { source: 'Correctness', target: 'Aggregate', name: 'weight_correctness' },
    { source: 'Clarity', target: 'Aggregate', name: 'weight_clarity' },
    { source: 'Completeness', target: 'Aggregate', name: 'weight_completeness' },
    { source: 'Efficiency', target: 'Aggregate', name: 'weight_efficiency' },
  ]);

  return new SimpleCategory(objects, morphisms);
}

/**
 * Prompt Schema: Task → Output via transformations
 */
export function createPromptSchema(): SimpleCategory {
  const objects = new Set(['Task', 'Context', 'Mode', 'Format', 'Output']);
  const morphisms = new Set<Morphism<string, string>>([
    { source: 'Task', target: 'Context', name: 'analyze' },
    { source: 'Context', target: 'Mode', name: 'select_strategy' },
    { source: 'Mode', target: 'Format', name: 'apply_template' },
    { source: 'Format', target: 'Output', name: 'generate' },
  ]);

  return new SimpleCategory(objects, morphisms);
}
