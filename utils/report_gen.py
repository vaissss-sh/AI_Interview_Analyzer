import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from utils.db import get_session_by_id

def generate_report(session_id: int, charts_data: dict = None) -> str:
    """
    Generates a PDF report for a given session.
    charts_data can contain paths to saved chart images (e.g. radar chart).
    Returns the file path to the generated PDF.
    """
    session_data = get_session_by_id(session_id)
    if not session_data:
        raise ValueError("Session not found.")
        
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"report_{session_id}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    elements = []
    
    # Cover / Header
    elements.append(Paragraph("InterviewIQ Evaluation Report", title_style))
    elements.append(Spacer(1, 20))
    
    # Candidate Info
    cand = session_data.get('candidate', {})
    elements.append(Paragraph(f"<b>Candidate:</b> {cand.get('name')}", normal_style))
    elements.append(Paragraph(f"<b>Email:</b> {cand.get('email')}", normal_style))
    elements.append(Paragraph(f"<b>Role:</b> {cand.get('role')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Metrics
    metrics = session_data.get('metrics', {})
    elements.append(Paragraph("Overall Performance", heading_style))
    metrics_data = [
        ["Overall Score", f"{metrics.get('overall_score', 0):.1f}/100"],
        ["Final Grade", metrics.get('grade', 'N/A')]
    ]
    t_metrics = Table(metrics_data, colWidths=[200, 200])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(t_metrics)
    elements.append(Spacer(1, 20))
    
    # Breakdown
    bd = session_data.get('breakdown', {})
    if bd:
        elements.append(Paragraph("Score Breakdown", heading_style))
        bd_data = [
            ["Communication", f"{bd.get('communication', 0):.1f}"],
            ["Confidence", f"{bd.get('confidence', 0):.1f}"],
            ["Technical", f"{bd.get('technical', 0):.1f}"],
            ["Emotional IQ", f"{bd.get('emotional_iq', 0):.1f}"],
            ["Engagement", f"{bd.get('engagement', 0):.1f}"],
            ["Professionalism", f"{bd.get('professionalism', 0):.1f}"]
        ]
        t_bd = Table(bd_data, colWidths=[200, 200])
        t_bd.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t_bd)
        elements.append(Spacer(1, 20))
        
    # Transcript Highlights
    elements.append(Paragraph("Interview Transcript Highlights", heading_style))
    questions = session_data.get('questions', [])
    for q in questions:
        elements.append(Paragraph(f"<b>Q:</b> {q.get('text', '')}", normal_style))
        elements.append(Paragraph(f"<i>Ans:</i> {q.get('transcript', '')}", normal_style))
        elements.append(Paragraph(f"Score: {q.get('score', 0):.1f}", normal_style))
        elements.append(Spacer(1, 10))
        
    doc.build(elements)
    return filepath

def export_transcript(session_id: int) -> str:
    """Exports just the transcript to a simple text file."""
    session_data = get_session_by_id(session_id)
    if not session_data:
        raise ValueError("Session not found.")
        
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"transcript_{session_id}.txt")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        cand = session_data.get('candidate', {})
        f.write(f"Transcript for {cand.get('name', 'Unknown')}\n")
        f.write("="*40 + "\n\n")
        
        for q in session_data.get('questions', []):
            f.write(f"Interviewer: {q.get('text', '')}\n")
            f.write(f"Candidate: {q.get('transcript', '')}\n")
            f.write("-" * 20 + "\n")
            
    return filepath

def export_comparison_report(session_ids_list: list) -> str:
    """Generates a comparison PDF for multiple candidates."""
    # Placeholder for multi-candidate comparison
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "comparison_report.pdf")
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("Candidate Comparison Report", styles['Title']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Comparing {len(session_ids_list)} candidates.", styles['Normal']))
    
    doc.build(elements)
    return filepath
