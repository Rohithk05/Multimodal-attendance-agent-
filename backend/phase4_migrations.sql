CREATE TABLE IF NOT EXISTS teacher_profiles (
    teacher_id VARCHAR(50) PRIMARY KEY,
    effectiveness_score FLOAT DEFAULT 0.0,
    total_sessions INTEGER DEFAULT 0,
    avg_engagement FLOAT DEFAULT 0.0,
    improvement_trend FLOAT DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS student_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    student_id VARCHAR(50), 
    points INTEGER DEFAULT 0,
    badge VARCHAR(50),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    trigger_condition TEXT,
    suggestion_text TEXT,
    priority_level VARCHAR(10),
    expected_impact FLOAT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
