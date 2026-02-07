# Coronary Artery Disease (CAD) Prediction System

A professional, production-ready machine learning system for predicting Coronary Artery Disease risk. Built with multiple algorithms, comprehensive hyperparameter tuning, cloud-based MongoDB database, and multi-user authentication with a modern healthcare-focused web interface.

## ✨ What's New (v2.0)

### Cloud Database Integration
- **MongoDB Atlas**: Cloud-based data persistence for multi-machine access
- **User Accounts**: Registration and authentication system
- **Role-Based Access**: Patient and Doctor user roles
- **Data Security**: Werkzeug password hashing (PBKDF2)
- **Profile Management**: User-specific patient and doctor profiles
- **Prediction History**: Track assessments per user

## Features

### Machine Learning
- **Multiple Algorithms**: Logistic Regression, Random Forest, and SVM
- **Hyperparameter Tuning**: GridSearchCV for optimal model configuration
- **Cross-Validation**: 5-fold stratified k-fold validation to prevent overfitting
- **Preprocessing**: StandardScaler normalization and stratified train-test split
- **Performance Metrics**: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- **Feature Importance**: Identifies most influential health factors
- **Model Comparison**: Detailed metrics for all algorithms

### Authentication & User Management
- **Registration**: Patient and Doctor user registration
- **Secure Authentication**: Email/password login with session management
- **Multi-Role Support**: Different dashboards for patients and doctors
- **User Profiles**: Persistent user data in MongoDB Atlas
- **Access Control**: Role-based dashboard access
- **Session Management**: HttpOnly, SameSite=Strict cookie security

### Backend (Flask API)
- **REST Endpoints**: Multiple endpoints for predictions and data retrieval
- **Risk Categorization**: Three-tier risk assessment (Low/Medium/High)
- **Probability Prediction**: Returns CAD probability with confidence
- **Prediction Logging**: All predictions saved to MongoDB with user tracking
- **JSON API**: Integration-ready endpoints for third-party systems
- **Error Handling**: Comprehensive error messages and validation
- **MongoDB Integration**: Cloud database for scalable data storage

### Frontend (HTML/CSS)
- **Professional Design**: Healthcare-themed blue, white, and green color scheme
- **Responsive Layout**: Fully mobile-responsive design
- **Clean Interface**: Intuitive forms with clear labels and tooltips
- **Result Display**: Color-coded risk categories with recommendations
- **User Dashboards**: Patient and Doctor specific interfaces
- **Navigation**: Home, Register, Login, Predict, Profile, and About pages
- **Accessibility**: Semantic HTML5 and proper structure

## Project Structure

```
CAD_Prediction_System/
├── backend/
│   ├── app_mongodb.py           # Flask + MongoDB (RECOMMENDED - Production)
│   ├── app.py                   # Legacy Flask + SQLite version
│   ├── ml_model.py              # Model training with multiple algorithms
│   ├── model.py                 # Alternative model implementation
│   ├── best_cad_model.pkl       # Trained Random Forest model
│   ├── scaler.pkl               # Feature scaler
│   ├── model_metrics.pkl        # Model comparison metrics
│   ├── feature_importance.csv   # Feature importance rankings
│   ├── predictions.csv          # Prediction audit log (old version)
│   ├── test_mongodb.py          # MongoDB integration tests
│   ├── test_prediction.py       # Prediction testing utilities
│   └── test_auth.py             # Authentication tests
├── frontend/
│   ├── static/
│   │   └── style.css            # Responsive styling
│   └── templates/
│       ├── base.html            # Base template with navbar
│       ├── index.html           # Home page
│       ├── login.html           # User login form
│       ├── register_patient.html # Patient registration
│       ├── register_doctor.html  # Doctor registration
│       ├── predict.html          # CAD prediction form
│       ├── prediction_result.html # Results display
│       ├── patient_dashboard.html # Patient dashboard
│       ├── doctor_dashboard.html  # Doctor dashboard
│       ├── profile.html          # User profile page
│       ├── about.html            # System information
│       └── (other templates)
├── dataset/
│   └── heart.csv                # Heart disease dataset (299 samples)
├── .env                         # Environment variables (MongoDB credentials)
├── .env.example                 # Environment template (credentials removed)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── DOCUMENTATION_INDEX.md       # ⭐ Master documentation guide
├── QUICK_VERIFICATION_GUIDE.md  # Step-by-step testing guide
├── MONGODB_REGISTRATION_LOGIN_FIX.md # Detailed fix explanation
├── FIXES_SUMMARY.md             # Technical changes summary
├── CODE_CHANGES_BEFORE_AFTER.md # Code review with comparisons
├── MONGODB_ATLAS_NAVIGATION.md  # Visual guide to MongoDB Atlas
├── MONGODB_FIX_EXECUTIVE_SUMMARY.md # High-level overview
└── FILES_MODIFIED_AND_DOCUMENTATION.md # Complete change log
```

## Quick Start

### Option 1: MongoDB Atlas Version (Recommended for Production)

#### 1. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

#### 2. Configure MongoDB Atlas

1. Create a MongoDB Atlas account at https://www.mongodb.com/cloud/atlas
2. Create a free M0 cluster
3. Copy your connection string
4. Update `.env` file:
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/cad_prediction_db?retryWrites=true&w=majority&appName=cadprediction1
   ```
5. **Important:** Replace credentials and cluster name in your `.env` file

#### 3. Train the Model

```bash
cd backend
python ml_model.py
```

#### 4. Start the MongoDB-Enabled Application

```bash
cd backend
python app_mongodb.py
```

The server will start at: **http://127.0.0.1:5000**

#### 5. Access the System

Open your browser and navigate to:
- **Home/Login**: http://127.0.0.1:5000/ (redirects to login)
- **Register Patient**: http://127.0.0.1:5000/register_patient
- **Register Doctor**: http://127.0.0.1:5000/register_doctor
- **Patient Dashboard**: http://127.0.0.1:5000/patient_dashboard (after login)
- **Doctor Dashboard**: http://127.0.0.1:5000/doctor_dashboard (after login)

---

### Option 2: SQLite Version (Legacy - Single Machine Only)

#### 1. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

#### 2. Train the Model

```bash
cd backend
python ml_model.py
```

#### 3. Start the Local Application

```bash
cd backend
python app.py
```

The server will start at: **http://127.0.0.1:5000**

#### 4. Access the System

Open your browser and navigate to:
- **Home/Prediction**: http://127.0.0.1:5000/
- **About**: http://127.0.0.1:5000/about

## Model Performance

### Best Model: Random Forest

| Metric | Score |
|--------|-------|
| Accuracy | 83.33% |
| Precision | 80.00% |
| Recall | 63.16% |
| F1-Score | 70.59% |
| ROC-AUC | 91.01% |

### Algorithm Comparison

| Model | Accuracy | F1-Score | ROC-AUC |
|-------|----------|----------|---------|
| Random Forest | 83.33% | 70.59% | 91.01% |
| Logistic Regression | 81.67% | 66.67% | 86.01% |
| SVM | 78.33% | 55.17% | 85.62% |

### Top 5 Contributing Features

1. **Follow-up Time** (0.4534) - Most important predictor
2. **Serum Creatinine** (0.1603) - Kidney function marker
3. **Ejection Fraction** (0.1380) - Heart pump efficiency
4. **Age** (0.0664) - Patient age
5. **CPK** (0.0551) - Enzyme level

---

## MongoDB Atlas Setup

### Prerequisites

- MongoDB Atlas account (free at https://www.mongodb.com/cloud/atlas)
- Free M0 cluster (0-512 MB storage)
- Network access from your machine

### Setup Steps

1. **Create MongoDB Atlas Cluster**
   - Go to: https://www.mongodb.com/cloud/atlas
   - Sign up or login
   - Create new cluster
   - Select: M0 Free Tier
   - Choose region closest to you

2. **Get Connection String**
   - Click: "Connect" button on cluster
   - Choose: "Connect your application"
   - Copy the connection string
   - It should include `mongodb+srv://`

3. **Create `.env` File**
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/cad_prediction_db?retryWrites=true&w=majority&appName=cadprediction1
   FLASK_SECRET_KEY=your-secret-key
   ```

4. **Verify Connection**
   - Start app: `python app_mongodb.py`
   - Should see: "✓ MONGODB ATLAS CONNECTION SUCCESSFUL!"

### Accessing Your Data

1. Go to: https://cloud.mongodb.com
2. Click: "Browse Collections"
3. Select database: `cad_prediction_db`
4. View collections:
   - `users` - User accounts and credentials
   - `patient_profiles` - Patient-specific data
   - `doctor_profiles` - Doctor-specific data
   - `assessments` - CAD predictions and history

---

## Authentication System

### User Registration

**Patient Registration**: `/register_patient`
- Username (3+ characters)
- Email address
- Password (6+ characters)
- Creates patient profile in MongoDB

**Doctor Registration**: `/register_doctor`
- Username (3+ characters)
- Email address
- Password (6+ characters)
- Creates doctor profile in MongoDB

### User Login

**Login Page**: `/login`
- Username or email
- Password (case-sensitive)
- Session-based authentication
- Redirects to appropriate dashboard

### User Roles

**Patient Dashboard** (`/patient_dashboard`)
- View personal CAD risk assessment
- Input health parameters
- Get risk predictions
- View personal recommendation history
- Manage profile

**Doctor Dashboard** (`/doctor_dashboard`)
- View patient referrals
- Access team assessment tools
- Monitor CAD risk trends
- Patient management interface

---

## Documentation

### Complete Documentation Guides

| Document | Purpose | Best For |
|----------|---------|----------|
| **DOCUMENTATION_INDEX.md** | Navigation guide to all files | Finding what you need |
| **QUICK_VERIFICATION_GUIDE.md** | Step-by-step testing | Verifying the system works |
| **MONGODB_REGISTRATION_LOGIN_FIX.md** | Detailed technical explanation | Understanding the implementation |
| **MONGODB_ATLAS_NAVIGATION.md** | Visual guide to MongoDB Atlas | Viewing data in the cloud |
| **CODE_CHANGES_BEFORE_AFTER.md** | Side-by-side code comparison | Code review |

**Start here:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

The system analyzes 12 patient health indicators:

| Parameter | Type | Range | Unit |
|-----------|------|-------|------|
| **age** | numeric | 0-120 | years |
| **sex** | binary | 0/1 | Female/Male |
| **anaemia** | binary | 0/1 | No/Yes |
| **creatinine_phosphokinase** | numeric | 0+ | mcg/L |
| **diabetes** | binary | 0/1 | No/Yes |
| **ejection_fraction** | numeric | 0-100 | % |
| **high_blood_pressure** | binary | 0/1 | No/Yes |
| **platelets** | numeric | 0+ | kiloplatelets/mL |
| **serum_creatinine** | numeric | 0+ | mg/dL |
| **serum_sodium** | numeric | 100-160 | mEq/L |
| **smoking** | binary | 0/1 | Never/Current-Former |
| **time** | numeric | 0+ | days |

## Risk Categories

### LOW RISK (0-33%)
- Continue regular health check-ups
- Maintain healthy lifestyle choices
- No immediate clinical intervention needed

### MEDIUM RISK (33-67%)
- Schedule appointment with cardiologist
- Consider lifestyle modifications
- May need additional diagnostic tests

### HIGH RISK (67-100%)
- URGENT: Consult cardiologist immediately
- Consider advanced cardiac testing
- Implement aggressive risk management

## API Endpoints

### Web Interface
- `GET /` - Home page with prediction form
- `GET /about` - System information and documentation
- `POST /predict` - Submit predictions (form-based)

### JSON API
- `POST /api/predict` - JSON prediction endpoint
- `GET /api/features` - Get required features and descriptions
- `GET /api/predictions-log` - Retrieve recent predictions (admin)

### Example JSON Request

```json
{
  "age": 55,
  "sex": 1,
  "anaemia": 0,
  "creatinine_phosphokinase": 500,
  "diabetes": 0,
  "ejection_fraction": 40,
  "high_blood_pressure": 1,
  "platelets": 250000,
  "serum_creatinine": 1.2,
  "serum_sodium": 137,
  "smoking": 0,
  "time": 7
}
```

### Example JSON Response

```json
{
  "success": true,
  "probability": 42.5,
  "risk_category": "MEDIUM",
  "risk_color": "#f39c12",
  "contributing_features": [
    {
      "feature": "serum_creatinine",
      "importance": 0.1603
    },
    {
      "feature": "ejection_fraction",
      "importance": 0.1380
    }
  ],
  "recommendation": {
    "text": "Schedule appointment with cardiologist for further evaluation.",
    "icon": "⚠"
  }
}
```

## Key Files Explained

### MongoDB Version (Recommended)

#### app_mongodb.py
Flask backend application with MongoDB integration:
- Connects to MongoDB Atlas cloud database
- User registration and authentication
- Role-based access control (Patient/Doctor)
- CAD prediction endpoints
- User profile management
- Detailed logging for debugging
- Session-based security
- Password hashing with werkzeug

#### test_mongodb.py
Comprehensive test suite for MongoDB integration:
- Tests connection to MongoDB Atlas
- Tests user registration
- Tests login authentication
- Tests role-based access
- Tests prediction workflow
- 8/8 tests passing

### Legacy Version (SQLite)

#### app.py
Flask backend with local SQLite database:
- Predictions without user management
- No authentication
- Single machine only
- Simple form-based predictions

## Technologies Used

### Machine Learning
- **scikit-learn** - ML algorithms and preprocessing
- **pandas** - Data manipulation
- **NumPy** - Numerical computing

### Backend
- **Flask** - Web framework for routing and templating
- **Python 3.8+** - Programming language
- **pymongo** - MongoDB driver
- **werkzeug** - Password hashing and security utilities
- **python-dotenv** - Environment variable management

### Database
- **MongoDB Atlas** - Cloud-hosted NoSQL database
- **PyMongo 4.6.0+** - MongoDB Python driver

### Frontend
- **HTML5** - Semantic structure
- **CSS3** - Responsive styling
- **Jinja2** - Server-side template rendering
- **Bootstrap-ready** - Mobile-responsive CSS framework

## Dataset Information

**Source**: Heart Failure Clinical Records Dataset
- **Samples**: 299 patient records
- **Features**: 12 health parameters
- **Target**: DEATH_EVENT (binary: 0=No, 1=Yes)
- **Class Distribution**: 203 No (67.9%), 96 Yes (32.1%)

## Security Considerations

### Data Protection
- Input validation on all form fields and API endpoints
- Type checking for numeric inputs and range validation
- SQL injection prevention (using parametric queries in MongoDB)
- XSS prevention through Jinja2 template escaping

### Authentication & Authorization
- Passwords hashed using werkzeug (PBKDF2 with salt)
- Raw passwords never stored or transmitted in plain text
- Session-based authentication with HTTPOnly cookies
- SameSite=Strict cookie policy for CSRF prevention
- Role-based access control (Patient vs Doctor)
- Session timeout on browser closure

### MongoDB Security
- Connection string requires username and password
- `.env` file contains credentials (NOT in git repository)
- `.env.example` provided as template without credentials
- MongoDB Atlas IP whitelist for network access control
- TLS/SSL encryption for data in transit
- Database isolation per application

### File-Based Storage (Legacy)
- Pickle files stored securely on filesystem
- Model and scaler files protected from unauthorized access
- Prediction logs saved for audit trails

### Additional Security Measures
- No sensitive information in error messages
- Unique indexes on username and email prevent duplicates
- Password minimum requirements (6+ characters)
- Rate limiting recommended for production deployment
- HTTPS recommended for production

## Files Generated

After training and predictions:

1. **best_cad_model.pkl** - Trained Random Forest model
2. **scaler.pkl** - Feature standardization scaler
3. **model_metrics.pkl** - Detailed performance metrics
4. **feature_importance.csv** - Feature importance rankings
5. **predictions.csv** - Log of all predictions made

## Important Medical Disclaimer

**THIS SYSTEM IS FOR INFORMATIONAL AND EDUCATIONAL PURPOSES ONLY.**

The predictions generated by this machine learning system:
- Should NOT be used as a substitute for professional medical diagnosis
- Should NOT replace consultation with qualified healthcare providers
- May not account for all factors affecting CAD risk in individuals
- Require validation by medical professionals

**Always consult with qualified cardiologists and healthcare professionals before making any medical decisions.**

## Contributing

### Completed Features
- ✅ User authentication with role-based access
- ✅ MongoDB Atlas cloud database integration
- ✅ Patient and Doctor dashboards
- ✅ Multi-algorithm comparison
- ✅ Comprehensive logging and debugging
- ✅ Responsive mobile design

### Future Improvements
1. Advanced algorithms (XGBoost, Neural Networks)
2. SHAP/LIME for explainable AI
3. Patient history tracking and trends
4. Doctor-patient messaging system
5. DICOM image analysis for cardiac imaging
6. Mobile app (React/Flutter)
7. Advanced analytics dashboard
8. Integration with EHR systems

## References

- Scikit-learn Documentation: https://scikit-learn.org/
- Flask Documentation: https://flask.palletsprojects.com/
- Heart Disease Dataset: https://archive.ics.uci.edu/
- CAD Epidemiology: Standard medical literature

## Support

For issues or questions:

### Getting Help

1. **Quick Setup Issues:**
   - Read: [QUICK_VERIFICATION_GUIDE.md](QUICK_VERIFICATION_GUIDE.md)
   - Follow step-by-step verification procedures

2. **MongoDB Connection Issues:**
   - Read: [MONGODB_ATLAS_NAVIGATION.md](MONGODB_ATLAS_NAVIGATION.md)
   - Verify connection string in `.env` file
   - Check MongoDB Atlas IP whitelist settings

3. **Registration/Login Problems:**
   - Read: [MONGODB_REGISTRATION_LOGIN_FIX.md](MONGODB_REGISTRATION_LOGIN_FIX.md)
   - Check console output for detailed error messages
   - Verify database credentials are correct

4. **Understanding the Code:**
   - Read: [CODE_CHANGES_BEFORE_AFTER.md](CODE_CHANGES_BEFORE_AFTER.md)
   - Read: [FIXES_SUMMARY.md](FIXES_SUMMARY.md)

### Troubleshooting Checklist

- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with MongoDB credentials
- [ ] MongoDB Atlas cluster created and running
- [ ] Connection string includes `/cad_prediction_db`
- [ ] IP whitelist includes your machine's IP
- [ ] Model files present: `best_cad_model.pkl`, `scaler.pkl`
- [ ] App starts without import errors
- [ ] Console shows "✓ MONGODB ATLAS CONNECTION SUCCESSFUL!"

## License

Educational and research use. Consult institution for deployment/commercial use.

---

## Project Status

**Version**: 2.0 - MongoDB Atlas Integration  
**Release Date**: February 2026  
**Status**: ✅ Production Ready  

### Key Milestones
- ✅ Phase 1: Core ML model training and evaluation
- ✅ Phase 2: Flask web application with UI
- ✅ Phase 3: MongoDB Atlas cloud integration
- ✅ Phase 4: User authentication and role-based access
- ✅ Phase 5: Comprehensive documentation and testing

[**Start here:** Read DOCUMENTATION_INDEX.md for complete navigation guide](DOCUMENTATION_INDEX.md)
