from deepface import DeepFace
import cv2
import numpy as np
import os

class FaceRecognizer:
    def __init__(self, db_path="student_db"):
        self.db_path = db_path
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            
    def register_student(self, img_path, student_id):
        # In a real app, we'd store embeddings. 
        # DeepFace.find uses a folder of images as DB.
        pass

    def recognize(self, frame):
        try:
            # Save frame temporarily or pass numpy array directly if supported (DeepFace supports numpy)
            # DeepFace.find requires a db_path with images.
            # If no DB yet, we can't recognize.
            if not os.listdir(self.db_path):
                return []
            
            # This is computing intensive, so we should run it sparingly
            dfs = DeepFace.find(img_path=frame, db_path=self.db_path, silent=True, enforce_detection=False)
            
            results = []
            for df in dfs:
                if not df.empty:
                    # df contains 'identity', 'distance', etc.
                    # We'd extract the student ID from the filename
                    results.append(df.to_dict(orient='records'))
            return results
        except Exception as e:
            print(f"Recognition error: {e}")
            return []

    def verify(self, frame, known_img_path):
        result = DeepFace.verify(frame, known_img_path, enforce_detection=False)
        return result
