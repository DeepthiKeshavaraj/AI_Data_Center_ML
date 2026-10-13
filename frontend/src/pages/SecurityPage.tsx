import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Play,
  RotateCcw,
  Sparkles,
  BarChart2,
  Sliders,
  CheckCircle2,
  Info,
} from 'lucide-react';
import {
  SecurityMetadataResponse,
  SecurityPredictRequest,
  SecurityPredictResponse,
} from '../types';
import { predictSecurity } from '../api';

interface SecurityPageProps {
  metadata: SecurityMetadataResponse | null;
}

const DEFAULT_FORM: SecurityPredictRequest = {
  protocol: 'tcp',
  flow_duration: 0.125,
  src_packets: 10,
  dst_packets: 8,
  src_bytes: 540,
  dst_bytes: 320,
  connection_state: 'fin',
  service: 'http',
};

export const SecurityPage: React.FC<SecurityPageProps> = ({ metadata }) => {
  const [formData, setFormData] = useState<SecurityPredictRequest>(DEFAULT_FORM);
  const [result, setResult] = useState<SecurityPredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await predictSecurity(formData);
      setResult(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to execute inference.');
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (presetValues: SecurityPredictRequest) => {
    setFormData(presetValues);
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-5 rounded-xl bg-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-xl font-bold text-white m-0">Network Threat Intelligence</h2>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Live Model Active
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 m-0">
            Real-time inference using trained Random Forest (200 estimators, balanced weights) on UNSW-NB15 standardized telemetry.
          </p>
        </div>

        {/* 1-Click Presets */}
        {metadata?.sample_presets && (
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 flex items-center gap-1 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Presets:
            </span>
            {metadata.sample_presets.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => applyPreset(preset.values)}
                className="px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 hover:border-slate-600 transition cursor-pointer"
                title={preset.description}
              >
                {preset.expected_label === 'Attack' ? '🚨 ' : '🛡️ '}
                {preset.name.split(' ')[0]}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Prediction Form (7 cols) */}
        <div className="lg:col-span-7 rounded-xl border border-slate-800 bg-slate-900/80 p-5">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 m-0">
              <Sliders className="w-4 h-4 text-cyan-400" />
              Network Flow Telemetry Parameters
            </h3>
            <button
              type="button"
              onClick={() => {
                setFormData(DEFAULT_FORM);
                setResult(null);
                setError(null);
              }}
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1 cursor-pointer"
            >
              <RotateCcw className="w-3 h-3" /> Reset
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Protocol */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Protocol (tcp, udp, ospf, arp)
                </label>
                <input
                  type="text"
                  value={formData.protocol}
                  onChange={(e) => setFormData({ ...formData, protocol: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
                  required
                />
              </div>

              {/* Flow Duration */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Flow Duration (seconds)
                </label>
                <input
                  type="number"
                  step="any"
                  min="0"
                  value={formData.flow_duration}
                  onChange={(e) => setFormData({ ...formData, flow_duration: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
                  required
                />
              </div>

              {/* Source Packets */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Source Packets (count)
                </label>
                <input
                  type="number"
                  step="1"
                  min="0"
                  value={formData.src_packets}
                  onChange={(e) => setFormData({ ...formData, src_packets: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
                  required
                />
              </div>

              {/* Destination Packets */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Destination Packets (count)
                </label>
                <input
                  type="number"
                  step="1"
                  min="0"
                  value={formData.dst_packets}
                  onChange={(e) => setFormData({ ...formData, dst_packets: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
                  required
                />
              </div>

              {/* Source Bytes */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Source Bytes (bytes)
                </label>
                <input
                  type="number"
                  step="1"
                  min="0"
                  value={formData.src_bytes}
                  onChange={(e) => setFormData({ ...formData, src_bytes: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
                  required
                />
              </div>

              {/* Destination Bytes */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Destination Bytes (bytes)
                </label>
                <input
                  type="number"
                  step="1"
                  min="0"
                  value={formData.dst_bytes}
                  onChange={(e) => setFormData({ ...formData, dst_bytes: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
                  required
                />
              </div>

              {/* Connection State */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Connection State (fin, con, int, req)
                </label>
                <input
                  type="text"
                  value={formData.connection_state}
                  onChange={(e) => setFormData({ ...formData, connection_state: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
                  required
                />
              </div>

              {/* Service */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Service (-, http, dns, ftp, smtp)
                </label>
                <input
                  type="text"
                  value={formData.service}
                  onChange={(e) => setFormData({ ...formData, service: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-cyan-500 font-mono"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 flex items-center justify-center space-x-2 py-2.5 px-4 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm transition disabled:opacity-50 cursor-pointer shadow-lg shadow-cyan-900/30"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{loading ? 'Evaluating Model Prediction...' : 'Execute ML Model Prediction'}</span>
            </button>
          </form>

          {error && (
            <div className="mt-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Prediction Results & Explanation (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">
            <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2 m-0">
              <ShieldAlert className="w-4 h-4 text-cyan-400" />
              Model Inference Output
            </h3>

            {result ? (
              <div className="space-y-4">
                {/* Result Banner */}
                <div
                  className={`p-4 rounded-xl border flex items-center justify-between ${
                    result.label === 'Attack'
                      ? 'bg-rose-500/15 border-rose-500/40 text-rose-300'
                      : 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    {result.label === 'Attack' ? (
                      <ShieldAlert className="w-8 h-8 text-rose-400" />
                    ) : (
                      <ShieldCheck className="w-8 h-8 text-emerald-400" />
                    )}
                    <div>
                      <div className="text-xs uppercase tracking-wider font-semibold opacity-80">
                        Classification
                      </div>
                      <div className="text-xl font-bold">{result.label.toUpperCase()}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs opacity-80">Confidence</div>
                    <div className="text-xl font-bold">
                      {(result.confidence_score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                {/* Probability Bars */}
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between text-slate-300">
                    <span>Attack Probability:</span>
                    <span className="font-semibold text-rose-400">
                      {(result.attack_probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                    <div
                      className="bg-rose-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${result.attack_probability * 100}%` }}
                    ></div>
                  </div>

                  <div className="flex justify-between text-slate-300 pt-1">
                    <span>Normal Probability:</span>
                    <span className="font-semibold text-emerald-400">
                      {(result.normal_probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                    <div
                      className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${result.normal_probability * 100}%` }}
                    ></div>
                  </div>
                </div>

                {/* Interpretation */}
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 leading-relaxed">
                  <span className="font-semibold text-cyan-400 block mb-1">Model Rationale:</span>
                  {result.interpretation}
                </div>

                <div className="text-[11px] text-slate-500 text-center">
                  Model: {result.model_used}
                </div>
              </div>
            ) : (
              <div className="py-12 px-4 text-center text-slate-500 text-xs">
                <ShieldAlert className="w-10 h-10 mx-auto text-slate-700 mb-3" />
                <p>Fill the network telemetry form or click a preset above, then execute prediction.</p>
              </div>
            )}
          </div>

          {/* Unseen Feature Combinations Card */}
          <div className="rounded-xl border border-cyan-500/20 bg-slate-900/60 p-4">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-cyan-400" />
              Unseen Feature Generalization
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed mb-3">
              Holdout evaluation on <strong>47,089</strong> test records having zero feature overlap with training data:
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs mb-3">
              <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                <div className="text-slate-400">Unseen Accuracy</div>
                <div className="text-base font-bold text-cyan-400">82.49%</div>
              </div>
              <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                <div className="text-slate-400">Unseen ROC-AUC</div>
                <div className="text-base font-bold text-cyan-400">0.9384</div>
              </div>
            </div>
            <p className="text-[11px] text-slate-500 leading-normal m-0">
              <strong>Evaluation Scope:</strong> Measures classifier resilience when encountering novel feature combinations within the UNSW-NB15 holdout set. Does not claim universal zero-day immunity.
            </p>
          </div>
        </div>
      </div>

      {/* Feature Importance & Confusion Matrix Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Feature Importance Chart */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2 m-0">
            <BarChart2 className="w-4 h-4 text-cyan-400" />
            Verified Feature Importances (Impurity-Based)
          </h3>
          <div className="space-y-2 pt-2">
            {metadata?.feature_importances && metadata.feature_importances.length > 0 ? (
              metadata.feature_importances.map((item, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs text-slate-300">
                    <span className="font-mono">{item.original_feature}</span>
                    <span className="text-cyan-400 font-semibold">
                      {(item.importance * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-1.5 border border-slate-800 overflow-hidden">
                    <div
                      className="bg-cyan-500 h-1.5 rounded-full"
                      style={{ width: `${item.importance * 100 * 3.5}%` }}
                    ></div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-500">Loading importances...</div>
            )}
          </div>
        </div>

        {/* Confusion Matrix */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2 m-0">
            <Info className="w-4 h-4 text-cyan-400" />
            Holdout Test Confusion Matrix (82,332 records)
          </h3>
          <div className="overflow-x-auto pt-2">
            <table className="w-full text-xs text-center border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="p-2 text-left">Actual \ Predicted</th>
                  <th className="p-2 text-emerald-400">Predicted Normal</th>
                  <th className="p-2 text-rose-400">Predicted Attack</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                <tr>
                  <td className="p-2.5 text-left text-slate-300 font-sans font-medium">Actual Normal</td>
                  <td className="p-2.5 bg-emerald-500/10 text-emerald-400 font-bold">29,542 (79.8%)</td>
                  <td className="p-2.5 bg-rose-500/10 text-rose-400 font-bold">7,458 (20.2%)</td>
                </tr>
                <tr>
                  <td className="p-2.5 text-left text-slate-300 font-sans font-medium">Actual Attack</td>
                  <td className="p-2.5 bg-rose-500/10 text-rose-400 font-bold">2,129 (4.7%)</td>
                  <td className="p-2.5 bg-emerald-500/10 text-emerald-400 font-bold">43,203 (95.3%)</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="text-[11px] text-slate-400 mt-4 leading-relaxed m-0">
            The model demonstrates a high <strong>95.3% recall on attack flows</strong>, ensuring cyber threats are caught with minimal false negatives.
          </p>
        </div>
      </div>
    </div>
  );
};
