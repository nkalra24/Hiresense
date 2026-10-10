import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.ml.skills_normalizer import extract_skills_from_text

# Common job titles for extraction and seniority detection
COMMON_TITLES = [
    "Chief Technology Officer", "CTO", "VP of Engineering", "Vice President",
    "Director of Engineering", "Engineering Manager", "Technical Lead", "Tech Lead",
    "Principal Software Engineer", "Staff Software Engineer", "Senior Software Engineer",
    "Lead Developer", "Software Architect", "Solutions Architect",
    "Senior Data Scientist", "Lead Data Scientist", "Senior ML Engineer",
    "Senior DevOps Engineer", "Senior Product Manager",
    "Software Engineer", "Full Stack Developer", "Backend Developer", "Frontend Developer",
    "Data Scientist", "Machine Learning Engineer", "DevOps Engineer", "Data Engineer",
    "Cloud Engineer", "System Administrator", "Product Manager", "QA Engineer",
    "Junior Software Engineer", "Associate Developer", "Intern", "Software Engineering Intern"
]

DEGREE_PATTERNS = [
    (r"\b(?:Ph\.?D|Doctor of Philosophy)\b", "Ph.D."),
    (r"\b(?:M\.?S\.?|Master(?:'s)?(?:\s+Degree)?|Master of Science|M\.?Tech|Master of Technology|M\.?A\.?|MBA|Master of Business Administration)\b", "Master's Degree"),
    (r"\b(?:B\.?S\.?|Bachelor(?:'s)?(?:\s+Degree)?|Bachelor of Science|B\.?Tech|Bachelor of Technology|B\.?E\.?|Bachelor of Engineering|B\.?A\.?)\b", "Bachelor's Degree"),
    (r"\b(?:Associate(?:'s)?(?:\s+Degree)?|Associate of Science|Associate of Arts)\b", "Associate Degree"),
    (r"\b(?:High School Diploma|GED)\b", "High School Diploma")
]

CERTIFICATION_PATTERNS = [
    r"AWS Certified\s*(?:[A-Za-z\s]+)?",
    r"Azure Certified\s*(?:[A-Za-z\s]+)?",
    r"Google Cloud Certified\s*(?:[A-Za-z\s]+)?",
    r"Kubernetes Administrator\s*(?:\(CKA\))?",
    r"Certified Kubernetes Application Developer\s*(?:\(CKAD\))?",
    r"PMP|Project Management Professional",
    r"Scrum Master\s*(?:\(CSM\))?",
    r"CISSP",
    r"CompTIA\s*(?:Security\+|Network\+|A\+)"
]

def extract_email(text: str) -> Optional[str]:
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    # Matches US, international, and standard phone number formats
    match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    return match.group(0) if match else None

def extract_name(text: str, filename: str = "") -> str:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        if filename:
            clean_stem = Path(filename).stem
            clean_stem = re.sub(r'\(\d+\)', '', clean_stem)
            clean_stem = re.sub(r'[_+\-]', ' ', clean_stem)
            clean_stem = re.sub(r'\bresume\b|\bcv\b|\bprofile\b', '', clean_stem, flags=re.IGNORECASE).strip().title()
            return clean_stem if clean_stem else "Unknown Candidate"
        return "Unknown Candidate"

    # Look at the first 8 non-empty lines for candidate name
    for line in lines[:8]:
        # Filter out lines that look like contact info, labels, URLs, or skills
        if re.search(r'@|http|www|\.com|\.in|\.org|\.net|phone|email|curriculum|resume|page\s*\d+|github|linkedin|\+?\d{10,}', line, re.IGNORECASE):
            continue
        # Clean special chars
        clean = re.sub(r'[^a-zA-Z\s\.\-]', '', line).strip()
        words = clean.split()
        if 1 <= len(words) <= 4 and len(clean) >= 2:
            if clean.lower() not in ("education", "experience", "skills", "summary", "projects", "profile", "contact", "about me", "technical skills"):
                if all(w.isupper() or w[0].isupper() for w in words if len(w) > 1):
                    return clean

    # Fallback to sanitized filename
    if filename:
        clean_name = Path(filename).stem
        clean_name = re.sub(r'\(\d+\)', '', clean_name)
        clean_name = re.sub(r'[_+\-]', ' ', clean_name)
        clean_name = re.sub(r'\bresume\b|\bcv\b|\bprofile\b', '', clean_name, flags=re.IGNORECASE).strip().title()
        if clean_name:
            return clean_name

    return lines[0][:40] if lines else "Unknown Candidate"

def extract_experience_years(text: str) -> float:
    """
    Extracts total years of experience using both explicit mentions (e.g. '7+ years experience')
    and timeline date span calculations (e.g. 2018 - 2024).
    """
    # 1. Explicit mention check
    explicit_match = re.search(r'(\d{1,2}(?:\.\d)?)\+?\s*(?:years|yrs)(?:\s+of)?(?:\s+relevant)?\s+experience', text, re.IGNORECASE)
    if explicit_match:
        try:
            return min(float(explicit_match.group(1)), 40.0)
        except ValueError:
            pass

    # 2. Date ranges check (e.g. 2016 - 2023, 2020 - Present)
    current_year = datetime.now().year
    year_ranges = re.findall(r'\b(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(20\d{2}|present|current)\b', text, re.IGNORECASE)
    
    total_span = 0.0
    intervals = []
    for start_str, end_str in year_ranges:
        try:
            start_yr = int(start_str)
            end_yr = current_year if end_str.lower() in ("present", "current") else int(end_str)
            if start_yr <= end_yr <= current_year + 1 and (end_yr - start_yr) <= 35:
                intervals.append((start_yr, end_yr))
        except ValueError:
            continue

    if intervals:
        # Merge overlapping intervals
        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]
        for current in intervals[1:]:
            prev_start, prev_end = merged[-1]
            if current[0] <= prev_end:
                merged[-1] = (prev_start, max(prev_end, current[1]))
            else:
                merged.append(current)
        total_span = sum(end - start for start, end in merged)
        if total_span > 0:
            return float(min(total_span, 40.0))

    return 0.0

def extract_education(text: str) -> List[str]:
    found_degrees = set()
    for pattern, label in DEGREE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            found_degrees.add(label)
    return sorted(list(found_degrees))

def extract_certifications(text: str) -> List[str]:
    found = set()
    for pattern in CERTIFICATION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            found.add(m.strip())
    return sorted(list(found))

def extract_job_titles(text: str) -> List[str]:
    found_titles = set()
    for title in COMMON_TITLES:
        pattern = r'\b' + re.escape(title) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_titles.add(title)
    return sorted(list(found_titles), key=lambda x: len(x), reverse=True)

def parse_resume(text: str, filename: str = "") -> Dict[str, Any]:
    """
    Parses a raw resume string into structured candidate information.
    Ensures non-hallucinated, verifiable extractions.
    """
    email = extract_email(text)
    phone = extract_phone(text)
    name = extract_name(text, filename)
    skills_data = extract_skills_from_text(text)
    years_exp = extract_experience_years(text)
    education = extract_education(text)
    certs = extract_certifications(text)
    job_titles = extract_job_titles(text)

    # Extract brief professional summary (first 300 characters or summary paragraph)
    summary_match = re.search(
        r'(?:summary|profile|about me|objective)[:\s\n]+(.*?)(?=\n\s*(?:experience|skills|education|projects|$))',
        text, re.IGNORECASE | re.DOTALL
    )
    summary = summary_match.group(1).strip()[:400] if summary_match else text[:300].strip()

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "summary": summary,
        "explicit_skills": skills_data["explicit_skills"],
        "inferred_skills": skills_data["inferred_skills"],
        "all_skills": sorted(list(set(skills_data["explicit_skills"] + skills_data["inferred_skills"]))),
        "years_experience": years_exp,
        "education": education,
        "certifications": certs,
        "previous_titles": job_titles,
    }
