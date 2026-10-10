from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Candidate, ScreeningResult, ScreeningSession, RecruiterReview
from app.schemas import CandidateDetail

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.get("", response_model=List[CandidateDetail])
def list_candidates(
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Candidate)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(Candidate.name.ilike(search_pattern) | Candidate.email.ilike(search_pattern))

    candidates = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()
    return candidates

@router.get("/{id}")
def get_candidate(id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Fetch screening results for this candidate across all sessions
    results = db.query(ScreeningResult, ScreeningSession, RecruiterReview).\
        join(ScreeningSession, ScreeningResult.screening_session_id == ScreeningSession.id).\
        outerjoin(
            RecruiterReview,
            (RecruiterReview.screening_session_id == ScreeningResult.screening_session_id) &
            (RecruiterReview.candidate_id == ScreeningResult.candidate_id)
        ).\
        filter(ScreeningResult.candidate_id == id).all()

    screenings_history = []
    for res, session, review in results:
        screenings_history.append({
            "session_id": session.id,
            "job_title": session.job_title,
            "department": session.department,
            "screening_date": session.created_at,
            "match_score": res.final_match_score,
            "overqualification_status": res.overqualification_status,
            "review_status": review.review_status if review else "pending",
            "recruiter_notes": review.recruiter_notes if review else None
        })

    return {
        "candidate": CandidateDetail.model_validate(candidate),
        "screenings_history": screenings_history
    }

@router.delete("/{id}")
def delete_candidate(id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.delete(candidate)
    db.commit()
    return {"message": "Candidate record and associated results removed successfully"}
