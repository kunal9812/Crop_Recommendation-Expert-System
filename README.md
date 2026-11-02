# 🌾 Rule-Based Crop Recommendation & Advisory Expert System

**Course:** AI Concepts and Its Applications — Problem-Based Learning (PBL)  
**Method:** Symbolic AI — Forward Chaining Inference with Certainty Factors

A pure-Python, from-scratch implementation of a classical Expert System for precision agricultural crop recommendation and multi-level soil health advisory. Unlike statistical ML models, this system provides complete, verifiable reasoning through an Explanation Facility.

---

## 📁 Project Structure

```
Rule-Based-Crop-Expert-System/
│
├── app_streamlit.py          # Streamlit web frontend (main UI)
├── main.py                   # CLI driver: automated test cases & interactive mode
├── knowledge_acquisition.py  # Data pipeline: CSV → knowledge_base.json
├── knowledge_base.json       # Auto-generated machine-readable knowledge base (22 crops)
├── Crop_recommendation.csv   # Source agricultural dataset (2,200 rows × 8 columns)
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
│
├── engine/                   # Core Symbolic AI Engine (pure Python, no ML)
│   ├── __init__.py
│   ├── fact.py               # Fact & WorkingMemory classes
│   ├── rule.py               # Rule & RuleEvaluationResult classes
│   ├── inference_engine.py   # ForwardChainingEngine (Match → Resolve → Act loop)
│   └── explanation_facility.py  # HOW / WHY NOT / WHY explanations
│
└── knowledge_base/           # Production rule definitions
    ├── __init__.py           # get_complete_knowledge_base() entry point
    ├── crop_rules.py         # 22 crop suitability rules (loaded from knowledge_base.json)
    └── soil_advisory_rules.py  # Multi-level soil diagnostic & corrective action rules
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Regenerate the knowledge base from raw data

Only needed if you modify `Crop_recommendation.csv` or want to rebuild the rules:

```bash
python knowledge_acquisition.py
```

This processes the CSV dataset and writes a fresh `knowledge_base.json`.

### 3. Launch the web UI

```bash
streamlit run app_streamlit.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser.

### 4. (Alternative) Run the CLI demo

```bash
# Run 3 automated test scenarios (Rice / Coffee+Acidity / Apple)
python main.py

# Interactive mode — enter your own values
python main.py --interactive
```

---

## 🌐 Streamlit Web Interface

The web UI is a clean, centered single-page form. It requires no frameworks beyond Streamlit and uses custom CSS for result cards.

### How to use it

1. Fill in the 7 input fields (Nitrogen, Phosphorus, Potassium, Temperature, Humidity, pH, Rainfall).
2. Optionally pick a crop from the **"Why not?"** dropdown to run a counterfactual audit.
3. Click **Get Recommendation**.

### What it shows

| Section | Description |
| :--- | :--- |
| **Recommended crop card** | Crop name, confidence (Certainty Factor), and agronomic justification. |
| **Other options chips** | Alternative crops that also matched, with their confidence scores. |
| **Soil health** | Intermediate diagnostic facts asserted by Level 1 rules (e.g. acidity, nutrient deficits). |
| **Recommended actions** | Corrective advisories from Level 2 rules (e.g. lime treatment, fertilizer prescription). |
| **How was this decided?** (expander) | Full HOW reasoning audit table — every rule that fired, with PASS/FAIL per parameter. |
| **Why not `<crop>`?** (expander) | Counterfactual breakdown listing the exact boundary violations that disqualified the chosen crop. |

---

## 🧠 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Rule-Based Expert System                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
  [ User Interface ]  [ Inference Engine ]  [ Knowledge Base ]
  app_streamlit.py    inference_engine.py   crop_rules.py
  main.py             ── MATCH             soil_advisory_rules.py
                      ── RESOLVE           knowledge_base.json
                      ── ACT
                           │
                           ▼
                  [ Working Memory ]        [ Explanation Facility ]
                  fact.py                   explanation_facility.py
                  WorkingMemory             HOW / WHY NOT / WHY
```

### Inference Cycle (Forward Chaining)

Each call to `engine.run()` executes up to 5 passes:

1. **MATCH** — Each unfired rule's antecedents are checked against Working Memory.
2. **RESOLVE** — Eligible rules are ranked by: `priority (saliency)` → `specificity (# conditions)` → `certainty factor`.
3. **ACT** — Rules fire in order. Soil diagnostic rules assert new intermediate facts (e.g. `soil_is_acidic = True`) back into Working Memory, enabling Level 2 corrective rules to fire in the next pass.
4. **QUIESCENCE** — The cycle stops when no new rules fire.

---

## ⚙️ Core Components

### `engine/fact.py` — `Fact` & `WorkingMemory`

| Class | Role |
| :--- | :--- |
| `Fact(name, value, certainty, source)` | A single piece of knowledge. `certainty` is a float in `[-1.0, 1.0]`. `source` is either `"user_input"` or `"rule:<id>"` for inferred facts. |
| `WorkingMemory` | Session-scoped store. Supports `assert_fact`, `get_fact`, `has_fact`, `clear`. |

### `engine/rule.py` — `Rule` & `RuleEvaluationResult`

| Field | Description |
| :--- | :--- |
| `rule_id` | Unique string ID (e.g. `RULE_RICE_RECOMMENDATION`) |
| `name` | Human-readable label |
| `category` | `"crop_recommendation"`, `"soil_diagnostics"`, or `"corrective_action"` |
| `parameter_bounds` | `{param: (min, max)}` — the antecedent envelope |
| `certainty_factor` | Base confidence (0.9–0.98). Modulated by proximity to midpoint of range at evaluation time. |
| `priority` | Saliency integer (1–100). Higher = evaluated first during conflict resolution. |
| `custom_predicate` | Optional `lambda memory: bool` for rules that check inferred facts (e.g. `soil_is_acidic`). |

**Certainty modulation:** When a value is inside a bound but far from the midpoint, its per-condition CF is reduced using:
```
proximity_score = max(0.6, 1.0 - 0.4 × (distance / half_range))
final_cf = min(condition_cfs) × rule_base_cf
```

### `engine/inference_engine.py` — `ForwardChainingEngine`

Key methods:

```python
engine.load_user_inputs(dict)   # Assert user facts into Working Memory
engine.run()                    # Execute inference; returns structured result dict
engine.explain()                # → HOW audit trail (Markdown string)
engine.explain_why_not(crop)    # → Counterfactual breakdown (Markdown string)
engine.memory.clear()           # Reset between sessions
```

Result dict keys: `primary_recommendation`, `alternative_candidates`, `soil_diagnostics`, `corrective_actions`, `total_rules_evaluated`, `total_rules_fired`, `facts_in_memory`.

### `engine/explanation_facility.py` — `ExplanationFacility`

| Method | Output |
| :--- | :--- |
| `explain_how()` | Markdown table showing every fired rule with PASS/FAIL per parameter. |
| `explain_why_not(crop)` | Lists which specific parameter bounds a rejected crop violated. |
| `explain_why_parameter(param, rules)` | Explains which rules (and crops) depend on a given input parameter. |

### `knowledge_base/` — Production Rules

**`soil_advisory_rules.py`** defines 2 levels of chained rules:

- **Level 1 — Soil Diagnostics** (`soil_diagnostics` category): detect conditions like acidity (`ph < 5.5`), alkalinity (`ph > 7.8`), and nutrient deficits (N < 40, P < 25, K < 25). Each fires by asserting an intermediate fact (e.g. `soil_is_acidic = True`) into Working Memory.
- **Level 2 — Corrective Actions** (`corrective_action` category): triggered by those intermediate facts via `custom_predicate`. Outputs a structured advisory (e.g. Agricultural Lime Treatment, Urea Fertilisation).

**`crop_rules.py`** loads all 22 crop rules from `knowledge_base.json`. Each rule's bounds are derived as absolute min/max from the dataset, buffered by 5% for real-world tolerance.

### `knowledge_acquisition.py` — Knowledge Acquisition Pipeline

Reads `Crop_recommendation.csv` and computes for each crop:
- `absolute_bounds` — dataset min/max per parameter.
- `optimal_ranges` — 5th to 95th percentile per parameter.
- `means` — average value per parameter.
- `saliency_priority` — inversely proportional to total relative spread (specialised crops with narrow envelopes get higher priority).

Output is saved to `knowledge_base.json`.

---

## 🌱 Supported Crops (22)

Rice, Maize, Chickpea, Kidney Beans, Pigeon Peas, Moth Beans, Mung Bean, Black Gram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Musk Melon, Apple, Orange, Papaya, Coconut, Cotton, Jute, Coffee.

---

## 🧪 CLI Test Scenarios (`main.py`)

| Scenario | Key Inputs | Expected Outcome |
| :--- | :--- | :--- |
| Test Case 1 | N=85, P=45, K=42, Temp=23.5, Hum=82%, pH=6.5, Rain=235mm | Rice recommendation |
| Test Case 2 | N=105, P=30, K=32, Temp=24.5, Hum=60%, pH=5.2, Rain=165mm | Coffee + Acidic Soil diagnostic + Lime advisory |
| Test Case 3 | N=25, P=130, K=195, Temp=22, Hum=92%, pH=6.0, Rain=110mm | Apple recommendation |

Run interactively with `python main.py --interactive` to enter custom values.

---
