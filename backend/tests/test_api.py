import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_models_status_endpoint():
    response = client.get("/api/models/status")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) == 3

    model_ids = {m["model_id"]: m for m in data["models"]}
    assert "security" in model_ids
    assert "workload" in model_ids
    assert "thermal" in model_ids

    # Security model must be loaded
    assert model_ids["security"]["status"] == "loaded"
    assert model_ids["security"]["inference_supported"] is True

    # Workload and thermal should be truthfully marked unavailable
    assert model_ids["workload"]["status"] == "unavailable"
    assert model_ids["thermal"]["status"] == "unavailable"


def test_overview_endpoint():
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["system_status"] == "operational"
    assert data["active_models_count"] >= 1
    assert data["verified_security_accuracy"] == 0.8836


def test_security_metadata_endpoint():
    response = client.get("/api/security/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "UNSW-NB15 Random Forest Classifier"
    assert len(data["features"]) == 8
    assert len(data["sample_presets"]) >= 2


def test_security_prediction_normal_sample():
    payload = {
        "protocol": "tcp",
        "flow_duration": 0.125,
        "src_packets": 10.0,
        "dst_packets": 8.0,
        "src_bytes": 540.0,
        "dst_bytes": 320.0,
        "connection_state": "fin",
        "service": "http",
    }
    response = client.post("/api/security/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_class"] == 0
    assert data["label"] == "Normal"
    assert 0.0 <= data["attack_probability"] <= 1.0
    assert 0.0 <= data["normal_probability"] <= 1.0


def test_security_prediction_attack_sample():
    # Authentic reconnaissance probe from UNSW-NB15 test set #243
    payload = {
        "protocol": "ospf",
        "flow_duration": 0.921987,
        "src_packets": 20.0,
        "dst_packets": 0.0,
        "src_bytes": 1280.0,
        "dst_bytes": 0.0,
        "connection_state": "int",
        "service": "-",
    }
    response = client.post("/api/security/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_class"] == 1
    assert data["label"] == "Attack"
    assert data["attack_probability"] >= 0.5


def test_security_validation_rejects_negative_and_missing():
    # Negative flow duration
    bad_payload = {
        "protocol": "tcp",
        "flow_duration": -5.0,
        "src_packets": 10.0,
        "dst_packets": 8.0,
        "src_bytes": 540.0,
        "dst_bytes": 320.0,
        "connection_state": "fin",
        "service": "http",
    }
    response = client.post("/api/security/predict", json=bad_payload)
    assert response.status_code == 422  # Pydantic validation error

    # Missing required field
    missing_payload = {
        "protocol": "tcp",
        "src_packets": 10.0,
    }
    response = client.post("/api/security/predict", json=missing_payload)
    assert response.status_code == 422


def test_workload_predict_unavailable_graceful_error():
    payload = {
        "machine_cpu": 45.0,
        "machine_gpu": 10.0,
        "machine_cpu_usr": 30.0,
        "machine_cpu_kernel": 8.0,
        "machine_cpu_iowait": 2.0,
        "machine_load_1": 3.5,
        "machine_num_worker": 16.0,
    }
    response = client.post("/api/workload/predict", json=payload)
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_workload_allocation_simulation():
    payload = {
        "total_cpu_demand": 128.0,
        "total_memory_demand": 512.0,
        "total_gpu_demand": 2.0,
        "allocation_strategy": "balanced",
        "max_servers_to_use": 8,
    }
    response = client.post("/api/workload/allocate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_simulation"] is True
    assert "server_allocations" in data
    assert len(data["server_allocations"]) == 8
    assert data["total_allocated_cpu"] > 0
    assert "disclaimer" in data


def test_thermal_predict_unavailable_graceful_error():
    payload = {
        "mean_inlet_temp": 24.5,
        "mean_outlet_temp": 38.0,
        "mean_power_consumption": 12.0,
        "mean_temperature_difference": 13.5,
    }
    response = client.post("/api/thermal/predict", json=payload)
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_datasets_summary_and_sample():
    # Summary
    response = client.get("/api/datasets/summary")
    assert response.status_code == 200
    datasets = response.json()
    assert len(datasets) >= 4

    # Sample from approved dataset
    sample_res = client.get("/api/datasets/pai_machine_spec/sample?limit=5")
    assert sample_res.status_code == 200
    sample_data = sample_res.json()
    assert len(sample_data["sample_rows"]) == 5

    # Sample from ton_iot dataset (tests NaN handling)
    ton_res = client.get("/api/datasets/ton_iot/sample?limit=5")
    assert ton_res.status_code == 200
    ton_data = ton_res.json()
    assert len(ton_data["sample_rows"]) == 5

    # Sample from non-approved dataset returns 404
    bad_res = client.get("/api/datasets/non_existent_dataset/sample")
    assert bad_res.status_code == 404
