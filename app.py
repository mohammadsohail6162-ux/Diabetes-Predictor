import streamlit as st
import pandas as pd
import pickle

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="Diabetes Prediction App",
    page_icon="🩺",
    layout="centered"
)

# =====================================
# LOAD MODEL
# =====================================
model = pickle.load(open("diabetes_model.pkl", "rb"))
columns = pickle.load(open("columns.pkl", "rb"))

# =====================================
# SIDEBAR
# =====================================
st.sidebar.title("🩺 About App")
st.sidebar.info(
    """
    This Machine Learning app predicts
    the risk of diabetes based on
    patient health details.
    """
)

st.sidebar.success("Developed using Streamlit")

# =====================================
# MAIN TITLE
# =====================================
st.title("🩺 Diabetes Prediction System")
st.markdown("---")

st.write("### Enter Patient Details")

# =====================================
# INPUTS
# =====================================
col1, col2 = st.columns(2)

with col1:
    preg = st.number_input("Pregnancies", 0, 20, 1)
    glucose = st.number_input("Glucose", 50, 200, 120)
    bp = st.number_input("Blood Pressure", 30, 120, 70)
    skin = st.number_input("Skin Thickness", 0, 100, 20)

with col2:
    insulin = st.number_input("Insulin", 0, 300, 100)
    bmi = st.number_input("BMI", 10.0, 60.0, 25.0)
    dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.5)
    age = st.number_input("Age", 1, 100, 30)

st.markdown("---")

# =====================================
# BMI STATUS
# =====================================
if bmi < 18.5:
    bmi_status = "Underweight"
elif bmi < 25:
    bmi_status = "Normal"
elif bmi < 30:
    bmi_status = "Overweight"
else:
    bmi_status = "Obese"

st.info(f"📌 BMI Category: {bmi_status}")

# =====================================
# PREDICTION BUTTON
# =====================================
if st.button("🔍 Predict Diabetes"):

    # Input dataframe
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

    # =====================================
    # FEATURE ENGINEERING
    # =====================================
    input_raw['Glucose_BMI'] = input_raw['Glucose'] * input_raw['BMI']
    input_raw['Insulin_Glucose'] = input_raw['Insulin'] * input_raw['Glucose']
    input_raw['Age_BMI'] = input_raw['Age'] * input_raw['BMI']
    input_raw['BMI_Squared'] = input_raw['BMI'] ** 2

    # =====================================
    # ENCODING
    # =====================================
    input_encoded = pd.get_dummies(input_raw)

    # Match columns
    input_df = input_encoded.reindex(columns=columns, fill_value=0)

    # =====================================
    # PREDICTION
    # =====================================
    prediction = model.predict(input_df)
    probability = model.predict_proba(input_df)[0][1]

    st.markdown("---")

    # =====================================
    # RESULT
    # =====================================
    if prediction[0] == 1:
        st.error("⚠️ High Risk of Diabetes")
    else:
        st.success("✅ Low Risk of Diabetes")

    # =====================================
    # PROBABILITY
    # =====================================
    st.write(f"### 📊 Diabetes Probability: {probability*100:.2f}%")

    st.progress(float(probability))

    # =====================================
    # HEALTH TIPS
    # =====================================
    st.markdown("## 💡 Health Tips")

    if prediction[0] == 1:
        st.warning("""
        - Reduce sugar intake
        - Exercise regularly
        - Maintain healthy weight
        - Monitor blood glucose
        - Consult a doctor
        """)
    else:
        st.success("""
        - Maintain healthy lifestyle
        - Exercise regularly
        - Eat balanced diet
        - Stay hydrated
        - Regular health checkups
        """)

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption("Machine Learning Powered Diabetes Prediction App")
