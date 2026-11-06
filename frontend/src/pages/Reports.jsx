import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import {
  FileSpreadsheet,
  FileText,
  Download,
  CheckCircle2,
  Calendar,
  Sparkles,
  ArrowRight
} from 'lucide-react';

export default function Reports() {
  const { activeWorkspace, activeDataset } = useAuth();
  const [generating, setGenerating] = useState(false);
  const [generatedReport, setGeneratedReport] = useState(null);
  const [reportFormat, setReportFormat] = useState('excel');

  const handleGenerateReport = async () => {
    if (!activeWorkspace) return;
    setGenerating(true);
    setGeneratedReport(null);
    try {
      const res = await api.post(`/reports/generate?workspace_id=${activeWorkspace.id}&report_format=${reportFormat}`);
      setGeneratedReport(res.data);
    } catch (err) {
      alert(`Report generation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          Executive Decision Reports & Data Export
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Generate comprehensive audit workbooks and board-ready PDF executive briefs
        </p>
      </div>

      {/* Generator Card */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-8 shadow-sm">
        <div className="max-w-2xl mx-auto text-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-cyan-500 flex items-center justify-center mx-auto text-white shadow-xl shadow-brand-500/20">
            <FileSpreadsheet className="w-8 h-8" />
          </div>

          <h2 className="text-xl font-bold text-white">Generate Analytical Export Package</h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            Exports verified KPIs, walk-forward forecast models, prediction intervals, multi-method anomaly logs,
            and prioritized business recommendations into an interconnected enterprise file.
          </p>

          {/* Format Selector Radio */}
          <div className="grid grid-cols-2 gap-4 max-w-md mx-auto pt-4">
            <div
              onClick={() => setReportFormat('excel')}
              className={`p-4 rounded-xl border text-left cursor-pointer transition-all ${
                reportFormat === 'excel'
                  ? 'bg-brand-500/10 border-brand-500/50 text-white shadow-sm'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <FileSpreadsheet className="w-6 h-6 text-emerald-400 mb-2" />
              <h3 className="text-xs font-bold text-white">Excel Workbook (.xlsx)</h3>
              <p className="text-[11px] text-slate-400 mt-1">Multi-tab financial & model tables</p>
            </div>

            <div
              onClick={() => setReportFormat('pdf')}
              className={`p-4 rounded-xl border text-left cursor-pointer transition-all ${
                reportFormat === 'pdf'
                  ? 'bg-brand-500/10 border-brand-500/50 text-white shadow-sm'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
              }`}
            >
              <FileText className="w-6 h-6 text-rose-400 mb-2" />
              <h3 className="text-xs font-bold text-white">PDF Executive Brief (.pdf)</h3>
              <p className="text-[11px] text-slate-400 mt-1">Board-ready stylized audit document</p>
            </div>
          </div>

          <div className="pt-4">
            <button
              onClick={handleGenerateReport}
              disabled={generating}
              className="px-6 py-3 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-brand-600/25 transition-all inline-flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>{generating ? 'Compiling Report...' : `Compile & Export ${reportFormat.toUpperCase()}`}</span>
            </button>
          </div>
        </div>

        {/* Download Callout */}
        {generatedReport && (
          <div className="mt-8 p-6 rounded-xl bg-emerald-500/10 border border-emerald-500/30 max-w-xl mx-auto flex items-center justify-between animate-fadeIn">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
              <div className="text-left">
                <p className="text-xs font-bold text-white">{generatedReport.message}</p>
                <p className="text-[11px] text-slate-400 font-mono mt-0.5">{generatedReport.filename}</p>
              </div>
            </div>

            <a
              href={generatedReport.download_url}
              download
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md transition-colors"
            >
              <Download className="w-4 h-4" />
              Download
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

