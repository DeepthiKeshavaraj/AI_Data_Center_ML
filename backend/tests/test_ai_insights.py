import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.api.ai_insights_router import ai_router

test_app = FastAPI()
test_app.include_router(ai_router)
client = TestClient(test_app)


def test_ai_status_endpoint():
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert data["total_models_count"] == 3
    assert data["active_models_count"] >= 1
    # Check security model status
    sec_model = next((m for m in data["models"] if m["model_id"] == "security"), None)
    assert sec_model is not None
    assert sec_model["inference_ready"] is True
    assert sec_model["status"] == "loaded"


def test_ai_security_prediction_normal_flow():
    payload = {
        "flow_duration": 0.125,
        "src_packets": 10.0,
        "dst_packets": 8.0,
        "src_bytes": 540.0,
        "dst_bytes": 320.0,
        "protocol": "tcp",
        "connection_state": "fin",
        "service": "http",
    }
    response = client.post("/api/ai/security/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "Normal"
    assert data["is_threat"] is False
    assert 0.0 <= data["confidence"] <= 1.0
    assert "probabilities" in data
    assert "Normal" in data["probabilities"]
    assert "Attack" in data["probabilities"]
    assert len(data["feature_contributions"]) == 8


def test_ai_security_prediction_attack_flow():
    payload = {
        "flow_duration": 0.921987,
        "src_packets": 20.0,
        "dst_packets": 0.0,
        "src_bytes": 1280.0,
        "dst_bytes": 0.0,
        "protocol": "ospf",
        "connection_state": "int",
        "service": "-",
    }
    response = client.post("/api/ai/security/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "Attack"
    assert data["is_threat"] is True
    assert data["class_id"] == 1
    assert data["risk_level"] in ["HIGH", "CRITICAL"]
    assert data["confidence"] >= 0.5


def test_ai_security_input_validation():
    # Negative duration should fail validation
    payload = {
        "flow_duration": -5.0,
        "src_packets": 10.0,
        "dst_packets": 8.0,
        "src_bytes": 540.0,
        "dst_bytes": 320.0,
        "protocol": "tcp",
        "connection_state": "fin",
        "service": "http",
    }
    response = client.post("/api/ai/security/predict", json=payload)
    assert response.status_code == 422


def test_ai_workload_prediction_graceful_unavailable():
    payload = {
        "machine_cpu": 45.2,
        "machine_gpu": 20.0,
        "machine_cpu_usr": 32.1,
        "machine_cpu_kernel": 8.5,
        "machine_cpu_iowait": 1.2,
        "machine_load_1": 4.1,
        "machine_num_worker": 16.0,
    }
    response = client.post("/api/ai/workload/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Since workload model artifact is omitted from git, should be honest unavailable
    assert data["status"] == "unavailable"
    assert data["predicted_next_cpu"] is None
    assert data["baseline_prediction"] == 45.2
    assert "pending" in data["message"].lower()


def test_ai_workload_recommendation():
    payload = {
        "requested_cores": 128.0,
        "requested_memory_gb": 512.0,
        "requested_gpus": 2.0,
        "strategy": "balanced",
        "max_servers": 8,
    }
    response = client.post("/api/ai/workload/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["allocations"]) == 8
    assert data["cluster_capacity_cores"] > 0
    assert data["average_utilization_pct"] > 0


def test_ai_thermal_prediction_risk_thresholds():
    # High outlet temperature (>65°C) should evaluate to CRITICAL
    payload = {
        "mean_inlet_temp": 28.0,
        "mean_outlet_temp": 66.5,
        "mean_power_consumption": 18.5,
        "mean_temperature_difference": 38.5,
    }
    response = client.post("/api/ai/thermal/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unavailable"
    assert data["predicted_outlet_temp_30min"] is None
    assert data["risk_level"] == "CRITICAL"
    assert "thermal alarm limit" in data["threshold_assessment"].lower()
    assert "fan curves" in data["recommended_mitigation"].lower()
