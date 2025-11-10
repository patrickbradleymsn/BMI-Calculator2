import streamlit as st

# -----------------------------
# Helpers
# -----------------------------
LBS_TO_KG = 0.45359237
IN_TO_M = 0.0254

CATEGORY_BOUNDS = [
    (0, 18.5, "Underweight", "#60a5fa", "🪁"),
    (18.5, 25, "Normal weight", "#34d399", "🥑"),
    (25, 30, "Overweight", "#f59e0b", "🍯"),
    (30, float('inf'), "Obesity", "#ef4444", "🍰"),
]

def to_metric(feet: int, inches: int, lbs: float):
    total_inches = max((feet * 12) + inches, 1)  # avoid zero height
    height_m = total_inches * IN_TO_M
    weight_kg = lbs * LBS_TO_KG
    return height_m, weight_kg

def calculate_bmi(height_m: float, weight_kg: float):
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)

def bmi_category(bmi: float):
    for lo, hi, name, color, emoji in CATEGORY_BOUNDS:
        if lo <= bmi < hi:
            return {"name": name, "color": color, "emoji": emoji}
    # Fallback (shouldn't hit)
    return {"name": "Unknown", "color": "#6b7280", "emoji": "❓"}

def healthy_weight_range_lbs(height_m: float):
    # Normal BMI range 18.5–24.9
    low_kg = 18.5 * (height_m ** 2)
    high_kg = 24.9 * (height_m ** 2)
    low_lbs = low_kg / LBS_TO_KG
    high_lbs = high_kg / LBS_TO_KG
    return round(low_lbs), round(high_lbs)

INSIGHTS = {
    "Underweight": {
        "blurb": "Your BMI suggests you may be under the typical range for most adults.",
        "tips": [
            "Aim for nutrient-dense add-ons: nut butters, olive oil, seeds, and full‑fat yogurt.",
            "Include resistance training 2–3×/week to support lean mass.",
            "Discuss unintentional weight loss or appetite changes with a clinician.",
        ],
    },
    "Normal weight": {
        "blurb": "Nice balance! Your BMI lands in the generally healthy range.",
        "tips": [
            "Keep a steady activity mix: 150+ minutes/week of moderate activity plus strength training.",
            "Prioritize sleep (7–9 hrs) and fiber (25–35g/day).",
            "Annual wellness checks are still a win—prevention > correction.",
        ],
    },
    "Overweight": {
        "blurb": "Your BMI is above the typical range for most adults.",
        "tips": [
            "Start with small, durable adjustments: +1 veggie serving and +10 minutes of walking daily.",
            "Strength training helps preserve muscle while changing body composition.",
            "Consider tracking added sugars and liquid calories for two weeks to spot easy wins.",
        ],
    },
    "Obesity": {
        "blurb": "Your BMI is in a range associated with higher health risks for many people.",
        "tips": [
            "Combine nutrition tweaks with progressive strength + brisk walking 3–5×/week.",
            "Discuss options with your clinician—personalized guidance (including medications) may help.",
            "Focus on habit stacking: pair an existing routine (morning coffee) with a 10‑minute walk.",
        ],
    },
}

# -----------------------------
# Page config & fun styling
# -----------------------------
st.set_page_config(page_title="Playful BMI Calculator (lbs/ft/in)", page_icon="🧮", layout="centered")

st.markdown(
    """
    <style>
      .bmi-card { 
        background: linear-gradient(135deg, #f8fafc, #eef2ff);
        border: 1px solid #e5e7eb; padding: 1rem 1.25rem; border-radius: 1rem; 
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
      }
      .pill { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 999px; font-weight:600; }
      .footer { color:#6b7280; font-size: 0.85rem; }
      .gauge { display:flex; height:16px; border-radius:999px; overflow:hidden; border:1px solid #e5e7eb; }
      .seg { flex:1; }
      .seg.u { background:#60a5fa55; }
      .seg.n { background:#34d39955; }
      .seg.o { background:#f59e0b55; }
      .seg.b { background:#ef444455; }
      .marker { position:relative; height:0; }
      .pin { position:absolute; top:-6px; width:2px; height:28px; background:#111827; border-radius:2px; }
      .ticks { display:flex; justify-content:space-between; font-size:12px; color:#6b7280; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Playful BMI Calculator 🧮✨")
st.caption("Enter height in feet/inches and weight in pounds. We'll convert under the hood and add friendly guidance.")

# -----------------------------
# Inputs
# -----------------------------
col1, col2 = st.columns([1,1])
with col1:
    st.subheader("Height")
    feet = st.number_input("Feet", min_value=3, max_value=8, value=5)
    inches = st.number_input("Inches", min_value=0, max_value=11, value=7)
with col2:
    st.subheader("Weight")
    lbs = st.number_input("Pounds (lb)", min_value=1.0, value=165.0, step=0.5)

# Fun micro‑emoji row
st.write("Height & Weight locked? ", "🔐" if lbs and feet else "🔓")

# -----------------------------
# Calculate
# -----------------------------
if st.button("Calculate BMI 🎯", use_container_width=True):
    h_m, w_kg = to_metric(feet, inches, lbs)
    bmi = calculate_bmi(h_m, w_kg)
    cat = bmi_category(bmi)
    low_w, high_w = healthy_weight_range_lbs(h_m)

    # Card summary
    st.markdown(f"<div class='bmi-card'>", unsafe_allow_html=True)
    st.subheader(f"{cat['emoji']}  Your BMI: **{bmi}**")
    st.markdown(
        f"<span class='pill' style='background:{cat['color']}22; color:{cat['color']}; border:1px solid {cat['color']}55'>Category: {cat['name']}</span>",
        unsafe_allow_html=True,
    )

    # --- HTML/CSS gauge (no matplotlib) ---
    # normalize to 10–40
    norm = min(max((bmi - 10) / 30, 0), 1)
    st.markdown(
        """
        <div class='gauge'>
          <div class='seg u' style='flex:8.5'></div>
          <div class='seg n' style='flex:6.5'></div>
          <div class='seg o' style='flex:5'></div>
          <div class='seg b' style='flex:10'></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(norm)
    st.markdown(
        """
        <div class='ticks'>
           <span>10</span><span>18.5</span><span>25</span><span>30</span><span>40</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Healthy weight bounds for this height
    st.markdown(
        f"**For your height**, a weight between **{low_w}–{high_w} lb** corresponds to a BMI of 18.5–24.9.")

    # Insights & tips
    info = INSIGHTS[cat["name"]]
    st.markdown("---")
    st.markdown(f"### {cat['emoji']} Insights")
    st.write(info["blurb"])
    st.markdown("#### Tips you can try this week")
    for tip in info["tips"]:
        st.markdown(f"- {tip}")

    # Notes
    st.markdown("---")
    st.markdown(
        """
        <div class='footer'>
        ⚠️ BMI is a simple screening tool and doesn't directly measure body fat, health status, or distribution. 
        Training level, age, ethnicity, and body composition matter. For personalized guidance, talk with your clinician.
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.info("Enter your height and weight, then click **Calculate BMI 🎯**.")
