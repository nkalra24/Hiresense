from typing import Dict, Any, List
from app.core.config import settings

ADVISORY_DISCLAIMER = (
    "Overqualification is an advisory signal based on the available resume and job requirements. "
    "It does not establish a candidate's interest, salary expectations, retention likelihood, or willingness to accept the role."
)

EXECUTIVE_TITLES = {
    "Chief Technology Officer", "CTO", "VP of Engineering", "Vice President",
    "Director of Engineering", "Head of Engineering", "Engineering Director"
}

SENIOR_TITLES = {
    "Technical Lead", "Tech Lead", "Principal Software Engineer",
    "Staff Software Engineer", "Engineering Manager"
}

def detect_overqualification(
    candidate_profile: Dict[str, Any],
    job_title: str,
    min_exp_required: float
) -> Dict[str, Any]:
    """
    Evaluates candidate credentials against job seniority.
    Provides explainable evidence without penalizing high-performing candidates.
    """
    cand_exp = float(candidate_profile.get("years_experience", 0.0))
    cand_titles = candidate_profile.get("previous_titles", [])
    cand_education = candidate_profile.get("education", [])

    is_entry_or_mid = not any(w in job_title.lower() for w in ["senior", "lead", "principal", "staff", "director", "head", "manager"])
    
    evidence_points: List[str] = []
    confidence = 0.0
    status = "No Clear Overqualification Signal"

    if cand_exp == 0.0 and not cand_titles:
        return {
            "status": "Insufficient Information",
            "confidence": 0.2,
            "evidence": ["Resume timeline dates could not be verified confidently."],
            "disclaimer": ADVISORY_DISCLAIMER
        }

    # 1. Experience Delta Check
    exp_delta = cand_exp - min_exp_required if min_exp_required > 0 else cand_exp - 3.0
    if min_exp_required > 0 and cand_exp >= (min_exp_required + settings.OVERQUALIFICATION_EXP_THRESHOLD_YEARS):
        evidence_points.append(
            f"Candidate has {cand_exp:.1f} years of documented experience, significantly exceeding the required {min_exp_required:.1f} years."
        )

    # 2. Seniority Mismatch (Executive / Manager titles applying for individual contributor)
    has_exec_title = any(t in EXECUTIVE_TITLES for t in cand_titles)
    has_senior_title = any(t in SENIOR_TITLES for t in cand_titles)

    if is_entry_or_mid and has_exec_title:
        evidence_points.append(
            f"Candidate previously held executive leadership titles ({', '.join([t for t in cand_titles if t in EXECUTIVE_TITLES])}) while target role is non-executive ({job_title})."
        )
    elif is_entry_or_mid and has_senior_title and cand_exp >= 7.0:
        evidence_points.append(
            f"Candidate holds documented leadership/staff engineering roles ({', '.join([t for t in cand_titles if t in SENIOR_TITLES])}) with {cand_exp:.1f} years experience."
        )

    # 3. Advanced degree check
    if is_entry_or_mid and "Ph.D." in cand_education and cand_exp >= 5.0:
        evidence_points.append("Candidate holds a Ph.D. with significant commercial industry experience.")

    # Determine classification
    if has_exec_title and is_entry_or_mid:
        status = "Potentially Overqualified"
        confidence = 0.85
    elif len(evidence_points) >= 2:
        status = "Potentially Overqualified"
        confidence = 0.75
    elif evidence_points:
        status = "Experience Exceeds Requirements"
        confidence = 0.65
    else:
        status = "No Clear Overqualification Signal"
        confidence = 0.90

    return {
        "status": status,
        "confidence": confidence,
        "evidence": evidence_points if evidence_points else ["Candidate credentials align well within expected role parameters."],
        "disclaimer": ADVISORY_DISCLAIMER
    }
