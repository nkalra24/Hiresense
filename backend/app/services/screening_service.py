import logging
import hashlib
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import ScreeningSession, Candidate, ResumeSubmission, ScreeningResult, RecruiterReview
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.resume_parser import parse_resume
from app.ml.scoring_engine import calculate_candidate_score
from app.ml.overqualification import detect_overqualification

logger = logging.getLogger(__name__)

def compute_file_hash(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def process_screening_session(session_id: int, _db: Session = None):
    """
    Executes the resume parsing, AI analysis, scoring, and ranking pipeline.
    Updates granular statuses per resume and for the entire screening session.

    IMPORTANT: This function creates its own independent database session
    because FastAPI BackgroundTasks run AFTER the response is sent, meaning
    the dependency-injected session from the request handler may be closed.
    """
    # Always create an independent database session for background processing
    db = SessionLocal()
    try:
        _process_screening_impl(session_id, db)
    except Exception as e:
        logger.error(f"Critical error in screening session {session_id}: {e}", exc_info=True)
        try:
            session = db.query(ScreeningSession).filter(ScreeningSession.id == session_id).first()
            if session:
                session.processing_status = "failed"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


def _process_screening_impl(session_id: int, db: Session):
    """
    Internal implementation of the screening pipeline.
    Separated from the public function to ensure clean error handling and session management.
    """
    session = db.query(ScreeningSession).filter(ScreeningSession.id == session_id).first()
    if not session:
        logger.error(f"ScreeningSession {session_id} not found.")
        return

    session.processing_status = "processing"
    db.commit()

    submissions = db.query(ResumeSubmission).filter(ResumeSubmission.screening_session_id == session_id).all()
    job_reqs = session.extracted_requirements or {}
    job_desc = session.job_description or ""
    weights = session.scoring_weights

    processed_count = 0
    failed_count = 0

    for sub in submissions:
        file_path = Path(sub.stored_file_path)
        sub.parsing_status = "extracting"
        db.commit()

        resume_text = ""
        try:
            # 1. Text Extraction
            if file_path.suffix.lower() == ".pdf":
                resume_text = extract_text_from_pdf(file_path)
            elif file_path.suffix.lower() == ".docx":
                resume_text = extract_text_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

            if not resume_text or len(resume_text.strip()) < 20:
                raise ValueError("Resume contains insufficient extractable text or is empty")

            # Update hash
            sub.file_hash = compute_file_hash(file_path)

            # 2. Parsing structured candidate information
            sub.parsing_status = "analyzing"
            db.commit()

            logger.info(f"Parsing resume: {sub.original_filename}")
            parsed_profile = parse_resume(resume_text, sub.original_filename)
            logger.info(f"Parsed profile for {parsed_profile.get('name', 'Unknown')}: "
                       f"{len(parsed_profile.get('all_skills', []))} skills, "
                       f"{parsed_profile.get('years_experience', 0)} yrs exp")

            # 3. Candidate Persistence / Deduplication
            cand = None
            if parsed_profile.get("email"):
                cand = db.query(Candidate).filter(Candidate.email == parsed_profile["email"]).first()

            if not cand:
                cand = Candidate(
                    name=parsed_profile.get("name", "Unknown Candidate"),
                    email=parsed_profile.get("email"),
                    phone=parsed_profile.get("phone"),
                    extracted_profile=parsed_profile,
                    resume_text=resume_text
                )
                db.add(cand)
                db.flush()
            else:
                # Update existing candidate with latest profile details
                cand.extracted_profile = parsed_profile
                cand.resume_text = resume_text

            sub.candidate_id = cand.id

            # 4. Score Calculation
            logger.info(f"Calculating score for {cand.name} against '{session.job_title}'")
            score_data = calculate_candidate_score(
                candidate_profile=parsed_profile,
                job_requirements=job_reqs,
                job_description=job_desc,
                resume_text=resume_text,
                weights=weights
            )
            logger.info(f"Score for {cand.name}: {score_data['final_match_score']}/100")

            # 5. Overqualification Detection (if enabled)
            overqual_status = "No Clear Overqualification Signal"
            overqual_conf = 0.0
            overqual_ev = None

            if session.overqualification_enabled:
                min_exp = float(job_reqs.get("min_experience_years", 0.0))
                overqual = detect_overqualification(
                    candidate_profile=parsed_profile,
                    job_title=session.job_title,
                    min_exp_required=min_exp
                )
                overqual_status = overqual["status"]
                overqual_conf = overqual["confidence"]
                overqual_ev = {
                    "evidence": overqual["evidence"],
                    "disclaimer": overqual["disclaimer"]
                }

            # 6. Screening Result Persistence
            existing_result = db.query(ScreeningResult).filter(
                ScreeningResult.screening_session_id == session_id,
                ScreeningResult.candidate_id == cand.id
            ).first()

            if existing_result:
                existing_result.final_match_score = score_data["final_match_score"]
                existing_result.component_scores = score_data["component_scores"]
                existing_result.matched_skills = score_data["matched_skills"]
                existing_result.missing_required_skills = score_data["missing_required_skills"]
                existing_result.relevant_experience = score_data["relevant_experience"]
                existing_result.matching_explanation = score_data["matching_explanation"]
                existing_result.overqualification_status = overqual_status
                existing_result.overqualification_confidence = overqual_conf
                existing_result.overqualification_evidence = overqual_ev
            else:
                new_result = ScreeningResult(
                    screening_session_id=session_id,
                    candidate_id=cand.id,
                    final_match_score=score_data["final_match_score"],
                    component_scores=score_data["component_scores"],
                    matched_skills=score_data["matched_skills"],
                    missing_required_skills=score_data["missing_required_skills"],
                    relevant_experience=score_data["relevant_experience"],
                    matching_explanation=score_data["matching_explanation"],
                    overqualification_status=overqual_status,
                    overqualification_confidence=overqual_conf,
                    overqualification_evidence=overqual_ev
                )
                db.add(new_result)

            # Ensure RecruiterReview record exists
            review = db.query(RecruiterReview).filter(
                RecruiterReview.screening_session_id == session_id,
                RecruiterReview.candidate_id == cand.id
            ).first()
            if not review:
                db.add(RecruiterReview(
                    screening_session_id=session_id,
                    candidate_id=cand.id,
                    review_status="pending"
                ))

            sub.parsing_status = "completed"
            sub.error_message = None
            processed_count += 1

        except Exception as e:
            logger.error(f"Error processing resume {sub.original_filename}: {e}", exc_info=True)
            sub.parsing_status = "failed"
            sub.error_message = str(e)
            failed_count += 1

        db.commit()

    # Update session final status
    session.processed_resumes = processed_count
    session.failed_resumes = failed_count
    if processed_count == 0 and failed_count > 0:
        session.processing_status = "failed"
    else:
        session.processing_status = "completed"

    db.commit()
    logger.info(f"Screening session {session_id} completed: {processed_count} processed, {failed_count} failed")
