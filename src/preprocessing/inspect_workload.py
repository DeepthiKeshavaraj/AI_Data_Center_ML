from pathlib import Path
import pandas as pd

# Project root is the parent of src/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "workload"

print("=" * 70)
print("AI DATA CENTER - WORKLOAD DATASET INSPECTION")
print("=" * 70)

if not RAW_DIR.exists():
    raise FileNotFoundError(f"Dataset folder not found: {RAW_DIR}")

csv_files = sorted(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")

for file in csv_files:
    print(f"\n{'=' * 70}")
    print(f"FILE: {file.name}")
    print("=" * 70)

    try:
        df = pd.read_csv(file, nrows=10000)

        print(f"Rows inspected: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print("\nColumn names:")
        print(df.columns.tolist())

        print("\nData types:")
        print(df.dtypes.to_string())

        print("\nMissing values:")
        print(df.isnull().sum().to_string())

        print(f"\nDuplicate rows in inspected sample: {df.duplicated().sum()}")

        print("\nFirst 5 rows:")
        print(df.head().to_string())

    except Exception as exc:
        print(f"Could not inspect {file.name}: {exc}")

print("\nInspection completed.")
