import React from 'react';
import {
  ShieldAlert,
  Cpu,
  Flame,
  CheckCircle2,
  ArrowRight,
  Zap,
  Activity,
  Server,
  Network,
} from 'lucide-react';
import { OverviewResponse } from '../types';
import { TabType } from '../components/Sidebar';

interface OverviewPageProps {
  overview: OverviewResponse | null;
  onNavigate: (tab: TabType) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-6 pt-1">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-xl border border-cyan-500/20 bg-gradient-to-r from-slate-900 via-slate-900/95 to-cyan-950/40 p-6 shadow-sm">
        <div className="relative z-10">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold mb-3">
            <Zap className="w-3.5 h-3.5" />
            <span>Integrated Data Center Management Framework</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight m-0">
            Intelligent AI Data Center Operations Platform
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed m-0">
            Unifying multi-domain operational intelligence across GPU/CPU workload scheduling, thermal risk prevention,
            and high-throughput network anomaly detection. Powered by native machine learning models trained on standardized
            benchmarks.
          </p>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Security Model Accuracy</span>
            <ShieldAlert className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">88.36%</div>
          <div className="text-xs text-emerald-400 font-medium mt-1">ROC-AUC: 0.9721 (UNSW-NB15)</div>
        </div>

        {/* KPI 2 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Unseen Flow Robustness</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">82.49%</div>
          <div className="text-xs text-cyan-400 font-medium mt-1">47,089 holdout flows with zero overlap</div>
        </div>

        {/* KPI 3 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Cluster Capacity Catalog</span>
            <Server className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">1,897 Nodes</div>
          <div className="text-xs text-blue-400 font-medium mt-1">Alibaba PAI Machine Specs</div>
        </div>

        {/* KPI 4 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>System Pipeline Status</span>
            <CheckCircle2 className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">Operational</div>
          <div className="text-xs text-purple-400 font-medium mt-1">FastAPI Backend + ML Model Registry</div>
        </div>
      </div>

      {/* Triad Intelligence Components Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Security Card */}
        <div className="rounded-xl border border-emerald-500/30 bg-slate-900/70 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Active & Live
              </span>
            </div>
            <h3 className="text-base font-bold text-white mb-1">Network Threat Intelligence</h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Real-time intrusion classifier detecting reconnaissance, exploits, and anomalies in network traffic flows.
            </p>
            <div className="space-y-1.5 text-xs text-slate-300 border-t border-slate-800/80 pt-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Model:</span>
                <span className="font-medium text-slate-200">Random Forest (200 trees)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Input Schema:</span>
                <span className="font-medium text-slate-200">8 Network Features</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Training Rows:</span>
                <span className="font-medium text-slate-200">175,341 flows</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Attack Recall:</span>
                <span className="font-medium text-emerald-400">95.3%</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => onNavigate('security')}
            className="mt-5 w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition cursor-pointer"
          >
            <span>Launch Threat Inference</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Workload Card */}
        <div className="rounded-xl border border-blue-500/30 bg-slate-900/70 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                <Cpu className="w-5 h-5" />
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Allocation Simulation
              </span>
            </div>
            <h3 className="text-base font-bold text-white mb-1">Workload Forecasting & Allocation</h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Simulates demand scheduling across 1,897 authentic Alibaba PAI server specifications with 85% safety caps.
            </p>
            <div className="space-y-1.5 text-xs text-slate-300 border-t border-slate-800/80 pt-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Predictive Target:</span>
                <span className="font-medium text-slate-200">next_machine_cpu (%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Documented MAE:</span>
                <span className="font-medium text-cyan-400">1.546 (R² = 0.971)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Simulation Engine:</span>
                <span className="font-medium text-slate-200">Balanced & Bin-Packing</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Cluster Catalog:</span>
                <span className="font-medium text-slate-200">1,897 Authentic Nodes</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => onNavigate('workload')}
            className="mt-5 w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 text-xs font-semibold transition cursor-pointer"
          >
            <span>Run Allocation Simulation</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Thermal Card */}
        <div className="rounded-xl border border-amber-500/30 bg-slate-900/70 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="w-9 h-9 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <Flame className="w-5 h-5" />
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                Architecture & Schema
              </span>
            </div>
            <h3 className="text-base font-bold text-white mb-1">Thermal Management & Risk</h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Statistical risk thresholds and 30-minute predictive temperature forecasting architecture for server racks.
            </p>
            <div className="space-y-1.5 text-xs text-slate-300 border-t border-slate-800/80 pt-3">
              <div className="flex justify-between">
                <span className="text-slate-400">Forecast Horizon:</span>
                <span className="font-medium text-slate-200">30 minutes ahead</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Risk Thresholds:</span>
                <span className="font-medium text-slate-200">55°C, 60°C, 65°C, 70°C</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Dataset Source:</span>
                <span className="font-medium text-slate-200">Marconi A2 Supercomputer</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Sensors Modeled:</span>
                <span className="font-medium text-slate-200">Inlet, Outlet, Power, ΔT</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => onNavigate('thermal')}
            className="mt-5 w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-lg bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 text-xs font-semibold transition cursor-pointer"
          >
            <span>View Thermal Intelligence</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Integrated Data Flow Architecture Diagram */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-base font-bold text-white mb-2 flex items-center gap-2 m-0">
          <Network className="w-5 h-5 text-cyan-400" />
          Integrated AI Data Center Decision-Making Framework
        </h3>
        <p className="text-xs text-slate-400 mb-6 mt-1">
          How heterogeneous ML models interconnect to safeguard infrastructure against resource bottlenecks, hotspot overheating, and network attacks:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex flex-col items-center">
            <Cpu className="w-8 h-8 text-blue-400 mb-2" />
            <h4 className="text-xs font-bold text-slate-200 uppercase mb-1">1. Workload Ingestion</h4>
            <p className="text-[11px] text-slate-400 m-0">
              Task queues and CPU/GPU usage metrics forecast demand variations.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex flex-col items-center">
            <Flame className="w-8 h-8 text-amber-400 mb-2" />
            <h4 className="text-xs font-bold text-slate-200 uppercase mb-1">2. Thermal Feedback</h4>
            <p className="text-[11px] text-slate-400 m-0">
              Inlet/outlet air temperatures and power dissipation predict hotspot risks.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex flex-col items-center">
            <ShieldAlert className="w-8 h-8 text-emerald-400 mb-2" />
            <h4 className="text-xs font-bold text-slate-200 uppercase mb-1">3. Security Filtering</h4>
            <p className="text-[11px] text-slate-400 m-0">
              Network telemetry is screened for probes, reconnaissance, and intrusions.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-cyan-500/40 bg-cyan-950/20 flex flex-col items-center">
            <Zap className="w-8 h-8 text-cyan-400 mb-2" />
            <h4 className="text-xs font-bold text-cyan-300 uppercase mb-1">4. Common Decision</h4>
            <p className="text-[11px] text-slate-300 m-0">
              Optimal resource allocation balancing performance, cooling, and security.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
