class GamificationEngine:
    def __init__(self):
        # In-memory points storage for the active session
        self.session_points = {} # person_id -> points
        self.streaks = {} # person_id -> consecutive_high_attention_seconds

    def process_frame_points(self, metrics: dict):
        """
        Calculate points based on current frame metrics.
        metrics: { 'people': [ { 'id': '1', 'attention': 80, ... } ] }
        """
        updates = []
        
        for p in metrics.get('people', []):
            pid = p['id']
            att = p['attention']
            
            # Init
            if pid not in self.session_points: self.session_points[pid] = 0
            if pid not in self.streaks: self.streaks[pid] = 0
            
            # Points Logic (per second approx, assuming this is called per frame)
            # We scale down since fps is ~30. 
            # Logic: +10pts/sec -> +0.33pts/frame
            
            pts = 0
            if att > 90:
                pts = 0.33
                self.streaks[pid] += 1
            elif att > 70:
                pts = 0.16
                self.streaks[pid] = 0
            elif att > 50:
                pts = 0.03
                self.streaks[pid] = 0
            else:
                pts = -0.06 # -2pts/sec
                self.streaks[pid] = 0
                
            self.session_points[pid] += pts
            
            # Badge Logic
            badge = None
            if self.streaks[pid] > 300: # 10 seconds (approx 30fps)
                badge = "🔥 Hot Streak"
                
            updates.append({
                "id": pid,
                "points": int(self.session_points[pid]),
                "badge": badge
            })
            
        # rank
        updates.sort(key=lambda x: x['points'], reverse=True)
        return updates

    def get_leaderboard(self):
        leaderboard = []
        for pid, score in self.session_points.items():
            leaderboard.append({"id": pid, "points": int(score)})
        leaderboard.sort(key=lambda x: x['points'], reverse=True)
        return leaderboard[:5] # Top 5
