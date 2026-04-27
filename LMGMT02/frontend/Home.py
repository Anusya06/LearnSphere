"""
LearnSphere Pro - Main Entry Point
Modern AI-Powered Learning Management System
"""
import streamlit as st
import sys
from pathlib import Path

# Add components to path
sys.path.append(str(Path(__file__).parent))

from components.ui_components import gradient_card, stat_card, animated_progress_bar
from components.auth_components import check_authentication, login_page, logout_user
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix


# Page config
st.set_page_config(
    page_title="LearnSphere Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"  # Keep sidebar expanded by default
)

# Apply global theme
apply_theme()
load_theme_css()
apply_sidebar_fix()  # Fix sidebar navigation

# Add layout fix CSS
st.markdown("""
<style>
/* ========================================
   LAYOUT FIX - CENTER CONTENT PROPERLY
   ======================================== */

/* Ensure main content is centered and properly spaced */
.main .block-container {
    max-width: 1400px !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    padding-top: 2rem !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* Fix column alignment */
[data-testid="column"] {
    padding: 0.5rem !important;
}

/* Ensure proper spacing for all elements */
.element-container {
    margin-bottom: 1rem;
}

/* Center hero header */
.hero-header {
    text-align: center;
    margin: 0 auto;
    max-width: 100%;
}

/* Responsive grid for cards */
.stColumns {
    gap: 1.5rem !important;
}

/* Ensure buttons and interactive elements are properly sized */
.stButton > button {
    width: 100%;
}

/* Fix any overflow issues */
.main {
    overflow-x: hidden;
}

/* Responsive design */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables with persistence"""
    defaults = {
        "authenticated": False,
        "user_id": None,
        "username": None,
        "email": None,
        "theme": "light",
        "current_topic": None,
        "current_page": "home",  # Track current page
        "logged_in": False,  # Additional flag for compatibility
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Sync authenticated and logged_in states
    if st.session_state.authenticated:
        st.session_state.logged_in = True


def render_header():
    """Render modern header"""
    st.markdown("""
        <div style="
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        ">
            <h1 style="
                color: white;
                font-size: 3em;
                margin: 0;
                font-weight: 800;
                letter-spacing: -1px;
            ">🎓 LearnSphere Pro</h1>
            <p style="
                color: rgba(255,255,255,0.9);
                font-size: 1.2em;
                margin: 10px 0 0 0;
                font-weight: 500;
            ">Next-Gen AI-Powered Learning Platform</p>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render simple sidebar with logout button"""
    with st.sidebar:
        if st.session_state.authenticated:
            # Simple user info
            st.markdown(f"### 👤 {st.session_state.username}")
            st.caption(st.session_state.email)
            st.markdown("---")
            
            # Logout Button
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                logout_user()
                st.rerun()


def home_page():
    """Main home page content"""
    render_header()
    
    # Hero section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        gradient_card(
            title="Welcome to LearnSphere Pro",
            content="Experience the future of learning with AI-powered personalized education. "
                   "Master machine learning concepts through interactive lessons, adaptive quizzes, "
                   "and real-time AI tutoring.",
            icon="🚀",
            gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        )
        
        st.markdown("### ✨ Key Features")
        
        features = [
            ("🤖", "AI-Generated Content", "Personalized learning materials tailored to your level"),
            ("📊", "Advanced Analytics", "Track your progress with detailed insights"),
            ("💬", "AI Tutor Chat", "Get instant help from your personal AI tutor"),
            ("🎯", "Adaptive Quizzes", "Smart assessments that adapt to your skill level"),
            ("📱", "Responsive Design", "Learn anywhere on any device"),
            ("🏆", "Gamification", "Earn badges and maintain learning streaks"),
        ]
        
        cols = st.columns(2)
        for i, (icon, title, desc) in enumerate(features):
            with cols[i % 2]:
                st.markdown(f"""
                    <div class="feature-card" style="
                        background: var(--card-bg, #f5f5f5);
                        color: var(--text-primary, #111111);
                        padding: 20px;
                        border-radius: 15px;
                        margin: 10px 0;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                        transition: transform 0.3s ease;
                        border: 1px solid var(--border-color, #e0e0e0);
                    " onmouseover="this.style.transform='translateY(-5px)'"
                       onmouseout="this.style.transform='translateY(0)'">
                        <h4 style="margin: 0 0 10px 0; color: #667eea;">
                            <span style="font-size: 1.5em;">{icon}</span> {title}
                        </h4>
                        <p style="margin: 0; color: var(--text-secondary, #666); font-size: 0.9em;">{desc}</p>
                    </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📈 Platform Stats")
        
        stat_card("10K+", "Active Learners", "👥", "#667eea")
        st.markdown("<br>", unsafe_allow_html=True)
        
        stat_card("500+", "AI-Generated Topics", "📚", "#764ba2")
        st.markdown("<br>", unsafe_allow_html=True)
        
        stat_card("95%", "Success Rate", "🎯", "#10b981")
        st.markdown("<br>", unsafe_allow_html=True)
        
        stat_card("24/7", "AI Tutor Support", "💬", "#f59e0b")
    
    # CTA Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        ">
            <h2 style="margin: 0 0 15px 0; font-size: 2.5em;">Ready to Start Learning?</h2>
            <p style="margin: 0 0 25px 0; font-size: 1.2em; opacity: 0.9;">
                Join thousands of learners mastering ML with AI-powered education
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started Now", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Learn.py")


def main():
    """Main application entry point"""
    init_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
    else:
        render_sidebar()
        home_page()


if __name__ == "__main__":
    main()
