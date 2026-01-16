import cv2
import time
import asyncio
from fastapi import WebSocket

class CameraService:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False

    def start(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_id)
            self.is_running = True

    def stop(self):
        if self.cap:
            self.cap.release()
            self.cap = None
            self.is_running = False

    def get_frame(self):
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    async def stream_frames(self, websocket: WebSocket):
        await websocket.accept()
        self.start()
        try:
            while self.is_running:
                frame = self.get_frame()
                if frame is not None:
                    # Encode frame to JPEG
                    _, buffer = cv2.imencode('.jpg', frame)
                    # Send via websocket
                    await websocket.send_bytes(buffer.tobytes())
                # Control FPS slightly
                await asyncio.sleep(0.03) 
        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            self.stop()
