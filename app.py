import streamlit as st
import numpy as np
import pickle
import pandas as pd
import hashlib
import sqlite3
from datetime import datetime

# ---- Symptom & Disease Dictionaries (abbreviated) ----
symptoms_dict = {
     'itching': 0, 'skin rash': 1, 'nodal skin eruptions': 2, 'continuous sneezing': 3, 
    'shivering': 4, 'chills': 5, 'joint pain': 6, 'stomach pain': 7, 'acidity': 8, 
    'ulcers on tongue': 9, 'muscle wasting': 10, 'vomiting': 11, 'burning micturition': 12, 
    'spotting urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 
    'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight loss': 19, 'restlessness': 20, 
    'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 
    'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 
    'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 
    'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 
    'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 
    'fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 
    'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 
    'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 
    'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 
    'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 
    'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 
    'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 
    'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 
    'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 
    'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 
    'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 
    'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 
    'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 
    'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 
    'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 
    'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 
    'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 
    'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 
    'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 
    'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 
    'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 
    'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 
    'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 
    'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 
    'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 
    'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 
    'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 
    'red_sore_around_nose': 130, 'yellow_crust_ooze': 131

    # ... include all 132 symptoms ...
}

diseases_list = {
     0: '(vertigo) Paroymsal  Positional Vertigo', 1: 'AIDS', 2: 'Acne', 3: 'Alcoholic hepatitis',
    4: 'Allergy', 5: 'Arthritis', 6: 'Bronchial Asthma', 7: 'Cervical spondylosis',
    8: 'Chicken pox', 9: 'Chronic cholestasis', 10: 'Common Cold', 11: 'Dengue',
    12: 'Diabetes ', 13: 'Dimorphic hemmorhoids(piles)', 14: 'Drug Reaction',
    15: 'Fungal infection', 16: 'GERD', 17: 'Gastroenteritis', 18: 'Heart attack',
    19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E',
    23: 'Hypertension ', 24: 'Hyperthyroidism', 25: 'Hypoglycemia',
    26: 'Hypothyroidism', 27: 'Impetigo', 28: 'Jaundice', 29: 'Malaria',
    30: 'Migraine', 31: 'Osteoarthristis', 32: 'Paralysis (brain hemorrhage)',
    33: 'Peptic ulcer diseae', 34: 'Pneumonia', 35: 'Psoriasis', 36: 'Tuberculosis',
    37: 'Typhoid', 38: 'Urinary tract infection', 39: 'Varicose veins',
    40: 'hepatitis A'

    # ... include all 41 diseases ...
}

# ---- Database Setup ----
def init_db():
    conn = sqlite3.connect('med_history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symptoms TEXT,
            predicted_disease TEXT,
            description TEXT,
            precautions TEXT,
            medications TEXT,
            workouts TEXT,
            diets TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# ---- Authentication ----
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect('med_history.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                  (username.strip(), hash_password(password.strip())))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('med_history.db')
    c = conn.cursor()
    c.execute('SELECT id, password FROM users WHERE username = ?', (username.strip(),))
    result = c.fetchone()
    conn.close()
    if result and result[1] == hash_password(password.strip()):
        return result[0]
    return None

# ---- Data Loading ----
@st.cache_data
def load_model_and_data():
    with open("svc.pkl", "rb") as f:
        svc = pickle.load(f)
    description = pd.read_csv("description.csv")
    precaution = pd.read_csv("precautions_df.csv")
    workout = pd.read_csv("workout_df.csv")
    medication = pd.read_csv("medications.csv")
    diet = pd.read_csv("diets.csv")
    return svc, description, precaution, workout, medication, diet

# ---- Helpers ----
def get_recommendations(dis, description_df, prec_df, med_df, diet_df, workout_df):
    desc = " ".join(description_df[description_df['Disease']==dis]['Description'].tolist())
    pre = prec_df[prec_df['Disease']==dis][['Precaution_1','Precaution_2','Precaution_3','Precaution_4']].values
    med = med_df[med_df['Disease']==dis]['Medication'].tolist()
    die = diet_df[diet_df['Disease']==dis]['Diet'].tolist()
    wrk = workout_df[workout_df['disease']==dis]['workout'].tolist()
    return desc, pre, med, die, wrk

def log_consultation(uid, symp, disease, desc, prec, meds, wrk, die):
    conn = sqlite3.connect('med_history.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO consultations
        (user_id, symptoms, predicted_disease, description, precautions, medications, workouts, diets)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (uid, symp, disease, desc, prec, meds, wrk, die))
    conn.commit()
    conn.close()

def fetch_history(uid):
    conn = sqlite3.connect('med_history.db')
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, symptoms, predicted_disease, description,
               precautions, medications, workouts, diets
        FROM consultations
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (uid,))
    data = c.fetchall()
    conn.close()
    return data

# ---- Pages ----
def medicine_recommendation_page(uid, svc, description_df, prec_df, workout_df, med_df, diet_df):
    st.title("🩺 Medicine Recommendation System")
    st.caption("Example symptoms: headache, fever, cough")

    with st.form("symp"):
        inp = st.text_input("Enter symptoms (comma-separated):")
        ok = st.form_submit_button("Get Prediction")

    if ok and inp.strip():
        syms = [s.strip().lower() for s in inp.split(',')]
        iv = np.zeros(len(symptoms_dict))
        for s in syms:
            if s in symptoms_dict:
                iv[symptoms_dict[s]] = 1
            else:
                st.warning(f"Symptom '{s}' not recognized")

        if iv.sum() == 0:
            st.error("Please input valid symptoms.")
            return

        pred = svc.predict([iv])[0]
        disease = diseases_list[pred]
        desc, pre, meds, die, wrk = get_recommendations(disease, description_df, prec_df, med_df, diet_df, workout_df)
        st.success(f"Predicted Disease: **{disease}**")

        with st.expander("Recommendations"):
            st.subheader("Description"); st.write(desc)
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Precautions")
                for i, p in enumerate(pre[0], 1): st.write(f"{i}. {p}")
                st.subheader("Medications")
                for i, m in enumerate(meds, 1): st.write(f"{i}. {m}")
            with c2:
                st.subheader("Diet Plan")
                for i, d in enumerate(die, 1): st.write(f"{i}. {d}")
                st.subheader("Workout Plan")
                for i, w in enumerate(wrk, 1): st.write(f"{i}. {w}")

        log_consultation(uid, inp, disease, desc, "|".join(pre[0]), "|".join(meds), "|".join(wrk), "|".join(die))

def history_page(uid):
    st.title("Consultation History")
    hist = fetch_history(uid)
    if not hist:
        st.info("No history yet.")
        return
    for rec in hist:
        ts = datetime.fromisoformat(rec[0])
        with st.expander(f"{ts.strftime('%b %d, %Y %H:%M')}"):
            st.write(f"**Symptoms:** {rec[1]}")
            st.write(f"**Disease:** {rec[2]}")
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Description"); st.write(rec[3])
                st.subheader("Precautions")
                for j, p in enumerate(rec[4].split('|'), 1): st.write(f"{j}. {p}")
                if rec[5]:
                    st.subheader("Medications")
                    for j, m in enumerate(rec[5].split('|'), 1): st.write(f"{j}. {m}")
            with c2:
                if rec[7]:
                    st.subheader("Diet")
                    for j, d in enumerate(rec[7].split('|'), 1): st.write(f"{j}. {d}")
                if rec[6]:
                    st.subheader("Workout")
                    for j, w in enumerate(rec[6].split('|'), 1): st.write(f"{j}. {w}")

# ---- Main ----
def main():
    init_db()
    svc, description_df, prec_df, workout_df, med_df, diet_df = load_model_and_data()

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    if not st.session_state.user_id:
        st.sidebar.title("Authentication")
        mode = st.sidebar.radio("Action", ["Login", "Register"])

        if mode == "Login":
            u = st.sidebar.text_input("Username")
            p = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                uid = verify_user(u, p)
                if uid:
                    st.session_state.user_id = uid
                    st.session_state.username = u.strip()
                    st.rerun()
                else:
                    st.sidebar.error("Invalid credentials")

        else:
            u2 = st.sidebar.text_input("New Username")
            p2 = st.sidebar.text_input("New Password", type="password")
            p3 = st.sidebar.text_input("Confirm Password", type="password")
            if st.sidebar.button("Register"):
                if not u2.strip() or not p2.strip():
                    st.sidebar.error("Fields required")
                elif p2 != p3:
                    st.sidebar.error("Passwords don't match")
                elif register_user(u2, p2):
                    st.sidebar.success("Registration successful, login now")
                else:
                    st.sidebar.error("Username exists")

    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.user_id = None
            st.rerun()
        choice = st.sidebar.radio("Navigation", ["Get Recommendation", "View History"])
        if choice == "Get Recommendation":
            medicine_recommendation_page(st.session_state.user_id, svc, description_df,
                                         prec_df, workout_df, med_df, diet_df)
        else:
            history_page(st.session_state.user_id)

if __name__ == "__main__":
    main()
