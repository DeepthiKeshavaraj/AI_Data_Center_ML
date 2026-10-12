from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data" / "standardized" / "thermal"
OUTPUT_DIR = ROOT / "data" / "processed" / "thermal"
REPORT_DIR = ROOT / "reports" / "thermal"

FILES = {
    "inlet": DATA_DIR / "Marconi_A2_Inlet_Air_Temp_standardized.csv",
    "outlet": DATA_DIR / "Marconi_A2_Outlet_Air_Temp_standardized.csv",
    "power": DATA_DIR / "Marconi_A2_Power_Consumption_standardized.csv",
}

CHUNK_SIZE = 500
# Exploratory threshold only. Confirm an appropriate threshold
# from your research papers or system requirements before deployment.
THERMAL_RISK_THRESHOLD_C = 40.0


def main():
    for path in FILES.values():
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / "thermal_features.csv"

    # Read headers and confirm the same sensor layout.
    headers = {
        name: pd.read_csv(path, nrows=0).columns.tolist()
        for name, path in FILES.items()
    }

    reference_columns = headers["inlet"]

    for name, columns in headers.items():
        if columns != reference_columns:
            raise ValueError(
                f"{name} dataset has a different column layout."
            )

    sensor_columns = reference_columns[1:]

    if not sensor_columns:
        raise ValueError("No sensor columns found.")

    print(f"Sensor columns: {len(sensor_columns)}")
    print(f"Chunk size: {CHUNK_SIZE}")

    total_rows = 0
    first_timestamp = None
    last_timestamp = None
    timestamp_gaps = 0
    previous_timestamp = None

    # Overwrite an existing output rather than appending stale rows.
    if output_path.exists():
        output_path.unlink()

    for chunk_number, (inlet, outlet, power) in enumerate(
        zip(
            pd.read_csv(FILES["inlet"], chunksize=CHUNK_SIZE),
            pd.read_csv(FILES["outlet"], chunksize=CHUNK_SIZE),
            pd.read_csv(FILES["power"], chunksize=CHUNK_SIZE),
        ),
        start=1,
    ):
        # All chunks must contain the same timestamps in the same order.
        timestamps = pd.to_datetime(
            inlet["timestamp"], errors="raise"
        )

        for name, frame in [
            ("outlet", outlet),
            ("power", power),
        ]:
            other_timestamps = pd.to_datetime(
                frame["timestamp"], errors="raise"
            )

            if not timestamps.equals(other_timestamps):
                raise ValueError(
                    f"Timestamp mismatch in chunk {chunk_number}: {name}"
                )

        # Convert sensor readings to numeric arrays.
        # The source files remain unchanged.
        inlet_values = inlet[sensor_columns].to_numpy(
            dtype=np.float64
        )
        outlet_values = outlet[sensor_columns].to_numpy(
            dtype=np.float64
        )
        power_values = power[sensor_columns].to_numpy(
            dtype=np.float64
        )

        features = pd.DataFrame({
            "timestamp": timestamps,
            "mean_inlet_temp": np.mean(inlet_values, axis=1),
            "max_inlet_temp": np.max(inlet_values, axis=1),
            "mean_outlet_temp": np.mean(outlet_values, axis=1),
            "max_outlet_temp": np.max(outlet_values, axis=1),
            "mean_power_consumption": np.mean(power_values, axis=1),
        })

        features["mean_temperature_difference"] = (
            features["mean_outlet_temp"]
            - features["mean_inlet_temp"]
        )

        # Exploratory label based on the maximum outlet reading.
        # This is NOT a validated operational alarm threshold.
        features["thermal_risk_flag"] = (
            features["max_outlet_temp"]
            >= THERMAL_RISK_THRESHOLD_C
        ).astype("int8")

        # Track time coverage and intervals between observations.
        if not timestamps.empty:
            if first_timestamp is None:
                first_timestamp = timestamps.iloc[0]

            for timestamp in timestamps:
                if previous_timestamp is not None:
                    delta = timestamp - previous_timestamp

                    if delta != pd.Timedelta(minutes=10):
                        timestamp_gaps += 1

                previous_timestamp = timestamp

            last_timestamp = timestamps.iloc[-1]

        features.to_csv(
            output_path,
            mode="a",
            header=(chunk_number == 1),
            index=False,
        )

        total_rows += len(features)
        print(
            f"Processed chunk {chunk_number}: "
            f"{total_rows:,} rows completed"
        )

    report = {
        "output_file": str(output_path.relative_to(ROOT)),
        "rows": total_rows,
        "sensor_count": len(sensor_columns),
        "features": [
            "timestamp",
            "mean_inlet_temp",
            "max_inlet_temp",
            "mean_outlet_temp",
            "max_outlet_temp",
            "mean_power_consumption",
            "mean_temperature_difference",
            "thermal_risk_flag",
        ],
        "first_timestamp": str(first_timestamp),
        "last_timestamp": str(last_timestamp),
        "non_10_minute_intervals": timestamp_gaps,
        "exploratory_risk_threshold_c": THERMAL_RISK_THRESHOLD_C,
    }

    import json

    report_path = REPORT_DIR / "thermal_feature_report.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nFEATURE ENGINEERING COMPLETED")
    print(f"Rows: {total_rows:,}")
    print(f"Output: {output_path}")
    print(f"Report: {report_path}")
    print(f"Non-10-minute intervals: {timestamp_gaps}")


if __name__ == "__main__":
    main()