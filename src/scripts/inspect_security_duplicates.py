
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "security"

FILES = [
    "train_test_network(in).csv",
    "UNSW_NB15_training-set(in).csv",
    "UNSW_NB15_testing-set(in).csv",
]


def main():
    for filename in FILES:
        path = RAW_DIR / filename

        print("\n" + "=" * 72)
        print(filename)
        print("=" * 72)

        if not path.exists():
            print("File not found.")
            continue

        df = pd.read_csv(path, low_memory=False)

        duplicate_count = int(df.duplicated().sum())
        print(f"Rows: {len(df):,}")
        print(f"Exact duplicate rows in original file: {duplicate_count:,}")
        print(
            "Duplicate percentage: "
            f"{duplicate_count / len(df) * 100:.2f}%"
        )


if __name__ == "__main__":
    main()
