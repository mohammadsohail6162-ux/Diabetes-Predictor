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
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(to right, #00c6ff, #0072ff);
    color: white;
    border-radius: 10px;
    height: 3em;
    border: none;
    font-size: 18px;
    font-weight: bold;
}

.metric-card {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}

.big-font {
    font-size: 22px !important;
    font-weight: bold;
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
This AI-powered application predicts
diabetes risk using Machine Learning.
""")

st.sidebar.markdown("---")

patient_name = st.sidebar.text_input("👤 Patient Name")
gender = st.sidebar.selectbox("⚧ Gender", ["Male", "Female"])
date = st.sidebar.date_input("📅 Date", datetime.today())

st.sidebar.success("✅ System Ready")

# =========================================================
# TITLE
# =========================================================
st.title("🧠 AI Diabetes Risk Prediction System")
st.markdown("### Smart Healthcare Analytics Dashboard")

st.markdown("---")

# =========================================================
# INPUT SECTION
# =========================================================
left, right = st.columns([2, 1])

with left:

    st.subheader("📋 Enter Medical Details")

    c1, c2, c3 = st.columns(3)

    with c1:

    # Show pregnancies only for female
    if gender == "Female":
        preg = st.number_input(
            "Pregnancies",
            min_value=0,
            max_value=20,
            value=1
        )
    else:
        preg = 0
        st.info("Pregnancies not applicable for male patients")

    glucose = st.slider(
        "Glucose",
        50,
        250,
        120
    )

    with c2:
        bp = st.slider("Blood Pressure", 40, 150, 70)
        skin = st.slider("Skin Thickness", 0, 100, 20)

    with c3:
        insulin = st.slider("Insulin", 0, 400, 100)
        age = st.slider("Age", 1, 100, 30)

    bmi = st.slider("BMI", 10.0, 60.0, 25.0)
    dpf = st.slider("Diabetes Pedigree Function", 0.0, 3.0, 0.5)

with right:

    st.subheader("📊 Live Metrics")

    st.metric("Glucose", glucose)
    st.metric("BMI", bmi)
    st.metric("Blood Pressure", bp)
    st.metric("Age", age)

# =========================================================
# BMI STATUS
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
    <p class="big-font">BMI Category</p>
    <h2 style='color:{bmi_color};'>{bmi_status}</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# PREDICTION BUTTON
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
    input_raw['Glucose_BMI'] = input_raw['Glucose'] * input_raw['BMI']
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

    # =====================================================
    # MATCH TRAINING COLUMNS
    # =====================================================
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
    # RESULT SECTION
    # =====================================================
    colA, colB = st.columns(2)

    with colA:

        if prediction == 1:
            st.error("⚠️ HIGH RISK OF DIABETES")
        else:
            st.success("✅ LOW RISK OF DIABETES")

        st.write(
            f"### 🎯 Prediction Confidence: "
            f"{probability*100:.2f}%"
        )

        # Risk level
        if probability < 0.30:
            st.success("🟢 Low Risk")

        elif probability < 0.70:
            st.warning("🟡 Medium Risk")

        else:
            st.error("🔴 High Risk")

    with colB:

        # =================================================
        # GAUGE CHART
        # =================================================
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=probability * 100,

            title={'text': "Diabetes Risk %"},

            gauge={
                'axis': {'range': [0, 100]},

                'steps': [
                    {'range': [0, 30], 'color': "green"},
                    {'range': [30, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "red"}
                ]
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # =====================================================
    # ANALYTICS CHART
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

    st.plotly_chart(fig2, use_container_width=True)

    # =====================================================
    # HEALTH RECOMMENDATIONS
    # =====================================================
    st.subheader("💡 AI Health Recommendations")

    if prediction == 1:

        st.warning("""
        ### Recommended Actions
        - Reduce sugar intake
        - Daily exercise
        - Weight management
        - Regular glucose monitoring
        - Consult a doctor
        """)

    else:

        st.success("""
        ### Healthy Lifestyle Tips
        - Maintain healthy diet
        - Exercise regularly
        - Drink enough water
        - Sleep properly
        - Regular health checkup
        """)

    # =====================================================
    # PDF REPORT GENERATION
    # =====================================================
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    # =====================================================
    # TITLE
    # =====================================================
    title = Paragraph(
        "<b>AI Diabetes Prediction Medical Report</b>",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    # =====================================================
    # PATIENT INFO TABLE
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
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold')
    ]))

    elements.append(patient_table)
    elements.append(Spacer(1, 20))

    # =====================================================
    # MEDICAL DATA TABLE
    # =====================================================
    medical_data = [
        ["Parameter", "Value"],
        ["Pregnancies", preg],
        ["Glucose", glucose],
        ["Blood Pressure", bp],
        ["Skin Thickness", skin],
        ["Insulin", insulin],
        ["BMI", bmi],
        ["DPF", dpf],
        ["Age", age]
    ]

    medical_table = Table(
        medical_data,
        colWidths=[200, 250]
    )

    medical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica')
    ]))

    elements.append(medical_table)
    elements.append(Spacer(1, 20))

    # =====================================================
    # RESULT TEXT
    # =====================================================
    result_text = f"""
    <b>Prediction Result:</b> {result_label}<br/><br/>
    <b>Prediction Confidence:</b> {probability*100:.2f}%<br/><br/>
    <b>BMI Category:</b> {bmi_status}
    """

    result_para = Paragraph(
        result_text,
        styles['BodyText']
    )

    elements.append(result_para)
    elements.append(Spacer(1, 20))

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================
    recommendation = """
    <b>Health Recommendations:</b><br/>
    - Exercise regularly<br/>
    - Maintain balanced diet<br/>
    - Drink enough water<br/>
    - Regular health checkup
    """

    recommendation_para = Paragraph(
        recommendation,
        styles['BodyText']
    )

    elements.append(recommendation_para)

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
        label="📄 Download Full Medical PDF Report",
        data=pdf,
        file_name="AI_Diabetes_Report.pdf",
        mime="application/pdf"
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.caption(
    "🚀 Advanced AI Diabetes Prediction System "
    "using Machine Learning + Streamlit"
)
