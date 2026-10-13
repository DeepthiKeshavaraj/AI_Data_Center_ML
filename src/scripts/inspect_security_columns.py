
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "security"

FILES = [
    "train_test_network(in).csv",
    "UNSW_NB15_training-set(in).csv",
    "UNSW_NB15_testing-set(in).csv",
]

for filename in FILES:
    path = RAW_DIR / filename

    print("\n" + "=" * 72)
    print(filename)
    print("=" * 72)

    if not path.exists():
        print("FILE NOT FOUND")
        continue

    # Read only the header, not the full dataset.
    columns = pd.read_csv(path, nrows=0).columns.tolist()

    for column in columns:
        print(repr(column))

    print(f"\nTotal original columns: {len(columns)}")
