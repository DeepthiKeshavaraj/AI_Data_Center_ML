from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class ExplanationRequest(BaseModel):
    module: Literal["security", "workload", "cluster", "thermal", "benchmarks"] = Field(
        ...,
        description="The target operational module being explained",
    )
    context: Dict[str, Any] = Field(
        ...,
        description="Structured, validated telemetry and prediction outputs from the application",
    )
    question: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional operator follow-up inquiry",
    )
    detail_level: Literal["concise", "detailed"] = Field(
        "concise",
        description="Desired level of technical detail in the generated explanation",
    )

    @field_validator("context")
    @classmethod
    def sanitize_context(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        # Filter out any sensitive internal credentials or session keys if present
        sanitized = {}
        disallowed_keys = {"password", "session_token", "cookie", "token", "secret", "api_key", "authorization"}
        for k, val in v.items():
            if any(dis in k.lower() for dis in disallowed_keys):
                continue
            sanitized[k] = val
        return sanitized


class ExplanationResponse(BaseModel):
    success: bool = True
    module: str
    explanation: str
    key_findings: List[str]
    recommendations: List[str]
    limitations: List[str]
    provider: str = "OpenAI"
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None


class ExplanationStatusResponse(BaseModel):
    configured: bool
    model: str
    provider: str = "OpenAI"
    message: str
