from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "workload"
OUT_DIR = PROJECT_ROOT / "data" / "standardized" / "workload"

OUT_DIR.mkdir(parents=True, exist_ok=True)

SCHEMAS = {
    "pai_instance_table.csv": [
        "job_name", "task_name", "inst_name", "worker_name",
        "inst_id", "status", "start_time", "end_time", "machine"
    ],
    "pai_job_table.csv": [
        "job_name", "inst_id", "user", "status",
        "start_time", "end_time"
    ],
    "pai_machine_metric.csv": [
        "worker_name", "machine", "start_time", "end_time",
        "machine_cpu_iowait", "machine_cpu_kernel",
        "machine_cpu_usr", "machine_gpu", "machine_load_1",
        "machine_net_receive", "machine_num_worker", "machine_cpu"
    ],
    "pai_machine_spec.csv": [
        "machine", "gpu_type", "cap_cpu", "cap_mem", "cap_gpu"
    ],
    "pai_sensor_table.csv": [
        "job_name", "task_name", "worker_name", "inst_id",
        "machine", "gpu_name", "cpu_usage", "gpu_wrk_util",
        "avg_mem", "max_mem", "avg_gpu_wrk_mem",
        "max_gpu_wrk_mem", "read", "write",
        "read_count", "write_count"
    ],
    "pai_task_table.csv": [
        "job_name", "task_name", "inst_num", "status",
        "start_time", "end_time", "plan_cpu", "plan_mem",
        "plan_gpu", "gpu_type"
    ],
}

summary = []

for filename, columns in SCHEMAS.items():
    source = RAW_DIR / filename

    if not source.exists():
        print(f"SKIPPED: {filename} not found")
        continue

    print(f"\nProcessing {filename} ...")

    # Original files have no header row.
    df = pd.read_csv(source, header=None)

    if len(df.columns) != len(columns):
        raise ValueError(
            f"{filename}: expected {len(columns)} columns, "
            f"found {len(df.columns)}. No output written for this file."
        )

    # Assign documented names without dropping the first record.
    df.columns = columns

    # Preserve identifiers as strings and convert known numeric fields.
    id_columns = {
        "job_name", "task_name", "inst_name", "worker_name",
        "inst_id", "machine", "user", "status", "gpu_name", "gpu_type"
    }

    for col in df.columns:
        if col not in id_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    output = OUT_DIR / filename
    df.to_csv(output, index=False)

    summary.append({
        "file": filename,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "output": str(output.relative_to(PROJECT_ROOT)),
    })

    print(f"Saved: {output}")
    print(f"Rows: {len(df):,}")
    print(f"Missing cells: {df.isna().sum().sum():,}")

if summary:
    report = pd.DataFrame(summary)
    report.to_csv(OUT_DIR / "preprocessing_summary.csv", index=False)
    print("\nPreprocessing summary:")
    print(report.to_string(index=False))

print("\nSchema restoration completed.")
