"""
Code Complexity Analyzer
AI-powered analysis of time/space complexity and optimization suggestions
"""
import streamlit as st
from groq import Groq
import json
import ast
import sqlite3
from pathlib import Path
from datetime import datetime


class CodeComplexityAnalyzer:
    """Analyze code complexity using AI + AST"""

    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "complexity_analysis.db"
        self._init_database()
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception:
            self.client = None

    def _init_database(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                code TEXT NOT NULL,
                language TEXT NOT NULL,
                time_complexity TEXT,
                space_complexity TEXT,
                efficiency_score INTEGER,
                suggestions TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def analyze(self, code: str, language: str = "Python", user_id: int = None) -> dict:
        """Analyze code complexity using AI"""
        if not self.client:
            return self._fallback_analysis(code, language)

        try:
            # Get AST info for Python
            ast_info = ""
            if language == "Python":
                ast_info = self._get_ast_info(code)

            prompt = f"""Analyze the following {language} code for complexity and quality.

CODE:
```{language.lower()}
{code}
```

{f"AST INFO: {ast_info}" if ast_info else ""}

Return ONLY valid JSON in this exact format:
{{
  "time_complexity": "O(n²)",
  "space_complexity": "O(n)",
  "efficiency_score": 65,
  "complexity_explanation": "The nested loops cause O(n²) time complexity...",
  "space_explanation": "The list stores n elements...",
  "inefficient_parts": [
    {{"line": "for i in range(n): for j in range(n):", "issue": "Nested loops - O(n²)", "suggestion": "Use a hash map instead"}}
  ],
  "optimizations": [
    "Use a dictionary/hash map to reduce lookup time from O(n) to O(1)",
    "Consider sorting the array first to enable binary search"
  ],
  "optimized_code": "def optimized_solution(arr):\\n    seen = {{}}\\n    # optimized version here",
  "overall_assessment": "The code is functional but has performance issues with large inputs."
}}

efficiency_score: 0-100 (100 = perfectly optimized)
Return ONLY JSON, no markdown."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a code analysis expert. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                timeout=30
            )

            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)

            # Save to DB
            if user_id:
                self._save_analysis(user_id, code, language, result)

            return result

        except Exception as e:
            print(f"Complexity analysis error: {e}")
            return self._fallback_analysis(code, language)

    def _get_ast_info(self, code: str) -> str:
        """Extract basic AST info from Python code"""
        try:
            tree = ast.parse(code)
            info = []
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    info.append("for-loop")
                elif isinstance(node, ast.While):
                    info.append("while-loop")
                elif isinstance(node, ast.FunctionDef):
                    info.append(f"function:{node.name}")
                elif isinstance(node, ast.ListComp):
                    info.append("list-comprehension")
                elif isinstance(node, ast.Dict):
                    info.append("dict-usage")
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        info.append(f"method-call:{node.func.attr}")
            return ", ".join(set(info))
        except Exception:
            return ""

    def _save_analysis(self, user_id: int, code: str, language: str, result: dict):
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analyses (user_id, code, language, time_complexity, space_complexity, efficiency_score, suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, code, language,
                result.get('time_complexity', 'Unknown'),
                result.get('space_complexity', 'Unknown'),
                result.get('efficiency_score', 0),
                json.dumps(result.get('optimizations', []))
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving analysis: {e}")

    def get_history(self, user_id: int, limit: int = 10) -> list:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT time_complexity, space_complexity, efficiency_score, language, analyzed_at
                FROM analyses WHERE user_id = ?
                ORDER BY analyzed_at DESC LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            conn.close()
            return [{"time": r[0], "space": r[1], "score": r[2], "language": r[3], "date": r[4]} for r in rows]
        except Exception:
            return []

    def _fallback_analysis(self, code: str, language: str) -> dict:
        return {
            "time_complexity": "O(n)",
            "space_complexity": "O(1)",
            "efficiency_score": 70,
            "complexity_explanation": "Analysis unavailable - AI client not configured.",
            "space_explanation": "Could not determine space complexity.",
            "inefficient_parts": [],
            "optimizations": ["Add your GROQ_API_KEY to enable full analysis"],
            "optimized_code": code,
            "overall_assessment": "Please configure the AI client for detailed analysis."
        }


_analyzer_instance = None

def get_complexity_analyzer():
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = CodeComplexityAnalyzer()
    return _analyzer_instance
