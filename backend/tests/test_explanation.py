import sys
from pathlib import Path
import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
import openai

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.api.ai_insights_router import ai_router

test_app = FastAPI()
test_app.include_router(ai_router)
client = TestClient(test_app)


def test_explanation_status_unconfigured():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "", "GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
        res = client.get("/api/ai/explain/status")
        assert res.status_code == 200
        data = res.json()
        assert data["configured"] is False
        assert "not set" in data["message"].lower()


def test_explanation_status_configured():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-dummy-key", "OPENAI_MODEL": "gpt-4o-mini", "AI_PROVIDER": "openai", "GEMINI_API_KEY": ""}):
        res = client.get("/api/ai/explain/status")
        assert res.status_code == 200
        data = res.json()
        assert data["configured"] is True
        assert data["model"] == "gpt-4o-mini"
        assert data["provider"] == "OpenAI"


def test_explanation_status_configured_gemini():
    with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSyTestKey", "GEMINI_MODEL": "gemini-3.1-flash-lite", "AI_PROVIDER": "gemini"}):
        res = client.get("/api/ai/explain/status")
        assert res.status_code == 200
        data = res.json()
        assert data["configured"] is True
        assert data["model"] == "gemini-3.1-flash-lite"
        assert data["provider"] == "Google Gemini"


def test_explanation_missing_credentials_returns_503():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "", "GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
        payload = {
            "module": "security",
            "context": {"label": "Attack", "confidence": 0.98},
            "detail_level": "concise",
        }
        res = client.post("/api/ai/explain", json=payload)
        # Strictly ensure no fabricated response is returned
        assert res.status_code == 503
        data = res.json()
        assert "api key is not configured" in data["detail"].lower()


def test_explanation_invalid_module_fails_validation():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-dummy"}):
        payload = {
            "module": "invalid_module_name",
            "context": {"test": 123},
        }
        res = client.post("/api/ai/explain", json=payload)
        assert res.status_code == 422


def test_explanation_security_success_mocked():
    mock_openai_payload = {
        "explanation": "The Random Forest classifier flagged this OSPF flow as malicious due to zero return packets and prolonged duration.",
        "key_findings": [
            "Source transmitted 20 packets with 0 destination responses.",
            "Connection state remained in INT (interrupted) state.",
        ],
        "recommendations": [
            "Inspect upstream ingress router access logs.",
            "Verify whether OSPF neighbor discovery was authorized on this interface.",
        ],
        "limitations": [
            "Classification is based on UNSW-NB15 flow characteristics and does not confirm payload contents.",
        ],
    }

    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(mock_openai_payload)
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.prompt_tokens = 120
    mock_response.usage.completion_tokens = 85

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-dummy", "OPENAI_MODEL": "gpt-4o-mini", "AI_PROVIDER": "openai", "GEMINI_API_KEY": ""}):
        with patch("app.services.explanation_service.AsyncOpenAI") as mock_openai_cls:
            mock_client_instance = MagicMock()
            mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai_cls.return_value = mock_client_instance

            payload = {
                "module": "security",
                "context": {
                    "label": "Attack",
                    "confidence": 0.985,
                    "risk_level": "CRITICAL",
                    "flow_duration": 0.92,
                    "protocol": "ospf",
                    "src_packets": 20,
                    "dst_packets": 0,
                },
                "question": "What is the primary indicator of attack here?",
                "detail_level": "concise",
            }

            res = client.post("/api/ai/explain", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["success"] is True
            assert data["module"] == "security"
            assert "OSPF flow as malicious" in data["explanation"]
            assert len(data["key_findings"]) == 2
            assert len(data["recommendations"]) == 2
            assert len(data["limitations"]) == 1
            assert data["provider"] == "OpenAI"
            assert data["model"] == "gpt-4o-mini"
            assert data["prompt_tokens"] == 120
            assert data["completion_tokens"] == 85


def test_explanation_workload_unavailable_mocked():
    mock_openai_payload = {
        "explanation": "Live regression predictions are unavailable because the multi-gigabyte Alibaba PAI metrics dataset has not been ingested. The system provides a persistence baseline of 45.2% CPU.",
        "key_findings": [
            "Regression model artifact (cpu_prediction_random_forest.joblib) is missing from disk.",
            "Persistence baseline reflects current machine CPU load without trend extrapolation.",
        ],
        "recommendations": [
            "Ingest pai_machine_metric.csv and execute train_workload_model.py to produce the artifact.",
            "Monitor live cluster nodes using the 1,897 node allocation engine.",
        ],
        "limitations": [
            "Cannot provide 10-minute predictive outlook without the trained regression artifact.",
        ],
    }

    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(mock_openai_payload)
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.prompt_tokens = 95
    mock_response.usage.completion_tokens = 70

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-dummy", "AI_PROVIDER": "openai", "GEMINI_API_KEY": ""}):
        with patch("app.services.explanation_service.AsyncOpenAI") as mock_openai_cls:
            mock_client_instance = MagicMock()
            mock_client_instance.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai_cls.return_value = mock_client_instance

            payload = {
                "module": "workload",
                "context": {
                    "model_status": "unavailable",
                    "machine_cpu": 45.2,
                    "baseline_prediction": 45.2,
                    "suggested_headroom_pct": 39.8,
                },
                "detail_level": "concise",
            }

            res = client.post("/api/ai/explain", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert "unavailable" in data["explanation"].lower()
            assert data["module"] == "workload"


def test_explanation_openai_timeout_returns_504():
    mock_request = MagicMock()
    timeout_err = openai.APITimeoutError(request=mock_request)

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-dummy", "AI_PROVIDER": "openai", "GEMINI_API_KEY": ""}):
        with patch("app.services.explanation_service.AsyncOpenAI") as mock_openai_cls:
            mock_client_instance = MagicMock()
            mock_client_instance.chat.completions.create = AsyncMock(side_effect=timeout_err)
            mock_openai_cls.return_value = mock_client_instance

            payload = {
                "module": "thermal",
                "context": {"mean_outlet_temp": 62.5},
            }

            res = client.post("/api/ai/explain", json=payload)
            assert res.status_code == 504
            assert "timed out" in res.json()["detail"].lower()


def test_explanation_openai_auth_error_returns_401():
    mock_response = MagicMock()
    mock_response.status_code = 401
    auth_err = openai.AuthenticationError("Incorrect API key provided", response=mock_response, body=None)

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-invalid-key", "AI_PROVIDER": "openai", "GEMINI_API_KEY": ""}):
        with patch("app.services.explanation_service.AsyncOpenAI") as mock_openai_cls:
            mock_client_instance = MagicMock()
            mock_client_instance.chat.completions.create = AsyncMock(side_effect=auth_err)
            mock_openai_cls.return_value = mock_client_instance

            payload = {
                "module": "cluster",
                "context": {"total_cpu_demand": 128},
            }

            res = client.post("/api/ai/explain", json=payload)
            assert res.status_code == 401
            assert "authentication failed" in res.json()["detail"].lower()


def test_explanation_openai_rate_limit_returns_429():
    mock_response = MagicMock()
    mock_response.status_code = 429
    rate_err = openai.RateLimitError("Rate limit exceeded", response=mock_response, body=None)

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-rate-limited", "AI_PROVIDER": "openai", "GEMINI_API_KEY": ""}):
        with patch("app.services.explanation_service.AsyncOpenAI") as mock_openai_cls:
            mock_client_instance = MagicMock()
            mock_client_instance.chat.completions.create = AsyncMock(side_effect=rate_err)
            mock_openai_cls.return_value = mock_client_instance

            payload = {
                "module": "benchmarks",
                "context": {"holdout_accuracy": 0.8836},
            }

            res = client.post("/api/ai/explain", json=payload)
            assert res.status_code == 429
            assert "rate limit" in res.json()["detail"].lower()


def test_context_sanitization_removes_sensitive_keys():
    from app.schemas.explanation import ExplanationRequest

    raw_context = {
        "flow_duration": 0.125,
        "password": "supersecretpassword",
        "session_token": "token123456",
        "cookie": "sid=999",
        "safe_metric": 42,
    }

    req = ExplanationRequest(module="security", context=raw_context)
    sanitized = req.context
    assert "flow_duration" in sanitized
    assert "safe_metric" in sanitized
    assert "password" not in sanitized
    assert "session_token" not in sanitized
    assert "cookie" not in sanitized


def test_explanation_gemini_success_mocked():
    mock_payload = {
        "explanation": "Google Gemini analyzed the UNSW-NB15 flow characteristics and confirmed benign HTTP behavior.",
        "key_findings": ["Packet rate is within standard baseline", "No anomalous flags"],
        "recommendations": ["Maintain current telemetry sampling rate"],
        "limitations": ["Single flow assessment"],
    }
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_payload)
    mock_response.usage_metadata.prompt_token_count = 110
    mock_response.usage_metadata.candidates_token_count = 70

    with patch.dict("os.environ", {"GEMINI_API_KEY": "AIzaSyFakeKey", "AI_PROVIDER": "gemini", "GEMINI_MODEL": "gemini-2.0-flash"}):
        with patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            payload = {
                "module": "security",
                "context": {"label": "Normal", "confidence": 0.95},
            }
            res = client.post("/api/ai/explain", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["success"] is True
            assert data["provider"] == "Google Gemini"
            assert data["model"] == "gemini-2.0-flash"
            assert "Google Gemini" in data["explanation"]

