import React from 'react';
import { Cpu, CheckCircle2, AlertTriangle, RefreshCw, Activity, LogOut, User as UserIcon } from 'lucide-react';
import { User } from '../types';

interface NavbarProps {
  backendHealthy: boolean | null;
  activeModelsCount: number;
  totalModelsCount: number;
  onRefresh: () => void;
  loading: boolean;
  currentUser?: User | null;
  onLogout?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  backendHealthy,
  activeModelsCount,
  totalModelsCount,
  onRefresh,
  loading,
  currentUser,
  onLogout,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950 sticky top-0 z-40 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base sm:text-lg font-bold tracking-tight text-white m-0">
                AI Data Center Operations Platform
              </h1>
              <span className="text-[10px] sm:text-xs font-semibold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 hidden sm:inline-block">
                Final Review Edition
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-400 m-0">
              Integrated Resource Management, Thermal Prevention & Threat Isolation
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Active Model Indicator */}
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-md bg-slate-900 border border-slate-800 text-xs">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span className="text-slate-400">Models:</span>
            <span className="font-semibold text-slate-200">
              {activeModelsCount}/{totalModelsCount} Active
            </span>
          </div>

          {/* Backend Status Badge */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-slate-900 border border-slate-800 text-xs">
            {backendHealthy === true ? (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span className="text-emerald-400 font-medium flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 inline" /> Core API Online
                </span>
              </>
            ) : backendHealthy === false ? (
              <>
                <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                <span className="text-rose-400 font-medium flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5 inline" /> Disconnected
                </span>
              </>
            ) : (
              <span className="text-slate-400">Connecting...</span>
            )}
          </div>

          {/* User Profile Pill & Logout */}
          {currentUser && (
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
              <div className="flex items-center space-x-2 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs">
                <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-purple-600 to-cyan-500 flex items-center justify-center font-bold text-white text-[11px] shadow-sm">
                  {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div className="hidden md:block text-left leading-tight">
                  <div className="font-semibold text-white truncate max-w-[100px]">{currentUser.name}</div>
                  <div className="text-[10px] text-slate-400">Researcher</div>
                </div>
              </div>

              {onLogout && (
                <button
                  onClick={onLogout}
                  className="p-1.5 rounded-lg bg-slate-900 hover:bg-rose-950/40 border border-slate-800 hover:border-rose-500/40 text-slate-400 hover:text-rose-400 transition cursor-pointer"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              )}
            </div>
          )}

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-2 rounded-md bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-white transition disabled:opacity-50 cursor-pointer"
            title="Refresh System Status"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
};
