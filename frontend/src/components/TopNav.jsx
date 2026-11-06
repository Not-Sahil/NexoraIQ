import React from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Briefcase,
  Database,
  Bell,
  Search,
  LogOut,
  ChevronDown,
  User,
  Sparkles
} from 'lucide-react';

export default function TopNav() {
  const {
    user,
    workspaces,
    activeWorkspace,
    switchWorkspace,
    datasets,
    activeDataset,
    switchDataset,
    logout
  } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Workspace & Dataset Selectors */}
      <div className="flex items-center gap-4">
        {/* Workspace Dropdown */}
        <div className="relative flex items-center gap-2 bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 shadow-sm">
          <Briefcase className="w-4 h-4 text-brand-400" />
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase font-semibold tracking-wider">Workspace</span>
            <select
              value={activeWorkspace?.id || ''}
              onChange={(e) => switchWorkspace(e.target.value)}
              className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer pr-4"
            >
              {workspaces.map((ws) => (
                <option key={ws.id} value={ws.id} className="bg-slate-900 text-slate-200">
                  {ws.name} ({ws.domain_type})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Dataset Dropdown */}
        <div className="relative flex items-center gap-2 bg-slate-900/80 border border-slate-800 rounded-lg px-3 py-1.5 shadow-sm">
          <Database className="w-4 h-4 text-cyan-400" />
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase font-semibold tracking-wider">Active Dataset</span>
            <select
              value={activeDataset?.id || ''}
              onChange={(e) => switchDataset(e.target.value)}
              className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer pr-4 max-w-[200px] truncate"
            >
              {datasets.map((ds) => (
                <option key={ds.id} value={ds.id} className="bg-slate-900 text-slate-200 truncate">
                  {ds.name}
                </option>
              ))}
              {datasets.length === 0 && (
                <option value="" disabled className="bg-slate-900 text-slate-400">
                  No datasets loaded
                </option>
              )}
            </select>
          </div>
        </div>
      </div>

      {/* Global Actions & User Profile */}
      <div className="flex items-center gap-4">
        {/* Quality Score Indicator */}
        {activeDataset && (
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Data Health: {activeDataset.quality_score}%</span>
          </div>
        )}

        {/* User Info & Logout */}
        <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center font-bold text-xs text-white shadow-md">
            {user?.full_name ? user.full_name.charAt(0) : 'U'}
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-semibold text-slate-200 truncate max-w-[140px]">
              {user?.full_name || 'Business Analyst'}
            </p>
            <p className="text-[10px] text-slate-400 capitalize">
              {user?.role || 'Owner'}
            </p>
          </div>
          <button
            onClick={logout}
            title="Log out"
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}

