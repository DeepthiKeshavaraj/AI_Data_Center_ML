
from pathlib import Path
import json

import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "processed" / "thermal" / "thermal_features.csv"
REPORT_DIR = ROOT / "reports" / "thermal"
RESULTS_DIR = ROOT / "results" / "thermal"

# Exploratory thresholds only, not validated safety limits.
THRESHOLDS = [55.0, 60.0, 65.0, 70.0]


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Feature dataset not found: {INPUT_FILE}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    required = ["timestamp", "max_outlet_temp", "mean_outlet_temp"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df.dropna(subset=required)

    # Summarize how often each exploratory threshold is exceeded.
    threshold_rows = []
    for threshold in THRESHOLDS:
        count = int((df["max_outlet_temp"] >= threshold).sum())
        threshold_rows.append({
            "threshold_c": threshold,
            "records_at_or_above": count,
            "percentage_of_records": round(count / len(df) * 100, 4),
        })

    threshold_df = pd.DataFrame(threshold_rows)
    threshold_df.to_csv(
        REPORT_DIR / "thermal_risk_threshold_analysis.csv",
        index=False
    )

    # Describe unusually high periods using the 95th percentile.
    high_temp_cutoff = float(df["max_outlet_temp"].quantile(0.95))
    df["high_temperature_period"] = (
        df["max_outlet_temp"] >= high_temp_cutoff
    )

    # Group consecutive high-temperature records into events.
    # A gap in timestamps starts a new event as well.
    is_high = df["high_temperature_period"]
    previous_high = is_high.shift(fill_value=False)
    timestamp_gap = df["timestamp"].diff().ne(pd.Timedelta(minutes=10))
    new_event = is_high & (~previous_high | timestamp_gap)
    df["event_id"] = new_event.cumsum()

    high_df = df[is_high].copy()
    events = []

    if not high_df.empty:
        for event_id, group in high_df.groupby("event_id"):
            events.append({
                "event_id": int(event_id),
                "start": str(group["timestamp"].min()),
                "end": str(group["timestamp"].max()),
                "records": int(len(group)),
                "duration_minutes": int(len(group) * 10),
                "peak_max_outlet_temp_c": float(
                    group["max_outlet_temp"].max()
                ),
                "mean_max_outlet_temp_c": float(
                    group["max_outlet_temp"].mean()
                ),
            })

    events_df = pd.DataFrame(events)
    events_df.to_csv(
        REPORT_DIR / "thermal_high_temperature_events.csv",
        index=False
    )

    summary = {
        "records_analyzed": int(len(df)),
        "analysis_period_start": str(df["timestamp"].min()),
        "analysis_period_end": str(df["timestamp"].max()),
        "max_outlet_temperature_95th_percentile_c": high_temp_cutoff,
        "high_temperature_records": int(is_high.sum()),
        "high_temperature_percentage": round(
            float(is_high.mean() * 100), 4
        ),
        "high_temperature_events": int(len(events)),
        "thresholds_are_exploratory": True,
        "warning": (
            "These statistical thresholds are not validated equipment "
            "safety limits. Confirm operational limits with domain experts."
        ),
    }

    with open(
        REPORT_DIR / "thermal_risk_analysis_summary.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(summary, file, indent=4)

    # Plot max outlet temperature over time.
    plt.figure(figsize=(14, 6))
    plt.plot(
        df["timestamp"],
        df["max_outlet_temp"],
        linewidth=0.7,
        label="Maximum outlet temperature"
    )
    plt.axhline(
        high_temp_cutoff,
        linestyle="--",
        label=f"95th percentile: {high_temp_cutoff:.2f}°C"
    )

    for threshold in THRESHOLDS:
        plt.axhline(
            threshold,
            linestyle=":",
            alpha=0.6,
            label=f"{threshold:.0f}°C threshold"
        )

    plt.title("Thermal Risk Exploration Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Maximum Outlet Temperature (°C)")
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.savefig(
        RESULTS_DIR / "thermal_risk_timeline.png",
        dpi=150
    )
    plt.close()

    print("\n" + "=" * 65)
    print("THERMAL RISK ANALYSIS")
    print("=" * 65)
    print(f"Records analyzed: {len(df):,}")
    print(f"95th-percentile cutoff: {high_temp_cutoff:.2f}°C")
    print(f"High-temperature records: {int(is_high.sum()):,}")
    print(f"High-temperature events: {len(events):,}")

    print("\nThreshold analysis:")
    print(threshold_df.to_string(index=False))

    print("\nReports saved in:", REPORT_DIR)
    print("Timeline saved in:", RESULTS_DIR / "thermal_risk_timeline.png")


if __name__ == "__main__":
    main()
