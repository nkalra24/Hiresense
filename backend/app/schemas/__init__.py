from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

class ScoringWeightsSchema(BaseModel):
    weight_required_skills: float = Field(default=35.0, ge=0, le=100)
    weight_semantic_similarity: float = Field(default=25.0, ge=0, le=100)
    weight_experience: float = Field(default=20.0, ge=0, le=100)
    weight_preferred_skills: float = Field(default=10.0, ge=0, le=100)
    weight_education: float = Field(default=10.0, ge=0, le=100)

class JobRequirementsSchema(BaseModel):
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    min_experience_years: float = 0.0
    education_requirements: List[str] = []
    certifications: List[str] = []
    domain_keywords: List[str] = []

class ScreeningSessionCreate(BaseModel):
    job_title: str
    department: Optional[str] = None
    job_description: str
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_experience_years: Optional[float] = None
    education_requirements: Optional[List[str]] = None
    scoring_weights: Optional[ScoringWeightsSchema] = None
    overqualification_enabled: bool = True

class ResumeSubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    parsing_status: str
    error_message: Optional[str] = None
    uploaded_at: datetime

class ScreeningSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_title: str
    department: Optional[str] = None
    job_description: str
    extracted_requirements: Optional[Dict[str, Any]] = None
    scoring_weights: Optional[Dict[str, Any]] = None
    overqualification_enabled: bool
    processing_status: str
    total_resumes: int
    processed_resumes: int
    failed_resumes: int
    created_at: datetime
    updated_at: datetime

class CandidateDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    extracted_profile: Optional[Dict[str, Any]] = None
    resume_text: Optional[str] = None
    created_at: datetime

class ScreeningResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    screening_session_id: int
    candidate_id: int
    candidate_name: str
    candidate_email: Optional[str] = None
    final_match_score: float
    component_scores: Dict[str, float]
    matched_skills: List[str] = []
    missing_required_skills: List[str] = []
    relevant_experience: float
    matching_explanation: Dict[str, Any]
    overqualification_status: str
    overqualification_confidence: float
    overqualification_evidence: Optional[Dict[str, Any]] = None
    review_status: str = "pending"
    recruiter_notes: Optional[str] = None
    override_reason: Optional[str] = None
    created_at: datetime

class RecruiterReviewUpdate(BaseModel):
    review_status: str = Field(..., pattern=r"^(pending|shortlisted|under_review|rejected)$")
    recruiter_notes: Optional[str] = None
    override_reason: Optional[str] = None

class SystemHealthResponse(BaseModel):
    status: str
    database: str
    ai_model_loaded: bool
    model_name: str
    version: str
