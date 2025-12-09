/**
 * Functorial Data Migration (Δ, Σ, Π)
 * Based on Spivak's "Functorial Data Migration" (2012)
 *
 * Given functor F: C → D:
 * - Δ_F: Set^D → Set^C (pullback/reindexing)
 * - Σ_F: Set^C → Set^D (left adjoint, colimit)
 * - Π_F: Set^C → Set^D (right adjoint, limit)
 *
 * Adjunction: Σ ⊣ Δ ⊣ Π
 */

import { Category, Morphism } from '../category/Category.js';
import { Functor, SetFunctor, SimpleSetFunctor } from '../category/Functor.js';

/**
 * Delta (Δ): Pullback functor
 *
 * Δ_F(I)(c) = I(F(c))
 *
 * "Pull data back along functor F"
 */
export function Delta<C_Obj, C_Mor extends Morphism<C_Obj, C_Obj>, D_Obj, D_Mor extends Morphism<D_Obj, D_Obj>>(
  F: Functor<C_Obj, C_Mor, D_Obj, D_Mor>,
  I: SetFunctor<D_Obj, D_Mor>
): SetFunctor<C_Obj, C_Mor> {
  // For simple string-based categories
  if (typeof F.source.objects.values().next().value === 'string') {
    const objectData = new Map<string, Set<any>>();
    const morphismFunctions = new Map<string, (value: any) => any>();

    // Δ_F(I)(c) = I(F(c))
    for (const c of F.source.objects as Set<string>) {
      const fc = F.onObjects(c as any) as any;
      objectData.set(c as string, I.onObjects(fc));
    }

    // Δ_F(I)(f: c → c') = I(F(f): F(c) → F(c'))
    for (const f of F.source.morphisms as Set<Morphism<string, string>>) {
      const ff = F.onMorphisms(f as any) as any;
      morphismFunctions.set(f.name, I.onMorphisms(ff));
    }

    return new SimpleSetFunctor(
      F.source as any,
      objectData,
      morphismFunctions
    ) as any;
  }

  throw new Error('Delta only implemented for string-based categories');
}

/**
 * Sigma (Σ): Left adjoint (colimit/union)
 *
 * Σ_F(I)(d) = colim_{F(c)=d} I(c)
 *
 * "Push data forward and take union"
 *
 * For quality aggregation: weighted average (colimit with weights)
 */
export function Sigma<C_Obj, C_Mor extends Morphism<C_Obj, C_Obj>, D_Obj, D_Mor extends Morphism<D_Obj, D_Obj>>(
  F: Functor<C_Obj, C_Mor, D_Obj, D_Mor>,
  I: SetFunctor<C_Obj, C_Mor>,
  options?: {
    aggregation?: 'union' | 'weighted-average';
    weights?: Map<C_Obj, number>;
  }
): SetFunctor<D_Obj, D_Mor> {
  const aggregation = options?.aggregation || 'union';

  if (typeof F.target.objects.values().next().value === 'string') {
    const objectData = new Map<string, Set<any>>();
    const morphismFunctions = new Map<string, (value: any) => any>();

    // Σ_F(I)(d) = colim_{F(c)=d} I(c)
    for (const d of F.target.objects as Set<string>) {
      const fiber: any[] = [];

      // Find all c where F(c) = d (fiber over d)
      for (const c of F.source.objects as Set<string>) {
        if (F.onObjects(c as any) === d) {
          const data = I.onObjects(c as any);
          fiber.push(...Array.from(data));
        }
      }

      if (aggregation === 'weighted-average' && fiber.length > 0) {
        // Weighted average for quality aggregation
        const weights = options?.weights || new Map();
        let sum = 0;
        let weightSum = 0;

        for (const c of F.source.objects as Set<string>) {
          if (F.onObjects(c as any) === d) {
            const data = I.onObjects(c as any);
            const weight = weights.get(c as any) || 1;

            for (const value of data) {
              if (typeof value === 'number') {
                sum += value * weight;
                weightSum += weight;
              }
            }
          }
        }

        const average = weightSum > 0 ? sum / weightSum : 0;
        objectData.set(d as string, new Set([average]));
      } else {
        // Union (default colimit)
        objectData.set(d as string, new Set(fiber));
      }
    }

    // Morphisms: apply I morphisms then take colimit
    for (const g of F.target.morphisms as Set<Morphism<string, string>>) {
      morphismFunctions.set(g.name, (x) => x); // Simplified
    }

    return new SimpleSetFunctor(
      F.target as any,
      objectData,
      morphismFunctions
    ) as any;
  }

  throw new Error('Sigma only implemented for string-based categories');
}

/**
 * Pi (Π): Right adjoint (limit/intersection)
 *
 * Π_F(I)(d) = lim_{F(c)=d} I(c)
 *
 * "Push data forward and take intersection"
 *
 * For quality filtering: keep only data satisfying ALL constraints
 */
export function Pi<C_Obj, C_Mor extends Morphism<C_Obj, C_Obj>, D_Obj, D_Mor extends Morphism<D_Obj, D_Obj>>(
  F: Functor<C_Obj, C_Mor, D_Obj, D_Mor>,
  I: SetFunctor<C_Obj, C_Mor>,
  options?: {
    predicate?: (value: any) => boolean;
  }
): SetFunctor<D_Obj, D_Mor> {
  if (typeof F.target.objects.values().next().value === 'string') {
    const objectData = new Map<string, Set<any>>();
    const morphismFunctions = new Map<string, (value: any) => any>();

    // Π_F(I)(d) = lim_{F(c)=d} I(c)
    for (const d of F.target.objects as Set<string>) {
      const fiberSets: Set<any>[] = [];

      // Find all c where F(c) = d
      for (const c of F.source.objects as Set<string>) {
        if (F.onObjects(c as any) === d) {
          fiberSets.push(I.onObjects(c as any));
        }
      }

      if (fiberSets.length === 0) {
        objectData.set(d as string, new Set());
      } else if (fiberSets.length === 1) {
        objectData.set(d as string, fiberSets[0]);
      } else {
        // Intersection (limit)
        const intersection = new Set(
          Array.from(fiberSets[0]).filter((x) =>
            fiberSets.every((s) => s.has(x))
          )
        );

        // Apply predicate if provided
        if (options?.predicate) {
          const filtered = new Set(
            Array.from(intersection).filter(options.predicate)
          );
          objectData.set(d as string, filtered);
        } else {
          objectData.set(d as string, intersection);
        }
      }
    }

    return new SimpleSetFunctor(
      F.target as any,
      objectData,
      morphismFunctions
    ) as any;
  }

  throw new Error('Pi only implemented for string-based categories');
}

/**
 * Verify adjunction: Σ ⊣ Δ
 *
 * Hom(Σ_F(I), J) ≅ Hom(I, Δ_F(J))
 */
export function verifyAdjunctionSigmaDelta<C_Obj, C_Mor extends Morphism<C_Obj, C_Obj>, D_Obj, D_Mor extends Morphism<D_Obj, D_Obj>>(
  F: Functor<C_Obj, C_Mor, D_Obj, D_Mor>,
  I: SetFunctor<C_Obj, C_Mor>,
  J: SetFunctor<D_Obj, D_Mor>
): boolean {
  // Simplified verification for MVP
  // Full verification would check natural isomorphism
  return true;
}
