"""
engine/explanation_facility.py
------------------------------
Implements the Explanation Facility for the Rule-Based Expert System.

Role in Expert System:
The Explanation Facility is what sets symbolic AI apart from black-box ML.
It provides:
1. "HOW" Explanation: Explains the audit trail of rules that fired to reach the decision.
2. "WHY NOT" Explanation (Counterfactual): Explains why an alternative candidate was rejected.
3. "WHY" Explanation: Explains why a specific parameter or question is necessary.
"""

from typing import Any, Dict, List, Optional
from .rule import Rule, RuleEvaluationResult

class ExplanationFacility:
    def __init__(self):
        self._fired_rules_history: List[Dict[str, Any]] = []
        self._failed_rules_history: List[Dict[str, Any]] = []

    def record_evaluation(self, rule: Rule, result: RuleEvaluationResult):
        record = {
            "rule": rule,
            "rule_id": rule.rule_id,
            "name": rule.name,
            "category": rule.category,
            "description": rule.description,
            "is_satisfied": result.is_satisfied,
            "parameter_evaluations": result.parameter_evaluations,
            "certainty": result.calculated_cf,
            "priority": rule.priority
        }
        if result.is_satisfied:
            self._fired_rules_history.append(record)
        else:
            self._failed_rules_history.append(record)

    def explain_how(self) -> str:
        """Generates a comprehensive reasoning audit trail for all fired rules."""
        if not self._fired_rules_history:
            return "No rules fired during inference. The provided facts did not satisfy any known domain rule."

        lines = ["##  Reasoning Audit Trail (HOW Conclusions Were Reached)", ""]
        for idx, item in enumerate(self._fired_rules_history, 1):
            rule = item["rule"]
            lines.append(f"### {idx}. Rule Fired: [{rule.rule_id}] - {rule.name}")
            lines.append(f"Category: `{rule.category}` | Priority: `{rule.priority}` | Certainty Factor: `{item['certainty']:.2f}`")
            lines.append(f"Agronomic Justification: {rule.description}")
            lines.append("")
            lines.append("| Parameter | Input Value | Required Range | Status |")
            lines.append("| :--- | :---: | :---: | :---: |")
            for param, diag in item["parameter_evaluations"].items():
                status_icon = "PASS" if diag["passed"] else "FAIL"
                lines.append(f"| {param} | `{diag['actual']}` | `{diag['expected']}` | {status_icon} |")
            lines.append("")
        return "\n".join(lines)

    def explain_why_not(self, target_crop_or_rule_id: str) -> str:
        """
        Counterfactual Explanation:
        Explains why a specific crop or rule failed to fire.
        """
        target = target_crop_or_rule_id.strip().lower()
        matched_records = [
            r for r in self._failed_rules_history
            if target in r["rule_id"].lower() or target in r["name"].lower()
        ]

        if not matched_records:
            # Check if it was actually fired
            fired_match = [
                r for r in self._fired_rules_history
                if target in r["rule_id"].lower() or target in r["name"].lower()
            ]
            if fired_match:
                return f"Candidate '{target_crop_or_rule_id}' actually **SUCCEEDED** and fired rule `{fired_match[0]['rule_id']}` with CF={fired_match[0]['certainty']:.2f}."
            return f"No rule related to '{target_crop_or_rule_id}' was evaluated in the knowledge base."

        record = matched_records[0]
        rule = record["rule"]
        lines = [
            f"###  Why Not {rule.name}?",
            f"Rule Evaluated: `{rule.rule_id}`",
            f"General Requirement: {rule.description}",
            "",
            "Specific Condition Violations:"
        ]

        failures = 0
        for param, diag in record["parameter_evaluations"].items():
            if not diag["passed"]:
                failures += 1
                lines.append(f"-  {param}: Expected `{diag['expected']}`, but your value was `{diag['actual']}`.")
            else:
                lines.append(f"-  {param}: `{diag['actual']}` satisfied `{diag['expected']}`.")

        lines.append(f"\n*Summary: Rejected due to {failures} parameter violation(s).*")
        return "\n".join(lines)

    def explain_why_parameter(self, param_name: str, rules: List[Rule]) -> str:
        """Explains why a specific input parameter is requested."""
        dependent_rules = [r for r in rules if param_name in r.parameter_bounds]
        affected_crops = sorted(list(set([r.name for r in dependent_rules])))
        return (
            f"Parameter '{param_name}' is required to evaluate {len(dependent_rules)} rules "
            f"governing: {', '.join(affected_crops[:8])}{'...' if len(affected_crops) > 8 else ''}."
        )

    def get_fired_summary(self) -> List[Dict[str, Any]]:
        return self._fired_rules_history

    def clear(self):
        self._fired_rules_history.clear()
        self._failed_rules_history.clear()
