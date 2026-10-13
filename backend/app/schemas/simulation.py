from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.schemas.security import SecurityPredictRequest, SecurityPredictResponse


class SimulationPresetInfo(BaseModel):
    id: str
    name: str
    description: str
    initiating_domain: str
    defaults: Dict[str, Any]


class SimulationRunRequest(BaseModel):
    preset: str = Field(default="security_incident", description="Preset identifier or 'custom'")
    base_cpu_demand: float = Field(default=450.0, ge=10.0, le=2500.0, description="Base application CPU core demand")
    cluster_capacity: float = Field(default=1000.0, ge=100.0, le=5000.0, description="Total nominal cluster CPU core capacity")
    suspicious_traffic_intensity: float = Field(default=0.75, ge=0.0, le=1.0, description="Suspicious traffic factor (0.0 to 1.0)")
    ambient_inlet_temp: float = Field(default=24.0, ge=15.0, le=45.0, description="Ambient air inlet temperature in Celsius")
    throttling_threshold: float = Field(default=60.0, ge=45.0, le=75.0, description="Thermal threshold triggering dynamic downclocking in Celsius")
    inspection_overhead_factor: float = Field(default=0.25, ge=0.0, le=1.0, description="CPU inspection overhead multiplier per suspicious intensity")
    throttling_penalty_rate: float = Field(default=0.05, ge=0.01, le=0.20, description="Fraction of capacity curtailed per degree over threshold")
    max_throttling_limit: float = Field(default=0.50, ge=0.05, le=0.80, description="Maximum capacity curtailment fraction (e.g. 0.50 = 50%)")
    flow_sample: Optional[SecurityPredictRequest] = Field(default=None, description="Optional 8-feature network flow for real ML inference")


class MetricItem(BaseModel):
    label: str
    initial_value: float
    final_value: float
    unit: str
    category: str = Field(..., description="'real_ml' | 'simulation_assumption' | 'rule_policy'")
    category_label: str
    change_pct: Optional[float] = None


class SimulationEventItem(BaseModel):
    step: int
    timestamp_offset_sec: int
    domain: str = Field(..., description="'security' | 'workload' | 'thermal' | 'policy'")
    severity: str = Field(..., description="'info' | 'warning' | 'danger'")
    title: str
    description: str


class SimulationRecommendationItem(BaseModel):
    id: str
    domain: str
    priority: str = Field(..., description="'low' | 'medium' | 'high' | 'critical'")
    action: str
    rationale: str


class DomainStatus(BaseModel):
    state: str = Field(..., description="'normal' | 'warning' | 'critical'")
    headline: str
    details: str
    primary_metric: str


class SimulationRunResponse(BaseModel):
    scenario_name: str
    initiating_domain: str
    security_ml_used: bool
    security_result: Optional[SecurityPredictResponse] = None
    security_explanation: str
    
    initial_state: Dict[str, Any]
    final_state: Dict[str, Any]
    metrics: List[MetricItem]
    domain_statuses: Dict[str, DomainStatus]
    
    triggered_rules: List[str]
    event_log: List[SimulationEventItem]
    recommendations: List[SimulationRecommendationItem]
    
    is_simulation: bool = True
    disclaimer: str = (
        "Simulation Notice: Security flow classification uses the authentic trained Random Forest model when a flow is provided. "
        "Inspection overhead, CPU demand propagation, thermal dissipation, and hardware throttling policies are transparent rule-based "
        "simulations representing data center operational interactions. No physical servers were altered."
    )
