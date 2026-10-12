from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "security"

TRAIN_FILE = DATA_DIR / "unsw_nb15_UNSW_NB15_training-set(in)_ml_ready.csv"
TEST_FILE = DATA_DIR / "unsw_nb15_UNSW_NB15_testing-set(in)_ml_ready.csv"

train_df = pd.read_csv(TRAIN_FILE, low_memory=False)
test_df = pd.read_csv(TEST_FILE, low_memory=False)

# Compare predictor features only.
# Labels and metadata are excluded from this comparison.
feature_columns = [
    "protocol",
    "flow_duration",
    "src_packets",
    "dst_packets",
    "src_bytes",
    "dst_bytes",
    "connection_state",
    "service",
]

train_features = train_df[feature_columns].copy()
test_features = test_df[feature_columns].copy()

# Normalize categorical values for a consistent comparison.
for column in ["protocol", "connection_state", "service"]:
    train_features[column] = train_features[column].fillna("<MISSING>").astype(str)
    test_features[column] = test_features[column].fillna("<MISSING>").astype(str)

# Count duplicate feature rows within each dataset.
train_duplicates = int(train_features.duplicated().sum())
test_duplicates = int(test_features.duplicated().sum())

# Count test rows whose feature combination appears in training.
train_index = pd.MultiIndex.from_frame(train_features)
test_index = pd.MultiIndex.from_frame(test_features)

overlap_mask = test_index.isin(train_index)
overlap_count = int(overlap_mask.sum())

print("=" * 60)
print("UNSW-NB15 DUPLICATE AND OVERLAP CHECK")
print("=" * 60)

print(f"Training rows: {len(train_features):,}")
print(f"Testing rows: {len(test_features):,}")
print(f"Duplicate feature rows in training: {train_duplicates:,}")
print(f"Duplicate feature rows in testing: {test_duplicates:,}")
print(f"Test rows whose features occur in training: {overlap_count:,}")
print(
    "Percentage of test rows overlapping training: "
    f"{overlap_count / len(test_features) * 100:.2f}%"
)

print("\nCheck complete. No data has been modified.")