from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_SECURITY_DIR = PROJECT_ROOT / "data" / "raw" / "security"
STANDARDIZED_SECURITY_DIR = PROJECT_ROOT / "data" / "standardized" / "security"

STANDARDIZED_SECURITY_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# Generic utilities
# ---------------------------------------------------------------------

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to lowercase snake_case."""
    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    return df


def remove_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove completely duplicated rows."""
    return df.drop_duplicates().reset_index(drop=True)


def normalize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Convert common missing-value representations to pandas NA."""
    df = df.copy()

    missing_values = [
        "",
        " ",
        "nan",
        "NaN",
        "NULL",
        "null",
        "None",
        "none",
        "N/A",
        "n/a",
        "NA",
    ]

    return df.replace(missing_values, pd.NA)


def basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """Apply generic cleaning shared by all security datasets."""
    df = clean_column_names(df)
    df = normalize_missing_values(df)
    df = remove_duplicate_rows(df)

    return df


# ---------------------------------------------------------------------
# Dataset inspection
# ---------------------------------------------------------------------

def inspect_dataset(
    df: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Print a basic summary of a dataset."""

    print(f"\n{'=' * 60}")
    print(f"DATASET: {dataset_name}")
    print(f"{'=' * 60}")

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nMissing values:")
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        print("  None")
    else:
        print(missing)

    print("\nDuplicate rows:")
    print(f"  {df.duplicated().sum():,}")


# ---------------------------------------------------------------------
# Save standardized dataset
# ---------------------------------------------------------------------

def save_standardized_dataset(
    df: pd.DataFrame,
    filename: str,
) -> Path:
    """Save a standardized security dataset."""

    output_path = STANDARDIZED_SECURITY_DIR / filename

    df.to_csv(
        output_path,
        index=False,
    )

    print(f"\nSaved standardized dataset:")
    print(output_path)

    return output_path