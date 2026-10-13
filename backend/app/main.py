import os
import gc

# Essential memory & thread limits for Linux containers (e.g. Render 512MiB limit)
os.environ.setdefault("MALLOC_ARENA_MAX", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import logging
from pathlib import Path

# Load environment variables from backend/.env or root .env
try:
    from dotenv import load_dotenv
    _backend_env = Path(__file__).resolve().parent.parent / ".env"
    _root_env = Path(__file__).resolve().parent.parent.parent / ".env"
    if _backend_env.exists():
        load_dotenv(_backend_env)
    elif _root_env.exists():
        load_dotenv(_root_env)
    else:
        load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.endpoints import router
from app.api.ai_insights_router import ai_router

# Free transient import allocations
gc.collect()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ai_data_center")

app = FastAPI(
    title="AI Data Center ML Intelligence API",
    description="Operational ML backend integrating workload, thermal, and security models for AI data center management.",
    version="1.0.0",
)

# CORS configuration for frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://ai-data-center-ml.vercel.app",
    "https://ai-datacenter-ml.onrender.com",
]

# Allow custom frontend origins via environment variable
custom_origins = os.getenv("CORS_ORIGINS") or os.getenv("FRONTEND_ORIGIN")
if custom_origins:
    for origin in custom_origins.split(","):
        trimmed = origin.strip()
        if trimmed and trimmed not in origins:
            origins.append(trimmed)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https://.*(onrender\.com|vercel\.app|netlify\.app|pages\.dev)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(ai_router)

# Determine if built frontend distribution exists
_possible_dist_dirs = [
    Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",
    Path(__file__).resolve().parent.parent / "dist",
    Path(__file__).resolve().parent / "dist",
]
FRONTEND_DIST_DIR = next((p for p in _possible_dist_dirs if p.exists() and (p / "index.html").exists()), None)

if FRONTEND_DIST_DIR and (FRONTEND_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="frontend_assets")


def _get_landing_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Data Center ML Operational Intelligence API</title>
  <style>
    :root {
      --bg: #090d16;
      --card-bg: rgba(17, 24, 39, 0.85);
      --card-border: rgba(56, 189, 248, 0.25);
      --text: #f3f4f6;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --accent: #10b981;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: radial-gradient(circle at 50% 0%, #172554 0%, var(--bg) 75%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .container {
      max-width: 760px;
      width: 100%;
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 36px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 40px rgba(56, 189, 248, 0.08);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #34d399;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 20px;
    }
    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #34d399;
      box-shadow: 0 0 10px #34d399;
    }
    h1 {
      font-size: 28px;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }
    p.lead {
      color: var(--text-muted);
      font-size: 15px;
      line-height: 1.6;
      margin-bottom: 28px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
      margin-bottom: 28px;
    }
    .card-link {
      display: flex;
      flex-direction: column;
      padding: 16px;
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(148, 163, 184, 0.15);
      border-radius: 10px;
      color: var(--text);
      text-decoration: none;
      transition: all 0.2s ease;
    }
    .card-link:hover {
      background: rgba(56, 189, 248, 0.12);
      border-color: rgba(56, 189, 248, 0.4);
      transform: translateY(-2px);
    }
    .card-link .title {
      font-weight: 600;
      font-size: 15px;
      color: var(--primary);
      margin-bottom: 4px;
    }
    .card-link .desc {
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.4;
    }
    .info-box {
      background: rgba(15, 23, 42, 0.85);
      border-left: 3px solid var(--primary);
      padding: 14px 18px;
      border-radius: 6px;
      font-size: 13px;
      color: #cbd5e1;
      line-height: 1.6;
    }
    .info-box code {
      background: rgba(255, 255, 255, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
      color: #7dd3fc;
      font-family: monospace;
    }
    footer {
      margin-top: 24px;
      text-align: center;
      font-size: 12px;
      color: #64748b;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="badge">
      <div class="dot"></div>
      Backend Service Online & Healthy
    </div>
    <h1>AI Data Center ML Operational Intelligence</h1>
    <p class="lead">
      Real-time ML backend integrating Workload Forecasting, Marconi A2 Thermal Risk Monitoring, Network Threat Classification, and Generative AI Operational Explanations.
    </p>

    <div class="grid">
      <a class="card-link" href="/docs">
        <span class="title">&#128216; Interactive API Docs &rarr;</span>
        <span class="desc">OpenAPI Swagger testing console (/docs)</span>
      </a>
      <a class="card-link" href="/redoc">
        <span class="title">&#128196; ReDoc Specification &rarr;</span>
        <span class="desc">Endpoint schema reference (/redoc)</span>
      </a>
      <a class="card-link" href="/api/health">
        <span class="title">&#128154; Health Check &rarr;</span>
        <span class="desc">Live service status & uptime (/api/health)</span>
      </a>
      <a class="card-link" href="/api/models/status">
        <span class="title">&#129504; ML Models Status &rarr;</span>
        <span class="desc">Status summary for all ML models</span>
      </a>
      <a class="card-link" href="/api/ai/status">
        <span class="title">&#129302; GenAI Provider Status &rarr;</span>
        <span class="desc">Google Gemini / OpenAI connectivity</span>
      </a>
      <a class="card-link" href="/api/overview">
        <span class="title">&#128202; Cluster Overview &rarr;</span>
        <span class="desc">Telemetry summary and cluster KPIs</span>
      </a>
    </div>

    <div class="info-box">
      <strong>Looking for the React Frontend Dashboard?</strong><br>
      This URL serves the FastAPI ML backend. To access the interactive React dashboard, deploy the <code>frontend/</code> directory (e.g. as a Render Static Site or on Vercel) and configure <code>VITE_API_BASE_URL=https://ai-datacenter-ml.onrender.com/api</code>.
    </div>
  </div>

  <footer>
    AI Data Center ML Operational Platform &bull; v1.0.0
  </footer>
</body>
</html>"""


@app.get("/", tags=["System"])
@app.head("/", tags=["System"])
def root_endpoint(request: Request):
    """
    Root endpoint responding to browser visits, Render health probes (HEAD), and API clients.
    """
    if request.method == "HEAD":
        return Response(status_code=200, media_type="text/html")

    # If static frontend bundle exists, serve the SPA index.html
    if FRONTEND_DIST_DIR and (FRONTEND_DIST_DIR / "index.html").exists():
        return FileResponse(str(FRONTEND_DIST_DIR / "index.html"))

    # If client explicitly requests JSON (e.g. curl or API consumers)
    accept_header = request.headers.get("accept", "")
    if "application/json" in accept_header and "text/html" not in accept_header:
        return JSONResponse(
            status_code=200,
            content={
                "status": "online",
                "service": "AI Data Center ML Operational Intelligence API",
                "version": "1.0.0",
                "docs_url": "/docs",
                "redoc_url": "/redoc",
                "health_url": "/api/health",
                "models_url": "/api/models/status",
                "ai_status_url": "/api/ai/status",
                "overview_url": "/api/overview",
            },
        )

    # Default browser presentation: landing dashboard
    return HTMLResponse(content=_get_landing_html(), status_code=200)


@app.get("/favicon.ico", include_in_schema=False)
def favicon_endpoint():
    """Satisfy browser favicon requests cleanly to avoid 404 noise."""
    return Response(status_code=204)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception processing {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred while processing the request.",
            "path": request.url.path,
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
