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
# Backend pytest suite (28 test cases covering health, models, inference, simulation, Argon2id auth, sessions, and datasets)
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

---

## 5. 3-Minute Final Review Demonstration Script

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

3. **Network Security Intelligence (1:30 - 2:15)**:
   - Navigate to **Security Intelligence**.
   - Click preset **"OSPF Reconnaissance Probe"** (authentic UNSW-NB15 record #243) and **"Execute ML Model Prediction"**: Observe immediate live **ATTACK** classification with 100% confidence.
   - Click preset **"Standard HTTP Web Traffic"**: Observe **NORMAL** classification with 52% probability.
   - Review feature importances chart (flow duration 22.7%, source bytes 19.3%) and 95.3% attack recall.

4. **Workload Allocation & Real Datasets (2:15 - 3:00)**:
   - Navigate to **Workload & Allocation**: Run allocation simulation across 1,897 Alibaba nodes respecting the 85% safety ceiling.
   - Navigate to **Evaluation & Datasets**: Click **"Inspect Sample Records"** on UNSW-NB15 or Alibaba PAI to prove genuine local data integration without fabrications.