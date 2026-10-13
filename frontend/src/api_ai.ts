// Isolated API client for AI Insights & Real ML capabilities

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

async function aiApiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
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

export interface FeatureContribution {
  feature: string;
  value: any;
  importance_weight: number;
  description: string;
}

export interface AiSecurityPredictRequest {
  flow_duration: number;
  src_packets: number;
  dst_packets: number;
  src_bytes: number;
  dst_bytes: number;
  protocol: string;
  connection_state: string;
  service: string;
}

export interface AiSecurityPredictResponse {
  label: string;
  class_id: number;
  is_threat: boolean;
  confidence: number;
  probabilities: {
    Normal: number;
    Attack: number;
  };
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  recommended_action: string;
  feature_contributions: FeatureContribution[];
  model_name: string;
  evaluation_basis: string;
}

export interface AiWorkloadPredictRequest {
  machine_cpu: number;
  machine_gpu: number;
  machine_cpu_usr: number;
  machine_cpu_kernel: number;
  machine_cpu_iowait: number;
  machine_load_1: number;
  machine_num_worker: number;
}

export interface AiWorkloadPredictResponse {
  status: string;
  predicted_next_cpu: number | null;
  unit: string;
  model_status: string;
  message: string;
  explanation: string | null;
  baseline_prediction: number | null;
  suggested_headroom_pct: number | null;
}

export interface AiWorkloadRecommendRequest {
  requested_cores: number;
  requested_memory_gb: number;
  requested_gpus: number;
  strategy: string;
  max_servers: number;
}

export interface NodePlacement {
  machine_id: string;
  gpu_type: string;
  total_cpu: number;
  total_mem: number;
  total_gpu: number;
  allocated_cpu: number;
  allocated_mem: number;
  allocated_gpu: number;
  utilization_pct_after: number;
  status: string;
}

export interface AiWorkloadRecommendResponse {
  status: string;
  demands_satisfied: boolean;
  strategy_used: string;
  allocations: NodePlacement[];
  total_nodes_evaluated: number;
  cluster_capacity_cores: number;
  cluster_demand_cores: number;
  average_utilization_pct: number;
  recommendation_summary: string;
}

export interface AiThermalPredictRequest {
  mean_inlet_temp: number;
  mean_outlet_temp: number;
  mean_power_consumption: number;
  mean_temperature_difference?: number | null;
}

export interface AiThermalPredictResponse {
  status: string;
  predicted_outlet_temp_30min: number | null;
  unit: string;
  model_status: string;
  risk_level: string;
  message: string;
  threshold_assessment: string | null;
  recommended_mitigation: string | null;
}

export interface AiModelStatus {
  model_id: string;
  name: string;
  component: string;
  status: string;
  inference_ready: boolean;
  artifact_path: string | null;
  description: string;
}

export interface AiStatusResponse {
  system_status: string;
  active_models_count: number;
  total_models_count: number;
  models: AiModelStatus[];
  data_center_telemetry_ready: boolean;
}

export async function fetchAiStatus(): Promise<AiStatusResponse> {
  return aiApiFetch<AiStatusResponse>('/ai/status', { method: 'GET' });
}

export async function predictAiSecurity(payload: AiSecurityPredictRequest): Promise<AiSecurityPredictResponse> {
  return aiApiFetch<AiSecurityPredictResponse>('/ai/security/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function predictAiWorkload(payload: AiWorkloadPredictRequest): Promise<AiWorkloadPredictResponse> {
  return aiApiFetch<AiWorkloadPredictResponse>('/ai/workload/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function recommendWorkloadPlacement(
  payload: AiWorkloadRecommendRequest
): Promise<AiWorkloadRecommendResponse> {
  return aiApiFetch<AiWorkloadRecommendResponse>('/ai/workload/recommend', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function predictAiThermal(payload: AiThermalPredictRequest): Promise<AiThermalPredictResponse> {
  return aiApiFetch<AiThermalPredictResponse>('/ai/thermal/predict', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// --- Generative AI Explanation Interfaces & Endpoints ---

export interface ExplanationRequest {
  module: 'security' | 'workload' | 'cluster' | 'thermal' | 'benchmarks';
  context: Record<string, any>;
  question?: string;
  detail_level?: 'concise' | 'detailed';
}

export interface ExplanationResponse {
  success: boolean;
  module: string;
  explanation: string;
  key_findings: string[];
  recommendations: string[];
  limitations: string[];
  provider: string;
  model: string;
  prompt_tokens?: number;
  completion_tokens?: number;
}

export interface ExplanationStatusResponse {
  configured: boolean;
  model: string;
  provider: string;
  message: string;
}

export async function fetchExplanationStatus(): Promise<ExplanationStatusResponse> {
  return aiApiFetch<ExplanationStatusResponse>('/ai/explain/status', { method: 'GET' });
}

export async function requestExplanation(payload: ExplanationRequest): Promise<ExplanationResponse> {
  return aiApiFetch<ExplanationResponse>('/ai/explain', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

