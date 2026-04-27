"""
Study Timer (Pomodoro Technique)
Helps users manage study sessions with focus and break intervals
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


class StudyTimer:
    """Pomodoro-style study timer"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "study_sessions.db"
        self._init_database()
        
        # Timer settings (in minutes)
        self.FOCUS_TIME = 25
        self.SHORT_BREAK = 5
        self.LONG_BREAK = 15
        self.SESSIONS_BEFORE_LONG_BREAK = 4
    
    def _init_database(self):
        """Initialize study sessions database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_type TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                topic TEXT,
                completed BOOLEAN DEFAULT 0,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                total_focus_minutes INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                completed_sessions INTEGER DEFAULT 0,
                UNIQUE(user_id, date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def start_session(self, user_id, session_type="focus", topic=None):
        """Start a new study session"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        duration = self.FOCUS_TIME if session_type == "focus" else self.SHORT_BREAK
        
        cursor.execute("""
            INSERT INTO study_sessions 
            (user_id, session_type, duration_minutes, topic, start_time)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, session_type, duration, topic, datetime.now()))
        
        session_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def complete_session(self, session_id, user_id):
        """Mark session as completed"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE study_sessions
            SET completed = 1, end_time = ?
            WHERE id = ? AND user_id = ?
        """, (datetime.now(), session_id, user_id))
        
        # Update daily stats
        today = datetime.now().date()
        
        cursor.execute("""
            SELECT session_type, duration_minutes FROM study_sessions
            WHERE id = ?
        """, (session_id,))
        
        result = cursor.fetchone()
        if result:
            session_type, duration = result
            
            if session_type == "focus":
                cursor.execute("""
                    INSERT INTO daily_stats (user_id, date, total_focus_minutes, total_sessions, completed_sessions)
                    VALUES (?, ?, ?, 1, 1)
                    ON CONFLICT(user_id, date) DO UPDATE SET
                        total_focus_minutes = total_focus_minutes + ?,
                        total_sessions = total_sessions + 1,
                        completed_sessions = completed_sessions + 1
                """, (user_id, today, duration, duration))
        
        conn.commit()
        conn.close()
    
    def get_today_stats(self, user_id):
        """Get today's study statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        cursor.execute("""
            SELECT total_focus_minutes, total_sessions, completed_sessions
            FROM daily_stats
            WHERE user_id = ? AND date = ?
        """, (user_id, today))
        
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                'focus_minutes': result[0],
                'total_sessions': result[1],
                'completed_sessions': result[2],
                'focus_hours': round(result[0] / 60, 1)
            }
        else:
            return {
                'focus_minutes': 0,
                'total_sessions': 0,
                'completed_sessions': 0,
                'focus_hours': 0
            }
    
    def get_week_stats(self, user_id):
        """Get this week's study statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        week_ago = (datetime.now() - timedelta(days=7)).date()
        
        cursor.execute("""
            SELECT SUM(total_focus_minutes), SUM(completed_sessions)
            FROM daily_stats
            WHERE user_id = ? AND date >= ?
        """, (user_id, week_ago))
        
        result = cursor.fetchone()
        
        conn.close()
        
        if result and result[0]:
            return {
                'focus_minutes': result[0],
                'completed_sessions': result[1],
                'focus_hours': round(result[0] / 60, 1)
            }
        else:
            return {
                'focus_minutes': 0,
                'completed_sessions': 0,
                'focus_hours': 0
            }
    
    def get_recent_sessions(self, user_id, limit=10):
        """Get recent study sessions"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_type, duration_minutes, topic, completed, start_time
            FROM study_sessions
            WHERE user_id = ?
            ORDER BY start_time DESC
            LIMIT ?
        """, (user_id, limit))
        
        sessions = [
            {
                'type': row[0],
                'duration': row[1],
                'topic': row[2],
                'completed': bool(row[3]),
                'start_time': row[4]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return sessions
    
    def get_productivity_score(self, user_id):
        """Calculate productivity score (0-100)"""
        today_stats = self.get_today_stats(user_id)
        
        # Target: 4 pomodoro sessions (100 minutes) per day
        target_minutes = 100
        actual_minutes = today_stats['focus_minutes']
        
        score = min(100, int((actual_minutes / target_minutes) * 100))
        
        return score


def get_study_timer():
    """Get study timer instance"""
    return StudyTimer()
