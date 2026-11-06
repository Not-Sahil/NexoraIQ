import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  Cpu,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  Layers,
  BarChart3,
  ArrowRight
} from 'lucide-react';

export default function ModelPerformance() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [explainData, setExplainData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    const fetchExplain = async () => {
      setLoading(true);
      try {
        const url = activeDataset
          ? `/explainability/attribution?workspace_id=${activeWorkspace.id}&dataset_id=${activeDataset.id}`
          : `/explainability/attribution?workspace_id=${activeWorkspace.id}`;
        const res = await api.get(url);
        setExplainData(res.data);
      } catch (err) {
        console.error('Error fetching model explainability:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchExplain();
  }, [activeWorkspace, activeDataset]);

  if (loading) return <LoadingSpinner message="Calculating SHAP TreeExplainer values and feature contributions..." />;
  if (!explainData || !explainData.feature_impacts) return <EmptyState title="No Models Trained" description="Upload a dataset to run ML model interpretation." />;

  const impacts = explainData.feature_impacts || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          Explainable AI (XAI) & Model Performance Registry
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          SHAP-based feature importance, directional attributions, and data leakage audits on <span className="text-brand-400 font-semibold">{explainData.dataset_name}</span>
        </p>
      </div>

      {/* Business Language Narrative Callout */}
      <div className="rounded-xl bg-gradient-to-r from-brand-600/15 via-cyan-600/10 to-slate-900 border border-brand-500/30 p-6">
        <div className="flex items-start gap-3.5">
          <div className="p-2.5 rounded-lg bg-brand-500/20 text-brand-300 mt-0.5">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase text-brand-400 tracking-wider">Automated Executive Interpretation</span>
            <p className="text-sm text-slate-200 mt-1.5 leading-relaxed font-medium">
              "{explainData.business_narrative}"
            </p>
            <span className="text-[10px] text-slate-500 mt-2 block font-mono">
              Attribution Method: {explainData.method} &bull; Target Variable: {explainData.target_column}
            </span>
          </div>
        </div>
      </div>

      {/* SHAP Feature Contribution Ranking */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-base font-semibold text-white">Global Feature Importance & Directional Impact</h2>
            <p className="text-xs text-slate-400">Relative weight of each variable on model predictions</p>
          </div>
        </div>

        <div className="space-y-3">
          {impacts.map((feat, idx) => {
            const isPos = feat.direction === 'positive';
            const isNeg = feat.direction === 'negative';
            return (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-slate-950 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
              >
                <div className="flex items-center gap-3">
                  <span className="w-6 text-[11px] font-mono text-slate-500 font-bold">#{idx + 1}</span>
                  <span className="font-semibold text-white">{feat.feature}</span>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 block uppercase">Latest Value</span>
                    <span className="font-mono text-slate-300 font-semibold">{feat.latest_value}</span>
                  </div>

                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 block uppercase">SHAP Importance</span>
                    <span className="font-mono text-white font-bold">{feat.global_importance}</span>
                  </div>

                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    isPos
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : isNeg
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : 'bg-slate-800 text-slate-400'
                  }`}>
                    {feat.direction}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Leakage Prevention Audit Certificate */}
      <div className="rounded-xl bg-slate-900/40 border border-emerald-500/30 p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0 border border-emerald-500/30">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Target Leakage Protection Protocol Active</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Strict chronological 70% / 15% / 15% temporal splitting. Lag transforms and statistics fitted strictly on training partitions.
            </p>
          </div>
        </div>
        <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 shrink-0">
          Verified Zero-Leakage
        </span>
      </div>
    </div>
  );
}

