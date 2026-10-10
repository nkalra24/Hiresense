from app.ml.skills_normalizer import canonicalize_skill, extract_skills_from_text
from app.ml.scoring_engine import calculate_candidate_score
from app.ml.overqualification import detect_overqualification, ADVISORY_DISCLAIMER
from app.parsers.job_parser import parse_job_description

def test_skill_normalization():
    assert canonicalize_skill("js") == "JavaScript"
    assert canonicalize_skill("postgres") == "PostgreSQL"
    assert canonicalize_skill("k8s") == "Kubernetes"
    assert canonicalize_skill("py") == "Python"
    assert canonicalize_skill("react.js") == "React"

def test_explicit_vs_inferred_skills():
    text = """
    John Doe
    Technical Skills: Python, React, PostgreSQL
    Work Experience:
    Software Engineer at Acme Corp. Built cloud services using Docker and Kubernetes.
    """
    res = extract_skills_from_text(text)
    assert "Python" in res["explicit_skills"]
    assert "React" in res["explicit_skills"]
    assert "Docker" in res["inferred_skills"] or "Docker" in res["explicit_skills"]

def test_job_description_parsing():
    jd = """
    Job Title: Senior Backend Developer
    Requirements:
    - 5+ years of experience with Python and FastAPI
    - Strong database skills with PostgreSQL
    - Bachelor's Degree in Computer Science
    Preferred Qualifications:
    - Experience with Docker and Redis
    """
    parsed = parse_job_description("Senior Backend Developer", jd)
    assert "Python" in parsed["required_skills"]
    assert "FastAPI" in parsed["required_skills"]
    assert "PostgreSQL" in parsed["required_skills"]
    assert "Docker" in parsed["preferred_skills"] or "Redis" in parsed["preferred_skills"]
    assert parsed["min_experience_years"] == 5.0
    assert any("Bachelor" in e for e in parsed["education_requirements"])

def test_weighted_scoring_calculation():
    cand_profile = {
        "all_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "years_experience": 5.0,
        "education": ["Bachelor's Degree"],
        "certifications": []
    }
    job_reqs = {
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "preferred_skills": ["Docker", "Kubernetes"],
        "min_experience_years": 4.0,
        "education_requirements": ["Bachelor's Degree"],
        "certifications": []
    }
    jd_text = "Looking for a Python FastAPI engineer with PostgreSQL and Docker experience."
    resume_text = "Experienced Python developer with FastAPI, PostgreSQL, Docker, and 5 years experience."

    result = calculate_candidate_score(
        candidate_profile=cand_profile,
        job_requirements=job_reqs,
        job_description=jd_text,
        resume_text=resume_text
    )

    assert result["final_match_score"] >= 75.0
    assert result["component_scores"]["required_skills"] == 100.0
    assert result["component_scores"]["preferred_skills"] == 50.0  # 1 of 2
    assert "Python" in result["matched_skills"]
    assert len(result["missing_required_skills"]) == 0
    assert "strengths" in result["matching_explanation"]

def test_overqualification_detection():
    # Executive / Tech Lead applying for Junior / Mid Role
    cand_profile = {
        "years_experience": 12.0,
        "previous_titles": ["VP of Engineering", "Technical Lead"],
        "education": ["Master's Degree"],
    }
    ov = detect_overqualification(
        candidate_profile=cand_profile,
        job_title="Junior Software Engineer",
        min_exp_required=1.0
    )

    assert ov["status"] == "Potentially Overqualified"
    assert ov["confidence"] >= 0.70
    assert ov["disclaimer"] == ADVISORY_DISCLAIMER
    assert len(ov["evidence"]) > 0

def test_standard_fit_not_overqualified():
    cand_profile = {
        "years_experience": 3.0,
        "previous_titles": ["Software Engineer"],
        "education": ["Bachelor's Degree"],
    }
    ov = detect_overqualification(
        candidate_profile=cand_profile,
        job_title="Software Engineer",
        min_exp_required=3.0
    )

    assert ov["status"] == "No Clear Overqualification Signal"
