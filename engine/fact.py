"""
engine/fact.py
--------------
Represents Facts and Working Memory in the Rule-Based Expert System.

Role in Expert System:
Working Memory stores the current state of knowledge during an inference session.
Facts can be:
- Directly asserted by the user (e.g., Temperature = 24.5, pH = 6.8)
- Inferred as intermediate facts by rules (e.g., Soil_State = 'Acidic', Drought_Risk = True)
- Supported by a Certainty Factor (CF) ranging from -1.0 (definitely false) to +1.0 (definitely true).
"""

from typing import Any, Dict, List, Optional

class Fact:
    def __init__(self, name: str, value: Any, certainty: float = 1.0, source: str = "user_input"):
        """
        :param name: Unique name / identifier for the fact (e.g., 'temperature')
        :param value: Concrete value (numeric, string, or boolean)
        :param certainty: Certainty factor between -1.0 and 1.0 (default: 1.0)
        :param source: Origin of the fact ('user_input', 'inferred_rule:<id>', etc.)
        """
        self.name = name
        self.value = value
        self.certainty = max(-1.0, min(1.0, float(certainty)))
        self.source = source

    def __repr__(self):
        return f"Fact({self.name}={self.value}, CF={self.certainty:.2f}, source='{self.source}')"


class WorkingMemory:
    """
    Manages the active facts for an inference session.
    Provides methods to assert, query, retract, and inspect facts.
    """
    def __init__(self):
        self._facts: Dict[str, Fact] = {}
        self._history: List[Fact] = []

    def assert_fact(self, name: str, value: Any, certainty: float = 1.0, source: str = "user_input") -> Fact:
        fact = Fact(name, value, certainty, source)
        self._facts[name] = fact
        self._history.append(fact)
        return fact

    def get_fact(self, name: str) -> Optional[Fact]:
        return self._facts.get(name)

    def get_value(self, name: str, default: Any = None) -> Any:
        fact = self._facts.get(name)
        return fact.value if fact is not None else default

    def has_fact(self, name: str) -> bool:
        return name in self._facts

    def get_all_facts(self) -> Dict[str, Any]:
        return {k: f.value for k, f in self._facts.items()}

    def get_fact_objects(self) -> List[Fact]:
        return list(self._facts.values())

    def clear(self):
        self._facts.clear()
        self._history.clear()

    def __repr__(self):
        return f"<WorkingMemory: {len(self._facts)} active facts>"
