import mediapipe as mp
try:
    print(f"MP dir: {dir(mp)}")
    print(f"Solutions: {mp.solutions}")
    print(f"FaceDetection: {mp.solutions.face_detection}")
except Exception as e:
    print(f"Error: {e}")
