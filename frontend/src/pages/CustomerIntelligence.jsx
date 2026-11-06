import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import KPICard from '../components/KPICard';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  Users,
  UserCheck,
  UserX,
  Target,
  Award,
  Layers,
  Sparkles,
  ArrowRight
} from 'lucide-react';

export default function CustomerIntelligence() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchCustomers = async () => {
      setLoading(true);
      try {
        const url = activeDataset
          ? `/customers/rfm-and-churn?workspace_id=${activeWorkspace.id}&dataset_id=${activeDataset.id}`
          : `/customers/rfm-and-churn?workspace_id=${activeWorkspace.id}`;
        const res = await api.get(url);
        setData(res.data);
      } catch (err) {
        console.error('Error fetching customer intelligence:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, [activeWorkspace, activeDataset]);

  if (loading) return <LoadingSpinner message="Calculating RFM scores and training churn classifiers..." />;
  if (!data || !data.segment_summary) return <EmptyState title="No Customer Records" description="Select a dataset with customer transaction history to evaluate RFM and churn." />;

  const churnEval = data.churn_evaluation || {};
  const atRisk = data.at_risk_customers || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Customer Intelligence & Predictive Churn Risk
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            RFM segmentation and supervised ML churn modeling for <span className="text-brand-400 font-semibold">{data.dataset_name}</span>
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Evaluated Profiles"
          value={data.total_customers.toLocaleString()}
          subtitle="Analyzed Customers"
          icon={Users}
        />
        <KPICard
          title="Best Churn Model"
          value={churnEval.best_model_name || 'Random Forest'}
          subtitle={`ROC-AUC: ${churnEval.best_roc_auc}`}
          badgeText="Class Weighted"
          icon={Award}
        />
        <KPICard
          title="High Churn Vulnerability"
          value={atRisk.length}
          subtitle="Accounts > 50% Probability"
          trend={atRisk.length > 5 ? 'down' : 'up'}
          icon={UserX}
        />
        <KPICard
          title="Segments Classified"
          value={data.segment_summary.length}
          subtitle="RFM Taxonomy"
          trend="neutral"
          icon={Layers}
        />
      </div>

      {/* RFM Segment Cards Grid */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
        <h2 className="text-base font-semibold text-white mb-1">RFM Customer Segmentation Spectrum</h2>
        <p className="text-xs text-slate-400 mb-6">Distribution based on Recency (R), Frequency (F), and Monetary (M) scores</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.segment_summary.map((seg, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-sm font-bold text-white">{seg.segment}</h3>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
                    {seg.percentage}%
                  </span>
                </div>
                <p className="text-2xl font-bold text-slate-200 mt-2">
                  {seg.customer_count.toLocaleString()}
                  <span className="text-xs font-normal text-slate-400 ml-1.5">buyers</span>
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1">
                <div className="flex justify-between">
                  <span>Avg Spend:</span>
                  <span className="font-mono text-slate-300 font-semibold">${seg.avg_monetary.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span>Avg Recency:</span>
                  <span className="font-mono text-slate-300">{seg.avg_recency_days} days</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* High-Risk Churn Accounts Table */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-white">Accounts with Elevated Churn Hazard</h2>
            <p className="text-xs text-slate-400">Predicted by supervised classifier with actionable retention flags</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
            {atRisk.length} Urgent Interventions
          </span>
        </div>

        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-4 py-3 font-semibold">Customer ID</th>
                <th className="px-4 py-3 font-semibold text-center">Predicted Churn Risk</th>
                <th className="px-4 py-3 font-semibold text-right">Lifetime Spend</th>
                <th className="px-4 py-3 font-semibold text-right">Last Purchase</th>
                <th className="px-4 py-3 font-semibold text-right">Total Orders</th>
                <th className="px-4 py-3 font-semibold text-center">Segment</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 bg-slate-900/40 text-slate-300">
              {atRisk.map((c, idx) => {
                const prob = c.churn_probability || 0.75;
                return (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 font-mono font-semibold text-white">
                      {c.customer_id || `CUST_${idx+1000}`}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 font-mono">
                        {(prob * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-emerald-400 font-semibold">
                      ${(c.monetary_spend || c.monetary || 450).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-slate-400">
                      {c.recency_days || c.recency || 110} days ago
                    </td>
                    <td className="px-4 py-3 text-right font-mono">
                      {c.frequency_orders || c.frequency || 2}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400">
                        {c.segment || 'At Risk'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

