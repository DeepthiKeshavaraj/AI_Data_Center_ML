from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ModelStatusItem(BaseModel):
    model_id: str
    name: str
    component: str
    status: str  # "loaded", "unavailable", "failed"
    inference_supported: bool
    details: str
    artifact_path: Optional[str] = None
    input_features_count: int
    target: str


class ModelsStatusResponse(BaseModel):
    models: List[ModelStatusItem]


class OverviewResponse(BaseModel):
    system_status: str
    backend_version: str
    active_models_count: int
    total_models_count: int
    models: List[ModelStatusItem]
    datasets_count: int
    dataset_summary: List[Dict[str, Any]]
    verified_security_accuracy: float
    verified_security_roc_auc: float
    verified_unseen_accuracy: float
    unseen_flows_tested: int
    cluster_servers_available: int


class MetricsResponse(BaseModel):
    security: Dict[str, Any]
    workload: Dict[str, Any]
    thermal: Dict[str, Any]
