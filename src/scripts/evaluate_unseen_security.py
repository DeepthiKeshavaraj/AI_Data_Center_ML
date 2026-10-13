from pathlib import Path
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "security"
REPORT_DIR = PROJECT_ROOT / "reports" / "security_model"

TRAIN_FILE = DATA_DIR / "unsw_nb15_UNSW_NB15_training-set(in)_ml_ready.csv"
TEST_FILE = DATA_DIR / "unsw_nb15_UNSW_NB15_testing-set(in)_ml_ready.csv"
PREDICTIONS_FILE = REPORT_DIR / "test_predictions.csv"

FEATURES = [
    "protocol",
    "flow_duration",
    "src_packets",
    "dst_packets",
    "src_bytes",
    "dst_bytes",
    "connection_state",
    "service",
]
CATEGORICAL = ["protocol", "connection_state", "service"]

train = pd.read_csv(TRAIN_FILE, low_memory=False)
test = pd.read_csv(TEST_FILE, low_memory=False)
predictions = pd.read_csv(PREDICTIONS_FILE)

if len(test) != len(predictions):
    raise ValueError(
        "Prediction row count does not match test row count. "
        "Do not evaluate until the row alignment is verified."
    )

# Match the feature normalization used in the earlier overlap check.
for df in (train, test):
    for column in CATEGORICAL:
        df[column] = df[column].fillna("<MISSING>").astype(str)

train_keys = pd.MultiIndex.from_frame(train[FEATURES])
test_keys = pd.MultiIndex.from_frame(test[FEATURES])

# Keep test rows whose feature combination does not occur in training.
unseen_mask = ~test_keys.isin(train_keys)

subset = predictions.loc[unseen_mask].copy()
print("=" * 65)
print("UNSEEN FEATURE-COMBINATION EVALUATION")
print("=" * 65)
print(f"All test rows: {len(test):,}")
print(f"Unseen-feature test rows: {int(unseen_mask.sum()):,}")
print(f"Excluded overlapping-feature test rows: {int((~unseen_mask).sum()):,}")

if subset.empty:
    print("No unseen feature combinations were found.")
else:
    y_true = subset["actual_label"].astype(int)
    y_pred = subset["predicted_label"].astype(int)
    y_prob = subset["attack_probability"]

    print(f"\nAccuracy: {accuracy_score(y_true, y_pred):.4f}")
    print(
        "Balanced accuracy: "
        f"{balanced_accuracy_score(y_true, y_pred):.4f}"
    )

    if y_true.nunique() == 2:
        print(f"ROC-AUC: {roc_auc_score(y_true, y_prob):.4f}")

    print("\nClassification report:")
    print(
        classification_report(
            y_true,
            y_pred,
            labels=[0, 1],
            target_names=["Normal", "Attack"],
            zero_division=0,
        )
    )

    print("Confusion matrix:")
    print(
        pd.DataFrame(
            confusion_matrix(y_true, y_pred, labels=[0, 1]),
            index=["Actual normal", "Actual attack"],
            columns=["Predicted normal", "Predicted attack"],
        )
    )

    subset.to_csv(
        REPORT_DIR / "unseen_feature_predictions.csv",
        index=False,
    )
    print(f"\nSubset predictions saved to: {REPORT_DIR}")

print("\nNo original data has been modified.")