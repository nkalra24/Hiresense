import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Mail,
  Phone,
  Briefcase,
  GraduationCap,
  Award,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  Save,
  Check,
  ShieldAlert,
  Sparkles
} from 'lucide-react';
import { getCandidateSessionDetail, updateRecruiterReview } from '../services/api';

export const CandidateDetailPage: React.FC = () => {
  const { screeningId, candidateId } = useParams<{ screeningId: string; candidateId: string }>();
  const sId = Number(screeningId);
  const cId = Number(candidateId);

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Recruiter Review state
  const [reviewStatus, setReviewStatus] = useState<string>('pending');
  const [recruiterNotes, setRecruiterNotes] = useState<string>('');
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saving, setSaving] = useState(false);

  // Tab state (Analysis vs Full Extracted Resume)
  const [activeTab, setActiveTab] = useState<'analysis' | 'resume'>('analysis');

  useEffect(() => {
    if (!sId || !cId) return;
    loadDetails();
  }, [sId, cId]);

  const loadDetails = async () => {
    try {
      setLoading(true);
      const res = await getCandidateSessionDetail(sId, cId);
      setData(res);
      if (res.review) {
        setReviewStatus(res.review.review_status || 'pending');
        setRecruiterNotes(res.review.recruiter_notes || '');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveReview = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await updateRecruiterReview(sId, cId, {
        review_status: reviewStatus as any,
        recruiter_notes: recruiterNotes,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      alert('Failed to save recruiter review.');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-9 w-9 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
          <p className="text-sm font-medium text-slate-500">Loading candidate evaluation...</p>
        </div>
      </div>
    );
  }

  const { candidate, session, result, review } = data;
  const profile = candidate.extracted_profile || {};
  const compScores = result?.component_scores || {};
  const explanation = result?.matching_explanation || {};
  const finalScore = result?.final_match_score || 0;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Breadcrumb Back Link */}
      <div>
        <Link
          to={`/screenings/${sId}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Screening Results ({session.job_title})</span>
        </Link>
      </div>

      {/* Header Profile Card */}
      <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">{candidate.name}</h1>
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${
                reviewStatus === 'shortlisted'
                  ? 'bg-emerald-100 text-emerald-800'
                  : reviewStatus === 'under_review'
                  ? 'bg-amber-100 text-amber-800'
                  : reviewStatus === 'rejected'
                  ? 'bg-rose-100 text-rose-800'
                  : 'bg-slate-100 text-slate-600'
              }`}
            >
              {reviewStatus}
            </span>
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-slate-500">
            {candidate.email && (
              <span className="flex items-center gap-1.5">
                <Mail className="h-3.5 w-3.5 text-slate-400" />
                {candidate.email}
              </span>
            )}
            {candidate.phone && (
              <span className="flex items-center gap-1.5">
                <Phone className="h-3.5 w-3.5 text-slate-400" />
                {candidate.phone}
              </span>
            )}
            <span className="flex items-center gap-1.5">
              <Briefcase className="h-3.5 w-3.5 text-slate-400" />
              {result?.relevant_experience || 0} years experience
            </span>
          </div>

          {profile.summary && (
            <p className="mt-3 text-xs text-slate-600 max-w-2xl leading-relaxed italic bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              "{profile.summary}"
            </p>
          )}
        </div>

        {/* Big Overall Score Badge */}
        <div className="flex flex-col items-center justify-center rounded-2xl border border-indigo-100 bg-gradient-to-b from-indigo-50/50 to-white p-5 text-center min-w-[140px] shadow-subtle shrink-0">
          <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-700">Overall Match</span>
          <span
            className={`text-4xl font-extrabold my-1 ${
              finalScore >= 75 ? 'text-emerald-600' : finalScore >= 50 ? 'text-indigo-600' : 'text-slate-600'
            }`}
          >
            {finalScore.toFixed(0)}%
          </span>
          <span className="text-[10px] text-slate-400">Weighted Fit Score</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('analysis')}
          className={`py-2.5 px-4 text-xs font-bold border-b-2 transition-colors ${
            activeTab === 'analysis'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-900'
          }`}
        >
          AI Match Breakdown & Evidence
        </button>
        <button
          onClick={() => setActiveTab('resume')}
          className={`py-2.5 px-4 text-xs font-bold border-b-2 transition-colors ${
            activeTab === 'resume'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-900'
          }`}
        >
          Extracted Resume Content
        </button>
      </div>

      {activeTab === 'analysis' ? (
        <div className="space-y-6">
          {/* Component Score Progress Bars */}
          <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle">
            <h2 className="text-sm font-bold text-slate-900 mb-4">Explainable Match Breakdown (0 - 100)</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
              {/* Required Skills */}
              <div>
                <div className="flex justify-between font-semibold text-slate-700 mb-1">
                  <span>Required Skills Match (35% Weight)</span>
                  <span>{compScores.required_skills ?? 0}/100</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-indigo-600"
                    style={{ width: `${compScores.required_skills ?? 0}%` }}
                  />
                </div>
              </div>

              {/* Semantic Similarity */}
              <div>
                <div className="flex justify-between font-semibold text-slate-700 mb-1">
                  <span>Semantic Vector Alignment (25% Weight)</span>
                  <span>{compScores.semantic_similarity ?? 0}/100</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-blue-600"
                    style={{ width: `${compScores.semantic_similarity ?? 0}%` }}
                  />
                </div>
              </div>

              {/* Relevant Experience */}
              <div>
                <div className="flex justify-between font-semibold text-slate-700 mb-1">
                  <span>Relevant Work Experience (20% Weight)</span>
                  <span>{compScores.experience ?? 0}/100</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-emerald-600"
                    style={{ width: `${compScores.experience ?? 0}%` }}
                  />
                </div>
              </div>

              {/* Preferred Skills */}
              <div>
                <div className="flex justify-between font-semibold text-slate-700 mb-1">
                  <span>Preferred Skills Match (10% Weight)</span>
                  <span>{compScores.preferred_skills ?? 0}/100</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-purple-600"
                    style={{ width: `${compScores.preferred_skills ?? 0}%` }}
                  />
                </div>
              </div>

              {/* Education & Certs */}
              <div className="sm:col-span-2">
                <div className="flex justify-between font-semibold text-slate-700 mb-1">
                  <span>Education & Certifications (10% Weight)</span>
                  <span>{compScores.education ?? 0}/100</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-teal-600"
                    style={{ width: `${compScores.education ?? 0}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Strengths, Gaps & Skills Chips */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matched & Missing Skills */}
            <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-4">
              <h3 className="text-sm font-bold text-slate-900">Skills Alignment</h3>

              <div>
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                  Demonstrated Matching Skills ({result?.matched_skills?.length || 0}):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {result?.matched_skills?.length > 0 ? (
                    result.matched_skills.map((skill: string, idx: number) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 rounded-md bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-800 border border-emerald-200"
                      >
                        <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400">None detected</span>
                  )}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                  Missing Required Skills ({result?.missing_required_skills?.length || 0}):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {result?.missing_required_skills?.length > 0 ? (
                    result.missing_required_skills.map((skill: string, idx: number) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 rounded-md bg-rose-50 px-2.5 py-1 text-xs font-semibold text-rose-800 border border-rose-200"
                      >
                        <XCircle className="h-3 w-3 text-rose-600" />
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-emerald-600 font-medium">✓ No missing required skills</span>
                  )}
                </div>
              </div>
            </div>

            {/* AI Summary, Strengths & Gaps */}
            <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-4">
              <h3 className="text-sm font-bold text-slate-900">Key Strengths & Evidence</h3>

              <div className="rounded-lg bg-indigo-50/50 p-3 border border-indigo-100 text-xs text-indigo-900 leading-relaxed font-medium">
                {explanation.summary || 'Profile evaluated successfully.'}
              </div>

              <div>
                <span className="text-[11px] font-semibold text-emerald-700 uppercase tracking-wider block mb-1.5">
                  Key Strengths:
                </span>
                <ul className="space-y-1.5 text-xs text-slate-700">
                  {explanation.strengths?.map((s: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-emerald-500 font-bold">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {explanation.gaps?.length > 0 && (
                <div className="pt-2 border-t border-slate-100">
                  <span className="text-[11px] font-semibold text-rose-700 uppercase tracking-wider block mb-1.5">
                    Identified Gaps:
                  </span>
                  <ul className="space-y-1.5 text-xs text-slate-700">
                    {explanation.gaps?.map((g: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-1.5">
                        <span className="text-rose-500 font-bold">•</span>
                        <span>{g}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Overqualification Advisory Panel (when enabled) */}
          {session.overqualification_enabled && result?.overqualification_evidence && (
            <div className="rounded-xl border border-amber-200 bg-amber-50/40 p-5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="h-5 w-5 text-amber-600 shrink-0" />
                  <h3 className="text-sm font-bold text-amber-900">Overqualification Advisory Analysis</h3>
                </div>
                <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-800">
                  {result.overqualification_status} ({Math.round(result.overqualification_confidence * 100)}% Confidence)
                </span>
              </div>

              <div className="text-xs text-slate-700 space-y-1 pl-7">
                {result.overqualification_evidence.evidence?.map((ev: string, idx: number) => (
                  <p key={idx} className="flex items-start gap-1.5">
                    <span className="text-amber-600 font-bold">›</span>
                    <span>{ev}</span>
                  </p>
                ))}
              </div>

              {/* Mandatory Advisory Disclaimer */}
              <div className="mt-3 pt-3 border-t border-amber-200/70 text-[11px] text-amber-800 italic leading-relaxed">
                <b>Disclaimer:</b> {result.overqualification_evidence.disclaimer}
              </div>
            </div>
          )}

          {/* Recruiter Review Actions Panel */}
          <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Recruiter Evaluation & Review Decision</h3>
            <p className="text-xs text-slate-500">
              Record your hiring decision and private feedback. Recruiter determinations are tracked separately from automated AI match scores.
            </p>

            <form onSubmit={handleSaveReview} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Status Decision</label>
                  <select
                    value={reviewStatus}
                    onChange={(e) => setReviewStatus(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="pending">Pending Evaluation</option>
                    <option value="shortlisted">Shortlisted for Interview</option>
                    <option value="under_review">Under Review / Additional Assessment</option>
                    <option value="rejected">Not Moving Forward (Rejected)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Private Recruiter Notes & Observations
                </label>
                <textarea
                  rows={3}
                  value={recruiterNotes}
                  onChange={(e) => setRecruiterNotes(e.target.value)}
                  placeholder="Add interview notes, portfolio assessment, or overrides..."
                  className="w-full rounded-lg border border-slate-200 p-3 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-between pt-2">
                {saveSuccess ? (
                  <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
                    <Check className="h-4 w-4" />
                    Review decisions recorded successfully!
                  </span>
                ) : (
                  <span />
                )}

                <button
                  type="submit"
                  disabled={saving}
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm"
                >
                  <Save className="h-3.5 w-3.5" />
                  <span>{saving ? 'Saving...' : 'Save Recruiter Decision'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : (
        /* Full Extracted Resume Content Tab */
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-6">
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-2">Candidate Education & Credentials</h3>
            <div className="space-y-1 text-xs text-slate-700">
              {profile.education?.length > 0 ? (
                profile.education.map((edu: string, idx: number) => (
                  <p key={idx} className="flex items-center gap-2">
                    <GraduationCap className="h-4 w-4 text-indigo-500" />
                    <span>{edu}</span>
                  </p>
                ))
              ) : (
                <p className="text-slate-400">Not specified</p>
              )}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-2">Certifications</h3>
            <div className="space-y-1 text-xs text-slate-700">
              {profile.certifications?.length > 0 ? (
                profile.certifications.map((cert: string, idx: number) => (
                  <p key={idx} className="flex items-center gap-2">
                    <Award className="h-4 w-4 text-amber-500" />
                    <span>{cert}</span>
                  </p>
                ))
              ) : (
                <p className="text-slate-400">None documented</p>
              )}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-2">Previous Documented Roles</h3>
            <div className="flex flex-wrap gap-1.5">
              {profile.previous_titles?.map((t: string, idx: number) => (
                <span key={idx} className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-800">
                  {t}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-2">Raw Resume Text Excerpt</h3>
            <pre className="rounded-lg bg-slate-50 p-4 text-xs font-mono text-slate-800 whitespace-pre-wrap max-h-96 overflow-y-auto border border-slate-200">
              {candidate.resume_text || 'No raw text available.'}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};
