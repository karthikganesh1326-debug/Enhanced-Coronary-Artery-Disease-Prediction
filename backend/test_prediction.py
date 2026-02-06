import pickle
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent
MODEL_PATH = BASE / "cad_model.pkl"
SCALER_PATH = BASE / "scaler.pkl"
DATA_PATH = BASE.parent / "dataset" / "heart.csv"

with SCALER_PATH.open("rb") as f:
    scaler = pickle.load(f)
with MODEL_PATH.open("rb") as f:
    model = pickle.load(f)

data = pd.read_csv(DATA_PATH)
if "target" in data.columns:
    target_col = "target"
elif "DEATH_EVENT" in data.columns:
    target_col = "DEATH_EVENT"
else:
    target_col = data.columns[-1]

sample = data.drop(target_col, axis=1).iloc[0].values
sample_scaled = scaler.transform([sample])
pred = model.predict(sample_scaled)
print("Prediction for first dataset row:", int(pred[0]))
