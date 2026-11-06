import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import KPICard from '../components/KPICard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  AlertTriangle,
  AlertOctagon,
  ShieldCheck,
  Zap,
  Sliders,
  CheckCircle2,
  Calendar,
  Layers
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';

export default function AnomalyDetection() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [data, setData] = useState(null);
  const [contamination, setContamination] = useState(0.05);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchAnomalies = async () => {
      setLoading(true);
      try {
        const url = activeDataset
          ? `/anomalies/?workspace_id=${activeWorkspace.id}&dataset_id=${activeDataset.id}&contamination=${contamination}`
          : `/anomalies/?workspace_id=${activeWorkspace.id}&contamination=${contamination}`;
        const res = await api.get(url);
        setData(res.data);
      } catch (err) {
        console.error('Error fetching anomalies:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnomalies();
  }, [activeWorkspace, activeDataset, contamination]);

  if (loading) return <LoadingSpinner message="Scanning dataset with Isolation Forest, LOF, and Rolling Z-Score..." />;
  if (!data || !data.anomalies) return <EmptyState title="No Anomalies Scanned" description="Select an active dataset to run multi-method anomaly detection." />;

  const anomalies = data.anomalies || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Intelligent Multi-Method Anomaly Detection
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Ensemble detection via Isolation Forest, LOF, and 3-sigma rolling boundaries on <span className="text-brand-400 font-semibold">{data.dataset_name}</span>
          </p>
        </div>

        {/* Contamination Slider */}
        <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-lg px-4 py-2">
          <Sliders className="w-4 h-4 text-brand-400" />
          <span className="text-xs text-slate-300 font-medium">Contamination Sensitivity:</span>
          <select
            value={contamination}
            onChange={(e) => setContamination(parseFloat(e.target.value))}
            className="bg-transparent text-xs font-bold text-white focus:outline-none cursor-pointer"
          >
            <option value={0.02} className="bg-slate-900">2% (Strict)</option>
            <option value={0.05} className="bg-slate-900">5% (Balanced)</option>
            <option value={0.10} className="bg-slate-900">10% (High Sensitivity)</option>
          </select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Flagged Events"
          value={data.total_count}
          subtitle="Ensemble Consensus"
          badgeText="Flagged"
          icon={AlertTriangle}
        />
        <KPICard
          title="Critical Severity"
          value={data.critical_count}
          subtitle="Deviation > 150%"
          trend={data.critical_count > 0 ? 'down' : 'up'}
          icon={AlertOctagon}
        />
        <KPICard
          title="High Severity"
          value={data.high_count}
          subtitle="Deviation > 75%"
          trend="neutral"
          icon={Zap}
        />
        <KPICard
          title="Target Monitored"
          value={data.target_column || 'Revenue'}
          subtitle="Primary Metric"
          trend="neutral"
          icon={Layers}
        />
      </div>

      {/* Detected Anomalies Feed */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-base font-semibold text-white">Anomalous Outlier Incidents ({anomalies.length})</h2>
            <p className="text-xs text-slate-400">Statistical anomalies mapped to operational root causes</p>
          </div>
        </div>

        <div className="space-y-3">
          {anomalies.map((anom, idx) => {
            const isCritical = anom.severity === 'critical';
            const isHigh = anom.severity === 'high';
            return (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 hover:border-slate-700/80 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="flex items-start gap-3.5">
                  <div className={`p-2 rounded-lg mt-0.5 ${
                    isCritical ? 'bg-rose-500/20 text-rose-400' : isHigh ? 'bg-amber-500/20 text-amber-400' : 'bg-cyan-500/20 text-cyan-400'
                  }`}>
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white">{anom.date}</span>
                      <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                        isCritical
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : isHigh
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                      }`}>
                        {anom.severity}
                      </span>
                      <span className="text-[11px] font-mono text-slate-400">
                        Method: {anom.primary_method}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
                      {anom.root_cause_explanation}
                    </p>
                  </div>
                </div>

                <div className="flex md:flex-col items-end justify-between md:justify-center border-t md:border-t-0 pt-2 md:pt-0 border-slate-800 shrink-0">
                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 block uppercase font-semibold">Recorded vs Expected</span>
                    <span className="text-xs font-mono font-bold text-white">
                      ${anom.actual_value.toLocaleString()} <span className="text-slate-500 font-normal">/ ${anom.expected_value.toLocaleString()}</span>
                    </span>
                  </div>
                  <div className="mt-1">
                    <span className={`text-xs font-mono font-bold ${
                      anom.deviation_pct < 0 ? 'text-rose-400' : 'text-emerald-400'
                    }`}>
                      {anom.deviation_pct > 0 ? `+${anom.deviation_pct}%` : `${anom.deviation_pct}%`}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}

          {anomalies.length === 0 && (
            <div className="p-8 text-center bg-slate-950/40 rounded-lg">
              <ShieldCheck className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
              <p className="text-xs text-slate-300">No statistically significant anomalies detected at current threshold.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

