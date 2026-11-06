import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  FileText,
  Percent,
  Layers,
  Sparkles
} from 'lucide-react';

export default function DataQuality() {
  const { activeDataset } = useAuth();
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeDataset) return;
    const fetchQuality = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/datasets/${activeDataset.id}`);
        setDetails(res.data);
      } catch (err) {
        console.error('Error fetching data quality:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchQuality();
  }, [activeDataset]);

  if (loading) return <LoadingSpinner message="Auditing dataset health and dimensions..." />;
  if (!details || !details.quality_report) return <EmptyState title="No Dataset Selected" description="Upload or select a dataset to inspect data quality." />;

  const report = details.quality_report;
  const grade = report.grade || 'A';

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          Data Quality & Hygiene Audit
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Automated multidimensional validation for <span className="text-brand-400 font-semibold">{details.name}</span>
        </p>
      </div>

      {/* Main Score & Quality Pillars */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Score Card */}
        <div className="rounded-xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800/80 p-6 flex flex-col justify-between items-center text-center">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Overall Health Rating
            </span>
            <div className="mt-4 flex items-center justify-center">
              <div className="w-32 h-32 rounded-full border-4 border-emerald-500/30 flex flex-col items-center justify-center bg-emerald-500/10 shadow-lg shadow-emerald-500/10">
                <span className="text-4xl font-extrabold text-emerald-400">{report.overall_score}%</span>
                <span className="text-xs font-bold text-slate-300 mt-0.5">Grade {grade}</span>
              </div>
            </div>
          </div>

          <div className="mt-6 w-full pt-4 border-t border-slate-800 text-xs text-slate-400 flex justify-between">
            <span>Rows: <strong className="text-white">{details.row_count.toLocaleString()}</strong></span>
            <span>Columns: <strong className="text-white">{details.col_count}</strong></span>
          </div>
        </div>

        {/* 4 Pillars Breakdown (2 cols) */}
        <div className="lg:col-span-2 rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
          <h2 className="text-base font-semibold text-white mb-1">Quality Assessment Dimensions</h2>
          <p className="text-xs text-slate-400 mb-6">4-factor weighted integrity calculation</p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-semibold text-slate-300">Completeness</span>
                <span className="text-xs font-bold text-emerald-400">{report.completeness_score}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden mb-2">
                <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${report.completeness_score}%` }} />
              </div>
              <span className="text-[11px] text-slate-500">
                {report.missing_cells} missing null cells detected
              </span>
            </div>

            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-semibold text-slate-300">Uniqueness</span>
                <span className="text-xs font-bold text-brand-400">{report.uniqueness_score}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden mb-2">
                <div className="h-full bg-brand-400 rounded-full" style={{ width: `${report.uniqueness_score}%` }} />
              </div>
              <span className="text-[11px] text-slate-500">
                {report.duplicate_rows} duplicate record rows identified
              </span>
            </div>

            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-semibold text-slate-300">Validity</span>
                <span className="text-xs font-bold text-indigo-400">{report.validity_score}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden mb-2">
                <div className="h-full bg-indigo-400 rounded-full" style={{ width: `${report.validity_score}%` }} />
              </div>
              <span className="text-[11px] text-slate-500">
                Format, date sequence & range conformance
              </span>
            </div>

            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs font-semibold text-slate-300">Consistency & Outliers</span>
                <span className="text-xs font-bold text-cyan-400">{report.consistency_score}%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden mb-2">
                <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${report.consistency_score}%` }} />
              </div>
              <span className="text-[11px] text-slate-500">
                {report.outlier_count} statistical outlier values isolated
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Issues & Remediations */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
        <h2 className="text-base font-semibold text-white mb-1 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-amber-400" />
          Detected Data Hygiene Alerts ({report.issues?.length || 0})
        </h2>
        <p className="text-xs text-slate-400 mb-6">
          Automated recommendations to improve statistical reliability prior to training predictive models
        </p>

        {report.issues && report.issues.length > 0 ? (
          <div className="space-y-3">
            {report.issues.map((issue, idx) => (
              <div
                key={idx}
                className="p-4 rounded-lg bg-slate-950 border border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-3"
              >
                <div className="flex items-start gap-3">
                  <div className={`mt-0.5 p-1.5 rounded-md ${
                    issue.severity === 'high' ? 'bg-rose-500/10 text-rose-400' : 'bg-amber-500/10 text-amber-400'
                  }`}>
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-white flex items-center gap-2">
                      {issue.message}
                      <span className="text-[10px] uppercase font-bold px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                        {issue.severity}
                      </span>
                    </h4>
                    <p className="text-xs text-slate-400 mt-1">
                      <strong className="text-slate-300">Action:</strong> {issue.remedy}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[11px] font-mono text-slate-500">{issue.type}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-slate-950/40 rounded-lg border border-slate-800/50">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <p className="text-xs font-medium text-slate-300">Clean dataset! No critical data hygiene issues detected.</p>
          </div>
        )}
      </div>
    </div>
  );
}

