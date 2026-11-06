import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import {
  Settings as SettingsIcon,
  Briefcase,
  Building,
  User,
  Shield,
  Plus,
  CheckCircle2,
  Lock
} from 'lucide-react';

export default function Settings() {
  const { user, activeWorkspace, workspaces, switchWorkspace } = useAuth();
  const [newWsName, setNewWsName] = useState('');
  const [newWsDesc, setNewWsDesc] = useState('');
  const [newWsDomain, setNewWsDomain] = useState('retail');
  const [creating, setCreating] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const handleCreateWorkspace = async (e) => {
    e.preventDefault();
    if (!newWsName.trim()) return;
    setCreating(true);
    setSuccessMsg('');
    try {
      const res = await api.post('/workspaces/', {
        name: newWsName,
        description: newWsDesc,
        domain_type: newWsDomain
      });
      setSuccessMsg(`Workspace '${res.data.name}' successfully initialized!`);
      setNewWsName('');
      setNewWsDesc('');
      window.location.reload();
    } catch (err) {
      alert(`Workspace creation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          Organization & Workspace Configuration
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Multi-tenant isolation, workspace provisioning, and security governance
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* User & Organization Details (1 col) */}
        <div className="space-y-6">
          <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6 space-y-4">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <User className="w-5 h-5 text-brand-400" />
              User Profile
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-500 block uppercase font-semibold text-[10px]">Full Name</span>
                <span className="font-semibold text-white text-sm">{user?.full_name || 'Senior Business Analyst'}</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-semibold text-[10px]">Email Address</span>
                <span className="text-slate-300 font-mono">{user?.email || 'demo@nexoraiq.com'}</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-semibold text-[10px]">Tenant Role</span>
                <span className="px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 font-semibold uppercase text-[10px] inline-block mt-1">
                  {user?.role || 'Owner'}
                </span>
              </div>
            </div>
          </div>

          <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6 space-y-4">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <Building className="w-5 h-5 text-cyan-400" />
              Organization Security
            </h2>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-500 block uppercase font-semibold text-[10px]">Active Plan</span>
                <span className="text-emerald-400 font-bold uppercase">Enterprise Tier</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-semibold text-[10px]">Database Architecture</span>
                <span className="text-slate-300 font-medium">Supabase PostgreSQL + RLS</span>
              </div>
              <div className="pt-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 text-[11px] font-semibold border border-emerald-500/20">
                  <Lock className="w-3.5 h-3.5" />
                  Tenant Data Isolated
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Workspace Provisioning & Listing (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Create New Workspace */}
          <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
            <h2 className="text-base font-semibold text-white mb-2 flex items-center gap-2">
              <Plus className="w-5 h-5 text-brand-400" />
              Create Isolated Business Workspace
            </h2>
            <p className="text-xs text-slate-400 mb-6">
              Each workspace maintains its own isolated datasets, forecasts, anomalies, and AI memory.
            </p>

            {successMsg && (
              <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{successMsg}</span>
              </div>
            )}

            <form onSubmit={handleCreateWorkspace} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Workspace Name *</label>
                <input
                  type="text"
                  required
                  value={newWsName}
                  onChange={(e) => setNewWsName(e.target.value)}
                  placeholder="e.g. European B2B Wholesale"
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Industry Domain Type</label>
                <select
                  value={newWsDomain}
                  onChange={(e) => setNewWsDomain(e.target.value)}
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-brand-500"
                >
                  <option value="retail">Retail and E-Commerce</option>
                  <option value="saas">SaaS and Subscription Business</option>
                  <option value="manufacturing">Manufacturing and Inventory</option>
                  <option value="general">General Business Financial Operations</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description (Optional)</label>
                <textarea
                  rows={2}
                  value={newWsDesc}
                  onChange={(e) => setNewWsDesc(e.target.value)}
                  placeholder="Operational scope, team ownership, or objectives..."
                  className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
                />
              </div>

              <button
                type="submit"
                disabled={creating || !newWsName.trim()}
                className="px-5 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-brand-600/20 transition-all inline-flex items-center gap-2"
              >
                <Briefcase className="w-4 h-4" />
                <span>{creating ? 'Creating Workspace...' : 'Initialize Workspace'}</span>
              </button>
            </form>
          </div>

          {/* Existing Workspaces List */}
          <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
            <h2 className="text-base font-semibold text-white mb-4">
              Registered Workspaces ({workspaces.length})
            </h2>

            <div className="space-y-3">
              {workspaces.map((ws) => {
                const isActive = activeWorkspace?.id === ws.id;
                return (
                  <div
                    key={ws.id}
                    onClick={() => switchWorkspace(ws.id)}
                    className={`p-4 rounded-xl border text-xs cursor-pointer flex items-center justify-between transition-all ${
                      isActive
                        ? 'bg-brand-500/10 border-brand-500/40 text-brand-200'
                        : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-sm">{ws.name}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-400 uppercase">
                          {ws.domain_type}
                        </span>
                      </div>
                      <p className="text-slate-400 mt-1">{ws.description || 'No description provided.'}</p>
                    </div>

                    {isActive ? (
                      <span className="px-2.5 py-1 rounded-md bg-brand-500/20 text-brand-300 font-bold text-[11px] border border-brand-500/30">
                        Current Active
                      </span>
                    ) : (
                      <button className="text-slate-400 hover:text-white font-medium text-xs">
                        Switch &rarr;
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

