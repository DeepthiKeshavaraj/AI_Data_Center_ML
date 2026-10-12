from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "security"
REPORT_DIR = PROJECT_ROOT / "reports" / "security_model"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_FILE = DATA_DIR / "unsw_nb15_UNSW_NB15_training-set(in)_ml_ready.csv"
TEST_FILE = DATA_DIR / "unsw_nb15_UNSW_NB15_testing-set(in)_ml_ready.csv"

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

for df in (train, test):
    for column in CATEGORICAL:
        df[column] = df[column].fillna("<MISSING>").astype(str)

# Count training labels for each exact feature combination.
label_counts = (
    train.groupby(FEATURES, dropna=False)
    .agg(
        train_count=("binary_label", "size"),
        distinct_train_labels=("binary_label", "nunique"),
        train_label=("binary_label", "first"),
    )
    .reset_index()
)

comparison = test[FEATURES + ["binary_label"]].merge(
    label_counts,
    on=FEATURES,
    how="inner",
)

# Only cases where training has exactly one label, and test has the opposite.
conflicts = comparison[
    (comparison["distinct_train_labels"] == 1)
    & (comparison["binary_label"] != comparison["train_label"])
].copy()

print("=" * 65)
print("UNSW-NB15 CONFLICT INSPECTION")
print("=" * 65)
print(f"Conflicting test rows: {len(conflicts):,}")

if conflicts.empty:
    print("No unambiguous label conflicts found.")
else:
    print("\nTest labels among conflicts:")
    print(conflicts["binary_label"].value_counts().sort_index().to_string())

    print("\nTraining labels for those same feature combinations:")
    print(conflicts["train_label"].value_counts().sort_index().to_string())

    print("\nTraining repetition count for conflicting combinations:")
    print(conflicts["train_count"].describe().to_string())

    # Group by feature combination to distinguish repeated test rows
    # from the number of distinct conflicting combinations.
    unique_conflicts = conflicts.drop_duplicates(subset=FEATURES)

    print(
        "\nDistinct conflicting feature combinations: "
        f"{len(unique_conflicts):,}"
    )

    print("\nExample conflicting combinations:")
    print(
        unique_conflicts[
            FEATURES + ["train_label", "binary_label", "train_count"]
        ].head(10).to_string(index=False)
    )

    conflicts.to_csv(
        REPORT_DIR / "unsw_label_conflicts.csv",
        index=False,
    )
    print(f"\nDetailed rows saved to: {REPORT_DIR / 'unsw_label_conflicts.csv'}")

print("\nNo original data has been modified.")