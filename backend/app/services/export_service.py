import io
import pandas as pd
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def generate_csv_report(session_title: str, results: List[Dict[str, Any]]) -> str:
    """
    Produces a CSV string of screening results using pandas.
    """
    rows = []
    for rank, r in enumerate(results, start=1):
        component_scores = r.get("component_scores", {})
        rows.append({
            "Rank": rank,
            "Candidate Name": r.get("candidate_name", "N/A"),
            "Email": r.get("candidate_email", "N/A"),
            "Final Match Score": r.get("final_match_score", 0.0),
            "Required Skills Score": component_scores.get("required_skills", 0.0),
            "Semantic Similarity": component_scores.get("semantic_similarity", 0.0),
            "Experience Score": component_scores.get("experience", 0.0),
            "Relevant Experience (Yrs)": r.get("relevant_experience", 0.0),
            "Matched Skills": ", ".join(r.get("matched_skills", [])),
            "Missing Required Skills": ", ".join(r.get("missing_required_skills", [])),
            "Overqualification Status": r.get("overqualification_status", "N/A"),
            "Review Status": r.get("review_status", "pending"),
            "Recruiter Notes": r.get("recruiter_notes", "")
        })

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def generate_pdf_report(session_data: Dict[str, Any], results: List[Dict[str, Any]]) -> bytes:
    """
    Produces a professional PDF report containing the screening summary and ranked candidate table.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#ffffff')
    )
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # Title & Header
    story.append(Paragraph("HireSense AI — Screening Report", title_style))
    job_title = session_data.get("job_title", "Untitled Role")
    created_at = str(session_data.get("created_at", ""))[:16]
    story.append(Paragraph(f"<b>Job Title:</b> {job_title} | <b>Date:</b> {created_at} | <b>Total Evaluated:</b> {len(results)}", subtitle_style))
    story.append(Spacer(1, 15))

    # Summary Metrics Cards Table
    avg_score = round(sum(r.get("final_match_score", 0.0) for r in results) / len(results), 1) if results else 0.0
    high_fit_count = sum(1 for r in results if r.get("final_match_score", 0.0) >= 75.0)

    summary_data = [
        [
            Paragraph(f"<b>Total Resumes:</b> {len(results)}", subtitle_style),
            Paragraph(f"<b>Average Fit Score:</b> {avg_score}%", subtitle_style),
            Paragraph(f"<b>High-Fit Candidates (>=75%):</b> {high_fit_count}", subtitle_style),
        ]
    ]
    summary_table = Table(summary_data, colWidths=[180, 180, 180])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Candidate Ranking Table
    story.append(Paragraph("<b>Candidate Ranking & Fit Breakdown</b>", styles['Heading3']))
    story.append(Spacer(1, 8))

    table_data = [
        [
            Paragraph("<b>#</b>", header_style),
            Paragraph("<b>Candidate</b>", header_style),
            Paragraph("<b>Match Score</b>", header_style),
            Paragraph("<b>Skills Fit</b>", header_style),
            Paragraph("<b>Experience</b>", header_style),
            Paragraph("<b>Status</b>", header_style),
            Paragraph("<b>Review</b>", header_style),
        ]
    ]

    for rank, r in enumerate(results, start=1):
        comp = r.get("component_scores", {})
        score = f"{r.get('final_match_score', 0):.1f}%"
        skills_fit = f"{comp.get('required_skills', 0):.0f}%"
        exp = f"{r.get('relevant_experience', 0):.1f} yrs"
        ov_status = r.get("overqualification_status", "")
        if "Overqualified" in ov_status:
            ov_badge = "Potentially Overqualified"
        else:
            ov_badge = "Standard Fit"
        review = r.get("review_status", "pending").capitalize()

        table_data.append([
            Paragraph(str(rank), cell_style),
            Paragraph(f"<b>{r.get('candidate_name', 'Unknown')}</b><br/>{r.get('candidate_email', '')}", cell_style),
            Paragraph(f"<b>{score}</b>", cell_style),
            Paragraph(skills_fit, cell_style),
            Paragraph(exp, cell_style),
            Paragraph(ov_badge, cell_style),
            Paragraph(review, cell_style),
        ])

    ranking_table = Table(table_data, colWidths=[25, 140, 75, 65, 70, 95, 70])
    ranking_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4338ca')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))

    story.append(ranking_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
