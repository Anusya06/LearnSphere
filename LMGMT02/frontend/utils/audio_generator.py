"""
Advanced Audio Generation System for LearnSphere
Optimized for speed with chunking, caching, and parallel processing
"""
import streamlit as st
from io import BytesIO
import hashlib
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


class AudioGenerator:
    """Optimized audio generation with chunking and caching"""
    
    def __init__(self, db_path: str = "frontend_users.db"):
        self.db_path = db_path
        self.chunk_size = 700  # Optimal chunk size for fast generation
        self.init_database()
    
    def init_database(self):
        """Create audio cache table"""
        import sqlite3
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        # Audio cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                audio_data BLOB NOT NULL,
                voice_type TEXT DEFAULT 'default',
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Audio history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                audio_hash TEXT NOT NULL,
                listened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Audio sections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                section_name TEXT NOT NULL,
                section_content TEXT NOT NULL,
                audio_data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_content_hash(self, text: str, voice: str = 'default', lang: str = 'en') -> str:
        """Generate unique hash for content"""
        content = f"{text}_{voice}_{lang}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_audio(self, content_hash: str) -> BytesIO:
        """Retrieve cached audio"""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT audio_data FROM audio_cache
                WHERE content_hash = ?
            """, (content_hash,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                audio_buffer = BytesIO(result[0])
                audio_buffer.seek(0)
                return audio_buffer
            
            return None
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            return None
    
    def save_to_cache(self, content_hash: str, audio_data: bytes, voice: str = 'default', lang: str = 'en'):
        """Save audio to cache"""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO audio_cache (content_hash, audio_data, voice_type, language)
                VALUES (?, ?, ?, ?)
            """, (content_hash, audio_data, voice, lang))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Cache save error: {e}")
    
    def split_text_into_chunks(self, text: str) -> list:
        """Split text into optimal chunks for fast generation"""
        # Clean text
        text = text.replace("#", "").replace("*", "").replace("`", "")
        
        # Split by sentences
        sentences = text.replace("!", ".").replace("?", ".").split(".")
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence exceeds chunk size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def generate_chunk_audio(self, chunk: str, lang: str = 'en') -> BytesIO:
        """Generate audio for a single chunk"""
        if not GTTS_AVAILABLE:
            return None
        
        try:
            tts = gTTS(text=chunk, lang=lang, slow=False)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            print(f"Chunk generation error: {e}")
            return None
    
    def merge_audio_chunks(self, audio_chunks: list) -> BytesIO:
        """Merge multiple audio chunks into one"""
        try:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            
            for chunk_audio in audio_chunks:
                if chunk_audio:
                    chunk_audio.seek(0)
                    audio_segment = AudioSegment.from_mp3(chunk_audio)
                    combined += audio_segment
            
            output = BytesIO()
            combined.export(output, format="mp3")
            output.seek(0)
            return output
        except ImportError:
            # If pydub not available, return first chunk
            if audio_chunks:
                audio_chunks[0].seek(0)
                return audio_chunks[0]
            return None
        except Exception as e:
            print(f"Merge error: {e}")
            return None
    
    def generate_audio_parallel(self, text: str, lang: str = 'en', voice: str = 'default') -> BytesIO:
        """Generate audio with parallel processing for speed"""
        
        # Check cache first
        content_hash = self.generate_content_hash(text, voice, lang)
        cached_audio = self.get_cached_audio(content_hash)
        
        if cached_audio:
            return cached_audio
        
        # Split into chunks
        chunks = self.split_text_into_chunks(text)
        
        if not chunks:
            return None
        
        # For small text, generate directly
        if len(chunks) == 1:
            audio = self.generate_chunk_audio(chunks[0], lang)
            if audio:
                audio.seek(0)
                audio_bytes = audio.read()
                self.save_to_cache(content_hash, audio_bytes, voice, lang)
                audio.seek(0)
            return audio
        
        # Parallel generation for multiple chunks
        audio_chunks = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_chunk = {
                executor.submit(self.generate_chunk_audio, chunk, lang): i 
                for i, chunk in enumerate(chunks)
            }
            
            # Collect results in order
            results = [None] * len(chunks)
            for future in as_completed(future_to_chunk):
                idx = future_to_chunk[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    print(f"Chunk {idx} error: {e}")
        
        # Merge chunks
        merged_audio = self.merge_audio_chunks(results)
        
        if merged_audio:
            merged_audio.seek(0)
            audio_bytes = merged_audio.read()
            self.save_to_cache(content_hash, audio_bytes, voice, lang)
            merged_audio.seek(0)
        
        return merged_audio
    
    def generate_audio_fast(self, text: str, lang: str = 'en') -> BytesIO:
        """Fast mode - lower quality, faster generation"""
        # Limit text size for fast mode
        if len(text) > 3000:
            text = text[:3000] + "..."
        
        return self.generate_audio_parallel(text, lang)
    
    def generate_summary_audio(self, text: str, lang: str = 'en') -> BytesIO:
        """Generate audio for summary (shorter)"""
        # Take first 1000 characters as summary
        summary_text = text[:1000] if len(text) > 1000 else text
        return self.generate_audio_parallel(summary_text, lang)
    
    def save_audio_history(self, user_id: int, topic: str, audio_hash: str):
        """Save audio listening history"""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audio_history (user_id, topic, audio_hash)
                VALUES (?, ?, ?)
            """, (user_id, topic, audio_hash))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"History save error: {e}")
    
    def get_audio_history(self, user_id: int, limit: int = 10) -> list:
        """Get user's audio history"""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT topic, listened_at
                FROM audio_history
                WHERE user_id = ?
                ORDER BY listened_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"History retrieval error: {e}")
            return []
    
    def split_into_sections(self, text: str) -> dict:
        """Split content into logical sections"""
        sections = {}
        
        # Try to identify sections by headers
        lines = text.split("\n")
        current_section = "Introduction"
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a header
            if line.startswith("##"):
                # Save previous section
                if current_content:
                    sections[current_section] = " ".join(current_content)
                
                # Start new section
                current_section = line.replace("##", "").strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = " ".join(current_content)
        
        # If no sections found, create default sections
        if not sections:
            text_length = len(text)
            chunk_size = text_length // 3
            
            sections = {
                "Introduction": text[:chunk_size],
                "Main Content": text[chunk_size:chunk_size*2],
                "Summary": text[chunk_size*2:]
            }
        
        return sections
    
    def generate_section_audio(self, section_name: str, section_content: str, lang: str = 'en') -> BytesIO:
        """Generate audio for a specific section"""
        return self.generate_audio_parallel(section_content, lang)
    
    def generate_podcast_audio(self, topic: str, content: str, lang: str = 'en') -> BytesIO:
        """Generate podcast-style audio with host and expert"""
        # Create podcast script
        podcast_script = f"""
        Host: Welcome to LearnSphere Audio Learning. Today we're exploring {topic}.
        
        Expert: Thank you for having me. Let me explain the key concepts.
        
        {content[:500]}
        
        Host: That's fascinating! Can you elaborate more?
        
        Expert: Absolutely. {content[500:1000] if len(content) > 500 else ''}
        
        Host: Thank you for this insightful explanation!
        """
        
        return self.generate_audio_parallel(podcast_script, lang)


# Global instance
_audio_generator = None

def get_audio_generator() -> AudioGenerator:
    """Get global audio generator instance"""
    global _audio_generator
    if _audio_generator is None:
        _audio_generator = AudioGenerator()
    return _audio_generator
