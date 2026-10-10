import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Users,
  Target,
  Award,
  ArrowRight,
  PlusCircle,
  Clock,
  CheckCircle2,
  AlertCircle,
  TrendingUp
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { getDashboardStats } from '../services/api';
import { DashboardStats } from '../types';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = () => {
    setLoading(true);
    getDashboardStats()
      .then((data) => {
        setStats(data);
        setError(null);
      })
      .catch((err) => {
        console.error(err);
        setError('Failed to load dashboard metrics from backend.');
      })
      .finally(() => setLoading(false));
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-9 w-9 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
          <p className="text-sm font-medium text-slate-500">Loading screening metrics...</p>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center text-red-700">
        <AlertCircle className="mx-auto h-8 w-8 text-red-500 mb-2" />
        <p className="font-semibold">{error || 'Unable to retrieve statistics'}</p>
        <button
          onClick={loadStats}
          className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Screenings',
      value: stats.total_sessions,
      icon: FileText,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      description: 'Active & completed sessions',
    },
    {
      title: 'Resumes Analyzed',
      value: stats.total_resumes_processed,
      icon: Users,
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
      description: 'Parsed across all jobs',
    },
    {
      title: 'Average Job-Fit Score',
      value: `${stats.average_score}%`,
      icon: Target,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
      description: 'Weighted multi-signal match',
    },
    {
      title: 'High-Fit Candidates',
      value: stats.high_fit_candidates,
      icon: Award,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
      description: 'Match score ≥ 75%',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Recruitment Dashboard</h1>
          <p className="text-sm text-slate-500">
            Real-time candidate ranking analytics and active screening pipeline.
          </p>
        </div>
        <Link
          to="/screenings/new"
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition-all focus:ring-2 focus:ring-indigo-500"
        >
          <PlusCircle className="h-4 w-4" />
          <span>Start New Screening</span>
        </Link>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div
            key={card.title}
            className="rounded-xl border border-slate-200/80 bg-white p-5 shadow-subtle hover:shadow-card transition-shadow"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {card.title}
              </span>
              <div className={`rounded-lg p-2.5 ${card.bg}`}>
                <card.icon className={`h-5 w-5 ${card.color}`} />
              </div>
            </div>
            <div className="mt-4">
              <span className="text-2xl font-bold text-slate-900">{card.value}</span>
              <p className="mt-1 text-xs text-slate-400">{card.description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts & Distribution Section */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Score Distribution Chart */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Candidate Match-Score Distribution</h2>
              <p className="text-xs text-slate-500">Volume of evaluated resumes grouped by fit score bracket</p>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <TrendingUp className="h-4 w-4 text-indigo-500" />
              <span>Real database records</span>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="range" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip
                  cursor={{ fill: '#f8fafc' }}
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {stats.distribution.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={index >= 3 ? '#4f46e5' : index === 2 ? '#6366f1' : '#cbd5e1'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Screening Summary / CTA */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">AI Resume Matching</h2>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">
              Upload multiple resumes in PDF or DOCX format to instantly extract candidate skills, work experience, calculate semantic fit, and detect potential overqualification.
            </p>

            <div className="mt-6 space-y-3">
              <div className="flex items-center gap-2.5 text-xs text-slate-700">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                <span>35% Required Skills & 25% Semantic Vector Match</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-slate-700">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                <span>Demographic-blind, fair, explainable rankings</span>
              </div>
              <div className="flex items-center gap-2.5 text-xs text-slate-700">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                <span>One-click PDF & CSV export for recruitment reports</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100">
            <Link
              to="/screenings/new"
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-50 py-2.5 text-xs font-semibold text-indigo-700 border border-indigo-200/70 hover:bg-indigo-100 transition-colors"
            >
              <span>Launch New Screening</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Tables Row: Recent Screenings & Recent Candidate Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Recent Screening Sessions (2 cols) */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Recent Screening Sessions</h2>
              <p className="text-xs text-slate-500">Latest job positions submitted for evaluation</p>
            </div>
            <Link to="/screenings" className="text-xs font-semibold text-indigo-600 hover:text-indigo-800">
              View All
            </Link>
          </div>

          {stats.recent_screenings.length === 0 ? (
            <div className="py-12 text-center">
              <FileText className="mx-auto h-8 w-8 text-slate-300 mb-2" />
              <p className="text-sm font-medium text-slate-600">No screening sessions yet</p>
              <p className="text-xs text-slate-400 mt-1">Start by creating your first job screening session.</p>
              <Link
                to="/screenings/new"
                className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-700"
              >
                <span>Create Screening</span>
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider">
                    <th className="pb-3">Job Title</th>
                    <th className="pb-3">Resumes</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Date</th>
                    <th className="pb-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {stats.recent_screenings.map((session) => (
                    <tr key={session.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 font-semibold text-slate-900">
                        {session.job_title}
                        {session.department && (
                          <span className="ml-2 rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-normal text-slate-500">
                            {session.department}
                          </span>
                        )}
                      </td>
                      <td className="py-3 text-slate-600">
                        {session.processed_resumes}/{session.total_resumes} analyzed
                      </td>
                      <td className="py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium capitalize ${
                            session.processing_status === 'completed'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : session.processing_status === 'processing'
                              ? 'bg-blue-50 text-blue-700 border border-blue-200 animate-pulse'
                              : 'bg-amber-50 text-amber-700 border border-amber-200'
                          }`}
                        >
                          {session.processing_status}
                        </span>
                      </td>
                      <td className="py-3 text-slate-500">
                        {new Date(session.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 text-right">
                        <Link
                          to={`/screenings/${session.id}`}
                          className="inline-flex items-center gap-1 font-semibold text-indigo-600 hover:text-indigo-800"
                        >
                          <span>Results</span>
                          <ArrowRight className="h-3 w-3" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Recent Candidate Activity (1 col) */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Candidate Activity</h2>
              <p className="text-xs text-slate-500">Recruiter decisions & status</p>
            </div>
            <Clock className="h-4 w-4 text-slate-400" />
          </div>

          {stats.recent_activity.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              No recent candidate reviews recorded yet.
            </div>
          ) : (
            <div className="space-y-3.5">
              {stats.recent_activity.map((act, idx) => (
                <div key={idx} className="flex items-start justify-between border-b border-slate-50 pb-2.5">
                  <div>
                    <p className="text-xs font-semibold text-slate-900">{act.candidate_name}</p>
                    <p className="text-[11px] text-slate-500 truncate max-w-[160px]">{act.job_title}</p>
                  </div>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize ${
                      act.review_status === 'shortlisted'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                        : act.review_status === 'under_review'
                        ? 'bg-amber-50 text-amber-700 border border-amber-100'
                        : act.review_status === 'rejected'
                        ? 'bg-rose-50 text-rose-700 border border-rose-100'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {act.review_status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
