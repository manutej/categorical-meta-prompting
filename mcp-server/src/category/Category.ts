/**
 * Core category theory abstractions based on Spivak's categorical databases
 *
 * A category C consists of:
 * - Objects: collection of types
 * - Morphisms: arrows between objects with composition
 * - Identity: each object has an identity morphism
 *
 * Laws:
 * - Identity: f ∘ id_A = f = id_B ∘ f
 * - Associativity: (h ∘ g) ∘ f = h ∘ (g ∘ f)
 */

export interface Morphism<A, B> {
  source: A;
  target: B;
  name: string;
}

export interface Category<Obj, Mor extends Morphism<Obj, Obj>> {
  objects: Set<Obj>;
  morphisms: Set<Mor>;

  /**
   * Compose two morphisms: g ∘ f
   * Requires: f.target === g.source
   */
  compose(f: Mor, g: Mor): Mor;

  /**
   * Identity morphism for an object
   */
  identity(obj: Obj): Mor;

  /**
   * Verify category laws (for testing)
   */
  verifyCategoryLaws?(): boolean;
}

/**
 * Simple category implementation with string objects and named morphisms
 */
export class SimpleCategory implements Category<string, Morphism<string, string>> {
  constructor(
    public objects: Set<string>,
    public morphisms: Set<Morphism<string, string>>
  ) {}

  compose(
    f: Morphism<string, string>,
    g: Morphism<string, string>
  ): Morphism<string, string> {
    if (f.target !== g.source) {
      throw new Error(
        `Cannot compose: f.target (${f.target}) ≠ g.source (${g.source})`
      );
    }

    // Check if composition already exists
    const composedName = `${g.name}∘${f.name}`;
    const existing = Array.from(this.morphisms).find(
      (m) => m.name === composedName && m.source === f.source && m.target === g.target
    );

    if (existing) {
      return existing;
    }

    // Create new composed morphism
    const composed: Morphism<string, string> = {
      source: f.source,
      target: g.target,
      name: composedName,
    };

    this.morphisms.add(composed);
    return composed;
  }

  identity(obj: string): Morphism<string, string> {
    if (!this.objects.has(obj)) {
      throw new Error(`Object ${obj} not in category`);
    }

    const idName = `id_${obj}`;
    const existing = Array.from(this.morphisms).find(
      (m) => m.name === idName && m.source === obj && m.target === obj
    );

    if (existing) {
      return existing;
    }

    const id: Morphism<string, string> = {
      source: obj,
      target: obj,
      name: idName,
    };

    this.morphisms.add(id);
    return id;
  }

  /**
   * Verify category laws hold
   */
  verifyCategoryLaws(): boolean {
    // Identity law: f ∘ id_A = f = id_B ∘ f
    for (const f of this.morphisms) {
      const idA = this.identity(f.source);
      const idB = this.identity(f.target);

      const leftCompose = this.compose(idA, f);
      const rightCompose = this.compose(f, idB);

      if (leftCompose.name !== f.name || rightCompose.name !== f.name) {
        console.error(`Identity law failed for morphism ${f.name}`);
        return false;
      }
    }

    // Associativity: (h ∘ g) ∘ f = h ∘ (g ∘ f)
    // (Simplified check - full check would require all composable triples)
    for (const f of this.morphisms) {
      for (const g of this.morphisms) {
        if (f.target !== g.source) continue;

        for (const h of this.morphisms) {
          if (g.target !== h.source) continue;

          const left = this.compose(this.compose(f, g), h);
          const right = this.compose(f, this.compose(g, h));

          if (left.source !== right.source || left.target !== right.target) {
            console.error(`Associativity failed for ${f.name}, ${g.name}, ${h.name}`);
            return false;
          }
        }
      }
    }

    return true;
  }
}

/**
 * Helper: Create a discrete category (only identity morphisms)
 */
export function discreteCategory(objects: string[]): SimpleCategory {
  const objSet = new Set(objects);
  const morSet = new Set<Morphism<string, string>>();

  // Add identity morphisms
  for (const obj of objects) {
    morSet.add({
      source: obj,
      target: obj,
      name: `id_${obj}`,
    });
  }

  return new SimpleCategory(objSet, morSet);
}
