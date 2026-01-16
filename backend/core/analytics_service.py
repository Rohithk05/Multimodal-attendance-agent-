from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import SessionLocal, Session as SessionModel, SessionPerson, PersonMetric

class AnalyticsService:
    def get_session_trends(self, session_id: int):
        db = SessionLocal()
        try:
            # Aggregate attention over time (minute buckets)
            # SQLite specific time grouping
            # For simplicity, we just return all metrics and let frontend downsample or bin
            
            # Fetch last 1000 points to avoid overload
            metrics = db.query(PersonMetric)\
                .filter(PersonMetric.session_id == session_id)\
                .order_by(PersonMetric.timestamp.asc())\
                .all()
                
            # Group by timestamp (seconds)
            timeline = {}
            for m in metrics:
                ts_str = m.timestamp.strftime("%H:%M:%S")
                if ts_str not in timeline:
                    timeline[ts_str] = {'att': [], 'emo': {}}
                
                timeline[ts_str]['att'].append(m.attention_score)
                timeline[ts_str]['emo'][m.emotion] = timeline[ts_str]['emo'].get(m.emotion, 0) + 1
            
            # Format output
            graph_data = []
            for ts, val in timeline.items():
                start_obj = {
                     'time': ts, 
                     'avg_attention': sum(val['att'])/len(val['att']),
                     'student_count': len(val['att'])
                }
                # Add emotion counts
                start_obj.update(val['emo'])
                graph_data.append(start_obj)
                
            return graph_data
        finally:
            db.close()
            
    def get_student_heatmap(self, session_id: int):
        # Return per-student average attention/engagement for the session
        db = SessionLocal()
        try:
             people = db.query(SessionPerson).filter(SessionPerson.session_id == session_id).all()
             return [{
                 'id': p.person_id,
                 'name': p.person_id, # Placeholder for name
                 'attention': p.avg_attention,
                 'dominant_emotion': p.dominant_emotion,
                 'presence': p.total_time_present
             } for p in people]
        finally:
             db.close()
