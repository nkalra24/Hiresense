import os
import shutil
import uuid
from pathlib import Path
from app.db.session import SessionLocal, Base, engine
from app.models import ScreeningSession, ResumeSubmission, RecruiterReview
from app.parsers.job_parser import parse_job_description
from app.services.screening_service import process_screening_session
from app.core.config import settings

def seed_initial_demo():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(ScreeningSession).count() > 0:
            print("Database already contains screening sessions. Skipping initial seed.")
            return

        print("Seeding initial screening session with synthetic resumes...")
        sample_dir = Path(__file__).resolve().parent.parent / "sample_resumes"
        sample_files = list(sample_dir.glob("*.pdf")) + list(sample_dir.glob("*.docx"))

        job_title = "Senior Full-Stack & AI Engineer"
        department = "Core Intelligence"
        job_desc = """We are seeking a Senior Full-Stack & AI Engineer to build scalable cloud SaaS architectures and deploy generative AI & machine learning pipelines.
        
Requirements:
- 4+ years of hands-on software development experience.
- Strong proficiency in Python, FastAPI, React, and TypeScript.
- Relational database modeling with PostgreSQL and containerization with Docker.
- Experience building REST APIs and microservice architectures.

Preferred Qualifications:
- Demonstrated knowledge of PyTorch, Transformers, NLP, and Hugging Face.
- Experience with Kubernetes and cloud architecture on AWS.
- Bachelor's or Master's degree in Computer Science."""

        parsed_reqs = parse_job_description(job_title, job_desc)
        session = ScreeningSession(
            job_title=job_title,
            department=department,
            job_description=job_desc,
            extracted_requirements=parsed_reqs,
            scoring_weights={
                "weight_required_skills": 35.0,
                "weight_semantic_similarity": 25.0,
                "weight_experience": 20.0,
                "weight_preferred_skills": 10.0,
                "weight_education": 10.0,
            },
            overqualification_enabled=True,
            processing_status="queued",
            total_resumes=len(sample_files),
            processed_resumes=0,
            failed_resumes=0
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        session_upload_dir = settings.UPLOAD_DIR / f"session_{session.id}"
        session_upload_dir.mkdir(parents=True, exist_ok=True)

        for fpath in sample_files:
            unique_name = f"{uuid.uuid4().hex}_{fpath.name}"
            dest = session_upload_dir / unique_name
            shutil.copy2(fpath, dest)

            sub = ResumeSubmission(
                screening_session_id=session.id,
                original_filename=fpath.name,
                stored_file_path=str(dest),
                parsing_status="queued"
            )
            db.add(sub)
        db.commit()

        # Run analysis pipeline
        print("Executing AI screening pipeline on sample resumes...")
        process_screening_session(session.id, db)

        # Update sample recruiter decisions
        reviews = db.query(RecruiterReview).filter(RecruiterReview.screening_session_id == session.id).all()
        if reviews:
            # Shortlist first
            reviews[0].review_status = "shortlisted"
            reviews[0].recruiter_notes = "Exceptional fit across core requirements. Fast-track to technical architecture interview."
            if len(reviews) > 1:
                reviews[1].review_status = "under_review"
                reviews[1].recruiter_notes = "Solid portfolio and clean work history. Awaiting recruiter screening call."
            db.commit()

        print("Seeding completed successfully! Dashboard and results populated.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_initial_demo()
