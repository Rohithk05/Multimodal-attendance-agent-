from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import cv2
import asyncio
import json
import numpy as np
import time
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from core.camera_service import CameraService
from core.audio_analysis import AudioAnalyzer
from core.database import init_db, get_db, SessionLocal
from core.session_manager import SessionManager
from core.llm_insights import InsightGenerator
from core.analytics_service import AnalyticsService
from core.report_generator import ReportGenerator
from core.recommendations_engine import RecommendationsEngine
from core.teacher_profiles import TeacherProfileService
from core.gamification_engine import GamificationEngine
from core.ai_suggestions import AISuggestionEngine

app = FastAPI(title="Multimodal Attendance & Attention Tracking Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
camera = CameraService()
audio_analyzer = AudioAnalyzer()
session_manager = SessionManager()
insight_generator = InsightGenerator()
analytics_service = AnalyticsService()
report_generator = ReportGenerator()
recommendations_engine = RecommendationsEngine()
teacher_profile_service = TeacherProfileService()
gamification_engine = GamificationEngine()
ai_suggestion_engine = AISuggestionEngine()

init_db()

class SessionStartRequest(BaseModel):
    teacher_id: str
    class_id: str

@app.get("/")
async def root():
    return {"message": "System is running", "status": "online"}

# Phase 4: Teacher & Gamification Endpoints
@app.get("/api/teacher/profile/{teacher_id}")
async def get_teacher_profile(teacher_id: str):
    return teacher_profile_service.get_profile(teacher_id)

@app.get("/api/gamification/leaderboard")
async def get_leaderboard():
    return gamification_engine.get_leaderboard()

@app.get("/api/suggestions/current")
async def get_ai_suggestions():
    # Generate based on current active session status
    if not session_manager.active_session_id:
        return []
    
    status = session_manager.get_status()
    # Adding mock aggregate metrics
    data = {
        'total_people': status['people_count'],
        'avg_attention': 75, # Mock, should calculate from GamificationEngine history or SessionManager
        'dominant_emotion': 'neutral'
    }
    return ai_suggestion_engine.generate_suggestions(data)

# Session Endpoints
@app.post("/api/session/start")
async def start_session(req: SessionStartRequest):
    result = session_manager.start_session(req.teacher_id, req.class_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result

@app.post("/api/session/stop")
async def stop_session():
    return session_manager.stop_session()

@app.get("/api/session/status")
async def get_session_status():
    return session_manager.get_status()

# Insights & Analytics Endpoints
@app.get("/api/insights/student/{student_id}")
async def get_student_insight(student_id: str):
    if session_manager.active_session_id:
        data = session_manager.person_history.get(student_id)
        if data:
            emotions = [e['label'] for e in data['emotions'][-10:]]
            summary = {
                "name": f"Student {student_id}",
                "emotion_history": emotions,
                "attention_scores": data['attention'][-10:]
            }
            return {"insight": insight_generator.generate_classroom_insight(summary)} # Reusing generic
    return {"insight": "Student not found."}

@app.get("/api/insights/classroom")
async def get_classroom_insight():
    if not session_manager.active_session_id:
        return {"insight": "No active session."}
    
    status = session_manager.get_status()
    # Mock aggregation for now (real aggregation in future)
    summary = {
        "total_people": status['people_count'],
        "dominant_emotion": "neutral", 
        "avg_attention": 75,
        "audio_db": 45
    }
    return insight_generator.generate_classroom_insight(summary)

@app.get("/api/analytics/trends/{session_id}")
async def get_trends(session_id: int):
    return analytics_service.get_session_trends(session_id)

@app.get("/api/reports/export/{session_id}/pdf")
async def export_pdf(session_id: int):
    pdf_buffer = report_generator.generate_pdf_report(session_id)
    if not pdf_buffer:
        raise HTTPException(status_code=404, detail="Session not found")
    return Response(content=pdf_buffer.read(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=report_{session_id}.pdf"})

@app.get("/api/reports/export/{session_id}/csv")
async def export_csv(session_id: int):
    csv_data = report_generator.generate_csv_export(session_id)
    if not csv_data:
        raise HTTPException(status_code=404, detail="Session not found")
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=report_{session_id}.csv"})

# WebSockets
@app.websocket("/ws/video")
async def video_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        camera.start()
    except:
        pass 

    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                await asyncio.sleep(0.1)
                continue
            
            processed_frame, metrics = session_manager.process_frame(frame)
            
            # Phase 4: Gamification & Suggestions Real-time
            leaderboard = gamification_engine.process_frame_points(metrics)
            metrics['leaderboard'] = leaderboard[:5] # Top 5
            
            # Generate Recommendations
            recs = recommendations_engine.generate_realtime_recommendations(metrics)
            metrics['recommendations'] = recs
            
            _, buffer = cv2.imencode('.jpg', processed_frame)
            await websocket.send_bytes(buffer.tobytes())
            await websocket.send_text(json.dumps(metrics))
            await asyncio.sleep(0.033)
            
    except WebSocketDisconnect:
        print("Video Client disconnected")
    except Exception as e:
        print(f"Video Error: {e}")

@app.websocket("/ws/audio")
async def audio_endpoint(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()
    last_db_log = 0
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_array = np.frombuffer(data, dtype=np.float32)
            metrics = audio_analyzer.analyze_audio_chunk(audio_array)
            if metrics:
                await websocket.send_json(metrics)
                if session_manager.active_session_id and (time.time() - last_db_log > 5.0):
                    from core.database import AudioMetric
                    db_metric = AudioMetric(
                        session_id=str(session_manager.active_session_id),
                        noise_db=metrics['noise_db'],
                        speech_ratio=0.0, 
                        activity_type=metrics['activity_type']
                    )
                    db.add(db_metric)
                    db.commit()
                    last_db_log = time.time()
    except Exception as e:
        print(f"Audio Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

