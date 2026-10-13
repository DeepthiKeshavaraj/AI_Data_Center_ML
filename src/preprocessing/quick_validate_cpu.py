
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/processed/workload/cpu_next_observation.csv"

con = duckdb.connect()

path = DATA.as_posix().replace("'", "''")

print("Checking generated dataset...")

result = con.execute(f"""
    SELECT
        COUNT(*) AS rows,
        COUNT(DISTINCT machine) AS machines,
        COUNT(*) FILTER (
            WHERE machine IS NULL
               OR start_time IS NULL
               OR machine_cpu IS NULL
               OR next_machine_cpu IS NULL
               OR next_start_time IS NULL
        ) AS missing_rows,
        COUNT(*) FILTER (
            WHERE next_start_time <= start_time
        ) AS invalid_time_gaps,
        COUNT(*) FILTER (
            WHERE machine_cpu < 0 OR next_machine_cpu < 0
        ) AS negative_cpu_rows
    FROM read_csv_auto('{path}', header=true)
""").fetchone()

print(f"Rows: {result[0]:,}")
print(f"Machines: {result[1]:,}")
print(f"Rows with missing required values: {result[2]:,}")
print(f"Invalid time gaps: {result[3]:,}")
print(f"Rows with negative CPU values: {result[4]:,}")

if result[0] > 0 and all(value == 0 for value in result[2:]):
    print("Basic checks passed.")
else:
    print("Basic checks need attention.")

con.close()
