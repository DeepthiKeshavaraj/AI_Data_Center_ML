
from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS AND CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT / "data" / "processed" / "thermal" / "thermal_features.csv"
)

REPORT_DIR = ROOT / "reports" / "thermal"
RESULTS_DIR = ROOT / "results" / "thermal"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FORECAST_STEPS = 3       # 3 x 10 minutes = 30 minutes
TEST_FRACTION = 0.20
RANDOM_STATE = 42

TARGET = "mean_outlet_temp"

BASE_FEATURES = [
    "mean_inlet_temp",
    "mean_outlet_temp",
    "mean_power_consumption",
    "mean_temperature_difference",
]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 65)
    print("THERMAL TEMPERATURE FORECASTING")
    print("=" * 65)

    # --------------------------------------------------------
    # 1. LOAD DATA
    # --------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        parse_dates=["timestamp"]
    )

    required = ["timestamp", TARGET] + BASE_FEATURES

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = (
        df.sort_values("timestamp")
        .drop_duplicates(subset="timestamp")
        .reset_index(drop=True)
    )

    if df[required].isna().any().any():
        raise ValueError(
            "Missing values exist in required columns. "
            "Resolve them before forecasting."
        )

    print(f"\nRecords loaded: {len(df):,}")
    print(f"Start: {df['timestamp'].min()}")
    print(f"End:   {df['timestamp'].max()}")

    # --------------------------------------------------------
    # 2. VERIFY 10-MINUTE INTERVALS
    # --------------------------------------------------------

    time_differences = df["timestamp"].diff().dropna()
    expected_interval = pd.Timedelta(minutes=10)

    irregular_count = int(
        (time_differences != expected_interval).sum()
    )

    print(
        "\nIntervals not equal to 10 minutes: "
        f"{irregular_count:,}"
    )

    if irregular_count > 0:
        raise ValueError(
            "Irregular timestamps detected. Do not assume three rows "
            "always represent 30 minutes. Inspect the time gaps first."
        )

    # --------------------------------------------------------
    # 3. CREATE 30-MINUTE-AHEAD TARGET
    # --------------------------------------------------------

    df["target_outlet_temp_30min"] = (
        df[TARGET].shift(-FORECAST_STEPS)
    )

    # --------------------------------------------------------
    # 4. CREATE HISTORICAL LAG FEATURES
    # --------------------------------------------------------

    feature_columns = []

    for column in BASE_FEATURES:

        for lag in [0, 1, 2, 3, 6]:

            feature_name = f"{column}_lag_{lag}"

            df[feature_name] = df[column].shift(lag)

            feature_columns.append(feature_name)

    # Drop rows without sufficient historical features or future target.
    model_df = df.dropna(
        subset=feature_columns + ["target_outlet_temp_30min"]
    ).copy()

    if len(model_df) < 100:
        raise ValueError(
            "Too few usable rows remain for model training."
        )

    X = model_df[feature_columns]
    y = model_df["target_outlet_temp_30min"]

    # --------------------------------------------------------
    # 5. CHRONOLOGICAL TRAIN / TEST SPLIT
    # --------------------------------------------------------

    split_index = int(len(model_df) * (1 - TEST_FRACTION))

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    test_timestamps = model_df["timestamp"].iloc[split_index:]

    print(f"\nTraining records: {len(X_train):,}")
    print(f"Testing records:  {len(X_test):,}")
    print(f"Training ends:    {model_df['timestamp'].iloc[split_index - 1]}")
    print(f"Testing starts:   {test_timestamps.iloc[0]}")

    # --------------------------------------------------------
    # 6. DEFINE MODELS
    # --------------------------------------------------------

    models = {
        "Persistence Baseline": None,

        "Linear Regression": make_pipeline(
            StandardScaler(),
            LinearRegression()
        ),

        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),
    }

    results = []
    predictions = {}

    # --------------------------------------------------------
    # 7. TRAIN AND EVALUATE
    # --------------------------------------------------------

    print("\nMODEL EVALUATION")
    print("-" * 65)

    for model_name, model in models.items():

        if model_name == "Persistence Baseline":
            # Predict the future temperature as the latest observed
            # outlet temperature. This is a simple reference model.
            y_pred = model_df[TARGET].iloc[split_index:].to_numpy()

        else:
            print(f"Training {model_name}...")

            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        results.append({
            "model": model_name,
            "MAE": float(mae),
            "RMSE": float(rmse),
            "R2": float(r2),
        })

        predictions[model_name] = y_pred

        print(f"\n{model_name}")
        print(f"MAE:  {mae:.4f} °C")
        print(f"RMSE: {rmse:.4f} °C")
        print(f"R²:   {r2:.4f}")

    # --------------------------------------------------------
    # 8. SAVE METRICS
    # --------------------------------------------------------

    results_df = pd.DataFrame(results).sort_values(
        by="MAE",
        ascending=True
    )

    metrics_file = REPORT_DIR / "thermal_forecasting_metrics.csv"

    results_df.to_csv(metrics_file, index=False)

    best_model_name = str(results_df.iloc[0]["model"])

    print("\nMODEL COMPARISON")
    print("-" * 65)
    print(results_df.to_string(index=False))
    print(f"\nLowest-MAE model: {best_model_name}")

    # --------------------------------------------------------
    # 9. SAVE TEST PREDICTIONS
    # --------------------------------------------------------

    prediction_df = pd.DataFrame({
        "timestamp": test_timestamps.to_numpy(),
        "actual_outlet_temp_30min": y_test.to_numpy(),
    })

    for model_name, values in predictions.items():

        safe_name = (
            model_name.lower()
            .replace(" ", "_")
        )

        prediction_df[f"predicted_{safe_name}"] = values

    prediction_file = (
        REPORT_DIR / "thermal_forecasting_predictions.csv"
    )

    prediction_df.to_csv(prediction_file, index=False)

    # --------------------------------------------------------
    # 10. PLOT ACTUAL VS PREDICTED TEMPERATURE
    # --------------------------------------------------------

    # Plot a readable sample of the first 500 test records.
    plot_count = min(500, len(prediction_df))
    plot_df = prediction_df.iloc[:plot_count]

    plt.figure(figsize=(15, 6))

    plt.plot(
        plot_df["timestamp"],
        plot_df["actual_outlet_temp_30min"],
        label="Actual future outlet temperature",
        linewidth=1.5
    )

    for model_name in models:

        safe_name = model_name.lower().replace(" ", "_")
        prediction_column = f"predicted_{safe_name}"

        plt.plot(
            plot_df["timestamp"],
            plot_df[prediction_column],
            label=model_name,
            linewidth=1
        )

    plt.xlabel("Timestamp")
    plt.ylabel("Outlet temperature (°C)")
    plt.title("30-Minute-Ahead Thermal Temperature Forecast")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    forecast_plot = (
        RESULTS_DIR / "thermal_forecasting_comparison.png"
    )

    plt.savefig(forecast_plot, dpi=150)
    plt.close()

    # --------------------------------------------------------
    # 11. SAVE SUMMARY
    # --------------------------------------------------------

    summary = {
        "task": "30-minute-ahead mean outlet temperature forecasting",
        "forecast_horizon_minutes": 30,
        "forecast_steps": FORECAST_STEPS,
        "total_input_records": int(len(df)),
        "usable_records": int(len(model_df)),
        "training_records": int(len(X_train)),
        "testing_records": int(len(X_test)),
        "irregular_intervals": irregular_count,
        "feature_count": int(len(feature_columns)),
        "models_evaluated": results,
        "lowest_mae_model": best_model_name,
        "metrics_file": str(metrics_file),
        "predictions_file": str(prediction_file),
        "comparison_plot": str(forecast_plot),
    }

    summary_file = (
        REPORT_DIR / "thermal_forecasting_summary.json"
    )

    with summary_file.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    # --------------------------------------------------------
    # 12. FINISH
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("THERMAL FORECASTING COMPLETED")
    print("=" * 65)

    print(f"Metrics:      {metrics_file}")
    print(f"Predictions:  {prediction_file}")
    print(f"Summary:      {summary_file}")
    print(f"Forecast plot: {forecast_plot}")

    print(
        "\nReminder: these are offline test results, "
        "not a live data-center deployment."
    )


if __name__ == "__main__":
    main()
