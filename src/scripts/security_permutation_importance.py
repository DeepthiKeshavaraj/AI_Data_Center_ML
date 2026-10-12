
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# PATHS
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed" / "security"
REPORT_DIR = PROJECT_ROOT / "reports" / "security_model"

TRAIN_FILE = (
    DATA_DIR
    / "unsw_nb15_UNSW_NB15_training-set(in)_ml_ready.csv"
)

TEST_FILE = (
    DATA_DIR
    / "unsw_nb15_UNSW_NB15_testing-set(in)_ml_ready.csv"
)

# --------------------------------------------------
# FEATURES
# --------------------------------------------------
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
TARGET = "binary_label"


def main():
    print("=" * 70)
    print("SECURITY PERMUTATION IMPORTANCE - UNSW-NB15")
    print("=" * 70)

    # Verify input files
    for file_path in [TRAIN_FILE, TEST_FILE]:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset not found:\n{file_path}"
            )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Load datasets
    train_df = pd.read_csv(TRAIN_FILE)
    test_df = pd.read_csv(TEST_FILE)

    required_columns = FEATURES + [TARGET]

    for name, df in [
        ("Training", train_df),
        ("Testing", test_df),
    ]:
        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"{name} dataset is missing columns: {missing}"
            )

    # Prepare data without using the target as an input
    train_df = train_df.dropna(subset=[TARGET]).copy()
    test_df = test_df.dropna(subset=[TARGET]).copy()

    X_train = train_df[FEATURES].copy()
    y_train = pd.to_numeric(
        train_df[TARGET], errors="coerce"
    )

    X_test = test_df[FEATURES].copy()
    y_test = pd.to_numeric(
        test_df[TARGET], errors="coerce"
    )

    # Remove rows with invalid target labels
    train_valid = y_train.isin([0, 1])
    test_valid = y_test.isin([0, 1])

    X_train = X_train.loc[train_valid].copy()
    y_train = y_train.loc[train_valid].astype(int)

    X_test = X_test.loc[test_valid].copy()
    y_test = y_test.loc[test_valid].astype(int)

    # Normalize feature types
    for col in NUMERIC_FEATURES:
        X_train[col] = pd.to_numeric(
            X_train[col], errors="coerce"
        )
        X_test[col] = pd.to_numeric(
            X_test[col], errors="coerce"
        )

        median = X_train[col].median()
        if pd.isna(median):
            median = 0

        X_train[col] = X_train[col].fillna(median)
        X_test[col] = X_test[col].fillna(median)

    for col in CATEGORICAL_FEATURES:
        X_train[col] = (
            X_train[col].fillna("<MISSING>").astype(str)
        )
        X_test[col] = (
            X_test[col].fillna("<MISSING>").astype(str)
        )

    print(f"Training rows: {len(X_train):,}")
    print(f"Testing rows:  {len(X_test):,}")
    print(f"Input features: {len(FEATURES)}")

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    # Match the Random Forest settings used in the
    # baseline model, if its configuration differs.
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    n_jobs=-1,
                    class_weight=None,
                ),
            ),
        ]
    )

    print("\nTraining Random Forest on training data only...")
    model.fit(X_train, y_train)

    print("\nCalculating permutation importance on test data...")
    print("This may take a few minutes.")

    # Score uses accuracy by default.
    # Shuffling one feature at a time shows the resulting
    # decrease in test accuracy.
    result = permutation_importance(
        model,
        X_test,
        y_test,
        scoring="accuracy",
        n_repeats=5,
        random_state=42,
        n_jobs=1,
    )

    importance_df = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    ).sort_values(
        "importance_mean", ascending=False
    ).reset_index(drop=True)

    importance_df["rank"] = (
        importance_df["importance_mean"]
        .rank(method="first", ascending=False)
        .astype(int)
    )

    importance_df = importance_df[
        ["rank", "feature", "importance_mean", "importance_std"]
    ]

    csv_path = REPORT_DIR / "permutation_importance.csv"
    importance_df.to_csv(csv_path, index=False)

    # Plot feature importance
    plot_df = importance_df.sort_values(
        "importance_mean", ascending=True
    )

    plt.figure(figsize=(10, 6))
    plt.barh(
        plot_df["feature"],
        plot_df["importance_mean"],
        xerr=plot_df["importance_std"],
        capsize=3,
    )
    plt.axvline(0, linewidth=1)
    plt.xlabel("Decrease in test accuracy after shuffling")
    plt.ylabel("Feature")
    plt.title("Permutation Feature Importance - UNSW-NB15")
    plt.tight_layout()

    plot_path = REPORT_DIR / "permutation_importance.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()

    print("\nPermutation importance ranking:")
    print(importance_df.to_string(index=False))

    print("\nSaved outputs:")
    print(f"1. {csv_path}")
    print(f"2. {plot_path}")
    print("\nPermutation importance analysis complete.")


if __name__ == "__main__":
    main()
