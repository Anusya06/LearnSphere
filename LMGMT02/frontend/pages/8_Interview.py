"""
Interview Preparation Page - Technical Interview Practice
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import time

sys.path.append(str(Path(__file__).parent.parent))

from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.interview_prep import get_interview_system

st.set_page_config(
    page_title="Interview Prep",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
load_theme_css()
apply_sidebar_fix()


def init_session_state():
    """Initialize session state"""
    if "interview_questions" not in st.session_state:
        st.session_state.interview_questions = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False
    if "practice_mode" not in st.session_state:
        st.session_state.practice_mode = False
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = None


def render_question_generator():
    """Render question generation interface"""
    st.markdown("### 🎯 Generate Interview Questions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        topic = st.text_input(
            "Topic",
            placeholder="e.g., Python, Machine Learning, System Design",
            key="interview_topic"
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            ["Entry Level", "Mid Level", "Senior Level"],
            key="interview_difficulty"
        )
    
    with col3:
        count = st.number_input(
            "Number of Questions",
            min_value=3,
            max_value=10,
            value=5,
            key="question_count"
        )
    
    if st.button("🚀 Generate Questions", use_container_width=True, type="primary"):
        if not topic:
            st.error("Please enter a topic")
        else:
            with st.spinner("🤖 AI is preparing interview questions..."):
                interview_system = get_interview_system()
                questions = interview_system.generate_questions(topic, difficulty, count)
                
                if questions:
                    # Save to database
                    question_ids = interview_system.save_questions(topic, difficulty, questions)
                    
                    # Add IDs to questions
                    for i, qid in enumerate(question_ids):
                        questions[i]['id'] = qid
                    
                    # Set session state
                    st.session_state.interview_questions = questions
                    st.session_state.current_question_index = 0
                    st.session_state.user_answers = {}
                    st.session_state.show_answer = False
                    st.session_state.practice_mode = True
                    
                    # Start practice session
                    if st.session_state.get("user_id"):
                        session_id = interview_system.start_practice_session(
                            st.session_state.user_id,
                            topic,
                            len(questions)
                        )
                        st.session_state.session_id = session_id
                        st.session_state.session_start_time = datetime.now()
                    
                    st.success(f"✅ Generated {len(questions)} questions!")
                    st.rerun()
                else:
                    st.error("Failed to generate questions. Please try again.")


def render_practice_interface():
    """Render practice mode interface"""
    questions = st.session_state.interview_questions
    current_idx = st.session_state.current_question_index
    
    if not questions or current_idx >= len(questions):
        st.info("Generate questions to start practicing!")
        return
    
    current_question = questions[current_idx]
    
    # Progress bar
    progress = (current_idx + 1) / len(questions)
    st.progress(progress)
    st.caption(f"Question {current_idx + 1} of {len(questions)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Question type badge
    type_colors = {
        "Concept": "#667eea",
        "Coding": "#10b981",
        "System Design": "#f59e0b",
        "Behavioral": "#8b5cf6"
    }
    
    q_type = current_question.get('question_type', 'Concept')
    color = type_colors.get(q_type, "#667eea")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"## Question {current_idx + 1}")
    
    with col2:
        st.markdown(f"""
            <div style="
                background: {color}22;
                border: 2px solid {color};
                padding: 8px 16px;
                border-radius: 10px;
                text-align: center;
                color: {color};
                font-weight: 600;
            ">
                {q_type}
            </div>
        """, unsafe_allow_html=True)
    
    # Question text
    st.markdown(f"""
        <div style="
            background: #1e1e1e;
            padding: 25px;
            border-radius: 15px;
            border-left: 4px solid {color};
            font-size: 1.1em;
            line-height: 1.8;
            margin: 20px 0;
        ">
            {current_question['question']}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # User answer input
    st.markdown("### ✍️ Your Answer")
    
    user_answer = st.text_area(
        "Type your answer here",
        value=st.session_state.user_answers.get(current_idx, ""),
        height=200,
        key=f"answer_{current_idx}",
        placeholder="Think through the problem and write your answer..."
    )
    
    st.session_state.user_answers[current_idx] = user_answer
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action buttons
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if not st.session_state.show_answer:
            if st.button("💡 Show Answer", use_container_width=True, type="primary"):
                st.session_state.show_answer = True
                st.rerun()
        else:
            if st.button("🙈 Hide Answer", use_container_width=True):
                st.session_state.show_answer = False
                st.rerun()
    
    with col_b:
        if current_idx > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_question_index -= 1
                st.session_state.show_answer = False
                st.rerun()
    
    with col_c:
        if current_idx < len(questions) - 1:
            if st.button("➡️ Next", use_container_width=True):
                st.session_state.current_question_index += 1
                st.session_state.show_answer = False
                st.rerun()
        else:
            if st.button("✅ Finish", use_container_width=True, type="primary"):
                # Complete session
                if st.session_state.session_id and st.session_state.session_start_time:
                    duration = int((datetime.now() - st.session_state.session_start_time).total_seconds() / 60)
                    answered_count = len([a for a in st.session_state.user_answers.values() if a.strip()])
                    
                    interview_system = get_interview_system()
                    interview_system.complete_practice_session(
                        st.session_state.session_id,
                        answered_count,
                        duration
                    )
                
                st.success("🎉 Practice session completed!")
                st.balloons()
                
                # Reset
                st.session_state.practice_mode = False
                st.session_state.interview_questions = []
                st.session_state.current_question_index = 0
                st.session_state.user_answers = {}
                
                time.sleep(2)
                st.rerun()
    
    # Show answer section
    if st.session_state.show_answer:
        st.markdown("---")
        st.markdown("### ✅ Model Answer")
        
        st.markdown(f"""
            <div style="
                background: rgba(16, 185, 129, 0.1);
                padding: 20px;
                border-radius: 12px;
                border-left: 4px solid #10b981;
                line-height: 1.8;
            ">
                {current_question['answer']}
            </div>
        """, unsafe_allow_html=True)
        
        # Hints
        if current_question.get('hints'):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 💡 Key Points")
            
            for hint in current_question['hints']:
                st.markdown(f"""
                    <div style="
                        background: rgba(102, 126, 234, 0.1);
                        padding: 12px;
                        border-radius: 8px;
                        margin: 8px 0;
                        border-left: 3px solid #667eea;
                    ">
                        • {hint}
                    </div>
                """, unsafe_allow_html=True)
        
        # Follow-up questions
        if current_question.get('follow_ups'):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🔄 Follow-up Questions")
            
            for i, follow_up in enumerate(current_question['follow_ups'], 1):
                st.markdown(f"""
                    <div style="
                        background: rgba(245, 158, 11, 0.1);
                        padding: 12px;
                        border-radius: 8px;
                        margin: 8px 0;
                        border-left: 3px solid #f59e0b;
                    ">
                        <strong style="color: #f59e0b;">{i}.</strong> {follow_up}
                    </div>
                """, unsafe_allow_html=True)


def render_user_stats():
    """Render user statistics"""
    if not st.session_state.get("user_id"):
        return
    
    st.markdown("### 📊 Your Progress")
    
    interview_system = get_interview_system()
    stats = interview_system.get_user_stats(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sessions", stats['total_sessions'])
    
    with col2:
        st.metric("Questions", stats['total_answered'])
    
    with col3:
        st.metric("Accuracy", f"{stats['accuracy']:.0f}%")
    
    with col4:
        hours = stats['total_time_minutes'] / 60
        st.metric("Study Time", f"{hours:.1f}h")
    
    # Recent sessions
    if stats['total_sessions'] > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📅 Recent Sessions")
        
        recent = interview_system.get_recent_sessions(st.session_state.user_id, limit=5)
        
        for session in recent:
            score_pct = (session['correct_answers'] / session['questions_count'] * 100) if session['questions_count'] > 0 else 0
            color = "#10b981" if score_pct >= 70 else "#f59e0b"
            
            st.markdown(f"""
                <div style="
                    background: #1e1e1e;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    border-left: 4px solid {color};
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #fafafa;">{session['topic']}</strong><br>
                            <span style="color: #b0b0b0; font-size: 0.9em;">
                                {session['correct_answers']}/{session['questions_count']} answered • 
                                {session['duration_minutes']} min
                            </span>
                        </div>
                        <span style="color: {color}; font-weight: 600; font-size: 1.2em;">
                            {score_pct:.0f}%
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)


def main():
    if not check_authentication():
        st.warning("Please login to access interview preparation")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()
    
    init_session_state()
    
    # Header
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <h1 style="color: white; margin: 0;">🎤 Interview Preparation</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;">
                Practice technical interview questions with AI
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # User stats
    render_user_stats()
    
    st.markdown("---")
    
    # Main content
    if st.session_state.practice_mode:
        render_practice_interface()
    else:
        render_question_generator()


if __name__ == "__main__":
    main()
