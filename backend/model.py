import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path

# Resolve paths relative to this file so the script can be run from anywhere
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "dataset" / "heart.csv"
MODEL_PATH = BASE_DIR / "cad_model.pkl"
SCALER_PATH = BASE_DIR / "scaler.pkl"

# Load dataset
data = pd.read_csv(DATA_PATH)

# Determine target column (support common names or fall back to last column)
if "target" in data.columns:
    target_col = "target"
elif "DEATH_EVENT" in data.columns:
    target_col = "DEATH_EVENT"
else:
    target_col = data.columns[-1]

X = data.drop(target_col, axis=1)
y = data[target_col]

# Scaling
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model
with MODEL_PATH.open("wb") as f:
    pickle.dump(model, f)

with SCALER_PATH.open("wb") as f:
    pickle.dump(scaler, f)

print(f"Model trained and saved successfully:\n  {MODEL_PATH}\n  {SCALER_PATH}")
