from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import math


class WorkloadPredictRequest(BaseModel):
    machine_cpu: float = Field(..., description="Current machine CPU utilization (%)")
    machine_gpu: float = Field(0.0, description="Current machine GPU utilization (%)")
    machine_cpu_usr: float = Field(..., description="User CPU utilization (%)")
    machine_cpu_kernel: float = Field(..., description="Kernel CPU utilization (%)")
    machine_cpu_iowait: float = Field(..., description="IO wait utilization (%)")
    machine_load_1: float = Field(..., description="1-minute machine load average")
    machine_num_worker: float = Field(..., description="Number of worker processes active")

    @field_validator("*")
    @classmethod
    def validate_finite(cls, v: float, info) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"{info.field_name} must be a finite number.")
        if v < 0:
            raise ValueError(f"{info.field_name} must be non-negative.")
        return v


class WorkloadPredictResponse(BaseModel):
    status: str
    predicted_next_cpu: Optional[float] = None
    unit: str = "%"
    model_status: str
    message: str


class WorkloadMetadataResponse(BaseModel):
    model_name: str
    status: str
    target: str
    unit: str
    features: List[Dict[str, Any]]
    baseline_comparison: Dict[str, Any]
    status_explanation: str
    training_script_path: str


class ServerAllocationDetail(BaseModel):
    machine_id: str
    gpu_type: str
    cap_cpu: float
    cap_mem: float
    cap_gpu: float
    allocated_cpu: float
    allocated_mem: float
    allocated_gpu: float
    utilization_cpu_before: float
    utilization_cpu_after: float
    status: str


class WorkloadAllocationRequest(BaseModel):
    total_cpu_demand: float = Field(..., ge=1.0, description="Total CPU cores requested")
    total_memory_demand: float = Field(..., ge=1.0, description="Total Memory (GB) requested")
    total_gpu_demand: float = Field(0.0, ge=0.0, description="Total GPUs requested")
    allocation_strategy: str = Field("balanced", description="Strategy: balanced, bin_packing, or gpu_priority")
    max_servers_to_use: int = Field(10, ge=1, le=50, description="Number of candidate cluster nodes to distribute across")


class WorkloadAllocationResponse(BaseModel):
    is_simulation: bool = True
    status: str
    feasible: bool
    strategy_used: str
    total_demanded_cpu: float
    total_allocated_cpu: float
    total_demanded_memory: float
    total_allocated_memory: float
    unallocated_cpu: float
    servers_evaluated: int
    servers_utilized: int
    server_allocations: List[ServerAllocationDetail]
    average_cluster_utilization_before: float
    average_cluster_utilization_after: float
    explanation: str
    disclaimer: str = "This is a simulated workload allocation based on authentic Alibaba PAI server specifications. No physical servers or live tasks are migrated."
