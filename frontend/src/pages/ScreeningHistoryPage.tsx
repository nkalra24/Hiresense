import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  FileSpreadsheet,
  Download,
  Trash2,
  PlusCircle,
  ArrowRight,
  Clock,
  CheckCircle2,
  Search
} from 'lucide-react';
import { getScreenings, deleteScreening, getExportCsvUrl, getExportPdfUrl } from '../services/api';
import { ScreeningSession } from '../types';

export const ScreeningHistoryPage: React.FC = () => {
  const [screenings, setScreenings] = useState<ScreeningSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await getScreenings();
      setScreenings(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this screening session and all associated files?')) return;
    try {
      await deleteScreening(id);
      setScreenings((prev) => prev.filter((s) => s.id !== id));
    } catch (e) {
      alert('Failed to delete session');
    }
  };

  const filtered = screenings.filter((s) => {
    if (!search) return true;
    const term = search.toLowerCase();
    return s.job_title.toLowerCase().includes(term) || s.department?.toLowerCase().includes(term);
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Screening History</h1>
          <p className="text-sm text-slate-500">
            All past candidate ranking sessions and evaluated positions.
          </p>
        </div>

        <Link
          to="/screenings/new"
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition-colors"
        >
          <PlusCircle className="h-4 w-4" />
          <span>New Screening</span>
        </Link>
      </div>

      {/* Search Input */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by job title or department..."
          className="w-full rounded-lg border border-slate-200 bg-white pl-9 pr-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      {/* History Table */}
      <div className="rounded-xl border border-slate-200/80 bg-white shadow-subtle overflow-hidden">
        {loading ? (
          <div className="py-20 text-center">
            <div className="mx-auto h-7 w-7 animate-spin rounded-full border-3 border-indigo-600 border-t-transparent mb-2" />
            <p className="text-xs text-slate-500">Loading screening sessions...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-20 text-center">
            <FileText className="mx-auto h-9 w-9 text-slate-300 mb-2" />
            <p className="text-sm font-semibold text-slate-700">No screening sessions found</p>
            <p className="text-xs text-slate-400 mt-1">Start your first AI resume screening session now.</p>
            <Link
              to="/screenings/new"
              className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow hover:bg-indigo-700"
            >
              <span>Create Screening</span>
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/75 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-4">Session #</th>
                  <th className="py-3 px-4">Job Title</th>
                  <th className="py-3 px-4">Resumes</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-slate-500">#{s.id}</td>
                    <td className="py-3.5 px-4">
                      <Link
                        to={`/screenings/${s.id}`}
                        className="font-bold text-slate-900 hover:text-indigo-600 transition-colors"
                      >
                        {s.job_title}
                      </Link>
                      {s.department && (
                        <span className="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500">
                          {s.department}
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">
                      {s.processed_resumes} of {s.total_resumes} analyzed
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize ${
                          s.processing_status === 'completed'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : s.processing_status === 'processing'
                            ? 'bg-blue-50 text-blue-700 border border-blue-200 animate-pulse'
                            : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}
                      >
                        {s.processing_status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {new Date(s.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <a
                          href={getExportCsvUrl(s.id)}
                          download
                          title="Download CSV"
                          className="rounded p-1 text-slate-400 hover:text-emerald-600"
                        >
                          <FileSpreadsheet className="h-4 w-4" />
                        </a>
                        <a
                          href={getExportPdfUrl(s.id)}
                          download
                          title="Download PDF"
                          className="rounded p-1 text-slate-400 hover:text-indigo-600"
                        >
                          <FileText className="h-4 w-4" />
                        </a>
                        <Link
                          to={`/screenings/${s.id}`}
                          className="inline-flex items-center gap-1 font-semibold text-indigo-600 hover:text-indigo-800 ml-1"
                        >
                          <span>Results</span>
                          <ArrowRight className="h-3 w-3" />
                        </Link>
                        <button
                          onClick={() => handleDelete(s.id)}
                          title="Delete Session"
                          className="rounded p-1 text-slate-400 hover:text-red-600 ml-1"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
