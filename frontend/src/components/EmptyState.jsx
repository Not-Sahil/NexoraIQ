import React from 'react';
import { Database, UploadCloud } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function EmptyState({
  title = "No Data Available",
  description = "Upload a CSV or Excel business dataset, or seed benchmark data to unlock analytics.",
  actionText = "Manage Datasets",
  actionLink = "/data"
}) {
  return (
    <div className="rounded-xl border border-dashed border-slate-800 bg-slate-900/30 p-12 text-center max-w-xl mx-auto my-8">
      <div className="w-12 h-12 rounded-full bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-brand-400 mx-auto mb-4">
        <Database className="w-6 h-6" />
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-sm text-slate-400 mb-6">{description}</p>
      {actionLink && (
        <Link
          to={actionLink}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-sm font-medium transition-colors shadow-lg shadow-brand-600/20"
        >
          <UploadCloud className="w-4 h-4" />
          {actionText}
        </Link>
      )}
    </div>
  );
}

