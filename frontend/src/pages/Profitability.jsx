import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import KPICard from '../components/KPICard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  TrendingUp,
  DollarSign,
  AlertOctagon,
  Percent,
  Layers,
  ArrowDownRight,
  ShieldAlert
} from 'lucide-react';

export default function Profitability() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchProfitability = async () => {
      setLoading(true);
      try {
        const url = activeDataset
          ? `/analytics/profitability?workspace_id=${activeWorkspace.id}&dataset_id=${activeDataset.id}`
          : `/analytics/profitability?workspace_id=${activeWorkspace.id}`;
        const res = await api.get(url);
        setData(res.data);
      } catch (err) {
        console.error('Error fetching profitability:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfitability();
  }, [activeWorkspace, activeDataset]);

  if (loading) return <LoadingSpinner message="Analyzing unit economics and margin contribution..." />;
  if (!data || data.error) return <EmptyState title="No Profitability Data" description="Upload a dataset containing revenue and cost figures." />;

  const isCompressing = data.margin_trend === 'compressing';
  const dimensions = data.dimension_breakdowns || {};
  const primaryDimKey = Object.keys(dimensions)[0];
  const primaryItems = primaryDimKey ? dimensions[primaryDimKey] : [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Profitability & Unit Economics Intelligence
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Margin deterioration tracking and dimensional contribution for <span className="text-brand-400 font-semibold">{data.dataset_name}</span>
          </p>
        </div>

        {isCompressing && (
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold">
            <ShieldAlert className="w-4 h-4" />
            <span>Alert: Sequential Margin Contraction Detected</span>
          </div>
        )}
      </div>

      {/* KPI Matrix */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Gross Profit"
          value={`$${data.gross_profit.toLocaleString()}`}
          subtitle={`Gross Margin: ${data.gross_margin_pct}%`}
          trend={data.gross_profit >= 0 ? 'up' : 'down'}
          icon={DollarSign}
        />
        <KPICard
          title="Net Operating Profit"
          value={`$${data.net_profit.toLocaleString()}`}
          subtitle={`Net Margin: ${data.net_margin_pct}%`}
          badgeText={data.net_margin_pct > 15 ? 'Strong' : 'Tight'}
          trend={data.net_profit >= 0 ? 'up' : 'down'}
          icon={TrendingUp}
        />
        <KPICard
          title="Contribution Margin Ratio"
          value={`${(data.contribution_margin_ratio * 100).toFixed(1)}%`}
          subtitle="Variable Coverage"
          trend="neutral"
          icon={Percent}
        />
        <KPICard
          title="Break-Even Threshold"
          value={`$${data.break_even_revenue.toLocaleString()}`}
          subtitle="Minimum Required Volume"
          trend="neutral"
          icon={AlertOctagon}
        />
      </div>

      {/* Flagged High-Volume Low-Profit Products Alert */}
      {primaryItems.some(i => i.is_high_revenue_low_profit) && (
        <div className="rounded-xl bg-amber-500/10 border border-amber-500/20 p-5 flex items-start gap-3">
          <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 mt-0.5">
            <AlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Hidden Profitability Leakage Isolated</h3>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              We identified items generating top 40% volume that yield net margins in the bottom 35th percentile.
              These high-volume products consume operating throughput while diluting overall portfolio return.
            </p>
          </div>
        </div>
      )}

      {/* Dimension Breakdown Table */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-white capitalize">
              {primaryDimKey || 'Product'} Margin Breakdown
            </h2>
            <p className="text-xs text-slate-400">Net contribution across individual catalog lines</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-800 text-slate-300">
            {primaryItems.length} lines evaluated
          </span>
        </div>

        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3 font-semibold">{primaryDimKey || 'Item'}</th>
                <th className="px-4 py-3 font-semibold text-right">Gross Revenue</th>
                <th className="px-4 py-3 font-semibold text-right">Direct COGS</th>
                <th className="px-4 py-3 font-semibold text-right">Net Profit</th>
                <th className="px-4 py-3 font-semibold text-right">Margin %</th>
                <th className="px-4 py-3 font-semibold text-center">Status Flag</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/40 text-slate-300">
              {primaryItems.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3 font-semibold text-white">
                    {item[primaryDimKey] || item.product || item.Product || item.Company || `Item #${idx+1}`}
                  </td>
                  <td className="px-4 py-3 text-right font-mono">${item.revenue?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right font-mono text-slate-400">${item.cost?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right font-mono text-emerald-400 font-semibold">${item.profit?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right font-mono font-semibold">
                    <span className={item.margin_pct < 20 ? 'text-rose-400' : 'text-emerald-400'}>
                      {item.margin_pct}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {item.is_high_revenue_low_profit ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        Margin Leakage
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400">
                        Balanced
                      </span>
                    )}
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

