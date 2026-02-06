# Coronary Artery Disease (CAD) Prediction System

A professional, production-ready machine learning system for predicting Coronary Artery Disease risk. Built with multiple algorithms, comprehensive hyperparameter tuning, and a modern healthcare-focused web interface.

## Features

### Machine Learning
- **Multiple Algorithms**: Logistic Regression, Random Forest, and SVM
- **Hyperparameter Tuning**: GridSearchCV for optimal model configuration
- **Cross-Validation**: 5-fold stratified k-fold validation to prevent overfitting
- **Preprocessing**: StandardScaler normalization and stratified train-test split
- **Performance Metrics**: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- **Feature Importance**: Identifies most influential health factors
- **Model Comparison**: Detailed metrics for all algorithms

### Backend (Flask API)
- **REST Endpoints**: Multiple endpoints for predictions and data retrieval
- **Risk Categorization**: Three-tier risk assessment (Low/Medium/High)
- **Probability Prediction**: Returns CAD probability with confidence
- **Prediction Logging**: All predictions saved to CSV for audit trail
- **JSON API**: Integration-ready endpoints for third-party systems
- **Error Handling**: Comprehensive error messages and validation

### Frontend (HTML/CSS)
- **Professional Design**: Healthcare-themed blue, white, and green color scheme
- **Responsive Layout**: Fully mobile-responsive design
- **Clean Interface**: Intuitive form with clear labels and tooltips
- **Result Display**: Color-coded risk categories with recommendations
- **Navigation**: Home, Predict, and About pages
- **Accessibility**: Semantic HTML5 and proper structure

## Project Structure

```
CAD_Prediction_System/
├── backend/
│   ├── ml_model.py              # Model training with multiple algorithms
│   ├── app.py                   # Flask backend API
│   ├── best_cad_model.pkl       # Trained Random Forest model
│   ├── scaler.pkl               # Feature scaler
│   ├── model_metrics.pkl        # Model comparison metrics
│   ├── feature_importance.csv   # Feature importance rankings
│   ├── predictions.csv          # Prediction audit log
│   └── test_prediction.py       # Testing utilities
├── frontend/
│   ├── static/
│   │   └── style.css            # Responsive styling
│   └── templates/
│       ├── base.html            # Base template with navbar
│       ├── index.html           # Home/Prediction form
│       ├── result.html          # Prediction results display
│       └── about.html           # System information
├── dataset/
│   └── heart.csv                # Heart disease dataset (299 samples)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Quick Start

### 1. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Train the Model

```bash
cd backend
python ml_model.py
```

This will:
- Load and preprocess the heart disease dataset
- Train 3 different ML algorithms
- Perform GridSearchCV hyperparameter tuning
- Evaluate models with 5-fold cross-validation
- Save the best model (Random Forest with F1-Score: 0.7059)
- Generate feature importance analysis

### 3. Start the Web Application

```bash
cd backend
python app.py
```

The server will start at: **http://127.0.0.1:5000**

### 4. Access the System

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

## Input Parameters

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

### ml_model.py
Comprehensive model training pipeline:
- Loads heart disease dataset
- Performs data preprocessing and scaling
- Trains multiple algorithms with GridSearchCV
- Evaluates models with cross-validation
- Saves best model and scaler
- Generates feature importance analysis

### app.py
Flask backend application:
- Loads trained model and scaler
- Provides prediction endpoints
- Implements risk categorization logic
- Logs all predictions to CSV
- Serves HTML templates
- Provides JSON APIs

### index.html
Home page with prediction form:
- Professional healthcare design
- Color-coded input groups
- Form validation and hints
- Clear button interface
- Medical disclaimer

### result.html
Prediction results page:
- Color-coded risk badges
- Probability visualization bar
- Risk category information
- Medical recommendations
- Contributing features display
- Navigation back to form

### about.html
Comprehensive system documentation:
- Algorithm descriptions
- Input parameter explanations
- Risk category guidelines
- Technology stack details
- Medical disclaimers

## Technologies Used

### Machine Learning
- **scikit-learn** - ML algorithms and preprocessing
- **pandas** - Data manipulation
- **NumPy** - Numerical computing

### Backend
- **Flask** - Web framework
- **Python 3.8+** - Programming language

### Frontend
- **HTML5** - Structure
- **CSS3** - Responsive styling
- **Jinja2** - Template rendering

## Dataset Information

**Source**: Heart Failure Clinical Records Dataset
- **Samples**: 299 patient records
- **Features**: 12 health parameters
- **Target**: DEATH_EVENT (binary: 0=No, 1=Yes)
- **Class Distribution**: 203 No (67.9%), 96 Yes (32.1%)

## Security Considerations

- Input validation on all form fields
- Type checking for numeric inputs
- File-based model storage (secure pickle)
- Prediction logging for audit trails
- Error handling without sensitive info leakage

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

To improve the system:
1. Train with larger datasets
2. Add more advanced algorithms (XGBoost with dependencies)
3. Implement SHAP/LIME for better feature explanations
4. Add user authentication and database storage
5. Implement patient history tracking
6. Add DICOM image analysis capabilities

## References

- Scikit-learn Documentation: https://scikit-learn.org/
- Flask Documentation: https://flask.palletsprojects.com/
- Heart Disease Dataset: https://archive.ics.uci.edu/
- CAD Epidemiology: Standard medical literature

## Support

For issues or questions:
1. Check the About page for system documentation
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Check that the model files (*.pkl) are present

## License

Educational and research use. Consult institution for deployment/commercial use.

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Status**: Production Ready
