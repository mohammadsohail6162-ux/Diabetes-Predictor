import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Diabetes Risk Analyzer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.stButton>button {
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
    box-shadow: 0px 0px 10px rgba(0,0,0,0.5);
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
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/2966/2966486.png",
    width=120
)

st.sidebar.title("🩺 AI Health Dashboard")

st.sidebar.info("""
This AI-powered application predicts
the probability of diabetes using
Machine Learning techniques.
""")

st.sidebar.markdown("---")

st.sidebar.write("### 👨‍⚕️ Patient Information")

patient_name = st.sidebar.text_input("Patient Name")
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
date = st.sidebar.date_input("Date", datetime.today())

st.sidebar.markdown("---")
st.sidebar.success("System Ready ✅")

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

    col1, col2, col3 = st.columns(3)

    with col1:
        preg = st.number_input("Pregnancies", 0, 20, 1)
        glucose = st.slider("Glucose", 50, 250, 120)

    with col2:
        bp = st.slider("Blood Pressure", 40, 150, 70)
        skin = st.slider("Skin Thickness", 0, 100, 20)

    with col3:
        insulin = st.slider("Insulin", 0, 400, 100)
        age = st.slider("Age", 1, 100, 30)

    bmi = st.slider("BMI", 10.0, 60.0, 25.0)
    dpf = st.slider("Diabetes Pedigree Function", 0.0, 3.0, 0.5)

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
    <p class="big-font">BMI Category</p>
    <h2 style='color:{bmi_color};'>{bmi_status}</h2>
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
    input_raw['Glucose_BMI'] = input_raw['Glucose'] * input_raw['BMI']
    input_raw['Insulin_Glucose'] = input_raw['Insulin'] * input_raw['Glucose']
    input_raw['Age_BMI'] = input_raw['Age'] * input_raw['BMI']
    input_raw['BMI_Squared'] = input_raw['BMI'] ** 2

    # =====================================================
    # ENCODING
    # =====================================================
    input_encoded = pd.get_dummies(input_raw)

    # =====================================================
    # MATCH TRAINING COLUMNS
    # =====================================================
    input_df = input_encoded.reindex(columns=columns, fill_value=0)

    # =====================================================
    # PREDICTION
    # =====================================================
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]

    st.markdown("---")

    # =====================================================
    # RESULT SECTION
    # =====================================================
    colA, colB = st.columns(2)

    with colA:

        if prediction == 1:
            st.error("⚠️ HIGH RISK OF DIABETES")
        else:
            st.success("✅ LOW RISK OF DIABETES")

        st.write(f"### 🎯 Prediction Confidence: {probability*100:.2f}%")

        # =================================================
        # RISK LEVEL
        # =================================================
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
                'bar': {'color': "red"},
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
    # HEALTH ANALYTICS
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
        ### Recommended Actions:
        - Reduce sugar intake
        - Daily physical exercise
        - Weight management
        - Regular glucose monitoring
        - Consult a diabetologist
        - Increase water intake
        """)

    else:

        st.success("""
        ### Healthy Lifestyle Tips:
        - Continue healthy diet
        - Maintain proper sleep
        - Regular exercise
        - Avoid excessive sugar
        - Annual health checkup
        """)

    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================
    report = pd.DataFrame({
        "Parameter": [
            "Patient Name",
            "Gender",
            "Glucose",
            "Blood Pressure",
            "BMI",
            "Age",
            "Prediction",
            "Probability"
        ],
        "Value": [
            patient_name,
            gender,
            glucose,
            bp,
            bmi,
            age,
            "High Risk" if prediction == 1 else "Low Risk",
            f"{probability*100:.2f}%"
        ]
    })

    csv = report.to_csv(index=False)

    st.download_button(
        label="📥 Download Medical Report",
        data=csv,
        file_name="diabetes_report.csv",
        mime="text/csv"
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.caption("🚀 Advanced AI Diabetes Prediction System using Machine Learning + Streamlit")
