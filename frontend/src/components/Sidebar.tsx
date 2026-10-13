import React from 'react';
import {
  LayoutDashboard,
  Cpu,
  Flame,
  ShieldAlert,
  BarChart3,
  Server,
  Layers,
  Activity,
} from 'lucide-react';

export type TabType = 'overview' | 'simulator' | 'security' | 'workload' | 'thermal' | 'metrics';

interface SidebarProps {
  currentTab: TabType;
  onSelectTab: (tab: TabType) => void;
  securityLoaded: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  securityLoaded,
}) => {
  const navItems = [
    {
      id: 'overview' as TabType,
      label: 'Overview Dashboard',
      description: 'System health, components & overview',
      icon: LayoutDashboard,
    },
    {
      id: 'simulator' as TabType,
      label: 'Impact Simulator',
      description: 'Cross-domain dependency & impact modeling',
      icon: Activity,
      badge: 'Interactive',
      badgeColor: 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30',
    },
    {
      id: 'security' as TabType,
      label: 'Security Intelligence',
      description: 'Real-time threat inference & classification',
      icon: ShieldAlert,
      badge: securityLoaded ? 'Live' : 'Pending',
      badgeColor: securityLoaded ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400',
    },
    {
      id: 'workload' as TabType,
      label: 'Workload & Allocation',
      description: 'Demand modeling & server allocation simulation',
      icon: Cpu,
      badge: 'Simulated',
      badgeColor: 'bg-blue-500/20 text-blue-400',
    },
    {
      id: 'thermal' as TabType,
      label: 'Thermal Intelligence',
      description: '30-min forecasting & risk threshold criteria',
      icon: Flame,
      badge: 'Architecture',
      badgeColor: 'bg-amber-500/20 text-amber-400',
    },
    {
      id: 'metrics' as TabType,
      label: 'Evaluation & Datasets',
      description: 'Verified metrics, feature rankings & raw data',
      icon: BarChart3,
    },
  ];

  return (
    <aside className="w-full md:w-64 bg-slate-950 border-r border-slate-800 p-4 shrink-0 md:sticky md:top-16 md:h-[calc(100vh-4rem)] md:overflow-y-auto flex flex-col justify-between z-30">
      <div className="space-y-1">
        <div className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          Intelligence Modules
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition cursor-pointer text-left ${
                isActive
                  ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                  : 'text-slate-300 hover:bg-slate-900 hover:text-white border border-transparent'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${item.badgeColor}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="mt-8 pt-4 border-t border-slate-800/80 px-3 text-xs text-slate-400 space-y-2">
        <div className="flex items-center space-x-2 text-slate-300">
          <Server className="w-4 h-4 text-cyan-500" />
          <span className="font-medium">PAI Cluster Spec:</span>
          <span>1,897 nodes</span>
        </div>
        <div className="flex items-center space-x-2 text-slate-300">
          <Layers className="w-4 h-4 text-emerald-500" />
          <span className="font-medium">UNSW-NB15:</span>
          <span>257k flows</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed pt-2">
          Final Review Prototype: Built on authentic local ML models, standardized datasets, and benchmark reports.
        </p>
      </div>
    </aside>
  );
};
