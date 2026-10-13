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
from app.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse,
    ExplanationStatusResponse,
)
from app.services.ai_insights_service import (
    get_ai_status,
    predict_ai_security,
    predict_ai_workload,
    recommend_workload_placement,
    predict_ai_thermal,
)
from app.services.explanation_service import (
    generate_explanation,
    get_explanation_service_status,
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


@ai_router.get("/explain/status", response_model=ExplanationStatusResponse)
def get_ai_explanation_status():
    """Check whether OpenAI Generative AI explanations are configured and ready."""
    return get_explanation_service_status()


@ai_router.post("/explain", response_model=ExplanationResponse)
async def explain_model_prediction(request: ExplanationRequest):
    """Generate a grounded, contextual explanation for model predictions and telemetry using OpenAI."""
    return await generate_explanation(request)
