import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, Base, engine

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"

@pytest.fixture(scope="module")
def client():
    # Setup test DB tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["database"] == "connected"

def test_settings_scoring_endpoint(client):
    res = client.get("/api/settings/scoring")
    assert res.status_code == 200
    data = res.json()
    assert data["weight_required_skills"] == 35.0
    assert data["weight_semantic_similarity"] == 25.0

def test_create_and_process_screening_session(client):
    # Prepare files
    pdf_files = list(SAMPLE_DIR.glob("*.pdf")) + list(SAMPLE_DIR.glob("*.docx"))
    assert len(pdf_files) >= 5, "Must have at least 5 sample resumes"

    file_tuples = []
    opened_files = []
    for p in pdf_files:
        f = open(p, "rb")
        opened_files.append(f)
        file_tuples.append(("files", (p.name, f, "application/octet-stream")))

    try:
        response = client.post(
            "/api/screenings",
            data={
                "job_title": "Senior AI & Full Stack Engineer",
                "department": "Engineering",
                "job_description": """
                We are seeking a Senior AI & Full Stack Engineer with strong experience in Python,
                FastAPI, React, TypeScript, and modern Machine Learning pipelines.
                Requirements:
                - 4+ years of software engineering experience
                - Hands-on proficiency in Python, FastAPI, React, and TypeScript
                - Solid understanding of PostgreSQL and Docker
                Preferred:
                - Knowledge of PyTorch, Transformers, and Kubernetes
                - Degree in Computer Science or related engineering discipline
                """,
                "min_experience_years": 4.0,
                "overqualification_enabled": True
            },
            files=file_tuples
        )
        assert response.status_code == 200
        session_data = response.json()
        session_id = session_data["id"]
        assert session_data["total_resumes"] == len(pdf_files)

        # Trigger processing (runs synchronously when called directly in test or wait for background)
        from app.services.screening_service import process_screening_session
        db = SessionLocal()
        try:
            process_screening_session(session_id, db)
        finally:
            db.close()

        # Check status
        status_res = client.get(f"/api/screenings/{session_id}/status")
        assert status_res.status_code == 200
        assert status_res.json()["processed_resumes"] >= 4

        # Fetch ranked results
        results_res = client.get(f"/api/screenings/{session_id}/results")
        assert results_res.status_code == 200
        results = results_res.json()
        assert len(results) >= 4

        # Check rankings are sorted by final_match_score descending
        scores = [r["final_match_score"] for r in results]
        assert scores == sorted(scores, reverse=True), "Candidates must be ordered by match score desc"

        # Verify Elena and Marcus have strong scores
        top_candidate = results[0]
        assert top_candidate["final_match_score"] > 60.0
        assert "strengths" in top_candidate["matching_explanation"]
        assert "required_skills" in top_candidate["component_scores"]

        # Recruiter review action: shortlist top candidate
        candidate_id = top_candidate["candidate_id"]
        patch_res = client.patch(
            f"/api/screenings/{session_id}/candidates/{candidate_id}/review",
            json={
                "review_status": "shortlisted",
                "recruiter_notes": "Impressive profile, schedule technical screen.",
                "override_reason": "Direct experience with required tech stack."
            }
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["review_status"] == "shortlisted"

        # Export CSV
        csv_res = client.get(f"/api/screenings/{session_id}/export/csv")
        assert csv_res.status_code == 200
        assert "text/csv" in csv_res.headers["content-type"]
        assert "Rank,Candidate Name" in csv_res.text

        # Export PDF
        pdf_res = client.get(f"/api/screenings/{session_id}/export/pdf")
        assert pdf_res.status_code == 200
        assert "application/pdf" in pdf_res.headers["content-type"]
        assert len(pdf_res.content) > 1000

        # Dashboard stats check
        stats_res = client.get("/api/settings/stats")
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_sessions"] >= 1
        assert stats["total_resumes_processed"] >= 4
        assert stats["average_score"] > 0

    finally:
        for f in opened_files:
            f.close()
