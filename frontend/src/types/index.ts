export interface ScoringWeights {
  weight_required_skills: number;
  weight_semantic_similarity: number;
  weight_experience: number;
  weight_preferred_skills: number;
  weight_education: number;
}

export interface JobRequirements {
  required_skills: string[];
  preferred_skills: string[];
  min_experience_years: number;
  education_requirements: string[];
  certifications: string[];
}

export interface ScreeningSession {
  id: number;
  job_title: string;
  department?: string;
  job_description: string;
  extracted_requirements?: JobRequirements;
  scoring_weights?: ScoringWeights;
  overqualification_enabled: boolean;
  processing_status: 'queued' | 'processing' | 'completed' | 'failed';
  total_resumes: number;
  processed_resumes: number;
  failed_resumes: number;
  created_at: string;
  updated_at: string;
}

export interface ComponentScores {
  required_skills: number;
  semantic_similarity: number;
  experience: number;
  preferred_skills: number;
  education: number;
}

export interface MatchingExplanation {
  summary: string;
  strengths: string[];
  gaps: string[];
}

export interface OverqualificationEvidence {
  evidence: string[];
  disclaimer: string;
}

export interface ScreeningResult {
  id: number;
  screening_session_id: number;
  candidate_id: number;
  candidate_name: string;
  candidate_email?: string;
  final_match_score: number;
  component_scores: ComponentScores;
  matched_skills: string[];
  missing_required_skills: string[];
  relevant_experience: number;
  matching_explanation: MatchingExplanation;
  overqualification_status: string;
  overqualification_confidence: number;
  overqualification_evidence?: OverqualificationEvidence;
  review_status: 'pending' | 'shortlisted' | 'under_review' | 'rejected';
  recruiter_notes?: string;
  override_reason?: string;
  created_at: string;
}

export interface DashboardStats {
  total_sessions: number;
  total_resumes_processed: number;
  average_score: number;
  high_fit_candidates: number;
  distribution: { range: string; count: number }[];
  recent_screenings: {
    id: number;
    job_title: string;
    department?: string;
    processing_status: string;
    total_resumes: number;
    processed_resumes: number;
    created_at: string;
  }[];
  recent_activity: {
    candidate_name: string;
    job_title: string;
    session_id: number;
    review_status: string;
    updated_at: string;
  }[];
}

export interface CandidateProfile {
  name: string;
  email?: string;
  phone?: string;
  summary?: string;
  explicit_skills: string[];
  inferred_skills: string[];
  all_skills: string[];
  years_experience: number;
  education: string[];
  certifications: string[];
  previous_titles: string[];
}

export interface Candidate {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  extracted_profile?: CandidateProfile;
  resume_text?: string;
  created_at: string;
}
