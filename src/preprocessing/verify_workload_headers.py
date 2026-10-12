from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "workload"

print("=" * 75)
print("VERIFYING ORIGINAL WORKLOAD CSV STRUCTURE")
print("=" * 75)

for file in sorted(RAW_DIR.glob("*.csv")):
    print(f"\n{'=' * 75}")
    print(f"FILE: {file.name}")
    print("=" * 75)

    # Read the CSV without assuming the first row contains column names.
    df = pd.read_csv(file, header=None, nrows=5)

    print(f"Columns detected: {df.shape[1]}")
    print("\nFirst 5 rows, preserving the original first row:")
    print(df.to_string(index=False, header=False))

    print("\nValues in the first row:")
    print(df.iloc[0].tolist())

print("\nVerification completed. No files were modified.")