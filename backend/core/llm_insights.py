from groq import Groq
import os
import random
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class InsightGenerator:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("⚠️ GROQ_API_KEY not found. Using Mock AI.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            
    def generate_classroom_insight(self, session_data: dict) -> dict:
        """
        Generates structured insights using Groq or Fallback.
        Returns: { 'insight': str, 'confidence': float, 'recommendation': str }
        """
        if not self.client:
             return self._generate_fallback(session_data)
             
        # Robust Prompt
        prompt = f"""
        Analyze this classroom session data and provide a teacher insight.
        
        Data:
        - Students Present: {session_data.get('total_people', 0)}
        - Average Attention: {session_data.get('avg_attention', 0)}%
        - Dominant Emotion: {session_data.get('dominant_emotion', 'neutral')}
        - Audio Level: {session_data.get('audio_db', '40')} dB ({session_data.get('audio_type', 'quiet')})
        - Trend: {session_data.get('trend', 'stable')}
        
        Output strictly in this format:
        Insight: [Scanning the room...]
        Recommendation: [Actionable advice]
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational AI assistant. Provide brief, professional, and actionable insights for a teacher."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.5,
                max_tokens=150,
            )
            
            response_text = chat_completion.choices[0].message.content
            
            # Simple Parsing
            insight = "Class status is stable."
            recommendation = "Maintain current pace."
            
            lines = response_text.split('\n')
            for line in lines:
                if line.startswith("Insight:"):
                    insight = line.replace("Insight:", "").strip()
                elif line.startswith("Recommendation:"):
                    recommendation = line.replace("Recommendation:", "").strip()
            
            return {
                "insight": insight,
                "confidence": 0.95,
                "recommendation": recommendation
            }
            
        except Exception as e:
            print(f"Groq API Error: {e}")
            return self._generate_fallback(session_data)

    def _generate_fallback(self, data):
        """Mock insights if API fails"""
        att = data.get('avg_attention', 0)
        emo = data.get('dominant_emotion', 'neutral')
        
        if att > 80:
             return {"insight": "High engagement detected.", "confidence": 0.9, "recommendation": "Great time to introduce complex topics."}
        elif att < 50:
             return {"insight": f"Attention is low ({att}%).", "confidence": 0.85, "recommendation": "Suggest a brain break or interactive activity."}
        elif emo == 'bored':
             return {"insight": "Students appear bored.", "confidence": 0.8, "recommendation": "Change the teaching modality."}
        elif emo == 'confused':
             return {"insight": "Signs of confusion detected.", "confidence": 0.8, "recommendation": "Pause and check for understanding."}
        else:
             return {"insight": "Classroom environment is stable.", "confidence": 0.9, "recommendation": "Continue with the lesson plan."}
