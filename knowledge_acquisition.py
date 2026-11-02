"""
knowledge_acquisition.py
------------------------
Module for the Knowledge Acquisition Phase of the Rule-Based Expert System.

Role in Expert System:
In classical AI, Knowledge Acquisition bridges domain expertise and the machine-
readable Knowledge Base. This script processes empirical agricultural data from
Crop_recommendation.csv to determine the agronomic parameter boundaries
(Nitrogen, Phosphorus, Potassium, Temperature, Humidity, pH, Rainfall) for each crop.

It calculates:
1. Hard Constraints: The absolute min and max observed bounds for each parameter.
2. Optimal Ranges: The 5th to 95th percentile ranges to avoid outlier noise.
3. Rule Saliency: Higher priority for crops with specialized, narrow climatic requirements.

The output is exported as `knowledge_base.json` for consumption by the inference engine.
"""

import json
import os
import pandas as pd
import numpy as np
import engine

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "Crop_recommendation.csv"
)
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "knowledge_base.json")

def acquire_knowledge(csv_path: str = DATA_PATH) -> dict:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    crops = sorted(df['label'].unique())

    knowledge_base = {
        "metadata": {
            "source": "Empirical Agronomic Dataset (Crop_recommendation.csv)",
            "total_crops": len(crops),
            "parameters": features,
            "description": "Rules and boundary conditions extracted for Rule-Based Expert System."
        },
        "crops": {},
        "soil_thresholds": {
            "nitrogen": {"low": 40, "high": 90, "unit": "kg/ha"},
            "phosphorus": {"low": 35, "high": 70, "unit": "kg/ha"},
            "potassium": {"low": 30, "high": 60, "unit": "kg/ha"},
            "ph": {
                "strongly_acidic": [0.0, 5.5],
                "moderately_acidic": [5.5, 6.5],
                "neutral": [6.5, 7.5],
                "alkaline": [7.5, 14.0]
            }
        }
    }

    for crop in crops:
        crop_data = df[df['label'] == crop]
        profile = {
            "name": crop.capitalize(),
            "optimal_ranges": {},
            "absolute_bounds": {},
            "means": {}
        }

        # Calculate range tolerance width to assess rule specificity
        total_relative_spread = 0.0

        for feat in features:
            values = crop_data[feat]
            q05 = float(np.percentile(values, 5))
            q95 = float(np.percentile(values, 95))
            min_val = float(values.min())
            max_val = float(values.max())
            mean_val = float(values.mean())

            profile["optimal_ranges"][feat] = {
                "min": round(q05, 2),
                "max": round(q95, 2)
            }
            profile["absolute_bounds"][feat] = {
                "min": round(min_val, 2),
                "max": round(max_val, 2)
            }
            profile["means"][feat] = round(mean_val, 2)

            # Measure variance / spread to set rule specificity priority
            spread = max_val - min_val
            total_relative_spread += spread / (mean_val + 1e-5)

        # More specialized crops (narrower climate niche) get higher priority in conflict resolution
        # E.g., Apple requires very specific low temperature compared to general crops
        profile["saliency_priority"] = max(1, int(100 - min(90, total_relative_spread * 5)))

        knowledge_base["crops"][crop] = profile

    return knowledge_base

def export_knowledge_base():
    kb = acquire_knowledge()
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2)
    print(f"Knowledge Base successfully built and saved to: {OUTPUT_JSON}")
    print(f"Extracted rules for {len(kb['crops'])} crops.")

if __name__ == "__main__":
    export_knowledge_base()
