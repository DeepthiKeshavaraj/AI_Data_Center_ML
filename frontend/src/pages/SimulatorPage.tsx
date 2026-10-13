import React, { useState, useEffect } from 'react';
import {
  Shield,
  Server,
  Flame,
  Cpu,
  RotateCcw,
  Play,
  Sliders,
  BarChart2,
  Clock,
  Lightbulb,
  Check,
  Info,
  ArrowRight,
  Loader2,
} from 'lucide-react';
import {
  SimulationRunRequest,
  SimulationRunResponse,
  SecurityPredictRequest,
} from '../types';
import { runSimulation } from '../api';

const FLOW_OPTIONS: Record<string, { label: string; values: SecurityPredictRequest | null }> = {
  mixed: {
    label: 'Mixed (HTTP + DNS + Other)',
    values: {
      protocol: 'tcp',
      flow_duration: 0.125,
      src_packets: 10.0,
      dst_packets: 8.0,
      src_bytes: 540.0,
      dst_bytes: 320.0,
      connection_state: 'fin',
      service: 'http',
    },
  },
  ospf_attack: {
    label: 'OSPF Reconnaissance (Attack Flow)',
    values: {
      protocol: 'ospf',
      flow_duration: 0.921987,
      src_packets: 20.0,
      dst_packets: 0.0,
      src_bytes: 1280.0,
      dst_bytes: 0.0,
      connection_state: 'int',
      service: '-',
    },
  },
  http_normal: {
    label: 'Standard Web Traffic (Normal Flow)',
    values: {
      protocol: 'tcp',
      flow_duration: 0.125,
      src_packets: 10.0,
      dst_packets: 8.0,
      src_bytes: 540.0,
      dst_bytes: 320.0,
      connection_state: 'fin',
      service: 'http',
    },
  },
  dns_normal: {
    label: 'DNS Resolution Query (Normal Flow)',
    values: {
      protocol: 'udp',
      flow_duration: 0.00045,
      src_packets: 2.0,
      dst_packets: 2.0,
      src_bytes: 146.0,
      dst_bytes: 178.0,
      connection_state: 'con',
      service: 'dns',
    },
  },
};

export const SimulatorPage: React.FC = () => {
  // Preset selection: default to 'workload_surge' matching reference image
  const [selectedPreset, setSelectedPreset] = useState<'security_incident' | 'workload_surge' | 'thermal_emergency'>('workload_surge');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form Controls State
  const [baseCpuDemand, setBaseCpuDemand] = useState<number>(320);
  const [suspiciousTrafficIntensity, setSuspiciousTrafficIntensity] = useState<number>(0.30);
  const [ambientTemp, setAmbientTemp] = useState<number>(24.0);
  const [selectedFlowType, setSelectedFlowType] = useState<string>('mixed');

  // Simulation Results State
  const [simResult, setSimResult] = useState<SimulationRunResponse | null>(null);

  // Handle Preset Switching
  const handleSelectPreset = (preset: 'security_incident' | 'workload_surge' | 'thermal_emergency') => {
    setSelectedPreset(preset);
    if (preset === 'security_incident') {
      setBaseCpuDemand(450);
      setSuspiciousTrafficIntensity(0.85);
      setAmbientTemp(24.0);
      setSelectedFlowType('ospf_attack');
    } else if (preset === 'workload_surge') {
      setBaseCpuDemand(320);
      setSuspiciousTrafficIntensity(0.30);
      setAmbientTemp(24.0);
      setSelectedFlowType('mixed');
    } else if (preset === 'thermal_emergency') {
      setBaseCpuDemand(750);
      setSuspiciousTrafficIntensity(0.15);
      setAmbientTemp(36.0);
      setSelectedFlowType('dns_normal');
    }
  };

  // Run Simulation API call
  const executeSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const flowData = FLOW_OPTIONS[selectedFlowType]?.values ?? null;
      const payload: SimulationRunRequest = {
        preset: selectedPreset,
        base_cpu_demand: Number(baseCpuDemand),
        cluster_capacity: 1000.0,
        suspicious_traffic_intensity: Number(suspiciousTrafficIntensity),
        ambient_inlet_temp: Number(ambientTemp),
        throttling_threshold: 60.0,
        inspection_overhead_factor: 0.25,
        flow_sample: flowData,
      };

      const result = await runSimulation(payload);
      setSimResult(result);
    } catch (err: any) {
      setError(err?.message || 'Simulation execution failed.');
    } finally {
      setLoading(false);
    }
  };

  // Run on mount
  useEffect(() => {
    executeSimulation();
  }, []);

  // Format Helper
  const fmtDelta = (init: number, final: number) => {
    if (!init || init === 0) return '+0%';
    const pct = Math.round(((final - init) / init) * 100);
    return pct >= 0 ? `+${pct}%` : `${pct}%`;
  };

  // Metrics extraction with fallbacks to defaults in screenshot
  const initialDemand = simResult?.initial_state?.base_cpu_demand_cores ?? baseCpuDemand;
  const finalDemand = simResult?.final_state?.total_cpu_demand_cores ?? 964;
  const demandDelta = simResult ? fmtDelta(initialDemand, finalDemand) : '+201%';

  const initialCap = simResult?.initial_state?.cluster_capacity_cores ?? 1000;
  const finalCap = simResult?.final_state?.cluster_capacity_cores ?? 520;
  const capDelta = simResult ? fmtDelta(initialCap, finalCap) : '-48%';

  const initialTemp = simResult?.initial_state?.outlet_temp_c ?? 24.0;
  const finalTemp = simResult?.final_state?.outlet_temp_c ?? 62.0;
  const tempDelta = simResult ? fmtDelta(initialTemp, finalTemp) : '+158%';

  const cpuUtil = simResult?.final_state?.cpu_utilization_pct ?? 78;
  const suspPct = Math.round((simResult ? (simResult.security_result ? simResult.security_result.attack_probability : suspiciousTrafficIntensity) : suspiciousTrafficIntensity) * 100);

  // Dynamic recommendations checklist
  const recAction = simResult?.recommendations?.[0]?.action ?? 'Scale Out and Improve Cooling';
  const recItems = [
    'Redistribute workload to less utilized nodes',
    'Increase cooling airflow for affected racks',
    'Monitor for sustained high temperatures',
    'Keep network traffic under observation',
  ];

  return (
    <div className="space-y-5 animate-fade-in pb-10 text-slate-100 font-sans">
      {/* 1. Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center space-x-2.5">
            <div className="w-7 h-7 rounded-lg bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              {/* 3-node icon */}
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="5" r="2.5" />
                <circle cx="5" cy="18" r="2.5" />
                <circle cx="19" cy="18" r="2.5" />
                <path d="M12 7.5L6.5 16M12 7.5L17.5 16M7.5 18h9" />
              </svg>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white m-0">
              Cross-Domain Impact Simulator
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1 m-0">
            See how changes propagate across security, workload and thermal systems in an AI data center.
          </p>
        </div>

        <button
          onClick={() => handleSelectPreset('workload_surge')}
          className="self-start sm:self-auto px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/80 hover:bg-slate-800 text-xs text-slate-300 font-medium transition flex items-center space-x-1.5 cursor-pointer shadow-sm"
        >
          <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
          <span>Reset to Defaults</span>
        </button>
      </div>

      {/* 2. Main Two-Column Section: (Diagram + Scenario Bar) on Left, Controls on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column: Preset Bar + 3-Node Connected Diagram (8 of 12 cols on desktop) */}
        <div className="lg:col-span-8 xl:col-span-8 space-y-4">
          {/* Compact Scenario Selector Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Scenario 1: Security Incident */}
            <button
              onClick={() => handleSelectPreset('security_incident')}
              className={`p-3 rounded-xl border text-left transition cursor-pointer flex items-center space-x-3 ${
                selectedPreset === 'security_incident'
                  ? 'bg-[#18112e] border-purple-500/60 shadow-[0_0_15px_rgba(168,85,247,0.2)] ring-1 ring-purple-500/50'
                  : 'bg-[#0f172a]/70 border-slate-800/80 hover:border-slate-700 text-slate-300'
              }`}
            >
              <div className="w-8 h-8 rounded-lg bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0">
                <Shield className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <div className="font-semibold text-white text-xs truncate">Security Incident</div>
                <div className="text-[10px] text-slate-400 truncate">DPI overhead, suspicious traffic</div>
              </div>
            </button>

            {/* Scenario 2: Workload Surge */}
            <button
              onClick={() => handleSelectPreset('workload_surge')}
              className={`p-3 rounded-xl border text-left transition cursor-pointer flex items-center justify-between relative ${
                selectedPreset === 'workload_surge'
                  ? 'bg-[#0e1e36] border-cyan-500/60 shadow-[0_0_15px_rgba(6,182,212,0.2)] ring-1 ring-cyan-500/50'
                  : 'bg-[#0f172a]/70 border-slate-800/80 hover:border-slate-700 text-slate-300'
              }`}
            >
              <div className="flex items-center space-x-3 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
                  <Server className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <div className="font-semibold text-white text-xs truncate">Workload Surge</div>
                  <div className="text-[10px] text-slate-400 truncate">High CPU demand, heat rise</div>
                </div>
              </div>
              {selectedPreset === 'workload_surge' && (
                <div className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_6px_#22d3ee] shrink-0" />
              )}
            </button>

            {/* Scenario 3: Thermal Emergency */}
            <button
              onClick={() => handleSelectPreset('thermal_emergency')}
              className={`p-3 rounded-xl border text-left transition cursor-pointer flex items-center space-x-3 ${
                selectedPreset === 'thermal_emergency'
                  ? 'bg-[#29180c] border-amber-500/60 shadow-[0_0_15px_rgba(245,158,11,0.2)] ring-1 ring-amber-500/50'
                  : 'bg-[#0f172a]/70 border-slate-800/80 hover:border-slate-700 text-slate-300'
              }`}
            >
              <div className="w-8 h-8 rounded-lg bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
                <Flame className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <div className="font-semibold text-white text-xs truncate">Thermal Emergency</div>
                <div className="text-[10px] text-slate-400 truncate">Cooling constraints, throttling</div>
              </div>
            </button>
          </div>

          {/* Connected 3-Domain Diagram Card */}
          <div className="relative rounded-2xl border border-slate-800/90 bg-[#0B1120] p-6 overflow-hidden min-h-[340px] flex items-center justify-center shadow-inner">
            {/* Background subtle radial gradient */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-900/40 via-[#0B1120] to-[#080D1A] pointer-events-none" />

            {/* SVG Connecting Flow Lines & Curved Directional Arrows */}
            <svg
              className="absolute inset-0 w-full h-full pointer-events-none z-10"
              viewBox="0 0 760 320"
              preserveAspectRatio="xMidYMid meet"
            >
              <defs>
                {/* Purple Arrowhead */}
                <marker id="arrow-purple" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
                  <polygon points="0 1, 6 3.5, 0 6" fill="#a855f7" />
                </marker>
                {/* Cyan Arrowhead */}
                <marker id="arrow-cyan" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
                  <polygon points="0 1, 6 3.5, 0 6" fill="#06b6d4" />
                </marker>
                {/* Amber Arrowhead */}
                <marker id="arrow-amber" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
                  <polygon points="0 1, 6 3.5, 0 6" fill="#f59e0b" />
                </marker>
                {/* Emerald/Cyan Arrowhead */}
                <marker id="arrow-emerald" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
                  <polygon points="0 1, 6 3.5, 0 6" fill="#10b981" />
                </marker>
              </defs>

              {/* 1. TOP ARROW: Security -> Workload (Purple) */}
              <path
                d="M 190 92 C 245 42, 305 42, 335 90"
                fill="none"
                stroke="#a855f7"
                strokeWidth="2"
                strokeLinecap="round"
                markerEnd="url(#arrow-purple)"
                className={loading ? 'flow-active' : ''}
              />
              <text x="262" y="32" textAnchor="middle" fill="#c084fc" fontSize="10.5" fontWeight="600">
                Suspicious traffic
              </text>
              <text x="262" y="45" textAnchor="middle" fill="#94a3b8" fontSize="9.5">
                Inspection overhead
              </text>

              {/* 2. TOP ARROW: Workload -> Thermal (Cyan) */}
              <path
                d="M 425 90 C 455 42, 515 42, 570 92"
                fill="none"
                stroke="#06b6d4"
                strokeWidth="2"
                strokeLinecap="round"
                markerEnd="url(#arrow-cyan)"
                className={loading ? 'flow-active' : ''}
              />
              <text x="498" y="32" textAnchor="middle" fill="#22d3ee" fontSize="10.5" fontWeight="600">
                Higher CPU & power
              </text>
              <text x="498" y="45" textAnchor="middle" fill="#94a3b8" fontSize="9.5">
                Increased heat generation
              </text>

              {/* 3. BOTTOM ARROW: Thermal -> Workload (Amber, points Left) */}
              <path
                d="M 570 228 C 515 278, 455 278, 425 230"
                fill="none"
                stroke="#f59e0b"
                strokeWidth="2"
                strokeLinecap="round"
                markerEnd="url(#arrow-amber)"
                className={loading ? 'flow-active' : ''}
              />
              <text x="498" y="278" textAnchor="middle" fill="#fbbf24" fontSize="10.5" fontWeight="600">
                Thermal constraints
              </text>
              <text x="498" y="291" textAnchor="middle" fill="#94a3b8" fontSize="9.5">
                Capacity throttling
              </text>

              {/* 4. BOTTOM ARROW: Workload -> Security (Emerald/Teal, points Left) */}
              <path
                d="M 335 230 C 305 278, 245 278, 190 228"
                fill="none"
                stroke="#10b981"
                strokeWidth="2"
                strokeLinecap="round"
                markerEnd="url(#arrow-emerald)"
                className={loading ? 'flow-active' : ''}
              />
              <text x="262" y="278" textAnchor="middle" fill="#34d399" fontSize="10.5" fontWeight="600">
                Mitigation actions
              </text>
              <text x="262" y="291" textAnchor="middle" fill="#94a3b8" fontSize="9.5">
                Adjust workload policies
              </text>
            </svg>

            {/* DOMAIN NODES ROW: 3 Large Circular Cards */}
            <div className="relative z-20 w-full flex flex-col sm:flex-row items-center justify-around gap-6 sm:gap-2">
              {/* NODE 1: SECURITY */}
              <div
                className={`w-44 h-44 rounded-full flex flex-col items-center justify-center p-3 text-center border-2 transition-all relative select-none ${
                  selectedPreset === 'security_incident'
                    ? 'border-purple-400 bg-gradient-to-b from-purple-950/50 via-[#10142A] to-[#0A0D18] shadow-[0_0_30px_rgba(168,85,247,0.35)] ring-2 ring-purple-500/40'
                    : 'border-purple-500/60 bg-gradient-to-b from-purple-950/30 via-[#10142A] to-[#0A0D18] shadow-[0_0_20px_rgba(168,85,247,0.2)]'
                }`}
              >
                <div className="text-purple-400 mb-1">
                  <Shield className="w-5 h-5" />
                </div>
                <h3 className="text-xs font-bold text-white tracking-wider m-0">SECURITY</h3>
                <p className="text-[10px] text-slate-400 m-0 leading-tight">
                  Network Threat<br />Intelligence
                </p>

                <div className="mt-2 mb-1">
                  <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    Normal
                  </span>
                </div>

                <div className="text-xs font-bold text-white font-mono leading-none">
                  {suspPct}%
                </div>
                <div className="text-[9px] text-slate-400">Suspicious Traffic</div>
              </div>

              {/* NODE 2: WORKLOAD */}
              <div
                className={`w-48 h-48 rounded-full flex flex-col items-center justify-center p-3 text-center border-2 transition-all relative select-none ${
                  selectedPreset === 'workload_surge'
                    ? 'border-cyan-400 bg-gradient-to-b from-cyan-950/50 via-[#0A182E] to-[#080F1E] shadow-[0_0_35px_rgba(6,182,212,0.35)] ring-2 ring-cyan-500/40'
                    : 'border-cyan-500/60 bg-gradient-to-b from-cyan-950/30 via-[#0A182E] to-[#080F1E] shadow-[0_0_20px_rgba(6,182,212,0.2)]'
                }`}
              >
                <div className="text-cyan-400 mb-1">
                  <Server className="w-5 h-5" />
                </div>
                <h3 className="text-xs font-bold text-white tracking-wider m-0">WORKLOAD</h3>
                <p className="text-[10px] text-slate-400 m-0 leading-tight">
                  Resource Allocation<br />& Scheduling
                </p>

                <div className="mt-2 mb-1">
                  <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                    High Load
                  </span>
                </div>

                {/* Semicircle Gauge Simulation */}
                <div className="relative flex flex-col items-center mt-0.5">
                  <div className="w-14 h-7 overflow-hidden relative">
                    <div
                      className="w-14 h-14 rounded-full border-4 border-cyan-400 border-b-transparent border-l-transparent transform -rotate-45"
                      style={{ opacity: 0.9 }}
                    />
                  </div>
                  <div className="text-xs font-bold text-white font-mono leading-none -mt-3">
                    {cpuUtil}%
                  </div>
                  <div className="text-[9px] text-slate-400">CPU Utilization</div>
                </div>
              </div>

              {/* NODE 3: THERMAL */}
              <div
                className={`w-44 h-44 rounded-full flex flex-col items-center justify-center p-3 text-center border-2 transition-all relative select-none ${
                  selectedPreset === 'thermal_emergency'
                    ? 'border-amber-400 bg-gradient-to-b from-amber-950/50 via-[#1F140A] to-[#0D0B09] shadow-[0_0_30px_rgba(245,158,11,0.35)] ring-2 ring-amber-500/40'
                    : 'border-amber-500/60 bg-gradient-to-b from-amber-950/30 via-[#1F140A] to-[#0D0B09] shadow-[0_0_20px_rgba(245,158,11,0.2)]'
                }`}
              >
                <div className="text-amber-400 mb-1">
                  <Flame className="w-5 h-5" />
                </div>
                <h3 className="text-xs font-bold text-white tracking-wider m-0">THERMAL</h3>
                <p className="text-[10px] text-slate-400 m-0 leading-tight">
                  Environment & Cooling
                </p>

                {/* Semicircle Gauge Indicator */}
                <div className="relative flex flex-col items-center mt-3">
                  <div className="w-14 h-7 overflow-hidden relative">
                    <div
                      className="w-14 h-14 rounded-full border-4 border-amber-500 border-b-transparent border-l-transparent transform rotate-15"
                      style={{ opacity: 0.95 }}
                    />
                  </div>
                  <div className="text-xs font-bold text-white font-mono leading-none -mt-3">
                    {Math.round(finalTemp)}°C
                  </div>
                  <div className="text-[9px] text-slate-400">Outlet Temperature</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Scenario Controls Panel (4 of 12 cols on desktop) */}
        <div className="lg:col-span-4 xl:col-span-4 rounded-2xl border border-slate-800 bg-[#0F172A]/90 p-5 space-y-4 shadow-sm backdrop-blur">
          <div className="flex items-center space-x-2 text-white font-semibold text-xs tracking-wide pb-2 border-b border-slate-800">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>Scenario Controls</span>
          </div>

          {/* Control 1: Base CPU Demand */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-300 font-medium">Base CPU Demand</span>
              <span className="font-mono text-cyan-400 font-semibold">{baseCpuDemand} cores</span>
            </div>
            <input
              type="range"
              min="100"
              max="1200"
              step="20"
              value={baseCpuDemand}
              onChange={(e) => setBaseCpuDemand(Number(e.target.value))}
              className="w-full accent-cyan-400 bg-slate-800 rounded-lg cursor-pointer h-1.5"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>100</span>
              <span>1,200</span>
            </div>
          </div>

          {/* Control 2: Suspicious Traffic Intensity */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-300 font-medium">Suspicious Traffic Intensity</span>
              <span className="font-mono text-rose-400 font-semibold">{Math.round(suspiciousTrafficIntensity * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={suspiciousTrafficIntensity}
              onChange={(e) => setSuspiciousTrafficIntensity(Number(e.target.value))}
              className="w-full accent-rose-500 bg-slate-800 rounded-lg cursor-pointer h-1.5"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span className="font-mono">0%</span>
              <span className="font-mono">100%</span>
            </div>
            <p className="text-[10px] text-slate-500 m-0 -mt-1">% of incoming network traffic</p>
          </div>

          {/* Control 3: Ambient Temperature */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-300 font-medium">Ambient Temperature</span>
              <span className="font-mono text-amber-400 font-semibold">{ambientTemp.toFixed(1)} °C</span>
            </div>
            <input
              type="range"
              min="18.0"
              max="40.0"
              step="0.5"
              value={ambientTemp}
              onChange={(e) => setAmbientTemp(Number(e.target.value))}
              className="w-full accent-amber-400 bg-slate-800 rounded-lg cursor-pointer h-1.5"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>18°C</span>
              <span>40°C</span>
            </div>
          </div>

          {/* Control 4: Security Traffic Type Dropdown */}
          <div className="space-y-1.5 pt-1">
            <label className="text-xs text-slate-300 font-medium block">Security Traffic Type</label>
            <select
              value={selectedFlowType}
              onChange={(e) => setSelectedFlowType(e.target.value)}
              className="w-full bg-[#0A0F1D] border border-slate-700/80 rounded-lg px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-400 transition"
            >
              {Object.entries(FLOW_OPTIONS).map(([key, opt]) => (
                <option key={key} value={key} className="bg-slate-900 text-slate-200">
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Run Simulation Action Button */}
          <button
            onClick={executeSimulation}
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold text-xs transition flex items-center justify-center space-x-2 cursor-pointer shadow-md shadow-cyan-500/20 disabled:opacity-50 mt-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Simulating...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run Simulation</span>
              </>
            )}
          </button>

          {/* Transparency Footnote */}
          <div className="flex items-start space-x-2 pt-2 text-[11px] text-slate-400 leading-snug">
            <Info className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
            <span>
              Uses ML models and simulation rules to show cross-domain effects. No real systems are modified.
            </span>
          </div>

          {error && (
            <div className="p-2 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* 3. Before vs After Simulation Metrics Section (3 Visual Progress Cards) */}
      <div className="rounded-2xl border border-slate-800 bg-[#0F172A]/80 p-5 space-y-4">
        <div className="flex items-center space-x-2 text-white font-semibold text-xs tracking-wide">
          <BarChart2 className="w-4 h-4 text-cyan-400" />
          <span>Before vs After Simulation</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Metric 1: Total CPU Demand */}
          <div className="p-4 rounded-xl bg-[#090E1A] border border-slate-800/80 space-y-3">
            <div className="flex items-center space-x-2 text-slate-200 font-semibold text-xs">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Total CPU Demand</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Baseline</span>
                <span className="font-mono text-slate-300 font-semibold">{Math.round(initialDemand)} cores</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-slate-500 rounded-full"
                  style={{ width: `${Math.min(100, (initialDemand / 1200) * 100)}%` }}
                />
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-slate-400">Simulated</span>
                <span className="font-mono text-cyan-400 font-semibold">{Math.round(finalDemand)} cores</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-cyan-400 rounded-full"
                  style={{ width: `${Math.min(100, (finalDemand / 1200) * 100)}%` }}
                />
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <span className="text-xs font-mono font-bold text-rose-400">
                ↑ {demandDelta}
              </span>
            </div>
          </div>

          {/* Metric 2: Available Cluster Capacity */}
          <div className="p-4 rounded-xl bg-[#090E1A] border border-slate-800/80 space-y-3">
            <div className="flex items-center space-x-2 text-slate-200 font-semibold text-xs">
              <Server className="w-4 h-4 text-cyan-400" />
              <span>Available Cluster Capacity</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Baseline</span>
                <span className="font-mono text-emerald-400 font-semibold">{Math.round(initialCap).toLocaleString()} cores</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div className="h-full bg-emerald-400 rounded-full w-full" />
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-slate-400">After Scenario</span>
                <span className="font-mono text-amber-400 font-semibold">{Math.round(finalCap)} cores</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-amber-400 rounded-full"
                  style={{ width: `${Math.min(100, (finalCap / initialCap) * 100)}%` }}
                />
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <span className="text-xs font-mono font-bold text-amber-400">
                ↓ {capDelta}
              </span>
            </div>
          </div>

          {/* Metric 3: Outlet Temperature */}
          <div className="p-4 rounded-xl bg-[#090E1A] border border-slate-800/80 space-y-3">
            <div className="flex items-center space-x-2 text-slate-200 font-semibold text-xs">
              <Flame className="w-4 h-4 text-rose-400" />
              <span>Outlet Temperature</span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Baseline</span>
                <span className="font-mono text-slate-300 font-semibold">{initialTemp.toFixed(1)} °C</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-slate-500 rounded-full"
                  style={{ width: `${Math.min(100, (initialTemp / 75) * 100)}%` }}
                />
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-slate-400">Simulated</span>
                <span className="font-mono text-rose-400 font-semibold">{finalTemp.toFixed(1)} °C</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div
                  className="h-full bg-rose-500 rounded-full"
                  style={{ width: `${Math.min(100, (finalTemp / 75) * 100)}%` }}
                />
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <span className="text-xs font-mono font-bold text-rose-400">
                ↑ {tempDelta}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Bottom Grid: Horizontal Timeline (Left) + Operational Recommendation (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
        {/* Horizontal Timeline (8 of 12 cols on desktop) */}
        <div className="lg:col-span-8 xl:col-span-8 rounded-2xl border border-slate-800 bg-[#0F172A]/80 p-5 space-y-4 flex flex-col justify-between">
          <div className="flex items-center space-x-2 text-white font-semibold text-xs tracking-wide">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>Chronological Impact Timeline</span>
          </div>

          {/* Horizontal Steps Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs items-start">
            {/* Step 1: Purple */}
            <div className="p-3 rounded-xl bg-[#090E1A] border border-slate-800/80 space-y-2 h-full flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/40 flex items-center justify-center font-bold text-[10px]">
                    1
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">00:00</span>
                </div>
                <div className="font-semibold text-slate-200 text-xs">Workload Surge Initiated</div>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed m-0">
                  CPU demand increased from {Math.round(initialDemand)} to {Math.round(finalDemand)} cores ({demandDelta}).
                </p>
              </div>
            </div>

            {/* Step 2: Blue */}
            <div className="p-3 rounded-xl bg-[#090E1A] border border-slate-800/80 space-y-2 h-full flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 flex items-center justify-center font-bold text-[10px]">
                    2
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">00:05</span>
                </div>
                <div className="font-semibold text-slate-200 text-xs">Higher Power Consumption</div>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed m-0">
                  Increased server power draw due to higher CPU utilization.
                </p>
              </div>
            </div>

            {/* Step 3: Amber */}
            <div className="p-3 rounded-xl bg-[#090E1A] border border-slate-800/80 space-y-2 h-full flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center justify-center font-bold text-[10px]">
                    3
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">00:10</span>
                </div>
                <div className="font-semibold text-slate-200 text-xs">Thermal Impact</div>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed m-0">
                  Outlet temperature rose to {finalTemp.toFixed(1)} °C ({tempDelta}), approaching safety limits.
                </p>
              </div>
            </div>

            {/* Step 4: Emerald */}
            <div className="p-3 rounded-xl bg-[#090E1A] border border-slate-800/80 space-y-2 h-full flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center font-bold text-[10px]">
                    4
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">00:15</span>
                </div>
                <div className="font-semibold text-slate-200 text-xs">Capacity Throttling</div>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed m-0">
                  Available capacity reduced by {capDelta.replace('-', '')}. Workload backlog increased.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Operational Recommendation (4 of 12 cols on desktop) */}
        <div className="lg:col-span-4 xl:col-span-4 rounded-2xl border border-slate-800 bg-[#0F172A]/80 p-5 space-y-3 flex flex-col justify-between">
          <div className="flex items-center space-x-2 text-white font-semibold text-xs tracking-wide">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            <span>Operational Recommendation</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#081322] border border-emerald-500/30 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white text-xs">{recAction}</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Recommended
              </span>
            </div>

            <div className="space-y-1.5 text-[11px] text-slate-300">
              {recItems.map((item, idx) => (
                <div key={idx} className="flex items-center space-x-2">
                  <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
