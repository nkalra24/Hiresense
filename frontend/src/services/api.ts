import axios from 'axios';
import type {
  ScreeningSession,
  ScreeningResult,
  DashboardStats,
  Candidate,
  ScoringWeights
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 60000,
});

export const getDashboardStats = async (): Promise<DashboardStats> => {
  const res = await api.get('/settings/stats');
  return res.data;
};

export const createScreening = async (formData: FormData): Promise<ScreeningSession> => {
  // Let the browser set multipart/form-data with the required boundary.
  const res = await api.post('/screenings', formData);
  return res.data;
};

export const getScreenings = async (skip = 0, limit = 50): Promise<ScreeningSession[]> => {
  const res = await api.get('/screenings', { params: { skip, limit } });
  return res.data;
};

export const getScreening = async (id: number): Promise<ScreeningSession> => {
  const res = await api.get(`/screenings/${id}`);
  return res.data;
};

export const deleteScreening = async (id: number): Promise<{ message: string }> => {
  const res = await api.delete(`/screenings/${id}`);
  return res.data;
};

export const getScreeningStatus = async (id: number) => {
  const res = await api.get(`/screenings/${id}/status`);
  return res.data;
};

export interface ResultFilterParams {
  search?: string;
  min_score?: number;
  max_score?: number;
  overqualification?: string;
  sort_by?: 'score_desc' | 'score_asc' | 'exp_desc';
}

export const getScreeningResults = async (
  id: number,
  params?: ResultFilterParams
): Promise<ScreeningResult[]> => {
  const res = await api.get(`/screenings/${id}/results`, { params });
  return res.data;
};

export const getCandidateSessionDetail = async (
  screeningId: number,
  candidateId: number
) => {
  const res = await api.get(`/screenings/${screeningId}/candidates/${candidateId}`);
  return res.data;
};

export const updateRecruiterReview = async (
  screeningId: number,
  candidateId: number,
  data: {
    review_status: 'pending' | 'shortlisted' | 'under_review' | 'rejected';
    recruiter_notes?: string;
    override_reason?: string;
  }
) => {
  const res = await api.patch(
    `/screenings/${screeningId}/candidates/${candidateId}/review`,
    data
  );
  return res.data;
};

export const getCandidates = async (search?: string, skip = 0, limit = 50): Promise<Candidate[]> => {
  const res = await api.get('/candidates', { params: { search, skip, limit } });
  return res.data;
};

export const getCandidate = async (id: number) => {
  const res = await api.get(`/candidates/${id}`);
  return res.data;
};

export const deleteCandidate = async (id: number) => {
  const res = await api.delete(`/candidates/${id}`);
  return res.data;
};

export const getScoringSettings = async (): Promise<ScoringWeights> => {
  const res = await api.get('/settings/scoring');
  return res.data;
};

export const updateScoringSettings = async (weights: ScoringWeights): Promise<ScoringWeights> => {
  const res = await api.patch('/settings/scoring', weights);
  return res.data;
};

export const getHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const getExportCsvUrl = (id: number): string => `/api/screenings/${id}/export/csv`;
export const getExportPdfUrl = (id: number): string => `/api/screenings/${id}/export/pdf`;

export default api;
