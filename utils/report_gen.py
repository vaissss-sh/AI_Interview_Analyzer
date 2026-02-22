import os
from fpdf import FPDF
import datetime

class ReportGenerator:
    def __init__(self, filename="Interview_Performance_Portfolio.pdf"):
        self.filename = filename
        
    def generate(self, aggregated_results, overall_score_metrics):
        """
        aggregated_results: List of Dicts (one for each question)
        overall_score_metrics: Dict with averages of emotions, final score, etc.
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Cover Page
        pdf.add_page()
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(200, 40, txt="AI-Elite Interviewer Platform", ln=True, align='C')
        pdf.set_font("Arial", '', 16)
        pdf.cell(200, 10, txt="Comprehensive Performance Portfolio", ln=True, align='C')
        pdf.set_font("Arial", 'I', 12)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf.cell(200, 10, txt=f"Date: {date_str}", ln=True, align='C')
        
        pdf.ln(20)
        
        # Overall Summary
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Executive Summary", ln=True)
        pdf.line(10, 100, 200, 100)
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, txt=f"Final Confidence Score: {overall_score_metrics.get('final_score', 0):.1f}/100", ln=True)
        pdf.cell(200, 10, txt=f"Dominant Emotion Profile: {overall_score_metrics.get('avg_emotion', 'Neutral')}", ln=True)
        pdf.cell(200, 10, txt=f"Average Speaking Pace (WPM): {overall_score_metrics.get('avg_wpm', 0):.1f}", ln=True)
        pdf.cell(200, 10, txt=f"Total Filler Words: {overall_score_metrics.get('total_fillers', 0)}", ln=True)
        pdf.cell(200, 10, txt=f"Average Eye Contact: {overall_score_metrics.get('avg_eye_contact', 0):.1f}%", ln=True)
        
        # Insert Plotly radar chart if exists
        radar_path = "temp_radar_chart.png"
        if os.path.exists(radar_path):
            pdf.ln(10)
            pdf.image(radar_path, x=10, w=180)
            
        # Per-Question Breakdown
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Detailed Question Breakdown", ln=True)
        pdf.line(10, 25, 200, 25)
        pdf.ln(5)
        
        for idx, res in enumerate(aggregated_results):
            pdf.set_font("Arial", 'B', 14)
            pdf.multi_cell(0, 10, txt=f"Q{idx+1}: {res['question']}")
            
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 8, txt=f"Response Transcript: {res['transcript']}")
            
            # Metrics
            pdf.set_font("Arial", 'I', 11)
            pdf.cell(200, 8, txt=f">> Metrics | Score: {res['score']}/100 | WPM: {res['wpm']} | Fillers: {res['fillers_count']} | Emotion: {res['emotion']} | Eye Contact: {res['eye_contact']:.1f}%", ln=True)
            pdf.ln(10)
            
        # Sentiment Chart
        sentiment_path = "temp_sentiment_chart.png"
        if os.path.exists(sentiment_path):
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Sentiment Timeline Analytics", ln=True)
            pdf.line(10, 25, 200, 25)
            pdf.ln(10)
            pdf.image(sentiment_path, x=10, w=180)
            
        pdf.output(self.filename)
        return self.filename
