
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "standardized" / "workload"
OUT = ROOT / "reports" / "workload_analysis"

OUT.mkdir(parents=True, exist_ok=True)

FILES = {
    "pai_sensor_table.csv": [
        "cpu_usage",
        "gpu_wrk_util",
        "avg_mem",
        "max_mem",
        "avg_gpu_wrk_mem",
        "max_gpu_wrk_mem",
    ],
    "pai_machine_metric.csv": [
        "machine_cpu",
        "machine_cpu_iowait",
        "machine_cpu_kernel",
        "machine_cpu_usr",
        "machine_gpu",
        "machine_load_1",
        "machine_net_receive",
    ],
    "pai_task_table.csv": [
        "inst_num",
        "plan_cpu",
        "plan_mem",
        "plan_gpu",
    ],
}

def main():
    reports = []

    for filename, columns in FILES.items():
        path = DATA / filename
        print(f"\nAnalyzing {filename}")

        chunks = pd.read_csv(path, chunksize=100_000)

        for chunk in chunks:
            for col in columns:
                values = pd.to_numeric(
                    chunk[col], errors="coerce"
                ).dropna()

                if values.empty:
                    continue

                reports.append({
                    "file": filename,
                    "column": col,
                    "rows_checked": len(values),
                    "min": values.min(),
                    "p50": values.quantile(0.50),
                    "p95": values.quantile(0.95),
                    "p99": values.quantile(0.99),
                    "max": values.max(),
                    "negative_count": int((values < 0).sum()),
                })

    result = pd.DataFrame(reports)

    # Combine chunk-level results conservatively:
    # these are diagnostic chunk statistics, not exact global quantiles.
    result.to_csv(
        OUT / "workload_value_validation_by_chunk.csv",
        index=False,
    )

    print("\nChunk-level validation report:")
    print(result.groupby(["file", "column"]).agg({
        "min": "min",
        "p50": "median",
        "p95": "median",
        "p99": "median",
        "max": "max",
        "negative_count": "sum",
    }).round(3).to_string())

    print(
        "\nSaved report:",
        OUT / "workload_value_validation_by_chunk.csv",
    )

if __name__ == "__main__":
    main()

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "standardized" / "workload"
OUT = ROOT / "reports" / "workload_analysis"

OUT.mkdir(parents=True, exist_ok=True)

FILES = {
    "pai_sensor_table.csv": [
        "cpu_usage",
        "gpu_wrk_util",
        "avg_mem",
        "max_mem",
        "avg_gpu_wrk_mem",
        "max_gpu_wrk_mem",
    ],
    "pai_machine_metric.csv": [
        "machine_cpu",
        "machine_cpu_iowait",
        "machine_cpu_kernel",
        "machine_cpu_usr",
        "machine_gpu",
        "machine_load_1",
        "machine_net_receive",
    ],
    "pai_task_table.csv": [
        "inst_num",
        "plan_cpu",
        "plan_mem",
        "plan_gpu",
    ],
}

def main():
    reports = []

    for filename, columns in FILES.items():
        path = DATA / filename
        print(f"\nAnalyzing {filename}")

        chunks = pd.read_csv(path, chunksize=100_000)

        for chunk in chunks:
            for col in columns:
                values = pd.to_numeric(
                    chunk[col], errors="coerce"
                ).dropna()

                if values.empty:
                    continue

                reports.append({
                    "file": filename,
                    "column": col,
                    "rows_checked": len(values),
                    "min": values.min(),
                    "p50": values.quantile(0.50),
                    "p95": values.quantile(0.95),
                    "p99": values.quantile(0.99),
                    "max": values.max(),
                    "negative_count": int((values < 0).sum()),
                })

    result = pd.DataFrame(reports)

    # Combine chunk-level results conservatively:
    # these are diagnostic chunk statistics, not exact global quantiles.
    result.to_csv(
        OUT / "workload_value_validation_by_chunk.csv",
        index=False,
    )

    print("\nChunk-level validation report:")
    print(result.groupby(["file", "column"]).agg({
        "min": "min",
        "p50": "median",
        "p95": "median",
        "p99": "median",
        "max": "max",
        "negative_count": "sum",
    }).round(3).to_string())

    print(
        "\nSaved report:",
        OUT / "workload_value_validation_by_chunk.csv",
    )

if __name__ == "__main__":
    main()
