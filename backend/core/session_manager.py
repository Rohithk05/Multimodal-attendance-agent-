import cv2
import time
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session as DBSession
from deep_sort_realtime.deepsort_tracker import DeepSort

from .database import SessionLocal, Session as SessionModel, SessionPerson, PersonMetric, get_db
from .emotion_detector_v2 import MediaPipeEmotionDetector

class SessionManager:
    def __init__(self):
        self.active_session_id = None
        self.active_session_data = None
        # Initialize DeepSORT
        self.tracker = DeepSort(max_age=60, n_init=3)
        self.emotion_detector = MediaPipeEmotionDetector()
        
        # In-memory history for active session
        # { 'track_id': { 'name': str, 'emotions': [], 'attention': [], 'first_seen': ts, 'last_seen': ts } }
        self.person_history = {}
        self.start_time = None
        
        # Throttling
        self.last_db_update = 0
        
    def start_session(self, teacher_id="teacher_1", class_id="class_1"):
        db = SessionLocal()
        try:
            # Close any existing active sessions
            active = db.query(SessionModel).filter(SessionModel.status == "active").all()
            for s in active:
                s.status = "completed"
                s.end_time = datetime.utcnow()
            
            new_session = SessionModel(
                teacher_id=teacher_id,
                class_id=class_id,
                start_time=datetime.utcnow(),
                status="active"
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            self.active_session_id = new_session.id
            self.active_session_data = new_session
            self.start_time = time.time()
            self.person_history = {}
            
            # Reset tracker
            self.tracker.delete_all_tracks()
            
            return {"status": "started", "session_id": self.active_session_id}
        except Exception as e:
            print(f"Error starting session: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def stop_session(self):
        if not self.active_session_id:
            return {"status": "no_active_session"}
            
        db = SessionLocal()
        try:
            session = db.query(SessionModel).filter(SessionModel.id == self.active_session_id).first()
            if session:
                session.status = "completed"
                session.end_time = datetime.utcnow()
                
                # Save final summaries to SessionPeople
                for pid, data in self.person_history.items():
                    # Calculate aggregates
                    avg_att = np.mean(data['attention']) if data['attention'] else 0
                    
                    # Determine dominant emotion
                    emotions = [e['label'] for e in data['emotions']]
                    if emotions:
                        dom = max(set(emotions), key=emotions.count)
                    else:
                        dom = "neutral"
                        
                    duration = data['last_seen'] - data['first_seen']
                    
                    sp = SessionPerson(
                        session_id=self.active_session_id,
                        person_id=str(pid),
                        total_time_present=duration,
                        avg_attention=float(avg_att),
                        dominant_emotion=dom
                    )
                    db.add(sp)
                
                db.commit()
                
            self.active_session_id = None
            self.active_session_data = None
            self.person_history = {}
            return {"status": "stopped"}
        finally:
            db.close()
            
    def process_frame(self, frame):
        """
        Main pipeline step.
        """
        # 1. Detection & Emotion Analysis
        # returns list of {bbox, emotion, landmarks}
        detections_raw = self.emotion_detector.detect(frame)
        
        current_people = []
        
        # 2. Prepare for DeepSORT
        # format: [[x,y,w,h], confidence, detection_class]
        ds_detections = []
        for det in detections_raw:
            bbox = det['bbox']
            conf = det['emotion'].confidence
            # We map detection index to associate later
            ds_detections.append((bbox, conf, "face", det)) 
            # Note: DeepSort expects (bbox, conf, class_name) usually. 
            # deep_sort_realtime allows passing 'others' data?
            # Actually deep-sort-realtime update_tracks accepts:
            # raw_detections list of (ltwh, confidence, class)
            
        # 3. Tracking
        # We need to map back inputs. 
        # DeepSORT might not return tracks in same order. 
        # But we can try to match by IoU or assume tracker handles it.
        # deep-sort-realtime requires simple format.
        
        formatted_dets = []
        for det in detections_raw:
             # (left, top, w, h), confidence, detection_class
             formatted_dets.append((det['bbox'], det['emotion'].confidence, 'person'))
             
        tracks = self.tracker.update_tracks(formatted_dets, frame=frame)
        
        # 4. Process Tracks
        db_metrics = [] # To save to DB
        
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
                
            track_id = track.track_id
            ltrb = track.to_ltrb() # left, top, right, bottom
            
            # Find closest original detection to attach emotion info
            # Simple IoU matching (or simple distance)
            matched_emotion = None
            
            # Get track center
            tx = (ltrb[0] + ltrb[2]) / 2
            ty = (ltrb[1] + ltrb[3]) / 2
            
            best_dist = 9999
            for det in detections_raw:
                dx, dy, dw, dh = det['bbox']
                cx = dx + dw/2
                cy = dy + dh/2
                dist = np.sqrt((tx-cx)**2 + (ty-cy)**2)
                if dist < 50: # Threshold pixels
                    if dist < best_dist:
                        best_dist = dist
                        matched_emotion = det['emotion']
            
            if matched_emotion:
                # Update Person History
                if track_id not in self.person_history:
                    self.person_history[track_id] = {
                        'emotions': [],
                        'attention': [],
                        'first_seen': time.time(),
                        'last_seen': time.time()
                    }
                
                ph = self.person_history[track_id]
                ph['last_seen'] = time.time()
                ph['emotions'].append({'label': matched_emotion.emotion, 'ts': time.time()})
                
                # Attention Proxy (Confidence of emotion usually correlates with face visibility/forwardness)
                # But we can also use gaze if we had it. using (1 - bored_score) etc.
                att_score = matched_emotion.confidence * 100
                if matched_emotion.emotion in ['bored', 'distracted']:
                    att_score = 30
                
                ph['attention'].append(att_score)
                
                # Annotate Frame
                label = f"ID: {track_id} | {matched_emotion.emotion}"
                color = (0, 255, 0)
                if matched_emotion.emotion in ['bored', 'sad']:
                    color = (0, 0, 255)
                
                cv2.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), color, 2)
                cv2.putText(frame, label, (int(ltrb[0]), int(ltrb[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                person_data = {
                    'id': track_id,
                    'bbox': [int(x) for x in ltrb],
                    'emotion': matched_emotion.emotion,
                    'confidence': matched_emotion.confidence,
                    'attention': att_score
                }
                current_people.append(person_data)
                
                # Collect DB Metric
                if self.active_session_id:
                     db_metrics.append(PersonMetric(
                         session_id=self.active_session_id,
                         person_id=str(track_id),
                         emotion=matched_emotion.emotion,
                         emotion_confidence=matched_emotion.confidence,
                         attention_score=att_score
                     ))

        # 5. DB Logging (Throttled 2s)
        if self.active_session_id and (time.time() - self.last_db_update > 2.0):
            if db_metrics:
                db = SessionLocal()
                try:
                    for m in db_metrics:
                        db.add(m)
                    
                    # Update session count
                    sess = db.query(SessionModel).get(self.active_session_id)
                    if sess:
                        sess.people_count = len(current_people)
                    
                    db.commit()
                    self.last_db_update = time.time()
                finally:
                    db.close()
                    
        return frame, {
            'timestamp': datetime.utcnow().isoformat(),
            'total_people': len(current_people),
            'people': current_people,
            'session_active': self.active_session_id is not None
        }

    def get_status(self):
        return {
            "active": self.active_session_id is not None,
            "session_id": self.active_session_id,
            "people_count": len(self.person_history), # Total unique people seen
            "duration": time.time() - self.start_time if self.start_time else 0
        }
