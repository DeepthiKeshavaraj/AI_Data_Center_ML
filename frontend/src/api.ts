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

/**
 * Production fallback Render backend URL.
 */
const DEFAULT_PRODUCTION_API_ORIGIN = 'https://ai-datacenter-ml.onrender.com';

/**
 * Returns the normalized API base URL.
 * Handles:
 * - Environment variable VITE_API_BASE_URL (if provided in Vercel or .env)
 * - Trailing slashes
 * - Ensuring the '/api' prefix is preserved exactly once
 * - Preventing duplicate '/api' prefixes (e.g. if VITE_API_BASE_URL is set to 'https://.../api')
 * - Defaulting in production to 'https://ai-datacenter-ml.onrender.com/api'
 * - Defaulting in development to '/api' (Vite dev proxy)
 */
export function getApiBaseUrl(): string {
  const envUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();

  // In local development without an explicit override, route through the Vite proxy
  if (import.meta.env.DEV && !envUrl) {
    return '/api';
  }

  // Determine starting base: explicit env var if set, otherwise default production origin
  let base = envUrl || DEFAULT_PRODUCTION_API_ORIGIN;

  // Strip trailing slashes
  base = base.replace(/\/+$/, '');

  // Ensure base ends with '/api' exactly once (avoiding duplicate '/api/api' or missing '/api')
  if (!base.endsWith('/api')) {
    base = `${base}/api`;
  }

  return base;
}

/**
 * Constructs a fully qualified URL for the given API endpoint.
 * Prevents duplicate '/api' prefixes, double slashes, or accidental relative URLs.
 */
export function buildApiUrl(endpoint: string): string {
  const base = getApiBaseUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

  // If endpoint already starts with '/api/', strip that leading '/api' so it doesn't duplicate
  const path = cleanEndpoint.startsWith('/api/') ? cleanEndpoint.slice(4) : cleanEndpoint;

  return `${base}${path}`;
}

// --- Token Management for Cross-Site Authentication Resilience ---

export function setAuthToken(token: string | null | undefined) {
  if (token) {
    try {
      localStorage.setItem('datacenter_auth_token', token);
    } catch {
      // Fallback if localStorage restricted
    }
  } else {
    try {
      localStorage.removeItem('datacenter_auth_token');
    } catch {
      // Ignore
    }
  }
}

export function getAuthToken(): string | null {
  try {
    return localStorage.getItem('datacenter_auth_token');
  } catch {
    return null;
  }
}

/**
 * Common fetch helper ensuring credentials: 'include' for HttpOnly cookie sessions
 * with fallback Authorization: Bearer header for cross-site cookie restrictions.
 */
async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const url = buildApiUrl(endpoint);
  const token = getAuthToken();
  const authHeaders: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

  const response = await fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders,
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
  const res = await apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (res?.token) {
    setAuthToken(res.token);
  }
  return res;
}

export async function loginUser(payload: {
  email: string;
  password: string;
}): Promise<AuthResponse> {
  const res = await apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  if (res?.token) {
    setAuthToken(res.token);
  }
  return res;
}

export async function fetchCurrentUser(): Promise<User> {
  return apiFetch('/auth/me', {
    method: 'GET',
  });
}

export async function logoutUser(): Promise<{ status: string; message: string }> {
  try {
    return await apiFetch('/auth/logout', {
      method: 'POST',
    });
  } finally {
    setAuthToken(null);
  }
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
