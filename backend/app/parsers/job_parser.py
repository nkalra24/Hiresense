import re
from typing import Dict, Any, List
from app.ml.skills_normalizer import extract_skills_from_text, canonicalize_skill
from app.parsers.resume_parser import DEGREE_PATTERNS, CERTIFICATION_PATTERNS

def parse_job_description(title: str, text: str) -> Dict[str, Any]:
    """
    Analyzes job description to automatically extract structured criteria:
    required skills, preferred skills, min experience, education requirements, certifications.
    """
    # 1. Split sections into Required vs Preferred
    required_text = ""
    preferred_text = ""

    # Patterns to find 'preferred / nice to have'
    pref_match = re.search(
        r'(?:preferred|nice to have|bonus points|good to have|desired qualifications)[:\s\n]+(.*?)(?=\n\s*(?:about us|benefits|compensation|responsibilities|$))',
        text, re.IGNORECASE | re.DOTALL
    )
    if pref_match:
        preferred_text = pref_match.group(1)

    # Patterns to find 'required / minimum qualifications'
    req_match = re.search(
        r'(?:required|requirements|minimum qualifications|must have|what you bring)[:\s\n]+(.*?)(?=\n\s*(?:preferred|nice to have|benefits|compensation|$))',
        text, re.IGNORECASE | re.DOTALL
    )
    if req_match:
        required_text = req_match.group(1)

    # Extract skills from sections
    req_skills_data = extract_skills_from_text(required_text or text)
    pref_skills_data = extract_skills_from_text(preferred_text)

    # Deduplicate: if skill is in both, required takes precedence
    required_skills = sorted(list(set(req_skills_data["explicit_skills"] + req_skills_data["inferred_skills"])))
    preferred_skills = sorted(list(set(pref_skills_data["explicit_skills"] + pref_skills_data["inferred_skills"]) - set(required_skills)))

    # 2. Extract Minimum Years of Experience
    min_exp = 0.0
    exp_matches = re.findall(r'(\d{1,2})\+?\s*(?:years|yrs)(?:\s+of)?(?:\s+relevant)?\s+experience', text, re.IGNORECASE)
    if exp_matches:
        try:
            # Take the lowest explicit required years or first mentioned
            min_exp = float(exp_matches[0])
        except ValueError:
            min_exp = 0.0

    # 3. Extract Education Requirements
    education_reqs = []
    for pattern, label in DEGREE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            education_reqs.append(label)

    # 4. Certifications
    certs = []
    for pattern in CERTIFICATION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            certs.append(m.strip())

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "min_experience_years": min_exp,
        "education_requirements": sorted(list(set(education_reqs))),
        "certifications": sorted(list(set(certs))),
    }
