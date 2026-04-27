"""
Interview Preparation System
AI-generated technical interview questions with practice mode
"""
import streamlit as st
from groq import Groq
import json
import sqlite3
from pathlib import Path
from datetime import datetime


class InterviewPrepSystem:
    """Manage interview questions and practice sessions"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "interview_prep.db"
        self._init_database()
        
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except KeyError:
            self.client = None
    
    def _init_database(self):
        """Initialize interview prep database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                question_type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                hints TEXT,
                follow_ups TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS practice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                questions_count INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                duration_minutes INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                session_id INTEGER,
                user_answer TEXT,
                is_correct BOOLEAN DEFAULT 0,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES interview_questions(id),
                FOREIGN KEY (session_id) REFERENCES practice_sessions(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_questions(self, topic: str, difficulty: str, count: int = 5):
        """Generate interview questions using AI"""
        if not self.client:
            return None
        
        try:
            prompt = f"""Generate {count} technical interview questions for: {topic}
Difficulty: {difficulty}

Return ONLY valid JSON array:
[
  {{
    "question_type": "Concept/Coding/System Design/Behavioral",
    "question": "Interview question text",
    "answer": "Detailed answer with explanation",
    "hints": ["Hint 1", "Hint 2"],
    "follow_ups": ["Follow-up question 1", "Follow-up question 2"]
  }}
]

Requirements:
- Mix of question types
- Clear, realistic interview questions
- Comprehensive answers
- 2-3 hints per question
- 2 follow-up questions
- Return ONLY JSON array, no markdown"""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a technical interview expert. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean markdown if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            questions = json.loads(content)
            return questions
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return None
    
    def save_questions(self, topic: str, difficulty: str, questions: list) -> list:
        """Save questions to database and return IDs"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        question_ids = []
        
        try:
            for q in questions:
                cursor.execute("""
                    INSERT INTO interview_questions 
                    (topic, question_type, difficulty, question, answer, hints, follow_ups)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    topic,
                    q.get('question_type', 'Concept'),
                    difficulty,
                    q['question'],
                    q['answer'],
                    json.dumps(q.get('hints', [])),
                    json.dumps(q.get('follow_ups', []))
                ))
                
                question_ids.append(cursor.lastrowid)
            
            conn.commit()
            return question_ids
            
        except Exception as e:
            print(f"Error saving questions: {e}")
            return []
        finally:
            conn.close()
    
    def get_question(self, question_id: int) -> dict:
        """Get question by ID"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, topic, question_type, difficulty, question, answer, hints, follow_ups
                FROM interview_questions
                WHERE id = ?
            """, (question_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'topic': row[1],
                    'question_type': row[2],
                    'difficulty': row[3],
                    'question': row[4],
                    'answer': row[5],
                    'hints': json.loads(row[6]),
                    'follow_ups': json.loads(row[7])
                }
            return None
            
        except Exception as e:
            print(f"Error getting question: {e}")
            return None
        finally:
            conn.close()
    
    def start_practice_session(self, user_id: int, topic: str, questions_count: int) -> int:
        """Start a new practice session"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO practice_sessions (user_id, topic, questions_count)
                VALUES (?, ?, ?)
            """, (user_id, topic, questions_count))
            
            session_id = cursor.lastrowid
            conn.commit()
            return session_id
            
        except Exception as e:
            print(f"Error starting session: {e}")
            return None
        finally:
            conn.close()
    
    def complete_practice_session(self, session_id: int, correct_answers: int, duration_minutes: int):
        """Complete a practice session"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE practice_sessions
                SET correct_answers = ?,
                    duration_minutes = ?,
                    completed_at = ?
                WHERE id = ?
            """, (correct_answers, duration_minutes, datetime.now(), session_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error completing session: {e}")
            return False
        finally:
            conn.close()
    
    def save_user_answer(self, user_id: int, question_id: int, user_answer: str, 
                        is_correct: bool, session_id: int = None):
        """Save user's answer"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_answers (user_id, question_id, session_id, user_answer, is_correct)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, question_id, session_id, user_answer, 1 if is_correct else 0))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error saving answer: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> dict:
        """Get user interview prep statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Total sessions
            cursor.execute("""
                SELECT COUNT(*) FROM practice_sessions
                WHERE user_id = ? AND completed_at IS NOT NULL
            """, (user_id,))
            total_sessions = cursor.fetchone()[0]
            
            # Total questions answered
            cursor.execute("""
                SELECT COUNT(*) FROM user_answers
                WHERE user_id = ?
            """, (user_id,))
            total_answered = cursor.fetchone()[0]
            
            # Correct answers
            cursor.execute("""
                SELECT COUNT(*) FROM user_answers
                WHERE user_id = ? AND is_correct = 1
            """, (user_id,))
            correct_answers = cursor.fetchone()[0]
            
            # Average score
            accuracy = (correct_answers / total_answered * 100) if total_answered > 0 else 0
            
            # Total study time
            cursor.execute("""
                SELECT SUM(duration_minutes) FROM practice_sessions
                WHERE user_id = ? AND completed_at IS NOT NULL
            """, (user_id,))
            total_time = cursor.fetchone()[0] or 0
            
            return {
                'total_sessions': total_sessions,
                'total_answered': total_answered,
                'correct_answers': correct_answers,
                'accuracy': accuracy,
                'total_time_minutes': total_time
            }
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {
                'total_sessions': 0,
                'total_answered': 0,
                'correct_answers': 0,
                'accuracy': 0,
                'total_time_minutes': 0
            }
        finally:
            conn.close()
    
    def get_recent_sessions(self, user_id: int, limit: int = 5):
        """Get recent practice sessions"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT topic, questions_count, correct_answers, duration_minutes, completed_at
                FROM practice_sessions
                WHERE user_id = ? AND completed_at IS NOT NULL
                ORDER BY completed_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'topic': row[0],
                    'questions_count': row[1],
                    'correct_answers': row[2],
                    'duration_minutes': row[3],
                    'completed_at': row[4]
                })
            
            return sessions
            
        except Exception as e:
            print(f"Error getting recent sessions: {e}")
            return []
        finally:
            conn.close()
    
    def get_questions_by_topic(self, topic: str, limit: int = 10):
        """Get questions by topic"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, question_type, difficulty, question
                FROM interview_questions
                WHERE topic = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (topic, limit))
            
            questions = []
            for row in cursor.fetchall():
                questions.append({
                    'id': row[0],
                    'question_type': row[1],
                    'difficulty': row[2],
                    'question': row[3]
                })
            
            return questions
            
        except Exception as e:
            print(f"Error getting questions: {e}")
            return []
        finally:
            conn.close()


def get_interview_system():
    """Get interview prep system instance"""
    return InterviewPrepSystem()
