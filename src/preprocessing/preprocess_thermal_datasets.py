
from pathlib import Path
import json

import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

RAW_DIR = Path("data/raw/thermal")
OUTPUT_DIR = Path("data/standardized/thermal")
REPORT_DIR = Path("reports/thermal")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    "Marconi_A2_Inlet_Air_Temp.csv",
    "Marconi_A2_Outlet_Air_Temp.csv",
    "Marconi_A2_Power_Consumption.csv",
]

# Small chunks help control memory usage for wide CSV files.
CHUNK_SIZE = 500

EXPECTED_INTERVAL_MINUTES = 10


# --------------------------------------------------
# PREPROCESS ONE DATASET
# --------------------------------------------------

def preprocess_file(filename):
    input_path = RAW_DIR / filename
    output_path = OUTPUT_DIR / (
        input_path.stem + "_standardized.csv"
    )
    report_path = REPORT_DIR / (
        input_path.stem + "_report.json"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {input_path}"
        )

    print("\n" + "=" * 70)
    print(f"Processing: {filename}")
    print(
        f"Input size: "
        f"{input_path.stat().st_size / (1024 ** 3):.2f} GB"
    )

    # Read the header first, without loading the full dataset.
    header = pd.read_csv(input_path, nrows=0).columns.tolist()

    if not header or header[0] != "index":
        raise ValueError(
            f"Unexpected first column in {filename}: "
            f"{header[0] if header else 'No columns'}"
        )

    if len(header) != len(set(header)):
        raise ValueError(
            f"Duplicate column names found in {filename}"
        )

    sensor_columns = header[1:]

    report = {
        "source_file": filename,
        "output_file": output_path.name,
        "input_columns": len(header),
        "sensor_columns": len(sensor_columns),
        "chunk_size": CHUNK_SIZE,
        "expected_interval_minutes": (
            EXPECTED_INTERVAL_MINUTES
        ),
        "rows_read": 0,
        "rows_written": 0,
        "invalid_timestamps": 0,
        "duplicate_timestamps": 0,
        "missing_values_by_column": {},
        "invalid_numeric_values_by_column": {},
        "timestamp_interval_counts_minutes": {},
        "first_timestamp": None,
        "last_timestamp": None,
        "sensor_columns": sensor_columns,
    }

    missing_counts = {col: 0 for col in sensor_columns}
    invalid_numeric_counts = {
        col: 0 for col in sensor_columns
    }

    seen_timestamps = set()
    previous_timestamp = None
    first_write = True

    # Process the large CSV incrementally.
    for chunk_number, chunk in enumerate(
        pd.read_csv(
            input_path,
            chunksize=CHUNK_SIZE,
            encoding="utf-8-sig",
            low_memory=True,
        ),
        start=1,
    ):
        report["rows_read"] += len(chunk)

        # Standardize the timestamp column name.
        chunk = chunk.rename(columns={"index": "timestamp"})

        # Parse timestamps; invalid values become NaT.
        timestamps = pd.to_datetime(
            chunk["timestamp"],
            errors="coerce",
        )

        invalid_timestamp_mask = timestamps.isna()
        report["invalid_timestamps"] += int(
            invalid_timestamp_mask.sum()
        )

        # Convert sensor measurements to numeric values.
        for column in sensor_columns:
            original = chunk[column]

            blank_mask = (
                original.isna()
                | original.astype("string").str.strip().eq("")
            )

            numeric = pd.to_numeric(
                original,
                errors="coerce",
            )

            invalid_mask = numeric.isna() & ~blank_mask

            missing_counts[column] += int(
                numeric.isna().sum()
            )
            invalid_numeric_counts[column] += int(
                invalid_mask.sum()
            )

            chunk[column] = numeric

        chunk["timestamp"] = timestamps

        # Count duplicate timestamps across chunks too.
        valid_timestamps = timestamps.dropna()

        for timestamp in valid_timestamps:
            timestamp = timestamp.to_pydatetime()

            if timestamp in seen_timestamps:
                report["duplicate_timestamps"] += 1
            else:
                seen_timestamps.add(timestamp)

        # Check chronological intervals in file order.
        for timestamp in valid_timestamps:
            timestamp = timestamp.to_pydatetime()

            if previous_timestamp is not None:
                interval = (
                    timestamp - previous_timestamp
                ).total_seconds() / 60

                key = str(interval)
                counts = report[
                    "timestamp_interval_counts_minutes"
                ]
                counts[key] = counts.get(key, 0) + 1

            previous_timestamp = timestamp

        # Track timestamp range.
        if not valid_timestamps.empty:
            first = valid_timestamps.iloc[0]
            last = valid_timestamps.iloc[-1]

            if report["first_timestamp"] is None:
                report["first_timestamp"] = str(first)

            report["last_timestamp"] = str(last)

        # Remove only rows with invalid timestamps.
        # Duplicate timestamps are reported but retained.
        chunk = chunk.loc[~invalid_timestamp_mask].copy()

        # Write incrementally to avoid holding the full dataset.
        chunk.to_csv(
            output_path,
            mode="w" if first_write else "a",
            header=first_write,
            index=False,
        )

        report["rows_written"] += len(chunk)
        first_write = False

        print(
            f"Chunk {chunk_number}: "
            f"{report['rows_read']:,} rows read, "
            f"{report['rows_written']:,} rows written"
        )

    # Handle the unusual case where no valid rows were written.
    if first_write:
        pd.DataFrame(
            columns=["timestamp"] + sensor_columns
        ).to_csv(output_path, index=False)

    report["missing_values_by_column"] = missing_counts
    report["invalid_numeric_values_by_column"] = (
        invalid_numeric_counts
    )

    report["expected_interval_observations"] = (
        report["timestamp_interval_counts_minutes"].get(
            str(float(EXPECTED_INTERVAL_MINUTES)), 0
        )
    )

    report["output_size_bytes"] = output_path.stat().st_size

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(f"\nCompleted: {filename}")
    print(f"Rows read: {report['rows_read']:,}")
    print(f"Rows written: {report['rows_written']:,}")
    print(
        f"Invalid timestamps: "
        f"{report['invalid_timestamps']:,}"
    )
    print(
        f"Duplicate timestamps: "
        f"{report['duplicate_timestamps']:,}"
    )
    print(f"Standardized CSV: {output_path}")
    print(f"Quality report: {report_path}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():
    for filename in FILES:
        preprocess_file(filename)

    print("\nAll three thermal datasets processed.")


if __name__ == "__main__":
    main()
