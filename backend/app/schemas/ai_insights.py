from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import math


class AiSecurityPredictRequest(BaseModel):
    flow_duration: float = Field(..., ge=0.0, description="Flow duration in seconds")
    src_packets: float = Field(..., ge=0.0, description="Source to destination packet count")
    dst_packets: float = Field(..., ge=0.0, description="Destination to source packet count")
    src_bytes: float = Field(..., ge=0.0, description="Source to destination transaction bytes")
    dst_bytes: float = Field(..., ge=0.0, description="Destination to source transaction bytes")
    protocol: str = Field(..., min_length=1, description="Protocol name (e.g. tcp, udp, ospf, arp)")
    connection_state: str = Field(..., min_length=1, description="State (e.g. fin, con, int, req)")
    service: str = Field(..., description="Service (e.g. http, dns, ftp, smtp, -)")

    @field_validator("flow_duration", "src_packets", "dst_packets", "src_bytes", "dst_bytes")
    @classmethod
    def validate_finite_floats(cls, v: float, info) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"{info.field_name} must be a finite number.")
        if v < 0:
            raise ValueError(f"{info.field_name} must be non-negative.")
        return v


class FeatureContribution(BaseModel):
    feature: str
    value: Any
    importance_weight: float
    description: str


class AiSecurityPredictResponse(BaseModel):
    label: str  # "Normal" or "Attack"
    class_id: int  # 0 or 1
    is_threat: bool
    confidence: float
    probabilities: Dict[str, float]
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    recommended_action: str
    feature_contributions: List[FeatureContribution]
    model_name: str
    evaluation_basis: str


class AiWorkloadPredictRequest(BaseModel):
    machine_cpu: float = Field(..., ge=0.0, le=100.0, description="Current machine CPU utilization (%)")
    machine_gpu: float = Field(0.0, ge=0.0, le=100.0, description="Current machine GPU utilization (%)")
    machine_cpu_usr: float = Field(..., ge=0.0, le=100.0, description="User CPU percentage (%)")
    machine_cpu_kernel: float = Field(..., ge=0.0, le=100.0, description="Kernel CPU percentage (%)")
    machine_cpu_iowait: float = Field(..., ge=0.0, le=100.0, description="IO wait percentage (%)")
    machine_load_1: float = Field(..., ge=0.0, description="1-minute machine load average")
    machine_num_worker: float = Field(..., ge=0.0, description="Active worker process count")

    @field_validator("*")
    @classmethod
    def validate_finite(cls, v: float, info) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"{info.field_name} must be a finite number.")
        if v < 0:
            raise ValueError(f"{info.field_name} must be non-negative.")
        return v


class AiWorkloadPredictResponse(BaseModel):
    status: str
    predicted_next_cpu: Optional[float] = None
    unit: str = "%"
    model_status: str
    message: str
    explanation: Optional[str] = None
    baseline_prediction: Optional[float] = None
    suggested_headroom_pct: Optional[float] = None


class AiWorkloadRecommendRequest(BaseModel):
    requested_cores: float = Field(..., ge=1.0, description="CPU cores demanded")
    requested_memory_gb: float = Field(..., ge=1.0, description="Memory demanded in GB")
    requested_gpus: float = Field(0.0, ge=0.0, description="GPUs demanded")
    strategy: str = Field("balanced", description="Placement strategy (balanced, bin_packing, gpu_optimized)")
    max_servers: int = Field(10, ge=1, le=50, description="Candidate servers to evaluate")


class NodePlacement(BaseModel):
    machine_id: str
    gpu_type: str
    total_cpu: float
    total_mem: float
    total_gpu: float
    allocated_cpu: float
    allocated_mem: float
    allocated_gpu: float
    utilization_pct_after: float
    status: str


class AiWorkloadRecommendResponse(BaseModel):
    status: str
    demands_satisfied: bool
    strategy_used: str
    allocations: List[NodePlacement]
    total_nodes_evaluated: int
    cluster_capacity_cores: float
    cluster_demand_cores: float
    average_utilization_pct: float
    recommendation_summary: str


class AiThermalPredictRequest(BaseModel):
    mean_inlet_temp: float = Field(..., description="Mean inlet air temperature (°C)")
    mean_outlet_temp: float = Field(..., description="Mean outlet air temperature (°C)")
    mean_power_consumption: float = Field(..., description="Mean power consumption (kW)")
    mean_temperature_difference: Optional[float] = Field(None, description="Delta temperature (°C)")

    @field_validator("*")
    @classmethod
    def validate_finite(cls, v: Optional[float], info) -> Optional[float]:
        if v is not None:
            if math.isnan(v) or math.isinf(v):
                raise ValueError(f"{info.field_name} must be a finite number.")
        return v


class AiThermalPredictResponse(BaseModel):
    status: str
    predicted_outlet_temp_30min: Optional[float] = None
    unit: str = "°C"
    model_status: str
    risk_level: str
    message: str
    threshold_assessment: Optional[str] = None
    recommended_mitigation: Optional[str] = None


class AiModelStatus(BaseModel):
    model_id: str
    name: str
    component: str
    status: str  # "loaded", "unavailable", "failed"
    inference_ready: bool
    artifact_path: Optional[str] = None
    description: str


class AiStatusResponse(BaseModel):
    system_status: str
    active_models_count: int
    total_models_count: int
    models: List[AiModelStatus]
    data_center_telemetry_ready: bool
