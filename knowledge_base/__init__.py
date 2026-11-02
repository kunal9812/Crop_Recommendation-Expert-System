"""
knowledge_base package
"""
from .crop_rules import load_crop_rules
from .soil_advisory_rules import load_soil_and_advisory_rules

def get_complete_knowledge_base():
    """Combines all crop rules, soil diagnostic rules, and corrective advisory rules."""
    rules = []
    rules.extend(load_soil_and_advisory_rules())  # Diagnostics & remedies
    rules.extend(load_crop_rules())               # 22 crop suitability rules
    return rules

__all__ = ["load_crop_rules", "load_soil_and_advisory_rules", "get_complete_knowledge_base"]
