
from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parents[2]

PREDICTIONS_FILE = (
    ROOT / "reports" / "thermal" /
    "thermal_forecasting_predictions.csv"
)

REPORT_DIR = ROOT / "reports" / "thermal"
RESULTS_DIR = ROOT / "results" / "thermal"

ACTUAL_COL = "actual_outlet_temp_30min"

MODEL_COLUMNS = {
    "Persistence Baseline": "predicted_persistence_baseline",
    "Linear Regression": "predicted_linear_regression",
    "Random Forest": "predicted_random_forest",
}


def main():
    if not PREDICTIONS_FILE.exists():
        raise FileNotFoundError(
            f"Predictions file not found: {PREDICTIONS_FILE}\n"
            "Run src/models/thermal_forecasting.py first."
        )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(PREDICTIONS_FILE, parse_dates=["timestamp"])

    required = ["timestamp", ACTUAL_COL, *MODEL_COLUMNS.values()]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.dropna(subset=required).sort_values("timestamp").reset_index(drop=True)

    if df.empty:
        raise ValueError("No valid prediction rows were found.")

    actual = df[ACTUAL_COL].to_numpy()
    metrics = []
    residuals = pd.DataFrame({"timestamp": df["timestamp"]})

    for model_name, pred_col in MODEL_COLUMNS.items():
        predicted = df[pred_col].to_numpy()
        errors = predicted - actual

        metrics.append({
            "model": model_name,
            "MAE": float(mean_absolute_error(actual, predicted)),
            "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
            "R2": float(r2_score(actual, predicted)),
            "Mean_Error_Bias": float(np.mean(errors)),
            "Median_Absolute_Error": float(np.median(np.abs(errors))),
            "95th_Percentile_Absolute_Error": float(
                np.percentile(np.abs(errors), 95)
            ),
            "Maximum_Absolute_Error": float(np.max(np.abs(errors))),
        })

        residuals[f"{model_name}_error"] = errors

    metrics_df = pd.DataFrame(metrics).sort_values("MAE")
    metrics_path = REPORT_DIR / "thermal_forecasting_error_analysis.csv"
    metrics_df.to_csv(metrics_path, index=False)

    summary = {
        "evaluation": "30-minute-ahead mean outlet temperature forecasting",
        "records_evaluated": int(len(df)),
        "test_start": str(df["timestamp"].min()),
        "test_end": str(df["timestamp"].max()),
        "error_definition": "prediction minus actual",
        "best_model_by_mae": str(metrics_df.iloc[0]["model"]),
        "metrics": metrics,
        "limitations": [
            "Offline evaluation on the existing chronological test set.",
            "Results do not establish production or real-time performance.",
            "Temperature risk thresholds require domain validation."
        ],
    }

    summary_path = REPORT_DIR / "thermal_forecasting_error_summary.json"
    with open(summary_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    # Plot 1: actual versus predicted temperatures for the first 500 test rows.
    sample = df.head(min(500, len(df)))

    plt.figure(figsize=(14, 6))
    plt.plot(
        sample["timestamp"], sample[ACTUAL_COL],
        label="Actual", linewidth=2
    )

    for model_name, pred_col in MODEL_COLUMNS.items():
        plt.plot(
            sample["timestamp"], sample[pred_col],
            label=model_name, alpha=0.8
        )

    plt.title("Thermal Forecasting: Actual vs Predicted")
    plt.xlabel("Timestamp")
    plt.ylabel("Mean Outlet Temperature (°C)")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(
        RESULTS_DIR / "thermal_forecasting_actual_vs_predicted.png",
        dpi=150
    )
    plt.close()

    # Plot 2: prediction errors across the complete test period.
    plt.figure(figsize=(14, 6))

    for model_name in MODEL_COLUMNS:
        plt.plot(
            df["timestamp"],
            residuals[f"{model_name}_error"],
            label=model_name,
            alpha=0.75
        )

    plt.axhline(0, linestyle="--")
    plt.title("Thermal Forecasting Residuals Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Prediction Error (°C)")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(
        RESULTS_DIR / "thermal_forecasting_residuals_over_time.png",
        dpi=150
    )
    plt.close()

    # Plot 3: compare absolute-error distributions.
    plt.figure(figsize=(10, 6))
    error_data = [
        np.abs(df[pred_col].to_numpy() - actual)
        for pred_col in MODEL_COLUMNS.values()
    ]

    plt.boxplot(error_data, tick_labels=list(MODEL_COLUMNS.keys()))
    plt.title("Absolute Forecasting Error Comparison")
    plt.ylabel("Absolute Error (°C)")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(
        RESULTS_DIR / "thermal_forecasting_error_distributions.png",
        dpi=150
    )
    plt.close()

    print("\n" + "=" * 65)
    print("THERMAL FORECASTING ERROR ANALYSIS")
    print("=" * 65)
    print(f"Records evaluated: {len(df):,}")
    print(f"Test period: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print("\nMetrics (lower MAE/RMSE is better; R² closer to 1 is better):")
    print(metrics_df.round(4).to_string(index=False))
    print("\nSaved reports:")
    print(metrics_path)
    print(summary_path)
    print("\nSaved plots:")
    print(RESULTS_DIR / "thermal_forecasting_actual_vs_predicted.png")
    print(RESULTS_DIR / "thermal_forecasting_residuals_over_time.png")
    print(RESULTS_DIR / "thermal_forecasting_error_distributions.png")


if __name__ == "__main__":
    main()
