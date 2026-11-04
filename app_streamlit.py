"""
app_streamlit.py
----------------
Simple form-based Streamlit frontend for the Rule-Based Crop Expert System.
Type your farm values, press the button, read the result.
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import streamlit as st
from engine.inference_engine import ForwardChainingEngine
from knowledge_base import get_complete_knowledge_base

ALL_CROPS = [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans",
    "mungbean", "blackgram", "lentil", "pomegranate", "banana", "mango",
    "grapes", "watermelon", "muskmelon", "apple", "orange", "papaya",
    "coconut", "cotton", "jute", "coffee",
]


def main():
    st.set_page_config(page_title="Crop Advisor", page_icon="🌾", layout="centered")

    st.markdown("""
    <style>
        .block-container { max-width: 760px; padding-top: 2.5rem; }
        h1 { text-align: center; margin-bottom: 0; }
        .subtitle { text-align: center; color: #64748b; margin-bottom: 1.8rem; }
        .result-card {
            background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 14px;
            padding: 20px 24px; margin: 1rem 0;
        }
        .result-card h2 { margin: 0; color: #166534; }
        .result-card .cf { color: #15803d; font-weight: 600; }
        .nomatch-card {
            background: #fffbeb; border: 1px solid #fde68a; border-radius: 14px;
            padding: 20px 24px; margin: 1rem 0; color: #92400e;
        }
        .chip {
            display: inline-block; background: #e2e8f0; color: #334155;
            border-radius: 9999px; padding: 3px 12px; margin: 2px 4px 2px 0;
            font-size: 0.85rem;
        }
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            width: 100%; background: #16a34a; color: white; border: none;
            border-radius: 10px; padding: 0.6rem 0; font-weight: 600;
        }
        div[data-testid="stFormSubmitButton"] > button:hover { background: #15803d; color: white; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌾 Crop Advisor")
    st.markdown('<div class="subtitle">Enter your soil and weather details to get a crop recommendation.</div>',
                unsafe_allow_html=True)

    with st.form("farm_form"):
        st.markdown("**Soil nutrients (kg/ha)**")
        c1, c2, c3 = st.columns(3)
        n = c1.number_input("Nitrogen (N)", min_value=0.0, max_value=200.0, value=None,
                            placeholder="e.g. 90", step=1.0)
        p = c2.number_input("Phosphorus (P)", min_value=0.0, max_value=200.0, value=None,
                            placeholder="e.g. 42", step=1.0)
        k = c3.number_input("Potassium (K)", min_value=0.0, max_value=250.0, value=None,
                            placeholder="e.g. 43", step=1.0)

        st.markdown("**Climate & soil**")
        c4, c5 = st.columns(2)
        temp = c4.number_input("Temperature (°C)", min_value=0.0, max_value=55.0, value=None,
                               placeholder="e.g. 21", step=0.1)
        hum = c5.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=None,
                              placeholder="e.g. 82", step=0.5)
        c6, c7 = st.columns(2)
        ph = c6.number_input("Soil pH", min_value=0.0, max_value=14.0, value=None,
                             placeholder="e.g. 6.5", step=0.1)
        rain = c7.number_input("Rainfall (mm)", min_value=0.0, max_value=400.0, value=None,
                               placeholder="e.g. 200", step=1.0)

        why_not = st.selectbox("Check why this crop was not chosen (optional)",
                               options=["None"] + [c.capitalize() for c in ALL_CROPS])

        submitted = st.form_submit_button("Get Recommendation")

    if submitted:
        values = {"N": n, "P": p, "K": k, "temperature": temp,
                  "humidity": hum, "ph": ph, "rainfall": rain}
        missing = [name for name, v in values.items() if v is None]
        if missing:
            st.error("Please fill in: " + ", ".join(missing))
            st.stop()

        engine = ForwardChainingEngine(get_complete_knowledge_base())
        engine.load_user_inputs(values)
        results = engine.run()

        primary = results["primary_recommendation"]
        alternatives = results["alternative_candidates"]
        diagnostics = results["soil_diagnostics"]
        remedies = results["corrective_actions"]

        st.markdown("---")

        if primary:
            crop = primary["name"].replace(" Suitability", "")
            st.markdown(
                f'<div class="result-card"><div>Recommended crop</div>'
                f'<h2>{crop}</h2>'
                f'<div class="cf">Confidence: {primary["certainty"]:.0%}</div>'
                f'<p style="margin:8px 0 0">{primary["description"]}</p></div>',
                unsafe_allow_html=True)
            if alternatives:
                chips = "".join(
                    f'<span class="chip">{a["name"].replace(" Suitability", "")} · {a["certainty"]:.0%}</span>'
                    for a in alternatives)
                st.markdown(f"**Other options:** {chips}", unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="nomatch-card"><b>No crop matched.</b> Your values do not fit '
                'any single crop\'s range. See the soil advice below and the "why not" details.</div>',
                unsafe_allow_html=True)

        if diagnostics:
            st.subheader("Soil health")
            for d in diagnostics:
                st.warning(f"**{d['name'].replace(' Diagnostic', '')}** — {d['description']}")

        if remedies:
            st.subheader("Recommended actions")
            for r in remedies:
                a = r["output"]
                st.info(f"**{r['name']}**\n\n{a['recommendation']}\n\n_Goal: {a['target']}_")

        st.markdown("---")
        with st.expander("How was this decided?"):
            st.markdown(engine.explain())

        if why_not != "None":
            with st.expander(f"Why not {why_not}?", expanded=True):
                st.markdown(engine.explain_why_not(why_not.lower()))


main()
