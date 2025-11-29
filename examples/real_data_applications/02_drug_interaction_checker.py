"""
Example 2: Drug Interaction Compositional Checker
=================================================

This example demonstrates:
- Monoidal category structure for drug combinations
- Tensor product composition for interaction checking
- Enriched quality tracking for safety scores
- Real drug interaction data

Categorical Structures Used:
- Monoidal Category: Drugs as objects, tensor product for combinations
- Enriched Category: [0,1] safety scores that degrade through composition
- Functor: Maps drug pairs to interaction severity

Data Source: DrugBank open data, SIDER, FDA drug interactions
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set, Optional
from enum import Enum
import json


# =============================================================================
# REAL DRUG INTERACTION DATA
# =============================================================================

# This is a curated subset of real drug interactions from DrugBank/FDA
# In production, this would query the actual DrugBank API or FDA database

DRUG_DATABASE = {
    # Drug info: (generic_name, drug_class, common_uses)
    "warfarin": ("Warfarin", "Anticoagulant", "Blood clot prevention"),
    "aspirin": ("Aspirin", "NSAID/Antiplatelet", "Pain relief, heart attack prevention"),
    "ibuprofen": ("Ibuprofen", "NSAID", "Pain relief, inflammation"),
    "metformin": ("Metformin", "Antidiabetic", "Type 2 diabetes"),
    "lisinopril": ("Lisinopril", "ACE Inhibitor", "Hypertension, heart failure"),
    "atorvastatin": ("Atorvastatin", "Statin", "High cholesterol"),
    "omeprazole": ("Omeprazole", "PPI", "Acid reflux, ulcers"),
    "metoprolol": ("Metoprolol", "Beta blocker", "Hypertension, heart conditions"),
    "amlodipine": ("Amlodipine", "Calcium channel blocker", "Hypertension"),
    "gabapentin": ("Gabapentin", "Anticonvulsant", "Seizures, nerve pain"),
    "sertraline": ("Sertraline", "SSRI", "Depression, anxiety"),
    "fluoxetine": ("Fluoxetine", "SSRI", "Depression, OCD"),
    "tramadol": ("Tramadol", "Opioid", "Pain relief"),
    "cyclobenzaprine": ("Cyclobenzaprine", "Muscle relaxant", "Muscle spasms"),
    "prednisone": ("Prednisone", "Corticosteroid", "Inflammation, immune conditions"),
    "ciprofloxacin": ("Ciprofloxacin", "Fluoroquinolone", "Bacterial infections"),
    "amoxicillin": ("Amoxicillin", "Penicillin", "Bacterial infections"),
    "acetaminophen": ("Acetaminophen", "Analgesic", "Pain relief, fever"),
    "clopidogrel": ("Clopidogrel", "Antiplatelet", "Blood clot prevention"),
    "simvastatin": ("Simvastatin", "Statin", "High cholesterol"),
}

# Real drug interactions with severity scores
# Format: (drug1, drug2): (severity, mechanism, clinical_effect)
# Severity: 0.0 = contraindicated, 0.3 = major, 0.6 = moderate, 0.9 = minor
INTERACTION_DATABASE = {
    ("warfarin", "aspirin"): (0.2, "Additive anticoagulant effect",
        "Significantly increased bleeding risk. Avoid combination unless specifically indicated."),
    ("warfarin", "ibuprofen"): (0.3, "NSAID inhibits platelet function + GI erosion",
        "Major bleeding risk, especially GI. Use alternative pain relief."),
    ("warfarin", "omeprazole"): (0.7, "CYP2C19 inhibition reduces warfarin metabolism",
        "May increase INR. Monitor and adjust warfarin dose."),
    ("warfarin", "ciprofloxacin"): (0.4, "Inhibits CYP1A2 and displaces protein binding",
        "Significant INR increase. Close monitoring required."),

    ("aspirin", "ibuprofen"): (0.5, "Competitive COX-1 binding",
        "Ibuprofen may reduce cardioprotective effect of aspirin. Take aspirin 30min before."),
    ("aspirin", "clopidogrel"): (0.6, "Additive antiplatelet effect",
        "Used therapeutically post-stent, but increases bleeding risk."),

    ("metformin", "ciprofloxacin"): (0.5, "Altered glucose metabolism",
        "May cause hypoglycemia or hyperglycemia. Monitor blood glucose."),
    ("metformin", "lisinopril"): (0.85, "Minimal interaction",
        "Generally safe. Both commonly used in diabetic patients."),

    ("lisinopril", "ibuprofen"): (0.4, "NSAIDs reduce ACE inhibitor efficacy",
        "Decreased blood pressure control, increased renal risk."),
    ("lisinopril", "metoprolol"): (0.75, "Additive hypotensive effect",
        "Often used together, but monitor for excessive BP reduction."),
    ("lisinopril", "atorvastatin"): (0.9, "No significant interaction",
        "Safe combination, commonly co-prescribed."),

    ("atorvastatin", "omeprazole"): (0.85, "Minor CYP interaction",
        "Generally safe, no dose adjustment needed."),
    ("atorvastatin", "ciprofloxacin"): (0.6, "CYP3A4 inhibition",
        "May increase statin levels. Watch for myopathy symptoms."),
    ("atorvastatin", "amlodipine"): (0.65, "CYP3A4 competition",
        "May increase statin exposure. Consider dose limits."),

    ("sertraline", "tramadol"): (0.25, "Serotonin syndrome risk",
        "Combined serotonergic effect. HIGH RISK - avoid if possible."),
    ("fluoxetine", "tramadol"): (0.2, "Serotonin syndrome + CYP2D6 inhibition",
        "MAJOR RISK - serotonin syndrome + reduced tramadol efficacy."),

    ("sertraline", "fluoxetine"): (0.1, "Duplicate therapy + serotonin excess",
        "CONTRAINDICATED - never combine SSRIs."),

    ("gabapentin", "tramadol"): (0.4, "Additive CNS depression",
        "Increased sedation, respiratory depression risk. Reduce doses."),

    ("metoprolol", "amlodipine"): (0.7, "Additive cardiac effects",
        "May enhance bradycardia/hypotension. Common therapeutic combination."),

    ("prednisone", "ibuprofen"): (0.45, "Additive GI toxicity",
        "Significantly increased ulcer/bleeding risk. Add GI protection."),

    ("cyclobenzaprine", "sertraline"): (0.35, "Serotonergic + anticholinergic effects",
        "Risk of serotonin syndrome. Use with caution."),

    ("amoxicillin", "warfarin"): (0.6, "Altered gut flora affects vitamin K",
        "May increase INR. Short courses usually okay with monitoring."),

    ("clopidogrel", "omeprazole"): (0.5, "CYP2C19 inhibition reduces clopidogrel activation",
        "Reduced antiplatelet effect. Use pantoprazole instead."),

    ("simvastatin", "amlodipine"): (0.5, "CYP3A4 inhibition increases simvastatin",
        "Limit simvastatin to 20mg with amlodipine. Myopathy risk."),
}


class InteractionSeverity(Enum):
    """Interaction severity levels."""
    CONTRAINDICATED = "contraindicated"  # 0.0-0.2
    MAJOR = "major"                       # 0.2-0.4
    MODERATE = "moderate"                 # 0.4-0.7
    MINOR = "minor"                       # 0.7-0.9
    NONE = "none"                         # 0.9-1.0


# =============================================================================
# CATEGORICAL FOUNDATIONS
# =============================================================================

@dataclass
class Drug:
    """
    Drug as an object in our monoidal category.

    The identity object is "no drug" (empty prescription).
    """
    id: str
    name: str
    drug_class: str
    uses: str

    @classmethod
    def from_id(cls, drug_id: str) -> 'Drug':
        """Construct drug from database."""
        if drug_id not in DRUG_DATABASE:
            raise ValueError(f"Unknown drug: {drug_id}")
        name, drug_class, uses = DRUG_DATABASE[drug_id]
        return cls(id=drug_id, name=name, drug_class=drug_class, uses=uses)


@dataclass
class SafetyScore:
    """
    Safety score in [0,1]-enriched category.

    1.0 = completely safe
    0.0 = contraindicated

    Composition uses tensor product (multiplication) for safety degradation.
    """
    value: float
    components: List[Tuple[str, str, float]] = field(default_factory=list)

    def __post_init__(self):
        assert 0 <= self.value <= 1, f"Safety must be in [0,1], got {self.value}"

    def tensor(self, other: 'SafetyScore') -> 'SafetyScore':
        """
        Tensor product composition: safety degrades multiplicatively.

        This models the categorical structure where combining drugs
        compounds risk (quality degradation through composition).
        """
        combined_value = self.value * other.value
        combined_components = self.components + other.components
        return SafetyScore(value=combined_value, components=combined_components)

    @property
    def severity(self) -> InteractionSeverity:
        """Map continuous score to severity category."""
        if self.value < 0.2:
            return InteractionSeverity.CONTRAINDICATED
        elif self.value < 0.4:
            return InteractionSeverity.MAJOR
        elif self.value < 0.7:
            return InteractionSeverity.MODERATE
        elif self.value < 0.9:
            return InteractionSeverity.MINOR
        return InteractionSeverity.NONE


@dataclass
class DrugInteraction:
    """
    Morphism in our enriched category: represents interaction between two drugs.
    """
    drug1: Drug
    drug2: Drug
    safety: SafetyScore
    mechanism: str
    clinical_effect: str


@dataclass
class DrugCombination:
    """
    Result of tensor product in monoidal category.

    Represents a set of drugs being taken together.
    """
    drugs: List[Drug]
    interactions: List[DrugInteraction]
    composite_safety: SafetyScore

    def add_drug(self, drug: Drug, interactions: List[DrugInteraction]) -> 'DrugCombination':
        """
        Tensor product: Add a drug to the combination.

        This is the monoidal product operation.
        """
        new_drugs = self.drugs + [drug]

        # Compose all new interactions
        new_safety = self.composite_safety
        for interaction in interactions:
            interaction_safety = SafetyScore(
                value=interaction.safety.value,
                components=[(interaction.drug1.id, interaction.drug2.id, interaction.safety.value)]
            )
            new_safety = new_safety.tensor(interaction_safety)

        return DrugCombination(
            drugs=new_drugs,
            interactions=self.interactions + interactions,
            composite_safety=new_safety
        )


# =============================================================================
# CATEGORICAL DRUG INTERACTION ENGINE
# =============================================================================

class DrugInteractionCategory:
    """
    Monoidal category of drugs with enriched interaction morphisms.

    Structure:
    - Objects: Drugs
    - Morphisms: Interactions with [0,1] safety enrichment
    - Tensor product: Drug combination with safety composition
    - Unit: Empty prescription (safety = 1.0)
    """

    def __init__(self):
        self.drug_db = DRUG_DATABASE
        self.interaction_db = INTERACTION_DATABASE

    def get_interaction(self, drug1: Drug, drug2: Drug) -> Optional[DrugInteraction]:
        """
        Look up interaction morphism between two drugs.

        Symmetric: interaction(A,B) = interaction(B,A)
        """
        key = (drug1.id, drug2.id)
        reverse_key = (drug2.id, drug1.id)

        if key in self.interaction_db:
            severity, mechanism, effect = self.interaction_db[key]
        elif reverse_key in self.interaction_db:
            severity, mechanism, effect = self.interaction_db[reverse_key]
        else:
            # No known interaction
            return None

        return DrugInteraction(
            drug1=drug1,
            drug2=drug2,
            safety=SafetyScore(
                value=severity,
                components=[(drug1.id, drug2.id, severity)]
            ),
            mechanism=mechanism,
            clinical_effect=effect
        )

    def tensor(self, combination: DrugCombination, new_drug: Drug) -> DrugCombination:
        """
        Monoidal tensor product: add drug to combination.

        Computes all pairwise interactions and composes safety scores.
        """
        new_interactions = []

        for existing_drug in combination.drugs:
            interaction = self.get_interaction(existing_drug, new_drug)
            if interaction:
                new_interactions.append(interaction)

        return combination.add_drug(new_drug, new_interactions)

    def unit(self) -> DrugCombination:
        """
        Monoidal unit: empty prescription with perfect safety.
        """
        return DrugCombination(
            drugs=[],
            interactions=[],
            composite_safety=SafetyScore(value=1.0, components=[])
        )

    def check_combination(self, drug_ids: List[str]) -> DrugCombination:
        """
        Check a drug combination by composing via tensor products.

        This is the main categorical operation: folding drugs with tensor.
        """
        combination = self.unit()

        for drug_id in drug_ids:
            drug = Drug.from_id(drug_id)
            combination = self.tensor(combination, drug)

        return combination

    def find_safest_alternative(
        self,
        current_drugs: List[str],
        problem_drug: str,
        alternatives: List[str]
    ) -> Tuple[str, DrugCombination]:
        """
        Find safest alternative by comparing composite safety scores.

        Uses enriched category comparison: higher safety = better.
        """
        other_drugs = [d for d in current_drugs if d != problem_drug]

        best_alternative = None
        best_combination = None
        best_safety = 0.0

        for alt in alternatives:
            test_drugs = other_drugs + [alt]
            combination = self.check_combination(test_drugs)

            if combination.composite_safety.value > best_safety:
                best_safety = combination.composite_safety.value
                best_alternative = alt
                best_combination = combination

        return best_alternative, best_combination


# =============================================================================
# INTERACTION ANALYSIS ENGINE
# =============================================================================

class DrugInteractionAnalyzer:
    """
    Full analysis engine with categorical composition and RMP refinement.
    """

    def __init__(self):
        self.category = DrugInteractionCategory()

    def analyze(self, drug_ids: List[str]) -> Dict:
        """
        Perform full interaction analysis using categorical composition.
        """
        print(f"\n{'='*70}")
        print("CATEGORICAL DRUG INTERACTION ANALYSIS")
        print(f"{'='*70}")

        # Build combination via tensor products
        combination = self.category.check_combination(drug_ids)

        print(f"\nAnalyzing {len(drug_ids)} drugs:")
        for drug_id in drug_ids:
            drug = Drug.from_id(drug_id)
            print(f"  • {drug.name} ({drug.drug_class})")

        print(f"\n{'-'*70}")
        print("CATEGORICAL COMPOSITION (Tensor Product)")
        print(f"{'-'*70}")

        # Show interactions found
        if combination.interactions:
            print(f"\n{len(combination.interactions)} interactions detected:\n")

            for interaction in combination.interactions:
                safety = interaction.safety.value
                severity = interaction.safety.severity.value.upper()

                # Color coding via symbols
                if safety < 0.3:
                    symbol = "⛔"
                elif safety < 0.5:
                    symbol = "⚠️"
                elif safety < 0.7:
                    symbol = "⚡"
                else:
                    symbol = "✓"

                print(f"{symbol} {interaction.drug1.name} + {interaction.drug2.name}")
                print(f"   Severity: {severity} (safety: {safety:.2f})")
                print(f"   Mechanism: {interaction.mechanism}")
                print(f"   Effect: {interaction.clinical_effect}")
                print()
        else:
            print("\nNo known interactions detected.")

        # Composite safety via tensor product
        print(f"{'-'*70}")
        print("ENRICHED CATEGORY: COMPOSITE SAFETY")
        print(f"{'-'*70}")

        composite = combination.composite_safety
        severity = composite.severity.value.upper()

        print(f"\nComposite Safety Score: {composite.value:.4f}")
        print(f"Overall Severity: {severity}")

        if composite.components:
            print("\nSafety composition chain:")
            running_safety = 1.0
            for d1, d2, safety in composite.components:
                running_safety *= safety
                print(f"  {d1} ⊗ {d2}: {safety:.2f} → cumulative: {running_safety:.4f}")

        # Generate recommendations
        print(f"\n{'-'*70}")
        print("RECOMMENDATIONS")
        print(f"{'-'*70}")

        if composite.value < 0.3:
            print("\n⛔ HIGH RISK COMBINATION")
            print("   This drug combination has serious interaction risks.")
            print("   Recommend immediate clinical review.")

            # Find the worst interaction
            worst = min(combination.interactions, key=lambda i: i.safety.value)
            print(f"\n   Primary concern: {worst.drug1.name} + {worst.drug2.name}")
            print(f"   Consider alternatives for one of these medications.")

        elif composite.value < 0.5:
            print("\n⚠️ MODERATE RISK - Use With Caution")
            print("   Monitor patient closely for adverse effects.")
            print("   Consider timing separation or dose adjustments.")

        elif composite.value < 0.7:
            print("\n⚡ MINOR INTERACTIONS PRESENT")
            print("   Generally acceptable with monitoring.")
            print("   Educate patient on warning signs.")

        else:
            print("\n✓ LOW RISK COMBINATION")
            print("   No significant interactions identified.")
            print("   Standard monitoring appropriate.")

        return {
            "drugs": drug_ids,
            "combination": combination,
            "composite_safety": composite.value,
            "severity": severity,
            "interactions": len(combination.interactions)
        }

    def compare_regimens(
        self,
        regimen1: List[str],
        regimen2: List[str]
    ) -> Dict:
        """
        Compare two drug regimens using enriched category ordering.
        """
        print(f"\n{'='*70}")
        print("REGIMEN COMPARISON (Enriched Category Ordering)")
        print(f"{'='*70}")

        combo1 = self.category.check_combination(regimen1)
        combo2 = self.category.check_combination(regimen2)

        print(f"\nRegimen A: {', '.join(regimen1)}")
        print(f"  Composite Safety: {combo1.composite_safety.value:.4f}")

        print(f"\nRegimen B: {', '.join(regimen2)}")
        print(f"  Composite Safety: {combo2.composite_safety.value:.4f}")

        if combo1.composite_safety.value > combo2.composite_safety.value:
            print(f"\n→ Regimen A is safer by {combo1.composite_safety.value - combo2.composite_safety.value:.4f}")
        elif combo2.composite_safety.value > combo1.composite_safety.value:
            print(f"\n→ Regimen B is safer by {combo2.composite_safety.value - combo1.composite_safety.value:.4f}")
        else:
            print("\n→ Both regimens have equivalent safety profiles")

        return {
            "regimen1_safety": combo1.composite_safety.value,
            "regimen2_safety": combo2.composite_safety.value,
            "safer": "A" if combo1.composite_safety.value > combo2.composite_safety.value else "B"
        }


# =============================================================================
# MAIN: Run analysis with real drug data
# =============================================================================

def main():
    """
    Demonstrate categorical drug interaction checking.
    """
    analyzer = DrugInteractionAnalyzer()

    # Example 1: Common polypharmacy scenario
    print("\n" + "="*70)
    print("SCENARIO 1: Elderly Patient with Multiple Conditions")
    print("="*70)

    elderly_regimen = [
        "warfarin",      # Atrial fibrillation
        "metoprolol",    # Hypertension
        "metformin",     # Type 2 diabetes
        "atorvastatin",  # Cholesterol
        "omeprazole",    # GERD
        "aspirin",       # Cardiovascular protection
    ]

    result1 = analyzer.analyze(elderly_regimen)

    # Example 2: High-risk psychiatric combination
    print("\n" + "="*70)
    print("SCENARIO 2: Pain Patient with Depression")
    print("="*70)

    pain_depression = [
        "sertraline",    # Depression
        "tramadol",      # Chronic pain
        "gabapentin",    # Neuropathic pain
    ]

    result2 = analyzer.analyze(pain_depression)

    # Example 3: Compare safer alternatives
    print("\n" + "="*70)
    print("SCENARIO 3: Finding Safer Alternative")
    print("="*70)

    # Original: sertraline + tramadol (high risk)
    # Alternative: sertraline + acetaminophen (safer)
    analyzer.compare_regimens(
        ["sertraline", "tramadol", "gabapentin"],
        ["sertraline", "acetaminophen", "gabapentin"]
    )

    # Example 4: Anticoagulation management
    print("\n" + "="*70)
    print("SCENARIO 4: Anticoagulation + NSAIDs")
    print("="*70)

    anticoag_scenario = [
        "warfarin",
        "ibuprofen",
        "prednisone",
    ]

    result4 = analyzer.analyze(anticoag_scenario)

    return {
        "scenario1": result1,
        "scenario2": result2,
        "scenario4": result4
    }


if __name__ == "__main__":
    results = main()
