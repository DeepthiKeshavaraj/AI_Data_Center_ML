
from pathlib import Path
import csv

RAW_DIR = Path("data/raw/thermal")

FILES = [
    "Marconi_A2_Inlet_Air_Temp.csv",
    "Marconi_A2_Outlet_Air_Temp.csv",
    "Marconi_A2_Power_Consumption.csv",
]

for filename in FILES:
    path = RAW_DIR / filename

    print("\n" + "=" * 60)
    print(f"FILE: {filename}")
    print(f"SIZE: {path.stat().st_size / (1024 ** 3):.2f} GB")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)

        for row_number, row in enumerate(reader):
            print(f"Row {row_number}: {len(row)} columns")

            # Show at most 10 values, each truncated if necessary.
            for index, value in enumerate(row[:10]):
                print(f"  [{index}] {value[:100]!r}")

            if row_number >= 2:
                break
