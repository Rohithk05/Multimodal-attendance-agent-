CREATE TABLE IF NOT EXISTS session_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    insight_text TEXT,
    confidence FLOAT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    student_id VARCHAR(50),
    recommendation TEXT,
    urgency_level VARCHAR(20),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
