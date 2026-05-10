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
# THEME SWITCHER
# =========================================================

theme = st.sidebar.toggle(
    "🌙 Dark Mode",
    value=True
)

# =========================================================
# DARK THEME
# =========================================================

if theme:

    st.markdown("""
    <style>

    .stApp {
        background: linear-gradient(
            to right,
            #0f172a,
            #111827
        );
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 2px solid #1f2937;
    }

    h1, h2, h3, h4, h5, h6, p, label {
        color: white !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput input,
    .stDateInput input {

        background-color: #1e293b !important;
        color: white !important;

        border-radius: 10px;
        border: 1px solid #334155;
    }

    .stSelectbox > div > div {

        background-color: #1e293b !important;
        color: white !important;

        border-radius: 10px;
    }

    .stButton > button {

        width: 100%;

        background: linear-gradient(
            135deg,
            #2563eb,
            #06b6d4
        );

        color: white;

        border: none;

        border-radius: 12px;

        height: 50px;

        font-size: 18px;
        font-weight: bold;

        transition: 0.3s;

        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }

    .stButton > button:hover {

        transform: scale(1.02);

        background: linear-gradient(
            135deg,
            #1d4ed8,
            #0891b2
        );
    }

    .metric-card {

        background: linear-gradient(
            135deg,
            #1e293b,
            #0f172a
        );

        padding: 25px;

        border-radius: 18px;

        border: 1px solid #334155;

        box-shadow: 0px 5px 20px rgba(0,0,0,0.3);

        text-align: center;

        margin-bottom: 15px;
    }

    div[data-testid="metric-container"] {

        background: #1e293b;

        border: 1px solid #334155;

        padding: 15px;

        border-radius: 15px;

        box-shadow: 0px 3px 10px rgba(0,0,0,0.2);
    }

    [data-testid="stDataFrame"] {

        border-radius: 15px;

        overflow: hidden;

        border: 1px solid #334155;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """, unsafe_allow_html=True)

# =========================================================
# LIGHT THEME
# =========================================================

else:

    st.markdown("""
    <style>

    .stApp {
        background: #f8fafc;
        color: black;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 2px solid #e2e8f0;
    }

    h1, h2, h3, h4, h5, h6, p, label {
        color: black !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput input,
    .stDateInput input {

        background-color: white !important;
        color: black !important;

        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }

    .stSelectbox > div > div {

        background-color: white !important;
        color: black !important;

        border-radius: 10px;
    }

    .stButton > button {

        width: 100%;

        background: linear-gradient(
            135deg,
            #2563eb,
            #06b6d4
        );

        color: white;

        border: none;

        border-radius: 12px;

        height: 50px;

        font-size: 18px;
        font-weight: bold;

        transition: 0.3s;
    }

    .metric-card {

        background: white;

        padding: 25px;

        border-radius: 18px;

        border: 1px solid #e2e8f0;

        box-shadow: 0px 5px 20px rgba(0,0,0,0.08);

        text-align: center;

        margin-bottom: 15px;
    }

    div[data-testid="metric-container"] {

        background: white;

        border: 1px solid #e2e8f0;

        padding: 15px;

        border-radius: 15px;
    }

    [data-testid="stDataFrame"] {

        border-radius: 15px;

        overflow: hidden;

        border: 1px solid #e2e8f0;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """, unsafe_allow_html=True)
# =========================================================
# DATABASE CONNECTION
# =========================================================

import sqlite3

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
# PATIENT TABLE
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

# IMPORTANT
columns = pickle.load(
    open("columns.pkl", "rb")
)

# =========================================================
# PASSWORD HASH
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

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =========================================================
# LOGIN / SIGNUP / ADMIN LOGIN
# =========================================================

if st.session_state.logged_in == False:

    st.title("🩺 AI Diabetes Prediction System")

    st.sidebar.markdown("## 📌 Navigation")

    # =====================================================
    # MENU BUTTONS
    # =====================================================

    if "menu" not in st.session_state:
        st.session_state.menu = "User Login"

    if st.sidebar.button("🔐 Login"):
        st.session_state.menu = "User Login"

    if st.sidebar.button("📝 Sign Up"):
        st.session_state.menu = "Create Account"

    if st.sidebar.button("🛡️ Admin Login"):
        st.session_state.menu = "Admin Login"

    choice = st.session_state.menu

    # =====================================================
    # USER LOGIN
    # =====================================================

    if choice == "User Login":

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

                    st.session_state.is_admin = False

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

    # =====================================================
    # ADMIN LOGIN
    # =====================================================

    elif choice == "Admin Login":

        st.subheader("🛡️ Admin Login")

        admin_email = st.text_input(
            "Admin Email"
        )

        admin_password = st.text_input(
            "Admin Password",
            type="password"
        )

        if st.button("Admin Login"):

            if (
                admin_email == "mohammadsohail6162@gmail.com"
                and admin_password == "9801686031"
            ):

                st.success(
                    "Admin Login Successful"
                )

                st.session_state.logged_in = True

                st.session_state.user_email = admin_email

                st.session_state.is_admin = True

                st.rerun()

            else:

                st.error(
                    "Invalid Admin Credentials"
                )

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🩺 AI Dashboard")

if st.session_state.is_admin:

    st.sidebar.success(
        "🛡️ Admin Logged In"
    )

else:

    st.sidebar.success(
        f"👤 {st.session_state.user_email}"
    )

# =========================================================
# LOGOUT
# =========================================================

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False

    st.session_state.user_email = ""

    st.session_state.is_admin = False

    st.rerun()

st.sidebar.markdown("---")

# =========================================================
# ADMIN DASHBOARD
# =========================================================

if st.session_state.is_admin:

    st.title("🛡️ Admin Dashboard")

    total_users = pd.read_sql_query(
        "SELECT COUNT(*) as total FROM users",
        conn
    )

    total_patients = pd.read_sql_query(
        "SELECT COUNT(*) as total FROM patients",
        conn
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total Users",
            int(total_users['total'][0])
        )

    with col2:

        st.metric(
            "Total Predictions",
            int(total_patients['total'][0])
        )

    st.markdown("---")

    st.subheader("📂 Patient Records")

    df_records = pd.read_sql_query(
        "SELECT * FROM patients",
        conn
    )

    st.dataframe(df_records)

    csv = df_records.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇ Download CSV",
        csv,
        "patients_records.csv",
        "text/csv"
    )

    st.stop()

# =========================================================
# USER SIDEBAR
# =========================================================

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
                "Pregnancies not applicable for male"
            )

        glucose = st.slider(
            "Glucose",
            50,
            250,
            120
        )

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
# PREDICTION
# =========================================================

if st.button("🚀 Run AI Prediction"):

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

    input_encoded = pd.get_dummies(
        input_raw
    )

    input_df = input_encoded.reindex(
        columns=columns,
        fill_value=0
    )

    prediction = model.predict(
        input_df
    )[0]

    probability = model.predict_proba(
        input_df
    )[0][1]

    if prediction == 1:

        result_label = "High Risk of Diabetes"

    else:

        result_label = "Low Risk of Diabetes"

    # =====================================================
    # SAVE DATABASE
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
    # PATIENT INFO
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
    # MEDICAL DATA
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
    # RECOMMENDATIONS IN PDF
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
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🚀 AI Diabetes Prediction System"
)
