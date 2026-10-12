
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "standardized" / "security"

REQUIRED_COLUMNS = [
    "flow_duration",
    "src_packets",
    "dst_packets",
    "src_bytes",
    "dst_bytes",
    "protocol",
    "binary_label",
    "attack_type",
    "dataset_source",
]


def main():
    files = sorted(DATA_DIR.glob("*.csv"))

    if not files:
        print(f"No standardized CSV files found in {DATA_DIR}")
        return

    for file_path in files:
        print("\n" + "=" * 70)
        print(f"FILE: {file_path.name}")
        print("=" * 70)

        df = pd.read_csv(file_path, low_memory=False)

        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")

        missing_columns = [
            col for col in REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing_columns:
            print("FAIL: Missing columns:", missing_columns)
        else:
            print("PASS: All required columns exist.")

        print("\nMissing-value percentage:")
        for col in REQUIRED_COLUMNS:
            if col in df.columns:
                pct = df[col].isna().mean() * 100
                print(f"  {col}: {pct:.2f}%")

        print("\nLabel distribution:")
        if "binary_label" in df.columns:
            print(df["binary_label"].value_counts(dropna=False).head(10))

        print("\nAttack types:")
        if "attack_type" in df.columns:
            print(df["attack_type"].value_counts(dropna=False).head(15))

        print("\nDataset source:")
        if "dataset_source" in df.columns:
            print(df["dataset_source"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
