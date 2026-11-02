"""
knowledge_base/soil_advisory_rules.py
-------------------------------------
Multi-Level Production Rules for Soil Health Diagnostics and Corrective Actions.

Role in Expert System:
Demonstrates chained reasoning (Intermediate Facts -> Corrective Recommendations).
Level 1: Inspects raw values (pH, N, P, K) and asserts diagnostic facts into Working Memory.
Level 2: Matches diagnostic facts and fires actionable agronomic remedies.
"""

from typing import List
from engine.rule import Rule
from engine.fact import WorkingMemory

def load_soil_and_advisory_rules() -> List[Rule]:
    rules: List[Rule] = []

    # =========================================================================
    # LEVEL 1: SOIL HEALTH DIAGNOSTIC RULES (Asserts intermediate facts)
    # =========================================================================

    rules.append(
        Rule(
            rule_id="DIAG_SOIL_ACIDIC",
            name="Soil Acidity Diagnostic",
            category="soil_diagnostics",
            description="pH below 5.5 impairs nutrient uptake and increases aluminum toxicity risk.",
            parameter_bounds={"ph": (0.0, 5.49)},
            action={"assert_fact": "soil_is_acidic", "value": True, "condition": "Strongly Acidic"},
            priority=85,
            certainty_factor=0.98
        )
    )

    rules.append(
        Rule(
            rule_id="DIAG_SOIL_ALKALINE",
            name="Soil Alkalinity Diagnostic",
            category="soil_diagnostics",
            description="pH above 7.8 leads to micronutrient fixation (Iron, Zinc, Phosphorus).",
            parameter_bounds={"ph": (7.8, 14.0)},
            action={"assert_fact": "soil_is_alkaline", "value": True, "condition": "Alkaline / Saline"},
            priority=85,
            certainty_factor=0.98
        )
    )

    rules.append(
        Rule(
            rule_id="DIAG_NITROGEN_DEFICIT",
            name="Nitrogen Deficit Diagnostic",
            category="soil_diagnostics",
            description="Nitrogen under 40 kg/ha causes stunted vegetative growth and chlorosis (yellowing).",
            parameter_bounds={"N": (0.0, 39.9)},
            action={"assert_fact": "nitrogen_deficit", "value": True, "condition": "Low Nitrogen"},
            priority=80,
            certainty_factor=0.95
        )
    )

    rules.append(
        Rule(
            rule_id="DIAG_POTASSIUM_DEFICIT",
            name="Potassium Deficit Diagnostic",
            category="soil_diagnostics",
            description="Potassium below 25 kg/ha reduces drought resistance, disease tolerance, and fruit sizing.",
            parameter_bounds={"K": (0.0, 24.9)},
            action={"assert_fact": "potassium_deficit", "value": True, "condition": "Low Potassium"},
            priority=80,
            certainty_factor=0.95
        )
    )

    rules.append(
        Rule(
            rule_id="DIAG_PHOSPHORUS_DEFICIT",
            name="Phosphorus Deficit Diagnostic",
            category="soil_diagnostics",
            description="Phosphorus below 25 kg/ha impairs root development and seed germination.",
            parameter_bounds={"P": (0.0, 24.9)},
            action={"assert_fact": "phosphorus_deficit", "value": True, "condition": "Low Phosphorus"},
            priority=80,
            certainty_factor=0.95
        )
    )

    # =========================================================================
    # LEVEL 2: CORRECTIVE ADVISORY RULES (Triggered by intermediate facts)
    # =========================================================================

    rules.append(
        Rule(
            rule_id="REMEDY_LIME_APPLICATION",
            name="Agricultural Lime Treatment",
            category="corrective_action",
            description="Neutralize high soil acidity to restore cation exchange capacity.",
            parameter_bounds={},  # Evaluates intermediate fact in working memory
            action={
                "action_type": "Soil Amendment",
                "recommendation": "Broadcast Agricultural Lime (CaCO3) at 1.5 - 2.5 tons/hectare 4 weeks prior to sowing.",
                "target": "Raise pH toward 6.5"
            },
            priority=40,
            certainty_factor=0.95,
            custom_predicate=lambda mem: mem.get_value("soil_is_acidic", False) is True
        )
    )

    rules.append(
        Rule(
            rule_id="REMEDY_GYPSUM_APPLICATION",
            name="Agricultural Gypsum Treatment",
            category="corrective_action",
            description="Remediate soil alkalinity and replace exchangeable sodium.",
            parameter_bounds={},
            action={
                "action_type": "Soil Amendment",
                "recommendation": "Apply Agricultural Gypsum (CaSO4) at 2.0 tons/ha accompanied by deep leaching irrigation.",
                "target": "Reduce pH toward neutral (7.0)"
            },
            priority=40,
            certainty_factor=0.95,
            custom_predicate=lambda mem: mem.get_value("soil_is_alkaline", False) is True
        )
    )

    rules.append(
        Rule(
            rule_id="REMEDY_UREA_TOPDRESSING",
            name="Nitrogen Replenishment Protocol",
            category="corrective_action",
            description="Restore soil nitrogen reserves to support rapid vegetative shoot growth.",
            parameter_bounds={},
            action={
                "action_type": "Fertilizer Advisory",
                "recommendation": "Apply split-dose Urea (46% N) at 80-100 kg/ha or incorporate green manure (Sesbania).",
                "target": "Correct Nitrogen Deficiency"
            },
            priority=35,
            certainty_factor=0.90,
            custom_predicate=lambda mem: mem.get_value("nitrogen_deficit", False) is True
        )
    )

    rules.append(
        Rule(
            rule_id="REMEDY_POTASH_APPLICATION",
            name="Muriate of Potash Application",
            category="corrective_action",
            description="Boost potassium for physiological hardiness and fruit filling.",
            parameter_bounds={},
            action={
                "action_type": "Fertilizer Advisory",
                "recommendation": "Apply Muriate of Potash (MOP / KCl) at 50 kg/ha during basal soil preparation.",
                "target": "Correct Potassium Deficiency"
            },
            priority=35,
            certainty_factor=0.90,
            custom_predicate=lambda mem: mem.get_value("potassium_deficit", False) is True
        )
    )

    return rules
