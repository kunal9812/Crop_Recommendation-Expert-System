"""
engine/rule.py
--------------
Represents Production Rules (IF <antecedents> THEN <consequent>)
in the Rule-Based Expert System.

Role in Expert System:
Production rules encode the domain expertise.
Each Rule encapsulates:
1. Antecedent (Conditions): Predicates checked against Working Memory.
2. Consequent (Action): Inferred facts, crop recommendations, or advisory actions.
3. Saliency (Priority): Conflict resolution weight.
4. Certainty Factor: The confidence of this rule given perfect conditions.
5. Explanation Metadata: Granular condition tracking for the Explanation Facility.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from .fact import WorkingMemory

class RuleEvaluationResult:
    """Holds the result of testing a rule against working memory."""
    def __init__(self, rule_id: str, is_satisfied: bool, parameter_evaluations: Dict[str, Dict[str, Any]], cf: float):
        self.rule_id = rule_id
        self.is_satisfied = is_satisfied
        self.parameter_evaluations = parameter_evaluations  # {param: {'actual': val, 'expected': range, 'passed': bool}}
        self.calculated_cf = cf

    def __repr__(self):
        status = "PASSED" if self.is_satisfied else "FAILED"
        return f"<RuleResult: {self.rule_id} [{status}] CF={self.calculated_cf:.2f}>"


class Rule:
    def __init__(
        self,
        rule_id: str,
        name: str,
        category: str,
        description: str,
        parameter_bounds: Dict[str, Tuple[float, float]],
        action: Union[str, Dict[str, Any], Callable[[WorkingMemory], Any]],
        priority: int = 50,
        certainty_factor: float = 1.0,
        custom_predicate: Optional[Callable[[WorkingMemory], bool]] = None
    ):
        """
        :param rule_id: Unique identifier (e.g., 'RULE_RICE_01')
        :param name: Human-readable name
        :param category: Classification category ('crop_recommendation', 'soil_diagnostics', 'treatment')
        :param description: Explanatory rationale of the rule
        :param parameter_bounds: Dict of {param_name: (min_val, max_val)}
        :param action: Consequent returned or executed when rule fires
        :param priority: Conflict resolution priority (1 to 100, higher fires first)
        :param certainty_factor: Base confidence factor (0.0 to 1.0)
        :param custom_predicate: Optional custom logic lambda
        """
        self.rule_id = rule_id
        self.name = name
        self.category = category
        self.description = description
        self.parameter_bounds = parameter_bounds
        self.action = action
        self.priority = priority
        self.certainty_factor = certainty_factor
        self.custom_predicate = custom_predicate

    def evaluate(self, memory: WorkingMemory) -> RuleEvaluationResult:
        """
        Evaluates the rule against the current facts in Working Memory.
        Computes both overall satisfaction and parameter-by-parameter diagnostics.
        """
        param_evals = {}
        all_passed = True
        min_condition_cf = 1.0

        for param, (low, high) in self.parameter_bounds.items():
            fact = memory.get_fact(param)
            if fact is None:
                param_evals[param] = {
                    "actual": None,
                    "expected": f"[{low}, {high}]",
                    "passed": False,
                    "reason": "Fact missing in working memory"
                }
                all_passed = False
                continue

            val = fact.value
            in_range = (low <= val <= high)
            param_evals[param] = {
                "actual": val,
                "expected": f"[{low}, {high}]",
                "passed": in_range,
                "reason": "Within bounds" if in_range else f"Out of bounds (Expected: {low} - {high}, Got: {val})"
            }

            if in_range:
                # Modulate certainty based on how close fact is to center of range
                midpoint = (low + high) / 2.0
                spread = max(1e-5, (high - low) / 2.0)
                distance_ratio = abs(val - midpoint) / spread
                proximity_score = max(0.6, 1.0 - (0.4 * distance_ratio))
                condition_cf = fact.certainty * proximity_score
                min_condition_cf = min(min_condition_cf, condition_cf)
            else:
                all_passed = False

        if self.custom_predicate is not None:
            predicate_passed = self.custom_predicate(memory)
            param_evals["custom_predicate"] = {
                "actual": predicate_passed,
                "expected": True,
                "passed": predicate_passed,
                "reason": "Custom condition met" if predicate_passed else "Custom condition failed"
            }
            if not predicate_passed:
                all_passed = False

        final_cf = (min_condition_cf * self.certainty_factor) if all_passed else 0.0
        return RuleEvaluationResult(self.rule_id, all_passed, param_evals, final_cf)

    def execute_action(self, memory: WorkingMemory) -> Any:
        """Executes or returns the rule consequent."""
        if callable(self.action):
            return self.action(memory)
        return self.action

    def __repr__(self):
        return f"<Rule {self.rule_id}: '{self.name}' (Priority={self.priority}, CF={self.certainty_factor})>"
