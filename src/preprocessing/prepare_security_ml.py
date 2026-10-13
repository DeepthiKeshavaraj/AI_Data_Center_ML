
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data" / "standardized" / "security"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "security"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Features shared by the two datasets.
FEATURE_COLUMNS = [
    "protocol",
    "flow_duration",
    "src_packets",
    "dst_packets",
    "src_bytes",
    "dst_bytes",
    "connection_state",
    "service",
]

TARGET_COLUMNS = [
    "binary_label",
    "attack_type",
    "dataset_source",
]

REQUIRED_COLUMNS = FEATURE_COLUMNS + TARGET_COLUMNS


def prepare_file(input_path):
    print("\n" + "=" * 72)
    print(f"Preparing: {input_path.name}")
    print("=" * 72)

    df = pd.read_csv(input_path, low_memory=False)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        print(f"ERROR: Missing required columns: {missing}")
        return

    # Keep only relevant shared features and metadata.
    output = df[REQUIRED_COLUMNS].copy()

    # Ensure binary labels are numeric and valid.
    output["binary_label"] = pd.to_numeric(
        output["binary_label"], errors="coerce"
    )

    invalid_labels = (
        output["binary_label"].isna()
        | ~output["binary_label"].isin([0, 1])
    )

    if invalid_labels.any():
        print(f"ERROR: {invalid_labels.sum()} rows have invalid labels.")
        print("No output written for this file.")
        return

    # Validate numeric traffic features.
    numeric_features = [
        "flow_duration",
        "src_packets",
        "dst_packets",
        "src_bytes",
        "dst_bytes",
    ]

    for col in numeric_features:
        output[col] = pd.to_numeric(output[col], errors="coerce")

        invalid = output[col].isna().sum()
        if invalid:
            print(f"WARNING: {col} has {invalid} missing/non-numeric values.")

        if (output[col].dropna() < 0).any():
            print(f"WARNING: {col} contains negative values.")

    output["protocol"] = output["protocol"].astype("string").str.lower()
    output["connection_state"] = (
        output["connection_state"].astype("string").str.lower()
    )
    output["service"] = output["service"].astype("string").str.lower()
    output["attack_type"] = output["attack_type"].astype("string").str.lower()

    output_path = OUTPUT_DIR / input_path.name.replace(
        "_standardized.csv", "_ml_ready.csv"
    )
    output.to_csv(output_path, index=False)

    print(f"Rows retained: {len(output):,}")
    print(f"Features: {FEATURE_COLUMNS}")
    print(f"Saved: {output_path}")


def main():
    files = sorted(INPUT_DIR.glob("*_standardized.csv"))

    if not files:
        print(f"No standardized files found in {INPUT_DIR}")
        return

    for input_path in files:
        prepare_file(input_path)

    print("\nPreparation complete.")


if __name__ == "__main__":
    main()
