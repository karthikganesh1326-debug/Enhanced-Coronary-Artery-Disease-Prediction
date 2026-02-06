"""
CAD Prediction System - Multi-Role Professional Edition
Features: Patient & Doctor roles, role-based dashboards, prediction history
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pickle
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sqlite3
from functools import wraps

# ===== SETUP =====
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = str(BASE_DIR.parent / "frontend" / "templates")
STATIC_DIR = str(BASE_DIR.parent / "frontend" / "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

DB_PATH = BASE_DIR / "cad_system.db"
MODEL_PATH = BASE_DIR / "best_cad_model.pkl"
SCALER_PATH = BASE_DIR / "scaler.pkl"

# ===== DATABASE FUNCTIONS =====
def init_db():
    """Initialize SQLite database with users and predictions tables"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        # Users table with role column (patient or doctor)
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     email TEXT,
                     password_hash TEXT NOT NULL,
                     role TEXT NOT NULL,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Predictions table to store patient predictions
        c.execute('''CREATE TABLE IF NOT EXISTS predictions (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER NOT NULL,
                     age REAL,
                     anaemia INTEGER,
                     creatinine_phosphokinase REAL,
                     diabetes INTEGER,
                     ejection_fraction REAL,
                     high_blood_pressure INTEGER,
                     platelets REAL,
                     serum_creatinine REAL,
                     serum_sodium REAL,
                     sex INTEGER,
                     smoking INTEGER,
                     time REAL,
                     probability REAL,
                     risk_category TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        conn.commit()
        conn.close()
        print("✓ Database initialized with users and predictions tables")
    except Exception as e:
        print(f"⚠ Database error: {e}")

def register_user(username, email, password, role):
    """Register a new user (patient or doctor)"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    if role not in ['patient', 'doctor']:
        return False, "Invalid role"
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        c.execute('SELECT id FROM users WHERE username = ?', (username,))
        if c.fetchone():
            conn.close()
            return False, "Username already exists"
        
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                  (username, email, password_hash, role))
        conn.commit()
        conn.close()
        
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(username, password):
    """Validate user credentials and return user info with role"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('SELECT id, password_hash, role, username FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            return True, {'user_id': user[0], 'role': user[2], 'username': user[3]}
        return False, None
    except Exception as e:
        print(f"Login error: {e}")
        return False, None

def get_user_info(user_id):
    """Get user info by ID"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('SELECT id, username, email, role FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        return user
    except:
        return None

def save_prediction(user_id, features, probability, risk_category):
    """Save prediction to database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        c.execute('''INSERT INTO predictions 
                     (user_id, age, anaemia, creatinine_phosphokinase, diabetes, 
                      ejection_fraction, high_blood_pressure, platelets, 
                      serum_creatinine, serum_sodium, sex, smoking, time, 
                      probability, risk_category)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, features['age'], features['anaemia'], 
                   features['creatinine_phosphokinase'], features['diabetes'],
                   features['ejection_fraction'], features['high_blood_pressure'],
                   features['platelets'], features['serum_creatinine'],
                   features['serum_sodium'], features['sex'], features['smoking'],
                   features['time'], probability, risk_category))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving prediction: {e}")
        return False

def get_patient_predictions(user_id):
    """Get all predictions for a specific patient"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('''SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC''',
                  (user_id,))
        predictions = c.fetchall()
        conn.close()
        
        result = []
        for p in predictions:
            result.append({
                'id': p[0],
                'probability': p[14],
                'risk_category': p[15],
                'created_at': p[16],
                'age': p[2],
                'ejection_fraction': p[6]
            })
        return result
    except Exception as e:
        print(f"Error fetching predictions: {e}")
        return []

def get_all_patients():
    """Get all patients for doctor dashboard"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('SELECT id, username, email, created_at FROM users WHERE role = ?', ('patient',))
        patients = c.fetchall()
        conn.close()
        
        result = []
        for p in patients:
            # Count predictions for each patient
            conn = sqlite3.connect(str(DB_PATH))
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM predictions WHERE user_id = ?', (p[0],))
            pred_count = c.fetchone()[0]
            conn.close()
            
            result.append({
                'id': p[0],
                'username': p[1],
                'email': p[2],
                'registered': p[3],
                'predictions_count': pred_count
            })
        
        return result
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return []

def get_patient_with_predictions(patient_id):
    """Get patient details and all their predictions"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        # Get patient info
        c.execute('SELECT id, username, email, created_at FROM users WHERE id = ? AND role = ?',
                  (patient_id, 'patient'))
        patient = c.fetchone()
        
        if not patient:
            return None
        
        # Get all predictions for this patient
        c.execute('''SELECT id, probability, risk_category, created_at FROM predictions 
                     WHERE user_id = ? ORDER BY created_at DESC''', (patient_id,))
        predictions = c.fetchall()
        conn.close()
        
        return {
            'id': patient[0],
            'username': patient[1],
            'email': patient[2],
            'registered': patient[3],
            'predictions': [{'id': pred[0], 'probability': pred[1], 
                           'risk_category': pred[2], 'date': pred[3]} 
                          for pred in predictions]
        }
    except Exception as e:
        print(f"Error fetching patient details: {e}")
        return None

# ===== DECORATORS =====
def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def patient_required(f):
    """Decorator to require patient role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'patient':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    """Decorator to require doctor role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'doctor':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== MODEL LOADING =====
print("Loading CAD Prediction Model...")
model = None
scaler = None
try:
    with MODEL_PATH.open("rb") as f:
        model = pickle.load(f)
    with SCALER_PATH.open("rb") as f:
        scaler = pickle.load(f)
    print("✓ Model loaded successfully")
except FileNotFoundError:
    print("⚠ Model not found! Please run ml_model.py first.")

# Load feature names
DATA_PATH = BASE_DIR.parent / "dataset" / "heart.csv"
try:
    df_header = pd.read_csv(DATA_PATH, nrows=0)
    target_col = "DEATH_EVENT" if "DEATH_EVENT" in df_header.columns else df_header.columns[-1]
    FEATURE_NAMES = [c for c in df_header.columns if c != target_col]
    print(f"✓ Features loaded: {len(FEATURE_NAMES)} parameters")
except:
    FEATURE_NAMES = []
    print("⚠ Could not load features")

# Load feature importance
FEATURE_IMPORTANCE = None
try:
    FEATURE_IMPORTANCE = pd.read_csv(BASE_DIR / "feature_importance.csv")
except:
    pass

# ===== UTILITY FUNCTIONS =====
def get_risk_category(probability):
    """Categorize risk level"""
    if probability < 0.33:
        return "LOW", "#27ae60"  # Green
    elif probability < 0.67:
        return "MEDIUM", "#f39c12"  # Orange
    else:
        return "HIGH", "#e74c3c"  # Red

def get_recommendation(risk_category):
    """Get medical recommendation"""
    recommendations = {
        'LOW': 'Continue regular health check-ups. Maintain healthy lifestyle.',
        'MEDIUM': 'Schedule appointment with cardiologist for further evaluation.',
        'HIGH': 'URGENT: Consult cardiologist immediately. Consider additional testing.',
        'ERROR': 'Unable to generate recommendation due to error.'
    }
    return recommendations.get(risk_category, recommendations['ERROR'])

# ===== ROUTES =====

@app.route("/")
def index():
    """Home page - redirect based on role"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    else:
        return redirect(url_for('patient_dashboard'))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login route for both patients and doctors"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template("login.html", error="Username and password required")
        
        success, user_info = login_user(username, password)
        
        if success:
            session.permanent = True
            session['user_id'] = user_info['user_id']
            session['role'] = user_info['role']
            session['username'] = user_info['username']
            
            # Redirect based on role
            if user_info['role'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        else:
            return render_template("login.html", error="Invalid username or password")
    
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register():
    """Redirect to role selection"""
    return render_template("register.html")

@app.route("/register_patient", methods=["GET", "POST"])
def register_patient():
    """Patient registration"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if password != confirm_password:
            return render_template("register_patient.html", error="Passwords do not match")
        
        success, message = register_user(username, email, password, 'patient')
        
        if success:
            return redirect(url_for('login'))
        else:
            return render_template("register_patient.html", error=message)
    
    return render_template("register_patient.html")

@app.route("/register_doctor", methods=["GET", "POST"])
def register_doctor():
    """Doctor registration"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if password != confirm_password:
            return render_template("register_doctor.html", error="Passwords do not match")
        
        success, message = register_user(username, email, password, 'doctor')
        
        if success:
            return redirect(url_for('login'))
        else:
            return render_template("register_doctor.html", error=message)
    
    return render_template("register_doctor.html")

@app.route("/logout")
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

@app.route("/patient/dashboard")
@patient_required
def patient_dashboard():
    """Patient dashboard - shows their predictions"""
    predictions = get_patient_predictions(session['user_id'])
    return render_template("patient_dashboard.html", 
                         username=session['username'],
                         predictions=predictions)

@app.route("/patient/predict", methods=["GET", "POST"])
@patient_required
def patient_predict():
    """Patient prediction form"""
    if request.method == "POST":
        if model is None or scaler is None:
            return render_template("predict.html", 
                                 error="Model not loaded",
                                 username=session['username'])
        
        try:
            # Collect features
            features_input = {}
            data = []
            for name in FEATURE_NAMES:
                val = request.form.get(name)
                if val is None or val == "":
                    return render_template("predict.html",
                                         error=f"Missing {name}",
                                         username=session['username'])
                features_input[name] = float(val)
                data.append(float(val))
            
            # Make prediction
            data_scaled = scaler.transform([data])
            probability = float(model.predict_proba(data_scaled)[0][1])
            risk_category, risk_color = get_risk_category(probability)
            
            # Save to database
            save_prediction(session['user_id'], features_input, probability, risk_category)
            
            result = {
                'probability': round(probability * 100, 2),
                'risk_category': risk_category,
                'risk_color': risk_color,
                'recommendation': get_recommendation(risk_category),
                'username': session['username']
            }
            
            return render_template("prediction_result.html", **result)
            
        except Exception as e:
            return render_template("predict.html",
                                 error=f"Prediction error: {str(e)}",
                                 username=session['username'])
    
    return render_template("predict.html", username=session['username'])

@app.route("/doctor/dashboard")
@doctor_required
def doctor_dashboard():
    """Doctor dashboard - shows all patients and their predictions"""
    patients = get_all_patients()
    return render_template("doctor_dashboard.html",
                         username=session['username'],
                         patients=patients)

@app.route("/doctor/patient/<int:patient_id>")
@doctor_required
def doctor_patient_details(patient_id):
    """Doctor view - patient details and predictions"""
    patient = get_patient_with_predictions(patient_id)
    
    if not patient:
        return render_template("doctor_dashboard.html",
                             username=session['username'],
                             error="Patient not found")
    
    return render_template("patient_details.html",
                         username=session['username'],
                         patient=patient)

@app.route("/about")
def about():
    """About page"""
    return render_template("about.html")

if __name__ == "__main__":
    init_db()
    print("\n" + "=" * 80)
    print("CAD Prediction System - Multi-Role Edition")
    print("=" * 80)
    print(f"Running on: http://127.0.0.1:5000")
    print("=" * 80 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
