
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[2]

SOURCE = ROOT / "data" / "standardized" / "workload" / "pai_machine_metric.csv"
OUTPUT = ROOT / "data" / "processed" / "workload" / "cpu_next_observation.csv"

con = duckdb.connect()

source = SOURCE.as_posix().replace("'", "''")
output = OUTPUT.as_posix().replace("'", "''")

print("Checking chronological alignment...")

con.execute(f"""
    CREATE OR REPLACE TEMP VIEW grouped_metrics AS
    SELECT
        CAST(machine AS VARCHAR) AS machine,
        CAST(start_time AS DOUBLE) AS start_time,
        AVG(TRY_CAST(machine_cpu AS DOUBLE)) AS machine_cpu
    FROM read_csv_auto('{source}', header=true)
    WHERE machine IS NOT NULL AND start_time IS NOT NULL
    GROUP BY machine, start_time
""")

con.execute("""
    CREATE OR REPLACE TEMP VIEW expected AS
    SELECT
        machine,
        start_time,
        machine_cpu,
        LEAD(machine_cpu) OVER (
            PARTITION BY machine ORDER BY start_time
        ) AS expected_next_cpu,
        LEAD(start_time) OVER (
            PARTITION BY machine ORDER BY start_time
        ) AS expected_next_time
    FROM grouped_metrics
""")

con.execute(f"""
    CREATE OR REPLACE TEMP VIEW actual AS
    SELECT *
    FROM read_csv_auto('{output}', header=true)
""")

# Match every output row to its unique current observation.
con.execute("""
    CREATE OR REPLACE TEMP VIEW comparison AS
    SELECT
        a.machine,
        a.start_time,
        a.machine_cpu,
        a.next_machine_cpu,
        a.next_start_time,
        e.expected_next_cpu,
        e.expected_next_time
    FROM actual a
    LEFT JOIN expected e
      ON a.machine = e.machine
     AND a.start_time = e.start_time
     AND ABS(a.machine_cpu - e.machine_cpu) < 0.000001
""")

summary = con.execute("""
    SELECT
        COUNT(*) AS output_rows,
        COUNT(expected_next_time) AS matched_rows,
        COUNT(*) FILTER (
            WHERE expected_next_time IS NOT NULL
              AND ABS(next_start_time - expected_next_time) > 0.000001
        ) AS timestamp_mismatches,
        COUNT(*) FILTER (
            WHERE expected_next_cpu IS NOT NULL
              AND ABS(next_machine_cpu - expected_next_cpu) > 0.000001
        ) AS cpu_mismatches,
        COUNT(*) FILTER (
            WHERE expected_next_time IS NULL
        ) AS unmatched_rows
    FROM comparison
""").fetchone()

print("\n--- VALIDATION RESULTS ---")
print(f"Output rows: {summary[0]:,}")
print(f"Rows matched to grouped source: {summary[1]:,}")
print(f"Timestamp mismatches: {summary[2]:,}")
print(f"CPU target mismatches: {summary[3]:,}")
print(f"Unmatched rows: {summary[4]:,}")

if (
    summary[0] == summary[1]
    and summary[2] == 0
    and summary[3] == 0
    and summary[4] == 0
):
    print("\nPASS: All output targets match the next chronological record.")
else:
    print("\nCHECK NEEDED: Some rows did not match the expected next record.")

con.close()
