"""
Coding Challenges Page - Interactive Code Editor with AI Problems
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
from utils.coding_challenges import get_coding_system
from utils.code_executor import CodeExecutor

st.set_page_config(
    page_title="Coding Challenges",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
load_theme_css()
apply_sidebar_fix()


def init_session_state():
    """Initialize session state"""
    if "current_challenge" not in st.session_state:
        st.session_state.current_challenge = None
    if "user_code" not in st.session_state:
        st.session_state.user_code = ""
    if "show_hints" not in st.session_state:
        st.session_state.show_hints = False
    if "show_solution" not in st.session_state:
        st.session_state.show_solution = False
    if "test_results" not in st.session_state:
        st.session_state.test_results = None


def render_challenge_generator():
    """Render challenge generation interface"""
    st.markdown("### 🎯 Generate New Challenge")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        topic = st.text_input(
            "Topic",
            placeholder="e.g., Arrays, Strings, Trees",
            key="challenge_topic"
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            key="challenge_difficulty"
        )
    
    with col3:
        language = st.selectbox(
            "Language",
            ["Python", "JavaScript", "Java", "C++", "C", "C#", "Go", "Ruby", "PHP", "Swift", "Kotlin", "Rust", "TypeScript"],
            key="challenge_language",
            help="✅ All languages supported via cloud execution"
        )
    
    # Language support notice
    st.info("✅ All languages support full code execution and testing!")
    
    if st.button("🚀 Generate Challenge", use_container_width=True, type="primary"):
        if not topic:
            st.error("Please enter a topic")
        else:
            # Create placeholder for status messages
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            try:
                # Show initial loading message
                status_placeholder.info("🤖 AI is creating your coding challenge...")
                progress_bar.progress(20)
                
                coding_system = get_coding_system()
                
                # Update progress
                progress_bar.progress(40)
                status_placeholder.info("⚙️ Generating challenge structure...")
                
                # Generate challenge (with retry logic built-in)
                challenge = coding_system.generate_challenge(topic, difficulty, language)
                
                progress_bar.progress(80)
                
                if challenge:
                    # Save to database
                    status_placeholder.info("💾 Saving challenge...")
                    challenge_id = coding_system.save_challenge(challenge)
                    challenge['id'] = challenge_id
                    
                    progress_bar.progress(100)
                    
                    # Set as current challenge
                    st.session_state.current_challenge = challenge
                    st.session_state.user_code = challenge['starter_code']
                    st.session_state.show_hints = False
                    st.session_state.show_solution = False
                    st.session_state.test_results = None
                    
                    status_placeholder.success("✅ Challenge generated successfully!")
                    time.sleep(0.5)  # Brief pause to show success message
                    st.rerun()
                else:
                    # This should rarely happen now due to fallback
                    progress_bar.empty()
                    status_placeholder.error("❌ Unable to generate challenge. Please check your API key and try again.")
                    
            except Exception as e:
                progress_bar.empty()
                status_placeholder.error(f"❌ An error occurred: {str(e)}")
                print(f"Challenge generation error: {e}")


def render_challenge_interface():
    """Render active challenge interface"""
    challenge = st.session_state.current_challenge
    
    if not challenge:
        st.info("Generate a challenge to start coding!")
        return
    
    # Challenge header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"## 💻 {challenge['title']}")
    
    with col2:
        difficulty_colors = {
            "Easy": "#10b981",
            "Medium": "#f59e0b",
            "Hard": "#ef4444"
        }
        color = difficulty_colors.get(challenge['difficulty'], "#667eea")
        
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
                {challenge['difficulty']}
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="
                background: #667eea22;
                border: 2px solid #667eea;
                padding: 8px 16px;
                border-radius: 10px;
                text-align: center;
                color: #667eea;
                font-weight: 600;
            ">
                {challenge['language']}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Two-column layout
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        # Problem description
        st.markdown("### 📋 Problem Description")
        st.markdown(f"""
            <div style="
                background: #1e1e1e;
                padding: 20px;
                border-radius: 12px;
                border-left: 4px solid #667eea;
                line-height: 1.8;
            ">
                {challenge['description']}
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Hints section
        st.markdown("### 💡 Hints")
        
        if not st.session_state.show_hints:
            if st.button("🔓 Show Hints", use_container_width=True):
                st.session_state.show_hints = True
                st.rerun()
        else:
            for i, hint in enumerate(challenge['hints'], 1):
                st.markdown(f"""
                    <div style="
                        background: rgba(16, 185, 129, 0.1);
                        padding: 12px;
                        border-radius: 8px;
                        margin: 8px 0;
                        border-left: 3px solid #10b981;
                    ">
                        <strong style="color: #10b981;">Hint {i}:</strong> {hint}
                    </div>
                """, unsafe_allow_html=True)
            
            if st.button("🔒 Hide Hints", use_container_width=True):
                st.session_state.show_hints = False
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Solution section
        st.markdown("### 🎯 Solution")
        
        if not st.session_state.show_solution:
            if st.button("👁️ Show Solution", use_container_width=True):
                st.session_state.show_solution = True
                st.rerun()
        else:
            st.code(challenge['solution_code'], language=challenge['language'].lower())
            
            if st.button("🙈 Hide Solution", use_container_width=True):
                st.session_state.show_solution = False
                st.rerun()
    
    with col_right:
        # Code editor
        st.markdown("### ✏️ Your Code")
        
        # Language indicator
        lang_color = "#10b981"  # Green for all supported languages
        lang_icon = "✅"
        lang_msg = "Execution Supported"
        
        st.markdown(f"""
            <div style="
                background: {lang_color}22;
                border: 2px solid {lang_color};
                padding: 10px 15px;
                border-radius: 10px;
                margin-bottom: 15px;
                text-align: center;
            ">
                <strong style="color: {lang_color};">{lang_icon} {challenge['language']}</strong>
                <span style="color: rgba(255,255,255,0.8); margin-left: 10px;">• {lang_msg}</span>
            </div>
        """, unsafe_allow_html=True)
        
        user_code = st.text_area(
            "Write your solution",
            value=st.session_state.user_code,
            height=400,
            key="code_editor",
            label_visibility="collapsed"
        )
        
        st.session_state.user_code = user_code
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Action buttons
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            # All languages now supported
            if st.button("▶️ Run Tests", use_container_width=True, type="primary"):
                if not user_code.strip():
                    st.error("Please write some code first!")
                else:
                    with st.spinner("Running tests..."):
                        coding_system = get_coding_system()
                        
                        # Pass expected function name if available
                        expected_func = challenge.get('expected_function')
                        
                        results = coding_system.validate_code(
                            user_code,
                            challenge['test_cases'],
                            challenge['language'],
                            expected_func
                        )
                        
                        st.session_state.test_results = results
                        
                        # Save submission
                        if st.session_state.get("user_id"):
                            coding_system.submit_solution(
                                st.session_state.user_id,
                                challenge['id'],
                                user_code,
                                results['passed']
                            )
                        
                        st.rerun()
        
        with col_b:
            if st.button("🔄 Reset Code", use_container_width=True):
                st.session_state.user_code = challenge['starter_code']
                st.session_state.test_results = None
                st.rerun()
        
        with col_c:
            if st.button("🆕 New Challenge", use_container_width=True):
                st.session_state.current_challenge = None
                st.session_state.user_code = ""
                st.session_state.test_results = None
                st.rerun()
        
        # Test results
        if st.session_state.test_results:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📊 Test Results")
            
            results = st.session_state.test_results
            
            if results['passed']:
                st.success(f"✅ {results['message']}")
                st.balloons()
            else:
                st.error(f"❌ {results['message']}")
            
            # Show individual test results
            for test_result in results.get('results', []):
                if test_result.get('passed'):
                    st.markdown(f"""
                        <div style="
                            background: rgba(16, 185, 129, 0.1);
                            padding: 12px;
                            border-radius: 8px;
                            margin: 8px 0;
                            border-left: 3px solid #10b981;
                        ">
                            <strong style="color: #10b981;">✅ Test {test_result['test']} Passed</strong><br>
                            Input: {test_result['input']}<br>
                            Expected: {test_result['expected']}<br>
                            Got: {test_result['got']}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    error_msg = test_result.get('error', 'Wrong output')
                    st.markdown(f"""
                        <div style="
                            background: rgba(239, 68, 68, 0.1);
                            padding: 12px;
                            border-radius: 8px;
                            margin: 8px 0;
                            border-left: 3px solid #ef4444;
                        ">
                            <strong style="color: #ef4444;">❌ Test {test_result['test']} Failed</strong><br>
                            Input: {test_result['input']}<br>
                            {f"Expected: {test_result.get('expected', 'N/A')}<br>" if 'expected' in test_result else ''}
                            {f"Got: {test_result.get('got', 'N/A')}<br>" if 'got' in test_result else ''}
                            {f"Error: {error_msg}" if 'error' in test_result else ''}
                        </div>
                    """, unsafe_allow_html=True)


def render_user_stats():
    """Render user statistics"""
    if not st.session_state.get("user_id"):
        return
    
    st.markdown("### 📊 Your Progress")
    
    coding_system = get_coding_system()
    stats = coding_system.get_user_stats(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Completed", stats['completed'])
    
    with col2:
        st.metric("Easy", stats['easy'], delta=None)
    
    with col3:
        st.metric("Medium", stats['medium'], delta=None)
    
    with col4:
        st.metric("Hard", stats['hard'], delta=None)


def main():
    if not check_authentication():
        st.warning("Please login to access coding challenges")
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
            <h1 style="color: white; margin: 0;">💻 Coding Challenges</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;">
                Practice coding with AI-generated problems
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # User stats
    render_user_stats()
    
    st.markdown("---")
    
    # Main content
    if st.session_state.current_challenge:
        render_challenge_interface()
    else:
        render_challenge_generator()


if __name__ == "__main__":
    main()
