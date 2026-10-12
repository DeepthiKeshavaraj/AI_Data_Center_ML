from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    balanced_accuracy_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# --------------------------------------------------
# Paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "security"
REPORT_DIR = PROJECT_ROOT / "reports" / "security_model"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = DATA_DIR / "unsw_nb15_UNSW_NB15_training-set(in)_ml_ready.csv"
TEST_FILE = DATA_DIR / "unsw_nb15_UNSW_NB15_testing-set(in)_ml_ready.csv"

TARGET = "binary_label"

NUMERIC_FEATURES = [
    "flow_duration",
    "src_packets",
    "dst_packets",
    "src_bytes",
    "dst_bytes",
]

CATEGORICAL_FEATURES = [
    "protocol",
    "connection_state",
    "service",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def main():
    # --------------------------------------------------
    # Load data
    # --------------------------------------------------
    train_df = pd.read_csv(TRAIN_FILE, low_memory=False)
    test_df = pd.read_csv(TEST_FILE, low_memory=False)

    required = FEATURES + [TARGET]

    for name, df in [("training", train_df), ("testing", test_df)]:
        missing = sorted(set(required) - set(df.columns))
        if missing:
            raise ValueError(f"{name} data is missing columns: {missing}")

        if df[TARGET].isna().any():
            raise ValueError(f"{name} data contains missing target labels.")

        if not set(df[TARGET].unique()).issubset({0, 1}):
            raise ValueError(f"{name} data has labels other than 0 and 1.")

    X_train = train_df[FEATURES].copy()
    y_train = train_df[TARGET].astype(int)

    X_test = test_df[FEATURES].copy()
    y_test = test_df[TARGET].astype(int)

    # --------------------------------------------------
    # Preprocessing
    # Fit only on training data through the pipeline.
    # --------------------------------------------------
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore"),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    n_jobs=-1,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    # --------------------------------------------------
    # Train
    # --------------------------------------------------
    print("Training Random Forest baseline...")
    print(f"Training rows: {len(X_train):,}")
    print(f"Testing rows:  {len(X_test):,}")
    print(f"Features: {len(FEATURES)}")

    model.fit(X_train, y_train)

    # --------------------------------------------------
    # Evaluate once on the supplied test set
    # --------------------------------------------------
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    print("\n" + "=" * 60)
    print("UNSW-NB15 RANDOM FOREST BASELINE")
    print("=" * 60)

    print(f"Accuracy:          {accuracy_score(y_test, predictions):.4f}")
    print(
        "Balanced accuracy: "
        f"{balanced_accuracy_score(y_test, predictions):.4f}"
    )

    if y_test.nunique() == 2:
        print(f"ROC-AUC:            {roc_auc_score(y_test, probabilities):.4f}")

    print("\nClassification report:")
    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["Normal", "Attack"],
        zero_division=0,
    )
    print(report)

    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])
    matrix_df = pd.DataFrame(
        matrix,
        index=["Actual normal", "Actual attack"],
        columns=["Predicted normal", "Predicted attack"],
    )

    print("\nConfusion matrix:")
    print(matrix_df)

    # --------------------------------------------------
    # Save results
    # --------------------------------------------------
    (REPORT_DIR / "classification_report.txt").write_text(
        report,
        encoding="utf-8",
    )

    matrix_df.to_csv(REPORT_DIR / "confusion_matrix.csv")

    metrics = pd.DataFrame(
        [
            {
                "model": "RandomForest",
                "dataset": "UNSW-NB15",
                "train_rows": len(X_train),
                "test_rows": len(X_test),
                "accuracy": accuracy_score(y_test, predictions),
                "balanced_accuracy": balanced_accuracy_score(
                    y_test, predictions
                ),
                "roc_auc": (
                    roc_auc_score(y_test, probabilities)
                    if y_test.nunique() == 2
                    else None
                ),
            }
        ]
    )

    metrics.to_csv(REPORT_DIR / "metrics.csv", index=False)

    prediction_output = pd.DataFrame(
        {
            "actual_label": y_test.to_numpy(),
            "predicted_label": predictions,
            "attack_probability": probabilities,
        }
    )
    prediction_output.to_csv(
        REPORT_DIR / "test_predictions.csv",
        index=False,
    )

    print(f"\nReports saved to: {REPORT_DIR}")
    print("Baseline training and evaluation complete.")


if __name__ == "__main__":
    main()