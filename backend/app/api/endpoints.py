from fastapi import APIRouter, Query, Depends, HTTPException, Request, Response, status
from typing import Dict, Any, List

from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    AuthResponse,
)
from app.schemas.models import (
    ModelsStatusResponse,
    ModelStatusItem,
    OverviewResponse,
    MetricsResponse,
)
from app.schemas.security import (
    SecurityPredictRequest,
    SecurityPredictResponse,
    SecurityMetadataResponse,
)
from app.schemas.workload import (
    WorkloadPredictRequest,
    WorkloadPredictResponse,
    WorkloadMetadataResponse,
    WorkloadAllocationRequest,
    WorkloadAllocationResponse,
)
from app.schemas.thermal import (
    ThermalPredictRequest,
    ThermalPredictResponse,
    ThermalMetadataResponse,
)
from app.schemas.simulation import (
    SimulationRunRequest,
    SimulationRunResponse,
    SimulationPresetInfo,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    get_current_user_from_token,
    invalidate_user_session,
    set_auth_cookie,
    clear_auth_cookie,
    COOKIE_NAME,
)
from app.services.db import get_db_status
from app.services.model_loader import registry
from app.services.security_service import (
    predict_security,
    get_security_metadata,
)
from app.services.workload_service import (
    get_workload_metadata,
    predict_workload,
    simulate_workload_allocation,
)
from app.services.thermal_service import (
    get_thermal_metadata,
    predict_thermal,
)
from app.services.dataset_service import (
    get_all_dataset_summaries,
    get_dataset_sample,
)
from app.services.simulation_service import (
    run_cross_domain_simulation,
    get_simulation_presets,
)

router = APIRouter(prefix="/api")


@router.get("/health", tags=["System"])
def get_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "AI Data Center ML Core API",
        "version": "1.0.0",
        "environment": "prototype_review",
    }


@router.get("/models/status", response_model=ModelsStatusResponse, tags=["Models"])
def get_models_status():
    summary = registry.get_status_summary()
    items = [ModelStatusItem(**item) for item in summary.values()]
    return ModelsStatusResponse(models=items)


@router.get("/overview", response_model=OverviewResponse, tags=["System"])
def get_overview():
    summary = registry.get_status_summary()
    items = [ModelStatusItem(**item) for item in summary.values()]
    active_count = sum(1 for item in items if item.status == "loaded")
    datasets = get_all_dataset_summaries()

    return OverviewResponse(
        system_status="operational",
        backend_version="1.0.0",
        active_models_count=active_count,
        total_models_count=len(items),
        models=items,
        datasets_count=len(datasets),
        dataset_summary=datasets,
        verified_security_accuracy=0.8836,
        verified_security_roc_auc=0.9721,
        verified_unseen_accuracy=0.8249,
        unseen_flows_tested=47089,
        cluster_servers_available=1898,
    )


# --- Security Endpoints ---
@router.get("/security/metadata", response_model=SecurityMetadataResponse, tags=["Security"])
def security_metadata():
    return get_security_metadata()


@router.post("/security/predict", response_model=SecurityPredictResponse, tags=["Security"])
def security_predict(request: SecurityPredictRequest):
    return predict_security(request)


# --- Workload Endpoints ---
@router.get("/workload/metadata", response_model=WorkloadMetadataResponse, tags=["Workload"])
def workload_metadata():
    return get_workload_metadata()


@router.post("/workload/predict", response_model=WorkloadPredictResponse, tags=["Workload"])
def workload_predict(request: WorkloadPredictRequest):
    return predict_workload(request)


@router.post("/workload/allocate", response_model=WorkloadAllocationResponse, tags=["Workload"])
def workload_allocate(request: WorkloadAllocationRequest):
    return simulate_workload_allocation(request)


# --- Thermal Endpoints ---
@router.get("/thermal/metadata", response_model=ThermalMetadataResponse, tags=["Thermal"])
def thermal_metadata():
    return get_thermal_metadata()


@router.post("/thermal/predict", response_model=ThermalPredictResponse, tags=["Thermal"])
def thermal_predict(request: ThermalPredictRequest):
    return predict_thermal(request)


# --- Metrics & Datasets ---
@router.get("/metrics", response_model=MetricsResponse, tags=["Metrics"])
def get_metrics():
    sec_meta = get_security_metadata()
    work_meta = get_workload_metadata()
    therm_meta = get_thermal_metadata()

    return MetricsResponse(
        security={
            "model_status": registry.get_status_summary()["security"]["status"],
            "metrics": sec_meta.verified_metrics,
            "feature_importances": sec_meta.feature_importances,
            "confusion_matrix": {
                "classes": ["Normal", "Attack"],
                "matrix": [
                    {"actual": "Normal", "predicted_normal": 29542, "predicted_attack": 7458},
                    {"actual": "Attack", "predicted_normal": 2129, "predicted_attack": 43203},
                ],
            },
            "unseen_confusion_matrix": {
                "classes": ["Normal", "Attack"],
                "matrix": [
                    {"actual": "Normal", "predicted_normal": 21967, "predicted_attack": 6498},
                    {"actual": "Attack", "predicted_normal": 1747, "predicted_attack": 16877},
                ],
            },
        },
        workload={
            "model_status": registry.get_status_summary()["workload"]["status"],
            "baseline_comparison": work_meta.baseline_comparison,
            "status_explanation": work_meta.status_explanation,
            "features": work_meta.features,
        },
        thermal={
            "model_status": registry.get_status_summary()["thermal"]["status"],
            "exploratory_risk_thresholds": therm_meta.exploratory_risk_thresholds,
            "status_explanation": therm_meta.status_explanation,
            "features": therm_meta.features,
        },
    )


@router.get("/datasets/summary", tags=["Datasets"])
def list_datasets():
    return get_all_dataset_summaries()


@router.get("/datasets/{dataset_id}/sample", tags=["Datasets"])
def sample_dataset(dataset_id: str, limit: int = Query(10, ge=1, le=50)):
    return get_dataset_sample(dataset_id, limit=limit)


# --- Integrated Intelligence / Impact Simulation Endpoints ---
@router.get(
    "/simulation/presets",
    response_model=List[SimulationPresetInfo],
    tags=["Simulation"],
)
def list_simulation_presets():
    return get_simulation_presets()


@router.post(
    "/simulation/run",
    response_model=SimulationRunResponse,
    tags=["Simulation"],
)
def execute_simulation(request: SimulationRunRequest):
    return run_cross_domain_simulation(request)


# --- Authentication Dependency & Endpoints ---
def get_current_user(request: Request) -> UserResponse:
    session_token = request.cookies.get(COOKIE_NAME)
    if not session_token:
        # Fallback to Authorization header if sent via Bearer
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_token = auth_header[7:].strip()

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
        )

    user = get_current_user_from_token(session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in again.",
        )
    return user


@router.post("/auth/register", response_model=AuthResponse, tags=["Authentication"])
def auth_register(req: UserRegisterRequest, response: Response):
    user, session_token = register_user(req)
    set_auth_cookie(response, session_token)
    return AuthResponse(
        status="success",
        message="Account created successfully. Welcome to AI Data Center Intelligence!",
        user=user,
        token=session_token,
    )


@router.post("/auth/login", response_model=AuthResponse, tags=["Authentication"])
def auth_login(req: UserLoginRequest, response: Response):
    user, session_token = authenticate_user(req)
    set_auth_cookie(response, session_token)
    return AuthResponse(
        status="success",
        message="Login successful.",
        user=user,
        token=session_token,
    )


@router.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
def auth_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.post("/auth/logout", tags=["Authentication"])
def auth_logout(request: Request, response: Response):
    session_token = request.cookies.get(COOKIE_NAME)
    if session_token:
        invalidate_user_session(session_token)
    clear_auth_cookie(response)
    return {"status": "success", "message": "Successfully logged out."}


@router.get("/auth/db-status", tags=["Authentication"])
def auth_db_status():
    return get_db_status()


@router.get("/dashboard/protected-data", tags=["Authentication"])
def get_protected_dashboard_data(current_user: UserResponse = Depends(get_current_user)):
    return {
        "status": "authorized",
        "user_id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "access_level": "researcher",
        "cluster_management_authorized": True,
    }

