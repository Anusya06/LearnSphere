"""
Learning Progress Database Management
Tracks user learning progress, roadmap completion, and analytics
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st


class LearningProgressDB:
    """Manage learning progress in database"""
    
    def __init__(self, db_path: str = "frontend_users.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Create learning progress tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Roadmap storage table - stores each roadmap task
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_roadmaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                week_number INTEGER NOT NULL,
                week_title TEXT NOT NULL,
                task_name TEXT NOT NULL,
                task_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, topic, week_number, task_name)
            )
        """)
        
        # Roadmap progress table - tracks checkbox completion
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmap_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                task_name TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, topic, task_name)
            )
        """)
        
        # Learning progress table (legacy - keep for compatibility)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                week_number INTEGER,
                task_name TEXT,
                completed INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Generated content cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                content_text TEXT,
                roadmap_json TEXT,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Tutor chat history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tutor_chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT,
                user_message TEXT,
                ai_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Learning topics table - stores all generated topics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic_name TEXT NOT NULL,
                difficulty TEXT,
                generated_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Quiz results table - stores quiz attempts and scores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage REAL,
                time_taken INTEGER,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Learning completion table - tracks completed topics with study time
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_completed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                study_time_minutes INTEGER DEFAULT 0,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, topic)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_task_progress(self, user_id: int, topic: str, week_number: int, task_name: str, completed: bool):
        """Save or update task completion status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if task exists
            cursor.execute("""
                SELECT id, completed FROM learning_progress
                WHERE user_id = ? AND topic = ? AND week_number = ? AND task_name = ?
            """, (user_id, topic, week_number, task_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE learning_progress
                    SET completed = ?, completed_at = ?
                    WHERE id = ?
                """, (1 if completed else 0, datetime.now() if completed else None, existing['id']))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO learning_progress (user_id, topic, week_number, task_name, completed, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, topic, week_number, task_name, 1 if completed else 0, datetime.now() if completed else None))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving progress: {e}")
            return False
        finally:
            conn.close()
    
    def get_task_progress(self, user_id: int, topic: str, week_number: int, task_name: str) -> bool:
        """Get task completion status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT completed FROM learning_progress
                WHERE user_id = ? AND topic = ? AND week_number = ? AND task_name = ?
            """, (user_id, topic, week_number, task_name))
            
            result = cursor.fetchone()
            return bool(result['completed']) if result else False
        except:
            return False
        finally:
            conn.close()
    
    def get_topic_progress(self, user_id: int, topic: str) -> Dict:
        """Get overall progress for a topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tasks,
                    SUM(completed) as completed_tasks
                FROM learning_progress
                WHERE user_id = ? AND topic = ?
            """, (user_id, topic))
            
            result = cursor.fetchone()
            
            total = result['total_tasks'] if result else 0
            completed = result['completed_tasks'] if result else 0
            
            return {
                "total_tasks": total,
                "completed_tasks": completed,
                "percentage": (completed / total * 100) if total > 0 else 0
            }
        except:
            return {"total_tasks": 0, "completed_tasks": 0, "percentage": 0}
        finally:
            conn.close()
    
    def save_generated_content(self, user_id: int, topic: str, content: str, roadmap: str, difficulty: str):
        """Save generated content to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO generated_content (user_id, topic, content_text, roadmap_json, difficulty)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, topic, content, roadmap, difficulty))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving content: {e}")
            return False
        finally:
            conn.close()
    
    def get_generated_content(self, user_id: int, topic: str) -> Optional[Dict]:
        """Get previously generated content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT content_text, roadmap_json, difficulty, created_at
                FROM generated_content
                WHERE user_id = ? AND topic = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id, topic))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    "content": result['content_text'],
                    "roadmap": result['roadmap_json'],
                    "difficulty": result['difficulty'],
                    "created_at": result['created_at']
                }
            return None
        except:
            return None
        finally:
            conn.close()
    
    def save_tutor_message(self, user_id: int, topic: str, user_message: str, ai_response: str):
        """Save tutor chat message"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO tutor_chat (user_id, topic, user_message, ai_response)
                VALUES (?, ?, ?, ?)
            """, (user_id, topic, user_message, ai_response))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving chat: {e}")
            return False
        finally:
            conn.close()
    
    def get_tutor_history(self, user_id: int, topic: str, limit: int = 50) -> List[Dict]:
        """Get tutor chat history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT user_message, ai_response, created_at
                FROM tutor_chat
                WHERE user_id = ? AND topic = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, topic, limit))
            
            results = cursor.fetchall()
            
            return [
                {
                    "user_message": row['user_message'],
                    "ai_response": row['ai_response'],
                    "created_at": row['created_at']
                }
                for row in results
            ][::-1]  # Reverse to show oldest first
        except:
            return []
        finally:
            conn.close()
    
    def save_roadmap(self, user_id: int, topic: str, roadmap_data: Dict) -> bool:
        """Save complete roadmap to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # First, delete existing roadmap for this user and topic
            cursor.execute("""
                DELETE FROM learning_roadmaps
                WHERE user_id = ? AND topic = ?
            """, (user_id, topic))
            
            # Insert new roadmap tasks
            weeks = roadmap_data.get("weeks", [])
            for week in weeks:
                week_num = week.get("week", 1)
                week_title = week.get("title", f"Week {week_num}")
                tasks = week.get("tasks", [])
                
                for task_order, task_name in enumerate(tasks, 1):
                    cursor.execute("""
                        INSERT OR REPLACE INTO learning_roadmaps 
                        (user_id, topic, week_number, week_title, task_name, task_order)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (user_id, topic, week_num, week_title, task_name, task_order))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving roadmap: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def load_roadmap(self, user_id: int, topic: str) -> Optional[Dict]:
        """Load roadmap from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT week_number, week_title, task_name, task_order
                FROM learning_roadmaps
                WHERE user_id = ? AND topic = ?
                ORDER BY week_number, task_order
            """, (user_id, topic))
            
            results = cursor.fetchall()
            
            if not results:
                return None
            
            # Organize into weeks structure
            weeks_dict = {}
            for row in results:
                week_num = row['week_number']
                if week_num not in weeks_dict:
                    weeks_dict[week_num] = {
                        "week": week_num,
                        "title": row['week_title'],
                        "tasks": []
                    }
                weeks_dict[week_num]["tasks"].append(row['task_name'])
            
            # Convert to list
            weeks_list = [weeks_dict[k] for k in sorted(weeks_dict.keys())]
            
            return {"weeks": weeks_list}
        except Exception as e:
            print(f"Error loading roadmap: {e}")
            return None
        finally:
            conn.close()
    
    def roadmap_exists(self, user_id: int, topic: str) -> bool:
        """Check if roadmap exists for user and topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM learning_roadmaps
                WHERE user_id = ? AND topic = ?
            """, (user_id, topic))
            
            result = cursor.fetchone()
            return result['count'] > 0 if result else False
        except:
            return False
        finally:
            conn.close()
    
    def delete_roadmap(self, user_id: int, topic: str) -> bool:
        """Delete roadmap for user and topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM learning_roadmaps
                WHERE user_id = ? AND topic = ?
            """, (user_id, topic))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting roadmap: {e}")
            return False
        finally:
            conn.close()
    
    def save_roadmap_progress(self, user_id: int, topic: str, task_name: str, completed: bool) -> bool:
        """Save checkbox progress for a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO roadmap_progress 
                (user_id, topic, task_name, completed, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, topic, task_name, 1 if completed else 0, datetime.now()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving progress: {e}")
            return False
        finally:
            conn.close()
    
    def get_roadmap_progress(self, user_id: int, topic: str, task_name: str) -> bool:
        """Get checkbox status for a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT completed
                FROM roadmap_progress
                WHERE user_id = ? AND topic = ? AND task_name = ?
            """, (user_id, topic, task_name))
            
            result = cursor.fetchone()
            return bool(result['completed']) if result else False
        except:
            return False
        finally:
            conn.close()
    
    def get_roadmap_overall_progress(self, user_id: int, topic: str) -> Dict:
        """Get overall progress for roadmap"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get total tasks from roadmap
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM learning_roadmaps
                WHERE user_id = ? AND topic = ?
            """, (user_id, topic))
            
            total_result = cursor.fetchone()
            total_tasks = total_result['total'] if total_result else 0
            
            # Get completed tasks
            cursor.execute("""
                SELECT COUNT(*) as completed
                FROM roadmap_progress
                WHERE user_id = ? AND topic = ? AND completed = 1
            """, (user_id, topic))
            
            completed_result = cursor.fetchone()
            completed_tasks = completed_result['completed'] if completed_result else 0
            
            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
        except Exception as e:
            print(f"Error getting progress: {e}")
            return {"total_tasks": 0, "completed_tasks": 0, "percentage": 0}
        finally:
            conn.close()
    
    def save_learning_topic(self, user_id: int, topic_name: str, difficulty: str, content: str) -> bool:
        """Save a generated learning topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO learning_topics (user_id, topic_name, difficulty, generated_content)
                VALUES (?, ?, ?, ?)
            """, (user_id, topic_name, difficulty, content))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving learning topic: {e}")
            return False
        finally:
            conn.close()
    
    def save_quiz_result(self, user_id: int, topic: str, score: int, total_questions: int, time_taken: int = 0) -> bool:
        """Save quiz result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            percentage = (score / total_questions * 100) if total_questions > 0 else 0
            
            cursor.execute("""
                INSERT INTO quiz_results (user_id, topic, score, total_questions, percentage, time_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, topic, score, total_questions, percentage, time_taken))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving quiz result: {e}")
            return False
        finally:
            conn.close()
    
    def get_learning_topics(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get all learning topics for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT topic_name, difficulty, created_at
                FROM learning_topics
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            
            return [
                {
                    "topic_name": row['topic_name'],
                    "difficulty": row['difficulty'],
                    "created_at": row['created_at']
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting learning topics: {e}")
            return []
        finally:
            conn.close()
    
    def get_quiz_results(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get all quiz results for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT topic, score, total_questions, percentage, time_taken, attempted_at
                FROM quiz_results
                WHERE user_id = ?
                ORDER BY attempted_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            
            return [
                {
                    "topic": row['topic'],
                    "score": row['score'],
                    "total_questions": row['total_questions'],
                    "percentage": row['percentage'],
                    "time_taken": row['time_taken'],
                    "attempted_at": row['attempted_at']
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting quiz results: {e}")
            return []
        finally:
            conn.close()
    
    def get_analytics_summary(self, user_id: int) -> Dict:
        """Get analytics summary for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Count topics learned
            cursor.execute("""
                SELECT COUNT(*) as count FROM learning_topics WHERE user_id = ?
            """, (user_id,))
            topics_count = cursor.fetchone()['count']
            
            # Count quizzes attempted
            cursor.execute("""
                SELECT COUNT(*) as count FROM quiz_results WHERE user_id = ?
            """, (user_id,))
            quizzes_count = cursor.fetchone()['count']
            
            # Average quiz score
            cursor.execute("""
                SELECT AVG(percentage) as avg_score FROM quiz_results WHERE user_id = ?
            """, (user_id,))
            avg_result = cursor.fetchone()
            avg_score = avg_result['avg_score'] if avg_result['avg_score'] else 0
            
            # Latest topic
            cursor.execute("""
                SELECT topic_name FROM learning_topics 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (user_id,))
            latest_topic_result = cursor.fetchone()
            latest_topic = latest_topic_result['topic_name'] if latest_topic_result else "None"
            
            return {
                "topics_learned": topics_count,
                "quizzes_attempted": quizzes_count,
                "average_score": avg_score,
                "latest_topic": latest_topic
            }
        except Exception as e:
            print(f"Error getting analytics summary: {e}")
            return {
                "topics_learned": 0,
                "quizzes_attempted": 0,
                "average_score": 0,
                "latest_topic": "None"
            }
        finally:
            conn.close()
    
    def get_recent_activity(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent user activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            activities = []
            
            # Get recent topics
            cursor.execute("""
                SELECT 'topic' as type, topic_name as name, created_at as timestamp
                FROM learning_topics
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit // 2))
            
            for row in cursor.fetchall():
                activities.append({
                    "type": "topic",
                    "description": f"Generated topic: {row['name']}",
                    "timestamp": row['timestamp']
                })
            
            # Get recent quizzes
            cursor.execute("""
                SELECT 'quiz' as type, topic, score, total_questions, attempted_at as timestamp
                FROM quiz_results
                WHERE user_id = ?
                ORDER BY attempted_at DESC
                LIMIT ?
            """, (user_id, limit // 2))
            
            for row in cursor.fetchall():
                activities.append({
                    "type": "quiz",
                    "description": f"Completed quiz: {row['topic']} (Score: {row['score']}/{row['total_questions']})",
                    "timestamp": row['timestamp']
                })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return activities[:limit]
        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return []
        finally:
            conn.close()
    
    def get_quiz_performance_trend(self, user_id: int, limit: int = 15) -> List[Dict]:
        """Get quiz performance trend data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT topic, percentage, attempted_at
                FROM quiz_results
                WHERE user_id = ?
                ORDER BY attempted_at ASC
                LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            
            return [
                {
                    "topic": row['topic'],
                    "percentage": row['percentage'],
                    "attempted_at": row['attempted_at']
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting quiz performance trend: {e}")
            return []
        finally:
            conn.close()
    
    # Learning Completion Methods
    
    def mark_topic_completed(self, user_id: int, topic: str, study_time_minutes: int = 0) -> bool:
        """Mark a topic as completed with study time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO learning_completed (user_id, topic, study_time_minutes, completed_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, topic, study_time_minutes, datetime.now()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marking topic completed: {e}")
            return False
        finally:
            conn.close()
    
    def is_topic_completed(self, user_id: int, topic: str) -> bool:
        """Check if a topic is already completed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id FROM learning_completed
                WHERE user_id = ? AND topic = ?
            """, (user_id, topic))
            
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error checking topic completion: {e}")
            return False
        finally:
            conn.close()
    
    def get_completed_topics_count(self, user_id: int) -> int:
        """Get total number of completed topics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) as count FROM learning_completed
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting completed topics count: {e}")
            return 0
        finally:
            conn.close()
    
    def get_total_study_time(self, user_id: int) -> int:
        """Get total study time in minutes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT SUM(study_time_minutes) as total FROM learning_completed
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            return result['total'] if result and result['total'] else 0
        except Exception as e:
            print(f"Error getting total study time: {e}")
            return 0
        finally:
            conn.close()
    
    def get_completed_topics_list(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get list of completed topics with details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT topic, study_time_minutes, completed_at
                FROM learning_completed
                WHERE user_id = ?
                ORDER BY completed_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            
            return [
                {
                    "topic": row['topic'],
                    "study_time_minutes": row['study_time_minutes'],
                    "completed_at": row['completed_at']
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting completed topics list: {e}")
            return []
        finally:
            conn.close()
    
    def get_learning_analytics(self, user_id: int) -> Dict:
        """Get comprehensive learning analytics for dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get topic performance (completed topics with progress)
            cursor.execute("""
                SELECT topic, study_time_minutes, completed_at
                FROM learning_completed
                WHERE user_id = ?
                ORDER BY completed_at DESC
                LIMIT 10
            """, (user_id,))
            
            completed_topics = cursor.fetchall()
            topic_performance = []
            
            for row in completed_topics:
                topic_performance.append({
                    "topic": row['topic'],
                    "completion": 100,  # Completed topics are 100%
                    "study_time": row['study_time_minutes']
                })
            
            # Get weekly activity (last 7 days)
            from datetime import datetime, timedelta
            weekly_activity = []
            today = datetime.now()
            
            for i in range(6, -1, -1):  # Last 7 days
                day_date = today - timedelta(days=i)
                day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                # Get study time for this day
                cursor.execute("""
                    SELECT SUM(study_time_minutes) as total
                    FROM learning_completed
                    WHERE user_id = ? 
                    AND completed_at >= ? 
                    AND completed_at <= ?
                """, (user_id, day_start.strftime('%Y-%m-%d %H:%M:%S'), day_end.strftime('%Y-%m-%d %H:%M:%S')))
                
                result = cursor.fetchone()
                minutes = result['total'] if result and result['total'] else 0
                hours = minutes / 60.0
                
                # Day name (Mon, Tue, etc.)
                day_name = day_date.strftime('%a')
                
                weekly_activity.append({
                    "day": day_name,
                    "time_spent": hours
                })
            
            return {
                "topic_performance": topic_performance,
                "weekly_activity": weekly_activity
            }
            
        except Exception as e:
            print(f"Error getting learning analytics: {e}")
            return {
                "topic_performance": [],
                "weekly_activity": [
                    {"day": "Mon", "time_spent": 0},
                    {"day": "Tue", "time_spent": 0},
                    {"day": "Wed", "time_spent": 0},
                    {"day": "Thu", "time_spent": 0},
                    {"day": "Fri", "time_spent": 0},
                    {"day": "Sat", "time_spent": 0},
                    {"day": "Sun", "time_spent": 0}
                ]
            }
        finally:
            conn.close()

    def get_learning_analytics(self, user_id: int) -> Dict:
        """Get comprehensive learning analytics for dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get topic performance (completed topics with progress)
            cursor.execute("""
                SELECT topic, study_time_minutes, completed_at
                FROM learning_completed
                WHERE user_id = ?
                ORDER BY completed_at DESC
                LIMIT 10
            """, (user_id,))

            completed_topics = cursor.fetchall()
            topic_performance = []

            for row in completed_topics:
                topic_performance.append({
                    "topic": row['topic'],
                    "completion": 100,  # Completed topics are 100%
                    "study_time": row['study_time_minutes']
                })

            # Get weekly activity (last 7 days)
            from datetime import datetime, timedelta
            weekly_activity = []
            today = datetime.now()

            for i in range(6, -1, -1):  # Last 7 days
                day_date = today - timedelta(days=i)
                day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                # Get study time for this day
                cursor.execute("""
                    SELECT SUM(study_time_minutes) as total
                    FROM learning_completed
                    WHERE user_id = ?
                    AND completed_at >= ?
                    AND completed_at <= ?
                """, (user_id, day_start.strftime('%Y-%m-%d %H:%M:%S'), day_end.strftime('%Y-%m-%d %H:%M:%S')))

                result = cursor.fetchone()
                minutes = result['total'] if result and result['total'] else 0
                hours = minutes / 60.0

                # Day name (Mon, Tue, etc.)
                day_name = day_date.strftime('%a')

                weekly_activity.append({
                    "day": day_name,
                    "time_spent": hours
                })

            return {
                "topic_performance": topic_performance,
                "weekly_activity": weekly_activity
            }

        except Exception as e:
            print(f"Error getting learning analytics: {e}")
            return {
                "topic_performance": [],
                "weekly_activity": [
                    {"day": "Mon", "time_spent": 0},
                    {"day": "Tue", "time_spent": 0},
                    {"day": "Wed", "time_spent": 0},
                    {"day": "Thu", "time_spent": 0},
                    {"day": "Fri", "time_spent": 0},
                    {"day": "Sat", "time_spent": 0},
                    {"day": "Sun", "time_spent": 0}
                ]
            }
        finally:
            conn.close()



# Global instance
_learning_db = None

def get_learning_db() -> LearningProgressDB:
    """Get global learning database instance"""
    global _learning_db
    if _learning_db is None:
        _learning_db = LearningProgressDB()
    return _learning_db


    # Additional methods for new features
    
    def get_completed_topics_list_simple(self, user_id: int) -> List[str]:
        """Get simple list of completed topic names"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT topic FROM learning_completed
                WHERE user_id = ?
                ORDER BY completed_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            return [row['topic'] for row in results]
        except Exception as e:
            print(f"Error getting completed topics: {e}")
            return []
        finally:
            conn.close()
    
    def get_recent_quiz_scores(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent quiz scores for AI mentor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT topic, score, total_questions as max_score, percentage, attempted_at
                FROM quiz_results
                WHERE user_id = ?
                ORDER BY attempted_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            
            return [
                {
                    "topic": row['topic'],
                    "score": row['score'],
                    "max_score": row['max_score'],
                    "percentage": row['percentage'],
                    "attempted_at": row['attempted_at']
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting recent quiz scores: {e}")
            return []
        finally:
            conn.close()
    
    def get_average_quiz_score(self, user_id: int) -> float:
        """Get average quiz score percentage"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT AVG(percentage) as avg_score
                FROM quiz_results
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            return result['avg_score'] if result and result['avg_score'] else 0
        except Exception as e:
            print(f"Error getting average quiz score: {e}")
            return 0
        finally:
            conn.close()
    
    def get_quiz_count(self, user_id: int) -> int:
        """Get total number of quizzes taken"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM quiz_results
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting quiz count: {e}")
            return 0
        finally:
            conn.close()
    
    def get_all_quiz_scores(self, user_id: int) -> List[Dict]:
        """Get all quiz scores for weak topic analysis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT topic, score, total_questions as max_score, percentage, attempted_at
                FROM quiz_results
                WHERE user_id = ?
                ORDER BY attempted_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            
            return [
                {
                    "topic": row['topic'],
                    "score": row['score'],
                    "max_score": row['max_score'],
                    "percentage": row['percentage'],
                    "attempted_at": row['attempted_at']
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting all quiz scores: {e}")
            return []
        finally:
            conn.close()
    
    def get_topic_quiz_history(self, user_id: int, topic: str) -> List[Dict]:
        """Get quiz history for a specific topic"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT score, total_questions as max_score, percentage, attempted_at
                FROM quiz_results
                WHERE user_id = ? AND topic = ?
                ORDER BY attempted_at ASC
            """, (user_id, topic))
            
            results = cursor.fetchall()
            
            return [
                {
                    "score": row['score'],
                    "max_score": row['max_score'],
                    "percentage": row['percentage'],
                    "attempted_at": row['attempted_at']
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting topic quiz history: {e}")
            return []
        finally:
            conn.close()
