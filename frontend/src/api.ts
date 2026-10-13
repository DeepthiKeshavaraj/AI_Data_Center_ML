import {
  OverviewResponse,
  ModelsStatusResponse,
  SecurityMetadataResponse,
  SecurityPredictRequest,
  SecurityPredictResponse,
  WorkloadMetadataResponse,
  WorkloadAllocationResponse,
  ThermalMetadataResponse,
  MetricsResponse,
  DatasetSummary,
  DatasetSampleResponse,
  SimulationPresetInfo,
  SimulationRunRequest,
  SimulationRunResponse,
  User,
  AuthResponse,
  DbStatusResponse,
} from './types';

// Dynamic base URL configurable via VITE_API_BASE_URL environment variable for deployment
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

/**
 * Common fetch helper ensuring credentials: 'include' for HttpOnly cookie sessions
 */
async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const message = errorData?.detail || errorData?.message || `Request failed with status ${response.status}`;
    const err = new Error(message);
    (err as any).status = response.status;
    throw err;
  }

  return response.json();
}

// --- Authentication Endpoints ---

export async function registerUser(payload: {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
}): Promise<AuthResponse> {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function loginUser(payload: {
  email: string;
  password: string;
}): Promise<AuthResponse> {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchCurrentUser(): Promise<User> {
  return apiFetch('/auth/me', {
    method: 'GET',
  });
}

export async function logoutUser(): Promise<{ status: string; message: string }> {
  return apiFetch('/auth/logout', {
    method: 'POST',
  });
}

export async function fetchDbStatus(): Promise<DbStatusResponse> {
  return apiFetch('/auth/db-status', {
    method: 'GET',
  });
}

// --- Core Intelligence & ML Endpoints ---

export async function fetchHealth() {
  return apiFetch('/health', { method: 'GET' });
}

export async function fetchOverview(): Promise<OverviewResponse> {
  return apiFetch('/overview', { method: 'GET' });
}

export async function fetchModelsStatus(): Promise<ModelsStatusResponse> {
  return apiFetch('/models/status', { method: 'GET' });
}

export async function fetchSecurityMetadata(): Promise<SecurityMetadataResponse> {
  return apiFetch('/security/metadata', { method: 'GET' });
}

export async function predictSecurity(payload: SecurityPredictRequest): Promise<SecurityPredictResponse> {
  return apiFetch('/security/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchWorkloadMetadata(): Promise<WorkloadMetadataResponse> {
  return apiFetch('/workload/metadata', { method: 'GET' });
}

export async function simulateWorkloadAllocation(payload: {
  total_cpu_demand: number;
  total_memory_demand: number;
  total_gpu_demand: number;
  allocation_strategy: string;
  max_servers_to_use: number;
}): Promise<WorkloadAllocationResponse> {
  return apiFetch('/workload/allocate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchThermalMetadata(): Promise<ThermalMetadataResponse> {
  return apiFetch('/thermal/metadata', { method: 'GET' });
}

export async function fetchMetrics(): Promise<MetricsResponse> {
  return apiFetch('/metrics', { method: 'GET' });
}

export async function fetchDatasets(): Promise<DatasetSummary[]> {
  return apiFetch('/datasets/summary', { method: 'GET' });
}

export async function fetchDatasetSample(id: string, limit = 10): Promise<DatasetSampleResponse> {
  return apiFetch(`/datasets/${id}/sample?limit=${limit}`, { method: 'GET' });
}

export async function fetchSimulationPresets(): Promise<SimulationPresetInfo[]> {
  return apiFetch('/simulation/presets', { method: 'GET' });
}

export async function runSimulation(payload: SimulationRunRequest): Promise<SimulationRunResponse> {
  return apiFetch('/simulation/run', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
