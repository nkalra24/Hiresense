import React, { useEffect, useState } from 'react';
import { Search, Users, Mail, Phone, Briefcase, GraduationCap, Trash2 } from 'lucide-react';
import { getCandidates, deleteCandidate } from '../services/api';
import { Candidate } from '../types';

export const CandidatesPage: React.FC = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  useEffect(() => {
    loadCandidates();
  }, [search]);

  const loadCandidates = async () => {
    try {
      setLoading(true);
      const data = await getCandidates(search || undefined);
      setCandidates(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete candidate profile and associated analysis history?')) return;
    try {
      await deleteCandidate(id);
      setCandidates((prev) => prev.filter((c) => c.id !== id));
      if (selectedCandidate?.id === id) setSelectedCandidate(null);
    } catch (e) {
      alert('Failed to delete candidate.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Talent Directory</h1>
        <p className="text-sm text-slate-500">
          All extracted candidate profiles across past and active screening sessions.
        </p>
      </div>

      {/* Search Input */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by candidate name, email, or technology..."
          className="w-full rounded-lg border border-slate-200 bg-white pl-9 pr-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      {/* Candidates Grid */}
      {loading ? (
        <div className="py-20 text-center">
          <div className="mx-auto h-7 w-7 animate-spin rounded-full border-3 border-indigo-600 border-t-transparent mb-2" />
          <p className="text-xs text-slate-500">Loading candidate profiles...</p>
        </div>
      ) : candidates.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
          <Users className="mx-auto h-8 w-8 text-slate-300 mb-2" />
          <p className="text-sm font-semibold text-slate-700">No candidates found</p>
          <p className="text-xs text-slate-400 mt-1">Upload resumes in a screening session to populate the directory.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {candidates.map((cand) => {
            const profile = cand.extracted_profile || ({} as any);
            const skills = profile.all_skills || [];

            return (
              <div
                key={cand.id}
                className="rounded-xl border border-slate-200/80 bg-white p-5 shadow-subtle hover:shadow-card transition-shadow flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">{cand.name}</h3>
                      <div className="space-y-0.5 mt-1.5 text-[11px] text-slate-500">
                        {cand.email && (
                          <p className="flex items-center gap-1.5 truncate">
                            <Mail className="h-3 w-3 text-slate-400 shrink-0" />
                            <span>{cand.email}</span>
                          </p>
                        )}
                        {cand.phone && (
                          <p className="flex items-center gap-1.5">
                            <Phone className="h-3 w-3 text-slate-400 shrink-0" />
                            <span>{cand.phone}</span>
                          </p>
                        )}
                        <p className="flex items-center gap-1.5 font-medium text-slate-700">
                          <Briefcase className="h-3 w-3 text-indigo-500 shrink-0" />
                          <span>{profile.years_experience || 0} yrs experience</span>
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => handleDelete(cand.id)}
                      className="text-slate-300 hover:text-red-500 p-1 transition-colors"
                      title="Delete Candidate"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  {/* Skills tags */}
                  <div className="mt-4 pt-3 border-t border-slate-100">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block mb-1.5">
                      Extracted Skills:
                    </span>
                    <div className="flex flex-wrap gap-1 max-h-16 overflow-hidden">
                      {skills.slice(0, 6).map((s: string, idx: number) => (
                        <span
                          key={idx}
                          className="rounded bg-indigo-50/60 px-1.5 py-0.5 text-[10px] font-medium text-indigo-700 border border-indigo-100/60"
                        >
                          {s}
                        </span>
                      ))}
                      {skills.length > 6 && (
                        <span className="text-[10px] text-slate-400">+{skills.length - 6} more</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                  <span>ID #{cand.id}</span>
                  <span>Added {new Date(cand.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
