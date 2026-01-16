class RecommendationsEngine:
    def generate_realtime_recommendations(self, session_status: dict):
        """
        Rule-based recommendations for immediate feedback.
        Input: Session status dict (people, emotions, attention)
        Output: List of { type: 'alert'|'warning'|'info', message: str }
        """
        recs = []
        
        # 1. Low Attention Alert
        avg_att = 0
        people = session_status.get('people', [])
        if people:
            avg_att = sum(p['attention'] for p in people) / len(people)
            
            # Individual check
            for p in people:
                if p['attention'] < 40:
                    recs.append({
                        'type': 'alert',
                        'message': f"Student {p['id']} is distracted ({p['attention']}%)."
                    })
        
        # 2. Global Attention Warning
        if len(people) > 2 and avg_att < 60:
             recs.append({
                 'type': 'warning',
                 'message': "Class engagement dropping below 60%. Consider a brain break."
             })
             
        # 3. Emotion Check
        bored_count = sum(1 for p in people if p['emotion'] == 'bored')
        confused_count = sum(1 for p in people if p['emotion'] == 'confused')
        
        if bored_count >= 2:
             recs.append({'type': 'info', 'message': "Multiple students appear bored. Change activity?"})
             
        if confused_count >= 1:
             recs.append({'type': 'alert', 'message': "Confusion detected. Check for understanding."})
             
        if not recs and people:
             recs.append({'type': 'success', 'message': "Engagement is optimal. Keep going!"})
             
        return recs
