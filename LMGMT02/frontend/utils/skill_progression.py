"""
Skill Level Progression System
Tracks user progress and calculates skill levels
"""
import sqlite3
from datetime import datetime
from pathlib import Path


class SkillProgressionSystem:
    """Manage user skill levels and XP progression"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "skill_progression.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize skill progression database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_levels (
                user_id INTEGER PRIMARY KEY,
                level TEXT NOT NULL,
                xp_points INTEGER DEFAULT 0,
                topics_completed INTEGER DEFAULT 0,
                quizzes_taken INTEGER DEFAULT 0,
                avg_quiz_score REAL DEFAULT 0,
                coding_challenges INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS xp_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                xp_gained INTEGER NOT NULL,
                reason TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def calculate_skill_level(self, user_id, learning_db):
        """
        Calculate user's skill level based on activity
        
        Returns:
            dict: {
                'level': 'Beginner/Intermediate/Advanced/Expert',
                'xp': current XP,
                'next_level_xp': XP needed for next level,
                'progress_percentage': progress to next level
            }
        """
        try:
            # Get user stats from learning database
            topics_completed = learning_db.get_completed_topics_count(user_id)
            avg_quiz_score = learning_db.get_average_quiz_score(user_id)
            quizzes_taken = learning_db.get_quiz_count(user_id)
            
            # Calculate XP
            xp = self._calculate_xp(topics_completed, avg_quiz_score, quizzes_taken)
            
            # Determine level
            level, next_level_xp = self._determine_level(xp)
            
            # Calculate progress to next level
            level_thresholds = {
                "Beginner": 0,
                "Intermediate": 100,
                "Advanced": 300,
                "Expert": 600
            }
            
            current_level_xp = level_thresholds[level]
            progress_percentage = ((xp - current_level_xp) / (next_level_xp - current_level_xp) * 100) if next_level_xp > current_level_xp else 100
            progress_percentage = min(100, max(0, progress_percentage))
            
            # Save to database
            self._save_skill_level(user_id, level, xp, topics_completed, quizzes_taken, avg_quiz_score)
            
            return {
                'level': level,
                'xp': xp,
                'next_level_xp': next_level_xp,
                'progress_percentage': progress_percentage,
                'topics_completed': topics_completed,
                'quizzes_taken': quizzes_taken,
                'avg_quiz_score': avg_quiz_score
            }
            
        except Exception as e:
            print(f"Error calculating skill level: {e}")
            return {
                'level': 'Beginner',
                'xp': 0,
                'next_level_xp': 100,
                'progress_percentage': 0,
                'topics_completed': 0,
                'quizzes_taken': 0,
                'avg_quiz_score': 0
            }
    
    def _calculate_xp(self, topics_completed, avg_quiz_score, quizzes_taken, coding_challenges=0):
        """Calculate total XP based on activities"""
        xp = 0
        
        # XP from completed topics (10 XP each)
        xp += topics_completed * 10
        
        # XP from quiz performance (up to 5 XP per quiz based on score)
        xp += int(quizzes_taken * (avg_quiz_score / 20))  # Max 5 XP per quiz at 100% score
        
        # XP from coding challenges (15 XP each)
        xp += coding_challenges * 15
        
        return xp
    
    def _determine_level(self, xp):
        """Determine skill level based on XP"""
        if xp < 100:
            return "Beginner", 100
        elif xp < 300:
            return "Intermediate", 300
        elif xp < 600:
            return "Advanced", 600
        else:
            return "Expert", 1000
    
    def _save_skill_level(self, user_id, level, xp, topics, quizzes, avg_score):
        """Save skill level to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO skill_levels 
            (user_id, level, xp_points, topics_completed, quizzes_taken, avg_quiz_score, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, level, xp, topics, quizzes, avg_score, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def add_xp(self, user_id, xp_amount, reason):
        """Add XP to user and log the reason"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Log XP gain
        cursor.execute("""
            INSERT INTO xp_history (user_id, xp_gained, reason)
            VALUES (?, ?, ?)
        """, (user_id, xp_amount, reason))
        
        # Update total XP
        cursor.execute("""
            UPDATE skill_levels
            SET xp_points = xp_points + ?,
                updated_at = ?
            WHERE user_id = ?
        """, (xp_amount, datetime.now(), user_id))
        
        conn.commit()
        conn.close()
    
    def get_xp_history(self, user_id, limit=10):
        """Get recent XP gains"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT xp_gained, reason, timestamp
            FROM xp_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        history = [
            {
                'xp': row[0],
                'reason': row[1],
                'timestamp': row[2]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return history
    
    def get_level_badge_emoji(self, level):
        """Get emoji badge for skill level"""
        badges = {
            "Beginner": "🌱",
            "Intermediate": "🌿",
            "Advanced": "🌳",
            "Expert": "🏆"
        }
        return badges.get(level, "🌱")
    
    def get_level_color(self, level):
        """Get color for skill level"""
        colors = {
            "Beginner": "#10b981",
            "Intermediate": "#3b82f6",
            "Advanced": "#8b5cf6",
            "Expert": "#f59e0b"
        }
        return colors.get(level, "#10b981")


def get_skill_system():
    """Get skill progression system instance"""
    return SkillProgressionSystem()
