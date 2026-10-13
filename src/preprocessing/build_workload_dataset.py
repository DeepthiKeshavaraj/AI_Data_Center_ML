
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[2]

SOURCE = ROOT / "data" / "standardized" / "workload" / "pai_machine_metric.csv"
OUTPUT = ROOT / "data" / "processed" / "workload" / "cpu_next_observation.csv"
TEMP_DIR = ROOT / "data" / "processed" / "workload" / "duckdb_temp"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

if not SOURCE.exists():
    raise FileNotFoundError(f"Source dataset not found: {SOURCE}")

print("Building chronologically aligned CPU dataset...")
print(f"Source: {SOURCE}")

con = duckdb.connect()
con.execute(f"SET temp_directory = '{TEMP_DIR.as_posix()}'")
con.execute("SET preserve_insertion_order = false")

source_sql = SOURCE.as_posix().replace("'", "''")
output_sql = OUTPUT.as_posix().replace("'", "''")

# Remove ambiguous duplicate machine/timestamp records.
# If duplicates exist, average their CPU readings into one observation.
con.execute(f"""
    CREATE OR REPLACE TABLE metrics AS
    SELECT
        CAST(machine AS VARCHAR) AS machine,
        CAST(start_time AS DOUBLE) AS start_time,
        AVG(TRY_CAST(machine_cpu AS DOUBLE)) AS machine_cpu,
        AVG(TRY_CAST(machine_gpu AS DOUBLE)) AS machine_gpu,
        AVG(TRY_CAST(machine_cpu_usr AS DOUBLE)) AS machine_cpu_usr,
        AVG(TRY_CAST(machine_cpu_kernel AS DOUBLE)) AS machine_cpu_kernel,
        AVG(TRY_CAST(machine_cpu_iowait AS DOUBLE)) AS machine_cpu_iowait,
        AVG(TRY_CAST(machine_load_1 AS DOUBLE)) AS machine_load_1,
        AVG(TRY_CAST(machine_num_worker AS DOUBLE)) AS machine_num_worker
    FROM read_csv_auto('{source_sql}', header = true)
    WHERE machine IS NOT NULL AND start_time IS NOT NULL
    GROUP BY machine, start_time
""")

con.execute("""
    CREATE OR REPLACE TABLE aligned AS
    SELECT
        *,
        LEAD(machine_cpu) OVER (
            PARTITION BY machine ORDER BY start_time
        ) AS next_machine_cpu,
        LEAD(start_time) OVER (
            PARTITION BY machine ORDER BY start_time
        ) AS next_start_time
    FROM metrics
""")

con.execute(f"""
    COPY (
        SELECT
            machine,
            start_time,
            machine_cpu,
            machine_gpu,
            machine_cpu_usr,
            machine_cpu_kernel,
            machine_cpu_iowait,
            machine_load_1,
            machine_num_worker,
            next_machine_cpu,
            next_start_time
        FROM aligned
        WHERE machine_cpu IS NOT NULL
          AND next_machine_cpu IS NOT NULL
          AND next_start_time > start_time
        ORDER BY machine, start_time
    )
    TO '{output_sql}'
    (HEADER, DELIMITER ',')
""")

row_count = con.execute(
    f"SELECT COUNT(*) FROM read_csv_auto('{output_sql}')"
).fetchone()[0]

machine_count = con.execute(
    "SELECT COUNT(DISTINCT machine) FROM metrics"
).fetchone()[0]

duplicate_count = con.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT machine, start_time
        FROM metrics
        GROUP BY machine, start_time
        HAVING COUNT(*) > 1
    )
""").fetchone()[0]

print("\nDataset rebuilt successfully.")
print(f"Unique machines: {machine_count:,}")
print(f"Duplicate keys remaining in grouped source: {duplicate_count:,}")
print(f"Output rows: {row_count:,}")
print(f"Saved to: {OUTPUT}")

print("\nSample rows:")
print(con.execute(
    f"SELECT * FROM read_csv_auto('{output_sql}') LIMIT 5"
).df())

con.close()
