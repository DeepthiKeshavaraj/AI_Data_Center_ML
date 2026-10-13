import React, { useState, useEffect } from 'react';
import {
  Brain,
  ShieldAlert,
  ShieldCheck,
  Cpu,
  Flame,
  Activity,
  Sparkles,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Info,
  Server,
  Layers,
  ArrowRight,
  TrendingUp,
  BarChart2,
  Lock,
  Loader2,
  Sliders,
} from 'lucide-react';
import {
  fetchAiStatus,
  predictAiSecurity,
  predictAiWorkload,
  recommendWorkloadPlacement,
  predictAiThermal,
  AiStatusResponse,
  AiSecurityPredictRequest,
  AiSecurityPredictResponse,
  AiWorkloadPredictRequest,
  AiWorkloadPredictResponse,
  AiWorkloadRecommendResponse,
  AiThermalPredictRequest,
  AiThermalPredictResponse,
} from '../api_ai';

const SECURITY_PRESETS: { name: string; desc: string; values: AiSecurityPredictRequest }[] = [
  {
    name: 'Benign Web HTTP',
    desc: 'Normal bidirectional TCP web browsing session with FIN termination.',
    values: {
      protocol: 'tcp',
      flow_duration: 0.125,
      src_packets: 10,
      dst_packets: 8,
      src_bytes: 540,
      dst_bytes: 320,
      connection_state: 'fin',
      service: 'http',
    },
  },
  {
    name: 'OSPF Reconnaissance',
    desc: 'UNSW-NB15 attack flow #243 with zero return packets.',
    values: {
      protocol: 'ospf',
      flow_duration: 0.921987,
      src_packets: 20,
      dst_packets: 0,
      src_bytes: 1280,
      dst_bytes: 0,
      connection_state: 'int',
      service: '-',
    },
  },
  {
    name: 'DNS Query',
    desc: 'Rapid UDP domain name resolution exchange.',
    values: {
      protocol: 'udp',
      flow_duration: 0.00045,
      src_packets: 2,
      dst_packets: 2,
      src_bytes: 146,
      dst_bytes: 178,
      connection_state: 'con',
      service: 'dns',
    },
  },
  {
    name: 'SYN Flood Probe',
    desc: 'One-sided high volume SYN requests without ACK completion.',
    values: {
      protocol: 'tcp',
      flow_duration: 0.0012,
      src_packets: 150,
      dst_packets: 0,
      src_bytes: 9000,
      dst_bytes: 0,
      connection_state: 'req',
      service: '-',
    },
  },
];

export const AiInsightsPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState<'security' | 'workload' | 'thermal' | 'benchmarks'>('security');
  const [aiStatus, setAiStatus] = useState<AiStatusResponse | null>(null);
  const [statusLoading, setStatusLoading] = useState<boolean>(true);

  // Security inference state
  const [secForm, setSecForm] = useState<AiSecurityPredictRequest>(SECURITY_PRESETS[0].values);
  const [secResult, setSecResult] = useState<AiSecurityPredictResponse | null>(null);
  const [secLoading, setSecLoading] = useState<boolean>(false);
  const [secError, setSecError] = useState<string | null>(null);

  // Workload inference & recommendation state
  const [wlForm, setWlForm] = useState<AiWorkloadPredictRequest>({
    machine_cpu: 45.2,
    machine_gpu: 20.0,
    machine_cpu_usr: 32.1,
    machine_cpu_kernel: 8.5,
    machine_cpu_iowait: 1.2,
    machine_load_1: 4.1,
    machine_num_worker: 16.0,
  });
  const [wlResult, setWlResult] = useState<AiWorkloadPredictResponse | null>(null);
  const [wlLoading, setWlLoading] = useState<boolean>(false);
  const [wlError, setWlError] = useState<string | null>(null);

  // Workload placement state
  const [demandCores, setDemandCores] = useState<number>(128);
  const [demandMem, setDemandMem] = useState<number>(512);
  const [demandGpus, setDemandGpus] = useState<number>(2);
  const [placementResult, setPlacementResult] = useState<AiWorkloadRecommendResponse | null>(null);
  const [placementLoading, setPlacementLoading] = useState<boolean>(false);

  // Thermal inference state
  const [thForm, setThForm] = useState<AiThermalPredictRequest>({
    mean_inlet_temp: 23.5,
    mean_outlet_temp: 58.2,
    mean_power_consumption: 15.4,
    mean_temperature_difference: 34.7,
  });
  const [thResult, setThResult] = useState<AiThermalPredictResponse | null>(null);
  const [thLoading, setThLoading] = useState<boolean>(false);
  const [thError, setThError] = useState<string | null>(null);

  useEffect(() => {
    fetchAiStatus()
      .then((data) => setAiStatus(data))
      .catch((err) => console.error('Failed to load AI status:', err))
      .finally(() => setStatusLoading(false));
  }, []);

  const handleSecuritySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSecLoading(true);
    setSecError(null);
    try {
      const res = await predictAiSecurity(secForm);
      setSecResult(res);
    } catch (err: any) {
      setSecError(err?.message || 'Security prediction failed.');
    } finally {
      setSecLoading(false);
    }
  };

  const handleWorkloadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setWlLoading(true);
    setWlError(null);
    try {
      const res = await predictAiWorkload(wlForm);
      setWlResult(res);
    } catch (err: any) {
      setWlError(err?.message || 'Workload prediction failed.');
    } finally {
      setWlLoading(false);
    }
  };

  const handleRecommendPlacement = async () => {
    setPlacementLoading(true);
    try {
      const res = await recommendWorkloadPlacement({
        requested_cores: demandCores,
        requested_memory_gb: demandMem,
        requested_gpus: demandGpus,
        strategy: 'balanced',
        max_servers: 8,
      });
      setPlacementResult(res);
    } catch (err: any) {
      console.error('Placement recommendation error:', err);
    } finally {
      setPlacementLoading(false);
    }
  };

  const handleThermalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setThLoading(true);
    setThError(null);
    try {
      const res = await predictAiThermal(thForm);
      setThResult(res);
    } catch (err: any) {
      setThError(err?.message || 'Thermal evaluation failed.');
    } finally {
      setThLoading(false);
    }
  };

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'CRITICAL':
      case 'EMERGENCY':
        return 'bg-red-500/20 text-red-400 border border-red-500/40';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border border-orange-500/40';
      case 'WARNING':
        return 'bg-amber-500/20 text-amber-400 border border-amber-500/40';
      case 'MEDIUM':
      case 'ADVISORY':
        return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <Brain className="w-4 h-4" />
              </div>
              <h2 className="text-xl font-bold text-white m-0">Dedicated AI / ML Insights</h2>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
                Operational Framework
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 m-0">
              Interactive interface for real-time model inference, honest telemetry validation, and cross-domain cluster recommendations.
            </p>
          </div>

          {/* Model Status Strip */}
          <div className="flex items-center space-x-2 text-xs">
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="font-medium">Security: Live (RF 200T)</span>
            </div>
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-slate-400">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              <span>Workload: Simulation</span>
            </div>
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-slate-400">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span>Thermal: Thresholds</span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-2 mt-5 pt-4 border-t border-slate-800">
          <button
            onClick={() => setActiveSection('security')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer flex items-center space-x-1.5 ${
              activeSection === 'security'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>1. Network Threat Intelligence (Live)</span>
          </button>

          <button
            onClick={() => setActiveSection('workload')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer flex items-center space-x-1.5 ${
              activeSection === 'workload'
                ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>2. Workload & Cluster Placement</span>
          </button>

          <button
            onClick={() => setActiveSection('thermal')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer flex items-center space-x-1.5 ${
              activeSection === 'thermal'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Flame className="w-3.5 h-3.5" />
            <span>3. Thermal Risk & Thresholds</span>
          </button>

          <button
            onClick={() => setActiveSection('benchmarks')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer flex items-center space-x-1.5 ${
              activeSection === 'benchmarks'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <BarChart2 className="w-3.5 h-3.5" />
            <span>4. Model Benchmarks & Metrics</span>
          </button>
        </div>
      </div>

      {/* SECTION 1: SECURITY INTELLIGENCE */}
      {activeSection === 'security' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Input Form Column */}
          <div className="lg:col-span-6 space-y-4">
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2 m-0">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  Network Traffic Telemetry Input
                </h3>
                <span className="text-[10px] text-emerald-400 font-mono">Live Random Forest (200 Trees)</span>
              </div>

              {/* 1-Click Presets */}
              <div className="mb-4 p-3 rounded-lg bg-slate-950 border border-slate-800/80">
                <div className="text-[11px] font-medium text-slate-400 mb-2 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Verified Telemetry Presets:</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {SECURITY_PRESETS.map((p, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        setSecForm(p.values);
                        setSecResult(null);
                        setSecError(null);
                      }}
                      className="px-2.5 py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-left border border-slate-800 hover:border-slate-700 transition cursor-pointer text-xs"
                    >
                      <div className="font-semibold text-slate-200">{p.name}</div>
                      <div className="text-[10px] text-slate-400 truncate">{p.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              <form onSubmit={handleSecuritySubmit} className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Protocol</label>
                    <select
                      value={secForm.protocol}
                      onChange={(e) => setSecForm({ ...secForm, protocol: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    >
                      <option value="tcp">TCP</option>
                      <option value="udp">UDP</option>
                      <option value="ospf">OSPF</option>
                      <option value="arp">ARP</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Connection State</label>
                    <select
                      value={secForm.connection_state}
                      onChange={(e) => setSecForm({ ...secForm, connection_state: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    >
                      <option value="fin">FIN (Graceful Close)</option>
                      <option value="con">CON (Established)</option>
                      <option value="int">INT (Interrupted / Zero Return)</option>
                      <option value="req">REQ (Requested)</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Service</label>
                    <select
                      value={secForm.service}
                      onChange={(e) => setSecForm({ ...secForm, service: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    >
                      <option value="http">HTTP</option>
                      <option value="dns">DNS</option>
                      <option value="ftp">FTP</option>
                      <option value="smtp">SMTP</option>
                      <option value="-">- (None / Raw)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Flow Duration (sec)</label>
                    <input
                      type="number"
                      step="any"
                      min="0"
                      value={secForm.flow_duration}
                      onChange={(e) => setSecForm({ ...secForm, flow_duration: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Source Packets</label>
                    <input
                      type="number"
                      min="0"
                      value={secForm.src_packets}
                      onChange={(e) => setSecForm({ ...secForm, src_packets: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Destination Packets</label>
                    <input
                      type="number"
                      min="0"
                      value={secForm.dst_packets}
                      onChange={(e) => setSecForm({ ...secForm, dst_packets: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Source Bytes</label>
                    <input
                      type="number"
                      min="0"
                      value={secForm.src_bytes}
                      onChange={(e) => setSecForm({ ...secForm, src_bytes: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Destination Bytes</label>
                    <input
                      type="number"
                      min="0"
                      value={secForm.dst_bytes}
                      onChange={(e) => setSecForm({ ...secForm, dst_bytes: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                {secError && (
                  <div className="p-2.5 rounded bg-red-500/10 border border-red-500/30 text-xs text-red-300 flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" />
                    <span>{secError}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={secLoading}
                  className="w-full py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition cursor-pointer flex items-center justify-center space-x-2 shadow-lg shadow-emerald-950/40"
                >
                  {secLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Classifying Network Flow...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 fill-white" />
                      <span>Execute Live Classification</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Result Column */}
          <div className="lg:col-span-6 space-y-4">
            {secResult ? (
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Classification Verdict</span>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${getRiskBadge(secResult.risk_level)}`}>
                    RISK LEVEL: {secResult.risk_level}
                  </span>
                </div>

                {/* Verdict Hero Banner */}
                <div
                  className={`p-4 rounded-xl border flex items-center justify-between ${
                    secResult.is_threat
                      ? 'bg-red-500/10 border-red-500/30 text-red-200'
                      : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        secResult.is_threat ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
                      }`}
                    >
                      {secResult.is_threat ? <ShieldAlert className="w-5 h-5" /> : <ShieldCheck className="w-5 h-5" />}
                    </div>
                    <div>
                      <div className="text-base font-bold">
                        {secResult.label} ({secResult.is_threat ? 'Malicious Attack' : 'Benign Traffic'})
                      </div>
                      <div className="text-xs opacity-80">Class ID: {secResult.class_id}</div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xl font-mono font-bold">{(secResult.confidence * 100).toFixed(1)}%</div>
                    <div className="text-[10px] opacity-70">Model Confidence</div>
                  </div>
                </div>

                {/* Probability Distribution */}
                <div>
                  <div className="text-xs font-semibold text-slate-300 mb-2">Class Probability Distribution</div>
                  <div className="space-y-1.5 font-mono text-xs">
                    <div>
                      <div className="flex justify-between text-slate-400 mb-1">
                        <span>Normal (Benign):</span>
                        <span>{(secResult.probabilities.Normal * 100).toFixed(2)}%</span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                        <div
                          className="bg-emerald-400 h-2 transition-all duration-500"
                          style={{ width: `${secResult.probabilities.Normal * 100}%` }}
                        />
                      </div>
                    </div>

                    <div className="pt-1">
                      <div className="flex justify-between text-slate-400 mb-1">
                        <span>Attack (Malicious):</span>
                        <span>{(secResult.probabilities.Attack * 100).toFixed(2)}%</span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                        <div
                          className="bg-red-400 h-2 transition-all duration-500"
                          style={{ width: `${secResult.probabilities.Attack * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recommended Operational Action */}
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <div className="text-xs font-semibold text-slate-300 mb-1 flex items-center space-x-1.5">
                    <Activity className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Operational Mitigation Recommendation</span>
                  </div>
                  <p className="text-xs text-slate-400 m-0 leading-relaxed">{secResult.recommended_action}</p>
                </div>

                {/* Feature Contribution Breakdown */}
                <div>
                  <div className="text-xs font-semibold text-slate-300 mb-2">
                    Key Features Evaluated (Random Forest Weights)
                  </div>
                  <div className="space-y-1.5 text-xs">
                    {secResult.feature_contributions.slice(0, 4).map((fc, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-2 rounded bg-slate-950/60 border border-slate-800/60"
                      >
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-cyan-300 font-medium">{fc.feature}</span>
                          <span className="text-[10px] text-slate-500">= {String(fc.value)}</span>
                        </div>
                        <div className="text-[11px] font-mono text-slate-400">
                          Weight: {(fc.importance_weight * 100).toFixed(1)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full min-h-[360px] p-8 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-center text-center text-slate-400 space-y-3">
                <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-emerald-400">
                  <ShieldAlert className="w-6 h-6" />
                </div>
                <div className="font-semibold text-white">Awaiting Network Inference Request</div>
                <p className="text-xs text-slate-400 max-w-sm m-0">
                  Select a pre-configured telemetry preset or adjust flow metrics on the left, then click{' '}
                  <strong className="text-emerald-400">Execute Live Classification</strong> to run the genuine 200-tree model.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SECTION 2: WORKLOAD ALLOCATION & SIMULATION */}
      {activeSection === 'workload' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Input Form */}
            <div className="lg:col-span-6 space-y-4">
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2 m-0">
                    <Cpu className="w-4 h-4 text-blue-400" />
                    Machine Metrics Input (Alibaba PAI Schema)
                  </h3>
                  <span className="text-[10px] text-blue-400 font-mono">7 Numeric Features</span>
                </div>

                <form onSubmit={handleWorkloadSubmit} className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-300 mb-1">Current Machine CPU (%)</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="100"
                        value={wlForm.machine_cpu}
                        onChange={(e) => setWlForm({ ...wlForm, machine_cpu: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-300 mb-1">Machine GPU (%)</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="100"
                        value={wlForm.machine_gpu}
                        onChange={(e) => setWlForm({ ...wlForm, machine_gpu: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-300 mb-1">User Space CPU (%)</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="100"
                        value={wlForm.machine_cpu_usr}
                        onChange={(e) => setWlForm({ ...wlForm, machine_cpu_usr: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-300 mb-1">Kernel Space CPU (%)</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="100"
                        value={wlForm.machine_cpu_kernel}
                        onChange={(e) => setWlForm({ ...wlForm, machine_cpu_kernel: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-300 mb-1">IO Wait (%)</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="100"
                        value={wlForm.machine_cpu_iowait}
                        onChange={(e) => setWlForm({ ...wlForm, machine_cpu_iowait: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-300 mb-1">1-Min Load</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        value={wlForm.machine_load_1}
                        onChange={(e) => setWlForm({ ...wlForm, machine_load_1: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] font-medium text-slate-300 mb-1">Active Workers</label>
                      <input
                        type="number"
                        min="1"
                        value={wlForm.machine_num_worker}
                        onChange={(e) => setWlForm({ ...wlForm, machine_num_worker: parseFloat(e.target.value) || 1 })}
                        className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={wlLoading}
                    className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition cursor-pointer flex items-center justify-center space-x-2"
                  >
                    {wlLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Querying Inference Engine...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 fill-white" />
                        <span>Submit Workload Prediction Request</span>
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>

            {/* Right: Workload Prediction Status & Baseline */}
            <div className="lg:col-span-6 space-y-4">
              {wlResult ? (
                <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Prediction Engine Status</span>
                    <span className="text-xs px-2.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 font-medium">
                      Status: {wlResult.status.toUpperCase()}
                    </span>
                  </div>

                  {/* Honest Status Banner */}
                  <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 space-y-2">
                    <div className="flex items-center space-x-2 font-bold text-xs">
                      <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                      <span>{wlResult.message}</span>
                    </div>
                    {wlResult.explanation && (
                      <p className="text-[11px] text-amber-300/80 m-0 leading-relaxed">{wlResult.explanation}</p>
                    )}
                  </div>

                  {/* Mathematical Comparison */}
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                      <div className="text-slate-400 mb-1">Persistence Baseline ŷ(t+1)</div>
                      <div className="text-lg font-mono font-bold text-blue-400">{wlResult.baseline_prediction}%</div>
                      <div className="text-[10px] text-slate-500">Equals latest observation y(t)</div>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                      <div className="text-slate-400 mb-1">Recommended Safety Headroom</div>
                      <div className="text-lg font-mono font-bold text-emerald-400">
                        {wlResult.suggested_headroom_pct}%
                      </div>
                      <div className="text-[10px] text-slate-500">Margin below 85% safe ceiling</div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-center text-center text-slate-400 space-y-3 h-full min-h-[240px]">
                  <Cpu className="w-8 h-8 text-blue-400 opacity-60" />
                  <div className="text-xs font-medium">Workload Predictor Ready</div>
                  <p className="text-[11px] text-slate-500 max-w-sm m-0">
                    Click Submit above to query the workload inference pipeline. Validates the input schema and reports model availability status honestly.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Cluster Placement Recommender (Active via 1,897 Alibaba Specs) */}
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2 m-0">
                  <Server className="w-4 h-4 text-cyan-400" />
                  Cluster Resource Allocation Recommender
                </h3>
                <p className="text-xs text-slate-400 mt-1 m-0">
                  Computes node placement recommendations across authentic Alibaba PAI server specifications (1,897 physical nodes).
                </p>
              </div>

              <button
                type="button"
                onClick={handleRecommendPlacement}
                disabled={placementLoading}
                className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition cursor-pointer flex items-center space-x-2 shrink-0"
              >
                {placementLoading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Evaluating Nodes...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Calculate Placement</span>
                  </>
                )}
              </button>
            </div>

            {/* Demand Sliders */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Demanded Cores:</span>
                  <span className="font-mono text-cyan-400 font-bold">{demandCores} Cores</span>
                </div>
                <input
                  type="range"
                  min="32"
                  max="512"
                  step="32"
                  value={demandCores}
                  onChange={(e) => setDemandCores(parseInt(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Demanded Memory:</span>
                  <span className="font-mono text-cyan-400 font-bold">{demandMem} GB</span>
                </div>
                <input
                  type="range"
                  min="128"
                  max="1024"
                  step="64"
                  value={demandMem}
                  onChange={(e) => setDemandMem(parseInt(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">Demanded GPUs:</span>
                  <span className="font-mono text-cyan-400 font-bold">{demandGpus} GPUs</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="8"
                  step="1"
                  value={demandGpus}
                  onChange={(e) => setDemandGpus(parseInt(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>
            </div>

            {/* Recommendation Results */}
            {placementResult && (
              <div className="pt-3 space-y-3">
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-slate-300 font-medium">{placementResult.recommendation_summary}</span>
                  </div>
                  <div className="text-slate-400 font-mono">
                    Avg Cluster Load: <strong className="text-white">{placementResult.average_utilization_pct}%</strong>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 font-mono">
                        <th className="py-2 px-3">Node ID</th>
                        <th className="py-2 px-3">GPU Type</th>
                        <th className="py-2 px-3">Total Cores</th>
                        <th className="py-2 px-3">Allocated Cores</th>
                        <th className="py-2 px-3">Post-Allocation Load</th>
                        <th className="py-2 px-3">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono">
                      {placementResult.allocations.map((node, i) => (
                        <tr key={i} className="hover:bg-slate-800/40">
                          <td className="py-2 px-3 text-cyan-400">{node.machine_id}</td>
                          <td className="py-2 px-3 text-slate-300">{node.gpu_type}</td>
                          <td className="py-2 px-3 text-slate-300">{node.total_cpu}</td>
                          <td className="py-2 px-3 text-emerald-400 font-bold">+{node.allocated_cpu}</td>
                          <td className="py-2 px-3">
                            <span className={node.utilization_pct_after > 80 ? 'text-amber-400' : 'text-slate-300'}>
                              {node.utilization_pct_after}%
                            </span>
                          </td>
                          <td className="py-2 px-3">
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                                node.status === 'Active'
                                  ? 'bg-emerald-500/20 text-emerald-400'
                                  : 'bg-slate-800 text-slate-400'
                              }`}
                            >
                              {node.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SECTION 3: THERMAL MANAGEMENT */}
      {activeSection === 'thermal' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-6 space-y-4">
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2 m-0">
                  <Flame className="w-4 h-4 text-amber-400" />
                  Thermal Telemetry & Threshold Evaluation
                </h3>
                <span className="text-[10px] text-amber-400 font-mono">Marconi A2 Architecture</span>
              </div>

              <form onSubmit={handleThermalSubmit} className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Inlet Air Temp (°C)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thForm.mean_inlet_temp}
                      onChange={(e) => setThForm({ ...thForm, mean_inlet_temp: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Outlet Air Temp (°C)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thForm.mean_outlet_temp}
                      onChange={(e) => setThForm({ ...thForm, mean_outlet_temp: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Rack Power (kW)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thForm.mean_power_consumption}
                      onChange={(e) => setThForm({ ...thForm, mean_power_consumption: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-300 mb-1">Temperature Delta (°C)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={thForm.mean_temperature_difference || 0}
                      onChange={(e) =>
                        setThForm({ ...thForm, mean_temperature_difference: parseFloat(e.target.value) || 0 })
                      }
                      className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={thLoading}
                  className="w-full py-2.5 px-4 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition cursor-pointer flex items-center justify-center space-x-2"
                >
                  {thLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Evaluating Risk Thresholds...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 fill-white" />
                      <span>Evaluate Thermal Thresholds</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          <div className="lg:col-span-6 space-y-4">
            {thResult ? (
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Thermal Risk Assessment</span>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${getRiskBadge(thResult.risk_level)}`}>
                    RISK: {thResult.risk_level}
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="text-xs font-bold text-white flex items-center space-x-2">
                    <Flame className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>Threshold Diagnostic</span>
                  </div>
                  <p className="text-xs text-slate-300 m-0 leading-relaxed">{thResult.threshold_assessment}</p>
                </div>

                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 space-y-1.5">
                  <div className="text-xs font-bold flex items-center space-x-1.5">
                    <Activity className="w-4 h-4 text-amber-400" />
                    <span>Cooling & Airflow Recommendation</span>
                  </div>
                  <p className="text-xs text-amber-300/80 m-0 leading-relaxed">{thResult.recommended_mitigation}</p>
                </div>

                <div className="text-[11px] text-slate-500 border-t border-slate-800/80 pt-3">
                  <strong>Notice:</strong> {thResult.message}
                </div>
              </div>
            ) : (
              <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center justify-center text-center text-slate-400 space-y-3 h-full min-h-[240px]">
                <Flame className="w-8 h-8 text-amber-400 opacity-60" />
                <div className="text-xs font-medium">Thermal Threshold Evaluator Ready</div>
                <p className="text-[11px] text-slate-500 max-w-sm m-0">
                  Input temperature metrics to evaluate against documented Marconi A2 statistical safety thresholds.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SECTION 4: BENCHMARKS & VERIFIED METRICS */}
      {activeSection === 'benchmarks' && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-5">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2 m-0">
              <BarChart2 className="w-4 h-4 text-purple-400" />
              Verified Multi-Domain Benchmark Summary
            </h3>
            <p className="text-xs text-slate-400 mt-1 m-0">
              Rigorous test-set evaluations and holdout comparison metrics across the entire framework.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Security Holdout Accuracy</span>
                <span className="text-emerald-400 font-bold">88.36%</span>
              </div>
              <div className="text-xl font-bold font-mono text-white">0.8836</div>
              <div className="text-[11px] text-slate-500">Evaluated on 82,332 UNSW-NB15 flows</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Unseen Feature Generalization</span>
                <span className="text-cyan-400 font-bold">82.49%</span>
              </div>
              <div className="text-xl font-bold font-mono text-white">0.8249</div>
              <div className="text-[11px] text-slate-500">Evaluated on 47,089 zero-overlap flows</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Security ROC-AUC Score</span>
                <span className="text-purple-400 font-bold">0.9721</span>
              </div>
              <div className="text-xl font-bold font-mono text-white">0.9721</div>
              <div className="text-[11px] text-slate-500">Demonstrates high class discrimination</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
