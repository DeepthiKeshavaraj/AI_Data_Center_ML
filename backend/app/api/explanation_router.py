from fastapi import APIRouter
from app.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse,
    ExplanationStatusResponse,
)
from app.services.explanation_service import (
    generate_explanation,
    get_explanation_service_status,
)

explanation_router = APIRouter(prefix="/api/ai", tags=["Generative AI Explanations"])


@explanation_router.get("/explain/status", response_model=ExplanationStatusResponse)
def get_ai_explanation_status():
    """Check whether OpenAI Generative AI explanations are configured and ready."""
    return get_explanation_service_status()


@explanation_router.post("/explain", response_model=ExplanationResponse)
async def explain_model_prediction(request: ExplanationRequest):
    """Generate a grounded, contextual explanation for model predictions and telemetry using OpenAI."""
    return await generate_explanation(request)
