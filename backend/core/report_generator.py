from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import io
import os
from .database import Session as SessionModel, SessionPerson, PersonMetric, Insight, get_db, SessionLocal

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_pdf_report(self, session_id: int):
        db = SessionLocal()
        try:
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if not session:
                return None
            
            # Fetch Attendees
            attendees = db.query(SessionPerson).filter(SessionPerson.session_id == session_id).all()
            
            # Create PDF Buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            # Header
            elements.append(Paragraph(f"EduSense AI - Session Report", self.styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Info
            info_data = [
                ["Session ID", str(session.id)],
                ["Date", session.start_time.strftime("%Y-%m-%d %H:%M")],
                ["Duration", str(session.end_time - session.start_time) if session.end_time else "N/A"],
                ["Total Attendees", str(session.people_count)],
                ["Avg Attention", f"{session.total_attention_avg:.1f}%"]
            ]
            t = Table(info_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 20))
            
            # Attendees Table
            elements.append(Paragraph("Attendance Summary", self.styles['Heading2']))
            data = [["Student Name/ID", "Time Present", "Avg Attention", "Dominant Emotion"]]
            for p in attendees:
                data.append([
                    p.person_id,
                    f"{p.total_time_present:.1f}s",
                    f"{p.avg_attention:.1f}%",
                    p.dominant_emotion or "N/A"
                ])
                
            t2 = Table(data)
            t2.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ]))
            elements.append(t2)
            
            doc.build(elements)
            buffer.seek(0)
            return buffer
            
        finally:
            db.close()

    def generate_csv_export(self, session_id: int):
        db = SessionLocal()
        try:
            metrics = db.query(PersonMetric).filter(PersonMetric.session_id == session_id).all()
            if not metrics:
                return None
                
            data = [{
                'timestamp': m.timestamp,
                'student_id': m.person_id,
                'emotion': m.emotion,
                'confidence': m.emotion_confidence,
                'attention': m.attention_score
            } for m in metrics]
            
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        finally:
            db.close()
