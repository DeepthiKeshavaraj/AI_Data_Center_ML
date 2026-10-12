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
} from './types';

const BASE_URL = '/api';

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchOverview(): Promise<OverviewResponse> {
  const res = await fetch(`${BASE_URL}/overview`);
  if (!res.ok) throw new Error(`Overview fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchModelsStatus(): Promise<ModelsStatusResponse> {
  const res = await fetch(`${BASE_URL}/models/status`);
  if (!res.ok) throw new Error(`Models status fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSecurityMetadata(): Promise<SecurityMetadataResponse> {
  const res = await fetch(`${BASE_URL}/security/metadata`);
  if (!res.ok) throw new Error(`Security metadata fetch failed: ${res.statusText}`);
  return res.json();
}

export async function predictSecurity(payload: SecurityPredictRequest): Promise<SecurityPredictResponse> {
  const res = await fetch(`${BASE_URL}/security/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(errorData?.detail || `Prediction error (${res.status})`);
  }
  return res.json();
}

export async function fetchWorkloadMetadata(): Promise<WorkloadMetadataResponse> {
  const res = await fetch(`${BASE_URL}/workload/metadata`);
  if (!res.ok) throw new Error(`Workload metadata fetch failed: ${res.statusText}`);
  return res.json();
}

export async function simulateWorkloadAllocation(payload: {
  total_cpu_demand: number;
  total_memory_demand: number;
  total_gpu_demand: number;
  allocation_strategy: string;
  max_servers_to_use: number;
}): Promise<WorkloadAllocationResponse> {
  const res = await fetch(`${BASE_URL}/workload/allocate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail || `Allocation error (${res.status})`);
  }
  return res.json();
}

export async function fetchThermalMetadata(): Promise<ThermalMetadataResponse> {
  const res = await fetch(`${BASE_URL}/thermal/metadata`);
  if (!res.ok) throw new Error(`Thermal metadata fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchMetrics(): Promise<MetricsResponse> {
  const res = await fetch(`${BASE_URL}/metrics`);
  if (!res.ok) throw new Error(`Metrics fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchDatasets(): Promise<DatasetSummary[]> {
  const res = await fetch(`${BASE_URL}/datasets/summary`);
  if (!res.ok) throw new Error(`Datasets fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchDatasetSample(id: string, limit = 10): Promise<DatasetSampleResponse> {
  const res = await fetch(`${BASE_URL}/datasets/${id}/sample?limit=${limit}`);
  if (!res.ok) throw new Error(`Dataset sample fetch failed: ${res.statusText}`);
  return res.json();
}
