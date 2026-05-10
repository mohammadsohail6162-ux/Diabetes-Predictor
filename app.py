# =========================================================
# AI DIABETES PREDICTION SYSTEM
# COMPLETE FINAL CODE
# =========================================================
# Run:
# streamlit run app.py
#
# IMPORTANT:
# Keep these files in same folder:
# 1. diabetes_model.pkl
# 2. columns.pkl
#
# FIRST TIME:
# Delete old users.db file
# =========================================================

import streamlit as st
import pandas as pd
import pickle
import sqlite3
import hashlib

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
    page_title="AI Diabetes Prediction System",
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
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect(
    "users.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =========================================================
# USERS TABLE
# =========================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,
    email TEXT UNIQUE,
    password TEXT

)

""")

# =========================================================
# PATIENTS TABLE
# =========================================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS patients (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_name TEXT,
    gender TEXT,
    date TEXT,

    pregnancies INTEGER,
    glucose INTEGER,
    blood_pressure INTEGER,
    skin_thickness INTEGER,
    insulin INTEGER,

    bmi REAL,
    dpf REAL,
    age INTEGER,

    prediction TEXT,
    probability REAL,

    created_by TEXT

)

""")

conn.commit()

# =========================================================
# LOAD MODEL
# =========================================================

model = pickle.load(
    open("diabetes_model.pkl", "rb")
)

columns = pickle.load(
    open("columns.pkl", "rb")
)

# =========================================================
# HASH PASSWORD
# =========================================================

def make_hash(password):

    return hashlib.sha256(
        str.encode(password)
    ).hexdigest()

# =========================================================
# LOGIN FUNCTION
# =========================================================

def login_user(email, password):

    cursor.execute(

        "SELECT * FROM users WHERE email=? AND password=?",

        (
            email,
            make_hash(password)
        )

    )

    data = cursor.fetchone()

    return data

# =========================================================
# SIGNUP FUNCTION
# =========================================================

def signup_user(username, email, password):

    cursor.execute(

        "INSERT INTO users(username, email, password) VALUES (?, ?, ?)",

        (
            username,
            email,
            make_hash(password)
        )

    )

    conn.commit()

# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

if "user_email" not in st.session_state:

    st.session_state.user_email = ""

# =========================================================
# LOGIN / SIGNUP PAGE
# =========================================================

if st.session_state.logged_in == False:

    st.title("🩺 AI Diabetes Prediction System")

    menu = ["Login", "Create Account"]

    choice = st.sidebar.selectbox(
        "Menu",
        menu
    )

    # =====================================================
    # LOGIN PAGE
    # =====================================================

    if choice == "Login":

        st.subheader("🔐 User Login")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            cursor.execute(

                "SELECT * FROM users WHERE email=?",

                (email,)

            )

            existing_user = cursor.fetchone()

            if existing_user is None:

                st.error(
                    "User does not exist"
                )

                st.info(
                    "Please create account first"
                )

            else:

                result = login_user(
                    email,
                    password
                )

                if result:

                    st.success(
                        "Login Successful"
                    )

                    st.session_state.logged_in = True

                    st.session_state.user_email = email

                    st.rerun()

                else:

                    st.error(
                        "Incorrect Password"
                    )

    # =====================================================
    # CREATE ACCOUNT
    # =====================================================

    elif choice == "Create Account":

        st.subheader("📝 Create Account")

        new_user = st.text_input(
            "Username"
        )

        new_email = st.text_input(
            "Email"
        )

        new_password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Create Account"):

            if (

                new_user == ""
                or new_email == ""
                or new_password == ""
                or confirm_password == ""

            ):

                st.warning(
                    "Please fill all fields"
                )

            elif new_password != confirm_password:

                st.error(
                    "Passwords do not match"
                )

            else:

                cursor.execute(

                    "SELECT * FROM users WHERE email=?",

                    (new_email,)

                )

                existing_user = cursor.fetchone()

                if existing_user:

                    st.error(
                        "Account already exists"
                    )

                else:

                    signup_user(

                        new_user,
                        new_email,
                        new_password

                    )

                    st.success(
                        "Account Created Successfully"
                    )

                    st.info(
                        "Now login using your account"
                    )

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🩺 AI Dashboard")

st.sidebar.success(
    f"Logged in as: {st.session_state.user_email}"
)

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False

    st.session_state.user_email = ""

    st.rerun()

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

# =========================================================
# TITLE
# =========================================================

st.title("🧠 AI Diabetes Risk Prediction System")

st.markdown(
    "### Smart Healthcare Analytics Dashboard"
)

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
                "Pregnancies not applicable for male patients"
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

    # =====================================================
    # OTHER INPUTS
    # =====================================================

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

    input_encoded = pd.get_dummies(
        input_raw
    )

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

    prediction = model.predict(
        input_df
    )[0]

    probability = model.predict_proba(
        input_df
    )[0][1]

    # =====================================================
    # RESULT LABEL
    # =====================================================

    if prediction == 1:

        result_label = "High Risk of Diabetes"

    else:

        result_label = "Low Risk of Diabetes"

    # =====================================================
    # SAVE TO DATABASE
    # =====================================================

    cursor.execute("""

    INSERT INTO patients (

        patient_name,
        gender,
        date,

        pregnancies,
        glucose,
        blood_pressure,
        skin_thickness,
        insulin,

        bmi,
        dpf,
        age,

        prediction,
        probability,
        created_by

    )

    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        patient_name,
        gender,
        str(date),

        preg,
        glucose,
        bp,
        skin,
        insulin,

        bmi,
        dpf,
        age,

        result_label,
        float(probability),

        st.session_state.user_email

    ))

    conn.commit()

    # =====================================================
    # RESULT DISPLAY
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        if prediction == 1:

            st.error(
                "⚠️ HIGH RISK OF DIABETES"
            )

        else:

            st.success(
                "✅ LOW RISK OF DIABETES"
            )

        st.write(
            f"### Prediction Confidence: "
            f"{probability*100:.2f}%"
        )

    with col2:

        fig = go.Figure(go.Indicator(

            mode="gauge+number",

            value=probability * 100,

            title={
                'text': "Diabetes Risk %"
            },

            gauge={

                'axis': {
                    'range': [0, 100]
                },

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

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # =====================================================
    # HEALTH RECOMMENDATIONS
    # =====================================================

    st.subheader("💡 Health Recommendations")

    if prediction == 1:

        st.warning("""

        - Reduce sugar intake
        - Daily exercise
        - Weight management
        - Regular glucose monitoring
        - Consult doctor regularly

        """)

    else:

        st.success("""

        - Maintain healthy diet
        - Exercise regularly
        - Drink enough water
        - Sleep properly
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

    # =====================================================
    # TITLE
    # =====================================================

    title = Paragraph(
        "<b>AI Diabetes Prediction Medical Report</b>",
        styles['Title']
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    # =====================================================
    # PATIENT INFO TABLE
    # =====================================================

    patient_info = [

        ["Patient Name", patient_name],
        ["Gender", gender],
        ["Date", str(date)],
        ["Prediction", result_label],
        ["Confidence", f"{probability*100:.2f}%"],
        ["BMI Status", bmi_status]

    ]

    patient_table = Table(
        patient_info,
        colWidths=[220, 220]
    )

    patient_table.setStyle(TableStyle([

        (
            'BACKGROUND',
            (0, 0),
            (-1, -1),
            colors.lightblue
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            1,
            colors.black
        ),

        (
            'FONTNAME',
            (0, 0),
            (-1, -1),
            'Helvetica-Bold'
        )

    ]))

    elements.append(patient_table)

    elements.append(
        Spacer(1, 20)
    )

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
        colWidths=[220, 220]
    )

    medical_table.setStyle(TableStyle([

        (
            'BACKGROUND',
            (0, 0),
            (-1, 0),
            colors.grey
        ),

        (
            'TEXTCOLOR',
            (0, 0),
            (-1, 0),
            colors.white
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            1,
            colors.black
        ),

        (
            'BACKGROUND',
            (0, 1),
            (-1, -1),
            colors.beige
        )

    ]))

    elements.append(medical_table)

    elements.append(
        Spacer(1, 20)
    )

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    if prediction == 1:

        recommendation_text = """

        <b>Health Recommendations:</b><br/><br/>

        • Reduce sugar intake<br/>
        • Daily exercise<br/>
        • Weight management<br/>
        • Regular glucose monitoring<br/>
        • Consult doctor regularly

        """

    else:

        recommendation_text = """

        <b>Healthy Lifestyle Tips:</b><br/><br/>

        • Maintain healthy diet<br/>
        • Exercise regularly<br/>
        • Drink enough water<br/>
        • Sleep properly<br/>
        • Regular health checkup

        """

    recommendation_para = Paragraph(
        recommendation_text,
        styles['BodyText']
    )

    elements.append(recommendation_para)

    elements.append(
        Spacer(1, 20)
    )

    footer = Paragraph(
        "Generated by AI Diabetes Prediction System",
        styles['Italic']
    )

    elements.append(footer)

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
# ADMIN DASHBOARD
# =========================================================

st.markdown("---")

if st.session_state.user_email == "admin@gmail.com":

    st.subheader("🛡️ Admin Dashboard")

    # =====================================================
    # TOTAL USERS
    # =====================================================

    total_users = pd.read_sql_query(
        "SELECT COUNT(*) as total FROM users",
        conn
    )

    total_patients = pd.read_sql_query(
        "SELECT COUNT(*) as total FROM patients",
        conn
    )

    colA, colB = st.columns(2)

    with colA:

        st.metric(
            "Total Users",
            int(total_users['total'][0])
        )

    with colB:

        st.metric(
            "Total Predictions",
            int(total_patients['total'][0])
        )

    st.markdown("---")

    # =====================================================
    # SHOW PATIENT RECORDS
    # =====================================================

    st.subheader("📂 Patient Records")

    df_records = pd.read_sql_query(
        "SELECT * FROM patients",
        conn
    )

    st.dataframe(df_records)

    # =====================================================
    # DOWNLOAD CSV
    # =====================================================

    csv = df_records.to_csv(
        index=False
    ).encode('utf-8')

    st.download_button(

        "⬇ Download Database CSV",

        csv,

        "patients_records.csv",

        "text/csv"

    )

else:

    st.info(
        "User Dashboard Active"
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🚀 Advanced AI Diabetes Prediction System "
    "using Machine Learning + Streamlit + SQLite"
)
