"""
Profile Database Management
Handles user profile data, settings, and achievements
"""
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import base64


class ProfileDB:
    """Manage user profiles in database"""
    
    def __init__(self, db_path: str = "frontend_users.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Create profile tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                username TEXT,
                bio TEXT,
                learning_interests TEXT,
                experience_level TEXT DEFAULT 'Beginner',
                profile_picture BLOB,
                location TEXT,
                occupation TEXT,
                website TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # User settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                theme TEXT DEFAULT 'Dark',
                language TEXT DEFAULT 'English',
                default_difficulty TEXT DEFAULT 'Intermediate',
                email_notifications INTEGER DEFAULT 1,
                learning_reminders INTEGER DEFAULT 1,
                weekly_summary INTEGER DEFAULT 1,
                achievement_alerts INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # User achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_id TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                achievement_description TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, achievement_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # Profile Methods
    
    def get_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM user_profiles WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
        finally:
            conn.close()
    
    def create_profile(self, user_id: int, username: str) -> bool:
        """Create initial profile for new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_profiles (user_id, username, full_name)
                VALUES (?, ?, ?)
            """, (user_id, username, username))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Profile already exists
            return True
        except Exception as e:
            print(f"Error creating profile: {e}")
            return False
        finally:
            conn.close()
    
    def update_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Update user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if profile exists
            cursor.execute("SELECT id FROM user_profiles WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing profile
                cursor.execute("""
                    UPDATE user_profiles
                    SET full_name = ?,
                        bio = ?,
                        learning_interests = ?,
                        experience_level = ?,
                        location = ?,
                        occupation = ?,
                        website = ?,
                        updated_at = ?
                    WHERE user_id = ?
                """, (
                    profile_data.get('full_name'),
                    profile_data.get('bio'),
                    profile_data.get('learning_interests'),
                    profile_data.get('experience_level'),
                    profile_data.get('location'),
                    profile_data.get('occupation'),
                    profile_data.get('website'),
                    datetime.now(),
                    user_id
                ))
            else:
                # Create new profile
                cursor.execute("""
                    INSERT INTO user_profiles 
                    (user_id, username, full_name, bio, learning_interests, experience_level, location, occupation, website)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    profile_data.get('username', ''),
                    profile_data.get('full_name'),
                    profile_data.get('bio'),
                    profile_data.get('learning_interests'),
                    profile_data.get('experience_level'),
                    profile_data.get('location'),
                    profile_data.get('occupation'),
                    profile_data.get('website')
                ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
        finally:
            conn.close()
    
    def update_profile_picture(self, user_id: int, image_data: bytes) -> bool:
        """Update profile picture"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE user_profiles
                SET profile_picture = ?, updated_at = ?
                WHERE user_id = ?
            """, (image_data, datetime.now(), user_id))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating profile picture: {e}")
            return False
        finally:
            conn.close()
    
    def get_profile_picture(self, user_id: int) -> Optional[bytes]:
        """Get profile picture"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT profile_picture FROM user_profiles WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result and result['profile_picture']:
                return result['profile_picture']
            return None
        except Exception as e:
            print(f"Error getting profile picture: {e}")
            return None
        finally:
            conn.close()
    
    # Settings Methods
    
    def get_settings(self, user_id: int) -> Optional[Dict]:
        """Get user settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM user_settings WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            print(f"Error getting settings: {e}")
            return None
        finally:
            conn.close()
    
    def create_default_settings(self, user_id: int) -> bool:
        """Create default settings for new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_settings (user_id)
                VALUES (?)
            """, (user_id,))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Settings already exist
            return True
        except Exception as e:
            print(f"Error creating settings: {e}")
            return False
        finally:
            conn.close()
    
    def update_settings(self, user_id: int, settings_data: Dict) -> bool:
        """Update user settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if settings exist
            cursor.execute("SELECT id FROM user_settings WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing settings
                cursor.execute("""
                    UPDATE user_settings
                    SET theme = ?,
                        language = ?,
                        default_difficulty = ?,
                        email_notifications = ?,
                        learning_reminders = ?,
                        weekly_summary = ?,
                        achievement_alerts = ?,
                        updated_at = ?
                    WHERE user_id = ?
                """, (
                    settings_data.get('theme'),
                    settings_data.get('language'),
                    settings_data.get('default_difficulty'),
                    settings_data.get('email_notifications', 1),
                    settings_data.get('learning_reminders', 1),
                    settings_data.get('weekly_summary', 1),
                    settings_data.get('achievement_alerts', 1),
                    datetime.now(),
                    user_id
                ))
            else:
                # Create new settings
                cursor.execute("""
                    INSERT INTO user_settings 
                    (user_id, theme, language, default_difficulty, email_notifications, learning_reminders, weekly_summary, achievement_alerts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    settings_data.get('theme'),
                    settings_data.get('language'),
                    settings_data.get('default_difficulty'),
                    settings_data.get('email_notifications', 1),
                    settings_data.get('learning_reminders', 1),
                    settings_data.get('weekly_summary', 1),
                    settings_data.get('achievement_alerts', 1)
                ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False
        finally:
            conn.close()
    
    # Achievement Methods
    
    def unlock_achievement(self, user_id: int, achievement_id: str, name: str, description: str) -> bool:
        """Unlock an achievement for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO user_achievements 
                (user_id, achievement_id, achievement_name, achievement_description)
                VALUES (?, ?, ?, ?)
            """, (user_id, achievement_id, name, description))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error unlocking achievement: {e}")
            return False
        finally:
            conn.close()
    
    def get_achievements(self, user_id: int) -> List[Dict]:
        """Get user's unlocked achievements"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT * FROM user_achievements 
                WHERE user_id = ?
                ORDER BY unlocked_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting achievements: {e}")
            return []
        finally:
            conn.close()
    
    def check_achievement(self, user_id: int, achievement_id: str) -> bool:
        """Check if user has unlocked an achievement"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id FROM user_achievements 
                WHERE user_id = ? AND achievement_id = ?
            """, (user_id, achievement_id))
            
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking achievement: {e}")
            return False
        finally:
            conn.close()
    
    # Statistics Methods (from learning_progress)
    
    def get_profile_statistics(self, user_id: int) -> Dict:
        """Get comprehensive profile statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {
                'topics_learned': 0,
                'quizzes_attempted': 0,
                'average_score': 0,
                'tasks_completed': 0,
                'total_study_time': 0,
                'current_streak': 0
            }
            
            # Topics learned
            cursor.execute("""
                SELECT COUNT(*) as count FROM learning_topics WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            stats['topics_learned'] = result['count'] if result else 0
            
            # Quizzes attempted
            cursor.execute("""
                SELECT COUNT(*) as count, AVG(percentage) as avg_score 
                FROM quiz_results WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                stats['quizzes_attempted'] = result['count'] if result['count'] else 0
                stats['average_score'] = result['avg_score'] if result['avg_score'] else 0
            
            # Tasks completed
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM roadmap_progress 
                WHERE user_id = ? AND completed = 1
            """, (user_id,))
            result = cursor.fetchone()
            stats['tasks_completed'] = result['count'] if result else 0
            
            return stats
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'topics_learned': 0,
                'quizzes_attempted': 0,
                'average_score': 0,
                'tasks_completed': 0,
                'total_study_time': 0,
                'current_streak': 0
            }
        finally:
            conn.close()


# Global instance
_profile_db = None

def get_profile_db() -> ProfileDB:
    """Get global profile database instance"""
    global _profile_db
    if _profile_db is None:
        _profile_db = ProfileDB()
    return _profile_db
