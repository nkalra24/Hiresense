import os
import json
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Query, Response
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.models import ScreeningSession, ResumeSubmission, ScreeningResult, Candidate, RecruiterReview
from app.schemas import (
    ScreeningSessionResponse,
    ScreeningResultResponse,
    RecruiterReviewUpdate,
    ResumeSubmissionResponse
)
from app.parsers.job_parser import parse_job_description
from app.services.screening_service import process_screening_session
from app.services.export_service import generate_csv_report, generate_pdf_report

router = APIRouter(prefix="/screenings", tags=["Screenings"])

@router.post("", response_model=ScreeningSessionResponse)
async def create_screening_session(
    background_tasks: BackgroundTasks,
    job_title: str = Form(...),
    department: Optional[str] = Form(None),
    job_description: str = Form(...),
    required_skills: Optional[str] = Form(None),  # JSON array string or comma separated
    preferred_skills: Optional[str] = Form(None),
    min_experience_years: Optional[float] = Form(None),
    education_requirements: Optional[str] = Form(None),
    scoring_weights: Optional[str] = Form(None),   # JSON string
    overqualification_enabled: bool = Form(True),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one resume file must be uploaded")

    # 1. Parse or merge job requirements
    parsed_reqs = parse_job_description(job_title, job_description)

    # Process overrides if recruiter provided manual skills
    if required_skills:
        try:
            req_list = json.loads(required_skills) if required_skills.startswith("[") else [s.strip() for s in required_skills.split(",") if s.strip()]
            parsed_reqs["required_skills"] = req_list
        except Exception:
            pass

    if preferred_skills:
        try:
            pref_list = json.loads(preferred_skills) if preferred_skills.startswith("[") else [s.strip() for s in preferred_skills.split(",") if s.strip()]
            parsed_reqs["preferred_skills"] = pref_list
        except Exception:
            pass

    if min_experience_years is not None and min_experience_years > 0:
        parsed_reqs["min_experience_years"] = min_experience_years

    if education_requirements:
        try:
            edu_list = json.loads(education_requirements) if education_requirements.startswith("[") else [e.strip() for e in education_requirements.split(",") if e.strip()]
            parsed_reqs["education_requirements"] = edu_list
        except Exception:
            pass

    # Weights
    weights = {
        "weight_required_skills": settings.DEFAULT_WEIGHT_REQUIRED_SKILLS,
        "weight_semantic_similarity": settings.DEFAULT_WEIGHT_SEMANTIC_SIMILARITY,
        "weight_experience": settings.DEFAULT_WEIGHT_EXPERIENCE,
        "weight_preferred_skills": settings.DEFAULT_WEIGHT_PREFERRED_SKILLS,
        "weight_education": settings.DEFAULT_WEIGHT_EDUCATION,
    }
    if scoring_weights:
        try:
            custom_w = json.loads(scoring_weights)
            weights.update(custom_w)
        except Exception:
            pass

    # Create ScreeningSession record
    session = ScreeningSession(
        job_title=job_title.strip(),
        department=department.strip() if department else None,
        job_description=job_description.strip(),
        extracted_requirements=parsed_reqs,
        scoring_weights=weights,
        overqualification_enabled=overqualification_enabled,
        processing_status="queued",
        total_resumes=len(files),
        processed_resumes=0,
        failed_resumes=0
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Session storage folder
    session_upload_dir = settings.UPLOAD_DIR / f"session_{session.id}"
    session_upload_dir.mkdir(parents=True, exist_ok=True)

    seen_filenames = set()
    for file in files:
        # Validate filename and duplicate in this session
        orig_name = os.path.basename(file.filename or "resume.pdf")
        if orig_name in seen_filenames:
            continue
        seen_filenames.add(orig_name)

        ext = os.path.splitext(orig_name)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            # Skip unsupported file or record as failed
            continue

        unique_name = f"{uuid.uuid4().hex}_{orig_name}"
        stored_path = session_upload_dir / unique_name

        with open(stored_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        submission = ResumeSubmission(
            screening_session_id=session.id,
            original_filename=orig_name,
            stored_file_path=str(stored_path),
            parsing_status="queued"
        )
        db.add(submission)

    db.commit()

    # Trigger background processing
    background_tasks.add_task(process_screening_session, session.id, db)

    return session


@router.get("", response_model=List[ScreeningSessionResponse])
def list_screenings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    sessions = db.query(ScreeningSession).order_by(ScreeningSession.created_at.desc()).offset(skip).limit(limit).all()
    return sessions


@router.get("/{id}", response_model=ScreeningSessionResponse)
def get_screening(id: int, db: Session = Depends(get_db)):
    session = db.query(ScreeningSession).filter(ScreeningSession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Screening session not found")
    return session


@router.delete("/{id}")
def delete_screening(id: int, db: Session = Depends(get_db)):
    session = db.query(ScreeningSession).filter(ScreeningSession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Screening session not found")

    # Clean stored files
    session_upload_dir = settings.UPLOAD_DIR / f"session_{session.id}"
    if session_upload_dir.exists():
        shutil.rmtree(session_upload_dir, ignore_errors=True)

    db.delete(session)
    db.commit()
    return {"message": "Screening session and all associated files deleted successfully"}


@router.post("/{id}/analyze")
def trigger_analysis(id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    session = db.query(ScreeningSession).filter(ScreeningSession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Screening session not found")

    background_tasks.add_task(process_screening_session, session.id, db)
    return {"message": "Analysis started in background", "status": "processing"}


@router.get("/{id}/status")
def get_screening_status(id: int, db: Session = Depends(get_db)):
    session = db.query(ScreeningSession).filter(ScreeningSession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Screening session not found")

    submissions = db.query(ResumeSubmission).filter(ResumeSubmission.screening_session_id == id).all()

    return {
        "id": session.id,
        "processing_status": session.processing_status,
        "total_resumes": session.total_resumes,
        "processed_resumes": session.processed_resumes,
        "failed_resumes": session.failed_resumes,
        "submissions": [
            {
                "id": s.id,
                "original_filename": s.original_filename,
                "parsing_status": s.parsing_status,
                "error_message": s.error_message
            }
            for s in submissions
        ]
    }


def fetch_ranked_results(
    db: Session,
    session_id: int,
    search: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    overqualification: Optional[str] = None,
    sort_by: str = "score_desc",
    skip: int = 0,
    limit: int = 50
) -> List[ScreeningResultResponse]:
    query = db.query(ScreeningResult, Candidate, RecruiterReview).\
        join(Candidate, ScreeningResult.candidate_id == Candidate.id).\
        outerjoin(
            RecruiterReview,
            (RecruiterReview.screening_session_id == ScreeningResult.screening_session_id) &
            (RecruiterReview.candidate_id == ScreeningResult.candidate_id)
        ).\
        filter(ScreeningResult.screening_session_id == session_id)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(Candidate.name.ilike(search_pattern) | Candidate.email.ilike(search_pattern))

    if min_score is not None:
        query = query.filter(ScreeningResult.final_match_score >= min_score)

    if max_score is not None:
        query = query.filter(ScreeningResult.final_match_score <= max_score)

    if overqualification:
        query = query.filter(ScreeningResult.overqualification_status.ilike(f"%{overqualification}%"))

    # Sorting
    if sort_by == "score_asc":
        query = query.order_by(ScreeningResult.final_match_score.asc())
    elif sort_by == "exp_desc":
        query = query.order_by(ScreeningResult.relevant_experience.desc())
    else:
        query = query.order_by(ScreeningResult.final_match_score.desc())

    records = query.offset(skip).limit(limit).all()

    response_list = []
    for res, cand, review in records:
        response_list.append(
            ScreeningResultResponse(
                id=res.id,
                screening_session_id=res.screening_session_id,
                candidate_id=res.candidate_id,
                candidate_name=cand.name,
                candidate_email=cand.email,
                final_match_score=res.final_match_score,
                component_scores=res.component_scores,
                matched_skills=res.matched_skills or [],
                missing_required_skills=res.missing_required_skills or [],
                relevant_experience=res.relevant_experience,
                matching_explanation=res.matching_explanation or {},
                overqualification_status=res.overqualification_status,
                overqualification_confidence=res.overqualification_confidence,
                overqualification_evidence=res.overqualification_evidence,
                review_status=review.review_status if review else "pending",
                recruiter_notes=review.recruiter_notes if review else None,
                override_reason=review.override_reason if review else None,
                created_at=res.created_at
            )
        )

    return response_list


@router.get("/{id}/results", response_model=List[ScreeningResultResponse])
def get_screening_results(
    id: int,
    search: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    overqualification: Optional[str] = Query(None),
    sort_by: str = Query("score_desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return fetch_ranked_results(
        db=db,
        session_id=id,
        search=search,
        min_score=min_score,
        max_score=max_score,
        overqualification=overqualification,
        sort_by=sort_by,
        skip=skip,
        limit=limit
    )


@router.get("/{screening_id}/candidates/{candidate_id}")
def get_candidate_session_detail(
    screening_id: int,
    candidate_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(ScreeningSession).filter(ScreeningSession.id == screening_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Screening session not found")

    cand = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")

    res = db.query(ScreeningResult).filter(
        ScreeningResult.screening_session_id == screening_id,
        ScreeningResult.candidate_id == candidate_id
    ).first()

    review = db.query(RecruiterReview).filter(
        RecruiterReview.screening_session_id == screening_id,
        RecruiterReview.candidate_id == candidate_id
    ).first()

    return {
        "candidate": {
            "id": cand.id,
            "name": cand.name,
            "email": cand.email,
            "phone": cand.phone,
            "extracted_profile": cand.extracted_profile,
            "resume_text": cand.resume_text,
            "created_at": cand.created_at
        },
        "session": {
            "id": session.id,
            "job_title": session.job_title,
            "job_description": session.job_description,
            "extracted_requirements": session.extracted_requirements,
            "overqualification_enabled": session.overqualification_enabled
        },
        "result": {
            "final_match_score": res.final_match_score if res else 0.0,
            "component_scores": res.component_scores if res else {},
            "matched_skills": res.matched_skills if res else [],
            "missing_required_skills": res.missing_required_skills if res else [],
            "relevant_experience": res.relevant_experience if res else 0.0,
            "matching_explanation": res.matching_explanation if res else {},
            "overqualification_status": res.overqualification_status if res else "No Clear Overqualification Signal",
            "overqualification_confidence": res.overqualification_confidence if res else 0.0,
            "overqualification_evidence": res.overqualification_evidence if res else {}
        } if res else None,
        "review": {
            "review_status": review.review_status if review else "pending",
            "recruiter_notes": review.recruiter_notes if review else None,
            "override_reason": review.override_reason if review else None,
            "updated_at": review.updated_at if review else None
        } if review else None
    }


@router.patch("/{screening_id}/candidates/{candidate_id}/review")
def update_recruiter_review(
    screening_id: int,
    candidate_id: int,
    review_in: RecruiterReviewUpdate,
    db: Session = Depends(get_db)
):
    review = db.query(RecruiterReview).filter(
        RecruiterReview.screening_session_id == screening_id,
        RecruiterReview.candidate_id == candidate_id
    ).first()

    if not review:
        review = RecruiterReview(
            screening_session_id=screening_id,
            candidate_id=candidate_id,
            review_status=review_in.review_status,
            recruiter_notes=review_in.recruiter_notes,
            override_reason=review_in.override_reason
        )
        db.add(review)
    else:
        review.review_status = review_in.review_status
        if review_in.recruiter_notes is not None:
            review.recruiter_notes = review_in.recruiter_notes
        if review_in.override_reason is not None:
            review.override_reason = review_in.override_reason

    db.commit()
    db.refresh(review)
    return {
        "message": "Recruiter review updated successfully",
        "review_status": review.review_status,
        "recruiter_notes": review.recruiter_notes,
        "override_reason": review.override_reason
    }


@router.get("/{id}/export/csv")
def export_csv(id: int, db: Session = Depends(get_db)):
    session = db.query(ScreeningSession).filter(ScreeningSession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Screening session not found")

    results_data = fetch_ranked_results(db=db, session_id=id, limit=500)
    raw_dicts = [r.model_dump() for r in results_data]

    csv_content = generate_csv_report(session.job_title, raw_dicts)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="hiresense_report_session_{id}.csv"'}
    )


@router.get("/{id}/export/pdf")
def export_pdf(id: int, db: Session = Depends(get_db)):
    session = db.query(ScreeningSession).filter(ScreeningSession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Screening session not found")

    results_data = fetch_ranked_results(db=db, session_id=id, limit=500)
    raw_dicts = [r.model_dump() for r in results_data]

    pdf_bytes = generate_pdf_report(
        session_data={
            "job_title": session.job_title,
            "created_at": session.created_at,
        },
        results=raw_dicts
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="hiresense_report_session_{id}.pdf"'}
    )
