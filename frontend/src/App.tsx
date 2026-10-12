import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, TabType } from './components/Sidebar';
import { OverviewPage } from './pages/OverviewPage';
import { SecurityPage } from './pages/SecurityPage';
import { WorkloadPage } from './pages/WorkloadPage';
import { ThermalPage } from './pages/ThermalPage';
import { MetricsDatasetsPage } from './pages/MetricsDatasetsPage';

import {
  fetchHealth,
  fetchOverview,
  fetchSecurityMetadata,
  fetchWorkloadMetadata,
  fetchThermalMetadata,
} from './api';
import {
  OverviewResponse,
  SecurityMetadataResponse,
  WorkloadMetadataResponse,
  ThermalMetadataResponse,
} from './types';

export function App() {
  const [currentTab, setCurrentTab] = useState<TabType>('overview');
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [securityMeta, setSecurityMeta] = useState<SecurityMetadataResponse | null>(null);
  const [workloadMeta, setWorkloadMeta] = useState<WorkloadMetadataResponse | null>(null);
  const [thermalMeta, setThermalMeta] = useState<ThermalMetadataResponse | null>(null);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      await fetchHealth();
      setBackendHealthy(true);

      const [ov, sec, wl, th] = await Promise.all([
        fetchOverview().catch(() => null),
        fetchSecurityMetadata().catch(() => null),
        fetchWorkloadMetadata().catch(() => null),
        fetchThermalMetadata().catch(() => null),
      ]);

      if (ov) setOverview(ov);
      if (sec) setSecurityMeta(sec);
      if (wl) setWorkloadMeta(wl);
      if (th) setThermalMeta(th);
    } catch (err) {
      console.error('Connection to backend failed:', err);
      setBackendHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const securityLoaded = securityMeta?.status === 'loaded';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      <Navbar
        backendHealthy={backendHealthy}
        activeModelsCount={overview?.active_models_count ?? 1}
        totalModelsCount={overview?.total_models_count ?? 3}
        onRefresh={loadInitialData}
        loading={loading}
      />

      <div className="flex-1 max-w-7xl w-full mx-auto flex flex-col md:flex-row relative">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          securityLoaded={securityLoaded}
        />

        <main className="flex-1 min-w-0 p-4 sm:p-6 lg:p-8">
          {currentTab === 'overview' && (
            <OverviewPage overview={overview} onNavigate={setCurrentTab} />
          )}
          {currentTab === 'security' && <SecurityPage metadata={securityMeta} />}
          {currentTab === 'workload' && <WorkloadPage metadata={workloadMeta} />}
          {currentTab === 'thermal' && <ThermalPage metadata={thermalMeta} />}
          {currentTab === 'metrics' && <MetricsDatasetsPage />}
        </main>
      </div>

      <footer className="border-t border-slate-900 bg-slate-950 py-3 text-center text-xs text-slate-500">
        AI Data Center Management Framework • Academic Final Project Review • Authentic ML Models & Benchmarks
      </footer>
    </div>
  );
}

export default App;
