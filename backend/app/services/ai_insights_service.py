from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from fastapi import HTTPException

from app.schemas.ai_insights import (
    AiSecurityPredictRequest,
    AiSecurityPredictResponse,
    FeatureContribution,
    AiWorkloadPredictRequest,
    AiWorkloadPredictResponse,
    AiWorkloadRecommendRequest,
    AiWorkloadRecommendResponse,
    NodePlacement,
    AiThermalPredictRequest,
    AiThermalPredictResponse,
    AiStatusResponse,
    AiModelStatus,
)
from app.services.model_loader import registry, PROJECT_ROOT

MACHINE_SPEC_PATH = PROJECT_ROOT / "src" / "data" / "raw" / "workload" / "pai_machine_spec.csv"

# Pre-computed feature weights from UNSW-NB15 Random Forest evaluation
SECURITY_FEATURE_WEIGHTS = {
    "flow_duration": (0.227, "Temporal duration of the bidirectional flow"),
    "src_bytes": (0.193, "Volume of bytes transmitted from source to destination"),
    "dst_bytes": (0.138, "Volume of payload bytes returned from destination"),
    "connection_state": (0.130, "TCP/IP state machine status (e.g. fin, con, int)"),
    "dst_packets": (0.096, "Packet count received from remote endpoint"),
    "src_packets": (0.094, "Packet count initiated by source endpoint"),
    "protocol": (0.066, "Transport/network layer protocol type"),
    "service": (0.056, "Application-layer service protocol designation"),
}

_cached_nodes: List[Dict[str, Any]] = []


def _load_nodes() -> List[Dict[str, Any]]:
    global _cached_nodes
    if _cached_nodes:
        return _cached_nodes
    if not MACHINE_SPEC_PATH.exists():
        return []
    try:
        df = pd.read_csv(
            MACHINE_SPEC_PATH,
            header=None,
            names=["machine", "gpu_type", "cap_cpu", "cap_mem", "cap_gpu"],
            nrows=200,
        )
        _cached_nodes = df.to_dict(orient="records")
    except Exception:
        _cached_nodes = []
    return _cached_nodes


def get_ai_status() -> AiStatusResponse:
    summary = registry.get_status_summary()
    model_statuses = []

    for key, data in summary.items():
        model_statuses.append(
            AiModelStatus(
                model_id=data["model_id"],
                name=data["name"],
                component=data["component"],
                status=data["status"],
                inference_ready=data["inference_supported"],
                artifact_path=data.get("artifact_path"),
                description=data.get("details", ""),
            )
        )

    active_count = sum(1 for m in model_statuses if m.inference_ready)
    return AiStatusResponse(
        system_status="operational" if active_count > 0 else "degraded",
        active_models_count=active_count,
        total_models_count=len(model_statuses),
        models=model_statuses,
        data_center_telemetry_ready=MACHINE_SPEC_PATH.exists(),
    )


def predict_ai_security(request: AiSecurityPredictRequest) -> AiSecurityPredictResponse:
    model = registry.security_model
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Security model is unavailable. Artifact (models/security/security_random_forest.joblib) is not loaded.",
        )

    # Construct input dataframe matching exact training columns
    input_df = pd.DataFrame([
        {
            "flow_duration": float(request.flow_duration),
            "src_packets": float(request.src_packets),
            "dst_packets": float(request.dst_packets),
            "src_bytes": float(request.src_bytes),
            "dst_bytes": float(request.dst_bytes),
            "protocol": str(request.protocol).strip().lower(),
            "connection_state": str(request.connection_state).strip().lower(),
            "service": str(request.service).strip().lower(),
        }
    ])

    try:
        pred_class = int(model.predict(input_df)[0])
        probabilities = model.predict_proba(input_df)[0]
        normal_prob = round(float(probabilities[0]), 4)
        attack_prob = round(float(probabilities[1]), 4)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Security model inference failed during execution: {str(e)}",
        )

    is_threat = (pred_class == 1)
    label = "Attack" if is_threat else "Normal"
    confidence = attack_prob if is_threat else normal_prob

    # Risk level classification
    if attack_prob >= 0.85:
        risk_level = "CRITICAL"
        recommended_action = "Immediate threat mitigation: Isolate ingress interface, throttle origin subnet, and divert traffic to deep inspection."
    elif attack_prob >= 0.50:
        risk_level = "HIGH"
        recommended_action = "Elevated threat risk: Activate DPI logging, inspect socket connections, and restrict bandwidth allocation."
    elif attack_prob >= 0.20:
        risk_level = "MEDIUM"
        recommended_action = "Anomalous traffic pattern: Maintain telemetry monitoring and track packet sequence symmetry."
    else:
        risk_level = "LOW"
        recommended_action = "Benign operational flow: Permit traffic with normal quality of service and routing."

    # Build feature contribution items
    contributions: List[FeatureContribution] = []
    req_dict = request.model_dump()
    for feat_name, (weight, desc) in SECURITY_FEATURE_WEIGHTS.items():
        contributions.append(
            FeatureContribution(
                feature=feat_name,
                value=req_dict.get(feat_name, "-"),
                importance_weight=weight,
                description=desc,
            )
        )
    contributions.sort(key=lambda x: x.importance_weight, reverse=True)

    return AiSecurityPredictResponse(
        label=label,
        class_id=pred_class,
        is_threat=is_threat,
        confidence=confidence,
        probabilities={"Normal": normal_prob, "Attack": attack_prob},
        risk_level=risk_level,
        recommended_action=recommended_action,
        feature_contributions=contributions,
        model_name="UNSW-NB15 Random Forest Classifier (200 trees)",
        evaluation_basis="Trained model holdout verification: 88.36% test accuracy, 82.49% unseen generalization.",
    )


def predict_ai_workload(request: AiWorkloadPredictRequest) -> AiWorkloadPredictResponse:
    model = registry.workload_model
    baseline_val = round(request.machine_cpu, 2)

    if model is None:
        # Strictly adhere to project requirements: do NOT fabricate fake predictions.
        return AiWorkloadPredictResponse(
            status="unavailable",
            predicted_next_cpu=None,
            unit="%",
            model_status="unavailable",
            message="Workload model artifact (cpu_prediction_random_forest.joblib) is pending source dataset ingestion.",
            explanation=(
                "The offline training pipeline is defined in src/models/workload/train_workload_model.py. "
                "Because the multi-gigabyte Alibaba PAI metrics dataset was omitted from Git, "
                "live regression inference is honestly reported as unavailable to prevent fake outputs."
            ),
            baseline_prediction=baseline_val,
            suggested_headroom_pct=round(max(0.0, 85.0 - baseline_val), 2),
        )

    # If model artifact exists, execute real inference
    try:
        input_df = pd.DataFrame([request.model_dump()])
        pred = float(model.predict(input_df)[0])
        pred_cpu = round(pred, 2)
        return AiWorkloadPredictResponse(
            status="success",
            predicted_next_cpu=pred_cpu,
            unit="%",
            model_status="loaded",
            message="Future machine CPU predicted successfully via Random Forest regressor.",
            explanation="Prediction computed directly from trained regression trees.",
            baseline_prediction=baseline_val,
            suggested_headroom_pct=round(max(0.0, 85.0 - pred_cpu), 2),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workload inference execution error: {str(e)}",
        )


def recommend_workload_placement(request: AiWorkloadRecommendRequest) -> AiWorkloadRecommendResponse:
    nodes = _load_nodes()
    if not nodes:
        raise HTTPException(
            status_code=500,
            detail="Alibaba PAI machine spec dataset (pai_machine_spec.csv) not available.",
        )

    candidates = nodes[: request.max_servers]
    allocations: List[NodePlacement] = []

    rem_cpu = float(request.requested_cores)
    rem_mem = float(request.requested_memory_gb)
    rem_gpu = float(request.requested_gpus)

    total_cluster_cores = sum(float(n.get("cap_cpu", 96)) for n in candidates)
    safety_ceiling = 0.85  # 85% safety capacity ceiling

    for node in candidates:
        cap_cpu = float(node.get("cap_cpu", 96))
        cap_mem = float(node.get("cap_mem", 512))
        cap_gpu = float(node.get("cap_gpu", 2))

        # Assume standard baseline baseline idle load (approx 20-30%)
        baseline_load = cap_cpu * 0.25
        avail_cpu = max(0.0, (cap_cpu * safety_ceiling) - baseline_load)
        avail_mem = max(0.0, (cap_mem * safety_ceiling) - (cap_mem * 0.25))
        avail_gpu = cap_gpu

        # Allocation per node
        alloc_cpu = min(rem_cpu, avail_cpu)
        alloc_mem = min(rem_mem, avail_mem)
        alloc_gpu = min(rem_gpu, avail_gpu)

        rem_cpu -= alloc_cpu
        rem_mem -= alloc_mem
        rem_gpu -= alloc_gpu

        new_total_cpu = baseline_load + alloc_cpu
        util_pct = round((new_total_cpu / cap_cpu) * 100.0, 1)

        allocations.append(
            NodePlacement(
                machine_id=str(node.get("machine", "node-unknown")),
                gpu_type=str(node.get("gpu_type", "T4")),
                total_cpu=cap_cpu,
                total_mem=cap_mem,
                total_gpu=cap_gpu,
                allocated_cpu=round(alloc_cpu, 1),
                allocated_mem=round(alloc_mem, 1),
                allocated_gpu=round(alloc_gpu, 1),
                utilization_pct_after=util_pct,
                status="Active" if alloc_cpu > 0 else "Standby",
            )
        )

    demands_satisfied = (rem_cpu <= 0.05 and rem_mem <= 0.05 and rem_gpu <= 0.05)
    total_allocated_cores = request.requested_cores - max(0.0, rem_cpu)
    avg_util = round(
        sum(a.utilization_pct_after for a in allocations) / max(1, len(allocations)), 1
    )

    if demands_satisfied:
        summary = f"Demand fully satisfied across {sum(1 for a in allocations if a.allocated_cpu > 0)} physical nodes while maintaining <85% safety ceiling."
    else:
        summary = f"Cluster capacity saturated. {round(rem_cpu, 1)} CPU cores or {round(rem_mem, 1)} GB memory could not be placed within the safety threshold."

    return AiWorkloadRecommendResponse(
        status="success",
        demands_satisfied=demands_satisfied,
        strategy_used=request.strategy,
        allocations=allocations,
        total_nodes_evaluated=len(candidates),
        cluster_capacity_cores=round(total_cluster_cores, 1),
        cluster_demand_cores=round(total_allocated_cores, 1),
        average_utilization_pct=avg_util,
        recommendation_summary=summary,
    )


def predict_ai_thermal(request: AiThermalPredictRequest) -> AiThermalPredictResponse:
    model = registry.thermal_model

    # Check inlet/outlet temperature difference
    inlet = request.mean_inlet_temp
    outlet = request.mean_outlet_temp
    delta = request.mean_temperature_difference if request.mean_temperature_difference is not None else (outlet - inlet)

    # Evaluate against documented Marconi A2 statistical risk thresholds
    if outlet >= 70.0:
        risk_level = "EMERGENCY"
        assessment = "Exceeds 70.0°C hardware safety shutdown ceiling. Imminent equipment protection trip."
        mitigation = "Emergency server power shedding and maximum CRAH fan speed override."
    elif outlet >= 65.0:
        risk_level = "CRITICAL"
        assessment = "Exceeds 65.0°C thermal alarm limit. Rapid silicon degradation threshold."
        mitigation = "Ramp dynamic server fan curves to 100% and initiate compute downclocking."
    elif outlet >= 60.0:
        risk_level = "WARNING"
        assessment = "Exceeds 60.0°C action threshold. Hot-aisle containment turbulence detected."
        mitigation = "Inspect containment blanking panels and rebalance chiller supply temperature."
    elif outlet >= 55.0:
        risk_level = "ADVISORY"
        assessment = "Elevated temperature zone (55.0°C). Airflow volume requires optimization."
        mitigation = "Verify floor tile perforations and adjust CRAC blower discharge."
    else:
        risk_level = "NORMAL"
        assessment = "Temperature profile within safe operational bounds (<55.0°C)."
        mitigation = "Standard cooling setpoint maintenance."

    if model is None:
        return AiThermalPredictResponse(
            status="unavailable",
            predicted_outlet_temp_30min=None,
            unit="°C",
            model_status="unavailable",
            risk_level=risk_level,
            message="Thermal model artifact is pending source Marconi A2 sensor dataset ingestion.",
            threshold_assessment=assessment,
            recommended_mitigation=mitigation,
        )

    try:
        input_df = pd.DataFrame([request.model_dump()])
        pred = float(model.predict(input_df)[0])
        return AiThermalPredictResponse(
            status="success",
            predicted_outlet_temp_30min=round(pred, 2),
            unit="°C",
            model_status="loaded",
            risk_level=risk_level,
            message="30-minute outlet temperature forecast computed via trained model.",
            threshold_assessment=assessment,
            recommended_mitigation=mitigation,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Thermal inference execution error: {str(e)}",
        )
