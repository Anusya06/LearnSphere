"""
Dynamic Profile Page - User settings, achievements, and statistics
All data is saved to database and persists across sessions
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import base64

sys.path.append(str(Path(__file__).parent.parent))

from components.ui_components import gradient_card, stat_card
from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.profile_database import get_profile_db
from utils.learning_progress import get_learning_db
from utils.advanced_features_db import get_advanced_db

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide", initial_sidebar_state="expanded")
apply_theme()
load_theme_css()
apply_sidebar_fix()


def check_and_award_badges(user_id: int):
    """Check conditions and award badges automatically"""
    advanced_db = get_advanced_db()
    learning_db = get_learning_db()
    profile_db = get_profile_db()
    
    # Get statistics
    stats = profile_db.get_profile_statistics(user_id)
    streak = advanced_db.get_streak(user_id)
    bookmarks = advanced_db.get_bookmarks(user_id)
    
    # First Topic Badge
    if stats['topics_learned'] >= 1 and not advanced_db.has_badge(user_id, "First Topic"):
        advanced_db.award_badge(user_id, "First Topic", "Generated your first learning topic")
    
    # Explorer Badge
    if stats['topics_learned'] >= 10 and not advanced_db.has_badge(user_id, "Explorer"):
        advanced_db.award_badge(user_id, "Explorer", "Learned 10 different topics")
    
    # Quiz Master Badge
    if stats['average_score'] >= 80 and not advanced_db.has_badge(user_id, "Quiz Master"):
        advanced_db.award_badge(user_id, "Quiz Master", "Achieved 80%+ average quiz score")
    
    # Perfectionist Badge
    if stats['average_score'] >= 100 and not advanced_db.has_badge(user_id, "Perfectionist"):
        advanced_db.award_badge(user_id, "Perfectionist", "Scored 100% on a quiz")
    
    # Consistent Learner Badge (7-day streak)
    if streak >= 7 and not advanced_db.has_badge(user_id, "Consistent Learner"):
        advanced_db.award_badge(user_id, "Consistent Learner", "Maintained a 7-day learning streak")
    
    # Dedicated Badge (30-day streak)
    if streak >= 30 and not advanced_db.has_badge(user_id, "Dedicated"):
        advanced_db.award_badge(user_id, "Dedicated", "Achieved a 30-day learning streak")
    
    # Bookworm Badge
    if len(bookmarks) >= 5 and not advanced_db.has_badge(user_id, "Bookworm"):
        advanced_db.award_badge(user_id, "Bookworm", "Saved 5 topics as bookmarks")
    
    # Task Master Badge
    if stats['tasks_completed'] >= 20 and not advanced_db.has_badge(user_id, "Task Master"):
        advanced_db.award_badge(user_id, "Task Master", "Completed 20 roadmap tasks")


def init_user_profile(user_id: int, username: str):
    """Initialize profile and settings for new user"""
    profile_db = get_profile_db()
    
    # Create profile if doesn't exist
    profile_db.create_profile(user_id, username)
    
    # Create default settings if don't exist
    profile_db.create_default_settings(user_id)


def render_profile_header(user_id: int, username: str, email: str):
    """Render profile header with picture and basic info"""
    profile_db = get_profile_db()
    profile = profile_db.get_profile(user_id)
    
    # Get profile data
    full_name = profile.get('full_name', username) if profile else username
    bio = profile.get('bio', '') if profile else ''
    experience_level = profile.get('experience_level', 'Beginner') if profile else 'Beginner'
    
    # Profile picture
    profile_pic = profile_db.get_profile_picture(user_id) if profile else None
    
    if profile_pic:
        # Display uploaded picture
        pic_base64 = base64.b64encode(profile_pic).decode()
        pic_src = f"data:image/png;base64,{pic_base64}"
    else:
        # Default avatar
        pic_src = f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
    
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        ">
            <img src="{pic_src}" 
                 style="
                     width: 120px;
                     height: 120px;
                     border-radius: 50%;
                     border: 4px solid white;
                     margin-bottom: 20px;
                     object-fit: cover;
                 ">
            <h2 style="margin: 0 0 10px 0;">{full_name}</h2>
            <p style="margin: 0; opacity: 0.9;">@{username}</p>
            <p style="margin: 5px 0; opacity: 0.9; font-size: 0.9em;">{email}</p>
            <div style="margin-top: 20px;">
                <span style="
                    background: rgba(255,255,255,0.2);
                    padding: 6px 15px;
                    border-radius: 15px;
                    font-size: 0.9em;
                    margin: 0 5px;
                ">🎓 {experience_level}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if bio:
        st.markdown(f"""
            <div style="
                background: #1e1e1e;
                padding: 20px;
                border-radius: 15px;
                margin-top: 20px;
                border-left: 4px solid #667eea;
            ">
                <h4 style="margin: 0 0 10px 0; color: #667eea;">📝 Bio</h4>
                <p style="margin: 0; color: #fafafa; line-height: 1.6;">{bio}</p>
            </div>
        """, unsafe_allow_html=True)


def render_profile_stats(user_id: int):
    """Render dynamic profile statistics"""
    profile_db = get_profile_db()
    stats = profile_db.get_profile_statistics(user_id)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Topics learned
    stat_card(str(stats['topics_learned']), "Topics Learned", "📚", "#667eea")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quizzes attempted
    stat_card(str(stats['quizzes_attempted']), "Quizzes Taken", "🎯", "#764ba2")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Average score
    avg_score = f"{stats['average_score']:.0f}%" if stats['average_score'] > 0 else "0%"
    stat_card(avg_score, "Average Score", "⭐", "#10b981")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tasks completed
    stat_card(str(stats['tasks_completed']), "Tasks Done", "✅", "#f59e0b")


def render_edit_profile_tab(user_id: int, username: str):
    """Edit profile tab with database save"""
    st.markdown("### ✏️ Edit Profile")
    
    profile_db = get_profile_db()
    profile = profile_db.get_profile(user_id)
    
    # Load existing data
    current_full_name = profile.get('full_name', username) if profile else username
    current_bio = profile.get('bio', '') if profile else ''
    current_interests = profile.get('learning_interests', '') if profile else ''
    current_level = profile.get('experience_level', 'Beginner') if profile else 'Beginner'
    current_location = profile.get('location', '') if profile else ''
    current_occupation = profile.get('occupation', '') if profile else ''
    current_website = profile.get('website', '') if profile else ''
    
    with st.form("edit_profile_form"):
        st.markdown("#### 👤 Personal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", value=current_full_name)
            location = st.text_input("Location", value=current_location, placeholder="e.g., San Francisco, CA")
        
        with col2:
            occupation = st.text_input("Occupation", value=current_occupation, placeholder="e.g., Software Engineer")
            website = st.text_input("Website", value=current_website, placeholder="https://yourwebsite.com")
        
        bio = st.text_area(
            "Bio",
            value=current_bio,
            placeholder="Tell us about yourself and your learning goals...",
            height=100
        )
        
        st.markdown("#### 🎯 Learning Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            learning_interests = st.text_area(
                "Learning Interests",
                value=current_interests,
                placeholder="e.g., Machine Learning, Web Development, Data Science",
                height=80,
                help="Separate interests with commas"
            )
        
        with col2:
            experience_levels = ["Beginner", "Intermediate", "Advanced", "Expert"]
            experience_level = st.selectbox(
                "Experience Level",
                experience_levels,
                index=experience_levels.index(current_level) if current_level in experience_levels else 0
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Profile", use_container_width=True, type="primary"):
                # Save to database
                profile_data = {
                    'username': username,
                    'full_name': full_name,
                    'bio': bio,
                    'learning_interests': learning_interests,
                    'experience_level': experience_level,
                    'location': location,
                    'occupation': occupation,
                    'website': website
                }
                
                if profile_db.update_profile(user_id, profile_data):
                    st.success("✅ Profile saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Error saving profile. Please try again.")
        
        with col2:
            if st.form_submit_button("🔄 Reset", use_container_width=True):
                st.rerun()
    
    # Profile picture upload
    st.markdown("---")
    st.markdown("#### 📸 Profile Picture")
    
    uploaded_file = st.file_uploader(
        "Upload Profile Picture",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a profile picture (PNG, JPG, JPEG)"
    )
    
    if uploaded_file is not None:
        # Display preview
        st.image(uploaded_file, width=200, caption="Preview")
        
        if st.button("💾 Save Profile Picture", type="primary"):
            # Save to database
            image_data = uploaded_file.read()
            if profile_db.update_profile_picture(user_id, image_data):
                st.success("✅ Profile picture updated!")
                st.rerun()
            else:
                st.error("❌ Error uploading picture. Please try again.")


def render_settings_tab(user_id: int):
    """Settings tab with database save"""
    st.markdown("### ⚙️ Account Settings")
    
    profile_db = get_profile_db()
    settings = profile_db.get_settings(user_id)
    
    # Load existing settings
    current_theme = settings.get('theme', 'Dark') if settings else 'Dark'
    current_language = settings.get('language', 'English') if settings else 'English'
    current_difficulty = settings.get('default_difficulty', 'Intermediate') if settings else 'Intermediate'
    current_email_notifs = bool(settings.get('email_notifications', 1)) if settings else True
    current_reminders = bool(settings.get('learning_reminders', 1)) if settings else True
    current_weekly = bool(settings.get('weekly_summary', 1)) if settings else True
    current_achievements = bool(settings.get('achievement_alerts', 1)) if settings else True
    
    with st.form("settings_form"):
        st.markdown("#### 🎨 Appearance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "Theme",
                ["Light", "Dark", "Auto"],
                index=["Light", "Dark", "Auto"].index(current_theme) if current_theme in ["Light", "Dark", "Auto"] else 1
            )
        
        with col2:
            language = st.selectbox(
                "Language",
                ["English", "Spanish", "French", "German", "Chinese"],
                index=["English", "Spanish", "French", "German", "Chinese"].index(current_language) if current_language in ["English", "Spanish", "French", "German", "Chinese"] else 0
            )
        
        st.markdown("#### 📚 Learning Preferences")
        
        default_difficulty = st.selectbox(
            "Default Difficulty Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(current_difficulty) if current_difficulty in ["Beginner", "Intermediate", "Advanced"] else 1,
            help="Default difficulty for generated content"
        )
        
        st.markdown("#### 🔔 Notifications")
        
        email_notifications = st.checkbox("Email Notifications", value=current_email_notifs)
        learning_reminders = st.checkbox("Learning Reminders", value=current_reminders)
        weekly_summary = st.checkbox("Weekly Progress Summary", value=current_weekly)
        achievement_alerts = st.checkbox("Achievement Alerts", value=current_achievements)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Settings", use_container_width=True, type="primary"):
                # Save to database
                settings_data = {
                    'theme': theme,
                    'language': language,
                    'default_difficulty': default_difficulty,
                    'email_notifications': 1 if email_notifications else 0,
                    'learning_reminders': 1 if learning_reminders else 0,
                    'weekly_summary': 1 if weekly_summary else 0,
                    'achievement_alerts': 1 if achievement_alerts else 0
                }
                
                if profile_db.update_settings(user_id, settings_data):
                    st.success("✅ Settings saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Error saving settings. Please try again.")
        
        with col2:
            if st.form_submit_button("🔄 Reset to Default", use_container_width=True):
                st.info("Settings reset to default")
                st.rerun()


def render_achievements_tab(user_id: int):
    """Achievements tab with dynamic unlocking and badges"""
    st.markdown("### 🏆 Your Achievements")
    
    # Check and award badges
    check_and_award_badges(user_id)
    
    profile_db = get_profile_db()
    learning_db = get_learning_db()
    advanced_db = get_advanced_db()
    
    # Get user's unlocked achievements
    unlocked = profile_db.get_achievements(user_id)
    unlocked_ids = {ach['achievement_id'] for ach in unlocked}
    
    # Get badges from advanced features
    badges = advanced_db.get_badges(user_id)
    badge_names = {badge['badge_name'] for badge in badges}
    
    # Get statistics for achievement checking
    stats = profile_db.get_profile_statistics(user_id)
    streak = advanced_db.get_streak(user_id)
    bookmarks = advanced_db.get_bookmarks(user_id)
    
    # Show earned badges section
    if badges:
        st.markdown("#### 🏅 Earned Badges")
        st.markdown(f"<p style='color:#b0b0b0;margin-bottom:20px'>You've earned {len(badges)} badges!</p>", unsafe_allow_html=True)
        
        badge_icons = {
            "First Topic": "🥇",
            "Explorer": "🗺️",
            "Quiz Master": "🎯",
            "Perfectionist": "💯",
            "Consistent Learner": "🔥",
            "Dedicated": "⭐",
            "Bookworm": "📚",
            "Task Master": "✅",
            "Code Warrior": "💻",
            "Speed Learner": "⚡"
        }
        
        cols = st.columns(4)
        for i, badge in enumerate(badges):
            with cols[i % 4]:
                icon = badge_icons.get(badge['badge_name'], "🏅")
                earned_date = badge['earned_at'][:10] if badge.get('earned_at') else "Recently"
                
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea22 0%, #764ba244 100%);
                        padding: 20px;
                        border-radius: 15px;
                        text-align: center;
                        margin: 10px 0;
                        border: 2px solid #667eea;
                    ">
                        <div style="font-size: 3.5em; margin-bottom: 10px;">{icon}</div>
                        <h4 style="margin: 0 0 5px 0; color: #fafafa; font-size: 1em;">{badge['badge_name']}</h4>
                        <p style="margin: 0 0 8px 0; color: #b0b0b0; font-size: 0.8em;">
                            {badge.get('badge_description', '')}
                        </p>
                        <p style="margin: 0; color: #10b981; font-size: 0.75em; font-weight: 600;">
                            Earned {earned_date}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
    
    # Show progress towards next badges
    st.markdown("#### 🎯 Badge Progress")
    
    next_badges = [
        {
            "name": "First Topic",
            "icon": "🥇",
            "description": "Generate your first topic",
            "progress": min(stats['topics_learned'], 1),
            "target": 1,
            "earned": "First Topic" in badge_names
        },
        {
            "name": "Explorer",
            "icon": "🗺️",
            "description": "Learn 10 different topics",
            "progress": min(stats['topics_learned'], 10),
            "target": 10,
            "earned": "Explorer" in badge_names
        },
        {
            "name": "Quiz Master",
            "icon": "🎯",
            "description": "Achieve 80%+ average score",
            "progress": min(stats['average_score'], 80),
            "target": 80,
            "earned": "Quiz Master" in badge_names
        },
        {
            "name": "Consistent Learner",
            "icon": "🔥",
            "description": "Maintain 7-day streak",
            "progress": min(streak, 7),
            "target": 7,
            "earned": "Consistent Learner" in badge_names
        },
        {
            "name": "Bookworm",
            "icon": "📚",
            "description": "Save 5 bookmarks",
            "progress": min(len(bookmarks), 5),
            "target": 5,
            "earned": "Bookworm" in badge_names
        },
        {
            "name": "Task Master",
            "icon": "✅",
            "description": "Complete 20 tasks",
            "progress": min(stats['tasks_completed'], 20),
            "target": 20,
            "earned": "Task Master" in badge_names
        }
    ]
    
    cols = st.columns(2)
    for i, badge_info in enumerate(next_badges):
        with cols[i % 2]:
            percentage = (badge_info['progress'] / badge_info['target']) * 100 if badge_info['target'] > 0 else 0
            
            if badge_info['earned']:
                status_color = "#10b981"
                status_text = "✅ Earned!"
                opacity = "1"
            else:
                status_color = "#667eea"
                status_text = f"{badge_info['progress']}/{badge_info['target']}"
                opacity = "0.8"
            
            st.markdown(f"""
                <div style="
                    background: #1e1e1e;
                    padding: 15px;
                    border-radius: 12px;
                    margin: 10px 0;
                    border-left: 4px solid {status_color};
                    opacity: {opacity};
                ">
                    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                        <div style="font-size: 2.5em;">{badge_info['icon']}</div>
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: #fafafa;">{badge_info['name']}</h4>
                            <p style="margin: 5px 0 0 0; color: #b0b0b0; font-size: 0.85em;">
                                {badge_info['description']}
                            </p>
                        </div>
                    </div>
                    <div style="background: #2e2e2e; border-radius: 10px; height: 8px; overflow: hidden;">
                        <div style="
                            background: linear-gradient(90deg, {status_color} 0%, {status_color}aa 100%);
                            height: 100%;
                            width: {percentage}%;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                    <p style="margin: 8px 0 0 0; color: {status_color}; font-size: 0.85em; font-weight: 600; text-align: right;">
                        {status_text}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Original achievements section
    st.markdown("#### 🎖️ Platform Achievements")
    
    profile_db = get_profile_db()
    learning_db = get_learning_db()
    
    # Get user's unlocked achievements
    unlocked = profile_db.get_achievements(user_id)
    unlocked_ids = {ach['achievement_id'] for ach in unlocked}
    
    # Get statistics for achievement checking
    stats = profile_db.get_profile_statistics(user_id)
    
    # Define all achievements
    all_achievements = [
        {
            "id": "first_topic",
            "icon": "🥇",
            "title": "First Steps",
            "description": "Generate your first learning topic",
            "condition": stats['topics_learned'] >= 1
        },
        {
            "id": "five_topics",
            "icon": "📚",
            "title": "Knowledge Seeker",
            "description": "Learn 5 different topics",
            "condition": stats['topics_learned'] >= 5
        },
        {
            "id": "ten_topics",
            "icon": "🎓",
            "title": "Dedicated Learner",
            "description": "Complete 10 topics",
            "condition": stats['topics_learned'] >= 10
        },
        {
            "id": "first_quiz",
            "icon": "🎯",
            "title": "Quiz Taker",
            "description": "Complete your first quiz",
            "condition": stats['quizzes_attempted'] >= 1
        },
        {
            "id": "quiz_master",
            "icon": "⭐",
            "title": "Quiz Master",
            "description": "Score 80%+ average on quizzes",
            "condition": stats['average_score'] >= 80
        },
        {
            "id": "perfect_score",
            "icon": "💯",
            "title": "Perfectionist",
            "description": "Score 100% on a quiz",
            "condition": stats['average_score'] >= 100
        },
        {
            "id": "task_completer",
            "icon": "✅",
            "title": "Task Master",
            "description": "Complete 10 roadmap tasks",
            "condition": stats['tasks_completed'] >= 10
        },
        {
            "id": "dedicated_worker",
            "icon": "🔥",
            "title": "Dedicated Worker",
            "description": "Complete 25 roadmap tasks",
            "condition": stats['tasks_completed'] >= 25
        }
    ]
    
    # Auto-unlock achievements
    for achievement in all_achievements:
        if achievement['condition'] and achievement['id'] not in unlocked_ids:
            profile_db.unlock_achievement(
                user_id,
                achievement['id'],
                achievement['title'],
                achievement['description']
            )
            unlocked_ids.add(achievement['id'])
    
    # Display achievements
    cols = st.columns(2)
    
    for i, achievement in enumerate(all_achievements):
        with cols[i % 2]:
            is_unlocked = achievement['id'] in unlocked_ids
            opacity = "1" if is_unlocked else "0.4"
            border_color = "#10b981" if is_unlocked else "#d1d5db"
            status_text = "Unlocked!" if is_unlocked else "Locked"
            
            st.markdown(f"""
                <div style="
                    background: #1e1e1e;
                    padding: 20px;
                    border-radius: 15px;
                    margin: 10px 0;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                    border-left: 4px solid {border_color};
                    opacity: {opacity};
                ">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div style="
                            font-size: 3em;
                            width: 70px;
                            height: 70px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            border-radius: 15px;
                        ">{achievement['icon']}</div>
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 5px 0; color: #fafafa;">{achievement['title']}</h4>
                            <p style="margin: 0 0 5px 0; color: #b0b0b0; font-size: 0.9em;">
                                {achievement['description']}
                            </p>
                            <p style="margin: 0; color: {border_color}; font-size: 0.85em; font-weight: 600;">
                                {status_text}
                            </p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


def render_statistics_tab(user_id: int):
    """Statistics tab with real data"""
    st.markdown("### 📊 Learning Statistics")
    
    profile_db = get_profile_db()
    learning_db = get_learning_db()
    
    stats = profile_db.get_profile_statistics(user_id)
    
    # Learning stats
    st.markdown("#### 📚 Learning Overview")
    
    learning_stats = [
        ("Topics Learned", str(stats['topics_learned']), "📚"),
        ("Quizzes Taken", str(stats['quizzes_attempted']), "🎯"),
        ("Average Score", f"{stats['average_score']:.0f}%", "⭐"),
        ("Tasks Completed", str(stats['tasks_completed']), "✅")
    ]
    
    cols = st.columns(4)
    
    for i, (label, value, icon) in enumerate(learning_stats):
        with cols[i]:
            st.markdown(f"""
                <div style="
                    background: #1e1e1e;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                    margin: 10px 0;
                ">
                    <div style="font-size: 2em; margin-bottom: 10px;">{icon}</div>
                    <div style="font-size: 1.8em; font-weight: 700; color: #667eea; margin: 5px 0;">
                        {value}
                    </div>
                    <div style="color: #b0b0b0; font-size: 0.9em;">{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("#### 📅 Recent Activity")
    
    # Get recent topics
    topics = learning_db.get_learning_topics(user_id, limit=5)
    
    if topics:
        for topic in topics:
            st.markdown(f"""
                <div style="
                    background: #1e1e1e;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    border-left: 4px solid #667eea;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #667eea; font-weight: 600;">📚 Generated topic:</span>
                            <span style="color: #fafafa; margin-left: 10px;">{topic['topic_name']}</span>
                        </div>
                        <span style="color: #b0b0b0; font-size: 0.85em;">{topic['created_at']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity. Start learning to see your progress here!")
    
    # Get recent quizzes
    quizzes = learning_db.get_quiz_results(user_id, limit=5)
    
    if quizzes:
        st.markdown("<br>", unsafe_allow_html=True)
        for quiz in quizzes:
            score_color = "#10b981" if quiz['percentage'] >= 70 else "#f59e0b"
            st.markdown(f"""
                <div style="
                    background: #1e1e1e;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    border-left: 4px solid {score_color};
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: {score_color}; font-weight: 600;">🎯 Completed quiz:</span>
                            <span style="color: #fafafa; margin-left: 10px;">{quiz['topic']}</span>
                            <span style="color: #b0b0b0; margin-left: 10px;">
                                (Score: {quiz['score']}/{quiz['total_questions']} - {quiz['percentage']:.0f}%)
                            </span>
                        </div>
                        <span style="color: #b0b0b0; font-size: 0.85em;">{quiz['attempted_at']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)


def render_resume_skills_tab(user_id: int, username: str):
    """Resume Skills Builder tab - NEW FEATURE"""
    st.markdown("### 📄 Resume Skills Builder")
    st.caption("Automatically generated from your completed topics")
    
    try:
        from utils.resume_builder import get_resume_builder
        
        resume_builder = get_resume_builder()
        learning_db = get_learning_db()
        
        # Generate skills
        skills = resume_builder.generate_resume_skills(user_id, learning_db)
        
        if skills:
            # Skill count
            total_skills = resume_builder.get_skill_count(skills)
            
            st.markdown(f"""
                <div class="glass-card" style="
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.2) 100%) !important;
                    border: 2px solid rgba(102, 126, 234, 0.3);
                    text-align: center;
                    margin-bottom: 20px;
                ">
                    <div style="font-size: 3em; margin-bottom: 10px;">🎯</div>
                    <h2 style="margin: 0 0 10px 0; color: #667eea; font-size: 2.5em;">
                        {total_skills} Skills
                    </h2>
                    <p style="margin: 0; color: rgba(255, 255, 255, 0.8);">
                        Ready for your resume
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Display categorized skills
            for category, skill_list in skills.items():
                st.markdown(f"""
                    <div class="glass-card">
                        <h4 style="margin: 0 0 15px 0; color: #667eea; font-size: 1.2em;">
                            {category}
                        </h4>
                        <div style="
                            display: flex;
                            flex-wrap: wrap;
                            gap: 10px;
                        ">
                """, unsafe_allow_html=True)
                
                for skill in skill_list:
                    st.markdown(f"""
                        <span style="
                            background: linear-gradient(135deg, #667eea22 0%, #764ba244 100%);
                            border: 1px solid #667eea;
                            padding: 8px 16px;
                            border-radius: 20px;
                            font-size: 0.9em;
                            color: #ffffff;
                            display: inline-block;
                            margin: 5px;
                        ">{skill}</span>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Download section
            st.markdown("### 📥 Export Skills")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Generate text export
                text_export = resume_builder.generate_skills_text_export(skills, username)
                
                st.download_button(
                    label="📄 Download as Text",
                    data=text_export,
                    file_name=f"{username}_skills.txt",
                    mime="text/plain",
                    use_container_width=True,
                    type="primary"
                )
            
            with col2:
                # Generate summary
                summary = resume_builder.generate_skill_summary(skills)
                
                st.download_button(
                    label="📋 Download Summary",
                    data=summary,
                    file_name=f"{username}_skill_summary.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            # Usage tips
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
                <div class="glass-card" style="
                    background: rgba(16, 185, 129, 0.1) !important;
                    border-left: 4px solid #10b981;
                ">
                    <h4 style="margin: 0 0 10px 0; color: #10b981;">💡 How to Use</h4>
                    <ul style="margin: 0; padding-left: 20px; color: rgba(255, 255, 255, 0.8); line-height: 1.8;">
                        <li>Copy skills directly to your resume</li>
                        <li>Use categories to organize your resume sections</li>
                        <li>Download the text file for easy editing</li>
                        <li>Update regularly as you learn new topics</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.info("📚 Complete more topics to build your skill profile!")
            
            st.markdown("""
                <div class="glass-card" style="text-align: center; padding: 40px;">
                    <div style="font-size: 4em; margin-bottom: 20px;">🚀</div>
                    <h3 style="color: #667eea; margin-bottom: 15px;">Start Building Your Skills</h3>
                    <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 25px;">
                        Complete learning topics to automatically generate resume-ready skills
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("📚 Start Learning", use_container_width=True, type="primary"):
                st.switch_page("pages/2_Learn.py")
    
    except Exception as e:
        st.error(f"Error loading resume skills: {str(e)}")
        st.info("Complete more topics to see your skills here!")


def main():
    if not check_authentication():
        st.warning("Please login to view your profile")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()
    
    # Get user info
    user_id = st.session_state.get("user_id")
    username = st.session_state.get("username", "User")
    email = st.session_state.get("email", "user@example.com")
    
    # Initialize profile if needed
    init_user_profile(user_id, username)
    
    st.markdown("# 👤 Profile")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile header
        render_profile_header(user_id, username, email)
        
        # Profile stats
        render_profile_stats(user_id)
    
    with col2:
        # Profile tabs
        tabs = st.tabs([
            "✏️ Edit Profile",
            "📄 Resume Skills",
            "⚙️ Settings",
            "🏆 Achievements",
            "📊 Statistics"
        ])
        
        with tabs[0]:
            render_edit_profile_tab(user_id, username)
        
        with tabs[1]:
            render_resume_skills_tab(user_id, username)
        
        with tabs[2]:
            render_settings_tab(user_id)
        
        with tabs[3]:
            render_achievements_tab(user_id)
        
        with tabs[4]:
            render_statistics_tab(user_id)


if __name__ == "__main__":
    main()
