import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import KPICard from '../components/KPICard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  Megaphone,
  Target,
  Percent,
  TrendingUp,
  BarChart2,
  Sparkles
} from 'lucide-react';

export default function Marketing() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchMarketing = async () => {
      setLoading(true);
      try {
        const url = activeDataset
          ? `/analytics/marketing?workspace_id=${activeWorkspace.id}&dataset_id=${activeDataset.id}`
          : `/analytics/marketing?workspace_id=${activeWorkspace.id}`;
        const res = await api.get(url);
        setData(res.data);
      } catch (err) {
        console.error('Error fetching marketing analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMarketing();
  }, [activeWorkspace, activeDataset]);

  if (loading) return <LoadingSpinner message="Auditing marketing channels and ROAS attribution..." />;
  if (!data || data.status === 'insufficient_data') {
    return <EmptyState title="No Marketing Data" description="Active dataset does not contain marketing spend metrics." />;
  }

  const channels = data.channels || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Marketing Performance & Acquisition Intelligence
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Channel attribution, customer acquisition cost (CAC), and return on ad spend (ROAS)
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Ad Spend"
          value={`$${data.total_marketing_spend.toLocaleString()}`}
          subtitle="All Channels"
          icon={Megaphone}
        />
        <KPICard
          title="Overall Portfolio ROAS"
          value={`${data.overall_roas}x`}
          subtitle={`Marketing ROI: ${data.marketing_roi_pct}%`}
          badgeText={data.overall_roas >= 3 ? 'Efficient' : 'Needs Optimization'}
          trend={data.overall_roas >= 3 ? 'up' : 'down'}
          icon={TrendingUp}
        />
        <KPICard
          title="Blended CAC"
          value={`$${data.cac.toFixed(2)}`}
          subtitle="Acquisition Cost per Customer"
          trend="neutral"
          icon={Target}
        />
        <KPICard
          title="Traffic Conversion Rate"
          value={`${data.avg_conversion_rate}%`}
          subtitle={`${data.total_traffic.toLocaleString()} Total Visits`}
          trend="neutral"
          icon={Percent}
        />
      </div>

      {/* Channel Efficiency Table */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-white">Channel Efficiency & ROAS Performance</h2>
            <p className="text-xs text-slate-400">Comparison of acquisition expenditure versus attributed top-line revenue</p>
          </div>
        </div>

        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3 font-semibold">Marketing Channel</th>
                <th className="px-4 py-3 font-semibold text-right">Spend Allocated</th>
                <th className="px-4 py-3 font-semibold text-right">Attributed Revenue</th>
                <th className="px-4 py-3 font-semibold text-right">ROAS Multiple</th>
                <th className="px-4 py-3 font-semibold text-center">Efficiency Rating</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/40 text-slate-300">
              {channels.map((ch, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3 font-semibold text-white">{ch.channel}</td>
                  <td className="px-4 py-3 text-right font-mono">${ch.spend?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right font-mono font-semibold text-emerald-400">
                    ${ch.revenue?.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-bold text-white">{ch.roas}x</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      ch.efficiency === 'stellar'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : ch.efficiency === 'efficient'
                          ? 'bg-brand-500/20 text-brand-300 border border-brand-500/30'
                          : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    }`}>
                      {ch.efficiency}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

