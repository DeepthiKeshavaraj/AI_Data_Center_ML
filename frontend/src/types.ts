export interface ModelStatusItem {
  model_id: string;
  name: string;
  component: string;
  status: 'loaded' | 'unavailable' | 'failed';
  inference_supported: boolean;
  details: string;
  artifact_path?: string | null;
  input_features_count: number;
  target: string;
}

export interface ModelsStatusResponse {
  models: ModelStatusItem[];
}

export interface DatasetSummary {
  id: string;
  name: string;
  component: string;
  description: string;
  size_mb: number;
  total_rows: number;
  features_count: number;
  is_available: boolean;
}

export interface OverviewResponse {
  system_status: string;
  backend_version: string;
  active_models_count: number;
  total_models_count: number;
  models: ModelStatusItem[];
  datasets_count: number;
  dataset_summary: DatasetSummary[];
  verified_security_accuracy: number;
  verified_security_roc_auc: number;
  verified_unseen_accuracy: number;
  unseen_flows_tested: number;
  cluster_servers_available: number;
}

export interface SecurityPredictRequest {
  protocol: string;
  flow_duration: number;
  src_packets: number;
  dst_packets: number;
  src_bytes: number;
  dst_bytes: number;
  connection_state: string;
  service: string;
}

export interface SecurityPredictResponse {
  status: string;
  predicted_class: number;
  label: 'Normal' | 'Attack';
  attack_probability: number;
  normal_probability: number;
  confidence_score: number;
  interpretation: string;
  model_used: string;
  feature_summary: Record<string, any>;
}

export interface SecurityMetadataResponse {
  model_name: string;
  status: string;
  target: string;
  features: Array<{
    name: string;
    type: string;
    unit?: string;
    description: string;
    default: any;
  }>;
  class_labels: Record<string, string>;
  dataset_source: string;
  verified_metrics: {
    dataset: string;
    training_rows: number;
    test_rows: number;
    test_accuracy: number;
    balanced_accuracy: number;
    roc_auc: number;
    normal_precision: number;
    normal_recall: number;
    normal_f1: number;
    attack_precision: number;
    attack_recall: number;
    attack_f1: number;
    unseen_test_rows: number;
    unseen_accuracy: number;
    unseen_balanced_accuracy: number;
    unseen_roc_auc: number;
  };
  feature_importances: Array<{
    original_feature: string;
    importance: number;
  }>;
  sample_presets: Array<{
    name: string;
    description: string;
    expected_label: string;
    values: SecurityPredictRequest;
  }>;
}

export interface ServerAllocationDetail {
  machine_id: string;
  gpu_type: string;
  cap_cpu: number;
  cap_mem: number;
  cap_gpu: number;
  allocated_cpu: number;
  allocated_mem: number;
  allocated_gpu: number;
  utilization_cpu_before: number;
  utilization_cpu_after: number;
  status: string;
}

export interface WorkloadAllocationResponse {
  is_simulation: boolean;
  status: string;
  feasible: boolean;
  strategy_used: string;
  total_demanded_cpu: number;
  total_allocated_cpu: number;
  total_demanded_memory: number;
  total_allocated_memory: number;
  unallocated_cpu: number;
  servers_evaluated: number;
  servers_utilized: number;
  server_allocations: ServerAllocationDetail[];
  average_cluster_utilization_before: number;
  average_cluster_utilization_after: number;
  explanation: string;
  disclaimer: string;
}

export interface WorkloadMetadataResponse {
  model_name: string;
  status: string;
  target: string;
  unit: string;
  features: Array<{
    name: string;
    unit?: string;
    description: string;
    default: number;
  }>;
  baseline_comparison: Record<string, any>;
  status_explanation: string;
  training_script_path: string;
}

export interface ThermalMetadataResponse {
  model_name: string;
  status: string;
  target: string;
  unit: string;
  features: Array<{
    name: string;
    unit?: string;
    description: string;
    default: number;
  }>;
  forecast_horizon_minutes: number;
  exploratory_risk_thresholds: Array<{
    threshold_c: number | string;
    level: string;
    description: string;
  }>;
  status_explanation: string;
  training_script_path: string;
}

export interface MetricsResponse {
  security: {
    model_status: string;
    metrics: Record<string, any>;
    feature_importances: Array<{ original_feature: string; importance: number }>;
    confusion_matrix: {
      classes: string[];
      matrix: Array<{ actual: string; predicted_normal: number; predicted_attack: number }>;
    };
    unseen_confusion_matrix: {
      classes: string[];
      matrix: Array<{ actual: string; predicted_normal: number; predicted_attack: number }>;
    };
  };
  workload: {
    model_status: string;
    baseline_comparison: Record<string, any>;
    status_explanation: string;
    features: Array<any>;
  };
  thermal: {
    model_status: string;
    exploratory_risk_thresholds: Array<any>;
    status_explanation: string;
    features: Array<any>;
  };
}

export interface DatasetSampleResponse {
  id: string;
  name: string;
  columns: string[];
  total_rows: number;
  sample_rows: Record<string, any>[];
  preview_count: number;
}
