from fastapi import APIRouter
from app.schemas.ai_insights import (
    AiStatusResponse,
    AiSecurityPredictRequest,
    AiSecurityPredictResponse,
    AiWorkloadPredictRequest,
    AiWorkloadPredictResponse,
    AiWorkloadRecommendRequest,
    AiWorkloadRecommendResponse,
    AiThermalPredictRequest,
    AiThermalPredictResponse,
)
from app.services.ai_insights_service import (
    get_ai_status,
    predict_ai_security,
    predict_ai_workload,
    recommend_workload_placement,
    predict_ai_thermal,
)

ai_router = APIRouter(prefix="/api/ai", tags=["AI Insights & Real ML"])


@ai_router.get("/status", response_model=AiStatusResponse)
def get_ai_models_status():
    """Retrieve verified status and capabilities for all AI/ML models."""
    return get_ai_status()


@ai_router.post("/security/predict", response_model=AiSecurityPredictResponse)
def execute_security_ai_prediction(request: AiSecurityPredictRequest):
    """Execute live classification on network telemetry using the trained Random Forest model."""
    return predict_ai_security(request)


@ai_router.post("/workload/predict", response_model=AiWorkloadPredictResponse)
def execute_workload_ai_prediction(request: AiWorkloadPredictRequest):
    """Predict future CPU utilization or return honest unavailable state without fake values."""
    return predict_ai_workload(request)


@ai_router.post("/workload/recommend", response_model=AiWorkloadRecommendResponse)
def execute_workload_recommendation(request: AiWorkloadRecommendRequest):
    """Generate resource allocation and placement recommendations using authentic Alibaba PAI server specs."""
    return recommend_workload_placement(request)


@ai_router.post("/thermal/predict", response_model=AiThermalPredictResponse)
def execute_thermal_ai_prediction(request: AiThermalPredictRequest):
    """Evaluate thermal risk thresholds and 30-min outlook with genuine model or statistical criteria."""
    return predict_ai_thermal(request)
