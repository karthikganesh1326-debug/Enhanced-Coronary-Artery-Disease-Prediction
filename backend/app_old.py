"""
Flask Backend API for CAD Prediction System
Provides REST endpoints for predictions with risk categorization
Includes user authentication, registration, and session management
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

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = str(BASE_DIR.parent / "frontend" / "templates")
STATIC_DIR = str(BASE_DIR.parent / "frontend" / "static")

# Create Flask app with correct folders
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Session configuration
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Database configuration
DB_PATH = BASE_DIR / "users.db"

MODEL_PATH = BASE_DIR / "best_cad_model.pkl"
SCALER_PATH = BASE_DIR / "scaler.pkl"
METRICS_PATH = BASE_DIR / "model_metrics.pkl"
PREDICTIONS_LOG = BASE_DIR / "predictions.csv"
DB_PATH = BASE_DIR / "users.db"

# ===== DATABASE SETUP =====
def init_db():
    """Initialize SQLite database with users table"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      password_hash TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
        print("✓ Database initialized")
    except Exception as e:
        print(f"⚠ Database error: {e}")

def register_user(username, password):
    """Register a new user
    Returns: (success: bool, message: str)
    """
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        # Check if user exists
        c.execute('SELECT id FROM users WHERE username = ?', (username,))
        if c.fetchone():
            conn.close()
            return False, "Username already exists"
        
        # Insert new user
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                  (username, password_hash))
        conn.commit()
        conn.close()
        
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(username, password):
    """Validate user credentials
    Returns: (success: bool, user_id: int or None)
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            return True, user[0]
        return False, None
    except Exception as e:
        print(f"Login error: {e}")
        return False, None

# Login required decorator
def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize database on startup
init_db()

# Load model and scaler
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

# Load feature names from dataset
DATA_PATH = BASE_DIR.parent / "dataset" / "heart.csv"
df_header = pd.read_csv(DATA_PATH, nrows=0)
target_col = "DEATH_EVENT" if "DEATH_EVENT" in df_header.columns else df_header.columns[-1]
FEATURE_NAMES = [c for c in df_header.columns if c != target_col]

# Load feature importance if available
FEATURE_IMPORTANCE = None
try:
    FEATURE_IMPORTANCE = pd.read_csv(BASE_DIR / "feature_importance.csv")
except:
    pass

print(f"✓ Features: {FEATURE_NAMES}")
print(f"✓ Predictions will be logged to: {PREDICTIONS_LOG}")

def get_risk_category(probability):
    """Categorize risk level based on probability"""
    if probability < 0.33:
        return "LOW", "#27ae60"  # Green
    elif probability < 0.67:
        return "MEDIUM", "#f39c12"  # Orange
    else:
        return "HIGH", "#e74c3c"  # Red

def log_prediction(input_data, probability, risk_category, risk_color):
    """Log prediction to CSV file"""
    try:
        new_record = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'probability': round(probability * 100, 2),
            'risk_category': risk_category,
            **{f: v for f, v in zip(FEATURE_NAMES, input_data)}
        }
        
        # Append to CSV (create if doesn't exist)
        if PREDICTIONS_LOG.exists():
            df = pd.read_csv(PREDICTIONS_LOG)
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        else:
            df = pd.DataFrame([new_record])
        
        df.to_csv(PREDICTIONS_LOG, index=False)
    except Exception as e:
        print(f"Warning: Could not log prediction: {e}")

def get_contributing_features(probability, top_n=5):
    """Get top contributing features to the prediction"""
    if FEATURE_IMPORTANCE is not None:
        return FEATURE_IMPORTANCE.head(top_n)[['feature', 'importance']].to_dict('records')
    return []

@app.route("/")
def home():
    """Home page - requires login"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("index.html", username=session.get('username'))

@app.route("/about")
def about():
    """About page - accessible to all"""
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration endpoint"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validation
        if not username or not password:
            return render_template("register.html", error="Username and password required")
        
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        
        success, message = register_user(username, password)
        
        if success:
            return redirect(url_for('login'))
        else:
            return render_template("register.html", error=message)
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login endpoint"""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template("login.html", error="Username and password required")
        
        success, user_id = login_user(username, password)
        
        if success:
            session.permanent = True
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Invalid username or password")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """User logout endpoint"""
    session.clear()
    return redirect(url_for('login'))

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    """
    Prediction endpoint
    Expected form data: age, sex, anaemia, creatinine_phosphokinase, diabetes,
                       ejection_fraction, high_blood_pressure, platelets,
                       serum_creatinine, serum_sodium, smoking
    """
    
    if model is None or scaler is None:
        return render_template("result.html", 
                             error="Model not loaded. Please contact administrator.",
                             risk_category="ERROR",
                             risk_color="#95a5a6")
    
    try:
        # Extract input data in correct feature order
        data = []
        for name in FEATURE_NAMES:
            val = request.form.get(name)
            if val is None or val == "":
                return render_template("result.html",
                                     error=f"Missing input for {name}",
                                     risk_category="ERROR",
                                     risk_color="#95a5a6")
            data.append(float(val))
        
        # Scale and predict
        data_scaled = scaler.transform([data])
        probability = model.predict_proba(data_scaled)[0][1]
        risk_category, risk_color = get_risk_category(probability)
        
        # Log prediction
        log_prediction(data, probability, risk_category, risk_color)
        
        # Get contributing features
        contributing_features = get_contributing_features(probability, top_n=5)
        
        # Prepare result
        result = {
            'probability': round(probability * 100, 2),
            'risk_category': risk_category,
            'risk_color': risk_color,
            'contributing_features': contributing_features,
            'recommendation': get_recommendation(risk_category)
        }
        
        return render_template("result.html", **result)
        
    except ValueError as e:
        return render_template("result.html",
                             error=f"Invalid input: {str(e)}",
                             risk_category="ERROR",
                             risk_color="#95a5a6")
    except Exception as e:
        return render_template("result.html",
                             error=f"Prediction error: {str(e)}",
                             risk_category="ERROR",
                             risk_color="#95a5a6")

@app.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    """
    JSON API endpoint for predictions
    Expected JSON: {"age": 50, "sex": 1, ...}
    """
    
    if model is None or scaler is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        input_json = request.get_json()
        
        # Extract features in correct order
        data = []
        for name in FEATURE_NAMES:
            if name not in input_json:
                return jsonify({'error': f'Missing feature: {name}'}), 400
            data.append(float(input_json[name]))
        
        # Predict
        data_scaled = scaler.transform([data])
        probability = model.predict_proba(data_scaled)[0][1]
        risk_category, risk_color = get_risk_category(probability)
        
        # Log prediction
        log_prediction(data, probability, risk_category, risk_color)
        
        # Get contributing features
        contributing_features = get_contributing_features(probability, top_n=5)
        
        return jsonify({
            'success': True,
            'probability': round(probability * 100, 2),
            'risk_category': risk_category,
            'risk_color': risk_color,
            'contributing_features': contributing_features,
            'recommendation': get_recommendation(risk_category)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route("/api/features")
def get_features():
    """Get list of required features"""
    return jsonify({
        'features': FEATURE_NAMES,
        'feature_descriptions': {
            'age': {'unit': 'years', 'min': 0, 'max': 120},
            'sex': {'unit': '0=Female/1=Male', 'min': 0, 'max': 1},
            'anaemia': {'unit': '0=No/1=Yes', 'min': 0, 'max': 1},
            'creatinine_phosphokinase': {'unit': 'mcg/L', 'min': 0},
            'diabetes': {'unit': '0=No/1=Yes', 'min': 0, 'max': 1},
            'ejection_fraction': {'unit': '%', 'min': 0, 'max': 100},
            'high_blood_pressure': {'unit': '0=No/1=Yes', 'min': 0, 'max': 1},
            'platelets': {'unit': 'kiloplatelets/mL', 'min': 0},
            'serum_creatinine': {'unit': 'mg/dL', 'min': 0},
            'serum_sodium': {'unit': 'mEq/L', 'min': 0},
            'smoking': {'unit': '0=No/1=Yes', 'min': 0, 'max': 1}
        }
    })

@app.route("/api/predictions-log")
def get_predictions_log():
    """Get all predictions log (for admin/analysis)"""
    try:
        if PREDICTIONS_LOG.exists():
            df = pd.read_csv(PREDICTIONS_LOG)
            return jsonify(df.tail(100).to_dict('records'))
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def get_recommendation(risk_category):
    """Get medical recommendation based on risk category"""
    recommendations = {
        'LOW': {
            'text': 'Continue regular health check-ups. Maintain healthy lifestyle.',
            'icon': '✓'
        },
        'MEDIUM': {
            'text': 'Schedule appointment with cardiologist for further evaluation.',
            'icon': '⚠'
        },
        'HIGH': {
            'text': 'URGENT: Consult cardiologist immediately. Consider additional testing.',
            'icon': '🚨'
        },
        'ERROR': {
            'text': 'Unable to generate recommendation due to error.',
            'icon': '❌'
        }
    }
    return recommendations.get(risk_category, recommendations['ERROR'])

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Starting CAD Prediction System Backend")
    print("=" * 80)
    print(f"Features: {FEATURE_NAMES}")
    print(f"Server running: http://127.0.0.1:5000")
    print("=" * 80 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
