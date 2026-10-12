
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "security"

INPUT_FILE = RAW_DIR / "train_test_network(in).csv"


def main():
    if not INPUT_FILE.exists():
        print(f"File not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    # Mark every row that has an identical earlier row.
    duplicate_mask = df.duplicated(keep="first")
    duplicate_rows = df.loc[duplicate_mask].copy()

    print("=" * 72)
    print("TON_IOT DUPLICATE ANALYSIS")
    print("=" * 72)

    print(f"Total rows: {len(df):,}")
    print(f"Duplicate occurrences: {int(duplicate_mask.sum()):,}")
    print(f"Unique rows: {len(df.drop_duplicates()):,}")

    print("\nOriginal label distribution:")
    print(df["label"].value_counts(dropna=False).to_string())

    print("\nDuplicate occurrence label distribution:")
    if duplicate_rows.empty:
        print("No duplicate rows found.")
    else:
        print(
            duplicate_rows["label"]
            .value_counts(dropna=False)
            .to_string()
        )

    if "type" in df.columns and not duplicate_rows.empty:
        print("\nDuplicate occurrence attack types:")
        print(
            duplicate_rows["type"]
            .value_counts(dropna=False)
            .to_string()
        )

    # Check whether identical feature rows ever carry conflicting labels.
    feature_columns = [
        col for col in df.columns if col not in ["label", "type"]
    ]

    grouped = (
        df.groupby(feature_columns, dropna=False)
        .agg(
            row_count=("label", "size"),
            distinct_binary_labels=("label", "nunique"),
            distinct_attack_types=("type", "nunique"),
        )
        .reset_index()
    )

    repeated_groups = grouped[grouped["row_count"] > 1]
    conflicting_labels = repeated_groups[
        repeated_groups["distinct_binary_labels"] > 1
    ]
    conflicting_types = repeated_groups[
        repeated_groups["distinct_attack_types"] > 1
    ]

    print("\nRepeated feature groups:", len(repeated_groups))
    print("Groups with conflicting binary labels:", len(conflicting_labels))
    print("Groups with conflicting attack types:", len(conflicting_types))

    print("\nNo rows were removed or modified.")


if __name__ == "__main__":
    main()
