"""
Settings Page - Application and Account Settings
Manage preferences, security, and notifications
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.profile_database import get_profile_db
from utils.auth_database import get_auth_db

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
apply_theme()
load_theme_css()
apply_sidebar_fix()


def render_account_settings(user_id: int, username: str, email: str):
    """Render account settings section"""
    st.markdown("### 👤 Account Settings")
    st.caption("Update your personal information")
    
    profile_db = get_profile_db()
    profile = profile_db.get_profile(user_id)
    
    # Load current data
    current_full_name = profile.get('full_name', username) if profile else username
    current_interests = profile.get('learning_interests', '') if profile else ''
    
    with st.form("account_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name",
                value=current_full_name,
                help="Your full name as it appears on your profile"
            )
        
        with col2:
            display_username = st.text_input(
                "Username",
                value=username,
                disabled=True,
                help="Username cannot be changed"
            )
        
        email_display = st.text_input(
            "Email",
            value=email,
            disabled=True,
            help="Email cannot be changed from settings"
        )
        
        learning_interests = st.text_area(
            "Learning Interests",
            value=current_interests,
            placeholder="e.g., Machine Learning, Deep Learning, NLP, Computer Vision",
            help="Comma-separated list of your learning interests",
            height=100
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("💾 Save Account Settings", use_container_width=True, type="primary"):
            # Update profile
            profile_data = {
                'username': username,
                'full_name': full_name,
                'learning_interests': learning_interests,
                'bio': profile.get('bio', '') if profile else '',
                'experience_level': profile.get('experience_level', 'Beginner') if profile else 'Beginner',
                'location': profile.get('location', '') if profile else '',
                'occupation': profile.get('occupation', '') if profile else '',
                'website': profile.get('website', '') if profile else ''
            }
            
            if profile_db.update_profile(user_id, profile_data):
                st.success("✅ Account settings saved successfully!")
                st.rerun()
            else:
                st.error("❌ Error saving account settings. Please try again.")


def render_password_settings(user_id: int):
    """Render password change section"""
    st.markdown("### 🔒 Change Password")
    st.caption("Update your account password")
    
    with st.form("password_change_form"):
        current_password = st.text_input(
            "Current Password",
            type="password",
            help="Enter your current password"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_password = st.text_input(
                "New Password",
                type="password",
                help="Enter your new password (min 6 characters)"
            )
        
        with col2:
            confirm_password = st.text_input(
                "Confirm New Password",
                type="password",
                help="Re-enter your new password"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("🔐 Update Password", use_container_width=True, type="primary"):
            # Validation
            if not current_password or not new_password or not confirm_password:
                st.error("❌ All fields are required")
            elif len(new_password) < 6:
                st.error("❌ New password must be at least 6 characters long")
            elif new_password != confirm_password:
                st.error("❌ New passwords do not match")
            else:
                # Use auth_db's change_password method
                auth_db = get_auth_db()
                success, message = auth_db.change_password(user_id, current_password, new_password)
                
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")


def render_preferences_settings(user_id: int):
    """Render application preferences section"""
    st.markdown("### 🎨 Application Preferences")
    st.caption("Customize your learning experience")
    
    profile_db = get_profile_db()
    settings = profile_db.get_settings(user_id)
    
    # Load current settings
    current_language = settings.get('language', 'English') if settings else 'English'
    current_difficulty = settings.get('default_difficulty', 'Intermediate') if settings else 'Intermediate'
    current_theme = settings.get('theme', 'Dark') if settings else 'Dark'
    
    with st.form("preferences_form"):
        st.markdown("#### 💻 Programming Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            preferred_language = st.selectbox(
                "Preferred Programming Language",
                ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript"],
                index=0,
                help="Default language for code examples"
            )
        
        with col2:
            learning_difficulty = st.selectbox(
                "Preferred Learning Difficulty",
                ["Beginner", "Intermediate", "Advanced", "Expert"],
                index=["Beginner", "Intermediate", "Advanced", "Expert"].index(current_difficulty) if current_difficulty in ["Beginner", "Intermediate", "Advanced", "Expert"] else 1,
                help="Default difficulty level for generated content"
            )
        
        st.markdown("#### 🎯 Learning Goals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            daily_goal = st.number_input(
                "Daily Learning Goal (minutes)",
                min_value=5,
                max_value=480,
                value=30,
                step=5,
                help="Target learning time per day"
            )
        
        with col2:
            weekly_goal = st.number_input(
                "Weekly Quiz Goal",
                min_value=1,
                max_value=50,
                value=5,
                step=1,
                help="Target number of quizzes per week"
            )
        
        st.markdown("#### 🌐 Interface Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            interface_language = st.selectbox(
                "Interface Language",
                ["English", "Spanish", "French", "German", "Chinese", "Japanese"],
                index=["English", "Spanish", "French", "German", "Chinese", "Japanese"].index(current_language) if current_language in ["English", "Spanish", "French", "German", "Chinese", "Japanese"] else 0,
                help="Language for the user interface"
            )
        
        with col2:
            theme_preference = st.selectbox(
                "Theme",
                ["Dark", "Light", "Auto"],
                index=["Dark", "Light", "Auto"].index(current_theme) if current_theme in ["Dark", "Light", "Auto"] else 0,
                help="Application theme preference"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("💾 Save Preferences", use_container_width=True, type="primary"):
            # Save preferences
            settings_data = {
                'theme': theme_preference,
                'language': interface_language,
                'default_difficulty': learning_difficulty,
                'email_notifications': settings.get('email_notifications', 1) if settings else 1,
                'learning_reminders': settings.get('learning_reminders', 1) if settings else 1,
                'weekly_summary': settings.get('weekly_summary', 1) if settings else 1,
                'achievement_alerts': settings.get('achievement_alerts', 1) if settings else 1
            }
            
            if profile_db.update_settings(user_id, settings_data):
                st.success("✅ Preferences saved successfully!")
                st.rerun()
            else:
                st.error("❌ Error saving preferences. Please try again.")


def render_notification_settings(user_id: int):
    """Render notification settings section"""
    st.markdown("### 🔔 Notification Settings")
    st.caption("Manage your notification preferences")
    
    profile_db = get_profile_db()
    settings = profile_db.get_settings(user_id)
    
    # Load current settings
    current_email_notifs = bool(settings.get('email_notifications', 1)) if settings else True
    current_reminders = bool(settings.get('learning_reminders', 1)) if settings else True
    current_weekly = bool(settings.get('weekly_summary', 1)) if settings else True
    current_achievements = bool(settings.get('achievement_alerts', 1)) if settings else True
    
    with st.form("notification_settings_form"):
        st.markdown("#### 📧 Email Notifications")
        
        email_notifications = st.checkbox(
            "Enable Email Notifications",
            value=current_email_notifs,
            help="Receive notifications via email"
        )
        
        st.markdown("#### ⏰ Reminders")
        
        col1, col2 = st.columns(2)
        
        with col1:
            quiz_reminders = st.checkbox(
                "Quiz Reminders",
                value=current_reminders,
                help="Get reminded to take quizzes"
            )
            
            roadmap_reminders = st.checkbox(
                "Roadmap Progress Reminders",
                value=current_reminders,
                help="Get reminded about roadmap tasks"
            )
        
        with col2:
            learning_reminders = st.checkbox(
                "Daily Learning Reminders",
                value=current_reminders,
                help="Daily reminders to continue learning"
            )
            
            streak_reminders = st.checkbox(
                "Streak Alerts",
                value=current_reminders,
                help="Alerts when your streak is about to break"
            )
        
        st.markdown("#### 📊 Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            weekly_summary = st.checkbox(
                "Weekly Learning Summary",
                value=current_weekly,
                help="Receive weekly progress reports"
            )
        
        with col2:
            achievement_alerts = st.checkbox(
                "Achievement Alerts",
                value=current_achievements,
                help="Get notified when you unlock achievements"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("💾 Save Notification Settings", use_container_width=True, type="primary"):
            # Save notification settings
            settings_data = {
                'theme': settings.get('theme', 'Dark') if settings else 'Dark',
                'language': settings.get('language', 'English') if settings else 'English',
                'default_difficulty': settings.get('default_difficulty', 'Intermediate') if settings else 'Intermediate',
                'email_notifications': 1 if email_notifications else 0,
                'learning_reminders': 1 if learning_reminders else 0,
                'weekly_summary': 1 if weekly_summary else 0,
                'achievement_alerts': 1 if achievement_alerts else 0
            }
            
            if profile_db.update_settings(user_id, settings_data):
                st.success("✅ Notification settings saved successfully!")
                st.rerun()
            else:
                st.error("❌ Error saving notification settings. Please try again.")


def render_security_settings(user_id: int):
    """Render security settings section"""
    st.markdown("### 🛡️ Security Settings")
    st.caption("Manage your account security")
    
    st.markdown("#### 🔐 Two-Factor Authentication")
    st.info("Two-factor authentication is coming soon!")
    
    st.markdown("#### 📱 Active Sessions")
    st.markdown("""
        <div style="
            background: #1e1e1e;
            padding: 20px;
            border-radius: 12px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        ">
            <h4 style="margin: 0 0 10px 0; color: #667eea;">Current Session</h4>
            <p style="margin: 5px 0; color: #fafafa;">
                <strong>Device:</strong> Web Browser
            </p>
            <p style="margin: 5px 0; color: #fafafa;">
                <strong>Location:</strong> Current Location
            </p>
            <p style="margin: 5px 0; color: #fafafa;">
                <strong>Last Active:</strong> Just now
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### ⚠️ Danger Zone")
    
    with st.expander("🗑️ Delete Account", expanded=False):
        st.warning("⚠️ This action cannot be undone. All your data will be permanently deleted.")
        
        confirm_text = st.text_input(
            "Type 'DELETE' to confirm",
            key="delete_confirm"
        )
        
        if st.button("🗑️ Delete My Account", type="secondary"):
            if confirm_text == "DELETE":
                st.error("Account deletion is currently disabled. Please contact support.")
            else:
                st.error("Please type 'DELETE' to confirm")


def main():
    if not check_authentication():
        st.warning("Please login to access settings")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()
    
    # Get user info
    user_id = st.session_state.get("user_id")
    username = st.session_state.get("username", "User")
    email = st.session_state.get("email", "user@example.com")
    
    # Initialize profile if needed
    profile_db = get_profile_db()
    profile_db.create_profile(user_id, username)
    profile_db.create_default_settings(user_id)
    
    st.markdown("# ⚙️ Settings")
    st.markdown("Manage your account and application preferences")
    st.markdown("---")
    
    # Create tabs for different settings sections
    tabs = st.tabs([
        "👤 Account",
        "🎨 Preferences",
        "🔔 Notifications",
        "🛡️ Security"
    ])
    
    with tabs[0]:
        render_account_settings(user_id, username, email)
        st.markdown("---")
        render_password_settings(user_id)
    
    with tabs[1]:
        render_preferences_settings(user_id)
    
    with tabs[2]:
        render_notification_settings(user_id)
    
    with tabs[3]:
        render_security_settings(user_id)


if __name__ == "__main__":
    main()
