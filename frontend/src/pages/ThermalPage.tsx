import React, { useState } from 'react';
import {
  Flame,
  Thermometer,
  Wind,
  Zap,
  Info,
  Clock,
  AlertTriangle,
  Sliders,
  CheckCircle2,
  Layers,
} from 'lucide-react';
import { ThermalMetadataResponse } from '../types';

interface ThermalPageProps {
  metadata: ThermalMetadataResponse | null;
}

export const ThermalPage: React.FC<ThermalPageProps> = ({ metadata }) => {
  const [inletTemp, setInletTemp] = useState<number>(22.5);
  const [outletTemp, setOutletTemp] = useState<number>(36.8);
  const [powerKw, setPowerKw] = useState<number>(14.5);

  const deltaTemp = +(outletTemp - inletTemp).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-white m-0">Thermal Management & Forecasting</h2>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                Marconi A2 Supercomputer Architecture
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 m-0">
              30-minute predictive temperature forecasting and statistical risk monitoring across data-center rack sensors.
            </p>
          </div>

          <div className="flex items-center space-x-2 text-xs">
            <span className="px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1.5 font-medium">
              <Info className="w-3.5 h-3.5" />
              Forecasting Model: Offline Architecture (Multi-GB Sensor Data Pending Ingestion)
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Sensor Feature Exploration Form (6 cols) */}
        <div className="lg:col-span-6 rounded-xl border border-slate-800 bg-slate-900/80 p-5">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-white flex items-center gap-2 m-0">
                <Sliders className="w-4 h-4 text-amber-400" />
                Rack Airflow & Thermal Telemetry
              </h3>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                User-Provided Input
              </span>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">10-Min Sample Interval</span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Mean Inlet Air Temperature (°C)
              </label>
              <input
                type="number"
                step="0.1"
                value={inletTemp}
                onChange={(e) => setInletTemp(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-amber-500 font-mono"
              />
              <span className="text-[11px] text-slate-500">Typical cold aisle range: 18°C - 27°C</span>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Mean Outlet Air Temperature (°C)
              </label>
              <input
                type="number"
                step="0.1"
                value={outletTemp}
                onChange={(e) => setOutletTemp(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-amber-500 font-mono"
              />
              <span className="text-[11px] text-slate-500">Hot aisle exhaust temperature</span>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Rack Power Consumption (kW)
              </label>
              <input
                type="number"
                step="0.1"
                value={powerKw}
                onChange={(e) => setPowerKw(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white text-xs focus:outline-none focus:border-amber-500 font-mono"
              />
              <span className="text-[11px] text-slate-500">Rack electrical dissipation</span>
            </div>

            {/* Computed Temperature Difference */}
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div className="text-xs">
                <span className="text-slate-400 block">Temperature Difference (ΔT = Outlet - Inlet):</span>
                <span className="text-slate-500 text-[11px]">Primary indicator of heat extraction efficiency</span>
              </div>
              <div className="text-lg font-bold font-mono text-amber-400">
                +{deltaTemp} °C
              </div>
            </div>

            {/* Notice regarding live prediction */}
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800/80 text-xs text-slate-400 leading-relaxed">
              <span className="font-semibold text-slate-300 flex items-center gap-1.5 mb-1">
                <Clock className="w-3.5 h-3.5 text-amber-400" />
                30-Minute Horizon Forecasting:
              </span>
              The model architecture (<code className="text-cyan-400 bg-slate-900 px-1 py-0.5 rounded">src/models/thermal_forecasting.py</code>)
              builds lag features at 0, 10, 20, 30, and 60 minutes across inlet, outlet, and power sensors to predict 30-minute-ahead outlet temperature.
              Because multi-gigabyte raw sensor datasets were omitted from version control, fabricated predictions are suppressed.
            </div>
          </div>
        </div>

        {/* Exploratory Risk Thresholds & Physics (6 cols) */}
        <div className="lg:col-span-6 space-y-6">
          {/* Thresholds Table */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">
            <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2 m-0">
              <Thermometer className="w-4 h-4 text-amber-400" />
              Exploratory Thermal Risk Thresholds
            </h3>
            <p className="text-xs text-slate-400 mb-3">
              Statistical operational thresholds evaluated in{' '}
              <code className="text-cyan-400 bg-slate-950 px-1 py-0.5 rounded">
                src/models/thermal_risk_analysis.py
              </code>
              :
            </p>

            <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-950">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 text-[10px] uppercase font-semibold">
                  <tr>
                    <th className="p-2.5">Threshold</th>
                    <th className="p-2.5">Severity</th>
                    <th className="p-2.5">Operational Protocol</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  <tr>
                    <td className="p-2.5 font-bold text-slate-300">55.0 °C</td>
                    <td className="p-2.5 text-blue-400">Advisory</td>
                    <td className="p-2.5 text-slate-400 font-sans">Elevated zone; inspect CRAH fan status</td>
                  </tr>
                  <tr>
                    <td className="p-2.5 font-bold text-amber-400">60.0 °C</td>
                    <td className="p-2.5 text-amber-400">Warning</td>
                    <td className="p-2.5 text-slate-400 font-sans">Action threshold; check containment panels</td>
                  </tr>
                  <tr>
                    <td className="p-2.5 font-bold text-orange-400">65.0 °C</td>
                    <td className="p-2.5 text-orange-400">Critical</td>
                    <td className="p-2.5 text-slate-400 font-sans">Workload throttling & fan speed ramp</td>
                  </tr>
                  <tr>
                    <td className="p-2.5 font-bold text-rose-400">70.0 °C</td>
                    <td className="p-2.5 text-rose-400">Emergency</td>
                    <td className="p-2.5 text-slate-400 font-sans">Hardware protection thermal limit</td>
                  </tr>
                  <tr>
                    <td className="p-2.5 font-bold text-purple-400">95th %ile</td>
                    <td className="p-2.5 text-purple-400">Statistical Peak</td>
                    <td className="p-2.5 text-slate-400 font-sans">Historical top 5% temperature events</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p className="text-[11px] text-slate-500 mt-3 leading-relaxed m-0">
              <strong>Research Note:</strong> Statistical thresholds are exploratory benchmarks from Marconi A2 supercomputer logs and require domain verification for specific facility hardware.
            </p>
          </div>

          {/* Cooling Dynamics Card */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">
            <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2 m-0">
              <Wind className="w-4 h-4 text-cyan-400" />
              Convective Heat Transfer in High-Density AI Racks
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              In AI compute clusters featuring dense GPU accelerators, electrical power converts almost entirely into thermal energy.
              Anticipating outlet temperature 30 minutes in advance enables proactive cooling adjustments and task placement redirection
              before hotspot zones trip emergency hardware throttling.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
