import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class ScreeningSession(Base):
    __tablename__ = "screening_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    job_description = Column(Text, nullable=False)
    extracted_requirements = Column(JSON, nullable=True)
    scoring_weights = Column(JSON, nullable=True)
    overqualification_enabled = Column(Boolean, default=True)
    processing_status = Column(String(50), default="queued")  # queued, processing, completed, failed
    total_resumes = Column(Integer, default=0)
    processed_resumes = Column(Integer, default=0)
    failed_resumes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    submissions = relationship("ResumeSubmission", back_populates="screening_session", cascade="all, delete-orphan")
    results = relationship("ScreeningResult", back_populates="screening_session", cascade="all, delete-orphan")
    reviews = relationship("RecruiterReview", back_populates="screening_session", cascade="all, delete-orphan")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, default="Unknown Candidate")
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(100), nullable=True)
    extracted_profile = Column(JSON, nullable=True)
    resume_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    submissions = relationship("ResumeSubmission", back_populates="candidate")
    results = relationship("ScreeningResult", back_populates="candidate")
    reviews = relationship("RecruiterReview", back_populates="candidate")


class ResumeSubmission(Base):
    __tablename__ = "resume_submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    screening_session_id = Column(Integer, ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="SET NULL"), nullable=True)
    original_filename = Column(String(255), nullable=False)
    stored_file_path = Column(String(512), nullable=False)
    file_hash = Column(String(64), nullable=True, index=True)
    parsing_status = Column(String(50), default="queued")  # queued, extracting, analyzing, completed, failed
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    screening_session = relationship("ScreeningSession", back_populates="submissions")
    candidate = relationship("Candidate", back_populates="submissions")


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    screening_session_id = Column(Integer, ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    final_match_score = Column(Float, nullable=False, default=0.0)
    component_scores = Column(JSON, nullable=False)
    matched_skills = Column(JSON, nullable=True)
    missing_required_skills = Column(JSON, nullable=True)
    relevant_experience = Column(Float, default=0.0)
    matching_explanation = Column(JSON, nullable=True)
    overqualification_status = Column(String(100), default="No Clear Overqualification Signal")
    overqualification_confidence = Column(Float, default=0.0)
    overqualification_evidence = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    screening_session = relationship("ScreeningSession", back_populates="results")
    candidate = relationship("Candidate", back_populates="results")


class RecruiterReview(Base):
    __tablename__ = "recruiter_reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    screening_session_id = Column(Integer, ForeignKey("screening_sessions.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    review_status = Column(String(50), default="pending")  # pending, shortlisted, under_review, rejected
    recruiter_notes = Column(Text, nullable=True)
    override_reason = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    screening_session = relationship("ScreeningSession", back_populates="reviews")
    candidate = relationship("Candidate", back_populates="reviews")
