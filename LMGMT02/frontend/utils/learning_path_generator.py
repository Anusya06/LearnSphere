"""
Learning Path Generator
AI-powered personalized learning roadmap generator
"""
import streamlit as st
from groq import Groq
import json
import sqlite3
from pathlib import Path
from datetime import datetime


class LearningPathGenerator:
    """Generate personalized learning paths using AI"""

    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "learning_paths.db"
        self._init_database()
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception:
            self.client = None

    def _init_database(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                goal TEXT NOT NULL,
                skill_level TEXT NOT NULL,
                hours_per_week INTEGER NOT NULL,
                duration_weeks INTEGER NOT NULL,
                path_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS path_progress (
                user_id INTEGER NOT NULL,
                path_id INTEGER NOT NULL,
                week_number INTEGER NOT NULL,
                topic_index INTEGER NOT NULL,
                completed BOOLEAN DEFAULT 0,
                completed_at TIMESTAMP,
                PRIMARY KEY (user_id, path_id, week_number, topic_index),
                FOREIGN KEY (path_id) REFERENCES learning_paths(id)
            )
        """)
        conn.commit()
        conn.close()

    def generate_path(self, goal: str, skill_level: str, hours_per_week: int, duration_weeks: int, user_id: int = None) -> dict:
        """Generate a personalized learning path"""
        if not self.client:
            return self._fallback_path(goal, skill_level, hours_per_week, duration_weeks)

        try:
            prompt = f"""Create a detailed learning roadmap for:
Goal: {goal}
Current Skill Level: {skill_level}
Available Time: {hours_per_week} hours/week
Duration: {duration_weeks} weeks

Return ONLY valid JSON in this exact format:
{{
  "title": "Complete {goal} Roadmap",
  "goal": "{goal}",
  "skill_level": "{skill_level}",
  "total_weeks": {duration_weeks},
  "overview": "Brief overview of this learning path...",
  "weeks": [
    {{
      "week": 1,
      "theme": "Week theme title",
      "topics": ["Topic 1", "Topic 2", "Topic 3"],
      "projects": ["Mini project idea"],
      "resources": ["Resource type: description"],
      "hours_required": {hours_per_week},
      "milestone": "What you'll be able to do after this week"
    }}
  ],
  "final_project": "Capstone project description",
  "career_outcomes": ["Job role 1", "Job role 2"],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"]
}}

Generate exactly {duration_weeks} weeks. Make it practical and progressive.
Return ONLY JSON."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a curriculum designer. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                timeout=45
            )

            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            path_data = json.loads(content)

            # Save to DB
            path_id = None
            if user_id:
                path_id = self._save_path(user_id, goal, skill_level, hours_per_week, duration_weeks, path_data)
                path_data['id'] = path_id

            return path_data

        except Exception as e:
            print(f"Path generation error: {e}")
            return self._fallback_path(goal, skill_level, hours_per_week, duration_weeks)

    def _save_path(self, user_id, goal, skill_level, hours_per_week, duration_weeks, path_data) -> int:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO learning_paths (user_id, goal, skill_level, hours_per_week, duration_weeks, path_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, goal, skill_level, hours_per_week, duration_weeks, json.dumps(path_data)))
            path_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return path_id
        except Exception as e:
            print(f"Error saving path: {e}")
            return None

    def get_user_paths(self, user_id: int) -> list:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, goal, skill_level, duration_weeks, created_at
                FROM learning_paths WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return [{"id": r[0], "goal": r[1], "skill_level": r[2], "weeks": r[3], "created_at": r[4]} for r in rows]
        except Exception:
            return []

    def get_path_by_id(self, path_id: int) -> dict:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT path_data FROM learning_paths WHERE id = ?", (path_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return json.loads(row[0])
            return None
        except Exception:
            return None

    def mark_topic_complete(self, user_id: int, path_id: int, week_number: int, topic_index: int):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO path_progress
                (user_id, path_id, week_number, topic_index, completed, completed_at)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (user_id, path_id, week_number, topic_index, datetime.now()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error marking complete: {e}")

    def get_progress(self, user_id: int, path_id: int) -> dict:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT week_number, topic_index FROM path_progress
                WHERE user_id = ? AND path_id = ? AND completed = 1
            """, (user_id, path_id))
            rows = cursor.fetchall()
            conn.close()
            completed = {(r[0], r[1]) for r in rows}
            return {"completed": completed, "total_completed": len(completed)}
        except Exception:
            return {"completed": set(), "total_completed": 0}

    def _fallback_path(self, goal, skill_level, hours_per_week, duration_weeks) -> dict:
        weeks = []
        topics_pool = [
            ("Foundations", ["Core concepts", "Basic syntax", "Setup & tools"], "Build your first simple project"),
            ("Core Skills", ["Data structures", "Algorithms", "Best practices"], "Implement a working solution"),
            ("Intermediate", ["Advanced topics", "Design patterns", "Testing"], "Build a complete feature"),
            ("Advanced", ["Optimization", "Architecture", "Real-world patterns"], "Deploy a production-ready app"),
        ]
        for i in range(1, duration_weeks + 1):
            pool_item = topics_pool[min(i - 1, len(topics_pool) - 1)]
            weeks.append({
                "week": i,
                "theme": f"Week {i}: {pool_item[0]}",
                "topics": pool_item[1],
                "projects": [f"Week {i} mini project"],
                "resources": ["Documentation", "Practice exercises"],
                "hours_required": hours_per_week,
                "milestone": pool_item[2]
            })
        return {
            "title": f"{goal} Learning Path",
            "goal": goal,
            "skill_level": skill_level,
            "total_weeks": duration_weeks,
            "overview": f"A structured {duration_weeks}-week path to achieve: {goal}",
            "weeks": weeks,
            "final_project": f"Build a complete {goal} project",
            "career_outcomes": ["Junior Developer", "Mid-level Engineer"],
            "prerequisites": ["Basic programming knowledge"]
        }


_generator_instance = None

def get_path_generator():
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = LearningPathGenerator()
    return _generator_instance
