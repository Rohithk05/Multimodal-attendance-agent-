import librosa
import numpy as np
import os

class AudioAnalyzer:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
    
    def analyze_audio_chunk(self, audio_data):
        """
        Analyzes raw audio bytes/array:
        1. Noise level (decibels)
        2. Speech vs silence ratio
        3. Sound activity patterns
        
        Returns engagement metrics
        """
        try:
            # Convert bytes to float32 numpy array if needed
            if isinstance(audio_data, bytes):
                # Assuming 16-bit PCM
                y = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                y = audio_data

            if len(y) == 0:
                return None

            # Metrics
            noise_level = self.get_noise_level(y)  # dB
            # speech_ratio = self.estimate_speech_ratio(y)  # 0-1 (Requires longer buffer usually)
            activity = self.detect_activity(y)  # active/silent/chaotic
            
            return {
                'noise_db': float(noise_level),
                # 'speech_ratio': float(speech_ratio),
                'activity_type': activity,
                'engagement_level': self.map_to_engagement(noise_level, activity)
            }
        except Exception as e:
            print(f"Audio analysis error: {e}")
            return None
    
    def get_noise_level(self, y):
        rms = np.sqrt(np.mean(y**2))
        return 20 * np.log10(max(rms, 1e-10))
    
    def estimate_speech_ratio(self, y):
        # Zero crossing rate is a simple proxy for speech vs noise
        zcr = librosa.feature.zero_crossing_rate(y)
        return np.mean(zcr)
    
    def detect_activity(self, y):
        # Simple energy based activity detection
        rms = np.sqrt(np.mean(y**2))
        
        # Thresholds need calibration based on mic sensitivity
        if rms < 0.005:
            return 'silent'
        elif rms < 0.05:
            return 'normal_discussion'
        else:
            return 'chaotic_loud'
    
    def map_to_engagement(self, noise, activity):
        if activity == 'silent':
            return 'low_engagement'
        elif activity == 'normal_discussion':
            return 'high_engagement'
        else:
            return 'moderate_engagement'
