import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, TabType } from './components/Sidebar';
import { OverviewPage } from './pages/OverviewPage';
import { SecurityPage } from './pages/SecurityPage';
import { WorkloadPage } from './pages/WorkloadPage';
import { ThermalPage } from './pages/ThermalPage';
import { SimulatorPage } from './pages/SimulatorPage';
import { MetricsDatasetsPage } from './pages/MetricsDatasetsPage';
import { AuthPage } from './pages/AuthPage';

import {
  fetchHealth,
  fetchOverview,
  fetchSecurityMetadata,
  fetchWorkloadMetadata,
  fetchThermalMetadata,
  fetchCurrentUser,
  logoutUser,
} from './api';
import {
  OverviewResponse,
  SecurityMetadataResponse,
  WorkloadMetadataResponse,
  ThermalMetadataResponse,
  User,
} from './types';
import { Loader2, Shield } from 'lucide-react';

export function App() {
  const [currentTab, setCurrentTab] = useState<TabType>('overview');
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  // Authentication State
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authChecking, setAuthChecking] = useState<boolean>(true);

  // Dashboard Data State
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [securityMeta, setSecurityMeta] = useState<SecurityMetadataResponse | null>(null);
  const [workloadMeta, setWorkloadMeta] = useState<WorkloadMetadataResponse | null>(null);
  const [thermalMeta, setThermalMeta] = useState<ThermalMetadataResponse | null>(null);

  // Check Session on Mount
  useEffect(() => {
    const initAuth = async () => {
      setAuthChecking(true);
      try {
        const user = await fetchCurrentUser();
        setCurrentUser(user);
        loadInitialData();
      } catch (err) {
        // Not authenticated
        setCurrentUser(null);
      } finally {
        setAuthChecking(false);
      }
    };

    initAuth();
  }, []);

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

  const handleAuthSuccess = (user: User) => {
    setCurrentUser(user);
    loadInitialData();
  };

  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch (err) {
      console.error('Logout error:', err);
    }
    setCurrentUser(null);
  };

  // Loading Screen while verifying session
  if (authChecking) {
    return (
      <div className="min-h-screen bg-[#070B14] flex flex-col items-center justify-center space-y-4 text-slate-300 font-sans">
        <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
          <Shield className="w-6 h-6 animate-pulse" />
        </div>
        <div className="flex items-center space-x-2 text-xs font-medium">
          <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
          <span>Verifying encrypted session token...</span>
        </div>
      </div>
    );
  }

  // If unauthenticated, display Login & Registration Page
  if (!currentUser) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  const securityLoaded = securityMeta?.status === 'loaded';

  // Authenticated Dashboard Layout
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      <Navbar
        backendHealthy={backendHealthy}
        activeModelsCount={overview?.active_models_count ?? 1}
        totalModelsCount={overview?.total_models_count ?? 3}
        onRefresh={loadInitialData}
        loading={loading}
        currentUser={currentUser}
        onLogout={handleLogout}
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
          {currentTab === 'simulator' && <SimulatorPage />}
          {currentTab === 'security' && <SecurityPage metadata={securityMeta} />}
          {currentTab === 'workload' && <WorkloadPage metadata={workloadMeta} />}
          {currentTab === 'thermal' && <ThermalPage metadata={thermalMeta} />}
          {currentTab === 'metrics' && <MetricsDatasetsPage />}
        </main>
      </div>

      <footer className="border-t border-slate-900 bg-slate-950 py-3 text-center text-xs text-slate-500">
        AI Data Center Management Framework • Secure MongoDB Authentication • Academic Final Project Review
      </footer>
    </div>
  );
}

export default App;
