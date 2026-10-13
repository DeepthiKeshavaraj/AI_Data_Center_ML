from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "security"

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

train = pd.read_csv(TRAIN_FILE, low_memory=False)
test = pd.read_csv(TEST_FILE, low_memory=False)

# Normalize categorical fields consistently.
for df in (train, test):
    for column in ["protocol", "connection_state", "service"]:
        df[column] = df[column].fillna("<MISSING>").astype(str)

# Count labels associated with each feature combination in training.
train_label_counts = (
    train.groupby(FEATURES, dropna=False)["binary_label"]
    .agg(["size", "nunique"])
    .reset_index()
    .rename(
        columns={
            "size": "train_count",
            "nunique": "train_label_count",
        }
    )
)

# Determine which test feature combinations occur in training.
comparison = test[FEATURES + ["binary_label"]].merge(
    train_label_counts,
    on=FEATURES,
    how="left",
)

overlap = comparison[comparison["train_count"].notna()].copy()

# Count test rows whose matching training feature combination has
# more than one label represented in the training data.
ambiguous_keys = overlap["train_label_count"] > 1
ambiguous_test_rows = int(ambiguous_keys.sum())

print("=" * 65)
print("UNSW-NB15 OVERLAP LABEL ANALYSIS")
print("=" * 65)

print(f"Test rows: {len(test):,}")
print(f"Test rows with matching training features: {len(overlap):,}")
print(f"Overlapping test rows with ambiguous training labels: {ambiguous_test_rows:,}")

if len(overlap):
    # For unambiguous keys, compare the test label with the sole training label.
    unambiguous = overlap[~ambiguous_keys].copy()

    if len(unambiguous):
        # This lookup is safe because each such feature combination has one label.
        train_single_labels = (
            train.groupby(FEATURES, dropna=False)["binary_label"]
            .first()
            .reset_index()
            .rename(columns={"binary_label": "train_label"})
        )

        checked = unambiguous.merge(
            train_single_labels,
            on=FEATURES,
            how="left",
        )

        conflicts = checked[
            checked["binary_label"] != checked["train_label"]
        ]

        print(
            "Unambiguous overlapping test rows with a different label: "
            f"{len(conflicts):,}"
        )
    else:
        print("No unambiguous overlapping rows were available for comparison.")

# Save a compact report without changing the original datasets.
REPORT_DIR = PROJECT_ROOT / "reports" / "security_model"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

summary = pd.DataFrame(
    [
        {"metric": "test_rows", "value": len(test)},
        {"metric": "overlapping_test_rows", "value": len(overlap)},
        {"metric": "ambiguous_overlapping_test_rows", "value": ambiguous_test_rows},
    ]
)

summary.to_csv(REPORT_DIR / "overlap_label_analysis.csv", index=False)

print(f"\nSummary saved to: {REPORT_DIR / 'overlap_label_analysis.csv'}")
print("No data has been modified.")