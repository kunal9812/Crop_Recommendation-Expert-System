"""
knowledge_base/crop_rules.py
----------------------------
Expanded Production Rules for all 22 Crops.

Role in Expert System:
Encodes the primary crop recommendation rules.
The bounds are derived from agronomic bounds in `knowledge_base.json`
(extracted during Knowledge Acquisition).
Each rule specifies:
- 7-parameter environmental & soil envelope (N, P, K, Temp, Humidity, pH, Rainfall)
- Agronomic description
- Conflict resolution priority (saliency)
- Base Certainty Factor (0.90 to 0.98)
"""

import json
import os
from typing import List
from engine.rule import Rule

KB_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge_base.json")

def load_crop_rules() -> List[Rule]:
    """Loads and instantiates production rules for all 22 crops from knowledge_base.json."""
    if not os.path.exists(KB_JSON_PATH):
        raise FileNotFoundError(f"Knowledge base file not found at: {KB_JSON_PATH}. Run knowledge_acquisition.py first.")

    with open(KB_JSON_PATH, "r", encoding="utf-8") as f:
        kb_data = json.load(f)

    rules: List[Rule] = []

    # Curated agronomic explanations for each crop
    crop_descriptions = {
        "rice": "Tropical cereal requiring abundant water (>180mm), high humidity (>80%), and warm temperatures (20-27°C).",
        "maize": "Versatile warm-season crop requiring balanced NPK, moderate rainfall (60-110mm), and neutral pH.",
        "chickpea": "Cooler semi-arid legume thriving in dry humidity (<25%), low rainfall (<100mm), and neutral soil.",
        "kidneybeans": "Cool-climate legume favoring lower temperatures (15-24°C), high potassium, and moderate rain.",
        "pigeonpeas": "Drought-hardy legume with high temperature tolerance and deep rooting requirements.",
        "mothbeans": "Arid-zone pulse crop highly tolerant of drought and low moisture conditions.",
        "mungbean": "Short-duration warm pulse crop suited for moderate temperature (27-29°C) and medium humidity.",
        "blackgram": "Warm humid legume thriving in high temperatures (25-35°C) and balanced phosphorus.",
        "lentil": "Cool-season pulse requiring low moisture and mild temperatures.",
        "pomegranate": "Subtropical fruit requiring low rainfall, warm dry ripening climate, and neutral-to-lightly alkaline soil.",
        "banana": "Heavy feeder requiring rich potassium (>45), high moisture, and constant warm tropical climate.",
        "mango": "Tropical fruit tree requiring warm conditions (27-36°C) and distinct dry periods for flowering.",
        "grapes": "Temperate/subtropical vine requiring very high potassium (>180), high phosphorus, and dry harvesting weather.",
        "watermelon": "Warm climate cucurbit requiring high temperatures (>24°C), sandy-loam soil, and high potassium.",
        "muskmelon": "Warm dry climate fruit with high phosphorus and potassium needs and low rain tolerance during maturity.",
        "apple": "Temperate tree fruit requiring cool chilling temperatures (15-24°C) and rich potassium reserves.",
        "orange": "Subtropical citrus needing moderate warmth (15-35°C), low-to-medium rainfall, and well-drained soil.",
        "papaya": "Tropical fruit requiring warm temperatures (25-38°C), high humidity (>90%), and ample rainfall.",
        "coconut": "Coastal tropical palm requiring continuous high humidity (>90%), sea-level warmth, and high rainfall.",
        "cotton": "Cash fiber crop requiring high heat, high phosphorus/potassium, and dry picking conditions.",
        "jute": "Golden bast fiber requiring prolonged high humidity (>80%), hot weather, and heavy rainfall (>150mm).",
        "coffee": "Highland tropical crop requiring gentle shade, high rainfall (150-200mm), acidic soil, and high nitrogen."
    }

    for crop_key, profile in kb_data["crops"].items():
        bounds = {}
        for feat in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']:
            # Use absolute bounds with a small 5% buffer for realistic tolerance
            abs_min = profile["absolute_bounds"][feat]["min"]
            abs_max = profile["absolute_bounds"][feat]["max"]
            buf = (abs_max - abs_min) * 0.05
            bounds[feat] = (round(max(0.0, abs_min - buf), 2), round(abs_max + buf, 2))

        rule_id = f"RULE_{crop_key.upper()}_RECOMMENDATION"
        crop_name = profile["name"]
        description = crop_descriptions.get(crop_key, f"Cultivation suitability rule for {crop_name}.")
        priority = profile.get("saliency_priority", 50)

        # High-specificity crops (like apple, coffee, rice, grapes) receive higher certainty
        base_cf = 0.95 if priority > 60 else 0.90

        rule = Rule(
            rule_id=rule_id,
            name=f"{crop_name} Suitability",
            category="crop_recommendation",
            description=description,
            parameter_bounds=bounds,
            action={
                "crop": crop_name,
                "label": crop_key,
                "optimal_ranges": profile["optimal_ranges"],
                "means": profile["means"]
            },
            priority=priority,
            certainty_factor=base_cf
        )
        rules.append(rule)

    return rules
