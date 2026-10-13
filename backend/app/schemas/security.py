from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import math


class SecurityPredictRequest(BaseModel):
    protocol: str = Field(..., description="Network protocol (e.g. tcp, udp, ospf, arp)")
    flow_duration: float = Field(..., description="Flow duration in seconds")
    src_packets: float = Field(..., description="Source-to-destination packet count")
    dst_packets: float = Field(..., description="Destination-to-source packet count")
    src_bytes: float = Field(..., description="Source-to-destination byte count")
    dst_bytes: float = Field(..., description="Destination-to-source byte count")
    connection_state: str = Field(..., description="Connection state (e.g. fin, con, int, req)")
    service: str = Field(..., description="Application service (e.g. -, http, dns, ftp)")

    @field_validator("flow_duration", "src_packets", "dst_packets", "src_bytes", "dst_bytes")
    @classmethod
    def validate_numeric_bounds(cls, v: float, info) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"{info.field_name} must be a finite number.")
        if v < 0:
            raise ValueError(f"{info.field_name} must be non-negative.")
        return v

    @field_validator("protocol", "connection_state", "service")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        s = v.strip().lower()
        if not s:
            return "-"
        return s


class SecurityPredictResponse(BaseModel):
    status: str = "success"
    predicted_class: int = Field(..., description="0 for Normal, 1 for Attack")
    label: str = Field(..., description="Normal or Attack")
    attack_probability: float = Field(..., description="Calibrated model probability of attack")
    normal_probability: float = Field(..., description="Calibrated model probability of normal traffic")
    confidence_score: float = Field(..., description="Prediction confidence (highest class probability)")
    interpretation: str
    model_used: str
    feature_summary: Dict[str, Any]


class SecurityMetadataResponse(BaseModel):
    model_name: str
    status: str
    target: str
    features: List[Dict[str, Any]]
    class_labels: Dict[int, str]
    dataset_source: str
    verified_metrics: Dict[str, Any]
    feature_importances: List[Dict[str, Any]]
    sample_presets: List[Dict[str, Any]]
