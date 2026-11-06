import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import KPICard from '../components/KPICard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  DollarSign,
  TrendingUp,
  Percent,
  Users,
  ShoppingCart,
  Target,
  Megaphone,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from 'recharts';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchDashboard = async () => {
      setLoading(true);
      try {
        const url = activeDataset
          ? `/dashboard/summary?workspace_id=${activeWorkspace.id}&dataset_id=${activeDataset.id}`
          : `/dashboard/summary?workspace_id=${activeWorkspace.id}`;
        const res = await api.get(url);
        setData(res.data);
      } catch (err) {
        console.error('Error fetching dashboard summary:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [activeWorkspace, activeDataset]);

  if (loading) return <LoadingSpinner message="Calculating business KPIs from verified data..." />;
  if (!data || !data.has_data) return <EmptyState />;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Executive Decision Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Live business intelligence synthesized from <span className="text-brand-400 font-semibold">{data.dataset_name}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/forecasting"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-600/20 transition-colors"
          >
            <span>Run ML Forecast</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
          <Link
            to="/reports"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700/60 transition-colors"
          >
            Export Brief
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Gross Revenue"
          value={`$${data.total_revenue.toLocaleString()}`}
          change={data.growth_pct}
          trend={data.growth_pct >= 0 ? 'up' : 'down'}
          subtitle="Period-over-Period"
          icon={DollarSign}
        />
        <KPICard
          title="Net Profit"
          value={`$${data.net_profit.toLocaleString()}`}
          subtitle={`Net Margin: ${data.net_margin_pct}%`}
          badgeText={data.net_margin_pct > 15 ? 'Healthy' : 'Compressed'}
          trend={data.net_profit >= 0 ? 'up' : 'down'}
          icon={TrendingUp}
        />
        <KPICard
          title="Customer Acquisition (CAC)"
          value={`$${data.cac.toFixed(2)}`}
          subtitle={`CLV: $${data.clv.toFixed(2)}`}
          trend="neutral"
          icon={Target}
        />
        <KPICard
          title="Marketing ROAS"
          value={`${data.marketing_roas}x`}
          subtitle={`Spend: $${data.marketing_spend.toLocaleString()}`}
          trend={data.marketing_roas >= 3 ? 'up' : 'down'}
          icon={Megaphone}
        />
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue & Profit Timeseries (2 cols) */}
        <div className="lg:col-span-2 rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-semibold text-white">Revenue & Profit Trajectory</h2>
              <p className="text-xs text-slate-400">Sequential performance over reporting periods</p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-800 text-slate-300">
              Verified Actuals
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.trend_chart}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0e8ce9" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0e8ce9" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val) => [`$${Number(val).toLocaleString()}`, '']}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="revenue" name="Gross Revenue" stroke="#0e8ce9" strokeWidth={2} fillOpacity={1} fill="url(#colorRevenue)" />
                <Area type="monotone" dataKey="profit" name="Net Profit" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorProfit)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Operating Cost Breakdown (1 col) */}
        <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-semibold text-white mb-1">Cost & Overhead Structure</h2>
            <p className="text-xs text-slate-400 mb-6">Distribution of operational expenditures</p>

            <div className="space-y-4">
              {data.expense_breakdown.map((exp, idx) => (
                <div key={idx} className="space-y-1.5">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-300">{exp.name}</span>
                    <span className="text-slate-400 font-mono">${exp.amount.toLocaleString()}</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        idx === 0 ? 'bg-brand-500' : idx === 1 ? 'bg-cyan-400' : idx === 2 ? 'bg-indigo-400' : 'bg-amber-400'
                      }`}
                      style={{ width: `${Math.min(100, exp.share)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-6 mt-6 border-t border-slate-800/80 text-center">
            <Link
              to="/profitability"
              className="text-xs font-semibold text-brand-400 hover:text-brand-300 transition-colors inline-flex items-center gap-1"
            >
              Deep-Dive Profitability Analytics &rarr;
            </Link>
          </div>
        </div>
      </div>

      {/* Secondary Operational KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-xl bg-slate-900/50 border border-slate-800/80 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-400">Total Active Buyers</p>
              <h4 className="text-lg font-bold text-white mt-0.5">{data.total_customers.toLocaleString()}</h4>
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-slate-900/50 border border-slate-800/80 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShoppingCart className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-400">Average Order Value (AOV)</p>
              <h4 className="text-lg font-bold text-white mt-0.5">${data.average_order_value.toFixed(2)}</h4>
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-slate-900/50 border border-slate-800/80 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Percent className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-400">Conversion Rate</p>
              <h4 className="text-lg font-bold text-white mt-0.5">{data.conversion_rate}%</h4>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

