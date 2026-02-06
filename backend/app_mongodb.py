"""
CAD Prediction System - MongoDB Atlas Edition
Features: Patient & Doctor roles, MongoDB shared database, role-based dashboards
Supports multi-user access from different machines
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import numpy as np
import pickle
from pathlib import Path
import pandas as pd
import json
import os
import io
import csv
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===== CONFIGURATION =====
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = str(BASE_DIR.parent / "frontend" / "templates")
STATIC_DIR = str(BASE_DIR.parent / "frontend" / "static")

# Flask App Setup
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# MongoDB Atlas Connection String
# Get from environment variable or use default (UPDATE WITH YOUR ATLAS CONNECTION STRING)
MONGODB_URL = os.environ.get(
    'MONGODB_URL',
    'mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority'
)

# Database and collection names
DB_NAME = 'cad_prediction_db'
COLLECTION_USERS = 'users'
COLLECTION_ASSESSMENTS = 'assessments'
COLLECTION_PATIENT_PROFILES = 'patient_profiles'
COLLECTION_DOCTOR_PROFILES = 'doctor_profiles'

# Model paths
MODEL_PATH = BASE_DIR / "best_cad_model.pkl"
SCALER_PATH = BASE_DIR / "scaler.pkl"
DATA_PATH = BASE_DIR.parent / "dataset" / "heart.csv"

# Global MongoDB client and database
mongoclient = None
db = None

# ===== MONGODB CONNECTION MANAGEMENT =====

def init_mongodb():
    """
    Initialize MongoDB Atlas connection and create necessary indexes.
    Called once at app startup.
    """
    global mongoclient, db
    
    try:
        print("Attempting to connect to MongoDB Atlas...")
        mongoclient = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        mongoclient.admin.command('ping')
        print("✓ MongoDB Atlas connection successful")
        
        db = mongoclient[DB_NAME]
        
        # Create indexes for better query performance
        # Users collection: unique username and email
        db[COLLECTION_USERS].create_index('username', unique=True)
        db[COLLECTION_USERS].create_index('email', unique=True)
        print("✓ User indexes created")
        
        # Assessments collection: faster queries by user_id and creation date
        db[COLLECTION_ASSESSMENTS].create_index('user_id')
        db[COLLECTION_ASSESSMENTS].create_index('created_at')
        print("✓ Assessment indexes created")
        
        print(f"✓ Connected to database: {DB_NAME}")
        return True
        
    except ServerSelectionTimeoutError:
        print("✗ Failed to connect to MongoDB Atlas")
        print("  Please check your MONGODB_URL connection string")
        return False
    except Exception as e:
        print(f"✗ MongoDB initialization error: {e}")
        return False

def get_db():
    """
    Get MongoDB database instance.
    Ensures connection is active before returning.
    """
    global db
    if db is None:
        raise RuntimeError("MongoDB not initialized. Call init_mongodb() first.")
    return db

# ===== DATABASE FUNCTIONS =====

def register_user(username, email, password, role):
    """
    Register a new user (patient or doctor) in MongoDB.
    
    Args:
        username: Unique username (min 3 chars)
        email: User email address
        password: Plain password (will be hashed)
        role: 'patient' or 'doctor'
    
    Returns:
        (success: bool, message: str)
    """
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters"
    if role not in ['patient', 'doctor']:
        return False, "Invalid role. Must be 'patient' or 'doctor'"
    
    try:
        db = get_db()
        
        # Check if username or email already exists
        if db[COLLECTION_USERS].find_one({'username': username}):
            return False, "Username already exists"
        if db[COLLECTION_USERS].find_one({'email': email}):
            return False, "Email already registered"
        
        # Hash the password using werkzeug
        password_hash = generate_password_hash(password)
        
        # Create user document
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert into users collection
        result = db[COLLECTION_USERS].insert_one(user_doc)
        user_id = result.inserted_id
        
        # Create role-specific profile documents
        if role == 'patient':
            patient_profile = {
                'user_id': user_id,
                'age': None,
                'gender': None,
                'medical_history': [],
                'created_at': datetime.utcnow()
            }
            db[COLLECTION_PATIENT_PROFILES].insert_one(patient_profile)
        
        elif role == 'doctor':
            doctor_profile = {
                'user_id': user_id,
                'license_number': None,
                'specialization': None,
                'hospital': None,
                'created_at': datetime.utcnow()
            }
            db[COLLECTION_DOCTOR_PROFILES].insert_one(doctor_profile)
        
        print(f"✓ User registered: {username} ({role})")
        return True, "Registration successful"
        
    except DuplicateKeyError:
        return False, "Username or email already exists"
    except Exception as e:
        print(f"Registration error: {e}")
        return False, f"Registration error: {str(e)}"

def login_user(username, password):
    """
    Validate user credentials against MongoDB.
    
    Args:
        username: Username to login
        password: Plain password to verify
    
    Returns:
        (success: bool, user_info: dict or None)
        user_info = {'user_id': ObjectId, 'role': str, 'username': str}
    """
    try:
        db = get_db()
        
        # Find user by username
        user = db[COLLECTION_USERS].find_one({'username': username})
        
        if not user:
            return False, None
        
        # Verify password hash
        if check_password_hash(user['password_hash'], password):
            return True, {
                'user_id': user['_id'],
                'role': user['role'],
                'username': user['username']
            }
        
        return False, None
        
    except Exception as e:
        print(f"Login error: {e}")
        return False, None

def get_user_info(user_id):
    """
    Retrieve user information from MongoDB by ID.
    
    Args:
        user_id: MongoDB ObjectId
    
    Returns:
        dict with user info or None
    """
    try:
        db = get_db()
        
        # Convert string ID to ObjectId if needed
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        user = db[COLLECTION_USERS].find_one({'_id': user_id})
        
        if user:
            return {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'created_at': user.get('created_at')
            }
        return None
        
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None

def save_assessment(user_id, features, probability, risk_category):
    """
    Save a CAD prediction assessment to MongoDB assessments collection.
    
    Args:
        user_id: MongoDB ObjectId of the patient
        features: dict of medical features
        probability: float between 0 and 1
        risk_category: 'LOW', 'MEDIUM', or 'HIGH'
    
    Returns:
        bool indicating success
    """
    try:
        db = get_db()
        
        # Convert string ID to ObjectId if needed
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        # Create assessment document
        assessment = {
            'user_id': user_id,
            'age': features.get('age'),
            'anaemia': features.get('anaemia'),
            'creatinine_phosphokinase': features.get('creatinine_phosphokinase'),
            'diabetes': features.get('diabetes'),
            'ejection_fraction': features.get('ejection_fraction'),
            'high_blood_pressure': features.get('high_blood_pressure'),
            'platelets': features.get('platelets'),
            'serum_creatinine': features.get('serum_creatinine'),
            'serum_sodium': features.get('serum_sodium'),
            'sex': features.get('sex'),
            'smoking': features.get('smoking'),
            'time': features.get('time'),
            'probability': probability,
            'risk_category': risk_category,
            'created_at': datetime.utcnow()
        }
        
        db[COLLECTION_ASSESSMENTS].insert_one(assessment)
        return True
        
    except Exception as e:
        print(f"Error saving assessment: {e}")
        return False

def get_patient_assessments(user_id):
    """
    Get all assessments for a specific patient.
    
    Args:
        user_id: MongoDB ObjectId of the patient
    
    Returns:
        list of assessment dicts, sorted by date (newest first)
    """
    try:
        db = get_db()
        
        # Convert string ID to ObjectId if needed
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        # Query assessments for this user, sorted by creation date descending
        assessments = db[COLLECTION_ASSESSMENTS].find(
            {'user_id': user_id}
        ).sort('created_at', -1)
        
        result = []
        for assessment in assessments:
            result.append({
                'id': str(assessment['_id']),
                'probability': assessment.get('probability'),
                'risk_category': assessment.get('risk_category'),
                'created_at': assessment.get('created_at'),
                'age': assessment.get('age'),
                'ejection_fraction': assessment.get('ejection_fraction')
            })
        
        return result
        
    except Exception as e:
        print(f"Error fetching patient assessments: {e}")
        return []

def get_all_patients():
    """
    Get all patient users for doctor dashboard.
    
    Returns:
        list of patient dicts with assessment counts
    """
    try:
        db = get_db()
        
        # Find all users with role='patient'
        patients = db[COLLECTION_USERS].find({'role': 'patient'})
        
        result = []
        for patient in patients:
            patient_id = patient['_id']
            
            # Count assessments for this patient
            assessment_count = db[COLLECTION_ASSESSMENTS].count_documents(
                {'user_id': patient_id}
            )
            
            result.append({
                'id': str(patient_id),
                'username': patient['username'],
                'email': patient.get('email'),
                'registered': patient.get('created_at'),
                'predictions_count': assessment_count,
                'prediction_count': assessment_count  # Backwards compatible
            })
        
        return result
        
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return []

def get_all_assessments():
    """
    Get all patient assessments for doctor view.
    Joins assessment data with patient usernames.
    
    Returns:
        list of assessment dicts with patient info
    """
    try:
        db = get_db()
        
        # Query all assessments, sorted by date descending
        assessments = db[COLLECTION_ASSESSMENTS].find().sort('created_at', -1)
        
        results = []
        for assessment in assessments:
            user_id = assessment['user_id']
            
            # Get patient username
            user = db[COLLECTION_USERS].find_one({'_id': user_id})
            username = user['username'] if user else 'Unknown'
            
            results.append({
                'id': str(assessment['_id']),
                'user_id': str(user_id),
                'username': username,
                'features': {
                    'age': assessment.get('age'),
                    'anaemia': assessment.get('anaemia'),
                    'creatinine_phosphokinase': assessment.get('creatinine_phosphokinase'),
                    'diabetes': assessment.get('diabetes'),
                    'ejection_fraction': assessment.get('ejection_fraction'),
                    'high_blood_pressure': assessment.get('high_blood_pressure'),
                    'platelets': assessment.get('platelets'),
                    'serum_creatinine': assessment.get('serum_creatinine'),
                    'serum_sodium': assessment.get('serum_sodium'),
                    'sex': assessment.get('sex'),
                    'smoking': assessment.get('smoking'),
                    'time': assessment.get('time')
                },
                'probability': assessment.get('probability'),
                'risk_category': assessment.get('risk_category'),
                'created_at': assessment.get('created_at')
            })
        
        return results
        
    except Exception as e:
        print(f"Error fetching all assessments: {e}")
        return []

def get_assessments_paginated(page=1, per_page=10, risk=None, username=None, start_date=None, end_date=None):
    """
    Get paginated assessments with optional filters.
    
    Args:
        page: Page number (1-indexed)
        per_page: Results per page
        risk: Filter by risk_category ('LOW', 'MEDIUM', 'HIGH')
        username: Filter by patient username (substring match)
        start_date: Filter assessments from this date
        end_date: Filter assessments until this date
    
    Returns:
        dict with 'assessments' list and 'total' count
    """
    try:
        db = get_db()
        
        # Build filter query
        filter_query = {}
        
        if risk:
            filter_query['risk_category'] = risk
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter['$gte'] = start_date
            if end_date:
                date_filter['$lte'] = end_date
            if date_filter:
                filter_query['created_at'] = date_filter
        
        # Get total count
        total = db[COLLECTION_ASSESSMENTS].count_documents(filter_query)
        
        # Parse pagination params
        try:
            page = max(1, int(page))
            per_page = max(1, int(per_page))
        except:
            page = 1
            per_page = 10
        
        skip = (page - 1) * per_page
        
        # Query with pagination
        assessments = db[COLLECTION_ASSESSMENTS].find(filter_query).sort(
            'created_at', -1
        ).skip(skip).limit(per_page)
        
        results = []
        for assessment in assessments:
            user_id = assessment['user_id']
            user = db[COLLECTION_USERS].find_one({'_id': user_id})
            uname = user['username'] if user else 'Unknown'
            
            # Apply username filter if specified
            if username and username.lower() not in uname.lower():
                continue
            
            results.append({
                'id': str(assessment['_id']),
                'user_id': str(user_id),
                'username': uname,
                'features': {
                    'age': assessment.get('age'),
                    'anaemia': assessment.get('anaemia'),
                    'creatinine_phosphokinase': assessment.get('creatinine_phosphokinase'),
                    'diabetes': assessment.get('diabetes'),
                    'ejection_fraction': assessment.get('ejection_fraction'),
                    'high_blood_pressure': assessment.get('high_blood_pressure'),
                    'platelets': assessment.get('platelets'),
                    'serum_creatinine': assessment.get('serum_creatinine'),
                    'serum_sodium': assessment.get('serum_sodium'),
                    'sex': assessment.get('sex'),
                    'smoking': assessment.get('smoking'),
                    'time': assessment.get('time')
                },
                'probability': assessment.get('probability'),
                'risk_category': assessment.get('risk_category'),
                'created_at': assessment.get('created_at')
            })
        
        return {'assessments': results, 'total': total}
        
    except Exception as e:
        print(f"Error fetching paginated assessments: {e}")
        return {'assessments': [], 'total': 0}

def get_assessments_filtered(risk=None, username=None, start_date=None, end_date=None):
    """
    Get all assessments matching optional filters (no pagination).
    Used for CSV export.
    
    Returns:
        list of assessment dicts
    """
    try:
        db = get_db()
        
        # Build filter query
        filter_query = {}
        
        if risk:
            filter_query['risk_category'] = risk
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter['$gte'] = start_date
            if end_date:
                date_filter['$lte'] = end_date
            if date_filter:
                filter_query['created_at'] = date_filter
        
        # Query and collect all matching assessments
        assessments = db[COLLECTION_ASSESSMENTS].find(filter_query).sort('created_at', -1)
        
        results = []
        for assessment in assessments:
            user_id = assessment['user_id']
            user = db[COLLECTION_USERS].find_one({'_id': user_id})
            uname = user['username'] if user else 'Unknown'
            
            # Apply username filter if specified
            if username and username.lower() not in uname.lower():
                continue
            
            results.append({
                'id': str(assessment['_id']),
                'user_id': str(user_id),
                'username': uname,
                'features': {
                    'age': assessment.get('age'),
                    'anaemia': assessment.get('anaemia'),
                    'creatinine_phosphokinase': assessment.get('creatinine_phosphokinase'),
                    'diabetes': assessment.get('diabetes'),
                    'ejection_fraction': assessment.get('ejection_fraction'),
                    'high_blood_pressure': assessment.get('high_blood_pressure'),
                    'platelets': assessment.get('platelets'),
                    'serum_creatinine': assessment.get('serum_creatinine'),
                    'serum_sodium': assessment.get('serum_sodium'),
                    'sex': assessment.get('sex'),
                    'smoking': assessment.get('smoking'),
                    'time': assessment.get('time')
                },
                'probability': assessment.get('probability'),
                'risk_category': assessment.get('risk_category'),
                'created_at': assessment.get('created_at')
            })
        
        return results
        
    except Exception as e:
        print(f"Error fetching filtered assessments: {e}")
        return []

def get_patient_profile(patient_id):
    """
    Get a patient's profile and all their assessments.
    
    Args:
        patient_id: MongoDB ObjectId or string ID
    
    Returns:
        dict with patient info and assessment list, or None
    """
    try:
        db = get_db()
        
        # Convert string ID to ObjectId if needed
        if isinstance(patient_id, str):
            patient_id = ObjectId(patient_id)
        
        # Get patient user info
        patient = db[COLLECTION_USERS].find_one({'_id': patient_id, 'role': 'patient'})
        
        if not patient:
            return None
        
        # Get all assessments for this patient
        assessments_cursor = db[COLLECTION_ASSESSMENTS].find(
            {'user_id': patient_id}
        ).sort('created_at', -1)
        
        assessments = []
        for a in assessments_cursor:
            assessments.append({
                'id': str(a['_id']),
                'age': a.get('age'),
                'anaemia': a.get('anaemia'),
                'creatinine_phosphokinase': a.get('creatinine_phosphokinase'),
                'diabetes': a.get('diabetes'),
                'ejection_fraction': a.get('ejection_fraction'),
                'high_blood_pressure': a.get('high_blood_pressure'),
                'platelets': a.get('platelets'),
                'serum_creatinine': a.get('serum_creatinine'),
                'serum_sodium': a.get('serum_sodium'),
                'sex': a.get('sex'),
                'smoking': a.get('smoking'),
                'time': a.get('time'),
                'probability': a.get('probability'),
                'risk_category': a.get('risk_category'),
                'created_at': a.get('created_at')
            })
        
        return {
            'id': str(patient['_id']),
            'username': patient['username'],
            'email': patient.get('email'),
            'registered': patient.get('created_at'),
            'predictions': assessments
        }
        
    except Exception as e:
        print(f"Error fetching patient profile: {e}")
        return None

def update_user_profile(user_id, new_username=None, new_email=None, new_password=None):
    """
    Update user profile information in MongoDB.
    
    Args:
        user_id: MongoDB ObjectId or string ID
        new_username: New username (optional)
        new_email: New email (optional)
        new_password: New password to hash (optional)
    
    Returns:
        (success: bool, message: str)
    """
    try:
        db = get_db()
        
        # Convert string ID to ObjectId if needed
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        # Check username uniqueness if changing
        if new_username:
            existing = db[COLLECTION_USERS].find_one({
                'username': new_username,
                '_id': {'$ne': user_id}
            })
            if existing:
                return False, 'Username already taken'
        
        # Check email uniqueness if changing
        if new_email:
            existing = db[COLLECTION_USERS].find_one({
                'email': new_email,
                '_id': {'$ne': user_id}
            })
            if existing:
                return False, 'Email already taken'
        
        # Build update dict
        update_doc = {'updated_at': datetime.utcnow()}
        
        if new_username:
            if len(new_username) < 3:
                return False, 'Username must be at least 3 characters'
            update_doc['username'] = new_username
        
        if new_email is not None:
            update_doc['email'] = new_email
        
        if new_password:
            if len(new_password) < 6:
                return False, 'Password must be at least 6 characters'
            update_doc['password_hash'] = generate_password_hash(new_password)
        
        if len(update_doc) == 1:  # Only updated_at
            return True, 'No changes'
        
        # Update user document
        result = db[COLLECTION_USERS].update_one(
            {'_id': user_id},
            {'$set': update_doc}
        )
        
        if result.matched_count == 0:
            return False, 'User not found'
        
        return True, 'Profile updated successfully'
        
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False, str(e)

# ===== DECORATORS =====

def login_required(f):
    """Decorator to require user login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def patient_required(f):
    """Decorator to require patient role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'patient':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    """Decorator to require doctor role."""
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

# Load feature names from dataset
try:
    df_header = pd.read_csv(DATA_PATH, nrows=0)
    target_col = "DEATH_EVENT" if "DEATH_EVENT" in df_header.columns else df_header.columns[-1]
    FEATURE_NAMES = [c for c in df_header.columns if c != target_col]
    print(f"✓ Features loaded: {len(FEATURE_NAMES)} parameters")
except:
    FEATURE_NAMES = []
    print("⚠ Could not load features from dataset")

# Load feature importance if available
FEATURE_IMPORTANCE = None
try:
    FEATURE_IMPORTANCE = pd.read_csv(BASE_DIR / "feature_importance.csv")
except:
    pass

# ===== UTILITY FUNCTIONS =====

def get_risk_category(probability):
    """
    Categorize CAD risk level based on prediction probability.
    
    Args:
        probability: float between 0 and 1
    
    Returns:
        (category: str, color: str) - category is LOW/MEDIUM/HIGH
    """
    if probability < 0.33:
        return "LOW", "#27ae60"  # Green
    elif probability < 0.67:
        return "MEDIUM", "#f39c12"  # Orange
    else:
        return "HIGH", "#e74c3c"  # Red

def get_recommendation(risk_category):
    """
    Get medical recommendation based on risk category.
    
    Args:
        risk_category: 'LOW', 'MEDIUM', 'HIGH', or 'ERROR'
    
    Returns:
        str with recommendation text
    """
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
    """Home page - redirect based on user role."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    else:
        return redirect(url_for('patient_dashboard'))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login route for both patients and doctors."""
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template("login.html", error="Username and password required")
        
        success, user_info = login_user(username, password)
        
        if success:
            # Start persistent session
            session.permanent = True
            session['user_id'] = str(user_info['user_id'])  # Store as string
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
    """Role selection page."""
    return render_template("register.html")

@app.route("/register_patient", methods=["GET", "POST"])
def register_patient():
    """Patient registration route."""
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
    """Doctor registration route."""
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
    """Logout route - clears session."""
    session.clear()
    return redirect(url_for('login'))

@app.route("/patient/dashboard")
@patient_required
def patient_dashboard():
    """Patient dashboard - shows their CAD assessments."""
    assessments = get_patient_assessments(session['user_id'])
    return render_template("patient_dashboard.html", 
                         username=session['username'],
                         predictions=assessments)

@app.route("/patient/predict", methods=["GET", "POST"])
@patient_required
def patient_predict():
    """Patient prediction form and processing."""
    if request.method == "POST":
        if model is None or scaler is None:
            return render_template("predict.html", 
                                 error="Model not loaded",
                                 username=session['username'])
        
        try:
            # Collect medical features from form
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
            
            # Make prediction using ML model
            data_scaled = scaler.transform([data])
            probability = float(model.predict_proba(data_scaled)[0][1])
            risk_category, risk_color = get_risk_category(probability)
            
            # Save assessment to MongoDB
            save_assessment(session['user_id'], features_input, probability, risk_category)
            
            # Prepare result for display
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
    """Doctor dashboard - shows all patients and their assessment counts."""
    patients = get_all_patients()
    return render_template("doctor_dashboard.html",
                         username=session['username'],
                         patients=patients)

@app.route("/doctor/patient/<patient_id>")
@doctor_required
def doctor_patient_details(patient_id):
    """Doctor view - patient details and all their assessments."""
    patient = get_patient_profile(patient_id)
    
    if not patient:
        return render_template("doctor_dashboard.html",
                             username=session['username'],
                             error="Patient not found")
    
    # Render patient details template with template-compatible variables
    return render_template("patient_details.html",
                         username=session['username'],
                         patient_name=patient.get('username'),
                         patient_email=patient.get('email'),
                         patient_created_at=patient.get('registered'),
                         total_predictions=len(patient.get('predictions', [])),
                         predictions=patient.get('predictions', []))

@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    """
    Profile page for logged-in user.
    Returns profile editing form or JSON user data.
    """
    user_id = session.get('user_id')
    
    try:
        user = get_user_info(user_id)
        
        if not user:
            return redirect(url_for('logout'))
        
        # Return JSON if requested
        if request.args.get('json') == '1':
            return jsonify({'user': user})
        
        # Render profile editing page
        return render_template('profile.html', username=session.get('username'))
        
    except Exception as e:
        print(f"Error loading profile: {e}")
        return redirect(url_for('login'))

@app.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    """
    Update logged-in user's profile information.
    Expects JSON: { username, email, password, confirm_password }
    Returns JSON: { success: bool, message: str }
    """
    user_id = session.get('user_id')
    
    try:
        # Parse request data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid request payload'}), 400
    
    # Extract and validate fields
    new_username = data.get('username', '').strip() if data.get('username') else None
    new_email = data.get('email') if 'email' in data else None
    new_password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    # Validate password if provided
    if new_password:
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
    
    # Validate username if provided
    if new_username:
        if len(new_username) < 3:
            return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
    
    # Update profile in MongoDB
    success, message = update_user_profile(
        user_id,
        new_username=new_username if new_username else None,
        new_email=new_email,
        new_password=new_password if new_password else None
    )
    
    if success:
        # Update session username if changed
        if new_username:
            session['username'] = new_username
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message}), 400

@app.route("/doctor/assessments")
@doctor_required
def doctor_assessments():
    """
    Doctor API endpoint returning all patient assessments as JSON.
    Supports pagination and filtering by risk, username, or date range.
    """
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    risk = request.args.get('risk')
    username = request.args.get('username')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    data = get_assessments_paginated(
        page=page,
        per_page=per_page,
        risk=risk,
        username=username,
        start_date=start_date,
        end_date=end_date
    )
    
    assessments = data.get('assessments', [])
    total = data.get('total', 0)
    
    try:
        page = int(page)
        per_page = int(per_page)
    except:
        page = 1
        per_page = 10
    
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    return jsonify({
        'assessments': assessments,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    })

@app.route('/doctor/assessments.csv')
@doctor_required
def doctor_assessments_csv():
    """
    Export all assessments as CSV file for doctors.
    Supports filtering by risk, username, or date range.
    """
    risk = request.args.get('risk')
    username = request.args.get('username')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    assessments = get_assessments_filtered(
        risk=risk,
        username=username,
        start_date=start_date,
        end_date=end_date
    )
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    headers = [
        'id', 'user_id', 'username', 'created_at', 'probability', 'risk_category',
        'age', 'anaemia', 'creatinine_phosphokinase', 'diabetes', 'ejection_fraction',
        'high_blood_pressure', 'platelets', 'serum_creatinine', 'serum_sodium',
        'sex', 'smoking', 'time'
    ]
    writer.writerow(headers)
    
    # Write assessment rows
    for a in assessments:
        f = a.get('features', {})
        row = [
            a.get('id'),
            a.get('user_id'),
            a.get('username'),
            a.get('created_at'),
            a.get('probability'),
            a.get('risk_category'),
            f.get('age'),
            f.get('anaemia'),
            f.get('creatinine_phosphokinase'),
            f.get('diabetes'),
            f.get('ejection_fraction'),
            f.get('high_blood_pressure'),
            f.get('platelets'),
            f.get('serum_creatinine'),
            f.get('serum_sodium'),
            f.get('sex'),
            f.get('smoking'),
            f.get('time')
        ]
        writer.writerow(row)
    
    csv_data = output.getvalue()
    output.close()
    
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=patient_assessments.csv'}
    )

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template("login.html", error="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    print(f"Server error: {error}")
    return render_template("login.html", error="Server error. Please try again."), 500

# ===== MAIN APP STARTUP =====

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CAD Prediction System - MongoDB Atlas Edition")
    print("=" * 80)
    
    # Initialize MongoDB connection
    if init_mongodb():
        print(f"Running on: http://127.0.0.1:5000")
        print("=" * 80 + "\n")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("✗ Failed to start: MongoDB connection failed")
        print("Please check your MONGODB_URL configuration")
        print("=" * 80 + "\n")
