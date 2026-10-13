
from pathlib import Path
import json
import warnings

import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=RuntimeWarning)

# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "standardized" / "workload"
REPORT_DIR = PROJECT_ROOT / "reports" / "workload_eda"
PLOT_DIR = REPORT_DIR / "plots"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILES = [
    "pai_instance_table.csv",
    "pai_job_table.csv",
    "pai_machine_metric.csv",
    "pai_machine_spec.csv",
    "pai_sensor_table.csv",
    "pai_task_table.csv",
]

# Keep memory usage manageable for large datasets.
SAMPLE_SIZE = 100_000
RANDOM_STATE = 42


def analyze_dataset(filename):
    """Analyze one standardized CSV without modifying it."""

    path = DATA_DIR / filename

    if not path.exists():
        print(f"\n[SKIPPED] File not found: {path}")
        return None

    print(f"\n{'=' * 65}")
    print(f"ANALYZING: {filename}")
    print("=" * 65)

    # Read only the header first, then process in chunks.
    columns = pd.read_csv(path, nrows=0).columns.tolist()

    row_count = 0
    duplicate_count = 0
    missing_counts = pd.Series(0, index=columns, dtype="int64")
    dtype_map = {}
    numeric_sample_parts = []

    # Chunked reading avoids loading millions of rows into memory.
    for chunk in pd.read_csv(path, chunksize=100_000):
        row_count += len(chunk)
        duplicate_count += int(chunk.duplicated().sum())
        missing_counts = missing_counts.add(
            chunk.isna().sum(), fill_value=0
        ).astype("int64")

        for column in chunk.columns:
            dtype_map[column] = str(chunk[column].dtype)

        numeric_columns = chunk.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:
            remaining = SAMPLE_SIZE - sum(
                len(part) for part in numeric_sample_parts
            )

            if remaining > 0:
                numeric_sample_parts.append(
                    chunk[numeric_columns].sample(
                        n=min(remaining, len(chunk)),
                        random_state=RANDOM_STATE,
                    )
                )

    missing_report = pd.DataFrame({
        "column": columns,
        "dtype": [dtype_map.get(col, "unknown") for col in columns],
        "missing_count": [
            int(missing_counts[col]) for col in columns
        ],
    })

    missing_report["missing_percentage"] = (
        missing_report["missing_count"] / row_count * 100
    ).round(2)

    missing_report = missing_report.sort_values(
        "missing_percentage", ascending=False
    )

    missing_report.to_csv(
        REPORT_DIR / f"{Path(filename).stem}_missing_values.csv",
        index=False,
    )

    print(f"Rows: {row_count:,}")
    print(f"Columns: {len(columns)}")
    print(f"Duplicate rows within chunks: {duplicate_count:,}")
    print(
        "Total missing cells:",
        f"{int(missing_counts.sum()):,}",
    )

    print("\nMissing-value report:")
    print(missing_report.to_string(index=False))

    # Plot missing percentage by column.
    plot_data = missing_report.sort_values(
        "missing_percentage", ascending=True
    )

    plt.figure(figsize=(10, max(4, len(columns) * 0.35)))
    plt.barh(
        plot_data["column"],
        plot_data["missing_percentage"],
    )
    plt.xlabel("Missing values (%)")
    plt.ylabel("Column")
    plt.title(f"Missing Values: {Path(filename).stem}")
    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / f"{Path(filename).stem}_missing_values.png",
        dpi=150,
    )
    plt.close()

    # Numeric feature distributions from a sample.
    if numeric_sample_parts:
        numeric_sample = pd.concat(
            numeric_sample_parts, ignore_index=True
        )

        numeric_sample = numeric_sample.loc[
            :, ~numeric_sample.columns.duplicated()
        ]

        numeric_sample.describe().T.to_csv(
            REPORT_DIR / f"{Path(filename).stem}_numeric_summary.csv"
        )

        for column in numeric_sample.columns:
            values = numeric_sample[column].dropna()

            if values.empty or values.nunique() <= 1:
                continue

            plt.figure(figsize=(8, 4))
            plt.hist(values, bins=40)
            plt.xlabel(column)
            plt.ylabel("Frequency")
            plt.title(
                f"{Path(filename).stem}: {column} distribution"
            )
            plt.tight_layout()

            plt.savefig(
                PLOT_DIR
                / f"{Path(filename).stem}_{column}_distribution.png",
                dpi=120,
            )
            plt.close()

    return {
        "file": filename,
        "rows": row_count,
        "columns": len(columns),
        "missing_cells": int(missing_counts.sum()),
        "duplicate_rows_within_chunks": duplicate_count,
    }


def main():
    print("AI DATA CENTER - WORKLOAD EDA")
    print(f"Input: {DATA_DIR}")
    print(f"Reports: {REPORT_DIR}")

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Workload data directory not found: {DATA_DIR}"
        )

    summaries = []

    for filename in CSV_FILES:
        result = analyze_dataset(filename)
        if result is not None:
            summaries.append(result)

    if summaries:
        summary_df = pd.DataFrame(summaries)
        summary_path = REPORT_DIR / "workload_eda_summary.csv"
        summary_df.to_csv(summary_path, index=False)

        print("\n" + "=" * 65)
        print("EDA SUMMARY")
        print("=" * 65)
        print(summary_df.to_string(index=False))
        print(f"\nSummary saved to: {summary_path}")
        print(f"Plots saved to: {PLOT_DIR}")

    print("\nEDA completed.")


if __name__ == "__main__":
    main()
