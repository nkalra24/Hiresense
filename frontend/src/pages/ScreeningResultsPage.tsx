import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Download,
  FileSpreadsheet,
  FileText,
  Search,
  Filter,
  ArrowUpDown,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  ChevronRight,
  Trash2,
  AlertCircle
} from 'lucide-react';
import {
  getScreening,
  getScreeningResults,
  getScreeningStatus,
  deleteScreening,
  getExportCsvUrl,
  getExportPdfUrl
} from '../services/api';
import { ScreeningSession, ScreeningResult } from '../types';

export const ScreeningResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const sessionId = Number(id);

  const [session, setSession] = useState<ScreeningSession | null>(null);
  const [results, setResults] = useState<ScreeningResult[]>([]);
  const [statusData, setStatusData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Filters & Search
  const [searchTerm, setSearchTerm] = useState('');
  const [scoreFilter, setScoreFilter] = useState<'all' | 'high' | 'mid' | 'low'>('all');
  const [overqualFilter, setOverqualFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'score_desc' | 'score_asc' | 'exp_desc'>('score_desc');

  useEffect(() => {
    if (!sessionId) return;
    loadSessionAndResults();
  }, [sessionId]);

  // Polling mechanism when processing
  useEffect(() => {
    if (!session || (session.processing_status !== 'queued' && session.processing_status !== 'processing')) {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const s = await getScreeningStatus(sessionId);
        setStatusData(s);
        if (s.processing_status === 'completed' || s.processing_status === 'failed') {
          clearInterval(interval);
          loadSessionAndResults();
        }
      } catch (e) {
        console.error(e);
      }
    }, 2500);

    return () => clearInterval(interval);
  }, [session, sessionId]);

  const loadSessionAndResults = async () => {
    try {
      setLoading(true);
      const [sess, resList] = await Promise.all([
        getScreening(sessionId),
        getScreeningResults(sessionId),
      ]);
      setSession(sess);
      setResults(resList);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this screening session and its files?')) return;
    try {
      await deleteScreening(sessionId);
      navigate('/screenings');
    } catch (e) {
      alert('Failed to delete screening session');
    }
  };

  // Filter & Sort logic
  const filteredResults = results
    .filter((r) => {
      if (searchTerm) {
        const term = searchTerm.toLowerCase();
        const matchesName = r.candidate_name.toLowerCase().includes(term);
        const matchesEmail = r.candidate_email?.toLowerCase().includes(term);
        const matchesSkill = r.matched_skills.some((s) => s.toLowerCase().includes(term));
        if (!matchesName && !matchesEmail && !matchesSkill) return false;
      }

      if (scoreFilter === 'high' && r.final_match_score < 75) return false;
      if (scoreFilter === 'mid' && (r.final_match_score < 50 || r.final_match_score >= 75)) return false;
      if (scoreFilter === 'low' && r.final_match_score >= 50) return false;

      if (overqualFilter !== 'all') {
        if (!r.overqualification_status.toLowerCase().includes(overqualFilter.toLowerCase())) {
          return false;
        }
      }

      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'score_asc') return a.final_match_score - b.final_match_score;
      if (sortBy === 'exp_desc') return b.relevant_experience - a.relevant_experience;
      return b.final_match_score - a.final_match_score;
    });

  if (loading && !session) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-9 w-9 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
          <p className="text-sm font-medium text-slate-500">Loading screening results...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center text-red-700">
        <AlertCircle className="mx-auto h-8 w-8 text-red-500 mb-2" />
        <p className="font-semibold">Screening session not found</p>
        <Link to="/screenings" className="mt-3 inline-block text-xs font-semibold underline">
          Back to history
        </Link>
      </div>
    );
  }

  const avgScore =
    results.length > 0
      ? (results.reduce((acc, r) => acc + r.final_match_score, 0) / results.length).toFixed(1)
      : '0.0';
  const highFitCount = results.filter((r) => r.final_match_score >= 75).length;

  return (
    <div className="space-y-6">
      {/* Processing Status Banner if Active */}
      {(session.processing_status === 'queued' || session.processing_status === 'processing') && (
        <div className="rounded-xl border border-indigo-200 bg-indigo-50/70 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
            <div>
              <p className="text-xs font-bold text-indigo-900">
                AI Pipeline Processing in Progress ({session.processed_resumes}/{session.total_resumes} Resumes Analyzed)
              </p>
              <p className="text-[11px] text-indigo-700">
                Extracting structured qualifications and computing vector embeddings. This view refreshes automatically.
              </p>
            </div>
          </div>
          <button
            onClick={loadSessionAndResults}
            className="rounded-lg bg-white px-3 py-1.5 text-xs font-semibold text-indigo-700 border border-indigo-200 hover:bg-indigo-50"
          >
            Refresh Now
          </button>
        </div>
      )}

      {session.processing_status === 'failed' && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-bold text-red-900">Screening could not process any resumes.</p>
            <p className="text-[11px] text-red-700">
              {session.failed_resumes} of {session.total_resumes} resume(s) failed. Check the uploaded files and try again.
            </p>
          </div>
          <button
            onClick={loadSessionAndResults}
            className="shrink-0 rounded-lg bg-white px-3 py-1.5 text-xs font-semibold text-red-700 border border-red-200 hover:bg-red-50"
          >
            Refresh Now
          </button>
        </div>
      )}

      {/* Top Header Card */}
      <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-slate-900">{session.job_title}</h1>
              {session.department && (
                <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                  {session.department}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Screening Session #{session.id} • Created on {new Date(session.created_at).toLocaleDateString()}
            </p>
          </div>

          {/* Export & Action Buttons */}
          <div className="flex items-center gap-2">
            <a
              href={getExportCsvUrl(sessionId)}
              download
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-subtle"
            >
              <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600" />
              <span>Export CSV</span>
            </a>

            <a
              href={getExportPdfUrl(sessionId)}
              download
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-subtle"
            >
              <FileText className="h-3.5 w-3.5 text-indigo-600" />
              <span>Export PDF Report</span>
            </a>

            <button
              onClick={handleDelete}
              className="rounded-lg border border-slate-200 p-2 text-slate-400 hover:text-red-600 hover:border-red-200 transition-colors"
              title="Delete Session"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Aggregate Stats Ribbon */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 pt-1">
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Total Uploaded</span>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{session.total_resumes} Resumes</p>
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Successfully Ranked</span>
            <p className="text-lg font-bold text-emerald-600 mt-0.5">{results.length} Candidates</p>
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Average Fit Score</span>
            <p className="text-lg font-bold text-slate-900 mt-0.5">{avgScore}%</p>
          </div>
          <div>
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">High-Fit (≥75%)</span>
            <p className="text-lg font-bold text-indigo-600 mt-0.5">{highFitCount} Candidates</p>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200/80 shadow-subtle text-xs">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search candidate name, email, or skill..."
            className="w-full rounded-lg border border-slate-200 pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        {/* Score filter */}
        <div className="flex items-center gap-2">
          <span className="text-slate-400 shrink-0 font-medium">Fit Range:</span>
          <select
            value={scoreFilter}
            onChange={(e: any) => setScoreFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-700 focus:border-indigo-500 focus:outline-none"
          >
            <option value="all">All Scores</option>
            <option value="high">High Fit (≥75%)</option>
            <option value="mid">Moderate Fit (50-74%)</option>
            <option value="low">Low Fit (&lt;50%)</option>
          </select>
        </div>

        {/* Overqualification filter */}
        <div className="flex items-center gap-2">
          <span className="text-slate-400 shrink-0 font-medium">Overqualification:</span>
          <select
            value={overqualFilter}
            onChange={(e) => setOverqualFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-700 focus:border-indigo-500 focus:outline-none"
          >
            <option value="all">All Signals</option>
            <option value="Potentially Overqualified">Potentially Overqualified</option>
            <option value="Experience Exceeds">Experience Exceeds</option>
            <option value="No Clear">Standard Fit</option>
          </select>
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <ArrowUpDown className="h-3.5 w-3.5 text-slate-400" />
          <select
            value={sortBy}
            onChange={(e: any) => setSortBy(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs text-slate-700 focus:border-indigo-500 focus:outline-none font-semibold"
          >
            <option value="score_desc">Highest Score First</option>
            <option value="score_asc">Lowest Score First</option>
            <option value="exp_desc">Most Experience First</option>
          </select>
        </div>
      </div>

      {/* Candidate Ranking Table */}
      <div className="rounded-xl border border-slate-200/80 bg-white shadow-subtle overflow-hidden">
        {filteredResults.length === 0 ? (
          <div className="py-16 text-center">
            <CheckCircle2 className="mx-auto h-8 w-8 text-slate-300 mb-2" />
            <p className="text-sm font-semibold text-slate-700">No candidates match your current filter</p>
            <p className="text-xs text-slate-400 mt-1">Try resetting the score range or search keyword.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/75 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-4 w-12 text-center">Rank</th>
                  <th className="py-3 px-4">Candidate Profile</th>
                  <th className="py-3 px-4">Match Score</th>
                  <th className="py-3 px-4">Required Skills</th>
                  <th className="py-3 px-4">Experience</th>
                  <th className="py-3 px-4">Overqualification Signal</th>
                  <th className="py-3 px-4">Recruiter Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredResults.map((cand, index) => {
                  const score = cand.final_match_score;
                  const reqScore = cand.component_scores.required_skills;
                  const isTop = index === 0;

                  return (
                    <tr
                      key={cand.id}
                      className="hover:bg-indigo-50/20 transition-colors group"
                    >
                      {/* Rank # */}
                      <td className="py-4 px-4 text-center font-bold text-slate-700">
                        {isTop ? (
                          <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-amber-100 text-amber-800 text-[11px] font-bold">
                            1
                          </span>
                        ) : (
                          `#${index + 1}`
                        )}
                      </td>

                      {/* Name & Contact */}
                      <td className="py-4 px-4">
                        <Link
                          to={`/screenings/${sessionId}/candidates/${cand.candidate_id}`}
                          className="font-bold text-slate-900 group-hover:text-indigo-600 transition-colors"
                        >
                          {cand.candidate_name}
                        </Link>
                        {cand.candidate_email && (
                          <p className="text-[11px] text-slate-400 mt-0.5">{cand.candidate_email}</p>
                        )}
                      </td>

                      {/* Overall Fit Score */}
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <div
                            className={`flex h-8 w-11 items-center justify-center rounded-lg font-bold text-xs ${
                              score >= 75
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : score >= 50
                                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                                : 'bg-slate-100 text-slate-600'
                            }`}
                          >
                            {score.toFixed(0)}%
                          </div>
                          <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden hidden sm:block">
                            <div
                              className={`h-full rounded-full ${
                                score >= 75 ? 'bg-emerald-500' : score >= 50 ? 'bg-indigo-600' : 'bg-slate-400'
                              }`}
                              style={{ width: `${score}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      {/* Required Skills Match & Missing */}
                      <td className="py-4 px-4">
                        <div className="space-y-1">
                          <span className="font-semibold text-slate-700">{reqScore.toFixed(0)}% Coverage</span>
                          {cand.missing_required_skills.length > 0 ? (
                            <div className="flex flex-wrap gap-1 max-w-[200px]">
                              {cand.missing_required_skills.slice(0, 2).map((m, idx) => (
                                <span
                                  key={idx}
                                  className="rounded bg-rose-50 px-1.5 py-0.5 text-[10px] text-rose-700 border border-rose-100"
                                >
                                  Missing {m}
                                </span>
                              ))}
                              {cand.missing_required_skills.length > 2 && (
                                <span className="text-[10px] text-slate-400">
                                  +{cand.missing_required_skills.length - 2} more
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="text-[10px] text-emerald-600 font-medium block">
                              ✓ All required skills present
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Relevant Experience */}
                      <td className="py-4 px-4">
                        <span className="font-semibold text-slate-800">
                          {cand.relevant_experience.toFixed(1)} yrs
                        </span>
                      </td>

                      {/* Overqualification Status */}
                      <td className="py-4 px-4">
                        {session.overqualification_enabled ? (
                          <span
                            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${
                              cand.overqualification_status.includes('Potentially Overqualified')
                                ? 'bg-amber-50 text-amber-800 border border-amber-200'
                                : cand.overqualification_status.includes('Experience Exceeds')
                                ? 'bg-blue-50 text-blue-800 border border-blue-200'
                                : 'bg-slate-50 text-slate-600'
                            }`}
                          >
                            {cand.overqualification_status.includes('Overqualified') && (
                              <AlertTriangle className="h-3 w-3 text-amber-600" />
                            )}
                            <span>{cand.overqualification_status}</span>
                          </span>
                        ) : (
                          <span className="text-[11px] text-slate-400">Disabled</span>
                        )}
                      </td>

                      {/* Recruiter Review Badge */}
                      <td className="py-4 px-4">
                        <span
                          className={`rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize ${
                            cand.review_status === 'shortlisted'
                              ? 'bg-emerald-100 text-emerald-800'
                              : cand.review_status === 'under_review'
                              ? 'bg-amber-100 text-amber-800'
                              : cand.review_status === 'rejected'
                              ? 'bg-rose-100 text-rose-800'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {cand.review_status}
                        </span>
                      </td>

                      {/* Action View */}
                      <td className="py-4 px-4 text-right">
                        <Link
                          to={`/screenings/${sessionId}/candidates/${cand.candidate_id}`}
                          className="inline-flex items-center gap-1 font-semibold text-indigo-600 hover:text-indigo-800 group-hover:underline"
                        >
                          <span>Analyze</span>
                          <ChevronRight className="h-3.5 w-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
