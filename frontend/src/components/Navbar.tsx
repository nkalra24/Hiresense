import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, Sparkles, Activity, ShieldCheck } from 'lucide-react';
import { getHealth } from '../services/api';

export const Navbar: React.FC = () => {
  const [health, setHealth] = useState<{ status: string; ai_model_loaded: boolean } | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'degraded', ai_model_loaded: false }));
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-6 backdrop-blur">
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-700 via-indigo-600 to-indigo-500 text-white shadow-md shadow-indigo-100">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight text-slate-900">HireSense</span>
              <span className="rounded bg-indigo-50 px-1.5 py-0.5 text-xs font-semibold text-indigo-700 border border-indigo-100">AI</span>
            </div>
            <p className="text-[11px] font-medium text-slate-500">Intelligent Resume Screening & Ranking</p>
          </div>
        </Link>
      </div>

      <div className="flex items-center gap-4">
        {/* System Health / AI Status Badge */}
        <div className="hidden sm:flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600">
          <Activity className={`h-3.5 w-3.5 ${health?.status === 'healthy' ? 'text-emerald-500 animate-pulse' : 'text-amber-500'}`} />
          <span className="font-medium">
            AI Engine: {health?.ai_model_loaded ? 'Sentence-Transformers Ready' : 'TF-IDF / Hybrid Mode'}
          </span>
        </div>

        {/* Responsible AI Disclaimer Pill */}
        <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-500">
          <ShieldCheck className="h-4 w-4 text-indigo-600" />
          <span>Fair & Explainable Evaluation</span>
        </div>

        {/* Start Screening CTA */}
        <Link
          to="/screenings/new"
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          <PlusCircle className="h-4 w-4" />
          <span>New Screening</span>
        </Link>
      </div>
    </header>
  );
};
