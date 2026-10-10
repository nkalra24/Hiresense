from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.core.config import settings
from app.schemas import ScoringWeightsSchema
from app.models import ScreeningSession, ScreeningResult, Candidate, RecruiterReview

router = APIRouter(prefix="/settings", tags=["Settings & Analytics"])

@router.get("/scoring", response_model=ScoringWeightsSchema)
def get_scoring_weights():
    return ScoringWeightsSchema(
        weight_required_skills=settings.DEFAULT_WEIGHT_REQUIRED_SKILLS,
        weight_semantic_similarity=settings.DEFAULT_WEIGHT_SEMANTIC_SIMILARITY,
        weight_experience=settings.DEFAULT_WEIGHT_EXPERIENCE,
        weight_preferred_skills=settings.DEFAULT_WEIGHT_PREFERRED_SKILLS,
        weight_education=settings.DEFAULT_WEIGHT_EDUCATION
    )

@router.patch("/scoring", response_model=ScoringWeightsSchema)
def update_scoring_weights(new_weights: ScoringWeightsSchema):
    settings.DEFAULT_WEIGHT_REQUIRED_SKILLS = new_weights.weight_required_skills
    settings.DEFAULT_WEIGHT_SEMANTIC_SIMILARITY = new_weights.weight_semantic_similarity
    settings.DEFAULT_WEIGHT_EXPERIENCE = new_weights.weight_experience
    settings.DEFAULT_WEIGHT_PREFERRED_SKILLS = new_weights.weight_preferred_skills
    settings.DEFAULT_WEIGHT_EDUCATION = new_weights.weight_education
    return new_weights

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Computes real database metrics for the recruiter dashboard.
    No hardcoded statistics.
    """
    total_sessions = db.query(func.count(ScreeningSession.id)).scalar() or 0
    total_processed = db.query(func.sum(ScreeningSession.processed_resumes)).scalar() or 0

    all_scores = [r[0] for r in db.query(ScreeningResult.final_match_score).all()]
    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0
    high_fit_count = sum(1 for s in all_scores if s >= 75.0)

    # Score Distribution Buckets for Chart
    distribution = [
        {"range": "0-20%", "count": sum(1 for s in all_scores if 0 <= s <= 20)},
        {"range": "21-40%", "count": sum(1 for s in all_scores if 20 < s <= 40)},
        {"range": "41-60%", "count": sum(1 for s in all_scores if 40 < s <= 60)},
        {"range": "61-80%", "count": sum(1 for s in all_scores if 60 < s <= 80)},
        {"range": "81-100%", "count": sum(1 for s in all_scores if 80 < s <= 100)},
    ]

    # Recent Screenings
    recent_screenings = db.query(ScreeningSession).order_by(ScreeningSession.created_at.desc()).limit(5).all()

    # Recent Candidate Activity
    recent_reviews = db.query(RecruiterReview, Candidate, ScreeningSession).\
        join(Candidate, RecruiterReview.candidate_id == Candidate.id).\
        join(ScreeningSession, RecruiterReview.screening_session_id == ScreeningSession.id).\
        order_by(RecruiterReview.updated_at.desc()).limit(6).all()

    activities = []
    for review, cand, session in recent_reviews:
        activities.append({
            "candidate_name": cand.name,
            "job_title": session.job_title,
            "session_id": session.id,
            "review_status": review.review_status,
            "updated_at": review.updated_at
        })

    return {
        "total_sessions": total_sessions,
        "total_resumes_processed": int(total_processed),
        "average_score": avg_score,
        "high_fit_candidates": high_fit_count,
        "distribution": distribution,
        "recent_screenings": [
            {
                "id": s.id,
                "job_title": s.job_title,
                "department": s.department,
                "processing_status": s.processing_status,
                "total_resumes": s.total_resumes,
                "processed_resumes": s.processed_resumes,
                "created_at": s.created_at
            }
            for s in recent_screenings
        ],
        "recent_activity": activities
    }
