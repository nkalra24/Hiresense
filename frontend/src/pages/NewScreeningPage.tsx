import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileText,
  X,
  Sliders,
  Sparkles,
  AlertCircle,
  HelpCircle,
  ShieldCheck,
  CheckCircle2,
  FolderOpen
} from 'lucide-react';
import { createScreening } from '../services/api';
import { ScoringWeights } from '../types';

export const NewScreeningPage: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Form states
  const [jobTitle, setJobTitle] = useState('');
  const [department, setDepartment] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [requiredSkills, setRequiredSkills] = useState('');
  const [preferredSkills, setPreferredSkills] = useState('');
  const [minExp, setMinExp] = useState<number>(3);
  const [educationReq, setEducationReq] = useState('');
  const [overqualificationEnabled, setOverqualificationEnabled] = useState(true);

  // Weights state
  const [weights, setWeights] = useState<ScoringWeights>({
    weight_required_skills: 35,
    weight_semantic_similarity: 25,
    weight_experience: 20,
    weight_preferred_skills: 10,
    weight_education: 10,
  });
  const [showWeightSliders, setShowWeightSliders] = useState(false);

  // File upload states
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Total weight check
  const totalWeight =
    weights.weight_required_skills +
    weights.weight_semantic_similarity +
    weights.weight_experience +
    weights.weight_preferred_skills +
    weights.weight_education;

  // File handling
  const handleFilesSelected = (newFiles: FileList | null) => {
    if (!newFiles) return;
    setUploadError(null);

    const validExtensions = ['.pdf', '.docx'];
    const added: File[] = [];
    const existingNames = new Set(files.map((f) => f.name.toLowerCase()));

    for (let i = 0; i < newFiles.length; i++) {
      const file = newFiles[i];
      const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

      if (!validExtensions.includes(ext)) {
        setUploadError(`File "${file.name}" has an unsupported format. Please upload PDF or DOCX.`);
        continue;
      }

      if (file.size > 15 * 1024 * 1024) {
        setUploadError(`File "${file.name}" exceeds the 15MB limit.`);
        continue;
      }

      if (existingNames.has(file.name.toLowerCase())) {
        continue; // deduplicate
      }

      added.push(file);
      existingNames.add(file.name.toLowerCase());
    }

    setFiles((prev) => [...prev, ...added]);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const loadSampleJob = () => {
    setJobTitle('Senior Full-Stack & AI Engineer');
    setDepartment('Engineering & Innovation');
    setJobDescription(`We are looking for a Senior Full-Stack & AI Engineer to lead the design and development of our intelligent cloud platform.
    
Key Responsibilities:
- Architect and maintain enterprise-grade web applications with modern frontend frameworks and robust backend microservices.
- Design high-throughput APIs and integrate machine learning / LLM models into production.
- Collaborate with product and design teams to build performant, accessible UI workflows.

Required Qualifications:
- 4+ years of professional software engineering experience.
- Strong proficiency in Python, FastAPI, React, and TypeScript.
- Hands-on experience with PostgreSQL, Docker, and relational database modeling.
- Solid understanding of REST APIs, unit testing, and Git version control.

Preferred Qualifications:
- Familiarity with PyTorch, Transformers, NLP, and Hugging Face.
- Experience with Kubernetes, AWS, and Redis caching.
- Bachelor's or Master's degree in Computer Science or related STEM field.`);
    setRequiredSkills('Python, React, TypeScript, FastAPI, PostgreSQL, Docker');
    setPreferredSkills('PyTorch, Transformers, Kubernetes, AWS, Redis');
    setMinExp(4);
    setEducationReq("Bachelor's Degree in Computer Science");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim()) {
      setUploadError('Job title is required.');
      return;
    }
    if (!jobDescription.trim()) {
      setUploadError('Job description is required.');
      return;
    }
    if (files.length === 0) {
      setUploadError('Please attach at least one candidate resume (PDF or DOCX).');
      return;
    }

    setSubmitting(true);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append('job_title', jobTitle.trim());
      if (department.trim()) formData.append('department', department.trim());
      formData.append('job_description', jobDescription.trim());
      if (requiredSkills.trim()) formData.append('required_skills', requiredSkills.trim());
      if (preferredSkills.trim()) formData.append('preferred_skills', preferredSkills.trim());
      formData.append('min_experience_years', minExp.toString());
      if (educationReq.trim()) formData.append('education_requirements', educationReq.trim());
      formData.append('overqualification_enabled', String(overqualificationEnabled));
      formData.append('scoring_weights', JSON.stringify(weights));

      files.forEach((file) => {
        formData.append('files', file);
      });

      const session = await createScreening(formData);
      navigate(`/screenings/${session.id}`);
    } catch (err: any) {
      console.error(err);
      setUploadError(err.response?.data?.detail || 'Failed to submit screening session. Please check your inputs.');
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">New Resume Screening Session</h1>
          <p className="text-sm text-slate-500">
            Define role requirements, configure weights, and upload resumes for AI ranking.
          </p>
        </div>

        {/* Quick Demo Pre-load Button */}
        <button
          type="button"
          onClick={loadSampleJob}
          className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-indigo-50/70 px-3 py-1.5 text-xs font-semibold text-indigo-700 hover:bg-indigo-100 transition-colors shadow-subtle"
        >
          <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
          <span>Load Sample Job Criteria</span>
        </button>
      </div>

      {uploadError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-xs font-medium text-red-700 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 text-red-500" />
          <span>{uploadError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Step 1: Job Details Card */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-4">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[11px] font-bold text-white">1</span>
            Job Position & Description
          </h2>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Job Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Senior Full-Stack Engineer"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Department / Team (Optional)
              </label>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="e.g. Product Engineering"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Job Description <span className="text-red-500">*</span>
            </label>
            <textarea
              required
              rows={6}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the full job description here. Our NLP parser will extract core qualifications, responsibilities, and key domain requirements automatically..."
              className="w-full rounded-lg border border-slate-200 p-3 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono text-xs leading-relaxed"
            />
          </div>

          {/* Granular Criteria Fields */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 pt-2 border-t border-slate-100">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Required Skills (Comma separated)
              </label>
              <input
                type="text"
                value={requiredSkills}
                onChange={(e) => setRequiredSkills(e.target.value)}
                placeholder="e.g. Python, React, PostgreSQL, Docker"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <span className="text-[11px] text-slate-400">Leave blank to auto-extract from description</span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Preferred / Nice-to-Have Skills
              </label>
              <input
                type="text"
                value={preferredSkills}
                onChange={(e) => setPreferredSkills(e.target.value)}
                placeholder="e.g. PyTorch, Kubernetes, AWS"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Minimum Years of Experience: <span className="font-bold text-indigo-700">{minExp} yrs</span>
              </label>
              <input
                type="range"
                min={0}
                max={15}
                step={0.5}
                value={minExp}
                onChange={(e) => setMinExp(parseFloat(e.target.value))}
                className="w-full accent-indigo-600"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Required Education / Degree
              </label>
              <input
                type="text"
                value={educationReq}
                onChange={(e) => setEducationReq(e.target.value)}
                placeholder="e.g. Bachelor's Degree in Computer Science"
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Step 2: Scoring Weights & Overqualification Settings */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[11px] font-bold text-white">2</span>
              Scoring Weights & Advisory Settings
            </h2>
            <button
              type="button"
              onClick={() => setShowWeightSliders(!showWeightSliders)}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
            >
              <Sliders className="h-3.5 w-3.5" />
              <span>{showWeightSliders ? 'Hide Weights' : 'Customize Weights'}</span>
            </button>
          </div>

          {/* Overqualification Toggle */}
          <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-4 flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-900">Enable Overqualification Advisory Analysis</span>
                <span className="rounded bg-indigo-100 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-800">Advisory Only</span>
              </div>
              <p className="mt-1 text-xs text-slate-500 leading-relaxed">
                Flags candidates whose seniority, leadership roles, or documented experience significantly exceed job parameters without penalizing their technical match score.
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer shrink-0">
              <input
                type="checkbox"
                checked={overqualificationEnabled}
                onChange={(e) => setOverqualificationEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>

          {/* Sliders Accordion */}
          {showWeightSliders && (
            <div className="space-y-4 pt-3 border-t border-slate-100">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">Weights Distribution</span>
                <span className={`font-bold ${totalWeight === 100 ? 'text-emerald-600' : 'text-amber-600'}`}>
                  Total: {totalWeight}% {totalWeight !== 100 && '(Normalized automatically)'}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <div className="flex justify-between mb-1 text-slate-600">
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
                  <div className="flex justify-between mb-1 text-slate-600">
                    <span>Semantic Vector Similarity</span>
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
                  <div className="flex justify-between mb-1 text-slate-600">
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
                  <div className="flex justify-between mb-1 text-slate-600">
                    <span>Preferred Skills Match</span>
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
                  <div className="flex justify-between mb-1 text-slate-600">
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
            </div>
          )}
        </div>

        {/* Step 3: Resume Upload Zone */}
        <div className="rounded-xl border border-slate-200/80 bg-white p-6 shadow-subtle space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[11px] font-bold text-white">3</span>
              Candidate Resumes (PDF / DOCX)
            </h2>
            <span className="text-xs text-slate-400">{files.length} file(s) queued</span>
          </div>

          {/* Drag & Drop Area */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragging(false);
              handleFilesSelected(e.dataTransfer.files);
            }}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              isDragging
                ? 'border-indigo-500 bg-indigo-50/50'
                : 'border-slate-300 hover:border-indigo-400 bg-slate-50/40 hover:bg-slate-50'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              multiple
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={(e) => handleFilesSelected(e.target.files)}
              className="hidden"
            />
            <UploadCloud className="mx-auto h-10 w-10 text-indigo-500 mb-2" />
            <p className="text-sm font-semibold text-slate-800">
              Drag & drop candidate resumes here, or <span className="text-indigo-600 underline">browse files</span>
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Supports multiple PDF and DOCX files (up to 15MB each). Duplicate files are filtered automatically.
            </p>
          </div>

          {/* Queued Files List */}
          {files.length > 0 && (
            <div className="space-y-2 pt-2">
              <span className="text-xs font-semibold text-slate-700">Attached Resumes:</span>
              <div className="max-h-56 overflow-y-auto space-y-1.5 pr-1">
                {files.map((file, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-700"
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileText className="h-4 w-4 text-indigo-500 shrink-0" />
                      <span className="font-medium truncate">{file.name}</span>
                      <span className="text-[11px] text-slate-400 shrink-0">
                        ({(file.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(idx)}
                      className="text-slate-400 hover:text-red-500 transition-colors p-1"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Screening Submission Summary Card */}
        <div className="rounded-xl border border-indigo-100 bg-indigo-50/40 p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-900">Screening Summary</h3>
            <p className="text-xs text-indigo-800 mt-0.5">
              Ready to analyze <b>{files.length} resume(s)</b> against <b>"{jobTitle || 'Untitled Role'}"</b>.
            </p>
            <p className="text-[11px] text-slate-500 mt-1">
              Processing runs asynchronously in the background. Results will be ranked from best fit to lowest fit.
            </p>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow hover:bg-indigo-700 disabled:opacity-50 transition-all focus:ring-2 focus:ring-indigo-500 shrink-0"
          >
            {submitting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                <span>Submitting Session...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>Analyze Resumes</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
