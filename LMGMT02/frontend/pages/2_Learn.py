"""
Advanced Learn Page - Complete AI Learning Hub
Features: AI Content, Audio, Tutor Chat, Videos, Code Examples, Roadmap, Flashcards, Study Notes
"""
import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime
from io import BytesIO
import re
import os
import base64

sys.path.append(str(Path(__file__).parent.parent))

from components.ui_components import gradient_card
from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.learning_progress import get_learning_db
from utils.code_executor import CodeExecutor
from utils.audio_generator import get_audio_generator, GTTS_AVAILABLE
from utils.advanced_features_db import get_advanced_db
from groq import Groq

st.set_page_config(
    page_title="LearnSphere AI - Learn", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"  # Keep sidebar expanded by default
)

# Apply theme and sidebar fix
apply_theme()
load_theme_css()
apply_sidebar_fix()  # Fix sidebar navigation
apply_theme()
load_theme_css()

# ============================================================================
# BACKGROUND IMAGE IMPLEMENTATION - Place at top of Learn page
# ============================================================================

def set_learn_page_background():
    """
    Set custom background image for Learn page only.
    Loads image from assets folder, converts to Base64, and applies CSS.
    """
    # Get the project root directory (2 levels up from this file)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    
    # Try multiple possible image names - prioritize learnsphere_bg.png
    possible_images = [
        "learnsphere_bg.png",  # First priority
        "learn_bg.png",        # Second priority
        "ml image.jpg"         # Third priority
    ]
    
    encoded_image = None
    image_path_found = None
    
    # Try to find and load the image from assets folder
    assets_folder = project_root / "assets"
    
    for image_name in possible_images:
        image_path = assets_folder / image_name
        try:
            if image_path.exists():
                with open(image_path, "rb") as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode()
                    image_path_found = str(image_path)
                    break
        except Exception as e:
            continue
    
    # If no image found, exit gracefully
    if not encoded_image:
        return
    
    # Inject CSS with Base64 encoded background image
    st.markdown(
        f"""
        <style>
        /* Remove default Streamlit background */
        .stApp {{
            background: transparent !important;
        }}
        
        /* Full-screen fixed background image layer */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100vw;
            height: 100vh;
            background-image: url("data:image/png;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            z-index: -2;
            pointer-events: none;
        }}
        
        /* Semi-transparent dark overlay for readability */
        .stApp::after {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(
                135deg,
                rgba(0, 0, 0, 0.80) 0%,
                rgba(14, 17, 23, 0.90) 100%
            );
            z-index: -1;
            pointer-events: none;
        }}
        
        /* Enhanced glass effects for Learn page content */
        .main .block-container {{
            background: rgba(255, 255, 255, 0.02) !important;
            border-radius: 20px;
            padding: 2rem;
        }}
        
        /* Sidebar enhancement */
        [data-testid="stSidebar"] {{
            background: rgba(14, 17, 23, 0.95) !important;
            border-right: 1px solid rgba(102, 126, 234, 0.3);
        }}
        
        /* Text readability enhancement */
        .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, 
        .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
            color: #ffffff !important;
            -webkit-font-smoothing: antialiased !important;
            text-rendering: optimizeLegibility !important;
        }}
        
        /* Enhanced buttons */
        .stButton > button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
            transform: translateY(-2px);
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border-radius: 12px;
            padding: 12px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            color: #ffffff !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: rgba(102, 126, 234, 0.4) !important;
        }}
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {{
            background: rgba(255, 255, 255, 0.10) !important;
            border: 1px solid rgba(102, 126, 234, 0.4) !important;
            color: #ffffff !important;
            border-radius: 10px;
            -webkit-font-smoothing: antialiased !important;
        }}
        
        /* Code blocks */
        .stCodeBlock {{
            background: rgba(0, 0, 0, 0.75) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 10px;
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(10px);
            border-radius: 10px;
            color: #ffffff !important;
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .stApp::before {{
                background-size: cover;
                background-position: center center;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Execute the background function immediately when Learn page loads
set_learn_page_background()

# ============================================================================
# END OF BACKGROUND IMPLEMENTATION
# ============================================================================

# Modern SaaS CSS Styling
st.markdown("""
<style>
    /* Force crisp text rendering on Learn page */
    *, *::before, *::after {
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        text-rendering: optimizeLegibility !important;
    }
    
    /* Professional Hero Header */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff !important;
        margin: 0;
        letter-spacing: -0.5px;
        -webkit-font-smoothing: antialiased !important;
        text-rendering: optimizeLegibility !important;
        /* Force white — override any global color rules */
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.95) !important;
        -webkit-text-fill-color: rgba(255,255,255,0.95) !important;
        margin-top: 0.5rem;
        font-weight: 500;
        opacity: 1 !important;
        -webkit-font-smoothing: antialiased !important;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(15, 18, 30, 0.82);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        margin: 1rem 0;
    }
    
    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.25) 0%, rgba(118, 75, 162, 0.25) 100%);
        border: 1px solid rgba(102, 126, 234, 0.5);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #7c8ff5 !important;
        margin: 0;
        -webkit-font-smoothing: antialiased !important;
        text-rendering: optimizeLegibility !important;
        letter-spacing: -0.5px;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #d0d0d0 !important;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
        -webkit-font-smoothing: antialiased !important;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #fafafa;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    /* Content Card */
    .content-card {
        background: rgba(30, 30, 30, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        line-height: 1.8;
    }
    
    /* Chat Bubbles */
    .chat-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 18px 18px 4px 18px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .chat-ai {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 18px 18px 18px 4px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    /* Flashcard */
    .flashcard {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 2px solid rgba(102, 126, 234, 0.3);
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        transition: transform 0.3s ease;
    }
    
    .flashcard:hover {
        transform: scale(1.02);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 4rem;
        color: #666;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Improved Spacing */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Button Improvements */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        -webkit-font-smoothing: antialiased !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

try:
    api_key = st.secrets["GROQ_API_KEY"]
    groq_client = Groq(api_key=api_key)
except KeyError:
    st.error("⚠️ Groq API key not found")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error: {str(e)}")
    st.stop()


def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "generated_content": None,
        "current_topic": None,
        "current_difficulty": "Intermediate",
        "chat_history": [],
        "roadmap_data": None,
        "audio_file": None,
        "audio_sections": None,
        "code_examples": None,
        "code_topic": "",
        "code_output": None,
        "flashcards": [],
        "flashcard_index": 0,
        "show_answer": False,
        "study_notes": None,
        "mindmap_data": None,
        "study_start_time": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def generate_learning_content(topic: str, difficulty: str) -> str:
    """Generate comprehensive learning content using AI"""
    try:
        prompt = f"""Create comprehensive learning content about: {topic}
Difficulty: {difficulty}

Include these sections:
## Introduction
## Key Concepts
## Detailed Explanation
## Real-World Applications
## Common Mistakes
## Summary"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert AI educator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def clean_roadmap_text(text: str) -> str:
    """Clean roadmap text by removing unwanted prefixes and patterns"""
    if not text:
        return text
    
    # Remove all variations of arr_week, arrWeek, arr_Week, etc.
    patterns_to_remove = [
        r'\.?arr[_\s]?[Ww]eek:?\s*',      # arr_week, arr week, arrweek, arrWeek
        r'\.?[Aa]rr[_\s]?[Ww]eek:?\s*',   # Arr_Week, Arr Week, ArrWeek
        r'\.?week[_\s]?title:?\s*',        # week_title, week title
        r'\.?week[_\s]?tasks:?\s*',        # week_tasks, week tasks
        r'\.?arr[_\s]?title:?\s*',         # arr_title, arr title
        r'\.?arr[_\s]?tasks:?\s*',         # arr_tasks, arr tasks
        r'^[Ww]eek\s+\d+\s*[-:]\s*',      # "Week 1 - " or "Week 1: " at start
        r'^[Ww]eek:?\s*',                  # Week: at start
        r'^\d+\.\s*',                      # "1. " at start
        r'^-\s*',                          # "- " at start
        r'^\*\s*',                         # "* " at start
    ]
    
    # Apply all patterns
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove any remaining dots at the start
    text = text.lstrip('.')
    
    return text.strip()


def generate_roadmap(topic: str, difficulty: str, weeks: int = 6) -> dict:
    """Generate learning roadmap"""
    try:
        prompt = f"""Create a {weeks}-week learning roadmap for: {topic}
Difficulty: {difficulty}

Return ONLY valid JSON in this exact format:
{{
  "weeks": [
    {{
      "week": 1,
      "title": "Introduction to {topic}",
      "tasks": [
        "Task 1 description",
        "Task 2 description",
        "Task 3 description"
      ]
    }}
  ]
}}

Make tasks specific and actionable. Return ONLY the JSON, no other text."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a curriculum designer. Return ONLY valid JSON, no markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        roadmap_data = json.loads(content)
        
        if "weeks" in roadmap_data:
            for week in roadmap_data["weeks"]:
                if "title" in week:
                    week["title"] = clean_roadmap_text(week["title"])
                if "tasks" in week:
                    week["tasks"] = [clean_roadmap_text(task) for task in week["tasks"]]
        
        return roadmap_data
    except Exception as e:
        st.error(f"Error generating roadmap: {str(e)}")
        return None


def generate_code_example(topic: str, language: str) -> dict:
    """Generate code example"""
    try:
        prompt = f"""Generate a practical code example for: {topic}
Programming Language: {language}

Return ONLY valid JSON. Escape all special characters properly.
{{
  "code": "code here",
  "explanation": "explanation here",
  "language": "{language}"
}}

IMPORTANT: Use proper JSON escaping. No control characters."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a coding instructor. Return ONLY valid JSON with properly escaped strings."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
        return json.loads(content)
    except json.JSONDecodeError as je:
        st.error(f"JSON parsing error: {str(je)}")
        return None
    except Exception as e:
        st.error(f"Error generating code: {str(e)}")
        return None


def detect_language_for_topic(topic: str) -> str:
    """Detect best programming language for topic"""
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ["ml", "ai", "neural", "data", "pandas", "numpy"]):
        return "Python"
    elif any(w in topic_lower for w in ["web", "react", "frontend", "dom"]):
        return "JavaScript"
    elif any(w in topic_lower for w in ["android", "spring", "jvm"]):
        return "Java"
    elif any(w in topic_lower for w in ["system", "performance", "memory"]):
        return "C++"
    else:
        return "Python"


def chat_with_tutor(user_message: str, topic: str, content: str) -> str:
    """Chat with AI tutor"""
    try:
        messages = [
            {"role": "system", "content": f"You are an AI tutor helping with: {topic}. Context: {content[:1000]}"},
        ]
        
        for msg in st.session_state.chat_history[-5:]:
            messages.append({"role": "user", "content": msg["user"]})
            messages.append({"role": "assistant", "content": msg["ai"]})
        
        messages.append({"role": "user", "content": user_message})
        
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def generate_flashcards(topic: str) -> list:
    """Generate AI flashcards"""
    try:
        prompt = f"""Generate 10 flashcards for: {topic}
    
Return ONLY a JSON array:
[
  {{"question": "Q1?", "answer": "A1"}},
  {{"question": "Q2?", "answer": "A2"}}
]

No markdown, just JSON."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON array."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        return json.loads(content)
    except Exception as e:
        st.error(f"Error generating flashcards: {str(e)}")
        return []


def generate_study_notes(topic: str, content: str) -> str:
    """Generate concise study notes"""
    try:
        prompt = f"""Summarize this topic into concise study notes: {topic}

Content: {content[:2000]}

Create bullet-point study notes highlighting:
- Key concepts
- Important definitions
- Main takeaways
- Practical applications

Format as markdown with clear sections."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a study notes generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating notes: {str(e)}")
        return None


def render_content_tab():
    """Render main content tab"""
    if st.session_state.generated_content:
        st.markdown('<h3 class="section-header">📘 Lesson Content</h3>', unsafe_allow_html=True)
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.generated_content)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mark as Completed Section
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        if st.session_state.get("user_id") and st.session_state.current_topic:
            db = get_learning_db()
            
            # Check if already completed
            is_completed = db.is_topic_completed(
                st.session_state.user_id,
                st.session_state.current_topic
            )
            
            if is_completed:
                st.success("✅ This topic is already completed!")
                st.caption("Great job! You've mastered this topic.")
            else:
                st.markdown("### 🎯 Complete Your Learning")
                st.caption("Mark this topic as completed to track your progress")
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if st.button("✅ Mark as Completed", use_container_width=True, type="primary"):
                        # Calculate study time
                        study_time_minutes = 0
                        if st.session_state.study_start_time:
                            time_diff = datetime.now() - st.session_state.study_start_time
                            study_time_minutes = max(1, int(time_diff.total_seconds() / 60))
                        
                        # Mark as completed
                        success = db.mark_topic_completed(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            study_time_minutes
                        )
                        
                        if success:
                            # Update streak
                            advanced_db = get_advanced_db()
                            advanced_db.update_streak(st.session_state.user_id)
                            
                            st.success(f"🎉 Congratulations! Topic completed in {study_time_minutes} minutes!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Failed to mark as completed. Please try again.")
                
                with col2:
                    if st.session_state.study_start_time:
                        elapsed = datetime.now() - st.session_state.study_start_time
                        elapsed_minutes = int(elapsed.total_seconds() / 60)
                        st.info(f"⏱️ Study time: {elapsed_minutes} minutes")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👆 Enter a topic above to generate learning content")


def render_audio_tab():
    """Simplified audio generation - Full content only"""
    if not GTTS_AVAILABLE:
        st.warning("⚠️ Install gTTS for audio generation")
        st.code("pip install gtts", language="bash")
        return
    
    if not st.session_state.generated_content:
        st.info("👆 Generate content first to enable audio")
        return
    
    st.markdown('<h3 class="section-header">🔊 Audio Learning</h3>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    st.caption(f"📚 Topic: **{st.session_state.current_topic}**")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Initialize audio generator
    try:
        audio_gen = get_audio_generator()
    except Exception as e:
        st.error(f"Error initializing audio generator: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Language selection
    language_options = [
        ("English", "en"),
        ("Spanish", "es"),
        ("French", "fr"),
        ("German", "de")
    ]
    language = st.selectbox(
        "🌐 Select Language",
        language_options,
        format_func=lambda x: x[0],
        key="audio_lang_select"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate audio button
    if st.button("🔊 Generate Audio", use_container_width=True, type="primary"):
        # Validate content
        if not st.session_state.generated_content:
            st.warning("⚠️ No content available to generate audio.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        with st.spinner("🎵 Generating audio for full content..."):
            import time
            start_time = time.time()
            
            # Clean text but keep full content
            audio_text = st.session_state.generated_content.replace("#", "").replace("*", "").replace("`", "")
            lang_code = language[1]
            
            # Validate text
            if not audio_text or len(audio_text.strip()) == 0:
                st.error("❌ Content is empty. Cannot generate audio.")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            
            try:
                # Generate audio for FULL content (no truncation)
                audio_buffer = audio_gen.generate_audio_parallel(audio_text, lang_code)
                
                generation_time = time.time() - start_time
                
                if audio_buffer:
                    st.session_state.audio_file = audio_buffer
                    st.success(f"✅ Audio generated in {generation_time:.1f} seconds!")
                    st.rerun()
                else:
                    st.error("❌ Failed to generate audio. Please try again.")
            except Exception as e:
                st.error(f"❌ Error generating audio: {str(e)}")
                st.caption("Try regenerating or check your internet connection.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display audio player if audio exists
    if st.session_state.audio_file:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🎧 Audio Player")
        
        st.audio(st.session_state.audio_file, format="audio/mp3")
        st.caption("💡 Use browser controls to play/pause and adjust speed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Download button
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Audio",
                data=st.session_state.audio_file,
                file_name=f"{st.session_state.current_topic.replace(' ', '_')}_audio.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
        
        with col2:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.audio_file = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_tutor_tab():
    """Chat with AI tutor"""
    if not st.session_state.generated_content:
        st.info("👆 Generate content first to enable tutor chat")
        return
    
    st.markdown('<h3 class="section-header">🤖 AI Tutor Chat</h3>', unsafe_allow_html=True)
    st.caption(f"Ask questions about **{st.session_state.current_topic}**")
    st.markdown("<br>", unsafe_allow_html=True)
    
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            st.markdown(f"""
                <div class="chat-user">
                    <strong style="color:white">👤 You</strong><br>
                    <span style="color:white">{msg["user"]}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="chat-ai">
                    <strong style="color:#10b981">🤖 AI Tutor</strong><br>
                    <span style="color:#fafafa">{msg["ai"]}</span>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    user_question = st.chat_input("💬 Ask a question (press Enter to send)...")
    
    if user_question:
        with st.spinner("🤖 AI Tutor is thinking..."):
            ai_response = chat_with_tutor(
                user_question,
                st.session_state.current_topic,
                st.session_state.generated_content
            )
            
            st.session_state.chat_history.append({
                "user": user_question,
                "ai": ai_response,
                "timestamp": datetime.now()
            })
            
            if st.session_state.get("user_id"):
                db = get_learning_db()
                db.save_tutor_message(
                    st.session_state.user_id,
                    st.session_state.current_topic,
                    user_question,
                    ai_response
                )
            
            st.rerun()


def render_videos_tab():
    """Render YouTube video recommendations"""
    if not st.session_state.current_topic:
        st.info("👆 Enter a topic to see video recommendations")
        return
    
    st.markdown("### 🎥 YouTube Learning Resources")
    st.caption("Curated video tutorials and explanations")
    
    topic = st.session_state.current_topic
    categories = [
        ("Tutorial", f"https://www.youtube.com/results?search_query={topic}+tutorial"),
        ("Beginner Guide", f"https://www.youtube.com/results?search_query={topic}+for+beginners"),
        ("Advanced", f"https://www.youtube.com/results?search_query={topic}+advanced"),
        ("Examples", f"https://www.youtube.com/results?search_query={topic}+examples"),
    ]
    
    cols = st.columns(2)
    for i, (cat, url) in enumerate(categories):
        with cols[i % 2]:
            st.markdown(f"""
                <div style="background:#1e1e1e;padding:20px;border-radius:12px;margin:10px 0;border:1px solid #3e3e3e">
                    <h4 style="margin:0 0 10px 0;color:#667eea">🎬 {cat}</h4>
                    <p style="margin:10px 0;color:#b0b0b0;font-size:0.9em">Search YouTube for {topic} {cat.lower()}</p>
                    <a href="{url}" target="_blank" style="
                        display:inline-block;
                        background:#667eea;
                        color:white;
                        padding:10px 20px;
                        border-radius:8px;
                        text-decoration:none;
                        font-weight:600;
                    ">🔗 Watch Videos</a>
                </div>
            """, unsafe_allow_html=True)


def render_code_tab():
    """Render code generation tab"""
    st.markdown("### 💻 Code Generator")
    st.caption("Generate code examples with custom topics")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        code_topic = st.text_input(
            "📝 Enter Topic for Code",
            value=st.session_state.get("code_topic", ""),
            placeholder="e.g., Binary Search, Linked List, REST API",
            key="code_topic_input",
            on_change=lambda: setattr(st.session_state, 'code_topic', st.session_state.code_topic_input)
        )
    
    with col2:
        default_lang = detect_language_for_topic(code_topic) if code_topic else "Python"
        language = st.selectbox(
            "Language",
            ["Python", "JavaScript", "Java", "C++", "Go", "Rust"],
            index=["Python", "JavaScript", "Java", "C++", "Go", "Rust"].index(default_lang) if default_lang in ["Python", "JavaScript", "Java", "C++", "Go", "Rust"] else 0,
            key="code_language"
        )
    
    if st.button("🚀 Generate Code", use_container_width=True, type="primary"):
        if not code_topic:
            st.error("❌ Please enter a topic")
        else:
            with st.spinner("Generating code..."):
                code_data = generate_code_example(code_topic, language)
                
                if code_data:
                    st.session_state.code_examples = code_data
                    st.session_state.code_topic = code_topic
                    st.success("✅ Code generated!")
                    st.rerun()
    
    if st.session_state.code_examples:
        st.markdown("---")
        st.markdown(f"#### 📝 {st.session_state.code_topic}")
        
        code = st.session_state.code_examples.get("code", "")
        explanation = st.session_state.code_examples.get("explanation", "")
        lang = st.session_state.code_examples.get("language", "python").lower()
        
        st.code(code, language=lang)
        
        st.markdown("#### 📖 Explanation")
        st.markdown(explanation)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download Code",
                data=code,
                file_name=f"{st.session_state.code_topic.replace(' ', '_')}.{lang}",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            if lang == "python" and st.button("▶️ Run Code", use_container_width=True):
                with st.spinner("Executing..."):
                    try:
                        executor = CodeExecutor()
                        result = executor.execute_python(code)
                        st.session_state.code_output = result
                        st.rerun()
                    except Exception as e:
                        st.error(f"Execution error: {str(e)}")
        
        if st.session_state.code_output:
            st.markdown("#### 🖥️ Output")
            if st.session_state.code_output.get("success"):
                st.code(st.session_state.code_output.get("output", ""), language="text")
            else:
                st.error(st.session_state.code_output.get("error", "Unknown error"))


def render_roadmap_tab():
    """Render learning roadmap tab"""
    if not st.session_state.current_topic:
        st.info("👆 Enter a topic to generate a learning roadmap")
        return
    
    st.markdown("### 🗺️ Learning Roadmap")
    st.caption(f"Structured path to master {st.session_state.current_topic}")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        weeks = st.number_input("Weeks", min_value=4, max_value=12, value=6, key="roadmap_weeks")
    
    with col1:
        if st.button("🎯 Generate Roadmap", use_container_width=True, type="primary"):
            with st.spinner("Creating your learning path..."):
                roadmap = generate_roadmap(
                    st.session_state.current_topic,
                    st.session_state.current_difficulty,
                    weeks
                )
                
                if roadmap:
                    st.session_state.roadmap_data = roadmap
                    
                    if st.session_state.get("user_id"):
                        db = get_learning_db()
                        db.save_roadmap(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            roadmap
                        )
                        db.save_generated_content(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            st.session_state.generated_content or "",
                            json.dumps(roadmap),
                            st.session_state.current_difficulty
                        )
                        
                        advanced_db = get_advanced_db()
                        advanced_db.update_streak(st.session_state.user_id)
                    
                    st.success("✅ Roadmap generated!")
                    st.rerun()
    
    if not st.session_state.roadmap_data and st.session_state.get("user_id"):
        db = get_learning_db()
        loaded_roadmap = db.load_roadmap(
            st.session_state.user_id,
            st.session_state.current_topic
        )
        if loaded_roadmap:
            # Clean arr_week artifacts from stored data on load
            for week in loaded_roadmap.get("weeks", []):
                def _strip_arr(text):
                    if not text:
                        return text
                    import re as _re
                    text = _re.sub(r'\.?arr[_\s]?[Ww]eek\d*:?\s*', '', text)
                    text = _re.sub(r'^[Ww]eek\s*\d+\s*[-:]\s*', '', text)
                    return ' '.join(text.split()).strip().lstrip('.')
                if "title" in week:
                    week["title"] = _strip_arr(week["title"])
                if "tasks" in week:
                    week["tasks"] = [_strip_arr(t) for t in week["tasks"]]
            st.session_state.roadmap_data = loaded_roadmap
    
    if st.session_state.roadmap_data:
        weeks_data = st.session_state.roadmap_data.get("weeks", [])
        
        if not weeks_data:
            st.warning("No roadmap data available")
            return
        
        if st.session_state.get("user_id"):
            db = get_learning_db()
            progress = db.get_roadmap_overall_progress(
                st.session_state.user_id,
                st.session_state.current_topic
            )
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                    <div style="background:#667eea22;padding:20px;border-radius:12px;margin:20px 0;text-align:center">
                        <h2 style="margin:0;color:#667eea">{progress['percentage']:.0f}% Complete</h2>
                        <p style="margin:10px 0 0 0;color:#b0b0b0;font-size:1.1em">
                            {progress['completed_tasks']} of {progress['total_tasks']} tasks completed
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📥 Download Roadmap", use_container_width=True, type="secondary"):
                    st.info("Download feature requires additional packages")
        
        st.markdown("---")
        
        for week_data in weeks_data:
            week_num = week_data.get("week", 1)
            week_title = week_data.get("title", f"Week {week_num}")
            tasks = week_data.get("tasks", [])
            
            # Aggressively clean arr_week artifacts from stored data
            import re as _re
            def _clean(text):
                if not text:
                    return text
                # Remove arr_week variants (the main culprit)
                text = _re.sub(r'\.?arr[_\s]?[Ww]eek\d*:?\s*', '', text)
                text = _re.sub(r'\.?[Aa]rr[_\s]?[Ww]eek\d*:?\s*', '', text)
                # Remove "Week N - " or "Week N: " prefix from title only
                text = _re.sub(r'^[Ww]eek\s*\d+\s*[-:]\s*', '', text)
                # Remove control chars and extra whitespace
                text = _re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
                text = ' '.join(text.split()).strip().lstrip('.')
                return text

            week_title = _clean(week_title)
            tasks = [_clean(t) for t in tasks]

            # Fallback if title ended up empty
            if not week_title:
                week_title = f"Week {week_num} Content"
            
            with st.expander(f"📅 Week {week_num}: {week_title}", expanded=(week_num == 1)):
                st.markdown(f"**Week {week_num} - {week_title}**")
                st.markdown("---")
                
                if not tasks:
                    st.info("No tasks defined for this week")
                    continue
                
                for i, task in enumerate(tasks, 1):
                    task = clean_roadmap_text(task)
                    
                    is_completed = False
                    if st.session_state.get("user_id"):
                        db = get_learning_db()
                        is_completed = db.get_roadmap_progress(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            task
                        )
                    
                    completed = st.checkbox(
                        task,
                        value=is_completed,
                        key=f"task_w{week_num}_t{i}_{hash(task)}"
                    )
                    
                    if completed != is_completed and st.session_state.get("user_id"):
                        db = get_learning_db()
                        db.save_roadmap_progress(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            task,
                            completed
                        )
                        
                        if completed:
                            advanced_db = get_advanced_db()
                            advanced_db.update_streak(st.session_state.user_id)
                        
                        st.rerun()


def render_flashcards_tab():
    """Render AI-generated flashcards"""
    if not st.session_state.current_topic:
        st.info("👆 Enter a topic to generate flashcards")
        return
    
    st.markdown("### 🎴 AI Flashcards")
    st.caption(f"Interactive flashcards for {st.session_state.current_topic}")
    
    if st.button("🚀 Generate Flashcards", use_container_width=True, type="primary"):
        with st.spinner("Creating flashcards..."):
            flashcards = generate_flashcards(st.session_state.current_topic)
            
            if flashcards:
                st.session_state.flashcards = flashcards
                st.session_state.flashcard_index = 0
                st.session_state.show_answer = False
                
                if st.session_state.get("user_id"):
                    advanced_db = get_advanced_db()
                    advanced_db.save_flashcards(
                        st.session_state.user_id,
                        st.session_state.current_topic,
                        flashcards
                    )
                    advanced_db.update_streak(st.session_state.user_id)
                
                st.success(f"✅ Generated {len(flashcards)} flashcards!")
                st.rerun()
    
    if not st.session_state.flashcards and st.session_state.get("user_id"):
        advanced_db = get_advanced_db()
        loaded_cards = advanced_db.get_flashcards(
            st.session_state.user_id,
            st.session_state.current_topic
        )
        if loaded_cards:
            st.session_state.flashcards = loaded_cards
    
    if st.session_state.flashcards:
        flashcards = st.session_state.flashcards
        current_index = st.session_state.flashcard_index
        current_card = flashcards[current_index]
        
        st.markdown(f"**Card {current_index + 1} of {len(flashcards)}**")
        st.markdown("---")
        
        if not st.session_state.show_answer:
            question_emoji = "❓"
            question_text = current_card['question']
            
            st.markdown(f"""
                <div style="
                    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                    padding:60px 40px;
                    border-radius:20px;
                    text-align:center;
                    min-height:250px;
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    box-shadow:0 10px 30px rgba(102,126,234,0.3);
                    cursor:pointer;
                ">
                    <h3 style="color:white;margin-bottom:20px;font-size:1.3em">{question_emoji} Question</h3>
                    <p style="color:white;font-size:1.4em;line-height:1.6;margin:0">{question_text}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            answer_emoji = "✅"
            answer_text = current_card['answer']
            
            st.markdown(f"""
                <div style="
                    background:linear-gradient(135deg,#10b981 0%,#059669 100%);
                    padding:60px 40px;
                    border-radius:20px;
                    text-align:center;
                    min-height:250px;
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    box-shadow:0 10px 30px rgba(16,185,129,0.3);
                    cursor:pointer;
                ">
                    <h3 style="color:white;margin-bottom:20px;font-size:1.3em">{answer_emoji} Answer</h3>
                    <p style="color:white;font-size:1.4em;line-height:1.6;margin:0">{answer_text}</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⬅️ Previous", use_container_width=True, disabled=(current_index == 0)):
                st.session_state.flashcard_index = max(0, current_index - 1)
                st.session_state.show_answer = False
                st.rerun()
        
        with col2:
            if st.button("🔄 Flip Card", use_container_width=True, type="primary"):
                st.session_state.show_answer = not st.session_state.show_answer
                st.rerun()
        
        with col3:
            if st.button("➡️ Next", use_container_width=True, disabled=(current_index == len(flashcards) - 1)):
                st.session_state.flashcard_index = min(len(flashcards) - 1, current_index + 1)
                st.session_state.show_answer = False
                st.rerun()
        
        with col4:
            if st.button("🔀 Shuffle", use_container_width=True):
                import random
                random.shuffle(st.session_state.flashcards)
                st.session_state.flashcard_index = 0
                st.session_state.show_answer = False
                st.rerun()


def render_study_notes_tab():
    """Render AI-generated study notes"""
    if not st.session_state.generated_content:
        st.info("👆 Generate content first to create study notes")
        return
    
    st.markdown("### 📝 Study Notes")
    st.caption(f"Concise notes for {st.session_state.current_topic}")
    
    if st.button("🚀 Generate Study Notes", use_container_width=True, type="primary"):
        with st.spinner("Creating study notes..."):
            notes = generate_study_notes(
                st.session_state.current_topic,
                st.session_state.generated_content
            )
            
            if notes:
                st.session_state.study_notes = notes
                
                if st.session_state.get("user_id"):
                    advanced_db = get_advanced_db()
                    advanced_db.save_notes(
                        st.session_state.user_id,
                        st.session_state.current_topic,
                        notes
                    )
                    advanced_db.update_streak(st.session_state.user_id)
                
                st.success("✅ Study notes generated!")
                st.rerun()
    
    if not st.session_state.study_notes and st.session_state.get("user_id"):
        advanced_db = get_advanced_db()
        loaded_notes = advanced_db.get_notes(
            st.session_state.user_id,
            st.session_state.current_topic
        )
        if loaded_notes:
            st.session_state.study_notes = loaded_notes
    
    if st.session_state.study_notes:
        st.markdown("---")
        st.markdown(st.session_state.study_notes)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("📥 Download as Text", use_container_width=True):
            notes_text = st.session_state.study_notes
            st.download_button(
                label="💾 Download TXT",
                data=notes_text,
                file_name=f"{st.session_state.current_topic.replace(' ', '_')}_notes.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("Click 'Generate Study Notes' to create concise notes for this topic")


def main():
    """Main application function"""
    if not check_authentication():
        st.warning("⚠️ Please login to access LearnSphere AI")
        if st.button("🔐 Go to Login"):
            st.switch_page("Home.py")
        st.stop()
    
    init_session_state()
    
    # Professional Hero Header
    st.markdown("""
        <div class="hero-header">
            <h1 style="font-size:3rem;font-weight:800;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;margin:0;letter-spacing:-0.5px;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;">🚀 LearnSphere AI</h1>
            <p style="font-size:1.3rem;color:rgba(255,255,255,0.95)!important;-webkit-text-fill-color:rgba(255,255,255,0.95)!important;margin-top:0.5rem;font-weight:500;-webkit-font-smoothing:antialiased;">Your Personal AI Learning Companion</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Professional Statistics Cards
    if st.session_state.get("user_id"):
        db = get_learning_db()
        advanced_db = get_advanced_db()
        
        # Get user stats
        try:
            # Get real completion data
            topics_count = db.get_completed_topics_count(st.session_state.user_id)
            streak = advanced_db.get_streak(st.session_state.user_id)
            
            # Calculate study time
            study_time_minutes = db.get_total_study_time(st.session_state.user_id)
            study_time_hours = round(study_time_minutes / 60, 1) if study_time_minutes > 0 else 0
            study_time = f"{study_time_hours}h"
        except:
            topics_count = 0
            streak = 0
            study_time = "0h"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size:2.5rem;">📚</div>
                    <div class="stat-value">{topics_count}</div>
                    <div class="stat-label">Topics Learned</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size:2.5rem;">⏱️</div>
                    <div class="stat-value">{study_time}</div>
                    <div class="stat-label">Study Time</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size:2.5rem;">🔥</div>
                    <div class="stat-value">{streak}</div>
                    <div class="stat-label">Day Streak</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Learning Input Section with Glass Card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        topic = st.text_input(
            "🎯 What do you want to learn today?",
            placeholder="e.g., Neural Networks, React Hooks, Data Structures",
            key="topic_input"
        )
    
    with col2:
        difficulty = st.selectbox(
            "📊 Difficulty Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=1,
            key="difficulty_select"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Generate Content", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if generate_btn and topic:
        with st.spinner("🤖 AI is crafting your personalized learning experience..."):
            content = generate_learning_content(topic, difficulty)
            
            if content:
                st.session_state.generated_content = content
                st.session_state.current_topic = topic
                st.session_state.current_difficulty = difficulty
                st.session_state.study_start_time = datetime.now()  # Track study start time
                st.session_state.audio_file = None
                st.session_state.audio_sections = None
                st.session_state.code_examples = None
                st.session_state.code_topic = topic
                st.session_state.code_output = None
                st.session_state.chat_history = []
                st.session_state.flashcards = []
                st.session_state.study_notes = None
                
                if st.session_state.get("user_id"):
                    db = get_learning_db()
                    db.save_learning_topic(st.session_state.user_id, topic, difficulty, content)
                    
                    advanced_db = get_advanced_db()
                    new_streak = advanced_db.update_streak(st.session_state.user_id)
                    
                    history = db.get_tutor_history(st.session_state.user_id, topic)
                    st.session_state.chat_history = [
                        {"user": h["user_message"], "ai": h["ai_response"]}
                        for h in history
                    ]
                
                st.success(f"✅ Content generated for: {topic}")
                st.rerun()
    
    if st.session_state.generated_content or st.session_state.current_topic:
        st.markdown("<br>", unsafe_allow_html=True)
        
        tabs = st.tabs([
            "📖 Content",
            "🔊 Audio",
            "🤖 Tutor",
            "🎥 Videos",
            "💻 Code",
            "🗺️ Roadmap",
            "🎴 Flashcards",
            "📝 Notes"
        ])
        
        with tabs[0]:
            render_content_tab()
        
        with tabs[1]:
            render_audio_tab()
        
        with tabs[2]:
            render_tutor_tab()
        
        with tabs[3]:
            render_videos_tab()
        
        with tabs[4]:
            render_code_tab()
        
        with tabs[5]:
            render_roadmap_tab()
        
        with tabs[6]:
            render_flashcards_tab()
        
        with tabs[7]:
            render_study_notes_tab()
    else:
        # Welcome Screen with Modern Design
        st.markdown("""
            <div class="glass-card" style="text-align:center;padding:60px 20px;margin:40px 0">
                <h2 style="color:#667eea;margin-bottom:20px;font-size:2.5rem">👋 Welcome to LearnSphere AI</h2>
                <p style="color:#b0b0b0;font-size:1.2em;margin-bottom:40px">Enter a topic above to start your personalized learning journey</p>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:20px;max-width:900px;margin:0 auto">
                    <div class="stat-card"><span style="font-size:2em">📖</span><br><span style="color:#fafafa;font-weight:600">AI Content</span></div>
                    <div class="stat-card"><span style="font-size:2em">🔊</span><br><span style="color:#fafafa;font-weight:600">Audio</span></div>
                    <div class="stat-card"><span style="font-size:2em">🤖</span><br><span style="color:#fafafa;font-weight:600">AI Tutor</span></div>
                    <div class="stat-card"><span style="font-size:2em">🎥</span><br><span style="color:#fafafa;font-weight:600">Videos</span></div>
                    <div class="stat-card"><span style="font-size:2em">💻</span><br><span style="color:#fafafa;font-weight:600">Code Lab</span></div>
                    <div class="stat-card"><span style="font-size:2em">🗺️</span><br><span style="color:#fafafa;font-weight:600">Roadmap</span></div>
                    <div class="stat-card"><span style="font-size:2em">🎴</span><br><span style="color:#fafafa;font-weight:600">Flashcards</span></div>
                    <div class="stat-card"><span style="font-size:2em">📝</span><br><span style="color:#fafafa;font-weight:600">Notes</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Professional Footer
    st.markdown("""
        <div class="footer">
            <p style="margin:0;font-size:0.9rem">Made with ❤️ by <strong style="color:#667eea">LearnSphere AI</strong></p>
            <p style="margin:0.5rem 0 0 0;font-size:0.8rem">© 2026 LearnSphere • Empowering learners worldwide</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
