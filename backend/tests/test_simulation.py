import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.services.security_service import SAMPLE_PRESETS

client = TestClient(app)


def test_simulation_presets_endpoint():
    response = client.get("/api/simulation/presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 3
    preset_ids = {p["id"] for p in presets}
    assert "security_incident" in preset_ids
    assert "workload_surge" in preset_ids
    assert "thermal_emergency" in preset_ids


def test_simulation_security_incident_preset():
    payload = {
        "preset": "security_incident",
        "base_cpu_demand": 450.0,
        "cluster_capacity": 1000.0,
        "suspicious_traffic_intensity": 0.85,
        "ambient_inlet_temp": 24.0,
        "throttling_threshold": 60.0,
        "inspection_overhead_factor": 0.35,
        "flow_sample": SAMPLE_PRESETS[1]["values"],  # OSPF Reconnaissance Probe (Attack)
    }
    response = client.post("/api/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["initiating_domain"] == "security"
    assert data["is_simulation"] is True
    assert data["security_ml_used"] is True
    assert data["security_result"] is not None
    assert data["security_result"]["label"] == "Attack"
    assert data["security_result"]["attack_probability"] >= 0.90

    # Inspection overhead must be added
    overhead = data["final_state"]["inspection_overhead_cores"]
    assert overhead > 50.0
    assert data["final_state"]["total_cpu_demand_cores"] > 450.0

    # Verification of rule triggering and event log
    assert "SECURITY_DPI_INSPECTION_OVERHEAD_ADDED" in data["triggered_rules"]
    assert len(data["event_log"]) >= 4
    assert len(data["recommendations"]) >= 1

    # Security recommendation should be present
    sec_recs = [r for r in data["recommendations"] if r["domain"] == "security"]
    assert len(sec_recs) >= 1
    assert "Targeted Gateway Flow Filtering" in sec_recs[0]["action"]


def test_simulation_workload_surge_preset():
    payload = {
        "preset": "workload_surge",
        "base_cpu_demand": 920.0,
        "cluster_capacity": 1000.0,
        "suspicious_traffic_intensity": 0.10,
        "ambient_inlet_temp": 24.0,
        "throttling_threshold": 60.0,
        "inspection_overhead_factor": 0.15,
        "flow_sample": SAMPLE_PRESETS[0]["values"],  # Standard HTTP Traffic (Normal)
    }
    response = client.post("/api/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["initiating_domain"] == "workload"
    assert data["security_result"]["label"] == "Normal"

    # Outlet temp should climb and trigger thermal throttling
    outlet_temp = data["final_state"]["outlet_temp_c"]
    assert outlet_temp > 55.0
    assert data["final_state"]["cpu_utilization_pct"] >= 90.0

    # If temperature exceeded 60C, throttling occurred and backlog or saturation was noted
    if "THERMAL_CAPACITY_THROTTLING_TRIGGERED" in data["triggered_rules"]:
        assert data["final_state"]["throttling_penalty_pct"] > 0.0
        assert data["final_state"]["cluster_capacity_cores"] < 1000.0


def test_simulation_thermal_emergency_preset():
    payload = {
        "preset": "thermal_emergency",
        "base_cpu_demand": 750.0,
        "cluster_capacity": 1000.0,
        "suspicious_traffic_intensity": 0.15,
        "ambient_inlet_temp": 36.0,  # Hot ambient inlet air
        "throttling_threshold": 58.0,
        "inspection_overhead_factor": 0.20,
        "throttling_penalty_rate": 0.05,
        "max_throttling_limit": 0.50,
        "flow_sample": SAMPLE_PRESETS[2]["values"],  # DNS Lookup
    }
    response = client.post("/api/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["initiating_domain"] == "thermal"
    assert "THERMAL_CAPACITY_THROTTLING_TRIGGERED" in data["triggered_rules"]

    # Capacity should be curtailed
    assert data["final_state"]["cluster_capacity_cores"] < 1000.0
    assert data["final_state"]["throttling_penalty_pct"] > 0.0

    # Backlog must be accumulated due to high demand and reduced capacity
    assert data["final_state"]["backlog_cores"] > 0.0
    assert "WORKLOAD_BACKLOG_ACCUMULATED" in data["triggered_rules"]

    # Recommendations must contain thermal chiller and workload shedding
    rec_domains = {r["domain"] for r in data["recommendations"]}
    assert "thermal" in rec_domains
    assert "workload" in rec_domains


def test_simulation_determinism():
    payload = {
        "preset": "custom",
        "base_cpu_demand": 500.0,
        "cluster_capacity": 1000.0,
        "suspicious_traffic_intensity": 0.50,
        "ambient_inlet_temp": 25.0,
        "throttling_threshold": 62.0,
        "inspection_overhead_factor": 0.25,
    }
    res1 = client.post("/api/simulation/run", json=payload).json()
    res2 = client.post("/api/simulation/run", json=payload).json()

    # Exact equality across deterministic calculations
    assert res1["final_state"] == res2["final_state"]
    assert res1["initial_state"] == res2["initial_state"]
    assert res1["triggered_rules"] == res2["triggered_rules"]
    assert len(res1["event_log"]) == len(res2["event_log"])


def test_simulation_fallback_without_flow_sample():
    # When no flow_sample is provided, model is not invoked; traffic intensity is used
    payload = {
        "preset": "custom",
        "base_cpu_demand": 400.0,
        "cluster_capacity": 1000.0,
        "suspicious_traffic_intensity": 0.90,
        "ambient_inlet_temp": 22.0,
        "throttling_threshold": 60.0,
    }
    response = client.post("/api/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["security_ml_used"] is False
    assert data["security_result"] is None
    assert "Telemetry Ingestion" in data["event_log"][1]["title"]
    # High intensity should still trigger inspection overhead
    assert data["final_state"]["inspection_overhead_cores"] > 0.0


def test_simulation_input_validation():
    # Out of range temperature (< 15 or > 45)
    bad_temp_payload = {
        "preset": "custom",
        "base_cpu_demand": 500.0,
        "ambient_inlet_temp": 99.0,
    }
    res = client.post("/api/simulation/run", json=bad_temp_payload)
    assert res.status_code == 422

    # Negative CPU demand
    bad_demand_payload = {
        "preset": "custom",
        "base_cpu_demand": -100.0,
    }
    res2 = client.post("/api/simulation/run", json=bad_demand_payload)
    assert res2.status_code == 422


def test_simulation_metrics_categorization():
    payload = {
        "preset": "security_incident",
        "base_cpu_demand": 450.0,
        "cluster_capacity": 1000.0,
        "suspicious_traffic_intensity": 0.85,
        "ambient_inlet_temp": 24.0,
        "throttling_threshold": 60.0,
        "flow_sample": SAMPLE_PRESETS[1]["values"],
    }
    response = client.post("/api/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    categories = {m["category"] for m in data["metrics"]}
    assert "simulation_assumption" in categories
    assert "rule_policy" in categories

    # Ensure disclaimers are explicit
    assert "Simulation Notice" in data["disclaimer"]
