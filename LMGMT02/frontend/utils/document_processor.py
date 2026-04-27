"""
Document Processor
Extract text from PDF/DOCX/TXT and generate learning content using AI
"""
import streamlit as st
from groq import Groq
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import io


class DocumentProcessor:
    """Process uploaded documents and generate learning content"""

    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "documents.db"
        self._init_database()
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception:
            self.client = None

    def _init_database(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                content_preview TEXT,
                summary TEXT,
                notes TEXT,
                quiz_data TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def extract_text(self, uploaded_file) -> str:
        """Extract text from uploaded file"""
        filename = uploaded_file.name.lower()
        content = uploaded_file.read()

        if filename.endswith('.txt'):
            return content.decode('utf-8', errors='ignore')

        elif filename.endswith('.pdf'):
            return self._extract_pdf(content)

        elif filename.endswith('.docx'):
            return self._extract_docx(content)

        return ""

    def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except ImportError:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
            except ImportError:
                return "[PDF extraction requires pypdf: pip install pypdf]"
        except Exception as e:
            return f"[PDF extraction error: {e}]"

    def _extract_docx(self, content: bytes) -> str:
        """Extract text from DOCX bytes"""
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        except ImportError:
            return "[DOCX extraction requires python-docx: pip install python-docx]"
        except Exception as e:
            return f"[DOCX extraction error: {e}]"

    def generate_summary(self, text: str) -> str:
        """Generate a concise summary of the document"""
        if not self.client:
            return "AI client not configured. Please add GROQ_API_KEY."

        # Truncate to avoid token limits
        truncated = text[:8000] if len(text) > 8000 else text

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing educational content. Be concise and clear."},
                    {"role": "user", "content": f"Summarize this document in 3-5 paragraphs, highlighting the key concepts and main takeaways:\n\n{truncated}"}
                ],
                temperature=0.5,
                max_tokens=1000,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Summary generation failed: {e}"

    def generate_notes(self, text: str) -> str:
        """Generate structured study notes"""
        if not self.client:
            return "AI client not configured."

        truncated = text[:8000] if len(text) > 8000 else text

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert note-taker. Create well-structured study notes."},
                    {"role": "user", "content": f"""Create detailed study notes from this document. Format as:
## Key Concepts
- Concept 1: explanation
- Concept 2: explanation

## Important Definitions
- Term: definition

## Key Takeaways
1. Takeaway 1
2. Takeaway 2

## Summary
Brief summary

Document:
{truncated}"""}
                ],
                temperature=0.5,
                max_tokens=1500,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Notes generation failed: {e}"

    def generate_quiz(self, text: str, num_questions: int = 5) -> list:
        """Generate quiz questions from document content"""
        if not self.client:
            return []

        truncated = text[:6000] if len(text) > 6000 else text

        try:
            prompt = f"""Generate {num_questions} multiple choice quiz questions based on this document.

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Why this is correct"
    }}
  ]
}}

Document:
{truncated}

Return ONLY JSON."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Generate quiz questions. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
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

    def save_document(self, user_id: int, filename: str, file_type: str,
                      content_preview: str, summary: str, notes: str, quiz_data: list) -> int:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO documents (user_id, filename, file_type, content_preview, summary, notes, quiz_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, filename, file_type, content_preview[:500], summary, notes, json.dumps(quiz_data)))
            doc_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return doc_id
        except Exception as e:
            print(f"Error saving document: {e}")
            return None

    def get_user_documents(self, user_id: int) -> list:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, file_type, content_preview, processed_at
                FROM documents WHERE user_id = ?
                ORDER BY processed_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
            conn.close()
            return [{"id": r[0], "filename": r[1], "type": r[2], "preview": r[3], "date": r[4]} for r in rows]
        except Exception:
            return []


_processor_instance = None

def get_document_processor():
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = DocumentProcessor()
    return _processor_instance
