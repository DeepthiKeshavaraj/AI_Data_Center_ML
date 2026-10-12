from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed" / "security"
REPORT_DIR = PROJECT_ROOT / "reports" / "security_model"

TRAIN_FILE = (
    DATA_DIR / "unsw_nb15_UNSW_NB15_training-set(in)_ml_ready.csv"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FEATURES
# ============================================================

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


# ============================================================
# LOAD AND VALIDATE DATA
# ============================================================

def main():
    print("=" * 70)
    print("SECURITY FEATURE IMPORTANCE - UNSW-NB15")
    print("=" * 70)

    if not TRAIN_FILE.exists():
        raise FileNotFoundError(
            f"Training dataset not found:\n{TRAIN_FILE}"
        )

    df = pd.read_csv(TRAIN_FILE, low_memory=False)

    missing = [
        column
        for column in FEATURES + [TARGET]
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Required columns are missing: {missing}"
        )

    df = df.dropna(subset=[TARGET]).copy()

    X = df[FEATURES].copy()
    y = pd.to_numeric(df[TARGET], errors="raise").astype(int)

    if not set(y.unique()).issubset({0, 1}):
        raise ValueError("Target must contain only binary labels 0 and 1.")

    for column in NUMERIC_FEATURES:
        X[column] = pd.to_numeric(X[column], errors="coerce")

    for column in CATEGORICAL_FEATURES:
        X[column] = X[column].fillna("<MISSING>").astype(str)

    print(f"Training rows: {len(X):,}")
    print(f"Original input features: {len(FEATURES)}")
    print(f"Normal rows: {(y == 0).sum():,}")
    print(f"Attack rows: {(y == 1).sum():,}")

    # ========================================================
    # PREPROCESSING
    # ========================================================

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", NUMERIC_FEATURES),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )

    # Match the baseline's Random Forest settings here if they
    # differ from these. Check security_baseline.py if needed.
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight=None,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model),
        ]
    )

    # Fit training data only. Do not load or evaluate test data here.
    print("\nTraining Random Forest on training data only...")
    pipeline.fit(X, y)

    # ========================================================
    # EXTRACT ENCODED FEATURE IMPORTANCE
    # ========================================================

    fitted_preprocessor = pipeline.named_steps["preprocessor"]
    fitted_model = pipeline.named_steps["classifier"]

    encoded_feature_names = (
        fitted_preprocessor.get_feature_names_out()
    )

    importances = fitted_model.feature_importances_

    if len(encoded_feature_names) != len(importances):
        raise RuntimeError(
            "Encoded feature names do not match importance values."
        )

    encoded_df = pd.DataFrame(
        {
            "encoded_feature": encoded_feature_names,
            "importance": importances,
        }
    ).sort_values("importance", ascending=False)

    encoded_path = REPORT_DIR / "feature_importance_encoded.csv"
    encoded_df.to_csv(encoded_path, index=False)

    # ========================================================
    # AGGREGATE IMPORTANCE BY ORIGINAL FEATURE
    # ========================================================

    def original_feature(encoded_name):
        # ColumnTransformer prefixes features with transformer names.
        if encoded_name.startswith("numeric__"):
            return encoded_name.removeprefix("numeric__")

        if encoded_name.startswith("categorical__"):
            remainder = encoded_name.removeprefix("categorical__")

            # Match the longest categorical column prefix.
            for column in CATEGORICAL_FEATURES:
                if remainder == column or remainder.startswith(
                    column + "_"
                ):
                    return column

        raise ValueError(
            f"Cannot map encoded feature to original feature: "
            f"{encoded_name}"
        )

    encoded_df["original_feature"] = encoded_df[
        "encoded_feature"
    ].map(original_feature)

    grouped_df = (
        encoded_df.groupby("original_feature", as_index=False)[
            "importance"
        ]
        .sum()
        .sort_values("importance", ascending=False)
    )

    grouped_path = REPORT_DIR / "feature_importance_by_group.csv"
    grouped_df.to_csv(grouped_path, index=False)

    # ========================================================
    # PLOT
    # ========================================================

    plot_df = grouped_df.sort_values("importance", ascending=True)

    fig_height = max(5, len(plot_df) * 0.55)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    ax.barh(
        plot_df["original_feature"],
        plot_df["importance"],
    )

    ax.set_title("Random Forest Feature Importance - UNSW-NB15")
    ax.set_xlabel("Aggregated impurity-based importance")
    ax.set_ylabel("Original feature")
    ax.grid(axis="x", alpha=0.25)

    fig.tight_layout()

    plot_path = REPORT_DIR / "feature_importance.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\nOriginal feature importance:")
    print(grouped_df.to_string(index=False))

    print("\nSaved outputs:")
    print(f"1. {grouped_path}")
    print(f"2. {encoded_path}")
    print(f"3. {plot_path}")

    print("\nFeature importance analysis complete.")


if __name__ == "__main__":
    main()
