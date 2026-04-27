"""
Daily Challenges System
Generate and track daily coding/quiz/concept challenges
"""
import streamlit as st
from groq import Groq
import json
import sqlite3
from pathlib import Path
from datetime import datetime, date


class DailyChallengeSystem:
    """Manage daily challenges for user engagement"""

    CHALLENGE_TYPES = ["coding", "quiz", "concept"]

    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "daily_challenges.db"
        self._init_database()
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception:
            self.client = None

    def _init_database(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_date TEXT NOT NULL UNIQUE,
                challenge_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                challenge_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                challenge_id INTEGER NOT NULL,
                challenge_date TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                user_answer TEXT,
                score INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                UNIQUE(user_id, challenge_date),
                FOREIGN KEY (challenge_id) REFERENCES daily_challenges(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_streaks (
                user_id INTEGER PRIMARY KEY,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_completed_date TEXT,
                total_completed INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def get_today_challenge(self) -> dict:
        """Get or generate today's challenge"""
        today = date.today().isoformat()

        # Check if today's challenge exists
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_challenges WHERE challenge_date = ?", (today,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "date": row[1],
                "type": row[2],
                "title": row[3],
                "description": row[4],
                "data": json.loads(row[5])
            }

        # Generate new challenge
        return self._generate_and_save_challenge(today)

    def _generate_and_save_challenge(self, challenge_date: str) -> dict:
        """Generate a new daily challenge"""
        # Rotate challenge types based on day of week
        day_num = date.today().weekday()
        challenge_type = self.CHALLENGE_TYPES[day_num % len(self.CHALLENGE_TYPES)]

        if self.client:
            challenge = self._generate_ai_challenge(challenge_type)
        else:
            challenge = self._get_fallback_challenge(challenge_type)

        # Save to DB
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO daily_challenges
                (challenge_date, challenge_type, title, description, challenge_data)
                VALUES (?, ?, ?, ?, ?)
            """, (
                challenge_date,
                challenge_type,
                challenge['title'],
                challenge['description'],
                json.dumps(challenge.get('data', {}))
            ))
            challenge_id = cursor.lastrowid
            conn.commit()
            conn.close()
            challenge['id'] = challenge_id
            challenge['date'] = challenge_date
            challenge['type'] = challenge_type
        except Exception as e:
            print(f"Error saving challenge: {e}")

        return challenge

    def _generate_ai_challenge(self, challenge_type: str) -> dict:
        """Generate challenge using AI"""
        try:
            if challenge_type == "coding":
                prompt = """Generate a daily coding challenge. Return ONLY valid JSON:
{
  "title": "Challenge title",
  "description": "Problem description with example",
  "data": {
    "starter_code": "def solution():\\n    pass",
    "example_input": "example",
    "example_output": "result",
    "hints": ["Hint 1", "Hint 2"],
    "solution": "def solution():\\n    return 'answer'"
  }
}"""
            elif challenge_type == "quiz":
                prompt = """Generate a daily quiz question about programming/CS. Return ONLY valid JSON:
{
  "title": "Daily Quiz Challenge",
  "description": "Test your knowledge!",
  "data": {
    "question": "Question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Why this is correct"
  }
}"""
            else:  # concept
                prompt = """Generate a daily concept challenge (explain a concept). Return ONLY valid JSON:
{
  "title": "Concept of the Day",
  "description": "Brief intro to the concept",
  "data": {
    "concept": "Concept name",
    "explanation": "Detailed explanation",
    "example": "Code or real-world example",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "question": "Reflection question for the user"
  }
}"""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Generate educational challenges. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000,
                timeout=20
            )

            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            return json.loads(content)

        except Exception as e:
            print(f"AI challenge generation error: {e}")
            return self._get_fallback_challenge(challenge_type)

    def _get_fallback_challenge(self, challenge_type: str) -> dict:
        fallbacks = {
            "coding": {
                "title": "Palindrome Checker",
                "description": "Write a function that checks if a string is a palindrome.",
                "data": {
                    "starter_code": "def is_palindrome(s: str) -> bool:\n    # Your code here\n    pass",
                    "example_input": '"madam"',
                    "example_output": "True",
                    "hints": ["Try reversing the string", "Compare with original"],
                    "solution": "def is_palindrome(s):\n    return s == s[::-1]"
                }
            },
            "quiz": {
                "title": "Daily Quiz Challenge",
                "description": "Test your knowledge!",
                "data": {
                    "question": "What is the time complexity of binary search?",
                    "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
                    "correct_answer": "O(log n)",
                    "explanation": "Binary search halves the search space each iteration, giving O(log n) complexity."
                }
            },
            "concept": {
                "title": "Concept: Big O Notation",
                "description": "Understanding algorithm complexity",
                "data": {
                    "concept": "Big O Notation",
                    "explanation": "Big O notation describes the upper bound of an algorithm's time or space complexity as input size grows.",
                    "example": "O(1) = constant, O(n) = linear, O(n²) = quadratic",
                    "key_points": ["Describes worst-case performance", "Ignores constants", "Helps compare algorithms"],
                    "question": "Can you think of a real-world example where O(n²) would be too slow?"
                }
            }
        }
        return fallbacks.get(challenge_type, fallbacks["concept"])

    def mark_completed(self, user_id: int, challenge_id: int, user_answer: str = "", score: int = 100):
        """Mark a challenge as completed"""
        today = date.today().isoformat()
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Save completion
            cursor.execute("""
                INSERT OR REPLACE INTO user_completions
                (user_id, challenge_id, challenge_date, completed, user_answer, score, completed_at)
                VALUES (?, ?, ?, 1, ?, ?, ?)
            """, (user_id, challenge_id, today, user_answer, score, datetime.now()))

            # Update streak
            cursor.execute("SELECT current_streak, longest_streak, last_completed_date FROM daily_streaks WHERE user_id = ?", (user_id,))
            streak_row = cursor.fetchone()

            if streak_row:
                current, longest, last_date = streak_row
                from datetime import timedelta
                yesterday = (date.today() - timedelta(days=1)).isoformat()

                if last_date == yesterday:
                    current += 1
                elif last_date == today:
                    pass  # Already completed today
                else:
                    current = 1

                longest = max(longest, current)
                cursor.execute("""
                    UPDATE daily_streaks SET current_streak=?, longest_streak=?, last_completed_date=?, total_completed=total_completed+1
                    WHERE user_id=?
                """, (current, longest, today, user_id))
            else:
                cursor.execute("""
                    INSERT INTO daily_streaks (user_id, current_streak, longest_streak, last_completed_date, total_completed)
                    VALUES (?, 1, 1, ?, 1)
                """, (user_id, today))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error marking complete: {e}")

    def is_completed_today(self, user_id: int) -> bool:
        """Check if user completed today's challenge"""
        today = date.today().isoformat()
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT completed FROM user_completions
                WHERE user_id = ? AND challenge_date = ? AND completed = 1
            """, (user_id, today))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception:
            return False

    def get_streak_info(self, user_id: int) -> dict:
        """Get user's streak information"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT current_streak, longest_streak, total_completed FROM daily_streaks WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {"current": row[0], "longest": row[1], "total": row[2]}
            return {"current": 0, "longest": 0, "total": 0}
        except Exception:
            return {"current": 0, "longest": 0, "total": 0}

    def get_completion_history(self, user_id: int, limit: int = 30) -> list:
        """Get user's completion history"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT uc.challenge_date, uc.score, dc.challenge_type, dc.title
                FROM user_completions uc
                JOIN daily_challenges dc ON uc.challenge_id = dc.id
                WHERE uc.user_id = ? AND uc.completed = 1
                ORDER BY uc.challenge_date DESC LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            conn.close()
            return [{"date": r[0], "score": r[1], "type": r[2], "title": r[3]} for r in rows]
        except Exception:
            return []


_daily_system_instance = None

def get_daily_challenge_system():
    global _daily_system_instance
    if _daily_system_instance is None:
        _daily_system_instance = DailyChallengeSystem()
    return _daily_system_instance
