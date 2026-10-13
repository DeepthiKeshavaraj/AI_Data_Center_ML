from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data" / "standardized" / "thermal"
REPORT_DIR = ROOT / "reports" / "thermal"

FILES = {
    "inlet_temperature": (
        "Marconi_A2_Inlet_Air_Temp_standardized.csv"
    ),
    "outlet_temperature": (
        "Marconi_A2_Outlet_Air_Temp_standardized.csv"
    ),
    "power_consumption": (
        "Marconi_A2_Power_Consumption_standardized.csv"
    ),
}


def inspect_dataset(name, filename):
    path = DATA_DIR / filename

    print("\n" + "=" * 65)
    print(f"DATASET: {name}")
    print("=" * 65)

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        return None

    # Read only the header first.
    columns = pd.read_csv(path, nrows=0).columns.tolist()

    if not columns:
        print("ERROR: Dataset has no columns.")
        return None

    timestamp_col = columns[0]
    sensor_cols = columns[1:]

    print(f"File: {filename}")
    print(f"Total columns: {len(columns)}")
    print(f"Sensor columns: {len(sensor_cols)}")
    print(f"Timestamp column: {timestamp_col}")

    # Process in chunks because these files are very large.
    rows = 0
    missing_timestamps = 0
    invalid_timestamps = 0
    duplicate_timestamps = 0
    missing_values = 0
    non_numeric_values = 0
    negative_values = 0
    minimum = None
    maximum = None
    timestamp_min = None
    timestamp_max = None
    seen_timestamps = set()

    for chunk in pd.read_csv(
        path,
        chunksize=1000,
        low_memory=False
    ):
        rows += len(chunk)

        timestamps = chunk[timestamp_col]
        missing_timestamps += int(timestamps.isna().sum())

        parsed = pd.to_datetime(
            timestamps,
            errors="coerce"
        )

        invalid_timestamps += int(
            (timestamps.notna() & parsed.isna()).sum()
        )

        valid_times = parsed.dropna()

        if not valid_times.empty:
            chunk_min = valid_times.min()
            chunk_max = valid_times.max()

            timestamp_min = (
                chunk_min if timestamp_min is None
                else min(timestamp_min, chunk_min)
            )
            timestamp_max = (
                chunk_max if timestamp_max is None
                else max(timestamp_max, chunk_max)
            )

        for timestamp in valid_times:
            key = timestamp.isoformat()

            if key in seen_timestamps:
                duplicate_timestamps += 1
            else:
                seen_timestamps.add(key)

        if sensor_cols:
            sensors = chunk[sensor_cols]
            numeric = sensors.apply(
                pd.to_numeric,
                errors="coerce"
            )

            missing_values += int(sensors.isna().sum().sum())

            non_numeric_values += int(
                (sensors.notna() & numeric.isna()).sum().sum()
            )

            negative_values += int(
                (numeric < 0).sum().sum()
            )

            chunk_min = numeric.min().min()
            chunk_max = numeric.max().max()

            if pd.notna(chunk_min):
                minimum = (
                    chunk_min if minimum is None
                    else min(minimum, float(chunk_min))
                )

            if pd.notna(chunk_max):
                maximum = (
                    chunk_max if maximum is None
                    else max(maximum, float(chunk_max))
                )

    report = {
        "dataset": name,
        "filename": filename,
        "rows": rows,
        "columns": len(columns),
        "sensor_columns": len(sensor_cols),
        "timestamp_column": timestamp_col,
        "missing_timestamps": missing_timestamps,
        "invalid_timestamps": invalid_timestamps,
        "duplicate_timestamps": duplicate_timestamps,
        "missing_sensor_values": missing_values,
        "non_numeric_sensor_values": non_numeric_values,
        "negative_sensor_values": negative_values,
        "minimum_sensor_value": minimum,
        "maximum_sensor_value": maximum,
        "earliest_timestamp": (
            str(timestamp_min) if timestamp_min is not None
            else None
        ),
        "latest_timestamp": (
            str(timestamp_max) if timestamp_max is not None
            else None
        ),
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output = REPORT_DIR / f"{name}_validation.json"
    with output.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    for key, value in report.items():
        print(f"{key}: {value}")

    print(f"Validation report saved: {output}")
    return report


def main():
    reports = []

    for name, filename in FILES.items():
        result = inspect_dataset(name, filename)
        if result is not None:
            reports.append(result)

    if len(reports) != len(FILES):
        raise SystemExit(
            "\nValidation incomplete. Check the missing files above."
        )

    print("\n" + "=" * 65)
    print("VALIDATION SUMMARY")
    print("=" * 65)

    for report in reports:
        print(
            f"{report['dataset']}: "
            f"{report['rows']} rows, "
            f"{report['sensor_columns']} sensors, "
            f"{report['missing_sensor_values']} missing values"
        )


if __name__ == "__main__":
    main()