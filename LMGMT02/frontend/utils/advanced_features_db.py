"""
Advanced Features Database Management
Handles flashcards, mindmaps, streaks, badges, bookmarks, recommendations, and challenges
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class AdvancedFeaturesDB:
    """Manage advanced learning features in database"""
    
    def __init__(self, db_path: str = "frontend_users.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Create all advanced feature tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Flashcards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Mind maps table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mindmaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                mindmap_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Learning streak table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_streak (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                streak_count INTEGER DEFAULT 0,
                last_activity_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Badges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_name TEXT NOT NULL,
                badge_description TEXT,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, badge_name)
            )
        """)
        
        # Bookmarks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                content TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Learning recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recommended_topic TEXT NOT NULL,
                reason TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Code challenges table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                challenge_topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                problem_statement TEXT NOT NULL,
                solution TEXT,
                score INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Study notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                notes_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Learning path table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                path_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Audio cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                content_hash TEXT NOT NULL UNIQUE,
                audio_url TEXT,
                language TEXT DEFAULT 'en',
                duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Audio history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                audio_id INTEGER,
                listened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (audio_id) REFERENCES audio_cache(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # Flashcards Methods
    
    def save_flashcards(self, user_id: int, topic: str, flashcards: List[Dict]) -> bool:
        """Save flashcards for a topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for card in flashcards:
                cursor.execute("""
                    INSERT INTO flashcards (user_id, topic, question, answer)
                    VALUES (?, ?, ?, ?)
                """, (user_id, topic, card['question'], card['answer']))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving flashcards: {e}")
            return False
        finally:
            conn.close()
    
    def get_flashcards(self, user_id: int, topic: str) -> List[Dict]:
        """Get flashcards for a topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT question, answer, created_at
                FROM flashcards
                WHERE user_id = ? AND topic = ?
                ORDER BY created_at DESC
            """, (user_id, topic))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting flashcards: {e}")
            return []
        finally:
            conn.close()
    
    # Mind Map Methods
    
    def save_mindmap(self, user_id: int, topic: str, mindmap_data: str) -> bool:
        """Save mind map data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO mindmaps (user_id, topic, mindmap_data)
                VALUES (?, ?, ?)
            """, (user_id, topic, mindmap_data))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving mindmap: {e}")
            return False
        finally:
            conn.close()
    
    def get_mindmap(self, user_id: int, topic: str) -> Optional[str]:
        """Get mind map data for a topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT mindmap_data
                FROM mindmaps
                WHERE user_id = ? AND topic = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id, topic))
            
            result = cursor.fetchone()
            return result['mindmap_data'] if result else None
        except Exception as e:
            print(f"Error getting mindmap: {e}")
            return None
        finally:
            conn.close()
    
    # Learning Streak Methods
    
    def update_streak(self, user_id: int) -> int:
        """Update learning streak"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            today = datetime.now().date()
            
            # Get current streak
            cursor.execute("""
                SELECT streak_count, last_activity_date
                FROM learning_streak
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                last_date = datetime.strptime(result['last_activity_date'], '%Y-%m-%d').date() if result['last_activity_date'] else None
                current_streak = result['streak_count']
                
                if last_date:
                    days_diff = (today - last_date).days
                    
                    if days_diff == 0:
                        # Same day, no change
                        new_streak = current_streak
                    elif days_diff == 1:
                        # Consecutive day, increase streak
                        new_streak = current_streak + 1
                    else:
                        # Gap > 1 day, reset streak
                        new_streak = 1
                else:
                    new_streak = 1
                
                # Update streak
                cursor.execute("""
                    UPDATE learning_streak
                    SET streak_count = ?, last_activity_date = ?
                    WHERE user_id = ?
                """, (new_streak, today, user_id))
            else:
                # Create new streak
                new_streak = 1
                cursor.execute("""
                    INSERT INTO learning_streak (user_id, streak_count, last_activity_date)
                    VALUES (?, ?, ?)
                """, (user_id, new_streak, today))
            
            conn.commit()
            return new_streak
        except Exception as e:
            print(f"Error updating streak: {e}")
            return 0
        finally:
            conn.close()
    
    def get_streak(self, user_id: int) -> int:
        """Get current learning streak"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT streak_count, last_activity_date
                FROM learning_streak
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result and result['last_activity_date']:
                last_date = datetime.strptime(result['last_activity_date'], '%Y-%m-%d').date()
                today = datetime.now().date()
                days_diff = (today - last_date).days
                
                # If more than 1 day gap, streak is broken
                if days_diff > 1:
                    return 0
                
                return result['streak_count']
            
            return 0
        except Exception as e:
            print(f"Error getting streak: {e}")
            return 0
        finally:
            conn.close()
    
    # Badge Methods
    
    def award_badge(self, user_id: int, badge_name: str, description: str) -> bool:
        """Award a badge to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO badges (user_id, badge_name, badge_description)
                VALUES (?, ?, ?)
            """, (user_id, badge_name, description))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error awarding badge: {e}")
            return False
        finally:
            conn.close()
    
    def get_badges(self, user_id: int) -> List[Dict]:
        """Get all badges for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT badge_name, badge_description, earned_at
                FROM badges
                WHERE user_id = ?
                ORDER BY earned_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting badges: {e}")
            return []
        finally:
            conn.close()
    
    def has_badge(self, user_id: int, badge_name: str) -> bool:
        """Check if user has a badge"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id FROM badges
                WHERE user_id = ? AND badge_name = ?
            """, (user_id, badge_name))
            
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking badge: {e}")
            return False
        finally:
            conn.close()
    
    # Bookmark Methods
    
    def save_bookmark(self, user_id: int, topic: str, content: str = "") -> bool:
        """Save a bookmark"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO bookmarks (user_id, topic, content)
                VALUES (?, ?, ?)
            """, (user_id, topic, content))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving bookmark: {e}")
            return False
        finally:
            conn.close()
    
    def get_bookmarks(self, user_id: int) -> List[Dict]:
        """Get all bookmarks for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT topic, content, saved_at
                FROM bookmarks
                WHERE user_id = ?
                ORDER BY saved_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting bookmarks: {e}")
            return []
        finally:
            conn.close()
    
    def delete_bookmark(self, user_id: int, topic: str) -> bool:
        """Delete a bookmark"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM bookmarks
                WHERE user_id = ? AND topic = ?
            """, (user_id, topic))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting bookmark: {e}")
            return False
        finally:
            conn.close()
    
    # Recommendation Methods
    
    def save_recommendations(self, user_id: int, recommendations: List[Dict]) -> bool:
        """Save AI recommendations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Clear old recommendations
            cursor.execute("DELETE FROM learning_recommendations WHERE user_id = ?", (user_id,))
            
            # Insert new recommendations
            for rec in recommendations:
                cursor.execute("""
                    INSERT INTO learning_recommendations (user_id, recommended_topic, reason)
                    VALUES (?, ?, ?)
                """, (user_id, rec['topic'], rec.get('reason', '')))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving recommendations: {e}")
            return False
        finally:
            conn.close()
    
    def get_recommendations(self, user_id: int) -> List[Dict]:
        """Get AI recommendations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT recommended_topic, reason, generated_at
                FROM learning_recommendations
                WHERE user_id = ?
                ORDER BY generated_at DESC
                LIMIT 5
            """, (user_id,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
        finally:
            conn.close()
    
    # Code Challenge Methods
    
    def save_challenge(self, user_id: int, topic: str, difficulty: str, problem: str) -> int:
        """Save a code challenge"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO code_challenges (user_id, challenge_topic, difficulty, problem_statement)
                VALUES (?, ?, ?, ?)
            """, (user_id, topic, difficulty, problem))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error saving challenge: {e}")
            return 0
        finally:
            conn.close()
    
    def complete_challenge(self, challenge_id: int, solution: str, score: int) -> bool:
        """Mark challenge as completed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE code_challenges
                SET solution = ?, score = ?, completed_at = ?
                WHERE id = ?
            """, (solution, score, datetime.now(), challenge_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error completing challenge: {e}")
            return False
        finally:
            conn.close()
    
    def get_challenges(self, user_id: int) -> List[Dict]:
        """Get user's code challenges"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, challenge_topic, difficulty, problem_statement, score, completed_at
                FROM code_challenges
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting challenges: {e}")
            return []
        finally:
            conn.close()
    
    # Study Notes Methods
    
    def save_notes(self, user_id: int, topic: str, notes: str) -> bool:
        """Save study notes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO study_notes (user_id, topic, notes_content)
                VALUES (?, ?, ?)
            """, (user_id, topic, notes))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving notes: {e}")
            return False
        finally:
            conn.close()
    
    def get_notes(self, user_id: int, topic: str) -> Optional[str]:
        """Get study notes for a topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT notes_content
                FROM study_notes
                WHERE user_id = ? AND topic = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id, topic))
            
            result = cursor.fetchone()
            return result['notes_content'] if result else None
        except Exception as e:
            print(f"Error getting notes: {e}")
            return None
        finally:
            conn.close()
    
    # Learning Path Methods
    
    def save_learning_path(self, user_id: int, topic: str, path_data: str) -> bool:
        """Save personalized learning path"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO learning_paths (user_id, topic, path_data)
                VALUES (?, ?, ?)
            """, (user_id, topic, path_data))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving learning path: {e}")
            return False
        finally:
            conn.close()
    
    def get_learning_path(self, user_id: int, topic: str) -> Optional[str]:
        """Get learning path for a topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT path_data
                FROM learning_paths
                WHERE user_id = ? AND topic = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id, topic))
            
            result = cursor.fetchone()
            return result['path_data'] if result else None
        except Exception as e:
            print(f"Error getting learning path: {e}")
            return None
        finally:
            conn.close()
    
    # Audio Cache Methods
    
    def save_audio_cache(self, user_id: int, topic: str, content_hash: str, 
                        audio_url: str, language: str = 'en', duration: int = 0) -> bool:
        """Save audio to cache"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO audio_cache 
                (user_id, topic, content_hash, audio_url, language, duration)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, topic, content_hash, audio_url, language, duration))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving audio cache: {e}")
            return False
        finally:
            conn.close()
    
    def get_audio_cache(self, content_hash: str) -> Optional[Dict]:
        """Get cached audio by content hash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, audio_url, language, duration, created_at
                FROM audio_cache
                WHERE content_hash = ?
            """, (content_hash,))
            
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"Error getting audio cache: {e}")
            return None
        finally:
            conn.close()
    
    def save_audio_history(self, user_id: int, topic: str, audio_id: int) -> bool:
        """Save audio listening history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO audio_history (user_id, topic, audio_id)
                VALUES (?, ?, ?)
            """, (user_id, topic, audio_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving audio history: {e}")
            return False
        finally:
            conn.close()
    
    def get_audio_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's audio listening history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT h.topic, h.listened_at, c.language, c.duration
                FROM audio_history h
                LEFT JOIN audio_cache c ON h.audio_id = c.id
                WHERE h.user_id = ?
                ORDER BY h.listened_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting audio history: {e}")
            return []
        finally:
            conn.close()


# Global instance
_advanced_db = None

def get_advanced_db() -> AdvancedFeaturesDB:
    """Get global advanced features database instance"""
    global _advanced_db
    if _advanced_db is None:
        _advanced_db = AdvancedFeaturesDB()
    return _advanced_db
