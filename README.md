# AI Data Center Management using Machine Learning

## Final Project Review Edition • Prototype Documentation

This project implements an integrated machine-learning framework and interactive dashboard for intelligent AI data center resource management, thermal safety, and network intrusion detection.

---

## 1. System Architecture

```text
[ Network Telemetry ] ──> [ Random Forest Classifier ] ──> Network Threat Isolation (Live 88.4% Acc)
[ Alibaba PAI Spec  ] ──> [ Cluster Allocation Sim   ] ──> Balanced CPU / Memory Placement (85% Cap)
[ Thermal Telemetry ] ──> [ 30-Min Lag Regressor Spec] ──> Heat Exchanger & Airflow Advisory
                                    ↓
                 Integrated Decision-Making Dashboard (React + FastAPI)
```

---

## 2. Implemented Components Status

| Component | Status | Model / Engine | Training / Benchmark Dataset | Metrics / Output |
| :--- | :--- | :--- | :--- | :--- |
| **Integrated Impact Simulator** | **Active Simulation + Real ML** | Cross-Domain Dependency Engine + Random Forest Inference | UNSW-NB15 Flow Features & Thermodynamic Dissipation Rules | 3 Presets, DPI overhead modeling, Joule heating, DVFS throttling, backlog tracking |
| **Network Security** | **Live & Loaded** | Random Forest (200 trees, balanced weights) | UNSW-NB15 Standardized (`175,341` train, `82,332` test) | **88.36% Accuracy**, **0.9721 ROC-AUC**, **82.49% Unseen Acc** (`47,089` flows) |
| **Workload Allocation** | **Active Simulation** | Heuristic & Capacity Placement Engine | Alibaba PAI Machine Specs (`pai_machine_spec.csv`, `1,898` nodes) | Multi-node balanced load distribution with 85% safety threshold |
| **Workload Regression** | **Architecture Documented** | Next-CPU Random Forest Regressor (`train_workload_model.py`) | Alibaba PAI Machine Metrics (multi-GB source dataset pending ingestion) | Documented schema (`machine_cpu` ... `machine_num_worker` → `next_machine_cpu`) |
| **Thermal Intelligence**| **Architecture Documented** | 30-Min Outlet Temp Regressor (`thermal_forecasting.py`) | Marconi A2 Supercomputer (multi-GB sensor files pending ingestion) | Exploratory thresholds: 55°C (Advisory), 60°C (Warn), 65°C (Crit), 70°C (Emerg) |
| **Generative AI Explanations** | **Live & Integrated** | OpenAI Official SDK (`AsyncOpenAI` JSON Mode) | Live ML Model Outputs & Operational Context | Structured operational explanations, key findings, actionable recommendations & limitations |

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.12+
- Node.js v20+ / npm v10+

### A. Backend Startup (FastAPI)
```bash
# From workspace root
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- Health Check: `http://127.0.0.1:8000/api/health`
- GenAI Status: `http://127.0.0.1:8000/api/ai/explain/status`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

### B. Frontend Startup (React + Vite + Tailwind CSS)
```bash
# In the frontend directory
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
- Open in browser: `http://127.0.0.1:5173/`

### C. Running Tests
```bash
# Backend pytest suite (45 test cases covering health, models, inference, simulation, Argon2id auth, sessions, datasets, and Generative AI explanation service)
python -m pytest backend/tests/ -v

# Frontend TypeScript check and production build
cd frontend
npm run build
```

---

## 4. MongoDB Atlas & Deployment Setup

### A. Setting up MongoDB Atlas
1. Create a free M0 cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Under **Security → Database Access**, create a database user (e.g., `ai_admin`) with **Read and Write to any database** privileges.
3. Under **Security → Network Access**, add `0.0.0.0/0` (Allow Access from Anywhere) or your production server's IP address.
4. Click **Connect → Drivers → Python** and copy the connection string.
5. Copy `.env.example` to `.env` in the project root:
   ```env
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DATABASE=ai_datacenter_ml
   ENVIRONMENT=production
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   OPENAI_API_KEY=your_actual_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```
*(Note: If no `MONGODB_URI` is provided, the backend automatically initializes an in-memory test database so local testing and offline academic reviews run with 0 friction!)*

### B. Production Start Commands
- **Backend (FastAPI)**:
  ```bash
  cd backend
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```
- **Frontend (Vite / Static Hosting)**:
  ```bash
  cd frontend
  npm run build
  # Deploy dist/ to Vercel, Netlify, or Render static site
  ```

---

## 5. API Endpoints

### Authentication & Sessions (Argon2id + HttpOnly Cookies)
- `POST /api/auth/register` - Validate researcher details, hash password with Argon2id, and create account.
- `POST /api/auth/login` - Verify credentials against Argon2id hash and establish authenticated session.
- `GET /api/auth/me` - Return currently authenticated user ID, name, and email (Protected).
- `POST /api/auth/logout` - Invalidate session in database and clear HttpOnly cookie.
- `GET /api/auth/db-status` - Database health and engine diagnostic (Atlas vs Mock).
- `GET /api/dashboard/protected-data` - Authenticated dashboard resource access check.

### Core Intelligence & Simulation
- `GET /api/health` - System health and service version.
- `GET /api/models/status` - Live loading status for Security, Workload, and Thermal components.
- `GET /api/overview` - KPI summaries, model readiness, and cluster server count.
- `GET /api/simulation/presets` - Parameter defaults and descriptions for cross-domain scenario presets.
- `POST /api/simulation/run` - Executes cross-domain simulation modeling Security → Workload → Thermal dependencies.
- `GET /api/security/metadata` - Input schema, 1-click presets, verified metrics, and feature importances.
- `POST /api/security/predict` - Real-time ML inference (Normal vs Attack, probability, confidence).
- `GET /api/workload/metadata` - Feature schema and persistence baseline benchmark details.
- `POST /api/workload/predict` - Regression inference (503 with explanation when dataset pending).
- `POST /api/workload/allocate` - Cluster workload allocation simulation on 1,898 Alibaba PAI nodes.
- `GET /api/thermal/metadata` - 30-minute lag features and exploratory thermal risk thresholds.
- `POST /api/thermal/predict` - Thermal inference (503 with explanation when dataset pending).
- `GET /api/metrics` - Full verified evaluation reports from offline experiments.
- `GET /api/datasets/summary` - Standardized datasets catalog (UNSW-NB15, ToN-IoT, Alibaba PAI).
- `GET /api/datasets/{dataset_id}/sample` - Bounded sample row preview directly from disk.

### Generative AI Explanation System (Google Gemini & OpenAI Integration)
- `GET /api/ai/explain/status` - Verifies configured provider status (`Gemini` or `OpenAI`), connection health, and active model.
- `POST /api/ai/explain` - Generates grounded operational explanations from actual ML predictions and datacenter context.
  - **Payload**: `{ module: "security" | "workload" | "cluster" | "thermal" | "benchmarks", context: {...}, question?: string, detail_level?: "concise" | "detailed" }`
  - **Response**: `{ success: true, module, explanation, key_findings: [], recommendations: [], limitations: [], provider, model }`

---

## 6. Generative AI Explanation System

### A. Architecture & Grounded Design
The Generative AI layer supports both **Google Gemini** (via official `google-genai` SDK, free tier available) and **OpenAI** (via `openai` SDK):
- **Distinction from Scikit-learn Models**:
  - **Random Forest Classifier**: Computes numeric attack probability and binary classification on UNSW-NB15 network flow features.
  - **Alibaba PAI Engine**: Computes exact cluster node placements respecting CPU, GPU, memory constraints, and safety ceilings.
  - **Marconi A2 Evaluator**: Computes deterministic rule-based thermal risk against established thresholds.
  - **Generative AI Layer (Gemini / OpenAI)**: Translates the structured, validated numeric outputs into operator-friendly technical explanations, operational trade-offs, actionable recommendations, and data limitations.
- **Strict Anti-Fabrication Guardrail**:
  - The AI service does **not** simulate or hallucinate predictions.
  - If a model is unavailable (e.g. Workload 503), the AI explicitly identifies the missing model and explains that real inference could not be performed.
  - If no API key is configured, the backend returns HTTP 503 with a structured diagnostic error. **No mock AI or canned responses are ever returned.**
- **Security & Privacy**:
  - API keys are securely loaded from environment variables on the backend; they are **never** exposed to the frontend or browser network requests.
  - Context payloads automatically sanitize sensitive fields (`password`, `token`, `session_token`) before dispatching to external providers.

### B. Environment Configuration
Configure your preferred provider in `backend/.env`:

#### Option 1: Google Gemini (Recommended — Free Tier Available)
1. Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Add to `backend/.env`:
```env
GEMINI_API_KEY=AIzaSy...your-actual-gemini-key...
GEMINI_MODEL=gemini-2.0-flash
AI_PROVIDER=gemini
```

#### Option 2: OpenAI
```env
OPENAI_API_KEY=sk-...your-actual-openai-key...
OPENAI_MODEL=gpt-4o-mini
AI_PROVIDER=openai
```
*(If both are configured, `AI_PROVIDER` controls which engine is utilized)*

### C. User Workflow on the AI Insights Page
1. **Network Threat Intelligence**: Execute live Random Forest classification on network traffic → Click **"Explain with AI"** to analyze attack classification, flow metrics, and incident triage recommendations.
2. **Workload Prediction**: View 7-feature schema and baseline → Click **"Explain with AI"** to analyze PAI metrics, capacity planning, and model status.
3. **Cluster Resource Allocation**: Simulate placement across 1,898 Alibaba nodes → Click **"Explain with AI"** to interpret node assignments, memory/GPU saturation, and safety limits.
4. **Thermal Risk Evaluation**: Evaluate Marconi A2 inlet/outlet temperatures → Click **"Explain with AI"** to assess temperature deltas, throttling hazards, and cooling adjustments.
5. **Model Benchmarks**: Click **"Explain with AI"** to receive an executive briefing on the 88.36% holdout accuracy, 82.49% unseen generalization, and 0.9721 ROC-AUC.

---

## 7. 3-Minute Final Review Demonstration Script

1. **Overview Dashboard (0:00 - 0:45)**:
   - Point out live backend connection (`Core API Online`).
   - Highlight the 88.36% test accuracy and 82.49% unseen generalization score.
   - Explain the triad framework (Workload + Thermal + Security).

2. **Integrated Impact Simulator (0:45 - 1:30)** *(The Core Innovation)*:
   - Navigate to **Impact Simulator**.
   - Review the connected 3-domain network (`Security ↔ Workload ↔ Thermal`).
   - Select **"Security Incident & DPI Overhead"**: Show how high-risk traffic evaluated by Random Forest triggers Deep Packet Inspection (+CPU overhead).
   - Select **"Workload Surge & Heat Rise"**: Show how compute demand forces Joule heating past 60°C.
   - Select **"Thermal Emergency & Throttling"**: Show how high ambient inlet temp triggers safety downclocking (-42% capacity) and accumulates workload backlog.
   - Examine the Before-and-After Metrics table, Chronological Event Trace, and dynamic recommendations.

3. **Network Security Intelligence & GenAI Explanation (1:30 - 2:15)**:
   - Navigate to **Security Intelligence / AI Insights**.
   - Click preset **"OSPF Reconnaissance Probe"** (authentic UNSW-NB15 record #243) and **"Execute ML Model Prediction"**: Observe immediate live **ATTACK** classification with 100% confidence.
   - Click **"Explain with AI"**: Observe grounded analysis of flow characteristics, packet rate, triage steps, and model limitations.
   - Review feature importances chart (flow duration 22.7%, source bytes 19.3%) and 95.3% attack recall.

4. **Workload Allocation, Thermal Safety & Model Benchmarks (2:15 - 3:00)**:
   - Navigate to **Workload & Allocation**: Run allocation simulation across 1,897 Alibaba nodes respecting the 85% safety ceiling, and trigger AI operational explanation.
   - Navigate to **Thermal Risk**: Evaluate Marconi A2 cooling parameters and inspect AI thermal advisory.
   - Navigate to **Evaluation & Datasets**: Click **"Inspect Sample Records"** on UNSW-NB15 or Alibaba PAI to prove genuine local data integration without fabrications.