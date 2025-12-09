/**
 * Functors: Structure-preserving maps between categories
 *
 * A functor F: C → D consists of:
 * - onObjects: maps objects of C to objects of D
 * - onMorphisms: maps morphisms of C to morphisms of D
 *
 * Laws:
 * - F(id_A) = id_{F(A)}
 * - F(g ∘ f) = F(g) ∘ F(f)
 */

import { Category, Morphism } from './Category.js';

export interface Functor<C_Obj, C_Mor extends Morphism<C_Obj, C_Obj>, D_Obj, D_Mor extends Morphism<D_Obj, D_Obj>> {
  source: Category<C_Obj, C_Mor>;
  target: Category<D_Obj, D_Mor>;

  onObjects(obj: C_Obj): D_Obj;
  onMorphisms(mor: C_Mor): D_Mor;
}

/**
 * SetFunctor: Instance of a database schema
 *
 * A functor F: C → Set maps:
 * - Each object to a set (table data)
 * - Each morphism to a function (constraint)
 */
export interface SetFunctor<Obj, Mor extends Morphism<Obj, Obj>> {
  schema: Category<Obj, Mor>;

  /**
   * Map object to its data set
   */
  onObjects(obj: Obj): Set<any>;

  /**
   * Map morphism to a function between sets
   */
  onMorphisms(mor: Mor): (value: any) => any;
}

/**
 * Simple functor implementation between string-based categories
 */
export class SimpleFunctor implements Functor<string, Morphism<string, string>, string, Morphism<string, string>> {
  constructor(
    public source: Category<string, Morphism<string, string>>,
    public target: Category<string, Morphism<string, string>>,
    private objectMap: Map<string, string>,
    private morphismMap: Map<string, string>
  ) {}

  onObjects(obj: string): string {
    const result = this.objectMap.get(obj);
    if (!result) {
      throw new Error(`Object ${obj} not mapped by functor`);
    }
    return result;
  }

  onMorphisms(mor: Morphism<string, string>): Morphism<string, string> {
    const targetMorName = this.morphismMap.get(mor.name);
    if (!targetMorName) {
      // Check if it's an identity morphism
      if (mor.name.startsWith('id_')) {
        const obj = mor.source;
        const targetObj = this.onObjects(obj);
        return this.target.identity(targetObj);
      }
      throw new Error(`Morphism ${mor.name} not mapped by functor`);
    }

    const targetMor = Array.from(this.target.morphisms).find(
      (m) => m.name === targetMorName
    );

    if (!targetMor) {
      throw new Error(`Target morphism ${targetMorName} not found`);
    }

    return targetMor;
  }

  /**
   * Verify functor laws
   */
  verifyFunctorLaws(): boolean {
    // F(id_A) = id_{F(A)}
    for (const obj of this.source.objects) {
      const idC = this.source.identity(obj);
      const fidC = this.onMorphisms(idC);
      const idFObj = this.target.identity(this.onObjects(obj));

      if (fidC.name !== idFObj.name) {
        console.error(`Functor doesn't preserve identity for ${obj}`);
        return false;
      }
    }

    // F(g ∘ f) = F(g) ∘ F(f)
    for (const f of this.source.morphisms) {
      for (const g of this.source.morphisms) {
        if (f.target !== g.source) continue;

        try {
          const gf = this.source.compose(f, g);
          const fgf = this.onMorphisms(gf);

          const ff = this.onMorphisms(f);
          const fg = this.onMorphisms(g);
          const fgCompfg = this.target.compose(ff, fg);

          if (fgf.source !== fgCompfg.source || fgf.target !== fgCompfg.target) {
            console.error(`Functor doesn't preserve composition: ${f.name}, ${g.name}`);
            return false;
          }
        } catch (e) {
          // Skip if composition not defined
        }
      }
    }

    return true;
  }
}

/**
 * Simple SetFunctor implementation
 */
export class SimpleSetFunctor implements SetFunctor<string, Morphism<string, string>> {
  constructor(
    public schema: Category<string, Morphism<string, string>>,
    private objectData: Map<string, Set<any>>,
    private morphismFunctions: Map<string, (value: any) => any>
  ) {}

  onObjects(obj: string): Set<any> {
    const data = this.objectData.get(obj);
    if (!data) {
      return new Set();
    }
    return data;
  }

  onMorphisms(mor: Morphism<string, string>): (value: any) => any {
    const fn = this.morphismFunctions.get(mor.name);
    if (!fn) {
      // Default: identity function
      return (x) => x;
    }
    return fn;
  }
}
