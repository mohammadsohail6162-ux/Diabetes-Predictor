# =========================================================
# ADVANCED AI DIABETES PREDICTION SYSTEM
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime
from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Diabetes Risk Analyzer",
    page_icon="🩺",
    layout="wide"
)

# =========================================================
# PREMIUM CYBERPUNK UI
# =========================================================
st.markdown("""
<style>

/* =======================================================
BACKGROUND
======================================================= */

.stApp {
    background: linear-gradient(
        135deg,
        #020617,
        #0f172a,
        #111827
    );
    color: white;
}

/* =======================================================
MAIN CONTAINER
======================================================= */

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* =======================================================
HEADINGS
======================================================= */

h1 {
    color: #00e5ff;
    text-align: center;
    font-weight: 800;
    text-shadow: 0px 0px 15px #00e5ff;
}

h2, h3 {
    color: white;
}

/* =======================================================
GLASS CARD
======================================================= */

.glass-card {

    background: rgba(255,255,255,0.08);

    border-radius: 20px;

    padding: 25px;

    backdrop-filter: blur(10px);

    border: 1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 8px 32px rgba(0,0,0,0.35);

    transition: 0.3s;
}

.glass-card:hover {

    transform: translateY(-5px);

    box-shadow:
        0 0 25px rgba(0,229,255,0.5);
}

/* =======================================================
BUTTONS
======================================================= */

.stButton > button {

    width: 100%;

    background: linear-gradient(
        90deg,
        #00e5ff,
        #7c3aed
    );

    color: white;

    border-radius: 15px;

    height: 3.5em;

    border: none;

    font-size: 18px;

    font-weight: bold;

    transition: 0.3s;

    box-shadow:
        0 0 15px rgba(0,229,255,0.5);
}

.stButton > button:hover {

    transform: scale(1.02);

    box-shadow:
        0 0 30px rgba(124,58,237,0.8);
}

/* =======================================================
METRICS
======================================================= */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.08);

    border-radius: 20px;

    padding: 15px;

    border: 1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 4px 20px rgba(0,0,0,0.3);
}

/* =======================================================
SIDEBAR
======================================================= */

section[data-testid="stSidebar"] {

    background: linear-gradient(
        180deg,
        #111827,
        #020617
    );
}

/* =======================================================
INPUT FIELDS
======================================================= */

.stTextInput input,
.stNumberInput input {

    background-color: rgba(255,255,255,0.08) !important;

    color: white !important;

    border-radius: 10px !important;
}

/* =======================================================
METRIC CARD
======================================================= */

.metric-card {

    background: rgba(255,255,255,0.08);

    border-radius: 20px;

    padding: 20px;

    text-align: center;

    backdrop-filter: blur(8px);

    border: 1px solid rgba(255,255,255,0.08);

    animation: glow 3s infinite;
}

@keyframes glow {

    0% {
        box-shadow: 0 0 5px #00e5ff;
    }

    50% {
        box-shadow: 0 0 20px #7c3aed;
    }

    100% {
        box-shadow: 0 0 5px #00e5ff;
    }
}

.big-font {

    font-size: 24px !important;

    font-weight: bold;

    color: white;
}

/* =======================================================
FOOTER
======================================================= */

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD MODEL
# =========================================================
model = pickle.load(open("diabetes_model.pkl", "rb"))
columns = pickle.load(open("columns.pkl", "rb"))

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🩺 AI Health Dashboard")

st.sidebar.info("""
AI-Powered Healthcare Analytics Platform
for Diabetes Risk Prediction.
""")

st.sidebar.markdown("---")

patient_name = st.sidebar.text_input(
    "👤 Patient Name"
)

gender = st.sidebar.selectbox(
    "⚧ Gender",
    ["Male", "Female"]
)

date = st.sidebar.date_input(
    "📅 Date",
    datetime.today()
)

st.sidebar.success("✅ System Ready")

# =========================================================
# TITLE
# =========================================================
st.markdown("""
<h1>
🧠 AI Diabetes Risk Prediction System
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div class="glass-card">

<h3 style="text-align:center;">
🚀 Smart Healthcare Analytics Dashboard
</h3>

<p style="text-align:center; color:lightgray;">
AI-Powered Medical Intelligence Platform
</p>

</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# INPUT SECTION
# =========================================================
left, right = st.columns([2, 1])

with left:

    st.subheader("📋 Enter Medical Details")

    c1, c2, c3 = st.columns(3)

    # =====================================================
    # COLUMN 1
    # =====================================================
    with c1:

        if gender == "Female":

            preg = st.number_input(
                "Pregnancies",
                min_value=0,
                max_value=20,
                value=1
            )

        else:

            preg = 0

            st.info(
                "Pregnancies not applicable"
            )

        glucose = st.slider(
            "Glucose",
            50,
            250,
            120
        )

    # =====================================================
    # COLUMN 2
    # =====================================================
    with c2:

        bp = st.slider(
            "Blood Pressure",
            40,
            150,
            70
        )

        skin = st.slider(
            "Skin Thickness",
            0,
            100,
            20
        )

    # =====================================================
    # COLUMN 3
    # =====================================================
    with c3:

        insulin = st.slider(
            "Insulin",
            0,
            400,
            100
        )

        age = st.slider(
            "Age",
            1,
            100,
            30
        )

    bmi = st.slider(
        "BMI",
        10.0,
        60.0,
        25.0
    )

    dpf = st.slider(
        "Diabetes Pedigree Function",
        0.0,
        3.0,
        0.5
    )

# =========================================================
# RIGHT PANEL
# =========================================================
with right:

    st.subheader("📊 Live Health Metrics")

    st.metric("Glucose", glucose)
    st.metric("BMI", bmi)
    st.metric("Blood Pressure", bp)
    st.metric("Age", age)

# =========================================================
# BMI CATEGORY
# =========================================================
if bmi < 18.5:

    bmi_status = "Underweight"
    bmi_color = "blue"

elif bmi < 25:

    bmi_status = "Normal"
    bmi_color = "green"

elif bmi < 30:

    bmi_status = "Overweight"
    bmi_color = "orange"

else:

    bmi_status = "Obese"
    bmi_color = "red"

st.markdown(f"""
<div class="metric-card">

<p class="big-font">
BMI Category
</p>

<h2 style='color:{bmi_color};'>
{bmi_status}
</h2>

</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# PREDICTION
# =========================================================
if st.button("🚀 Run AI Prediction"):

    # =====================================================
    # INPUT DATAFRAME
    # =====================================================
    input_raw = pd.DataFrame({

        'Pregnancies': [preg],
        'Glucose': [glucose],
        'BloodPressure': [bp],
        'SkinThickness': [skin],
        'Insulin': [insulin],
        'BMI': [bmi],
        'DiabetesPedigreeFunction': [dpf],
        'Age': [age]
    })

    # =====================================================
    # FEATURE ENGINEERING
    # =====================================================
    input_raw['Glucose_BMI'] = (
        input_raw['Glucose'] * input_raw['BMI']
    )

    input_raw['Insulin_Glucose'] = (
        input_raw['Insulin'] * input_raw['Glucose']
    )

    input_raw['Age_BMI'] = (
        input_raw['Age'] * input_raw['BMI']
    )

    input_raw['BMI_Squared'] = (
        input_raw['BMI'] ** 2
    )

    # =====================================================
    # ENCODING
    # =====================================================
    input_encoded = pd.get_dummies(input_raw)

    input_df = input_encoded.reindex(
        columns=columns,
        fill_value=0
    )

    # =====================================================
    # PREDICTION
    # =====================================================
    prediction = model.predict(input_df)[0]

    probability = model.predict_proba(input_df)[0][1]

    # =====================================================
    # RESULT LABEL
    # =====================================================
    if prediction == 1:

        result_label = "High Risk of Diabetes"

    else:

        result_label = "Low Risk of Diabetes"

    # =====================================================
    # HEALTH SCORE
    # =====================================================
    health_score = int(100 - (probability * 100))

    # =====================================================
    # RESULT SECTION
    # =====================================================
    colA, colB = st.columns(2)

    with colA:

        if prediction == 1:

            st.error(
                "⚠️ HIGH RISK OF DIABETES"
            )

        else:

            st.success(
                "✅ LOW RISK OF DIABETES"
            )

        st.write(
            f"### 🎯 Prediction Confidence: "
            f"{probability*100:.2f}%"
        )

        st.write(
            f"### ❤️ Health Score: "
            f"{health_score}/100"
        )

        if probability < 0.30:

            st.success("🟢 Low Risk")

        elif probability < 0.70:

            st.warning("🟡 Medium Risk")

        else:

            st.error("🔴 High Risk")

    # =====================================================
    # GAUGE CHART
    # =====================================================
    with colB:

        fig = go.Figure(go.Indicator(

            mode="gauge+number",

            value=probability * 100,

            title={'text': "Diabetes Risk %"},

            gauge={

                'axis': {'range': [0, 100]},

                'steps': [

                    {
                        'range': [0, 30],
                        'color': "green"
                    },

                    {
                        'range': [30, 70],
                        'color': "orange"
                    },

                    {
                        'range': [70, 100],
                        'color': "red"
                    }
                ]
            }
        ))

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("---")

    # =====================================================
    # ANALYTICS
    # =====================================================
    st.subheader("📈 Health Analytics")

    analytics_df = pd.DataFrame({

        "Feature": [
            "Glucose",
            "Blood Pressure",
            "BMI",
            "Insulin",
            "Age"
        ],

        "Value": [
            glucose,
            bp,
            bmi,
            insulin,
            age
        ]
    })

    fig2 = px.bar(

        analytics_df,

        x="Feature",

        y="Value",

        text="Value",

        title="Patient Health Parameters"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================
    st.subheader("💡 AI Health Recommendations")

    if prediction == 1:

        st.warning("""
        ### Recommended Actions

        - Reduce sugar intake
        - Daily exercise
        - Weight management
        - Regular glucose monitoring
        - Consult a diabetologist
        - Drink more water
        """)

    else:

        st.success("""
        ### Healthy Lifestyle Tips

        - Maintain balanced diet
        - Exercise regularly
        - Sleep properly
        - Drink enough water
        - Regular health checkup
        """)

    # =====================================================
    # PDF REPORT
    # =====================================================
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "<b>AI Diabetes Medical Report</b>",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    # =====================================================
    # PATIENT TABLE
    # =====================================================
    patient_info = [

        ["Patient Name", patient_name],

        ["Gender", gender],

        ["Date", str(date)]
    ]

    patient_table = Table(
        patient_info,
        colWidths=[200, 250]
    )

    patient_table.setStyle(TableStyle([

        ('BACKGROUND',
         (0, 0),
         (-1, -1),
         colors.lightblue),

        ('GRID',
         (0, 0),
         (-1, -1),
         1,
         colors.black),

        ('FONTNAME',
         (0, 0),
         (-1, -1),
         'Helvetica-Bold')
    ]))

    elements.append(patient_table)
    elements.append(Spacer(1, 20))

    # =====================================================
    # RESULT TEXT
    # =====================================================
    result_text = f"""
    <b>Prediction Result:</b>
    {result_label}<br/><br/>

    <b>Prediction Confidence:</b>
    {probability*100:.2f}%<br/><br/>

    <b>Health Score:</b>
    {health_score}/100<br/><br/>

    <b>BMI Category:</b>
    {bmi_status}
    """

    result_para = Paragraph(
        result_text,
        styles['BodyText']
    )

    elements.append(result_para)

    # =====================================================
    # BUILD PDF
    # =====================================================
    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    # =====================================================
    # DOWNLOAD BUTTON
    # =====================================================
    st.download_button(

        label="📄 Download Full PDF Report",

        data=pdf,

        file_name="AI_Diabetes_Report.pdf",

        mime="application/pdf"
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.caption(
    "🚀 Advanced AI Diabetes Prediction "
    "System using Machine Learning + Streamlit"
)
