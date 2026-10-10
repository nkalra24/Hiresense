from typing import Dict, Any, List, Optional
from app.ml.similarity_engine import similarity_engine

def calculate_candidate_score(
    candidate_profile: Dict[str, Any],
    job_requirements: Dict[str, Any],
    job_description: str,
    resume_text: str,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes a multi-signal job-fit score with explainable component breakdowns.
    Dynamically normalizes weights if certain optional criteria are omitted from the job posting.
    """
    if weights is None:
        weights = {
            "weight_required_skills": 35.0,
            "weight_semantic_similarity": 25.0,
            "weight_experience": 20.0,
            "weight_preferred_skills": 10.0,
            "weight_education": 10.0,
        }

    cand_skills = set(candidate_profile.get("all_skills", []))
    req_skills = set(job_requirements.get("required_skills", []))
    pref_skills = set(job_requirements.get("preferred_skills", []))
    min_exp = float(job_requirements.get("min_experience_years", 0.0))
    cand_exp = float(candidate_profile.get("years_experience", 0.0))
    req_edu = set(job_requirements.get("education_requirements", []))
    cand_edu = set(candidate_profile.get("education", []))
    cand_certs = set(candidate_profile.get("certifications", []))

    # 1. Required Skills Score (0 - 100)
    matched_req_skills = sorted(list(req_skills.intersection(cand_skills)))
    missing_req_skills = sorted(list(req_skills - cand_skills))
    if req_skills:
        score_req_skills = (len(matched_req_skills) / len(req_skills)) * 100.0
    else:
        # If no specific required skills were isolated, measure overlap with all skills
        score_req_skills = 100.0 if cand_skills else 50.0

    # 2. Preferred Skills Score (0 - 100)
    matched_pref_skills = sorted(list(pref_skills.intersection(cand_skills)))
    has_pref_skills_criteria = len(pref_skills) > 0
    if has_pref_skills_criteria:
        score_pref_skills = (len(matched_pref_skills) / len(pref_skills)) * 100.0
    else:
        score_pref_skills = 100.0  # Neutral fallback

    # 3. Semantic Similarity Score (0 - 100)
    semantic_sim_raw = similarity_engine.compute_semantic_similarity(job_description, resume_text)
    score_semantic = round(semantic_sim_raw * 100.0, 1)

    # 4. Relevant Experience Score (0 - 100)
    if min_exp > 0:
        if cand_exp >= min_exp:
            # Full marks for meeting min experience; capped bonus for up to +3 years
            score_exp = min(100.0, 85.0 + ((cand_exp - min_exp) / 3.0) * 15.0)
        else:
            # Proportional score for having partial experience
            score_exp = max(10.0, (cand_exp / min_exp) * 80.0)
    else:
        # Default generous baseline based on general career length
        score_exp = min(100.0, 50.0 + (cand_exp * 10.0))

    # 5. Education & Certifications Score (0 - 100)
    has_edu_criteria = len(req_edu) > 0
    if has_edu_criteria:
        matched_edu = req_edu.intersection(cand_edu)
        if matched_edu:
            score_edu = 90.0 + (10.0 if cand_certs else 0.0)
        elif cand_edu:
            score_edu = 65.0 + (15.0 if cand_certs else 0.0)
        else:
            score_edu = 30.0 + (20.0 if cand_certs else 0.0)
    else:
        # Not required in JD: grant solid baseline without penalizing self-taught candidates
        score_edu = 80.0 if cand_edu else 70.0
        if cand_certs:
            score_edu = min(100.0, score_edu + 15.0)

    # Active weight redistribution
    active_weights = {}
    active_weights["weight_required_skills"] = weights.get("weight_required_skills", 35.0)
    active_weights["weight_semantic_similarity"] = weights.get("weight_semantic_similarity", 25.0)
    active_weights["weight_experience"] = weights.get("weight_experience", 20.0)
    
    if has_pref_skills_criteria:
        active_weights["weight_preferred_skills"] = weights.get("weight_preferred_skills", 10.0)
    if has_edu_criteria:
        active_weights["weight_education"] = weights.get("weight_education", 10.0)

    total_weight = sum(active_weights.values()) or 100.0

    final_score = (
        (score_req_skills * active_weights.get("weight_required_skills", 0.0)) +
        (score_semantic * active_weights.get("weight_semantic_similarity", 0.0)) +
        (score_exp * active_weights.get("weight_experience", 0.0)) +
        (score_pref_skills * active_weights.get("weight_preferred_skills", 0.0)) +
        (score_edu * active_weights.get("weight_education", 0.0))
    ) / total_weight

    final_score = round(max(0.0, min(100.0, final_score)), 1)

    # Generate Strengths, Gaps, and Explanation
    strengths = []
    gaps = []

    if matched_req_skills:
        strengths.append(f"Demonstrated core skills: {', '.join(matched_req_skills[:5])}")
    if matched_pref_skills:
        strengths.append(f"Preferred skills matched: {', '.join(matched_pref_skills[:3])}")
    if cand_exp >= min_exp and min_exp > 0:
        strengths.append(f"Meets or exceeds experience requirement with {cand_exp:.1f} years")
    if score_semantic >= 75.0:
        strengths.append("High contextual and semantic alignment with job responsibilities")
    if cand_certs:
        strengths.append(f"Relevant certifications: {', '.join(list(cand_certs)[:3])}")

    if missing_req_skills:
        gaps.append(f"Missing required skills: {', '.join(missing_req_skills[:5])}")
    if min_exp > 0 and cand_exp < min_exp:
        gaps.append(f"Experience ({cand_exp:.1f} yrs) is below stated requirement ({min_exp:.1f} yrs)")
    if score_semantic < 50.0:
        gaps.append("Lower semantic alignment with domain responsibilities")

    # Explainable Summary sentence
    if final_score >= 80.0:
        summary_text = f"Strong candidate demonstrating {score_req_skills:.0f}% required skill coverage and solid domain experience."
    elif final_score >= 60.0:
        summary_text = f"Moderate fit with relevant foundational background, but missing {len(missing_req_skills)} required qualification(s)."
    else:
        summary_text = f"Low fit for this role. Significant gaps in core required competencies and direct experience."

    return {
        "final_match_score": final_score,
        "component_scores": {
            "required_skills": round(score_req_skills, 1),
            "semantic_similarity": round(score_semantic, 1),
            "experience": round(score_exp, 1),
            "preferred_skills": round(score_pref_skills, 1),
            "education": round(score_edu, 1),
        },
        "matched_skills": sorted(list(set(matched_req_skills + matched_pref_skills))),
        "missing_required_skills": missing_req_skills,
        "relevant_experience": cand_exp,
        "matching_explanation": {
            "summary": summary_text,
            "strengths": strengths if strengths else ["Basic profile received"],
            "gaps": gaps if gaps else ["No major gaps identified against posted criteria"],
        }
    }
