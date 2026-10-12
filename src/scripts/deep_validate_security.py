
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "standardized" / "security"

NUMERIC_COLUMNS = [
    "flow_duration",
    "src_packets",
    "dst_packets",
    "src_bytes",
    "dst_bytes",
    "src_packet_rate",
    "dst_packet_rate",
    "src_byte_rate",
    "dst_byte_rate",
]

REQUIRED_COLUMNS = [
    "protocol",
    "flow_duration",
    "src_packets",
    "dst_packets",
    "src_bytes",
    "dst_bytes",
    "binary_label",
    "attack_type",
    "dataset_source",
]


def inspect_file(file_path):
    print("\n" + "=" * 72)
    print(f"FILE: {file_path.name}")
    print("=" * 72)

    df = pd.read_csv(file_path, low_memory=False)

    # 1. Basic structure
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    missing_columns = [
        col for col in REQUIRED_COLUMNS if col not in df.columns
    ]

    if missing_columns:
        print("FAIL: Missing columns:", missing_columns)
        return

    print("PASS: Required columns exist.")

    # 2. Missing values and infinite values
    print("\nMissing values:")
    print(df[REQUIRED_COLUMNS].isna().sum().to_string())

    print("\nNumeric feature checks:")

    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue

        values = pd.to_numeric(df[col], errors="coerce")
        invalid = values.isna().sum()
        infinite = np.isinf(values.dropna()).sum()
        negative = (values.dropna() < 0).sum()

        print(
            f"{col}: "
            f"min={values.min()}, "
            f"max={values.max()}, "
            f"invalid={invalid}, "
            f"infinite={infinite}, "
            f"negative={negative}"
        )

    # 3. Binary label validation
    print("\nBinary label validation:")
    print(df["binary_label"].value_counts(dropna=False).to_string())

    labels = set(df["binary_label"].dropna().unique())
    if labels.issubset({0, 1}) and labels:
        print("PASS: Labels contain only 0 and 1.")
    else:
        print("WARNING: Unexpected binary label values:", labels)

    # 4. Attack type validation
    print("\nBlank attack types:", df["attack_type"].isna().sum())

    print("\nAttack type counts:")
    print(df["attack_type"].value_counts(dropna=False).to_string())

    # 5. Constant and entirely empty columns
    print("\nConstant or empty columns:")

    found = False
    for col in df.columns:
        if df[col].isna().all():
            print(f"EMPTY: {col}")
            found = True
        elif df[col].nunique(dropna=True) <= 1:
            print(f"CONSTANT: {col}")
            found = True

    if not found:
        print("None found.")

    # 6. Duplicate rows are reported, not removed
    print("\nExact duplicate rows:", df.duplicated().sum())

    print("\nValidation inspection complete.")


def main():
    if not DATA_DIR.exists():
        print(f"Directory not found: {DATA_DIR}")
        return

    files = sorted(DATA_DIR.glob("*_standardized.csv"))

    if not files:
        print(f"No standardized CSV files found in: {DATA_DIR}")
        return

    for file_path in files:
        try:
            inspect_file(file_path)
        except Exception as exc:
            print(f"\nERROR processing {file_path.name}: {exc}")


if __name__ == "__main__":
    main()
