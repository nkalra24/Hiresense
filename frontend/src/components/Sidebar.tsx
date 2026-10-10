import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileUp,
  History,
  Users,
  Settings,
  Scale,
  Sparkles,
  ExternalLink
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'New Screening', href: '/screenings/new', icon: FileUp },
  { name: 'Screening History', href: '/screenings', icon: History },
  { name: 'Candidates', href: '/candidates', icon: Users },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r border-slate-200 bg-white flex flex-col justify-between p-4 shrink-0">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Main Navigation
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                end={item.href === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-700 font-semibold shadow-subtle'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`
                }
              >
                <item.icon className="h-4 w-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Responsible AI Compliance Card */}
        <div className="rounded-xl border border-indigo-100 bg-gradient-to-br from-indigo-50/70 to-slate-50 p-3.5 text-xs text-slate-600">
          <div className="flex items-center gap-1.5 font-semibold text-indigo-900 mb-1">
            <Scale className="h-4 w-4 text-indigo-600" />
            <span>Ethical AI Guardrails</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Screening is demographic-blind, reproducible, and explainable. No protected attributes are factored into match scores.
          </p>
        </div>
      </div>

      {/* Footer Info */}
      <div className="border-t border-slate-100 pt-3 text-[11px] text-slate-400 flex items-center justify-between">
        <span>HireSense Enterprise v1.0</span>
        <a
          href="/api/docs"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1 hover:text-indigo-600 transition-colors"
        >
          <span>API Docs</span>
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>
    </aside>
  );
};
