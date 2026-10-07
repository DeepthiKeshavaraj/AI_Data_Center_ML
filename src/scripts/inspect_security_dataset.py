from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

# __file__ = E:\AI_Data_Center_ML\src\scripts\inspect_security_dataset.py
# parents[0] = scripts
# parents[1] = src
# parents[2] = AI_Data_Center_ML

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_SECURITY_DIR = PROJECT_ROOT / "data" / "raw" / "security"


# ============================================================
# DATASET INSPECTION
# ============================================================

def inspect_csv(file_path):
    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print("=" * 80)

    try:
        # Read only first 1000 rows to avoid loading huge datasets
        df = pd.read_csv(file_path, nrows=1000)

    except Exception as e:
        print(f"ERROR reading file: {e}")
        return

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    print(f"\nRows inspected : {len(df)}")
    print(f"Columns        : {len(df.columns)}")

    print("\n--- COLUMNS ---")
    for column in df.columns:
        print(column)

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\n--- DATA TYPES ---")
    print(df.dtypes)

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\n--- MISSING VALUES ---")
    missing = df.isnull().sum()
    print(missing[missing > 0])

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    print("\n--- DUPLICATES ---")
    print(f"Duplicate rows: {df.duplicated().sum()}")

    # --------------------------------------------------------
    # First few rows
    # --------------------------------------------------------

    print("\n--- FIRST 5 ROWS ---")
    print(df.head())

    # --------------------------------------------------------
    # Possible label / attack columns
    # --------------------------------------------------------

    possible_labels = [
        column
        for column in df.columns
        if any(
            keyword in column.lower()
            for keyword in [
                "label",
                "attack",
                "class",
                "type"
            ]
        )
    ]

    if possible_labels:
        print("\n--- POSSIBLE LABEL / ATTACK COLUMNS ---")

        for column in possible_labels:
            print(f"\nColumn: {column}")
            print(df[column].value_counts(dropna=False).head(20))

    else:
        print("\nNo obvious label/attack columns detected.")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("SECURITY DATASET INSPECTION")
    print("=" * 80)

    print(f"\nProject root:")
    print(PROJECT_ROOT)

    print(f"\nLooking for CSV files in:")
    print(RAW_SECURITY_DIR)

    # --------------------------------------------------------
    # Check directory
    # --------------------------------------------------------

    if not RAW_SECURITY_DIR.exists():
        print("\nSecurity dataset directory does not exist.")
        print("Create it using:")

        print("\n    data\\raw\\security")

        return

    # --------------------------------------------------------
    # Find CSV files recursively
    # --------------------------------------------------------

    csv_files = sorted(
        RAW_SECURITY_DIR.rglob("*.csv")
    )

    if not csv_files:
        print("\nNo CSV files found in:")
        print(RAW_SECURITY_DIR)

        print("\nDownload/place the security dataset files first.")

        return

    # --------------------------------------------------------
    # Display files found
    # --------------------------------------------------------

    print(f"\nFound {len(csv_files)} CSV file(s):")

    for file_path in csv_files:
        print(f"  - {file_path}")

    # --------------------------------------------------------
    # Inspect every CSV
    # --------------------------------------------------------

    for file_path in csv_files:
        inspect_csv(file_path)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()