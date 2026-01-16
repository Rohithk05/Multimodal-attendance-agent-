import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AISuggestionEngine:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None
        
    def generate_suggestions(self, session_data: dict):
        """
        Analyze session data and generate 3 prioritized suggestions.
        """
        if not self.client:
            return self._fallback_suggestions(session_data)
            
        prompt = f"""
        Analyze this classroom data:
        - Students: {session_data.get('total_people', 0)}
        - Avg Attention: {session_data.get('avg_attention', 0)}%
        - Dominant Emotion: {session_data.get('dominant_emotion', 'neutral')}
        
        Generate 3 prioritized suggestions for teacher.
        Format strictly:
        1. [Priority: High/Med/Low] | [Action] | [Impact]
        2. [Priority: High/Med/Low] | [Action] | [Impact]
        3. [Priority: High/Med/Low] | [Action] | [Impact]
        """
        
        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert AI teaching assistant."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192", 
                temperature=0.7,
                max_tokens=200
            )
            
            response = completion.choices[0].message.content
            return self._parse_response(response)
            
        except Exception as e:
            print(f"AI Suggestion Error: {e}")
            return self._fallback_suggestions(session_data)
            
    def _parse_response(self, text):
        suggestions = []
        lines = text.strip().split('\n')
        for line in lines:
            if "|" in line:
                parts = line.split("|")
                if len(parts) >= 3:
                     # Remove numbering
                     prio = parts[0].split('.')[-1].strip().replace("[Priority: ", "").replace("]", "")
                     action = parts[1].strip().replace("[Action]", "")
                     impact = parts[2].strip().replace("[Impact]", "")
                     
                     suggestions.append({
                         "priority": prio,
                         "action": action,
                         "impact": impact
                     })
        return suggestions[:3]

    def _fallback_suggestions(self, data):
        att = data.get('avg_attention', 0)
        if att < 60:
            return [
                {"priority": "High", "action": "Ask a question to random student", "impact": "+15% Attention"},
                {"priority": "Med", "action": "Switch to interactive activity", "impact": "Re-engagement"},
                {"priority": "Low", "action": "Check room temperature", "impact": "Comfort"}
            ]
        else:
             return [
                {"priority": "High", "action": "Challenge students with harder problem", "impact": "Deep Learning"},
                {"priority": "Med", "action": "Gamify next segment", "impact": "+10% Fun"},
                {"priority": "Low", "action": "Continue current pace", "impact": "Maintenance"}
            ]
