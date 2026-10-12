from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import math


class ThermalPredictRequest(BaseModel):
    mean_inlet_temp: float = Field(..., description="Mean inlet air temperature (°C)")
    mean_outlet_temp: float = Field(..., description="Mean outlet air temperature (°C)")
    mean_power_consumption: float = Field(..., description="Mean power consumption")
    mean_temperature_difference: Optional[float] = Field(None, description="Temperature difference (°C)")

    @field_validator("*")
    @classmethod
    def validate_finite(cls, v: Optional[float], info) -> Optional[float]:
        if v is not None:
            if math.isnan(v) or math.isinf(v):
                raise ValueError(f"{info.field_name} must be a finite number.")
        return v


class ThermalPredictResponse(BaseModel):
    status: str
    predicted_outlet_temp_30min: Optional[float] = None
    unit: str = "°C"
    model_status: str
    message: str


class ThermalMetadataResponse(BaseModel):
    model_name: str
    status: str
    target: str
    unit: str
    features: List[Dict[str, Any]]
    forecast_horizon_minutes: int
    exploratory_risk_thresholds: List[Dict[str, Any]]
    status_explanation: str
    training_script_path: str
