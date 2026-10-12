from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from fastapi import HTTPException

from app.schemas.workload import (
    WorkloadPredictRequest,
    WorkloadPredictResponse,
    WorkloadMetadataResponse,
    WorkloadAllocationRequest,
    WorkloadAllocationResponse,
    ServerAllocationDetail,
)
from app.services.model_loader import registry, PROJECT_ROOT

MACHINE_SPEC_PATH = PROJECT_ROOT / "src" / "data" / "raw" / "workload" / "pai_machine_spec.csv"

# Cache loaded machine specifications
_cached_machine_specs: List[Dict[str, Any]] = []


def _load_machine_specs() -> List[Dict[str, Any]]:
    global _cached_machine_specs
    if _cached_machine_specs:
        return _cached_machine_specs

    if not MACHINE_SPEC_PATH.exists():
        return []

    try:
        # Format: machine, gpu_type, cap_cpu, cap_mem, cap_gpu
        df = pd.read_csv(
            MACHINE_SPEC_PATH,
            header=None,
            names=["machine", "gpu_type", "cap_cpu", "cap_mem", "cap_gpu"],
            nrows=100,  # Focus on top 100 representative cluster nodes
        )
        _cached_machine_specs = df.to_dict(orient="records")
    except Exception:
        _cached_machine_specs = []

    return _cached_machine_specs


def get_workload_metadata() -> WorkloadMetadataResponse:
    features = [
        {"name": "machine_cpu", "unit": "%", "description": "Current machine CPU utilization", "default": 45.2},
        {"name": "machine_gpu", "unit": "%", "description": "Current machine GPU utilization", "default": 20.0},
        {"name": "machine_cpu_usr", "unit": "%", "description": "User space CPU utilization", "default": 32.1},
        {"name": "machine_cpu_kernel", "unit": "%", "description": "Kernel space CPU utilization", "default": 8.5},
        {"name": "machine_cpu_iowait", "unit": "%", "description": "I/O wait CPU percentage", "default": 1.2},
        {"name": "machine_load_1", "unit": "load", "description": "1-minute system load average", "default": 4.1},
        {"name": "machine_num_worker", "unit": "count", "description": "Number of active workers", "default": 16.0},
    ]

    baseline_comparison = {
        "persistence_baseline": {
            "formula": "next_machine_cpu = current_machine_cpu",
            "concept": "Carries forward latest CPU observation as simple reference point",
        },
        "random_forest_regressor": {
            "hyperparameters": "n_estimators=100, max_depth=18, min_samples_leaf=5",
            "target": "next_machine_cpu (%)",
            "documented_offline_metrics": {
                "mae": 1.546,
                "rmse": 3.153,
                "r2": 0.971,
                "note": "Documented benchmark evaluation on holdout Alibaba PAI metrics (src/models/workload/train_workload_model.py). Real regression inference is disabled until the multi-GB metric dataset is ingested.",
            },
        },
    }

    return WorkloadMetadataResponse(
        model_name="Alibaba PAI Next-CPU Random Forest Regressor",
        status=registry.get_status_summary()["workload"]["status"],
        target="next_machine_cpu (%)",
        unit="%",
        features=features,
        baseline_comparison=baseline_comparison,
        status_explanation=(
            "The offline training script (src/models/workload/train_workload_model.py) is implemented. "
            "Because the source multi-gigabyte pai_machine_metric.csv was not checked into git, "
            "the trained artifact is currently unavailable for live regression. "
            "The workload allocation simulation using real server specs (pai_machine_spec.csv) is fully active."
        ),
        training_script_path="src/models/workload/train_workload_model.py",
    )


def predict_workload(request: WorkloadPredictRequest) -> WorkloadPredictResponse:
    model = registry.workload_model
    if model is None:
        # Respect the critical rule: do not fabricate predictions
        raise HTTPException(
            status_code=503,
            detail=(
                "Workload model artifact (cpu_prediction_random_forest.joblib) is unavailable. "
                "The source dataset pai_machine_metric.csv is pending ingestion. "
                "Fake predictions are strictly prohibited."
            ),
        )

    # If model is loaded, perform genuine inference
    input_df = pd.DataFrame([request.model_dump()])
    predicted_val = float(model.predict(input_df)[0])
    return WorkloadPredictResponse(
        status="success",
        predicted_next_cpu=round(predicted_val, 2),
        unit="%",
        model_status="loaded",
        message="Prediction generated using trained Random Forest regressor.",
    )


def simulate_workload_allocation(request: WorkloadAllocationRequest) -> WorkloadAllocationResponse:
    specs = _load_machine_specs()
    if not specs:
        raise HTTPException(
            status_code=500,
            detail="Machine specification dataset (pai_machine_spec.csv) not available.",
        )

    # Select candidate machines based on request limit
    candidates = specs[: request.max_servers_to_use]
    total_cluster_cpu = sum(float(c.get("cap_cpu", 96)) for c in candidates)
    total_cluster_mem = sum(float(c.get("cap_mem", 512)) for c in candidates)

    demanded_cpu = float(request.total_cpu_demand)
    demanded_mem = float(request.total_memory_demand)
    demanded_gpu = float(request.total_gpu_demand)

    # Synthesize realistic initial utilization based on typical cluster load
    allocations: List[ServerAllocationDetail] = []
    remaining_cpu = demanded_cpu
    remaining_mem = demanded_mem
    remaining_gpu = demanded_gpu

    total_initial_cpu_load = 0.0
    total_new_cpu_load = 0.0

    # Sort or organize based on strategy
    sorted_candidates = list(candidates)
    if request.allocation_strategy == "bin_packing":
        # Keep original order, filling nodes to 85%
        pass
    elif request.allocation_strategy == "gpu_priority":
        # Prioritize servers with GPU capacity
        sorted_candidates.sort(key=lambda x: float(x.get("cap_gpu", 0)), reverse=True)
    else:  # balanced
        pass

    for i, node in enumerate(sorted_candidates):
        cap_c = float(node.get("cap_cpu", 96))
        cap_m = float(node.get("cap_mem", 512))
        cap_g = float(node.get("cap_gpu", 0))

        # Initial baseline load on server (deterministic from server index for reproducibility)
        base_pct = 25.0 + (i * 3.5) % 30.0  # e.g. 25% - 55%
        initial_c = (base_pct / 100.0) * cap_c
        initial_m = (base_pct / 100.0) * cap_m
        initial_g = (base_pct / 100.0) * cap_g if cap_g > 0 else 0.0

        total_initial_cpu_load += initial_c

        alloc_c = 0.0
        alloc_m = 0.0
        alloc_g = 0.0

        # Maximum safe utilization ceiling is 85%
        safe_max_cpu = 0.85 * cap_c
        safe_max_mem = 0.85 * cap_m
        safe_max_gpu = 0.85 * cap_g if cap_g > 0 else 0.0

        available_headroom_cpu = max(0.0, safe_max_cpu - initial_c)
        available_headroom_mem = max(0.0, safe_max_mem - initial_m)
        available_headroom_gpu = max(0.0, safe_max_gpu - initial_g)

        if remaining_cpu > 0:
            if request.allocation_strategy == "balanced":
                share_target = demanded_cpu / len(sorted_candidates)
                alloc_c = min(remaining_cpu, min(share_target, available_headroom_cpu))
            else:  # bin packing or gpu priority
                alloc_c = min(remaining_cpu, available_headroom_cpu)

            remaining_cpu -= alloc_c

        if remaining_mem > 0:
            if request.allocation_strategy == "balanced":
                share_target_m = demanded_mem / len(sorted_candidates)
                alloc_m = min(remaining_mem, min(share_target_m, available_headroom_mem))
            else:
                alloc_m = min(remaining_mem, available_headroom_mem)

            remaining_mem -= alloc_m

        if remaining_gpu > 0 and cap_g > 0:
            alloc_g = min(remaining_gpu, available_headroom_gpu)
            remaining_gpu -= alloc_g

        new_c = initial_c + alloc_c
        total_new_cpu_load += new_c

        allocations.append(
            ServerAllocationDetail(
                machine_id=str(node.get("machine", f"node-{i}")),
                gpu_type=str(node.get("gpu_type", "CPU")),
                cap_cpu=cap_c,
                cap_mem=cap_m,
                cap_gpu=cap_g,
                allocated_cpu=round(alloc_c, 2),
                allocated_mem=round(alloc_m, 2),
                allocated_gpu=round(alloc_g, 2),
                utilization_cpu_before=round((initial_c / cap_c) * 100.0, 1),
                utilization_cpu_after=round((new_c / cap_c) * 100.0, 1),
                status="Assigned" if alloc_c > 0 else "Unchanged",
            )
        )

    # Any leftover unallocated load
    allocated_total_cpu = demanded_cpu - remaining_cpu
    allocated_total_mem = demanded_mem - remaining_mem
    feasible = (remaining_cpu <= 0.01) and (remaining_mem <= 0.01) and (remaining_gpu <= 0.01)

    before_avg_util = (total_initial_cpu_load / total_cluster_cpu) * 100.0
    after_avg_util = (total_new_cpu_load / total_cluster_cpu) * 100.0

    servers_used = sum(1 for a in allocations if a.allocated_cpu > 0)

    if feasible:
        explanation = (
            f"Successfully allocated {allocated_total_cpu:.1f} CPU cores and {allocated_total_mem:.1f} GB memory "
            f"across {servers_used} candidate Alibaba PAI cluster nodes using the '{request.allocation_strategy}' strategy. "
            f"Cluster average CPU utilization increased from {before_avg_util:.1f}% to {after_avg_util:.1f}% "
            f"while respecting the 85% safety threshold per node."
        )
    else:
        explanation = (
            f"Partial allocation: {allocated_total_cpu:.1f}/{demanded_cpu:.1f} CPU cores placed. "
            f"{remaining_cpu:.1f} cores could not be scheduled due to the 85% safety capacity headroom limit."
        )

    return WorkloadAllocationResponse(
        is_simulation=True,
        status="feasible" if feasible else "capacity_constrained",
        feasible=feasible,
        strategy_used=request.allocation_strategy,
        total_demanded_cpu=round(demanded_cpu, 2),
        total_allocated_cpu=round(allocated_total_cpu, 2),
        total_demanded_memory=round(demanded_mem, 2),
        total_allocated_memory=round(allocated_total_mem, 2),
        unallocated_cpu=round(remaining_cpu, 2),
        servers_evaluated=len(allocations),
        servers_utilized=servers_used,
        server_allocations=allocations,
        average_cluster_utilization_before=round(before_avg_util, 1),
        average_cluster_utilization_after=round(after_avg_util, 1),
        explanation=explanation,
    )
