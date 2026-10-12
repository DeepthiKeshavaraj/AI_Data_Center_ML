from typing import List, Dict, Any
import pandas as pd
from fastapi import HTTPException

from app.schemas.thermal import (
    ThermalPredictRequest,
    ThermalPredictResponse,
    ThermalMetadataResponse,
)
from app.services.model_loader import registry


def get_thermal_metadata() -> ThermalMetadataResponse:
    features = [
        {"name": "mean_inlet_temp", "unit": "°C", "description": "Mean inlet airflow temperature", "default": 22.5},
        {"name": "mean_outlet_temp", "unit": "°C", "description": "Mean outlet airflow temperature", "default": 35.8},
        {"name": "mean_power_consumption", "unit": "kW", "description": "Rack electrical power consumption", "default": 14.2},
        {"name": "mean_temperature_difference", "unit": "°C", "description": "Delta (outlet minus inlet temperature)", "default": 13.3},
    ]

    thresholds = [
        {"threshold_c": 55.0, "level": "Advisory", "description": "Elevated thermal threshold for high-density rack zones"},
        {"threshold_c": 60.0, "level": "Warning", "description": "Action threshold: inspect cooling airflow and airflow containment"},
        {"threshold_c": 65.0, "level": "Critical", "description": "High temperature alarm: workload throttling or fan speed ramp"},
        {"threshold_c": 70.0, "level": "Emergency", "description": "Hardware safety thermal limit"},
        {"threshold_c": "95th Percentile", "level": "Statistical Peak", "description": "Historical top 5% temperature events from Marconi A2"},
    ]

    return ThermalMetadataResponse(
        model_name="Marconi A2 30-Minute Outlet Temperature Forecaster",
        status=registry.get_status_summary()["thermal"]["status"],
        target="target_outlet_temp_30min (°C)",
        unit="°C",
        features=features,
        forecast_horizon_minutes=30,
        exploratory_risk_thresholds=thresholds,
        status_explanation=(
            "The thermal forecasting pipeline (src/models/thermal_forecasting.py) and risk analysis "
            "(src/models/thermal_risk_analysis.py) are fully implemented. "
            "Because the multi-gigabyte Marconi A2 raw sensor datasets were omitted from Git, "
            "the trained model artifact is currently awaiting ingestion. "
            "Statistical risk criteria and architecture details are documented."
        ),
        training_script_path="src/models/thermal_forecasting.py",
    )


def predict_thermal(request: ThermalPredictRequest) -> ThermalPredictResponse:
    model = registry.thermal_model
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Thermal model artifact is unavailable. "
                "The multi-gigabyte Marconi A2 sensor dataset is pending ingestion. "
                "Fabricated temperature predictions are strictly prohibited."
            ),
        )

    # In case model is loaded
    input_df = pd.DataFrame([request.model_dump()])
    val = float(model.predict(input_df)[0])
    return ThermalPredictResponse(
        status="success",
        predicted_outlet_temp_30min=round(val, 2),
        unit="°C",
        model_status="loaded",
        message="30-minute-ahead outlet temperature predicted successfully.",
    )
