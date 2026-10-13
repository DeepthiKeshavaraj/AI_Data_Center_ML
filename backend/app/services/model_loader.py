from pathlib import Path
import logging
from typing import Dict, Any, Optional
import joblib

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _find_model_path(subpath: str) -> Path:
    candidates = [
        Path(__file__).resolve().parents[3] / subpath,
        Path(__file__).resolve().parents[2] / subpath,
        Path.cwd() / subpath,
        Path.cwd().parent / subpath,
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


SECURITY_MODEL_PATH = _find_model_path("models/security/security_random_forest.joblib")
WORKLOAD_MODEL_PATH = _find_model_path("models/workload/cpu_prediction_random_forest.joblib")
THERMAL_MODEL_PATH = _find_model_path("models/thermal/thermal_forecasting_model.joblib")


def _safe_relative_path(p: Path) -> Optional[str]:
    if not p.exists():
        return None
    try:
        return str(p.relative_to(PROJECT_ROOT))
    except Exception:
        return p.name


class ModelRegistry:
    def __init__(self):
        self._security_model: Optional[Any] = None
        self._workload_model: Optional[Any] = None
        self._thermal_model: Optional[Any] = None

        self._security_status: str = "unavailable"
        self._workload_status: str = "unavailable"
        self._thermal_status: str = "unavailable"

        self._security_error: Optional[str] = None
        self._workload_error: Optional[str] = None
        self._thermal_error: Optional[str] = None

        self.load_models()

    def load_models(self):
        # 1. Security Model
        if SECURITY_MODEL_PATH.exists():
            try:
                self._security_model = joblib.load(SECURITY_MODEL_PATH)
                self._security_status = "loaded"
                self._security_error = None
                logger.info(f"Loaded security model from {SECURITY_MODEL_PATH}")
            except Exception as e:
                self._security_status = "failed"
                self._security_error = f"Failed to load security model: {str(e)}"
                logger.error(self._security_error)
        else:
            self._security_status = "unavailable"
            self._security_error = f"Artifact not found at {SECURITY_MODEL_PATH}"

        # 2. Workload Model
        if WORKLOAD_MODEL_PATH.exists():
            try:
                self._workload_model = joblib.load(WORKLOAD_MODEL_PATH)
                self._workload_status = "loaded"
                self._workload_error = None
            except Exception as e:
                self._workload_status = "failed"
                self._workload_error = f"Failed to load workload model: {str(e)}"
        else:
            self._workload_status = "unavailable"
            self._workload_error = "Trained model artifact (cpu_prediction_random_forest.joblib) not found. Source metric dataset pending ingestion."

        # 3. Thermal Model
        if THERMAL_MODEL_PATH.exists():
            try:
                self._thermal_model = joblib.load(THERMAL_MODEL_PATH)
                self._thermal_status = "loaded"
                self._thermal_error = None
            except Exception as e:
                self._thermal_status = "failed"
                self._thermal_error = f"Failed to load thermal model: {str(e)}"
        else:
            self._thermal_status = "unavailable"
            self._thermal_error = "Trained model artifact not found. Marconi A2 multi-GB sensor dataset pending ingestion."

    @property
    def security_model(self):
        return self._security_model

    @property
    def workload_model(self):
        return self._workload_model

    @property
    def thermal_model(self):
        return self._thermal_model

    def get_status_summary(self) -> Dict[str, Any]:
        return {
            "security": {
                "model_id": "security",
                "name": "UNSW-NB15 Random Forest Classifier",
                "component": "Network Threat Detection",
                "status": self._security_status,
                "inference_supported": self._security_status == "loaded",
                "details": "Ready for real-time inference (200 trees, balanced weights)" if self._security_status == "loaded" else self._security_error,
                "artifact_path": _safe_relative_path(SECURITY_MODEL_PATH),
                "input_features_count": 8,
                "target": "binary_label (0=Normal, 1=Attack)",
            },
            "workload": {
                "model_id": "workload",
                "name": "Alibaba PAI Next-CPU Random Forest Regressor",
                "component": "Workload Forecasting",
                "status": self._workload_status,
                "inference_supported": self._workload_status == "loaded",
                "details": "Awaiting source dataset ingestion (cpu_next_observation.csv). Resource allocation simulation is active." if self._workload_status == "unavailable" else "Model loaded",
                "artifact_path": _safe_relative_path(WORKLOAD_MODEL_PATH),
                "input_features_count": 7,
                "target": "next_machine_cpu (%)",
            },
            "thermal": {
                "model_id": "thermal",
                "name": "Marconi A2 30-Min Outlet Temp Forecaster",
                "component": "Thermal Management",
                "status": self._thermal_status,
                "inference_supported": self._thermal_status == "loaded",
                "details": "Awaiting raw sensor dataset ingestion (Marconi A2 multi-GB inlet/outlet/power files). Statistical risk thresholds documented." if self._thermal_status == "unavailable" else "Model loaded",
                "artifact_path": _safe_relative_path(THERMAL_MODEL_PATH),
                "input_features_count": 20,
                "target": "target_outlet_temp_30min (°C)",
            },
        }


# Global singleton instance
registry = ModelRegistry()
