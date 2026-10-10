import React, { useEffect, useState } from 'react';
import { Sliders, Cpu, Save, RotateCcw, Check, ShieldCheck, Info } from 'lucide-react';
import { getScoringSettings, updateScoringSettings, getHealth } from '../services/api';
import { ScoringWeights } from '../types';

export const SettingsPage: React.FC = () => {
  const [weights, setWeights] = useState<ScoringWeights>({
    weight_required_skills: 35,
    weight_semantic_similarity: 25,
    weight_experience: 20,
    weight_preferred_skills: 10,
    weight_education: 10,
  });
  const [health, setHealth] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    getScoringSettings().then(setWeights).catch(console.error);
    getHealth().then(setHealth).catch(console.error);
  }, []);

  const total =
    weights.weight_required_skills +
    weights.weight_semantic_similarity +
    weights.weight_experience +
    weights.weight_preferred_skills +
    weights.weight_education;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await updateScoringSettings(weights);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (e) {
      alert('Failed to update scoring configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleResetDefaults = () => {
    setWeights({
      weight_required_skills: 35,
      weight_semantic_similarity: 25,
      weight_experience: 20,
      weight_preferred_skills: 10,
      weight_education: 10,
    });
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">System Settings & AI Configuration</h1>
        <p className="text-sm text-slate-500">
          Configure default scoring weights, inspect model parameters, and review matching criteria formulas.
        </p>
      </div>

      {/* Default Scoring Formula Config */}
      <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-5">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600">
              <Sliders className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Default Scoring Formula Weights</h2>
              <p className="text-xs text-slate-500">
                Applied automatically to new screening sessions unless overridden.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleResetDefaults}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset Defaults</span>
          </button>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-700">Weights Breakdown</span>
            <span className={`font-bold ${total === 100 ? 'text-emerald-600' : 'text-amber-600'}`}>
              Sum: {total}% {total !== 100 && '(Normalizes proportionally)'}
            </span>
          </div>

          <div className="space-y-3.5 text-xs">
            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Required Skills Match</span>
                <span className="font-bold">{weights.weight_required_skills}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={60}
                value={weights.weight_required_skills}
                onChange={(e) => setWeights({ ...weights, weight_required_skills: Number(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Semantic Similarity (Sentence-Transformers)</span>
                <span className="font-bold">{weights.weight_semantic_similarity}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={50}
                value={weights.weight_semantic_similarity}
                onChange={(e) => setWeights({ ...weights, weight_semantic_similarity: Number(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Relevant Work Experience</span>
                <span className="font-bold">{weights.weight_experience}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={40}
                value={weights.weight_experience}
                onChange={(e) => setWeights({ ...weights, weight_experience: Number(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Preferred / Nice-to-Have Skills</span>
                <span className="font-bold">{weights.weight_preferred_skills}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={30}
                value={weights.weight_preferred_skills}
                onChange={(e) => setWeights({ ...weights, weight_preferred_skills: Number(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Education & Certifications</span>
                <span className="font-bold">{weights.weight_education}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={30}
                value={weights.weight_education}
                onChange={(e) => setWeights({ ...weights, weight_education: Number(e.target.value) })}
                className="w-full accent-indigo-600"
              />
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-slate-100">
            {savedSuccess ? (
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-600">
                <Check className="h-4 w-4" />
                Default configuration updated!
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
              <span>{saving ? 'Saving...' : 'Save Default Weights'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Model & Architecture Details */}
      <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600">
            <Cpu className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">AI / ML Pipeline Architecture</h2>
            <p className="text-xs text-slate-500">
              Underlying open-source models and document extraction engines.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs pt-2">
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Embedding Model</span>
            <p className="font-bold text-slate-800 mt-1">all-MiniLM-L6-v2</p>
            <p className="text-[11px] text-slate-500 mt-0.5">384-dimensional dense sentence embeddings loaded at startup</p>
          </div>

          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Document Parsing</span>
            <p className="font-bold text-slate-800 mt-1">PyMuPDF & python-docx</p>
            <p className="text-[11px] text-slate-500 mt-0.5">High-fidelity binary text, table, and formatting extractions</p>
          </div>

          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Matching Signals</span>
            <p className="font-bold text-slate-800 mt-1">Hybrid Dense & Lexical</p>
            <p className="text-[11px] text-slate-500 mt-0.5">SentenceTransformers + TF-IDF cosine similarity + taxonomy normalizer</p>
          </div>

          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
            <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Overqualification Engine</span>
            <p className="font-bold text-slate-800 mt-1">Rule-Based Advisory</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Seniority delta, leadership titles, and advanced credential evaluation</p>
          </div>
        </div>
      </div>

      {/* Ethical AI & Fair Evaluation Guidelines */}
      <div className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-5 space-y-2 text-xs text-slate-700">
        <div className="flex items-center gap-2 font-bold text-indigo-900">
          <ShieldCheck className="h-4 w-4 text-indigo-600" />
          <span>Fairness & Responsible Use Principle</span>
        </div>
        <p className="text-[11px] text-slate-600 leading-relaxed">
          HireSense AI assists recruiters and human hiring managers — it never replaces human judgment. The system does not infer or score candidates on protected demographics (age, gender, ethnicity, disability, marital status). Ranking scores are strictly derived from verifiable job-related evidence in the submitted resumes.
        </p>
      </div>
    </div>
  );
};
