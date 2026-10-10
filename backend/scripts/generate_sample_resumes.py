import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import docx

def create_pdf_resume(filepath: Path, name: str, email: str, phone: str, title: str, summary: str, skills: list, experience: list, education: list):
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    name_style = ParagraphStyle('Name', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#1e1b4b'))
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#475569'))
    heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#3730a3'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#1e293b'))
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'), leftIndent=12)

    story = []
    story.append(Paragraph(name, name_style))
    story.append(Paragraph(f"{title} | {email} | {phone}", contact_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Professional Summary", heading_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Technical Skills", heading_style))
    story.append(Paragraph(", ".join(skills), body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Work Experience", heading_style))
    for job in experience:
        story.append(Paragraph(f"<b>{job['role']}</b> — {job['company']} ({job['dates']})", body_style))
        for bullet in job['bullets']:
            story.append(Paragraph(f"• {bullet}", bullet_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("Education & Certifications", heading_style))
    for edu in education:
        story.append(Paragraph(f"• {edu}", bullet_style))

    doc.build(story)

def create_docx_resume(filepath: Path, name: str, email: str, phone: str, title: str, summary: str, skills: list, experience: list, education: list):
    doc = docx.Document()
    
    # Title & Contact
    h = doc.add_heading(name, level=0)
    p = doc.add_paragraph(f"{title} | {email} | {phone}")
    
    # Summary
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(summary)
    
    # Skills
    doc.add_heading("Technical Skills", level=1)
    doc.add_paragraph(", ".join(skills))
    
    # Work Experience
    doc.add_heading("Work Experience", level=1)
    for job in experience:
        doc.add_paragraph(f"{job['role']} — {job['company']} ({job['dates']})", style='List Bullet')
        for bullet in job['bullets']:
            doc.add_paragraph(f"  - {bullet}")
            
    # Education
    doc.add_heading("Education & Certifications", level=1)
    for edu in education:
        doc.add_paragraph(edu, style='List Bullet')
        
    doc.save(str(filepath))

def generate_samples(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Senior AI Tech Lead (Potentially Overqualified for junior/mid)
    create_pdf_resume(
        target_dir / "Candidate_1_Elena_Rostova_Senior_AI_TechLead.pdf",
        name="Elena Rostova",
        email="elena.rostova@example.com",
        phone="(555) 234-5678",
        title="Technical Lead & Staff Machine Learning Engineer",
        summary="Accomplished engineering leader with 11+ years experience architecting scalable distributed systems and LLM pipelines. Led cross-functional teams of 15 engineers in production deep learning and NLP deployments.",
        skills=["Python", "PyTorch", "Transformers", "NLP", "Machine Learning", "FastAPI", "Kubernetes", "Docker", "AWS", "PostgreSQL", "CI/CD", "System Design"],
        experience=[
            {
                "role": "Technical Lead & Staff ML Engineer",
                "company": "Cognitive Scale AI",
                "dates": "2020 - Present",
                "bullets": [
                    "Spearheaded multi-tenant RAG systems processing 20M queries daily using Hugging Face Transformers and PyTorch.",
                    "Managed team of 14 machine learning engineers and DevOps specialists.",
                    "Architected high-throughput inference APIs using FastAPI and Kubernetes on AWS."
                ]
            },
            {
                "role": "Senior Machine Learning Engineer",
                "company": "DeepData Systems",
                "dates": "2015 - 2020",
                "bullets": [
                    "Engineered end-to-end NLP classification pipelines with 94% precision.",
                    "Implemented CI/CD automation and containerized model training workflows."
                ]
            },
            {
                "role": "Software Engineer",
                "company": "Apex Analytics",
                "dates": "2013 - 2015",
                "bullets": [
                    "Developed backend data ingestion pipelines in Python and PostgreSQL."
                ]
            }
        ],
        education=["Ph.D. in Computer Science — Stanford University", "AWS Certified Solutions Architect", "TensorFlow Certified Developer"]
    )

    # 2. Mid-Senior Full Stack Engineer (High Match)
    create_pdf_resume(
        target_dir / "Candidate_2_Marcus_Chen_FullStack_React_Node.pdf",
        name="Marcus Chen",
        email="marcus.chen@example.com",
        phone="(555) 456-7890",
        title="Full Stack Software Engineer",
        summary="Versatile Full Stack Engineer with 5+ years of experience building responsive SaaS applications. Proficient in React, TypeScript, Node.js, PostgreSQL, and cloud deployments.",
        skills=["React", "TypeScript", "Node.js", "JavaScript", "HTML5", "CSS3", "Tailwind CSS", "PostgreSQL", "REST API", "Docker", "Git", "Jest"],
        experience=[
            {
                "role": "Full Stack Developer",
                "company": "Nexus Web Solutions",
                "dates": "2021 - Present",
                "bullets": [
                    "Built modular dashboard UI components using React, TypeScript, and Tailwind CSS.",
                    "Designed RESTful microservices in Node.js with PostgreSQL database layer.",
                    "Improved client-side performance and reduced initial load time by 38%."
                ]
            },
            {
                "role": "Frontend Developer",
                "company": "Pulse Media Tech",
                "dates": "2019 - 2021",
                "bullets": [
                    "Engineered responsive user interfaces and customer-facing web portals.",
                    "Collaborated with UX designers to implement accessible design system components."
                ]
            }
        ],
        education=["Bachelor's Degree in Computer Science — UC Berkeley (B.S.)", "Scrum Master (CSM)"]
    )

    # 3. Python Backend Engineer (Mid-Level Match)
    create_docx_resume(
        target_dir / "Candidate_3_Amina_Diallo_Python_Backend.docx",
        name="Amina Diallo",
        email="amina.diallo@example.com",
        phone="(555) 789-0123",
        title="Backend Software Engineer",
        summary="Backend engineer with 4 years experience specializing in high-performance Python microservices, FastAPI, relational databases, and API development.",
        skills=["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Git", "REST API", "Linux", "SQL", "Unit Testing"],
        experience=[
            {
                "role": "Backend Developer",
                "company": "CloudForge Labs",
                "dates": "2021 - Present",
                "bullets": [
                    "Developed asynchronous REST APIs using FastAPI and SQLAlchemy.",
                    "Optimized complex PostgreSQL queries and integrated Redis caching.",
                    "Implemented unit test coverage exceeding 90% using Pytest."
                ]
            },
            {
                "role": "Junior Backend Engineer",
                "company": "Fintech Stream",
                "dates": "2020 - 2021",
                "bullets": [
                    "Maintained transaction processing pipelines and database migrations."
                ]
            }
        ],
        education=["Bachelor's Degree in Information Technology (B.Tech)", "Docker Certified Associate"]
    )

    # 4. Junior Frontend Developer (Entry Level / Missing Skills)
    create_docx_resume(
        target_dir / "Candidate_4_David_Kim_Junior_Frontend.docx",
        name="David Kim",
        email="david.kim@example.com",
        phone="(555) 890-1234",
        title="Junior Frontend Developer",
        summary="Enthusiastic Junior Web Developer with 1.5 years experience creating clean user interfaces with HTML, CSS, JavaScript, and React.",
        skills=["JavaScript", "React", "HTML5", "CSS3", "Git", "Bootstrap"],
        experience=[
            {
                "role": "Junior Web Developer",
                "company": "PixelCraft Studios",
                "dates": "2023 - Present",
                "bullets": [
                    "Created interactive UI web pages using HTML5, CSS3, and JavaScript.",
                    "Assisted in migrating legacy pages to React functional components."
                ]
            },
            {
                "role": "Frontend Intern",
                "company": "BlueSky Agency",
                "dates": "2022 - 2023",
                "bullets": [
                    "Built landing pages and fixed UI bugs across modern web browsers."
                ]
            }
        ],
        education=["Associate Degree in Web Development"]
    )

    # 5. Executive / Principal Cloud Architect (Highly Experienced / Overqualified)
    create_pdf_resume(
        target_dir / "Candidate_5_Lucas_Vance_Cloud_Architect.pdf",
        name="Lucas Vance",
        email="lucas.vance@example.com",
        phone="(555) 901-2345",
        title="VP of Infrastructure & Principal Cloud Architect",
        summary="Executive technology leader with 14+ years experience leading global cloud architecture and DevOps transformation. Formerly VP of Infrastructure managing $12M annual cloud budget.",
        skills=["Amazon Web Services (AWS)", "Kubernetes", "Terraform", "Docker", "Python", "CI/CD", "Linux", "Microservices", "System Design"],
        experience=[
            {
                "role": "VP of Infrastructure",
                "company": "Global Enterprise Cloud",
                "dates": "2018 - Present",
                "bullets": [
                    "Managed 45-person global infrastructure and site reliability organization.",
                    "Spearheaded multi-region cloud migration reducing hosting costs by 40%.",
                    "Defined enterprise security, compliance, and zero-trust guidelines."
                ]
            },
            {
                "role": "Principal Systems Architect",
                "company": "Horizon Networks",
                "dates": "2012 - 2018",
                "bullets": [
                    "Architected high-availability Kubernetes clusters and automated CI/CD pipelines.",
                    "Authored automated infrastructure as code modules using Terraform."
                ]
            },
            {
                "role": "Senior Linux Systems Engineer",
                "company": "DataCore Inc",
                "dates": "2010 - 2012",
                "bullets": [
                    "Administered enterprise Linux server clusters and storage area networks."
                ]
            }
        ],
        education=["Master's Degree in Computer Engineering (M.S.)", "AWS Certified Solutions Architect - Professional", "Certified Kubernetes Administrator (CKA)"]
    )

    print(f"Successfully generated 5 synthetic candidate resumes in: {target_dir}")

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "sample_resumes"
    generate_samples(out_dir)
