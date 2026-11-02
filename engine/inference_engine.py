"""
engine/inference_engine.py
--------------------------
Implements the Forward-Chaining Inference Engine with Conflict Resolution
for the Rule-Based Expert System.

Role in Expert System:
The Inference Engine executes the reasoning cycle:
1. MATCH: Matches facts in Working Memory against all rule antecedents.
2. RESOLVE CONFLICTS: Sorts matching rules using:
   - Saliency / Priority
   - Rule Specificity (more specific conditions take precedence)
   - Calculated Certainty Factor
3. ACT: Fires matching rules, generates recommendations, and asserts intermediate facts.
4. EXPLAIN: Integrates with ExplanationFacility to log execution traces.
"""

from typing import Any, Dict, List, Optional
from .fact import WorkingMemory, Fact
from .rule import Rule, RuleEvaluationResult
from .explanation_facility import ExplanationFacility

class ForwardChainingEngine:
    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules: List[Rule] = rules if rules is not None else []
        self.memory = WorkingMemory()
        self.explanation_facility = ExplanationFacility()

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def set_rules(self, rules: List[Rule]):
        self.rules = rules

    def assert_fact(self, name: str, value: Any, certainty: float = 1.0, source: str = "user_input"):
        return self.memory.assert_fact(name, value, certainty, source)

    def load_user_inputs(self, inputs: Dict[str, Any]):
        """Populates Working Memory with initial input parameters."""
        for param, val in inputs.items():
            self.memory.assert_fact(param, val, certainty=1.0, source="user_input")

    def run(self, max_cycles: int = 5) -> Dict[str, Any]:
        """
        Executes multi-pass forward chaining until no new rules fire or max_cycles is reached.
        Multi-pass allows intermediate facts (e.g., soil health diagnostics)
        to trigger subsequent corrective action rules.
        """
        self.explanation_facility.clear()
        fired_rule_ids = set()
        recommendations = []
        diagnostics = []
        corrective_actions = []

        for cycle in range(max_cycles):
            new_rules_fired_in_cycle = 0

            # 1. MATCH: Evaluate all un-fired rules
            eligible_rules: List[Rule] = []
            results_map: Dict[str, RuleEvaluationResult] = {}

            for rule in self.rules:
                if rule.rule_id in fired_rule_ids:
                    continue

                eval_result = rule.evaluate(self.memory)
                self.explanation_facility.record_evaluation(rule, eval_result)

                if eval_result.is_satisfied:
                    eligible_rules.append(rule)
                    results_map[rule.rule_id] = eval_result

            if not eligible_rules:
                # Quiescence reached: no more rules can fire
                break

            # 2. CONFLICT RESOLUTION:
            # Sort eligible rules by:
            # a) Priority (Saliency) descending
            # b) Specificity (number of parameter constraints) descending
            # c) Certainty Factor descending
            eligible_rules.sort(
                key=lambda r: (
                    r.priority,
                    len(r.parameter_bounds),
                    results_map[r.rule_id].calculated_cf
                ),
                reverse=True
            )

            # 3. ACT: Fire rules
            for rule in eligible_rules:
                fired_rule_ids.add(rule.rule_id)
                new_rules_fired_in_cycle += 1
                res = results_map[rule.rule_id]
                action_output = rule.execute_action(self.memory)

                entry = {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "category": rule.category,
                    "priority": rule.priority,
                    "certainty": round(res.calculated_cf, 3),
                    "output": action_output,
                    "description": rule.description
                }

                if rule.category == "crop_recommendation":
                    recommendations.append(entry)
                elif rule.category == "soil_diagnostics":
                    diagnostics.append(entry)
                    # Assert intermediate fact into working memory to feed corrective rules
                    if isinstance(action_output, dict) and "assert_fact" in action_output:
                        f_name = action_output["assert_fact"]
                        f_val = action_output.get("value", True)
                        self.memory.assert_fact(f_name, f_val, certainty=res.calculated_cf, source=f"rule:{rule.rule_id}")
                elif rule.category == "corrective_action":
                    corrective_actions.append(entry)

            if new_rules_fired_in_cycle == 0:
                break

        # Best recommendation (winner of conflict resolution)
        primary_crop = recommendations[0] if recommendations else None
        alternatives = recommendations[1:] if len(recommendations) > 1 else []

        return {
            "primary_recommendation": primary_crop,
            "alternative_candidates": alternatives,
            "soil_diagnostics": diagnostics,
            "corrective_actions": corrective_actions,
            "total_rules_evaluated": len(self.rules),
            "total_rules_fired": len(fired_rule_ids),
            "facts_in_memory": self.memory.get_all_facts()
        }

    def explain(self) -> str:
        """Convenience method to retrieve full reasoning trace."""
        return self.explanation_facility.explain_how()

    def explain_why_not(self, crop_name: str) -> str:
        """Convenience method to retrieve counterfactual explanation."""
        return self.explanation_facility.explain_why_not(crop_name)
