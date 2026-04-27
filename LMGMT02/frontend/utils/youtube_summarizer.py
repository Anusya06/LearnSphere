"""
YouTube Video Summarizer
Extract transcripts and generate learning content from YouTube videos
"""
import streamlit as st
from groq import Groq
import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime


class YouTubeSummarizer:
    """Summarize YouTube videos and generate learning content"""

    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "youtube_summaries.db"
        self._init_database()
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception:
            self.client = None

    def _init_database(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                video_url TEXT NOT NULL,
                video_id TEXT,
                title TEXT,
                transcript_preview TEXT,
                summary TEXT,
                key_points TEXT,
                notes TEXT,
                quiz_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_transcript(self, video_id: str) -> tuple:
        """Get transcript from YouTube video"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([item['text'] for item in transcript_list])
            return full_text, None
        except ImportError:
            return None, "youtube-transcript-api not installed. Run: pip install youtube-transcript-api"
        except Exception as e:
            error_msg = str(e)
            if "No transcript" in error_msg or "disabled" in error_msg.lower():
                return None, "This video doesn't have transcripts available (disabled by creator)."
            return None, f"Could not fetch transcript: {error_msg}"

    def generate_summary(self, transcript: str, video_url: str = "") -> str:
        """Generate video summary from transcript"""
        if not self.client:
            return "AI client not configured."

        truncated = transcript[:8000] if len(transcript) > 8000 else transcript

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing educational video content."},
                    {"role": "user", "content": f"Summarize this YouTube video transcript in 3-4 paragraphs. Focus on the main concepts, key insights, and practical takeaways:\n\n{truncated}"}
                ],
                temperature=0.5,
                max_tokens=800,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Summary generation failed: {e}"

    def generate_key_points(self, transcript: str) -> list:
        """Extract key points from transcript"""
        if not self.client:
            return []

        truncated = transcript[:6000] if len(transcript) > 6000 else transcript

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Extract key learning points. Return ONLY a JSON array."},
                    {"role": "user", "content": f"""Extract 5-8 key learning points from this transcript.
Return ONLY a JSON array like: ["Point 1", "Point 2", "Point 3"]

Transcript:
{truncated}"""}
                ],
                temperature=0.5,
                max_tokens=500,
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
            print(f"Key points error: {e}")
            return ["Could not extract key points"]

    def generate_notes(self, transcript: str) -> str:
        """Generate structured notes from transcript"""
        if not self.client:
            return "AI client not configured."

        truncated = transcript[:7000] if len(transcript) > 7000 else transcript

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Create structured study notes from video transcripts."},
                    {"role": "user", "content": f"""Create detailed study notes from this video transcript. Include:
## Main Topic
## Key Concepts
## Important Details
## Examples Mentioned
## Action Items / Next Steps

Transcript:
{truncated}"""}
                ],
                temperature=0.5,
                max_tokens=1200,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Notes generation failed: {e}"

    def generate_quiz(self, transcript: str, num_questions: int = 5) -> list:
        """Generate quiz from video content"""
        if not self.client:
            return []

        truncated = transcript[:6000] if len(transcript) > 6000 else transcript

        try:
            prompt = f"""Generate {num_questions} quiz questions from this video transcript.

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "Question?",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "explanation": "Why A is correct"
    }}
  ]
}}

Transcript:
{truncated}"""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Generate quiz questions. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                timeout=30
            )

            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            data = json.loads(content)
            return data.get("questions", [])
        except Exception as e:
            print(f"Quiz generation error: {e}")
            return []

    def save_summary(self, user_id: int, video_url: str, video_id: str,
                     transcript: str, summary: str, key_points: list,
                     notes: str, quiz_data: list) -> int:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO video_summaries
                (user_id, video_url, video_id, transcript_preview, summary, key_points, notes, quiz_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, video_url, video_id,
                transcript[:500] if transcript else "",
                summary,
                json.dumps(key_points),
                notes,
                json.dumps(quiz_data)
            ))
            vid_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return vid_id
        except Exception as e:
            print(f"Error saving summary: {e}")
            return None

    def get_user_summaries(self, user_id: int) -> list:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, video_url, video_id, transcript_preview, created_at
                FROM video_summaries WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return [{"id": r[0], "url": r[1], "video_id": r[2], "preview": r[3], "date": r[4]} for r in rows]
        except Exception:
            return []


_summarizer_instance = None

def get_youtube_summarizer():
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = YouTubeSummarizer()
    return _summarizer_instance
