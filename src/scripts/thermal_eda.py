
from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = (
    ROOT / "data" / "processed" / "thermal" / "thermal_features.csv"
)

REPORT_DIR = ROOT / "reports" / "thermal"
RESULTS_DIR = ROOT / "results" / "thermal"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# MAIN EDA FUNCTION
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. LOAD DATASET
    # --------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        parse_dates=["timestamp"]
    )

    if df.empty:
        raise ValueError("The processed dataset is empty.")

    required_columns = [
        "timestamp",
        "mean_inlet_temp",
        "max_inlet_temp",
        "mean_outlet_temp",
        "max_outlet_temp",
        "mean_power_consumption",
        "mean_temperature_difference",
        "thermal_risk_flag",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {missing_columns}"
        )

    df = (
        df.sort_values("timestamp")
        .reset_index(drop=True)
    )

    numeric_columns = (
        df.select_dtypes(include="number")
        .columns.tolist()
    )

    print("=" * 65)
    print("THERMAL DATA EXPLORATORY DATA ANALYSIS")
    print("=" * 65)

    # --------------------------------------------------------
    # 2. BASIC DATASET INFORMATION
    # --------------------------------------------------------

    print("\n1. DATASET OVERVIEW")
    print("-" * 40)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Start timestamp: {df['timestamp'].min()}")
    print(f"End timestamp: {df['timestamp'].max()}")

    missing_values = df.isna().sum()

    print(f"Total missing values: {int(missing_values.sum())}")
    print(
        "Duplicate timestamps: "
        f"{int(df['timestamp'].duplicated().sum())}"
    )

    # --------------------------------------------------------
    # 3. DESCRIPTIVE STATISTICS
    # --------------------------------------------------------

    print("\n2. DESCRIPTIVE STATISTICS")
    print("-" * 40)

    descriptive_statistics = df[numeric_columns].describe()

    print(descriptive_statistics.round(3))

    descriptive_file = (
        REPORT_DIR / "thermal_descriptive_statistics.csv"
    )

    descriptive_statistics.to_csv(descriptive_file)

    # --------------------------------------------------------
    # 4. MISSING VALUE REPORT
    # --------------------------------------------------------

    print("\n3. MISSING VALUE CHECK")
    print("-" * 40)

    print(missing_values[missing_values > 0])

    missing_report = {
        column: int(count)
        for column, count in missing_values.items()
    }

    # --------------------------------------------------------
    # 5. THERMAL RISK FLAG DISTRIBUTION
    # --------------------------------------------------------

    print("\n4. CURRENT THERMAL RISK FLAG DISTRIBUTION")
    print("-" * 40)

    risk_counts = (
        df["thermal_risk_flag"]
        .value_counts()
        .sort_index()
    )

    print(risk_counts)

    risk_percentages = (
        df["thermal_risk_flag"]
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(2)
    )

    print("\nRisk flag percentages:")
    print(risk_percentages)

    if df["thermal_risk_flag"].nunique() < 2:
        print(
            "\nWARNING: The current risk flag contains only one class. "
            "Do not use it as a classification target yet."
        )

    # --------------------------------------------------------
    # 6. OUTLET TEMPERATURE THRESHOLD ANALYSIS
    # --------------------------------------------------------

    print("\n5. OUTLET TEMPERATURE THRESHOLD ANALYSIS")
    print("-" * 40)

    thresholds = [40, 45, 50, 55, 60, 65, 70]

    threshold_results = []

    for threshold in thresholds:

        count = int(
            (df["max_outlet_temp"] >= threshold).sum()
        )

        percentage = count / len(df) * 100

        threshold_results.append({
            "threshold_celsius": threshold,
            "records_at_or_above": count,
            "records_below": len(df) - count,
            "percentage_at_or_above": round(percentage, 3),
        })

        print(
            f"Threshold >= {threshold}°C: "
            f"{count:,} records "
            f"({percentage:.2f}%)"
        )

    threshold_df = pd.DataFrame(threshold_results)

    threshold_file = (
        REPORT_DIR / "thermal_threshold_analysis.csv"
    )

    threshold_df.to_csv(threshold_file, index=False)

    # --------------------------------------------------------
    # 7. OUTLET TEMPERATURE PERCENTILES
    # --------------------------------------------------------

    print("\n6. MAXIMUM OUTLET TEMPERATURE PERCENTILES")
    print("-" * 40)

    percentiles = (
        df["max_outlet_temp"]
        .quantile([0.50, 0.75, 0.90, 0.95, 0.99, 1.00])
    )

    print(percentiles.round(3))

    percentiles_file = (
        REPORT_DIR / "thermal_outlet_temperature_percentiles.csv"
    )

    percentiles.to_csv(
        percentiles_file,
        header=["max_outlet_temp_celsius"]
    )

    # --------------------------------------------------------
    # 8. INVESTIGATE NEGATIVE TEMPERATURE DIFFERENCES
    # --------------------------------------------------------

    print("\n7. TEMPERATURE DIFFERENCE ANALYSIS")
    print("-" * 40)

    negative_difference_count = int(
        (df["mean_temperature_difference"] < 0).sum()
    )

    negative_difference_percentage = (
        negative_difference_count / len(df) * 100
    )

    print(
        "Records with negative mean temperature difference: "
        f"{negative_difference_count:,}"
    )

    print(
        "Percentage with negative difference: "
        f"{negative_difference_percentage:.3f}%"
    )

    print(
        "Minimum mean temperature difference: "
        f"{df['mean_temperature_difference'].min():.3f}°C"
    )

    # --------------------------------------------------------
    # 9. CORRELATION ANALYSIS
    # --------------------------------------------------------

    print("\n8. FEATURE CORRELATION ANALYSIS")
    print("-" * 40)

    correlation = df[numeric_columns].corr()

    correlation_file = (
        REPORT_DIR / "thermal_feature_correlations.csv"
    )

    correlation.to_csv(correlation_file)

    print("Correlation matrix saved.")

    # --------------------------------------------------------
    # 10. SAVE EDA SUMMARY REPORT
    # --------------------------------------------------------

    summary = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "start_timestamp": str(df["timestamp"].min()),
        "end_timestamp": str(df["timestamp"].max()),
        "missing_values": missing_report,
        "duplicate_timestamps": int(
            df["timestamp"].duplicated().sum()
        ),
        "descriptive_statistics": (
            df[numeric_columns].describe().to_dict()
        ),
        "thermal_risk_flag_counts": {
            str(key): int(value)
            for key, value in risk_counts.items()
        },
        "thermal_risk_flag_percentages": {
            str(key): float(value)
            for key, value in risk_percentages.items()
        },
        "outlet_temperature_threshold_analysis": threshold_results,
        "max_outlet_temperature_percentiles": {
            str(key): float(value)
            for key, value in percentiles.items()
        },
        "negative_temperature_difference_records": (
            negative_difference_count
        ),
        "negative_temperature_difference_percentage": (
            round(negative_difference_percentage, 3)
        ),
    }

    summary_file = REPORT_DIR / "thermal_eda_summary.json"

    with summary_file.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    # --------------------------------------------------------
    # 11. TEMPERATURE TREND CHART
    # --------------------------------------------------------

    print("\n9. GENERATING CHARTS")
    print("-" * 40)

    plt.figure(figsize=(14, 6))

    plt.plot(
        df["timestamp"],
        df["mean_inlet_temp"],
        label="Mean inlet temperature",
        linewidth=1
    )

    plt.plot(
        df["timestamp"],
        df["mean_outlet_temp"],
        label="Mean outlet temperature",
        linewidth=1
    )

    plt.xlabel("Timestamp")
    plt.ylabel("Temperature (°C)")
    plt.title("Thermal Temperature Trends Over Time")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "thermal_temperature_trends.png",
        dpi=150
    )

    plt.close()

    # --------------------------------------------------------
    # 12. POWER CONSUMPTION TREND
    # --------------------------------------------------------

    plt.figure(figsize=(14, 6))

    plt.plot(
        df["timestamp"],
        df["mean_power_consumption"],
        linewidth=1
    )

    plt.xlabel("Timestamp")
    plt.ylabel("Mean recorded power")
    plt.title("Mean Power Consumption Over Time")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "thermal_power_trend.png",
        dpi=150
    )

    plt.close()

    # --------------------------------------------------------
    # 13. TEMPERATURE DISTRIBUTION CHARTS
    # --------------------------------------------------------

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12, 5)
    )

    axes[0].hist(
        df["mean_inlet_temp"],
        bins=40
    )

    axes[0].set_title("Mean Inlet Temperature Distribution")
    axes[0].set_xlabel("Temperature (°C)")
    axes[0].set_ylabel("Frequency")

    axes[1].hist(
        df["mean_outlet_temp"],
        bins=40
    )

    axes[1].set_title("Mean Outlet Temperature Distribution")
    axes[1].set_xlabel("Temperature (°C)")
    axes[1].set_ylabel("Frequency")

    fig.tight_layout()

    fig.savefig(
        RESULTS_DIR / "thermal_temperature_distributions.png",
        dpi=150
    )

    plt.close(fig)

    # --------------------------------------------------------
    # 14. CORRELATION HEATMAP
    # --------------------------------------------------------

    fig, ax = plt.subplots(figsize=(10, 8))

    image = ax.imshow(
        correlation,
        aspect="auto",
        interpolation="nearest",
        vmin=-1,
        vmax=1
    )

    ax.set_xticks(range(len(numeric_columns)))
    ax.set_xticklabels(
        numeric_columns,
        rotation=70,
        ha="right"
    )

    ax.set_yticks(range(len(numeric_columns)))
    ax.set_yticklabels(numeric_columns)

    ax.set_title("Thermal Feature Correlation Matrix")

    fig.colorbar(
        image,
        ax=ax,
        label="Correlation"
    )

    fig.tight_layout()

    fig.savefig(
        RESULTS_DIR / "thermal_feature_correlations.png",
        dpi=150
    )

    plt.close(fig)

    # --------------------------------------------------------
    # 15. THRESHOLD ANALYSIS CHART
    # --------------------------------------------------------

    plt.figure(figsize=(10, 6))

    plt.bar(
        threshold_df["threshold_celsius"].astype(str),
        threshold_df["percentage_at_or_above"]
    )

    plt.xlabel("Exploratory threshold (°C)")
    plt.ylabel("Records at or above threshold (%)")
    plt.title("Maximum Outlet Temperature Threshold Analysis")
    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / "thermal_threshold_analysis.png",
        dpi=150
    )

    plt.close()

    # --------------------------------------------------------
    # 16. COMPLETION SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("THERMAL EDA COMPLETED SUCCESSFULLY")
    print("=" * 65)

    print(f"Rows analysed: {len(df):,}")
    print(f"Columns analysed: {len(df.columns)}")
    print(f"Missing values: {int(missing_values.sum())}")
    print(
        "Duplicate timestamps: "
        f"{int(df['timestamp'].duplicated().sum())}"
    )

    print(f"\nSummary report:\n{summary_file}")
    print(f"\nReports directory:\n{REPORT_DIR}")
    print(f"\nCharts directory:\n{RESULTS_DIR}")

    print("\nIMPORTANT:")
    print(
        "The threshold values are exploratory only. "
        "Do not treat them as operational alarm limits "
        "without supporting documentation."
    )


if __name__ == "__main__":
    main()
