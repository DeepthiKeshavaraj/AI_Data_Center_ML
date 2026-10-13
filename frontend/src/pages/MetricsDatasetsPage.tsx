import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Database,
  CheckCircle2,
  Table,
  Eye,
  FileText,
  Layers,
  Shield,
  Cpu,
  Flame,
  X,
  RefreshCw,
  Info,
} from 'lucide-react';
import {
  MetricsResponse,
  DatasetSummary,
  DatasetSampleResponse,
} from '../types';
import { fetchMetrics, fetchDatasets, fetchDatasetSample } from '../api';

export const MetricsDatasetsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [sampleData, setSampleData] = useState<DatasetSampleResponse | null>(null);
  const [loadingSample, setLoadingSample] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [m, d] = await Promise.all([fetchMetrics(), fetchDatasets()]);
      setMetrics(m);
      setDatasets(d);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleInspectDataset = async (id: string) => {
    setSelectedDatasetId(id);
    setLoadingSample(true);
    try {
      const sample = await fetchDatasetSample(id, 8);
      setSampleData(sample);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSample(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white m-0">Model Evaluation & Benchmark Datasets</h2>
          <p className="text-xs text-slate-400 mt-1 m-0">
            Verified performance metrics from offline experiment reports and interactive catalog of standardized datasets.
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 flex items-center gap-1.5 cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh Catalog
        </button>
      </div>

      {/* Verified Performance Metrics Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">
        <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 m-0">
          <BarChart3 className="w-4 h-4 text-cyan-400" />
          Verified Machine Learning Model Performance Summary
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Security Metrics */}
          <div className="p-4 rounded-xl bg-slate-950 border border-emerald-500/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                <Shield className="w-3.5 h-3.5" /> UNSW-NB15 Security Model
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
                Verified Test Set
              </span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Accuracy:</span>
                <span className="font-mono font-bold text-white">88.36%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Balanced Accuracy:</span>
                <span className="font-mono font-bold text-white">87.57%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">ROC-AUC:</span>
                <span className="font-mono font-bold text-emerald-400">0.9721</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Attack Recall:</span>
                <span className="font-mono font-bold text-white">95.3%</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-slate-800/80">
                <span className="text-slate-400">Unseen Feature Acc:</span>
                <span className="font-mono font-bold text-cyan-400">82.49% (47k flows)</span>
              </div>
            </div>
          </div>

          {/* Workload Benchmark Reference */}
          <div className="p-4 rounded-xl bg-slate-950 border border-blue-500/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-blue-400 flex items-center gap-1">
                <Cpu className="w-3.5 h-3.5" /> Workload CPU Regression
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400">
                Benchmark Design
              </span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Target Variable:</span>
                <span className="font-mono font-bold text-white">next_machine_cpu (%)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Evaluation Split:</span>
                <span className="font-mono text-white">Chronological 20% holdout</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Baseline Model:</span>
                <span className="font-mono text-slate-300">Persistence (ŷ_t+1 = y_t)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Documented MAE:</span>
                <span className="font-mono text-cyan-400 font-bold">1.546 %</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Documented RMSE:</span>
                <span className="font-mono text-cyan-400 font-bold">3.153 %</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Documented R²:</span>
                <span className="font-mono text-emerald-400 font-bold">0.971</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-slate-800/80">
                <span className="text-slate-400">Inference Status:</span>
                <span className="font-mono text-amber-400">Metric CSV pending</span>
              </div>
            </div>
          </div>

          {/* Thermal Forecasting Reference */}
          <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-amber-400 flex items-center gap-1">
                <Flame className="w-3.5 h-3.5" /> Marconi A2 Thermal Model
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400">
                Architecture Spec
              </span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Forecast Horizon:</span>
                <span className="font-mono font-bold text-white">30 minutes (3 steps)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Target Variable:</span>
                <span className="font-mono text-white">mean_outlet_temp (°C)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Historical Lags:</span>
                <span className="font-mono text-slate-300">0, 10, 20, 30, 60 mins</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Statistical 95th %ile:</span>
                <span className="font-mono text-purple-400">Peak events modeled</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-slate-800/80">
                <span className="text-slate-400">Dataset Status:</span>
                <span className="font-mono text-amber-400">Raw sensors pending</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Standardized Datasets Catalog */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">
        <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2 m-0">
          <Database className="w-4 h-4 text-cyan-400" />
          Standardized Datasets Catalog
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Genuine datasets available locally in the repository workspace. Click to safely preview sample records:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {datasets.map((d) => (
            <div
              key={d.id}
              className={`p-4 rounded-xl border transition ${
                selectedDatasetId === d.id
                  ? 'border-cyan-500 bg-cyan-950/20'
                  : 'border-slate-800 bg-slate-950 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h4 className="text-sm font-bold text-white m-0">{d.name}</h4>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                      {d.component}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">{d.description}</p>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 mt-3 pt-3 border-t border-slate-800/80 font-mono">
                <div>
                  <span>Rows: </span>
                  <strong className="text-slate-200">{d.total_rows.toLocaleString()}</strong>
                </div>
                <div>
                  <span>Size: </span>
                  <strong className="text-slate-200">{d.size_mb} MB</strong>
                </div>
                <div>
                  <span>Features: </span>
                  <strong className="text-slate-200">{d.features_count}</strong>
                </div>
              </div>

              <button
                type="button"
                onClick={() => handleInspectDataset(d.id)}
                className="mt-3 w-full py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-300 text-xs font-medium border border-slate-700 hover:border-slate-600 flex items-center justify-center gap-1.5 transition cursor-pointer"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>Inspect Sample Records</span>
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Live Sample Viewer Drawer/Modal */}
      {selectedDatasetId && (
        <div className="rounded-xl border border-cyan-500/40 bg-slate-900/90 p-5 shadow-xl">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <Table className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white m-0">
                Sample Records Preview: {sampleData?.name || selectedDatasetId}
              </h3>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400">
                Live Disk Preview
              </span>
            </div>
            <button
              onClick={() => {
                setSelectedDatasetId(null);
                setSampleData(null);
              }}
              className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {loadingSample ? (
            <div className="py-8 text-center text-xs text-slate-400">
              <RefreshCw className="w-5 h-5 animate-spin mx-auto text-cyan-400 mb-2" />
              Reading sample records safely from disk...
            </div>
          ) : sampleData ? (
            <div className="border border-slate-800 rounded-lg overflow-x-auto bg-slate-950 max-h-80">
              <table className="w-full text-xs text-left font-mono">
                <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 uppercase text-[10px] sticky top-0">
                  <tr>
                    {sampleData.columns.map((col, idx) => (
                      <th key={idx} className="p-2.5 whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {sampleData.sample_rows.map((row, rIdx) => (
                    <tr key={rIdx} className="hover:bg-slate-900/40">
                      {sampleData.columns.map((col, cIdx) => (
                        <td key={cIdx} className="p-2.5 whitespace-nowrap text-slate-300">
                          {row[col] !== null ? String(row[col]) : '<null>'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
};
