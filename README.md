# HireSense AI — Intelligent Resume Screening & Ranking System

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Sentence Transformers](https://img.shields.io/badge/AI%2FML-Sentence--Transformers-FF9900.svg)](https://www.sbert.net/)
[![Pytest](https://img.shields.io/badge/Tests-15%20Passing-brightgreen.svg?logo=pytest)](https://pytest.org/)

**HireSense AI** is an enterprise-grade, end-to-end recruitment platform that automates candidate resume parsing, multi-signal semantic matching, explainable scoring, and talent ranking.

Built with **React (TypeScript) + Tailwind CSS** on the frontend, **FastAPI + SQLAlchemy** on the backend, and a **hybrid NLP/Sentence Transformers + Scikit-Learn** machine learning pipeline, HireSense AI helps talent acquisition teams evaluate candidates fairly, consistently, and transparently without relying on third-party paid LLM APIs.

---

## 🌟 Key Features

1. **Multi-Format Document Parsing:**
   - High-fidelity text, table, and header extraction from **PDF** (`PyMuPDF`) and **DOCX** (`python-docx`).
   - Resilient against encrypted, corrupt, and empty documents with granular error reporting.

2. **Structured Candidate Profile Extraction:**
   - Automatically extracts candidate names, emails, phone numbers, total years of experience (from timelines and explicit mentions), previous job titles, degrees, certifications, and verbatim profile excerpts.

3. **Taxonomy-Driven Skill Normalization:**
   - Normalizes synonymous industry terms (e.g., `JS` → `JavaScript`, `Postgres` → `PostgreSQL`, `K8s` → `Kubernetes`, `Py` → `Python`, `AWS` → `Amazon Web Services (AWS)`).
   - Distinguishes **explicitly listed skills** from **inferred skills** embedded within work history.

4. **Multi-Signal Hybrid Matching Engine:**
   - **Sentence Transformers (`all-MiniLM-L6-v2`)** dense 384-dimensional vector embeddings for deep contextual similarity.
   - **TF-IDF + Cosine Similarity** fallback/hybrid signal.
   - Configurable weighted formula balancing Required Skills, Semantic Vector Alignment, Relevant Experience, Preferred Skills, and Education.

5. **Explainable Scoring & Gaps Analysis:**
   - Every candidate receives an itemized breakdown (0–100) per component.
   - Generates bulleted lists of demonstrated core strengths, matched skills, and specific missing requirements.

6. **Advisory Overqualification Detection:**
   - Identifies candidates whose seniority, leadership roles (e.g., CTO, VP, Tech Lead), or career span significantly exceed posted role parameters.
   - Includes mandatory advisory disclaimers and never automatically disqualifies candidates.

7. **Recruiter Review & Decision Workflow:**
   - Mark candidates as **Shortlisted**, **Under Review**, or **Rejected**.
   - Add private recruiter notes and override justifications stored separately from AI scores.

8. **Export & Reporting:**
   - One-click **CSV** export via Pandas.
   - One-click formatted **PDF Screening Reports** generated via ReportLab.

9. **Responsible AI & Demographic-Blind:**
   - Protected demographic attributes (name, gender, age, nationality, photo) are excluded from scoring features.

---

## 🏗️ Architecture

```
                                 ┌────────────────────────────────────────┐
                                 │            React Frontend              │
                                 │  (Vite + TS + Tailwind + Lucide +      │
                                 │   Recharts + React Router)             │
                                 └──────────────────┬─────────────────────┘
                                                    │ REST API (/api)
                                                    ▼
                                 ┌────────────────────────────────────────┐
                                 │            FastAPI Backend             │
                                 │   - Pydantic Validation & Schemas      │
                                 │   - Asynchronous Background Workers    │
                                 │   - ReportLab PDF & Pandas CSV Export  │
                                 └──────────┬──────────────────┬──────────┘
                                            │                  │
                     ┌──────────────────────┴───────┐          │
                     ▼                              ▼          ▼
┌──────────────────────────────┐ ┌──────────────────────┐ ┌────────────────┐
│   Document Extractors        │ │  AI / ML Pipeline    │ │  Database      │
│  - PyMuPDF (PDF Parser)      │ │  - MiniLM-L6-v2 Embed│ │  - SQLite      │
│  - python-docx (DOCX Parser) │ │  - TF-IDF Cosine Fall│ │    (Default)   │
│  - Regex Entity Recognizer   │ │  - Taxonomy Normal   │ │  - PostgreSQL  │
│  - Job Description Analyzer  │ │  - Overqualification │ │    (Production)│
└──────────────────────────────┘ └──────────────────────┘ └────────────────┘
```

---

## 📐 Scoring Formula & Weight Distribution

The system calculates candidate job-fit using a normalized weighted sum:

$$\text{Final Score} = \frac{\sum (\text{Component Score}_i \times \text{Active Weight}_i)}{\sum \text{Active Weight}_i}$$

### Default Weights:
- **Required Skill Coverage:** 35%
- **Semantic Job Description Similarity:** 25%
- **Relevant Work Experience:** 20%
- **Preferred Skill Coverage:** 10%
- **Education & Certifications:** 10%

### Dynamic Weight Normalization:
If a job description does not specify optional criteria (such as preferred skills or formal degree requirements), the system redistributes the weights across active criteria so self-taught or non-traditional candidates are not penalized.

---

## ⚖️ Overqualification Advisory Logic

The overqualification module evaluates candidate credentials against target role seniority:
- **Seniority Delta:** Candidate has $\ge 4$ years of experience beyond stated requirements.
- **Executive / Leadership Mismatch:** Candidate held titles such as *VP of Engineering*, *CTO*, or *Director* applying for an individual contributor or junior role.
- **Advanced Degrees:** Holds a Ph.D. with substantial industry experience for non-research roles.

**Advisory Classifications:**
1. `Potentially Overqualified`
2. `Experience Exceeds Requirements`
3. `No Clear Overqualification Signal`
4. `Insufficient Information`

> **Mandatory Disclaimer:**  
> *"Overqualification is an advisory signal based on the available resume and job requirements. It does not establish a candidate's interest, salary expectations, retention likelihood, or willingness to accept the role."*

---

## 🗄️ Database Schema

The database model is built with SQLAlchemy ORM and supports SQLite (zero-config local) and PostgreSQL (production/Docker):

- **`ScreeningSession`**: Stores job title, department, description, parsed requirements JSON, scoring weights JSON, overqualification toggle, and processing metrics.
- **`Candidate`**: Stores candidate name, email, phone, parsed profile JSON, and raw resume text.
- **`ResumeSubmission`**: Tracks uploaded filenames, storage paths, sha256 hashes, parsing statuses (`queued`, `extracting`, `analyzing`, `completed`, `failed`), and error logs.
- **`ScreeningResult`**: Stores job-specific final match scores, component breakdown JSON, matched skills, missing skills, overqualification status, confidence, and explainable evidence.
- **`RecruiterReview`**: Stores recruiter status (`pending`, `shortlisted`, `under_review`, `rejected`), private notes, and override reasons.

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and **npm**

---

### Option A: Local Development (Recommended, Zero-Config)

#### 1. Backend Setup
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Generate synthetic test resumes
python scripts\generate_sample_resumes.py

# Start FastAPI backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now accessible at `http://127.0.0.1:8000`  
OpenAPI documentation: `http://127.0.0.1:8000/docs`

#### 2. Frontend Setup
In a new terminal:
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite dev server with proxy to backend
npm run dev
```
Open **`http://127.0.0.1:5173`** in your browser.

---

### Option B: Docker Compose (Production Environment)

Run with PostgreSQL, backend, and frontend containers:

```bash
docker-compose up --build
```

- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **PostgreSQL:** Port `5432`

---

## 🧪 Automated Testing

HireSense AI includes a test suite covering document parsers, scoring calculations, ML models, and API routes:

```powershell
cd backend
.\venv\Scripts\pytest -v
```

### Test Coverage Highlights:
- `test_extract_text_from_pdf`: Validates PyMuPDF extraction on synthetic PDFs.
- `test_extract_text_from_docx`: Validates python-docx extraction on DOCX files.
- `test_pdf_invalid_file` & `test_docx_invalid_file`: Verifies corrupted file rejection.
- `test_skill_normalization`: Tests canonicalization (`JS` → `JavaScript`, `Postgres` → `PostgreSQL`).
- `test_job_description_parsing`: Tests automatic extraction of required skills and experience.
- `test_weighted_scoring_calculation`: Validates mathematical score normalization.
- `test_overqualification_detection`: Verifies advisory status and evidence detection.
- `test_create_and_process_screening_session`: Full end-to-end integration test with multipart resume uploads, result ranking, candidate shortlisting, and CSV/PDF export.

---

## 📑 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & AI model loading status |
| `POST` | `/api/screenings` | Create screening session with multipart resume files |
| `GET` | `/api/screenings` | List all screening sessions |
| `GET` | `/api/screenings/{id}` | Retrieve screening session details |
| `DELETE` | `/api/screenings/{id}` | Delete session and associated uploaded files |
| `POST` | `/api/screenings/{id}/analyze` | Trigger or resume screening analysis |
| `GET` | `/api/screenings/{id}/status` | Retrieve real-time analysis progress per file |
| `GET` | `/api/screenings/{id}/results` | Retrieve ranked candidates with search/filtering |
| `GET` | `/api/screenings/{id}/candidates/{cid}` | Get candidate job analysis and score breakdown |
| `PATCH` | `/api/screenings/{id}/candidates/{cid}/review` | Update recruiter review status and private notes |
| `GET` | `/api/screenings/{id}/export/csv` | Download CSV ranking report |
| `GET` | `/api/screenings/{id}/export/pdf` | Download formatted PDF screening report |
| `GET` | `/api/candidates` | Search talent directory across all sessions |
| `GET` | `/api/candidates/{id}` | Get candidate profile and past screening history |
| `GET` | `/api/settings/scoring` | Get default scoring weights |
| `PATCH` | `/api/settings/scoring` | Update default scoring weights |
| `GET` | `/api/settings/stats` | Retrieve aggregate metrics for recruiter dashboard |

---

## 🛡️ Security, Privacy & Compliance

- **File Validation:** Filenames are sanitized with UUID prefixes. Extension and mime-type checks prevent execution of arbitrary files.
- **Isolated Storage:** Uploaded resumes are stored in isolated directories outside the public web root.
- **ORM Parameterization:** All database operations utilize SQLAlchemy query parameterization, mitigating SQL injection risks.
- **CORS Protection:** Configurable CORS whitelist restricting unauthorized cross-origin requests.
- **Demographic Exclusion:** Candidates' demographic traits are omitted from AI ranking inputs to prevent bias.
- **Data Cleanup:** Deleting a screening session cascades removal of database records and purges stored files from disk.

---

## 📜 License
This project is open-source under the MIT License.
