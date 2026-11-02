"""
main.py
-------
Command-line driver and demonstration runner for the Rule-Based Expert System.

Supports:
1. Automated Pre-configured Test Cases (Rice, Coffee, Apple, Acidic Soil Remediation).
2. Interactive Consultation Mode (User enters their own farm parameters).
3. Explanation Facility Demonstration ("HOW" reasoning audit & "WHY NOT" counterfactuals).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from engine.inference_engine import ForwardChainingEngine
from knowledge_base import get_complete_knowledge_base

def run_consultation(inputs: dict, engine: ForwardChainingEngine, why_not_target: str = "apple"):
    print("\n" + "=" * 78)
    print("🌾 INITIATING RULE-BASED EXPERT CONSULTATION")
    print("=" * 78)
    print("Input Farm Parameters:")
    for k, v in inputs.items():
        print(f"  • {k:12}: {v}")

    # Load into engine
    engine.memory.clear()
    engine.load_user_inputs(inputs)

    # Execute forward chaining inference
    results = engine.run()

    print("\n" + "-" * 78)
    print(" INFERENCE CONCLUSIONS & RECOMMENDATIONS")
    print("-" * 78)

    # 1. Primary Recommendation
    primary = results["primary_recommendation"]
    if primary:
        crop_name = primary["name"]
        cf = primary["certainty"]
        rule_id = primary["rule_id"]
        print(f" PRIMARY RECOMMENDATION : {crop_name.upper()}")
        print(f"   Confidence / CF        : {cf:.2%} (Certainty Factor: {cf})")
        print(f"   Deciding Rule          : {rule_id}")
        print(f"   Agronomic Rationale    : {primary['description']}")
    else:
        print("⚠️ NO CROP MATCHED: The input environmental conditions did not satisfy any known crop rule.")

    # 2. Alternative Candidates
    alternatives = results["alternative_candidates"]
    if alternatives:
        print("\n🌱 Alternative Viable Crops:")
        for alt in alternatives:
            print(f"   - {alt['name']} (CF: {alt['certainty']:.2%}) via [{alt['rule_id']}]")

    # 3. Soil Diagnostics
    diagnostics = results["soil_diagnostics"]
    if diagnostics:
        print("\n🧪 Soil Health Observations:")
        for diag in diagnostics:
            print(f"   - Alert: {diag['name']} (CF: {diag['certainty']:.2%}) | {diag['description']}")

    # 4. Corrective Treatments
    remedies = results["corrective_actions"]
    if remedies:
        print("\n🛠️ Corrective Soil & Fertilizer Advisories:")
        for rem in remedies:
            action = rem["output"]
            print(f"   - {rem['name']}: {action['recommendation']} (Target: {action['target']})")

    # 5. Explanation Facility: HOW
    print("\n" + "=" * 78)
    print(engine.explain())

    # 6. Explanation Facility: WHY NOT (Counterfactual)
    if why_not_target:
        print("\n" + "-" * 78)
        print(f"🔍 COUNTERFACTUAL ANALYSIS: 'Why Not {why_not_target.capitalize()}?'")
        print("-" * 78)
        print(engine.explain_why_not(why_not_target))
        print("=" * 78)


def main():
    print("=" * 78)
    print(" RULE-BASED CROP RECOMMENDATION & ADVISORY EXPERT SYSTEM")
    print("   AI Concepts and Its Applications - PBL Expert System")
    print("=" * 78)

    # Initialize complete knowledge base (22 crop rules + soil health + remedies)
    print("\n[+] Loading Knowledge Base...")
    rules = get_complete_knowledge_base()
    print(f"[+] Loaded {len(rules)} production rules into Knowledge Base.")

    engine = ForwardChainingEngine(rules)

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Interactive mode
        print("\n--- Enter Farm & Climate Parameters ---")
        try:
            n = float(input("Enter Nitrogen (N in kg/ha) : "))
            p = float(input("Enter Phosphorus (P in kg/ha) : "))
            k = float(input("Enter Potassium (K in kg/ha) : "))
            temp = float(input("Enter Temperature (°C) : "))
            hum = float(input("Enter Relative Humidity (%) : "))
            ph = float(input("Enter Soil pH (0-14) : "))
            rain = float(input("Enter Rainfall (mm) : "))
            counterfactual = input("Enter a crop to run 'Why Not?' analysis against [default: 'apple']: ").strip()
            if not counterfactual:
                counterfactual = "apple"

            user_inputs = {
                "N": n, "P": p, "K": k,
                "temperature": temp, "humidity": hum,
                "ph": ph, "rainfall": rain
            }
            run_consultation(user_inputs, engine, why_not_target=counterfactual)
        except Exception as e:
            print(f"Invalid input: {e}")
    else:
        # Pre-configured test cases demonstrating different reasoning pathways
        test_cases = [
            {
                "title": "Test Case 1: High-Rainfall Tropical Profile (Expected: Rice)",
                "inputs": {
                    "N": 85.0, "P": 45.0, "K": 42.0,
                    "temperature": 23.5, "humidity": 82.0,
                    "ph": 6.5, "rainfall": 235.0
                },
                "why_not": "coffee"
            },
            {
                "title": "Test Case 2: Acidic Highland Profile (Expected: Coffee + Acidic Remedy)",
                "inputs": {
                    "N": 105.0, "P": 30.0, "K": 32.0,
                    "temperature": 24.5, "humidity": 60.0,
                    "ph": 5.2, "rainfall": 165.0  # pH 5.2 triggers acidity diagnostic & lime advisory
                },
                "why_not": "rice"
            },
            {
                "title": "Test Case 3: Temperate Cool Profile (Expected: Apple)",
                "inputs": {
                    "N": 25.0, "P": 130.0, "K": 195.0,
                    "temperature": 22.0, "humidity": 92.0,
                    "ph": 6.0, "rainfall": 110.0
                },
                "why_not": "rice"
            }
        ]

        print("\nRunning Automated Demonstration Scenarios:")
        for idx, tc in enumerate(test_cases, 1):
            print(f"\n>>> Running Scenario {idx}: {tc['title']}")
            run_consultation(tc["inputs"], engine, why_not_target=tc["why_not"])

        print("\nTip: To run an interactive test where you type parameters, run:")
        print("     python main.py --interactive")

if __name__ == "__main__":
    main()
