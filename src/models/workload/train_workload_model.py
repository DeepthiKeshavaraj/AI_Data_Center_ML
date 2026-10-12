
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = ROOT / "data/processed/workload/cpu_next_observation.csv"
MODEL_DIR = ROOT / "models/workload"
REPORT_DIR = ROOT / "reports/workload_model"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "machine_cpu",
    "machine_gpu",
    "machine_cpu_usr",
    "machine_cpu_kernel",
    "machine_cpu_iowait",
    "machine_load_1",
    "machine_num_worker",
]

TARGET = "next_machine_cpu"

print("Loading CPU prediction dataset...")
df = pd.read_csv(DATA_PATH)

# Ensure numeric values and remove incomplete feature rows.
for col in FEATURES + [TARGET, "machine", "start_time"]:
    if col in FEATURES + [TARGET]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(
    subset=FEATURES + [TARGET, "machine", "start_time"]
).copy()

# Sort chronologically within each machine.
df = df.sort_values(["machine", "start_time"]).reset_index(drop=True)

# Hold out the latest 20% of observations for each machine.
# This avoids randomly mixing earlier and later observations.
df["position"] = df.groupby("machine").cumcount()
df["machine_count"] = df.groupby("machine")["machine"].transform("size")
df["train_cutoff"] = np.floor(df["machine_count"] * 0.8)

train = df[df["position"] < df["train_cutoff"]].copy()
test = df[df["position"] >= df["train_cutoff"]].copy()

X_train = train[FEATURES]
y_train = train[TARGET]
X_test = test[FEATURES]
y_test = test[TARGET]

print(f"Training rows: {len(train):,}")
print(f"Testing rows: {len(test):,}")
print(f"Features: {FEATURES}")

def evaluate(name, actual, predicted):
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    return {
        "model": name,
        "MAE": float(mean_absolute_error(actual, predicted)),
        "RMSE": float(rmse),
        "R2": float(r2_score(actual, predicted)),
    }

results = []

# Baseline: predict that the next CPU value equals current CPU.
baseline_predictions = X_test["machine_cpu"].to_numpy()
results.append(
    evaluate("Persistence baseline", y_test, baseline_predictions)
)

print("\nTraining Random Forest...")
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=18,
    min_samples_leaf=5,
    n_jobs=-1,
    random_state=42,
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)

results.append(evaluate("Random Forest", y_test, predictions))

results_df = pd.DataFrame(results)
print("\n--- MODEL EVALUATION ---")
print(results_df.to_string(index=False))

results_df.to_csv(REPORT_DIR / "model_comparison.csv", index=False)

joblib.dump(model, MODEL_DIR / "cpu_prediction_random_forest.joblib")

with open(REPORT_DIR / "feature_importance.json", "w") as f:
    json.dump(
        dict(zip(FEATURES, model.feature_importances_.tolist())),
        f,
        indent=2,
    )

print(f"\nModel saved to: {MODEL_DIR}")
print(f"Reports saved to: {REPORT_DIR}")
print("\nTraining complete.")
