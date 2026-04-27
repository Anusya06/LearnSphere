"""
Authentication components with persistent database
"""
import streamlit as st
import requests
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.auth_database import get_auth_db

API_BASE_URL = "http://localhost:8000"


def check_authentication() -> bool:
    """Check if user is authenticated"""
    # Check both flags for compatibility
    return st.session_state.get("authenticated", False) or st.session_state.get("logged_in", False)


def login_page():
    """Modern login/register page"""
    
    st.markdown("""
        <div style="
            text-align: center;
            padding: 3rem 0 2rem 0;
        ">
            <h1 style="
                font-size: 3.5em;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
            ">🎓 LearnSphere Pro</h1>
            <p style="
                color: #666;
                font-size: 1.3em;
                margin: 15px 0 0 0;
            ">AI-Powered Learning Platform</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            render_login_form()
        
        with tab2:
            render_register_form()


def render_login_form():
    """Render login form with persistent database"""
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="your@email.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
        
        if submit:
            if not email or not password:
                st.error("❌ Please fill in all fields")
            else:
                # Authenticate with persistent database
                db = get_auth_db()
                success, message, user_data = db.authenticate_user(email, password)
                
                if success:
                    # Set session state - use BOTH flags for compatibility
                    st.session_state.authenticated = True
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_data['id']
                    st.session_state.username = user_data['username']
                    st.session_state.email = user_data['email']
                    st.session_state.full_name = user_data.get('full_name', '')
                    st.session_state.profile_picture = user_data.get('profile_picture', '')
                    st.session_state.theme = user_data.get('theme_preference', 'light')
                    
                    st.success(f"✅ {message}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


def render_register_form():
    """Render registration form with persistent database"""
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("register_form"):
        username = st.text_input("👤 Username", placeholder="Choose a username")
        email = st.text_input("📧 Email", placeholder="your@email.com")
        full_name = st.text_input("✏️ Full Name", placeholder="Your full name (optional)")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a password (min 6 characters)")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        
        # Optional profile picture upload
        st.markdown("**📸 Profile Picture (optional)**")
        uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("📝 Create Account", use_container_width=True, type="primary")
        
        if submit:
            if not all([username, email, password, confirm_password]):
                st.error("❌ Please fill in all required fields")
            elif password != confirm_password:
                st.error("❌ Passwords don't match")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters")
            elif not validate_email(email):
                st.error("❌ Please enter a valid email address")
            else:
                # Create user in persistent database
                db = get_auth_db()
                
                # Handle profile picture if uploaded
                profile_picture = None
                if uploaded_file:
                    # For now, use default avatar (file upload can be implemented later)
                    profile_picture = f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
                
                success, message, user_data = db.create_user(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name if full_name else None,
                    profile_picture=profile_picture
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.info("🎉 You can now login with your credentials!")
                    
                    # Auto-login after successful registration
                    st.session_state.authenticated = True
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_data['id']
                    st.session_state.username = user_data['username']
                    st.session_state.email = user_data['email']
                    st.session_state.full_name = user_data.get('full_name', '')
                    st.session_state.profile_picture = user_data.get('profile_picture', '')
                    st.session_state.theme = user_data.get('theme_preference', 'light')
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def logout_user():
    """Logout current user"""
    # Clear all session state
    keys_to_keep = []  # Keep nothing, full logout
    keys_to_clear = [key for key in st.session_state.keys() if key not in keys_to_keep]
    
    for key in keys_to_clear:
        del st.session_state[key]
    
    # Reset authentication - use BOTH flags
    st.session_state.authenticated = False
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.email = None
