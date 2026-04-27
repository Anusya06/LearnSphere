"""Script to create the complete Learn page"""

LEARN_PAGE_CONTENT = '''"""
Advanced Learn Page - Complete AI Learning Hub
Features: AI Content, Audio, Tutor Chat, Videos, Code Examples, Roadmap
"""
import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime
from io import BytesIO

sys.path.append(str(Path(__file__).parent.parent))

from components.ui_components import gradient_card
from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.learning_progress import get_learning_db
from utils.code_executor import CodeExecutor
from groq import Groq

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

st.set_page_config(page_title="Learn Hub", page_icon="📚", layout="wide")
apply_theme()
load_theme_css()

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
    defaults = {
        "generated_content": None,
        "current_topic": None,
        "current_difficulty": "Intermediate",
        "chat_history": [],
        "roadmap_data": None,
        "audio_file": None,
        "code_examples": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def generate_learning_content(topic: str, difficulty: str) -> str:
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


def generate_roadmap(topic: str, difficulty: str, weeks: int = 6) -> dict:
    try:
        prompt = f"""Create a {weeks}-week roadmap for: {topic}
Return ONLY valid JSON:
{{"weeks": [{{"week": 1, "title": "Title", "tasks": ["Task 1", "Task 2"]}}]}}"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
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
        st.error(f"Error: {str(e)}")
        return None


def generate_code_example(topic: str, language: str) -> dict:
    try:
        prompt = f"""Generate code for: {topic} in {language}
Return ONLY JSON: {{"code": "...", "explanation": "...", "language": "{language}"}}"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
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
        
        return json.loads(content)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def detect_language_for_topic(topic: str) -> str:
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ["ml", "ai", "neural", "data"]):
        return "python"
    elif any(w in topic_lower for w in ["web", "react", "javascript"]):
        return "javascript"
    elif any(w in topic_lower for w in ["database", "sql"]):
        return "sql"
    elif any(w in topic_lower for w in ["system", "c++"]):
        return "cpp"
    elif any(w in topic_lower for w in ["java", "spring"]):
        return "java"
    return "python"


def generate_audio(text: str) -> BytesIO:
    if not GTTS_AVAILABLE:
        return None
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def chat_with_tutor(user_message: str, topic: str, context: str) -> str:
    try:
        messages = [{"role": "system", "content": f"You are an AI tutor for {topic}. Context: {context[:1000]}"}]
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


def render_content_tab():
    if st.session_state.generated_content:
        st.markdown(st.session_state.generated_content)
    else:
        st.info("👆 Enter a topic above to generate learning content")


def render_audio_tab():
    if not GTTS_AVAILABLE:
        st.warning("⚠️ Install gTTS: pip install gtts")
        return
    if not st.session_state.generated_content:
        st.info("👆 Generate content first")
        return
    
    st.markdown("### 🔊 Listen to Content")
    if st.button("🎵 Generate Audio"):
        with st.spinner("Generating..."):
            text = st.session_state.generated_content.replace("#", "").replace("*", "")
            audio_buffer = generate_audio(text)
            if audio_buffer:
                st.session_state.audio_file = audio_buffer
                st.success("✅ Audio generated!")
                st.rerun()
    
    if st.session_state.audio_file:
        st.audio(st.session_state.audio_file, format="audio/mp3")


def render_tutor_tab():
    if not st.session_state.generated_content:
        st.info("👆 Generate content first")
        return
    
    st.markdown("### 🤖 AI Tutor Chat")
    for msg in st.session_state.chat_history:
        st.markdown(f'<div style="background:#667eea22;padding:15px;border-radius:12px;margin:10px 0;border-left:4px solid #667eea"><strong style="color:#667eea">👤 You:</strong><br><span style="color:#fafafa">{msg["user"]}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="background:#10b98122;padding:15px;border-radius:12px;margin:10px 0;border-left:4px solid #10b981"><strong style="color:#10b981">🤖 Tutor:</strong><br><span style="color:#fafafa">{msg["ai"]}</span></div>', unsafe_allow_html=True)
    
    user_question = st.text_input("💬 Ask:", key="tutor_input")
    if st.button("📤 Send"):
        if user_question:
            with st.spinner("Thinking..."):
                ai_response = chat_with_tutor(user_question, st.session_state.current_topic, st.session_state.generated_content)
                st.session_state.chat_history.append({"user": user_question, "ai": ai_response})
                if st.session_state.get("user_id"):
                    db = get_learning_db()
                    db.save_tutor_message(st.session_state.user_id, st.session_state.current_topic, user_question, ai_response)
                st.rerun()


def render_videos_tab():
    if not st.session_state.current_topic:
        st.info("👆 Enter a topic first")
        return
    
    st.markdown("### 🎥 YouTube Resources")
    topic = st.session_state.current_topic
    categories = [
        ("Tutorial", f"https://www.youtube.com/results?search_query={topic}+tutorial"),
        ("Beginner", f"https://www.youtube.com/results?search_query={topic}+for+beginners"),
        ("Advanced", f"https://www.youtube.com/results?search_query={topic}+advanced"),
        ("Examples", f"https://www.youtube.com/results?search_query={topic}+examples"),
    ]
    
    cols = st.columns(2)
    for i, (cat, url) in enumerate(categories):
        with cols[i % 2]:
            st.markdown(f'<div style="background:#1e1e1e;padding:20px;border-radius:12px;margin:10px 0"><h4 style="color:#667eea">🎬 {cat}</h4><a href="{url}" target="_blank" style="display:inline-block;background:#667eea;color:white;padding:8px 16px;border-radius:8px;text-decoration:none">🔗 Watch</a></div>', unsafe_allow_html=True)


def render_code_tab():
    if not st.session_state.current_topic:
        st.info("👆 Enter a topic first")
        return
    
    st.markdown("### 💻 Code Examples")
    detected = detect_language_for_topic(st.session_state.current_topic)
    st.info(f"🔍 Auto-detected: **{detected.upper()}**")
    
    language = st.selectbox("Language", ["python", "javascript", "java", "cpp", "sql"], index=["python", "javascript", "java", "cpp", "sql"].index(detected))
    
    if st.button("🚀 Generate Code"):
        with st.spinner("Generating..."):
            code_data = generate_code_example(st.session_state.current_topic, language)
            if code_data:
                st.session_state.code_examples = code_data
                st.rerun()
    
    if st.session_state.code_examples:
        st.markdown("#### 📝 Explanation")
        st.markdown(st.session_state.code_examples.get("explanation", ""))
        st.markdown("#### 💾 Code")
        st.code(st.session_state.code_examples.get("code", ""), language=st.session_state.code_examples.get("language", "python"))
        
        if st.session_state.code_examples.get("language") == "python":
            if st.button("▶️ Run"):
                executor = CodeExecutor()
                result = executor.execute(st.session_state.code_examples.get("code", ""), "python")
                if result and result.get("output"):
                    st.code(result["output"])


def render_roadmap_tab():
    if not st.session_state.current_topic:
        st.info("👆 Enter a topic first")
        return
    
    st.markdown("### 🗺️ Learning Roadmap")
    weeks = st.number_input("Weeks", 4, 12, 6)
    
    if st.button("🎯 Generate Roadmap"):
        with st.spinner("Creating..."):
            roadmap = generate_roadmap(st.session_state.current_topic, st.session_state.current_difficulty, weeks)
            if roadmap:
                st.session_state.roadmap_data = roadmap
                st.rerun()
    
    if st.session_state.roadmap_data:
        weeks_data = st.session_state.roadmap_data.get("weeks", [])
        
        if st.session_state.get("user_id"):
            db = get_learning_db()
            progress = db.get_topic_progress(st.session_state.user_id, st.session_state.current_topic)
            st.markdown(f'<div style="background:#667eea22;padding:15px;border-radius:12px;text-align:center"><h3 style="color:#667eea">{progress["percentage"]:.0f}% Complete</h3><p style="color:#b0b0b0">{progress["completed_tasks"]} of {progress["total_tasks"]} tasks</p></div>', unsafe_allow_html=True)
        
        for week_data in weeks_data:
            week_num = week_data.get("week", 1)
            week_title = week_data.get("title", f"Week {week_num}")
            tasks = week_data.get("tasks", [])
            
            with st.expander(f"📅 Week {week_num}: {week_title}", expanded=(week_num==1)):
                for task in tasks:
                    is_completed = False
                    if st.session_state.get("user_id"):
                        db = get_learning_db()
                        is_completed = db.get_task_progress(st.session_state.user_id, st.session_state.current_topic, week_num, task)
                    
                    completed = st.checkbox(task, value=is_completed, key=f"task_{week_num}_{task}")
                    if completed != is_completed and st.session_state.get("user_id"):
                        db = get_learning_db()
                        db.save_task_progress(st.session_state.user_id, st.session_state.current_topic, week_num, task, completed)


def main():
    if not check_authentication():
        st.warning("Please login")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()
    
    init_session_state()
    
    st.title("📚 AI Learning Hub")
    st.markdown("Complete learning platform with AI-powered content")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        topic = st.text_input("🔍 Enter Topic", placeholder="e.g., Neural Networks")
    with col2:
        difficulty = st.selectbox("📊 Level", ["Beginner", "Intermediate", "Advanced"])
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Generate", type="primary")
    
    if generate_btn and topic:
        with st.spinner("🤖 Generating..."):
            content = generate_learning_content(topic, difficulty)
            if content:
                st.session_state.generated_content = content
                st.session_state.current_topic = topic
                st.session_state.current_difficulty = difficulty
                st.session_state.audio_file = None
                st.session_state.code_examples = None
                st.session_state.chat_history = []
                st.success(f"✅ Generated: {topic}")
                st.rerun()
    
    if st.session_state.current_topic:
        st.markdown(f'<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px;border-radius:12px;text-align:center"><h2 style="color:white">📖 {st.session_state.current_topic}</h2><p style="color:rgba(255,255,255,0.9)">{st.session_state.current_difficulty} Level</p></div>', unsafe_allow_html=True)
    
    if st.session_state.generated_content or st.session_state.current_topic:
        tabs = st.tabs(["📖 Content", "🔊 Audio", "🤖 Tutor", "🎥 Videos", "💻 Code", "🗺️ Roadmap"])
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
    else:
        st.markdown('<div style="text-align:center;padding:60px 20px;background:#1e1e1e;border-radius:20px"><h2 style="color:#667eea">👋 Welcome to AI Learning Hub</h2><p style="color:#b0b0b0">Enter a topic above to start</p></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
'''

# Write the file
with open("frontend/pages/2_Learn.py", "w", encoding="utf-8") as f:
    f.write(LEARN_PAGE_CONTENT)

print("✅ Learn page created successfully!")
print(f"📊 File size: {len(LEARN_PAGE_CONTENT)} bytes")
print("\n🔄 Now restart Streamlit to see the changes")
