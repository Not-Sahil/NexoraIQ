import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  BrainCircuit,
  AlertTriangle,
  Users,
  Package,
  Megaphone,
  Landmark,
  Bot,
  FileSpreadsheet,
  Database,
  ShieldCheck,
  Cpu,
  Settings,
  ChevronRight
} from 'lucide-react';

const NAV_GROUPS = [
  {
    title: 'Executive Analytics',
    items: [
      { name: 'Dashboard', path: '/', icon: LayoutDashboard },
      { name: 'Profitability', path: '/profitability', icon: TrendingUp },
      { name: 'Forecasting', path: '/forecasting', icon: BrainCircuit, badge: 'ML' },
      { name: 'Anomaly Detection', path: '/anomalies', icon: AlertTriangle, badge: 'Live' }
    ]
  },
  {
    title: 'Domain Intelligence',
    items: [
      { name: 'Customer Churn', path: '/customers', icon: Users },
      { name: 'Inventory & DIO', path: '/inventory', icon: Package },
      { name: 'Marketing ROI', path: '/marketing', icon: Megaphone },
      { name: 'Cash Flow & Risk', path: '/finance', icon: Landmark }
    ]
  },
  {
    title: 'AI Decision Engine',
    items: [
      { name: 'AI Business Advisor', path: '/advisor', icon: Bot, highlight: true },
      { name: 'Model Explainability', path: '/explainability', icon: Cpu },
      { name: 'Executive Reports', path: '/reports', icon: FileSpreadsheet }
    ]
  },
  {
    title: 'Data & Workspaces',
    items: [
      { name: 'Data Management', path: '/data', icon: Database },
      { name: 'Data Quality Audit', path: '/quality', icon: ShieldCheck },
      { name: 'Settings', path: '/settings', icon: Settings }
    ]
  }
];

export default function Sidebar() {
  return (
    <aside className="w-64 border-r border-slate-800/80 bg-slate-950/95 flex flex-col h-screen sticky top-0 z-40 select-none backdrop-blur-xl">
      {/* Brand Logo Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 via-brand-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-brand-500/20">
          <BrainCircuit className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
            Nexora<span className="text-brand-400">IQ</span>
          </span>
          <span className="block text-[10px] font-medium text-slate-500 uppercase tracking-widest">
            Decision SaaS
          </span>
        </div>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
        {NAV_GROUPS.map((group, gIdx) => (
          <div key={gIdx} className="space-y-1.5">
            <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">
              {group.title}
            </h3>
            {group.items.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={item.path === '/'}
                  className={({ isActive }) => `
                    group flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150
                    ${isActive
                      ? 'bg-brand-500/15 text-brand-300 border border-brand-500/30 shadow-sm shadow-brand-500/10'
                      : item.highlight
                        ? 'text-cyan-300 hover:bg-cyan-500/10 hover:text-cyan-200'
                        : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60'
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 transition-transform group-hover:scale-110" />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
                      {item.badge}
                    </span>
                  )}
                  {item.highlight && (
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                  )}
                </NavLink>
              );
            })}
          </div>
        ))}
      </div>

      {/* Footer Status */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/30">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-[11px] text-slate-300 font-medium">ML Engine Online</span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">v1.0.0</span>
        </div>
      </div>
    </aside>
  );
}

