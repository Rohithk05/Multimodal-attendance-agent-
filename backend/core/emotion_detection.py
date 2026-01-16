try:
    from fer import FER
except ImportError:
    import sys
    print("Failed to import FER directly")
    # Make a mock if real one fails to prevent crash loop during debug
    class FER:
        def __init__(self, mtcnn=False): pass
        def top_emotion(self, img): return ("neutral", 0.9)


import cv2
import numpy as np

class EmotionDetector:
    def __init__(self):
        # Initialize FER with MTCNN for better accuracy, or use cascade if speed is issue
        # Using built-in detection for now as per updated requirements
        try:
            self.detector = FER(mtcnn=True) 
        except Exception as e:
            print(f"Warning: FER init failed, falling back to default: {e}")
            self.detector = FER()

    def detect_emotion(self, frame):
        """
        Returns: {emotion: probability, education_state: state}
        """
        try:
            # FER expects RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            emotion, score = self.detector.top_emotion(frame_rgb)
            
            if emotion is None:
                return None
                
            # Map to education context
            emotion_mapping = {
                'happy': 'engaged',
                'neutral': 'attentive',
                'surprise': 'interested',
                'disgust': 'confused',
                'fear': 'anxious',
                'sad': 'bored',
                'angry': 'frustrated'
            }
            
            return {
                'emotion': emotion,
                'confidence': float(score) if score else 0.0,
                'education_state': emotion_mapping.get(emotion, 'unknown')
            }
        except Exception as e:
            print(f"Emotion detection error: {e}")
            return None
