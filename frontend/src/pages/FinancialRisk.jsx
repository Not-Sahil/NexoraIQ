import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import KPICard from '../components/KPICard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  Landmark,
  Flame,
  Clock,
  PieChart,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';

export default function FinancialRisk() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchFinance = async () => {
      setLoading(true);
      try {
        const url = activeDataset
          ? `/analytics/finance?workspace_id=${activeWorkspace.id}&dataset_id=${activeDataset.id}`
          : `/analytics/finance?workspace_id=${activeWorkspace.id}`;
        const res = await api.get(url);
        setData(res.data);
      } catch (err) {
        console.error('Error fetching financial risk:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchFinance();
  }, [activeWorkspace, activeDataset]);

  if (loading) return <LoadingSpinner message="Evaluating cash flow, runway, and liquidity stress..." />;
  if (!data || data.status === 'insufficient_data') {
    return <EmptyState title="No Financial Risk Data" description="Active dataset requires financial operations metrics." />;
  }

  const isHealthy = data.stress_index === 'healthy';

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Cash-Flow & Financial Stress Risk Intelligence
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Liquidity runway analysis, burn rate projection, and revenue concentration vulnerability
          </p>
        </div>

        <div className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg border text-xs font-semibold ${
          isHealthy
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
        }`}>
          {isHealthy ? <ShieldCheck className="w-4 h-4" /> : <ShieldAlert className="w-4 h-4" />}
          <span>Stress Index: {data.stress_index.toUpperCase()}</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Projected Cash Runway"
          value={`${data.runway_months} Months`}
          subtitle="Until Zero Cash Balance"
          badgeText={data.runway_months > 6 ? 'Sufficient' : 'Critical Hazard'}
          trend={data.runway_months > 6 ? 'up' : 'down'}
          icon={Clock}
        />
        <KPICard
          title="Monthly Net Burn Rate"
          value={`$${data.monthly_burn_rate.toLocaleString()}`}
          subtitle="Operating Outflow Deficit"
          trend="neutral"
          icon={Flame}
        />
        <KPICard
          title="Estimated Liquidity Reserves"
          value={`$${data.cash_balance_estimate.toLocaleString()}`}
          subtitle="Working Capital Balance"
          trend="neutral"
          icon={Landmark}
        />
        <KPICard
          title="Revenue Concentration Risk"
          value={`${data.revenue_concentration_pct}%`}
          subtitle="Top 5 Accounts Share"
          badgeText={data.revenue_concentration_pct > 50 ? 'High Risk' : 'Diversified'}
          trend={data.revenue_concentration_pct > 50 ? 'down' : 'up'}
          icon={PieChart}
        />
      </div>

      {/* Stress Factors & Recommendations */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
        <h2 className="text-base font-semibold text-white mb-1 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          Financial Stress Contributors & Solvency Assessment
        </h2>
        <p className="text-xs text-slate-400 mb-6">Identified solvency risks requiring executive attention</p>

        {data.stress_factors && data.stress_factors.length > 0 ? (
          <div className="space-y-3">
            {data.stress_factors.map((factor, idx) => (
              <div key={idx} className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-3">
                <div className="p-1.5 rounded bg-rose-500/10 text-rose-400 mt-0.5">
                  <ShieldAlert className="w-4 h-4" />
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-medium">
                  {factor}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-slate-950/40 rounded-lg">
            <ShieldCheck className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <p className="text-xs text-slate-300">Working capital and cash reserves are fully adequate for current burn rate.</p>
          </div>
        )}
      </div>
    </div>
  );
}

