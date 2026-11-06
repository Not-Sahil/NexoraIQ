import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import KPICard from '../components/KPICard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  Package,
  Boxes,
  AlertTriangle,
  RotateCw,
  Clock,
  Layers,
  ArrowRight
} from 'lucide-react';

export default function Inventory() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchInventory = async () => {
      setLoading(true);
      try {
        const url = activeDataset
          ? `/analytics/inventory?workspace_id=${activeWorkspace.id}&dataset_id=${activeDataset.id}`
          : `/analytics/inventory?workspace_id=${activeWorkspace.id}`;
        const res = await api.get(url);
        setData(res.data);
      } catch (err) {
        console.error('Error fetching inventory:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchInventory();
  }, [activeWorkspace, activeDataset]);

  if (loading) return <LoadingSpinner message="Evaluating inventory velocity, DIO, and stockout hazards..." />;
  if (!data || data.status === 'insufficient_data') {
    return <EmptyState title="No Inventory Data" description="Active dataset does not contain SKU or inventory volume metrics. Select a manufacturing or retail dataset." />;
  }

  const abcItems = data.abc_classification || [];
  const stockoutRisks = data.high_stockout_risks || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Inventory & Operational Supply Intelligence
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Days Inventory Outstanding (DIO), ABC classification, and demand replenishment for <span className="text-brand-400 font-semibold">{data.dataset_name}</span>
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Inventory Turnover Ratio"
          value={`${data.inventory_turnover_ratio}x`}
          subtitle="Annualized Velocity"
          trend={data.inventory_turnover_ratio >= 4 ? 'up' : 'down'}
          icon={RotateCw}
        />
        <KPICard
          title="Days Inventory Outstanding (DIO)"
          value={`${data.days_inventory_outstanding} Days`}
          subtitle="Capital Tied Up In Stock"
          badgeText={data.days_inventory_outstanding < 60 ? 'Optimal' : 'Elevated'}
          trend="neutral"
          icon={Clock}
        />
        <KPICard
          title="Stockout Risk Vulnerability"
          value={stockoutRisks.length}
          subtitle="SKUs Needing Urgent Reorder"
          trend={stockoutRisks.length > 0 ? 'down' : 'up'}
          icon={AlertTriangle}
        />
        <KPICard
          title="Catalog SKUs Evaluated"
          value={data.abc_items_count}
          subtitle="ABC Pareto Stratification"
          trend="neutral"
          icon={Boxes}
        />
      </div>

      {/* ABC Classification Table */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-white">ABC Product Classification (80/15/5 Pareto Rule)</h2>
            <p className="text-xs text-slate-400">Class A drives 80% of revenue, Class B 15%, Class C 5%</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-slate-800 text-slate-300">
            {abcItems.length} Products Profiled
          </span>
        </div>

        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3 font-semibold">SKU / Product Name</th>
                <th className="px-4 py-3 font-semibold text-center">ABC Class</th>
                <th className="px-4 py-3 font-semibold text-right">Attributed Revenue</th>
                <th className="px-4 py-3 font-semibold text-right">Throughput Units</th>
                <th className="px-4 py-3 font-semibold text-center">Stockout Risk</th>
                <th className="px-4 py-3 font-semibold text-right">Recommended Reorder Buffer</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/40 text-slate-300">
              {abcItems.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3 font-semibold text-white">{item.product}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      item.abc_class === 'A'
                        ? 'bg-brand-500/20 text-brand-300 border border-brand-500/30'
                        : item.abc_class === 'B'
                          ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                          : 'bg-slate-800 text-slate-400'
                    }`}>
                      Class {item.abc_class}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-semibold text-emerald-400">
                    ${item.revenue?.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right font-mono">{item.units?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold font-mono ${
                      item.stockout_risk_score > 60
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}>
                      {item.stockout_risk_score}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-300 font-semibold">
                    {item.recommended_reorder_point} units
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

