import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  UploadCloud,
  Database,
  CheckCircle2,
  Sparkles,
  FileSpreadsheet,
  Table as TableIcon,
  Layers,
  ArrowUpRight
} from 'lucide-react';

export default function DataManagement() {
  const { activeWorkspace, datasets, activeDataset, switchDataset, refreshDatasets } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [datasetName, setDatasetName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [datasetDetails, setDatasetDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  useEffect(() => {
    if (!activeDataset) return;
    const fetchDetails = async () => {
      setLoadingDetails(true);
      try {
        const res = await api.get(`/datasets/${activeDataset.id}`);
        setDatasetDetails(res.data);
      } catch (err) {
        console.error('Error fetching dataset details:', err);
      } finally {
        setLoadingDetails(false);
      }
    };
    fetchDetails();
  }, [activeDataset]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile || !activeWorkspace) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('workspace_id', activeWorkspace.id);
    if (datasetName) formData.append('name', datasetName);

    try {
      await api.post('/datasets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSelectedFile(null);
      setDatasetName('');
      await refreshDatasets();
    } catch (err) {
      alert(`Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleSeedBenchmarks = async () => {
    if (!activeWorkspace) return;
    setSeeding(true);
    try {
      await api.post(`/datasets/seed-demo-datasets?workspace_id=${activeWorkspace.id}`);
      await refreshDatasets();
    } catch (err) {
      alert(`Seeding failed: ${err.message}`);
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Universal Data Management
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Upload CSV/Excel business datasets, review schema inferences, and inspect quality scores
          </p>
        </div>

        <button
          onClick={handleSeedBenchmarks}
          disabled={seeding}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-semibold shadow-sm transition-colors"
        >
          <Sparkles className="w-4 h-4" />
          <span>{seeding ? 'Seeding Benchmarks...' : 'Seed Benchmark Datasets'}</span>
        </button>
      </div>

      {/* Upload & Dataset Selector Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Card */}
        <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
          <h2 className="text-base font-semibold text-white mb-2 flex items-center gap-2">
            <UploadCloud className="w-5 h-5 text-brand-400" />
            Upload New Business Dataset
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            Supports CSV, TSV, and Excel (.xlsx, .xls) up to 100MB.
          </p>

          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Dataset Label (Optional)</label>
              <input
                type="text"
                value={datasetName}
                onChange={(e) => setDatasetName(e.target.value)}
                placeholder="e.g. Q4 Regional Omnichannel Sales"
                className="w-full rounded-lg bg-slate-950 border border-slate-800 px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
            </div>

            <div className="border border-dashed border-slate-700 rounded-lg p-6 text-center hover:border-brand-500 transition-colors cursor-pointer bg-slate-950/50">
              <input
                type="file"
                id="file-upload"
                accept=".csv,.xlsx,.xls,.txt"
                onChange={(e) => setSelectedFile(e.target.files[0])}
                className="hidden"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <FileSpreadsheet className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <span className="text-xs font-medium text-slate-300 block">
                  {selectedFile ? selectedFile.name : 'Click to browse files'}
                </span>
                <span className="text-[10px] text-slate-500 mt-1 block">
                  {selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB` : 'CSV or Excel formats'}
                </span>
              </label>
            </div>

            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="w-full py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-brand-600/20 transition-all"
            >
              {uploading ? 'Validating & Ingesting...' : 'Upload & Audit Dataset'}
            </button>
          </form>
        </div>

        {/* Available Datasets in Workspace (2 cols) */}
        <div className="lg:col-span-2 rounded-xl bg-slate-900/70 border border-slate-800/80 p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-semibold text-white mb-2 flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              Active Workspace Datasets ({datasets.length})
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              Select a dataset to activate it across all predictive and intelligence models.
            </p>

            <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
              {datasets.map((ds) => {
                const isSelected = activeDataset?.id === ds.id;
                return (
                  <div
                    key={ds.id}
                    onClick={() => switchDataset(ds.id)}
                    className={`p-3.5 rounded-lg border text-xs cursor-pointer flex items-center justify-between transition-all ${
                      isSelected
                        ? 'bg-brand-500/10 border-brand-500/40 text-brand-200'
                        : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-2.5 h-2.5 rounded-full ${isSelected ? 'bg-brand-400 ring-4 ring-brand-500/20' : 'bg-slate-600'}`} />
                      <div>
                        <p className="font-semibold text-white">{ds.name}</p>
                        <p className="text-[11px] text-slate-500">
                          {ds.row_count.toLocaleString()} rows &times; {ds.col_count} columns &bull; {(ds.file_size_bytes / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 font-medium text-[11px] border border-emerald-500/20">
                        Score: {ds.quality_score}%
                      </span>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-brand-400" />}
                    </div>
                  </div>
                );
              })}

              {datasets.length === 0 && (
                <p className="text-xs text-slate-500 py-6 text-center">
                  No datasets uploaded yet. Click "Seed Benchmark Datasets" above to populate immediate data.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Dataset Schema & Preview Section */}
      {loadingDetails ? (
        <LoadingSpinner message="Loading dataset schema and records..." />
      ) : datasetDetails ? (
        <div className="space-y-6">
          {/* Inferred Column Mapping Grid */}
          <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
            <h2 className="text-base font-semibold text-white mb-1 flex items-center gap-2">
              <TableIcon className="w-5 h-5 text-brand-400" />
              Inferred Column Schema & Semantic Role Mapping
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              Columns are automatically identified by statistical type and mapped to standard business semantic roles.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {datasetDetails.columns?.map((col, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                  <span className="font-semibold text-white truncate block">{col.column_name}</span>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 uppercase font-mono">
                      {col.inferred_type}
                    </span>
                    <span className="text-[11px] font-medium text-brand-400">
                      {col.mapped_semantic_role ? `→ ${col.mapped_semantic_role}` : 'unmapped'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Data Preview Table */}
          <div className="rounded-xl bg-slate-900/70 border border-slate-800/80 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-semibold text-white">Live Data Sample (First 20 Records)</h2>
                <p className="text-xs text-slate-400">Raw validated records stored in workspace</p>
              </div>
            </div>

            <div className="overflow-x-auto rounded-lg border border-slate-800 max-h-96">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider sticky top-0 border-b border-slate-800">
                  <tr>
                    {datasetDetails.columns?.map((col, i) => (
                      <th key={i} className="px-4 py-3 font-semibold">{col.column_name}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 bg-slate-900/40 text-slate-300">
                  {datasetDetails.preview?.map((row, rIdx) => (
                    <tr key={rIdx} className="hover:bg-slate-800/30 transition-colors">
                      {datasetDetails.columns?.map((col, cIdx) => (
                        <td key={cIdx} className="px-4 py-2.5 whitespace-nowrap font-mono text-[11px]">
                          {row[col.column_name] !== null && row[col.column_name] !== undefined
                            ? String(row[col.column_name])
                            : <span className="text-slate-600">null</span>
                          }
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

