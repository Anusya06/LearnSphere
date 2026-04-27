"""Script to create the improved Learn page with all fixes"""

IMPROVED_LEARN_PAGE = '''"""
Advanced Learn Page - Complete AI Learning Hub (IMPROVED)
Features: AI Content, Audio, Tutor Chat, Videos, Code Examples, Roadmap
Fixes: Enter key support, custom code topics, roadmap cleanup, progress tracking
"""
import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime
from io import BytesIO
import re

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
        "code_topic": "",
        "code_output": None,
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


def clean_roadmap_text(text: str) -> str:
    """Clean roadmap text by removing unwanted prefixes"""
    # Remove patterns like ".arrWeek:", "Week:", etc.
    text = re.sub(r'\\.arr[Ww]eek:\\s*', '', text)
    text = re.sub(r'^[Ww]eek:\\s*', '', text)
    text = text.strip()
    return text


def generate_roadmap(topic: str, difficulty: str, weeks: int = 6) -> dict:
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
        
        # Clean markdown formatting
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        roadmap_data = json.loads(content)
        
        # Clean all text in roadmap
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
    try:
        prompt = f"""Generate a practical code example for: {topic}
Programming Language: {language}

Return ONLY valid JSON in this format:
{{
  "code": "actual working code here",
  "explanation": "clear explanation of what the code does",
  "language": "{language}"
}}

Make the code educational, well-commented, and runnable. Return ONLY JSON."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a coding instructor. Return ONLY valid JSON, no markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        return json.loads(content)
    except Exception as e:
        st.error(f"Error generating code: {str(e)}")
        return None


def detect_language_for_topic(topic: str) -> str:
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ["ml", "ai", "neural", "data", "pandas", "numpy"]):
        return "python"
    elif any(w in topic_lower for w in ["web", "react", "javascript", "node", "frontend"]):
        return "javascript"
    elif any(w in topic_lower for w in ["database", "sql", "query"]):
        return "sql"
    elif any(w in topic_lower for w in ["system", "c++", "cpp", "pointer"]):
        return "cpp"
    elif any(w in topic_lower for w in ["java", "spring", "android"]):
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
        messages = [{"role": "system", "content": f"You are an AI tutor helping students learn {topic}. Answer clearly and concisely. Context: {context[:1000]}"}]
        
        # Add recent chat history
        for msg in st.session_state.chat_history[-5:]:
            messages.append({"role": "user", "content": msg["user"]})
            messages.append({"role": "assistant", "content": msg["ai"]})
        
        # Add current message
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
        st.code("pip install gtts", language="bash")
        return
    
    if not st.session_state.generated_content:
        st.info("👆 Generate content first to enable audio")
        return
    
    st.markdown("### 🔊 Listen to Content")
    st.caption("AI-generated audio narration")
    
    if st.button("🎵 Generate Audio", use_container_width=True):
        with st.spinner("Generating audio..."):
            text = st.session_state.generated_content.replace("#", "").replace("*", "")
            audio_buffer = generate_audio(text)
            if audio_buffer:
                st.session_state.audio_file = audio_buffer
                st.success("✅ Audio generated!")
                st.rerun()
    
    if st.session_state.audio_file:
        st.audio(st.session_state.audio_file, format="audio/mp3")
        st.caption("🎧 Use headphones for better experience")


def render_tutor_tab():
    """IMPROVED: Chat with Enter key support and auto-clearing input"""
    if not st.session_state.generated_content:
        st.info("👆 Generate content first to enable tutor chat")
        return
    
    st.markdown("### 🤖 AI Tutor Chat")
    st.caption(f"Ask questions about {st.session_state.current_topic}")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            # User message
            st.markdown(f"""
                <div style="background:#667eea22;padding:15px;border-radius:12px;margin:10px 0;border-left:4px solid #667eea">
                    <strong style="color:#667eea">👤 You:</strong><br>
                    <span style="color:#fafafa">{msg["user"]}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # AI response
            st.markdown(f"""
                <div style="background:#10b98122;padding:15px;border-radius:12px;margin:10px 0;border-left:4px solid #10b981">
                    <strong style="color:#10b981">🤖 Tutor:</strong><br>
                    <span style="color:#fafafa">{msg["ai"]}</span>
                </div>
            """, unsafe_allow_html=True)
    
    # FIXED: Use st.chat_input for Enter key support
    st.markdown("<br>", unsafe_allow_html=True)
    user_question = st.chat_input("💬 Ask a question (press Enter to send)...")
    
    # Process message when Enter is pressed
    if user_question:
        with st.spinner("🤖 Tutor is thinking..."):
            ai_response = chat_with_tutor(
                user_question,
                st.session_state.current_topic,
                st.session_state.generated_content
            )
            
            # Add to history
            st.session_state.chat_history.append({
                "user": user_question,
                "ai": ai_response,
                "timestamp": datetime.now()
            })
            
            # Save to database
            if st.session_state.get("user_id"):
                db = get_learning_db()
                db.save_tutor_message(
                    st.session_state.user_id,
                    st.session_state.current_topic,
                    user_question,
                    ai_response
                )
            
            # Rerun to show new message (input will auto-clear)
            st.rerun()


def render_videos_tab():
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
                    <a href="{url}" target="_blank" style="display:inline-block;background:#667eea;color:white;padding:8px 16px;border-radius:8px;text-decoration:none;font-weight:600">🔗 Watch Videos</a>
                </div>
            """, unsafe_allow_html=True)


def render_code_tab():
    """IMPROVED: Custom topic input for code generation"""
    st.markdown("### 💻 Code Generator")
    st.caption("Generate code examples with custom topics")
    
    # FIXED: Add custom topic input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        code_topic = st.text_input(
            "📝 Enter Topic for Code",
            value=st.session_state.get("code_topic", ""),
            placeholder="e.g., Binary Search, Linked List, REST API",
            key="code_topic_input",
            help="Enter any programming concept you want to generate code for"
        )
    
    with col2:
        # Auto-detect language based on code topic or main topic
        topic_for_detection = code_topic if code_topic else st.session_state.get("current_topic", "")
        detected = detect_language_for_topic(topic_for_detection)
        
        language = st.selectbox(
            "Select Language",
            ["python", "javascript", "java", "cpp", "sql"],
            index=["python", "javascript", "java", "cpp", "sql"].index(detected),
            key="code_language_select"
        )
    
    # Show auto-detection info
    if code_topic:
        st.info(f"🔍 Auto-detected language: **{detected.upper()}** (you can change it above)")
    
    # Generate button
    if st.button("🚀 Generate Code Example", use_container_width=True, type="primary"):
        if not code_topic:
            st.error("❌ Please enter a topic for code generation")
        else:
            with st.spinner(f"Generating {language.upper()} code for: {code_topic}..."):
                code_data = generate_code_example(code_topic, language)
                
                if code_data:
                    st.session_state.code_examples = code_data
                    st.session_state.code_topic = code_topic
                    st.session_state.code_output = None
                    st.success(f"✅ Code generated for: {code_topic}")
                    st.rerun()
    
    # Display generated code
    if st.session_state.code_examples:
        st.markdown("---")
        
        # Show what topic the code is for
        if st.session_state.get("code_topic"):
            st.markdown(f"**Topic:** {st.session_state.code_topic}")
        
        # Explanation
        st.markdown("#### 📝 Explanation")
        st.markdown(st.session_state.code_examples.get("explanation", ""))
        
        # Code
        st.markdown("#### 💾 Generated Code")
        code_lang = st.session_state.code_examples.get("language", "python")
        code_text = st.session_state.code_examples.get("code", "")
        st.code(code_text, language=code_lang)
        
        # FIXED: Run button for Python with proper output display
        if code_lang == "python":
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("▶️ Run Code", use_container_width=True):
                    with st.spinner("Executing code..."):
                        executor = CodeExecutor()
                        result = executor.execute(code_text, "python")
                        st.session_state.code_output = result
                        st.rerun()
            
            # Display output
            if st.session_state.code_output:
                st.markdown("---")
                st.markdown("#### 📤 Output")
                
                output_data = st.session_state.code_output
                
                # Show output
                if output_data.get("output"):
                    st.code(output_data["output"], language="text")
                
                # Show errors if any
                if output_data.get("error"):
                    st.markdown("#### ❌ Error")
                    st.error(output_data["error"])
                
                # Show execution time
                if output_data.get("execution_time"):
                    st.caption(f"⏱️ Execution time: {output_data['execution_time']:.3f}s")
        else:
            st.info(f"💡 {code_lang.upper()} code execution is not supported. Copy and run locally.")


def render_roadmap_tab():
    """IMPROVED: Clean roadmap display with proper formatting and progress"""
    if not st.session_state.current_topic:
        st.info("👆 Enter a topic to generate a learning roadmap")
        return
    
    st.markdown("### 🗺️ Learning Roadmap")
    st.caption(f"Structured path to master {st.session_state.current_topic}")
    
    # Roadmap generation controls
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
                    
                    # Save to database
                    if st.session_state.get("user_id"):
                        db = get_learning_db()
                        db.save_generated_content(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            st.session_state.generated_content or "",
                            json.dumps(roadmap),
                            st.session_state.current_difficulty
                        )
                    
                    st.success("✅ Roadmap generated!")
                    st.rerun()
    
    # Display roadmap
    if st.session_state.roadmap_data:
        weeks_data = st.session_state.roadmap_data.get("weeks", [])
        
        if not weeks_data:
            st.warning("No roadmap data available")
            return
        
        # FIXED: Calculate and display progress
        if st.session_state.get("user_id"):
            db = get_learning_db()
            progress = db.get_topic_progress(
                st.session_state.user_id,
                st.session_state.current_topic
            )
            
            # Progress indicator
            st.markdown(f"""
                <div style="background:#667eea22;padding:20px;border-radius:12px;margin:20px 0;text-align:center">
                    <h2 style="margin:0;color:#667eea">{progress['percentage']:.0f}% Complete</h2>
                    <p style="margin:10px 0 0 0;color:#b0b0b0;font-size:1.1em">
                        {progress['completed_tasks']} of {progress['total_tasks']} tasks completed
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # FIXED: Display weeks with proper formatting
        for week_data in weeks_data:
            week_num = week_data.get("week", 1)
            week_title = week_data.get("title", f"Week {week_num}")
            tasks = week_data.get("tasks", [])
            
            # Clean the title
            week_title = clean_roadmap_text(week_title)
            
            # Week header with proper styling
            with st.expander(f"📅 **Week {week_num}**: {week_title}", expanded=(week_num == 1)):
                st.markdown(f"**Week {week_num} - {week_title}**")
                st.markdown("---")
                
                if not tasks:
                    st.info("No tasks defined for this week")
                    continue
                
                # Display tasks with checkboxes
                for i, task in enumerate(tasks, 1):
                    # Clean task text
                    task = clean_roadmap_text(task)
                    
                    # Get completion status from database
                    is_completed = False
                    if st.session_state.get("user_id"):
                        db = get_learning_db()
                        is_completed = db.get_task_progress(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            week_num,
                            task
                        )
                    
                    # Checkbox with proper key
                    completed = st.checkbox(
                        task,
                        value=is_completed,
                        key=f"task_w{week_num}_t{i}_{hash(task)}"
                    )
                    
                    # Save progress if changed
                    if completed != is_completed and st.session_state.get("user_id"):
                        db = get_learning_db()
                        db.save_task_progress(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            week_num,
                            task,
                            completed
                        )
                        # Rerun to update progress
                        st.rerun()


def main():
    if not check_authentication():
        st.warning("Please login to access the learning hub")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()
    
    init_session_state()
    
    st.title("📚 AI Learning Hub")
    st.markdown("Complete learning platform with AI-powered content, tutor, and progress tracking")
    st.markdown("---")
    
    # Topic input
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        topic = st.text_input(
            "🔍 Enter Learning Topic",
            placeholder="e.g., Neural Networks, React Hooks, SQL Joins",
            key="main_topic_input"
        )
    
    with col2:
        difficulty = st.selectbox(
            "📊 Level",
            ["Beginner", "Intermediate", "Advanced"],
            key="difficulty_select"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Generate", use_container_width=True, type="primary")
    
    # Generate content
    if generate_btn and topic:
        with st.spinner("🤖 AI is creating your learning content..."):
            content = generate_learning_content(topic, difficulty)
            
            if content:
                st.session_state.generated_content = content
                st.session_state.current_topic = topic
                st.session_state.current_difficulty = difficulty
                st.session_state.audio_file = None
                st.session_state.code_examples = None
                st.session_state.code_topic = topic  # Pre-fill code topic
                st.session_state.code_output = None
                st.session_state.chat_history = []
                
                # Load chat history from database
                if st.session_state.get("user_id"):
                    db = get_learning_db()
                    history = db.get_tutor_history(st.session_state.user_id, topic)
                    st.session_state.chat_history = [
                        {"user": h["user_message"], "ai": h["ai_response"]}
                        for h in history
                    ]
                
                st.success(f"✅ Content generated for: {topic}")
                st.rerun()
    
    # Display current topic
    if st.session_state.current_topic:
        st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px;border-radius:12px;margin:20px 0;text-align:center">
                <h2 style="margin:0;color:white">📖 {st.session_state.current_topic}</h2>
                <p style="margin:5px 0 0 0;color:rgba(255,255,255,0.9)">{st.session_state.current_difficulty} Level</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Tabs
    if st.session_state.generated_content or st.session_state.current_topic:
        tabs = st.tabs([
            "📖 Content",
            "🔊 Audio",
            "🤖 Tutor",
            "🎥 Videos",
            "💻 Code",
            "🗺️ Roadmap"
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
    else:
        # Welcome message
        st.markdown("""
            <div style="text-align:center;padding:60px 20px;background:#1e1e1e;border-radius:20px;margin:40px 0">
                <h2 style="color:#667eea;margin-bottom:20px">👋 Welcome to Your AI Learning Hub</h2>
                <p style="color:#b0b0b0;font-size:1.1em;margin-bottom:30px">Enter a topic above to start your personalized learning journey</p>
                <div style="display:flex;justify-content:center;gap:20px;flex-wrap:wrap">
                    <div style="background:#667eea22;padding:15px 25px;border-radius:10px"><span style="font-size:1.5em">📖</span><br><span style="color:#fafafa">AI Content</span></div>
                    <div style="background:#667eea22;padding:15px 25px;border-radius:10px"><span style="font-size:1.5em">🔊</span><br><span style="color:#fafafa">Audio</span></div>
                    <div style="background:#667eea22;padding:15px 25px;border-radius:10px"><span style="font-size:1.5em">🤖</span><br><span style="color:#fafafa">AI Tutor</span></div>
                    <div style="background:#667eea22;padding:15px 25px;border-radius:10px"><span style="font-size:1.5em">🎥</span><br><span style="color:#fafafa">Videos</span></div>
                    <div style="background:#667eea22;padding:15px 25px;border-radius:10px"><span style="font-size:1.5em">💻</span><br><span style="color:#fafafa">Code</span></div>
                    <div style="background:#667eea22;padding:15px 25px;border-radius:10px"><span style="font-size:1.5em">🗺️</span><br><span style="color:#fafafa">Roadmap</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
'''

# Write the file
with open("frontend/pages/2_Learn.py", "w", encoding="utf-8") as f:
    f.write(IMPROVED_LEARN_PAGE)

print("✅ Improved Learn page created successfully!")
print(f"📊 File size: {len(IMPROVED_LEARN_PAGE)} bytes")
print("\n🎯 Improvements implemented:")
print("  ✅ Chat with Enter key support (st.chat_input)")
print("  ✅ Auto-clearing input after sending")
print("  ✅ Custom topic input for code generation")
print("  ✅ Proper code execution with output/error display")
print("  ✅ Clean roadmap text (removed .arrWeek: prefix)")
print("  ✅ Improved roadmap UI with proper formatting")
print("  ✅ Real-time progress calculation")
print("  ✅ Database storage for all progress")
print("\n🔄 Restart Streamlit to see the changes")
