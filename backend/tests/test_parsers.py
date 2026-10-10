import pytest
from pathlib import Path
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.resume_parser import parse_resume

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"

def test_extract_text_from_pdf():
    pdf_path = SAMPLE_DIR / "Candidate_1_Elena_Rostova_Senior_AI_TechLead.pdf"
    assert pdf_path.exists(), "Sample PDF must exist"
    text = extract_text_from_pdf(pdf_path)
    assert "Elena Rostova" in text
    assert "PyTorch" in text
    assert "Technical Lead" in text

def test_extract_text_from_docx():
    docx_path = SAMPLE_DIR / "Candidate_3_Amina_Diallo_Python_Backend.docx"
    assert docx_path.exists(), "Sample DOCX must exist"
    text = extract_text_from_docx(docx_path)
    assert "Amina Diallo" in text
    assert "FastAPI" in text
    assert "PostgreSQL" in text

def test_pdf_invalid_file(tmp_path):
    fake_pdf = tmp_path / "corrupted.pdf"
    fake_pdf.write_bytes(b"not a valid pdf data")
    with pytest.raises(ValueError, match="Corrupted or invalid PDF"):
        extract_text_from_pdf(fake_pdf)

def test_docx_invalid_file(tmp_path):
    fake_docx = tmp_path / "corrupted.docx"
    fake_docx.write_bytes(b"not a valid docx data")
    with pytest.raises(ValueError, match="Corrupted or invalid DOCX"):
        extract_text_from_docx(fake_docx)

def test_empty_resume_text():
    parsed = parse_resume("")
    assert parsed["name"] == "Unknown Candidate"
    assert parsed["years_experience"] == 0.0
    assert parsed["all_skills"] == []

def test_structured_resume_parsing():
    pdf_path = SAMPLE_DIR / "Candidate_2_Marcus_Chen_FullStack_React_Node.pdf"
    text = extract_text_from_pdf(pdf_path)
    profile = parse_resume(text, filename="Candidate_2_Marcus_Chen_FullStack_React_Node.pdf")

    assert profile["name"] == "Marcus Chen"
    assert profile["email"] == "marcus.chen@example.com"
    assert "React" in profile["all_skills"]
    assert "TypeScript" in profile["all_skills"]
    assert profile["years_experience"] >= 5.0
    assert any("Bachelor" in e for e in profile["education"])
