import React, { useState } from 'react';
import {
  Cpu,
  Server,
  Layers,
  Sliders,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Info,
  BarChart3,
  Shield,
  HelpCircle,
} from 'lucide-react';
import {
  WorkloadMetadataResponse,
  WorkloadAllocationResponse,
} from '../types';
import { simulateWorkloadAllocation } from '../api';

interface WorkloadPageProps {
  metadata: WorkloadMetadataResponse | null;
}

export const WorkloadPage: React.FC<WorkloadPageProps> = ({ metadata }) => {
  // Allocation simulation state
  const [demandCpu, setDemandCpu] = useState<number>(128);
  const [demandMem, setDemandMem] = useState<number>(512);
  const [demandGpu, setDemandGpu] = useState<number>(2);
  const [strategy, setStrategy] = useState<string>('balanced');
  const [serverCount, setServerCount] = useState<number>(8);

  const [allocationResult, setAllocationResult] = useState<WorkloadAllocationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await simulateWorkloadAllocation({
        total_cpu_demand: demandCpu,
        total_memory_demand: demandMem,
        total_gpu_demand: demandGpu,
        allocation_strategy: strategy,
        max_servers_to_use: serverCount,
      });
      setAllocationResult(res);
    } catch (err: any) {
      setError(err?.message || 'Simulation execution failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Status Banner */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-white m-0">Workload Intelligence & Allocation</h2>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Alibaba PAI Engine
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 m-0">
              CPU demand regression architecture and cluster resource placement simulation powered by 1,898 authentic server specs.
            </p>
          </div>

          <div className="flex items-center space-x-2 text-xs">
            <span className="px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1.5 font-medium">
              <Info className="w-3.5 h-3.5" />
              Regression Model: Offline Architecture (Dataset Pending Ingestion)
            </span>
          </div>
        </div>
      </div>

      {/* Model Architecture & Schema Overview Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Regression Schema */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2 m-0">
            <Cpu className="w-4 h-4 text-blue-400" />
            Next-Observation CPU Regression Architecture
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed mb-4">
            The workload forecasting model (implemented in{' '}
            <code className="text-cyan-400 bg-slate-950 px-1 py-0.5 rounded">
              src/models/workload/train_workload_model.py
            </code>
            ) trains a Random Forest regressor to predict future machine CPU utilization:
          </p>

          <div className="space-y-2 text-xs font-mono bg-slate-950 p-3.5 rounded-lg border border-slate-800/80">
            <div className="text-slate-400">
              <span className="text-cyan-400 font-semibold">Features:</span> [machine_cpu, machine_gpu, machine_cpu_usr, machine_cpu_kernel, machine_cpu_iowait, machine_load_1, machine_num_worker]
            </div>
            <div className="text-slate-400">
              <span className="text-cyan-400 font-semibold">Target:</span> next_machine_cpu (%)
            </div>
            <div className="text-slate-400">
              <span className="text-cyan-400 font-semibold">Evaluation Split:</span> Chronological holdout (latest 20% per node)
            </div>
          </div>
        </div>

        {/* Persistence Baseline Comparison */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2 m-0">
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            Baseline Benchmark Reference
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed mb-4">
            The forecasting pipeline benchmarks machine learning regressors against the canonical persistence baseline:
          </p>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
              <div className="font-semibold text-slate-300">Persistence Baseline</div>
              <p className="text-[11px] text-slate-400 mt-1">
                ŷ(t+1) = y(t). Predicts next CPU equals current CPU. Serves as essential sanity benchmark.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-cyan-500/30">
              <div className="font-semibold text-cyan-300">Random Forest Regressor</div>
              <p className="text-[11px] text-slate-400 mt-1 mb-2">
                100 estimators, max depth 18. Models multi-dimensional workload and IO wait interactions.
              </p>
              <div className="space-y-1 font-mono text-[11px] border-t border-slate-800/80 pt-1.5">
                <div className="flex justify-between text-slate-300">
                  <span>Documented MAE:</span>
                  <span className="text-cyan-400 font-bold">1.546 %</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Documented RMSE:</span>
                  <span className="text-cyan-400 font-bold">3.153 %</span>
                </div>
                <div className="flex justify-between text-slate-300">
                  <span>Documented R²:</span>
                  <span className="text-emerald-400 font-bold">0.971</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Workload Allocation Simulation */}
      <div className="p-6 rounded-xl bg-slate-900/90 border border-slate-800 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4 border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2 m-0">
              <Server className="w-5 h-5 text-cyan-400" />
              Cluster Resource Allocation & Placement Simulation
            </h3>
            <p className="text-xs text-slate-400 mt-0.5 m-0">
              Evaluates capacity constraints and load distribution across authentic Alibaba PAI server specifications.
            </p>
          </div>
          <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
            Alibaba PAI Server Spec Dataset
          </span>
        </div>

        <form onSubmit={handleSimulate} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
          {/* CPU Demand */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Total CPU Cores Requested
            </label>
            <input
              type="number"
              min="1"
              max="2000"
              value={demandCpu}
              onChange={(e) => setDemandCpu(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
          </div>

          {/* Memory Demand */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Total Memory (GB) Requested
            </label>
            <input
              type="number"
              min="1"
              max="10000"
              value={demandMem}
              onChange={(e) => setDemandMem(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
          </div>

          {/* GPU Demand */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Total GPUs Requested
            </label>
            <input
              type="number"
              min="0"
              max="64"
              value={demandGpu}
              onChange={(e) => setDemandGpu(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
              required
            />
          </div>

          {/* Strategy */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Allocation Strategy
            </label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
            >
              <option value="balanced">Balanced Distribution</option>
              <option value="bin_packing">Bin Packing (Dense)</option>
              <option value="gpu_priority">GPU Node Prioritization</option>
            </select>
          </div>

          {/* Candidate Node Count */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Candidate Nodes Evaluated
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                min="2"
                max="30"
                value={serverCount}
                onChange={(e) => setServerCount(parseInt(e.target.value) || 8)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-4 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs transition disabled:opacity-50 cursor-pointer flex items-center justify-center shrink-0"
              >
                <Play className="w-3.5 h-3.5 fill-white" />
              </button>
            </div>
          </div>
        </form>

        {error && (
          <div className="p-3 mb-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {allocationResult && (
          <div className="space-y-4">
            {/* Feasibility Alert */}
            <div
              className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 ${
                allocationResult.feasible
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
              }`}
            >
              <div className="flex items-center space-x-3">
                {allocationResult.feasible ? (
                  <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
                ) : (
                  <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0" />
                )}
                <div>
                  <h4 className="text-sm font-bold uppercase tracking-wider m-0">
                    {allocationResult.feasible ? 'Feasible Allocation Proposaled' : 'Capacity Constrained'}
                  </h4>
                  <p className="text-xs opacity-90 mt-0.5 m-0">{allocationResult.explanation}</p>
                </div>
              </div>

              <div className="flex items-center space-x-4 text-xs font-mono shrink-0">
                <div>
                  <span className="opacity-75 block text-[10px]">AVG UTIL BEFORE</span>
                  <span className="font-bold text-sm">
                    {allocationResult.average_cluster_utilization_before}%
                  </span>
                </div>
                <div>
                  <span className="opacity-75 block text-[10px]">AVG UTIL AFTER</span>
                  <span className="font-bold text-sm text-cyan-400">
                    {allocationResult.average_cluster_utilization_after}%
                  </span>
                </div>
              </div>
            </div>

            {/* Server Allocation Table */}
            <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950">
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px]">
                    <tr>
                      <th className="p-3">Node ID</th>
                      <th className="p-3">GPU Type</th>
                      <th className="p-3">Node Cap (CPU/Mem/GPU)</th>
                      <th className="p-3">Assigned CPU</th>
                      <th className="p-3">Utilization Shift</th>
                      <th className="p-3 w-48">CPU Load Level</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {allocationResult.server_allocations.map((srv, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/40">
                        <td className="p-3 font-semibold text-slate-300 text-[11px]">
                          {srv.machine_id.slice(0, 14)}...
                        </td>
                        <td className="p-3 text-slate-400">{srv.gpu_type}</td>
                        <td className="p-3 text-slate-300">
                          {srv.cap_cpu}C / {srv.cap_mem}G / {srv.cap_gpu}GPU
                        </td>
                        <td className="p-3 font-bold text-cyan-400">
                          +{srv.allocated_cpu} cores
                        </td>
                        <td className="p-3 text-slate-300">
                          {srv.utilization_cpu_before}% →{' '}
                          <span className={srv.utilization_cpu_after > 80 ? 'text-amber-400' : 'text-emerald-400'}>
                            {srv.utilization_cpu_after}%
                          </span>
                        </td>
                        <td className="p-3">
                          <div className="w-full bg-slate-900 rounded-full h-2 border border-slate-800 overflow-hidden relative">
                            <div
                              className={`h-2 rounded-full transition-all ${
                                srv.utilization_cpu_after > 80 ? 'bg-amber-500' : 'bg-cyan-500'
                              }`}
                              style={{ width: `${Math.min(100, srv.utilization_cpu_after)}%` }}
                            ></div>
                            {/* 85% safety threshold mark */}
                            <div
                              className="absolute top-0 bottom-0 w-0.5 bg-rose-500"
                              style={{ left: '85%' }}
                              title="85% Safety Ceiling"
                            ></div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Disclaimer */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px] text-slate-400 flex items-start gap-2">
              <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
              <span>{allocationResult.disclaimer}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
