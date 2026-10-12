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
# Backend pytest suite (11 test cases covering health, models, inference, schemas, simulation, and dataset preview)
python -m pytest backend/tests/test_api.py -v

# Frontend TypeScript check and production build
cd frontend
npm run build
```

---

## 4. API Endpoints

- `GET /api/health` - System health and service version.
- `GET /api/models/status` - Live loading status for Security, Workload, and Thermal components.
- `GET /api/overview` - KPI summaries, model readiness, and cluster server count.
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

2. **Network Security Intelligence (0:45 - 1:45)**:
   - Navigate to **Security Intelligence**.
   - Click preset **"OSPF Reconnaissance Probe"** (authentic UNSW-NB15 record #243).
   - Click **"Execute ML Model Prediction"**: Observe immediate live **ATTACK** classification with 100% confidence.
   - Click preset **"Standard HTTP Web Traffic"**: Observe **NORMAL** classification with 52% probability.
   - Review feature importances chart showing flow duration (22.7%) and source bytes (19.3%) as dominant predictors.
   - Point out the confusion matrix (95.3% attack recall).

3. **Workload Allocation Simulation (1:45 - 2:30)**:
   - Navigate to **Workload & Allocation**.
   - Explain the persistence baseline comparison concept.
   - Request 128 CPU cores and 512 GB memory using the **Balanced Distribution** strategy across 8 candidate nodes.
   - Run simulation: Review before-and-after server utilization bars respecting the 85% safety ceiling.

4. **Thermal Intelligence & Datasets Catalog (2:30 - 3:00)**:
   - Navigate to **Thermal Intelligence**: Explain the 30-minute forecasting lag architecture and exploratory thresholds (55°C to 70°C).
   - Navigate to **Evaluation & Datasets**: Click **"Inspect Sample Records"** on UNSW-NB15 or Alibaba PAI to prove genuine local data integration without fabrications.