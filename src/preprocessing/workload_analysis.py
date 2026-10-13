
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "standardized" / "workload"
REPORT_DIR = PROJECT_ROOT / "reports" / "workload_analysis"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 100_000


def status_missing_analysis(filename, label):
    """Count rows by status and missing start/end times."""
    path = DATA_DIR / filename
    parts = []

    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        chunk["missing_start_time"] = chunk["start_time"].isna()
        chunk["missing_end_time"] = chunk["end_time"].isna()

        summary = (
            chunk.groupby("status", dropna=False)
            .agg(
                rows=("status", "size"),
                missing_start_time=("missing_start_time", "sum"),
                missing_end_time=("missing_end_time", "sum"),
            )
        )
        parts.append(summary)

    result = pd.concat(parts).groupby(level=0).sum()
    result["missing_start_pct"] = (
        result["missing_start_time"] / result["rows"] * 100
    ).round(2)
    result["missing_end_pct"] = (
        result["missing_end_time"] / result["rows"] * 100
    ).round(2)

    output = REPORT_DIR / f"{label}_status_missing_times.csv"
    result.to_csv(output)

    print(f"\n{label.upper()}: status vs missing timestamps")
    print(result.to_string())
    print(f"Saved: {output}")


def numeric_summary(filename, columns, label):
    """Calculate descriptive statistics using chunked aggregation."""
    path = DATA_DIR / filename
    count = pd.Series(0, index=columns, dtype="int64")
    missing = pd.Series(0, index=columns, dtype="int64")
    minimum = pd.Series(float("inf"), index=columns)
    maximum = pd.Series(float("-inf"), index=columns)
    total = pd.Series(0.0, index=columns)
    total_sq = pd.Series(0.0, index=columns)

    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        data = chunk[columns]

        count += data.count()
        missing += data.isna().sum()

        minimum = pd.concat(
            [minimum, data.min()], axis=1
        ).min(axis=1)

        maximum = pd.concat(
            [maximum, data.max()], axis=1
        ).max(axis=1)

        total += data.sum()
        total_sq += (data ** 2).sum()

    mean = total / count
    variance = (total_sq / count - mean ** 2).clip(lower=0)
    std = variance ** 0.5

    result = pd.DataFrame({
        "non_missing_count": count,
        "missing_count": missing,
        "mean": mean,
        "std": std,
        "min": minimum,
        "max": maximum,
    })

    result.to_csv(REPORT_DIR / f"{label}_summary.csv")

    print(f"\n{label.upper()}: numeric summary")
    print(result.round(3).to_string())


def main():
    print("WORKLOAD STATUS AND RESOURCE ANALYSIS")

    status_missing_analysis(
        "pai_job_table.csv", "jobs"
    )
    status_missing_analysis(
        "pai_task_table.csv", "tasks"
    )
    status_missing_analysis(
        "pai_instance_table.csv", "instances"
    )

    numeric_summary(
        "pai_task_table.csv",
        ["inst_num", "plan_cpu", "plan_mem", "plan_gpu"],
        "task_resource_requests",
    )

    numeric_summary(
        "pai_sensor_table.csv",
        [
            "cpu_usage",
            "gpu_wrk_util",
            "avg_mem",
            "max_mem",
            "avg_gpu_wrk_mem",
            "max_gpu_wrk_mem",
        ],
        "sensor_utilization",
    )

    numeric_summary(
        "pai_machine_spec.csv",
        ["cap_cpu", "cap_mem", "cap_gpu"],
        "machine_capacity",
    )

    print(f"\nAnalysis complete. Reports: {REPORT_DIR}")


if __name__ == "__main__":
    main()
