"""
Advanced Machine Learning Model for CAD Prediction
Includes multiple algorithms, hyperparameter tuning, and cross-validation
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_validate, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report, roc_curve, auc
)
import warnings
warnings.filterwarnings('ignore')

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "dataset" / "heart.csv"
MODEL_PATH = BASE_DIR / "best_cad_model.pkl"
SCALER_PATH = BASE_DIR / "scaler.pkl"
METRICS_PATH = BASE_DIR / "model_metrics.pkl"

print("=" * 80)
print("CAD PREDICTION SYSTEM - ADVANCED ML MODEL TRAINING")
print("=" * 80)

# Load and prepare data
print("\n[1] Loading dataset...")
data = pd.read_csv(DATA_PATH)
print(f"   Dataset shape: {data.shape}")
print(f"   Columns: {list(data.columns)}")

# Identify target column
target_col = "DEATH_EVENT" if "DEATH_EVENT" in data.columns else data.columns[-1]
X = data.drop(target_col, axis=1)
y = data[target_col]

print(f"   Target column: {target_col}")
print(f"   Features: {list(X.columns)}")
print(f"   Class distribution:\n{y.value_counts()}")

# Preprocessing
print("\n[2] Preprocessing data...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

# Train-test split (80-20)
print("   Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   Train set: {X_train.shape[0]} samples")
print(f"   Test set: {X_test.shape[0]} samples")

# Define models with hyperparameter grids
models_config = {
    'Logistic Regression': {
        'model': LogisticRegression(random_state=42, max_iter=1000),
        'params': {
            'C': [0.001, 0.01, 0.1, 1, 10],
            'penalty': ['l2'],
            'solver': ['lbfgs']
        }
    },
    'Random Forest': {
        'model': RandomForestClassifier(random_state=42, n_jobs=-1),
        'params': {
            'n_estimators': [100, 200, 300],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
    },
    'SVM': {
        'model': SVC(random_state=42, probability=True),
        'params': {
            'C': [0.1, 1, 10, 100],
            'kernel': ['rbf', 'linear'],
            'gamma': ['scale', 'auto']
        }
    }
}

# Hyperparameter tuning and model evaluation
print("\n[3] Hyperparameter Tuning & Cross-Validation (k-fold=5)...")
print("-" * 80)

results = {}
best_model = None
best_score = 0
best_model_name = None

for model_name, config in models_config.items():
    print(f"\n   Training {model_name}...")
    
    # GridSearchCV
    grid_search = GridSearchCV(
        config['model'],
        config['params'],
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring='f1',
        n_jobs=-1,
        verbose=0
    )
    
    grid_search.fit(X_train, y_train)
    best_params = grid_search.best_params_
    cv_score = grid_search.best_score_
    
    print(f"   ✓ Best parameters: {best_params}")
    print(f"   ✓ Best CV F1-Score: {cv_score:.4f}")
    
    # Evaluate on test set
    y_pred = grid_search.predict(X_test)
    y_pred_proba = grid_search.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    results[model_name] = {
        'model': grid_search.best_estimator_,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc,
        'confusion_matrix': confusion_matrix(y_test, y_pred),
        'y_pred_proba': y_pred_proba
    }
    
    print(f"   ✓ Test Accuracy:  {accuracy:.4f}")
    print(f"   ✓ Test Precision: {precision:.4f}")
    print(f"   ✓ Test Recall:    {recall:.4f}")
    print(f"   ✓ Test F1-Score:  {f1:.4f}")
    print(f"   ✓ Test ROC-AUC:   {roc_auc:.4f}")
    
    # Track best model (using F1 as primary metric)
    if f1 > best_score:
        best_score = f1
        best_model = grid_search.best_estimator_
        best_model_name = model_name

# Summary and save
print("\n" + "=" * 80)
print("MODEL COMPARISON SUMMARY")
print("=" * 80)

print(f"\n{'Model':<20} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'ROC-AUC':<12}")
print("-" * 80)

for model_name in sorted(results.keys()):
    metrics = results[model_name]
    print(f"{model_name:<20} {metrics['accuracy']:<12.4f} {metrics['precision']:<12.4f} "
          f"{metrics['recall']:<12.4f} {metrics['f1']:<12.4f} {metrics['roc_auc']:<12.4f}")

print("-" * 80)
print(f"\n🏆 BEST MODEL: {best_model_name} (F1-Score: {best_score:.4f})")

# Save best model
print("\n[4] Saving best model and scaler...")
with MODEL_PATH.open("wb") as f:
    pickle.dump(best_model, f)

with SCALER_PATH.open("wb") as f:
    pickle.dump(scaler, f)

with METRICS_PATH.open("wb") as f:
    pickle.dump(results, f)

print(f"   ✓ Model saved: {MODEL_PATH}")
print(f"   ✓ Scaler saved: {SCALER_PATH}")
print(f"   ✓ Metrics saved: {METRICS_PATH}")

# Feature importance (for tree-based models)
print("\n[5] Feature Importance Analysis...")
if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 5 Most Important Features:")
    for idx, row in feature_importance.head(5).iterrows():
        print(f"   {row['feature']}: {row['importance']:.4f}")
    
    # Save feature importance
    feature_importance.to_csv(BASE_DIR / "feature_importance.csv", index=False)
    print(f"\n   ✓ Feature importance saved: {BASE_DIR / 'feature_importance.csv'}")

print("\n" + "=" * 80)
print("✓ MODEL TRAINING COMPLETE!")
print("=" * 80)
