"""
Dynamic Quiz Page - AI-Generated Questions with Real Scoring
Everything is generated dynamically using AI
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.append(str(Path(__file__).parent.parent))

from components.ui_components import gradient_card, animated_progress_bar
from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.user_data import add_quiz_attempt, get_user_data

# Import Groq for AI generation
from groq import Groq

st.set_page_config(page_title="Quiz", page_icon="📝", layout="wide", initial_sidebar_state="expanded")

# Apply theme and sidebar fix
apply_theme()
load_theme_css()
apply_sidebar_fix()

# Initialize Groq client
try:
    api_key = st.secrets["GROQ_API_KEY"]
    groq_client = Groq(api_key=api_key)
except KeyError:
    st.error("⚠️ Groq API key not found. Please add it to secrets.toml")
    st.stop()


def init_quiz_state():
    """Initialize quiz session state"""
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = None
    if "current_quiz_topic" not in st.session_state:
        st.session_state.current_quiz_topic = None
    if "quiz_difficulty" not in st.session_state:
        st.session_state.quiz_difficulty = "Intermediate"
    if "auto_generate_quiz" not in st.session_state:
        st.session_state.auto_generate_quiz = False
    if "suggested_topic" not in st.session_state:
        st.session_state.suggested_topic = ""
    if "suggested_difficulty" not in st.session_state:
        st.session_state.suggested_difficulty = "Intermediate"


def generate_quiz_questions(topic: str, difficulty: str, num_questions: int = 10):
    """Generate quiz questions dynamically using Groq AI"""
    try:
        prompt = f"""Generate {num_questions} multiple choice quiz questions about: {topic}
Difficulty level: {difficulty}

Return ONLY valid JSON in this EXACT format (no markdown, no code blocks):
{{
  "questions": [
    {{
      "id": "q1",
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option B",
      "explanation": "Brief explanation why this is correct",
      "difficulty": "easy"
    }}
  ]
}}

Requirements:
- Each question must have exactly 4 options
- correct_answer must be one of the options (exact match)
- difficulty can be: easy, medium, hard
- Make questions educational and clear
- Return ONLY the JSON, no other text"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a quiz generator. Return ONLY valid JSON, no markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        # Parse JSON
        quiz_data = json.loads(content)
        return quiz_data.get("questions", [])
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse quiz data: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Failed to generate quiz: {str(e)}")
        return None


def render_quiz_selector():
    """Quiz topic selection interface"""
    st.markdown("### 🎯 Create a New Quiz")
    st.caption("🤖 Questions are generated dynamically by AI")
    
    # Check if we need to auto-generate from suggested topic
    auto_generate = st.session_state.get("auto_generate_quiz", False)
    suggested_topic = st.session_state.get("suggested_topic", "")
    suggested_difficulty = st.session_state.get("suggested_difficulty", "Intermediate")
    
    # If auto-generate flag is set, generate quiz immediately
    if auto_generate and suggested_topic:
        # Clear flags first
        st.session_state.auto_generate_quiz = False
        
        with st.spinner(f"🤖 Generating {suggested_topic} quiz..."):
            # Map difficulty to number of questions
            num_questions = 10
            
            questions = generate_quiz_questions(suggested_topic, suggested_difficulty, num_questions)
            
            if questions and len(questions) > 0:
                st.session_state.quiz_questions = questions
                st.session_state.quiz_started = True
                st.session_state.current_quiz_topic = suggested_topic
                st.session_state.quiz_start_time = datetime.now()
                st.session_state.user_answers = {}
                st.session_state.quiz_submitted = False
                
                # Clear suggested topic data
                st.session_state.suggested_topic = ""
                st.session_state.suggested_difficulty = "Intermediate"
                
                st.success(f"✅ Generated {len(questions)} questions about {suggested_topic}!")
                st.rerun()
            else:
                st.error("❌ Failed to generate quiz. Please try again.")
                # Clear flags on error
                st.session_state.suggested_topic = ""
                st.session_state.suggested_difficulty = "Intermediate"
    
    col1, col2, col3 = st.columns(3)
    
    # Pre-fill from suggested topics if available (but don't auto-generate yet)
    default_topic = suggested_topic if suggested_topic else ""
    difficulty_map = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
    default_difficulty_idx = difficulty_map.get(suggested_difficulty, 1)
    
    with col1:
        topic = st.text_input("📝 Topic", value=default_topic, placeholder="e.g., Neural Networks", key="quiz_topic_input")
    
    with col2:
        # Use selectbox without key to avoid session state conflict
        difficulty = st.selectbox(
            "📊 Difficulty", 
            ["Beginner", "Intermediate", "Advanced"], 
            index=default_difficulty_idx
        )
    
    with col3:
        num_questions = st.number_input("🔢 Questions", min_value=5, max_value=20, value=10, key="quiz_num_questions")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
            if not topic:
                st.error("❌ Please enter a topic")
            else:
                with st.spinner("🤖 AI is generating quiz questions..."):
                    questions = generate_quiz_questions(topic, difficulty, num_questions)
                    
                    if questions and len(questions) > 0:
                        st.session_state.quiz_questions = questions
                        st.session_state.quiz_started = True
                        st.session_state.current_quiz_topic = topic
                        st.session_state.quiz_start_time = datetime.now()
                        st.session_state.user_answers = {}
                        st.session_state.quiz_submitted = False
                        st.success(f"✅ Generated {len(questions)} questions!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate quiz. Please try again.")
    
    # Show suggested topics with modern chip design
    st.markdown("---")
    st.markdown("### 💡 Quick Start - Suggested Topics")
    st.caption("Click any topic to instantly start a quiz")
    
    # Add CSS for modern chip buttons
    st.markdown("""
    <style>
    /* Suggested topic chip buttons */
    .stButton > button[data-testid*="suggested"] {
        background: linear-gradient(135deg, #667eea22 0%, #764ba244 100%) !important;
        border: 2px solid #667eea !important;
        border-radius: 20px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        height: auto !important;
        white-space: normal !important;
        text-align: center !important;
    }
    
    .stButton > button[data-testid*="suggested"]:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-color: #764ba2 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    suggested_topics = [
        ("🧠 Neural Networks", "Beginner"),
        ("🔄 Backpropagation", "Intermediate"),
        ("👁️ Computer Vision", "Intermediate"),
        ("💬 Natural Language Processing", "Advanced"),
        ("🎯 Optimization Algorithms", "Advanced"),
        ("📊 Data Preprocessing", "Beginner"),
    ]
    
    # Display in 3 columns
    cols = st.columns(3)
    for i, (topic_name, level) in enumerate(suggested_topics):
        with cols[i % 3]:
            # Create a more descriptive button label
            button_label = f"{topic_name}\n📊 {level}"
            
            if st.button(button_label, key=f"suggested_{i}", use_container_width=True):
                # Extract topic name (remove emoji)
                clean_topic = topic_name.split(" ", 1)[1]
                
                # Set session state to trigger quiz generation
                st.session_state.suggested_topic = clean_topic
                st.session_state.suggested_difficulty = level
                st.session_state.auto_generate_quiz = True  # Flag to auto-generate
                
                # Rerun to trigger auto-generation
                st.rerun()


def render_quiz_interface():
    """Render active quiz with dynamic questions"""
    topic = st.session_state.current_quiz_topic
    questions = st.session_state.quiz_questions
    
    if not questions:
        st.error("No questions available. Please generate a new quiz.")
        if st.button("← Back to Quiz Selection"):
            st.session_state.quiz_started = False
            st.rerun()
        return
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
            <h2 style="margin: 0; color: #667eea;">
                📝 {topic} Quiz
            </h2>
            <p style="margin: 5px 0 0 0; color: #b0b0b0;">
                {len(questions)} questions • {st.session_state.get('quiz_difficulty', 'Intermediate')} level
            </p>
        """, unsafe_allow_html=True)
    
    with col2:
        # Progress
        answered = len(st.session_state.user_answers)
        st.markdown(f"""
            <div style="
                background: #1e1e1e;
                padding: 15px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            ">
                <div style="font-size: 1.5em; font-weight: 700; color: #667eea;">
                    {answered}/{len(questions)}
                </div>
                <div style="font-size: 0.85em; color: #666;">Answered</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Progress bar
    progress = (answered / len(questions)) * 100 if questions else 0
    animated_progress_bar(progress, "Quiz Progress", "#667eea")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render questions
    for i, q in enumerate(questions, 1):
        with st.container():
            st.markdown(f"""
                <div style="
                    background: #1e1e1e;
                    padding: 25px;
                    border-radius: 15px;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: #fafafa;">Question {i}</h3>
                        <span style="
                            background: #667eea22;
                            color: #667eea;
                            padding: 4px 12px;
                            border-radius: 12px;
                            font-size: 0.85em;
                            font-weight: 600;
                        ">{q.get('difficulty', 'medium')}</span>
                    </div>
                    <p style="font-size: 1.1em; color: #fafafa; margin: 15px 0;">
                        {q['question']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Radio buttons for options - NO DEFAULT SELECTION
            answer = st.radio(
                "Select your answer:",
                q["options"],
                key=f"answer_{q['id']}",
                index=None,  # No default selection
                label_visibility="collapsed"
            )
            
            # Store answer if selected
            if answer is not None:
                st.session_state.user_answers[q['id']] = answer
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Check if all questions are answered
        all_answered = len(st.session_state.user_answers) == len(questions)
        
        if st.button("✅ Submit Quiz", type="primary", use_container_width=True, disabled=not all_answered):
            if all_answered:
                # Calculate score
                score_data = calculate_quiz_score(questions, st.session_state.user_answers)
                st.session_state.quiz_score = score_data
                st.session_state.quiz_submitted = True
                
                # Store in database
                add_quiz_attempt(
                    topic=topic,
                    score=score_data['score'],
                    max_score=score_data['max_score'],
                    time_taken=score_data['time_taken']
                )
                
                # Also save to learning_progress database
                if st.session_state.get("user_id"):
                    from utils.learning_progress import get_learning_db
                    from utils.advanced_features_db import get_advanced_db
                    
                    db = get_learning_db()
                    db.save_quiz_result(
                        st.session_state.user_id,
                        topic,
                        score_data['score'],
                        score_data['max_score'],
                        score_data['time_taken']
                    )
                    
                    # Update learning streak
                    advanced_db = get_advanced_db()
                    advanced_db.update_streak(st.session_state.user_id)
                
                st.rerun()
        
        if not all_answered:
            st.caption(f"⚠️ Answer all questions ({answered}/{len(questions)})")
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.quiz_questions = []
            st.session_state.user_answers = {}
            st.rerun()


def calculate_quiz_score(questions, user_answers):
    """Calculate quiz score based on correct answers"""
    score = 0
    max_score = len(questions)
    feedback = []
    
    for q in questions:
        qid = q['id']
        correct_answer = q['correct_answer']
        user_answer = user_answers.get(qid, "")
        
        is_correct = user_answer == correct_answer
        if is_correct:
            score += 1
        
        feedback.append({
            "question": q['question'],
            "correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "explanation": q.get('explanation', '')
        })
    
    # Calculate time taken
    start_time = st.session_state.get('quiz_start_time', datetime.now())
    time_taken = int((datetime.now() - start_time).total_seconds())
    
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    return {
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
        "time_taken": time_taken,
        "feedback": feedback
    }


def render_quiz_results():
    """Show quiz results with detailed feedback"""
    score_data = st.session_state.quiz_score
    percentage = score_data['percentage']
    
    # Result header
    if percentage >= 80:
        color = "#10b981"
        emoji = "🎉"
        message = "Excellent!"
    elif percentage >= 60:
        color = "#f59e0b"
        emoji = "👍"
        message = "Good Job!"
    else:
        color = "#ef4444"
        emoji = "📚"
        message = "Keep Learning!"
    
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {color}22 0%, {color}44 100%);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            margin: 20px 0;
            border: 2px solid {color};
        ">
            <div style="font-size: 5em; margin-bottom: 20px;">{emoji}</div>
            <h1 style="margin: 0 0 10px 0; color: {color}; font-size: 3em;">
                {percentage:.0f}%
            </h1>
            <h2 style="margin: 0; color: #fafafa;">{message}</h2>
            <p style="margin: 15px 0 0 0; color: #666; font-size: 1.1em;">
                Score: {score_data['score']}/{score_data['max_score']} • Time: {score_data['time_taken']//60}m {score_data['time_taken']%60}s
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Detailed feedback
    st.markdown("### 📊 Detailed Feedback")
    
    for i, item in enumerate(score_data['feedback'], 1):
        icon = "✅" if item["correct"] else "❌"
        color = "#10b981" if item["correct"] else "#ef4444"
        
        st.markdown(f"""
            <div style="
                background: #1e1e1e;
                padding: 20px;
                border-radius: 12px;
                margin: 15px 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                border-left: 4px solid {color};
            ">
                <h4 style="margin: 0 0 10px 0; color: #fafafa;">
                    {icon} Question {i}
                </h4>
                <p style="margin: 5px 0; color: #666; font-weight: 600;">
                    {item['question']}
                </p>
                <p style="margin: 10px 0 5px 0; color: #666;">
                    <strong>Your answer:</strong> {item['user_answer']}
                </p>
                <p style="margin: 5px 0; color: {color};">
                    <strong>Correct answer:</strong> {item['correct_answer']}
                </p>
                {f'<p style="margin: 10px 0 0 0; color: #666; font-style: italic;">{item["explanation"]}</p>' if item.get('explanation') else ''}
            </div>
        """, unsafe_allow_html=True)
    
    # Actions
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Take Another Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_started = False
            st.session_state.quiz_submitted = False
            st.session_state.quiz_questions = []
            st.session_state.user_answers = {}
            st.session_state.quiz_score = None
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/4_Analytics.py")
    
    with col3:
        if st.button("📚 Learn More", use_container_width=True):
            st.switch_page("pages/2_Learn.py")


def main():
    if not check_authentication():
        st.warning("⚠️ Please login to take quizzes")
        if st.button("🔐 Go to Login"):
            st.switch_page("Home.py")
        st.stop()
    
    init_quiz_state()
    
    st.markdown("# 📝 Dynamic Quiz Center")
    st.markdown("🤖 AI-Generated Questions • Real-Time Scoring • Personalized Learning")
    st.markdown("---")
    
    if st.session_state.quiz_submitted:
        render_quiz_results()
    elif st.session_state.quiz_started:
        render_quiz_interface()
    else:
        render_quiz_selector()


if __name__ == "__main__":
    main()
