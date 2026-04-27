"""
Dashboard - Modern AI SaaS Dashboard with Professional UI
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path
import os

sys.path.append(str(Path(__file__).parent.parent))

from components.auth_components import check_authentication

st.set_page_config(
    page_title="LearnSphere Dashboard", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load modern CSS
def load_modern_css():
    css_path = Path(__file__).parent.parent / "styles" / "modern_ui.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            modern_css = f.read()
        st.markdown(f"<style>{modern_css}</style>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg,#667eea,#764ba2); border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

sys.path.append(str(Path(__file__).parent.parent))
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.user_data import get_analytics_data, init_user_data, has_any_data
from utils.advanced_features_db import get_advanced_db

apply_theme()
load_modern_css()
apply_sidebar_fix()
init_user_data()


def render_dashboard():
    user_id = st.session_state.get("user_id")
    
    from utils.learning_progress import get_learning_db
    from utils.advanced_features_db import get_advanced_db
    
    db = get_learning_db()
    advanced_db = get_advanced_db()
    
    if user_id:
        completed_topics = db.get_completed_topics_count(user_id)
        study_time_minutes = db.get_total_study_time(user_id)
        study_time_hours = round(study_time_minutes / 60, 1) if study_time_minutes > 0 else 0
        current_streak = advanced_db.get_streak(user_id)
        quiz_results = db.get_quiz_results(user_id, limit=100)
        quiz_average = sum(q['percentage'] for q in quiz_results) / len(quiz_results) if quiz_results else 0
    else:
        completed_topics = 0
        study_time_hours = 0
        current_streak = 0
        quiz_average = 0
        quiz_results = []
    
    st.markdown("""
        <div class="hero-header">
            <h1 class="hero-title">🏠 Dashboard</h1>
            <p class="hero-subtitle">Welcome back, {username}! Here's your learning overview.</p>
        </div>
    """.format(username=st.session_state.get("username", "Learner")), unsafe_allow_html=True)
    
    if current_streak > 0:
        st.markdown(f"""
            <div class="glass-card" style="
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
                text-align: center; margin-bottom: 2rem; border: none;
                box-shadow: 0 8px 30px rgba(245,158,11,0.4);">
                <h2 style="color:white;margin:0;font-size:2.5rem;">🔥 {current_streak} Day Streak!</h2>
                <p style="color:rgba(255,255,255,0.9);margin:10px 0 0 0;font-size:1.2rem;">Keep learning to maintain your streak!</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="glass-card" style="text-align:center;margin-bottom:2rem;
                border:2px dashed #667eea;background:rgba(102,126,234,0.1)!important;">
                <h3 style="color:#667eea;margin:0;font-size:1.8rem;">🔥 Start Your Learning Streak!</h3>
                <p style="color:rgba(255,255,255,0.8);margin:10px 0 0 0;">Learn something today to begin your streak</p>
            </div>
        """, unsafe_allow_html=True)
    
    has_data = (completed_topics > 0 or len(quiz_results) > 0) if user_id else False
    
    if not has_data:
        st.markdown("""
            <div class="glass-card" style="text-align:center;padding:4rem 2rem;
                background:linear-gradient(135deg,rgba(102,126,234,0.1),rgba(118,75,162,0.2))!important;
                border:2px solid rgba(102,126,234,0.3);">
                <div style="font-size:5rem;margin-bottom:1.5rem;">🚀</div>
                <h2 style="color:#667eea;margin-bottom:1rem;font-size:2.5rem;">Welcome to Your Learning Journey!</h2>
                <p style="color:rgba(255,255,255,0.8);font-size:1.2rem;margin-bottom:2rem;">
                    You haven't started any learning activities yet. Let's get started!
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🚀 Quick Start")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""<div class="glass-card" style="text-align:center;border-top:4px solid #667eea;">
                <div style="font-size:3rem;margin-bottom:1rem;">📚</div>
                <h3 style="color:#ffffff;margin-bottom:0.5rem;">Start Learning</h3>
                <p style="color:rgba(255,255,255,0.7);margin-bottom:1.5rem;">Generate AI-powered content on any topic</p>
            </div>""", unsafe_allow_html=True)
            if st.button("📚 Go to Learn", use_container_width=True, type="primary"):
                st.switch_page("pages/2_Learn.py")
        with col2:
            st.markdown("""<div class="glass-card" style="text-align:center;border-top:4px solid #764ba2;">
                <div style="font-size:3rem;margin-bottom:1rem;">📝</div>
                <h3 style="color:#ffffff;margin-bottom:0.5rem;">Take a Quiz</h3>
                <p style="color:rgba(255,255,255,0.7);margin-bottom:1.5rem;">Test your knowledge with AI-generated quizzes</p>
            </div>""", unsafe_allow_html=True)
            if st.button("📝 Go to Quiz", use_container_width=True):
                st.switch_page("pages/3_Quiz.py")
        with col3:
            st.markdown("""<div class="glass-card" style="text-align:center;border-top:4px solid #10b981;">
                <div style="font-size:3rem;margin-bottom:1rem;">👤</div>
                <h3 style="color:#ffffff;margin-bottom:0.5rem;">Your Profile</h3>
                <p style="color:rgba(255,255,255,0.7);margin-bottom:1.5rem;">Customize your learning experience</p>
            </div>""", unsafe_allow_html=True)
            if st.button("👤 Go to Profile", use_container_width=True):
                st.switch_page("pages/5_Profile.py")
        return
    
    st.markdown("### 📊 Learning Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="stat-card"><div class="stat-icon">📚</div>
            <div class="stat-content"><div class="stat-value">{completed_topics}</div>
            <div class="stat-label">Topics Completed</div></div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-card"><div class="stat-icon">⏱️</div>
            <div class="stat-content"><div class="stat-value">{study_time_hours}h</div>
            <div class="stat-label">Time Spent</div></div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-card"><div class="stat-icon">🎯</div>
            <div class="stat-content"><div class="stat-value">{quiz_average:.0f}%</div>
            <div class="stat-label">Avg Quiz Score</div></div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="stat-card"><div class="stat-icon">🔥</div>
            <div class="stat-content"><div class="stat-value">{current_streak}</div>
            <div class="stat-label">Day Streak</div></div></div>""", unsafe_allow_html=True)

    st.markdown("### 🤖 AI Mentor Recommendation")
    try:
        from utils.ai_mentor import get_ai_mentor
        mentor = get_ai_mentor()
        recommendation = mentor.get_recommendation(user_id, db, advanced_db)
        if recommendation:
            st.markdown(f"""
                <div class="glass-card" style="background:linear-gradient(135deg,rgba(16,185,129,0.1),rgba(5,150,105,0.2))!important;
                    border:2px solid rgba(16,185,129,0.3);">
                    <div style="display:flex;align-items:start;gap:20px;">
                        <div style="font-size:3.5em;">🎯</div>
                        <div style="flex:1;">
                            <h3 style="margin:0 0 10px 0;color:#10b981;">Recommended: {recommendation['topic']}</h3>
                            <p style="margin:0 0 15px 0;color:rgba(255,255,255,0.9);line-height:1.6;">{recommendation['reason']}</p>
                            <div style="display:flex;gap:15px;flex-wrap:wrap;">
                                <span style="background:rgba(16,185,129,0.2);padding:6px 12px;border-radius:8px;font-size:0.85em;color:#10b981;">📊 {recommendation['difficulty']}</span>
                                <span style="background:rgba(16,185,129,0.2);padding:6px 12px;border-radius:8px;font-size:0.85em;color:#10b981;">⏱️ {recommendation['estimated_time']}</span>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Start Learning This Topic", use_container_width=True, type="primary"):
                st.session_state.suggested_topic = recommendation['topic']
                st.session_state.suggested_difficulty = recommendation['difficulty']
                st.switch_page("pages/2_Learn.py")
        else:
            st.info("💡 Complete more topics to get personalized recommendations!")
    except Exception:
        st.info("💡 AI Mentor recommendations will appear here as you progress!")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Your Skill Level")
    try:
        from utils.skill_progression import get_skill_system
        skill_system = get_skill_system()
        level_data = skill_system.calculate_skill_level(user_id, db)
        badge = skill_system.get_level_badge_emoji(level_data['level'])
        color = skill_system.get_level_color(level_data['level'])
        st.markdown(f"""
            <div class="glass-card" style="background:linear-gradient(135deg,{color}22,{color}44)!important;border:2px solid {color};">
                <div style="text-align:center;padding:20px 0;">
                    <div style="font-size:5em;margin-bottom:15px;">{badge}</div>
                    <h2 style="margin:0 0 10px 0;color:{color};font-size:2.5em;">{level_data['level']}</h2>
                    <p style="margin:0 0 20px 0;color:rgba(255,255,255,0.8);font-size:1.1em;">{level_data['xp']} / {level_data['next_level_xp']} XP</p>
                    <div style="background:rgba(0,0,0,0.3);border-radius:10px;height:12px;overflow:hidden;margin:0 20px;">
                        <div style="background:linear-gradient(90deg,{color},{color}aa);height:100%;width:{level_data['progress_percentage']}%;transition:width 0.3s;"></div>
                    </div>
                    <p style="margin:15px 0 0 0;color:rgba(255,255,255,0.7);font-size:0.9em;">{level_data['progress_percentage']:.0f}% to next level</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.info("📊 Your skill level will be calculated as you learn!")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⏱️ Today's Study Time")
    try:
        from utils.study_timer import get_study_timer
        timer = get_study_timer()
        today_stats = timer.get_today_stats(user_id)
        productivity_score = timer.get_productivity_score(user_id)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""<div class="glass-card" style="text-align:center;">
                <div style="font-size:2.5em;margin-bottom:10px;">⏱️</div>
                <div style="font-size:2em;font-weight:700;color:#667eea;">{today_stats['focus_hours']}h</div>
                <div style="color:#b0b0b0;font-size:0.9em;">Focus Time</div></div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class="glass-card" style="text-align:center;">
                <div style="font-size:2.5em;margin-bottom:10px;">🎯</div>
                <div style="font-size:2em;font-weight:700;color:#10b981;">{today_stats['completed_sessions']}</div>
                <div style="color:#b0b0b0;font-size:0.9em;">Sessions</div></div>""", unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""<div class="glass-card" style="text-align:center;">
                <div style="font-size:2.5em;margin-bottom:10px;">📈</div>
                <div style="font-size:2em;font-weight:700;color:#f59e0b;">{productivity_score}%</div>
                <div style="color:#b0b0b0;font-size:0.9em;">Productivity</div></div>""", unsafe_allow_html=True)
    except Exception:
        st.info("⏱️ Study timer stats will appear here!")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""<div class="glass-card"><div class="glass-card-header">
            <div class="glass-card-icon">📈</div><h3 class="glass-card-title">Learning Progress</h3></div>""",
            unsafe_allow_html=True)
        analytics = db.get_learning_analytics(user_id) if user_id else None
        if not analytics:
            analytics = {"topic_performance": [], "weekly_activity": [
                {"day": d, "time_spent": 0} for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]]}
        topic_perf = analytics.get('topic_performance', [])
        if topic_perf:
            overall_completion = sum(t['completion'] for t in topic_perf) / len(topic_perf)
            st.markdown(f"**Overall Completion: {overall_completion:.0f}%**")
            st.progress(overall_completion / 100)
            st.markdown("**Top Topics:**")
            for topic in topic_perf[:3]:
                st.markdown(f"- {topic['topic']}: {topic['completion']:.0f}%")
                st.progress(topic['completion'] / 100)
        else:
            st.info("Start learning to see your progress!")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div class="glass-card"><div class="glass-card-header">
            <div class="glass-card-icon">📊</div><h3 class="glass-card-title">Weekly Activity</h3></div>""",
            unsafe_allow_html=True)
        weekly_data = analytics.get('weekly_activity', [])
        days = [d['day'] for d in weekly_data]
        hours = [d['time_spent'] for d in weekly_data]
        fig = go.Figure(data=[go.Bar(
            x=days, y=hours,
            marker=dict(color=hours, colorscale=[[0,'#667eea'],[1,'#764ba2']], line=dict(width=0)),
            text=[f"{h:.1f}h" for h in hours], textposition='outside')])
        fig.update_layout(height=300, margin=dict(l=20,r=20,t=20,b=20),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            font=dict(family="Inter", size=12))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div class="glass-card"><div class="glass-card-header">
            <div class="glass-card-icon">🔥</div><h3 class="glass-card-title">Current Streak</h3></div>
            <p style="color:rgba(255,255,255,0.8);">You're on a <strong style="color:#f59e0b;">{current_streak}-day</strong> learning streak!</p>
        </div>""", unsafe_allow_html=True)

        st.markdown("""<div class="glass-card"><div class="glass-card-header">
            <div class="glass-card-icon">⭐</div><h3 class="glass-card-title">Saved Topics</h3></div>""",
            unsafe_allow_html=True)
        bookmarks = advanced_db.get_bookmarks(user_id) if user_id else []
        if bookmarks:
            for bookmark in bookmarks[:5]:
                st.markdown(f"""<div style="background:rgba(255,255,255,0.05);padding:12px;border-radius:8px;
                    margin:8px 0;border-left:3px solid #f59e0b;">
                    <p style="margin:0;color:#ffffff;font-weight:500;">⭐ {bookmark['topic']}</p>
                    <p style="margin:5px 0 0 0;color:rgba(255,255,255,0.6);font-size:0.8em;">Saved {bookmark['saved_at'][:10]}</p>
                </div>""", unsafe_allow_html=True)
            if st.button("📚 View All Bookmarks", use_container_width=True):
                st.switch_page("pages/2_Learn.py")
        else:
            st.info("No bookmarks yet. Save topics from the Learn page!")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div class="glass-card"><div class="glass-card-header">
            <div class="glass-card-icon">🏆</div><h3 class="glass-card-title">Achievements</h3></div>""",
            unsafe_allow_html=True)
        achievements = [
            {"icon":"🥇","title":"First Topic","description":"Completed your first topic","unlocked":True},
            {"icon":"📚","title":"Bookworm","description":"Completed 10 topics","unlocked":False},
            {"icon":"🎯","title":"Quiz Master","description":"Scored 90%+ on 5 quizzes","unlocked":False},
            {"icon":"⚡","title":"Speed Learner","description":"Completed a topic in under 2 hours","unlocked":False},
        ]
        for a in achievements:
            cls = "achievement-unlocked" if a["unlocked"] else "achievement-locked"
            st.markdown(f"""<div class="achievement-card {cls}">
                <div class="achievement-icon">{a['icon']}</div>
                <div class="achievement-content">
                    <div class="achievement-title">{a['title']}</div>
                    <div class="achievement-description">{a['description']}</div>
                </div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""<div class="glass-card"><div class="glass-card-header">
            <div class="glass-card-icon">⚡</div><h3 class="glass-card-title">Quick Actions</h3></div>""",
            unsafe_allow_html=True)
        if st.button("📚 Continue Learning", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Learn.py")
        if st.button("📝 Take a Quiz", use_container_width=True):
            st.switch_page("pages/3_Quiz.py")
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/4_Analytics.py")
        if st.button("🔥 Daily Challenge", use_container_width=True):
            st.switch_page("pages/13_DailyChallenge.py")
        if st.button("🗺️ Learning Path", use_container_width=True):
            st.switch_page("pages/10_LearningPath.py")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔥 Today's Challenge")
    try:
        from utils.daily_challenges import get_daily_challenge_system
        daily_system = get_daily_challenge_system()
        today_challenge = daily_system.get_today_challenge()
        streak_info = daily_system.get_streak_info(user_id) if user_id else {"current": 0}
        completed_today = daily_system.is_completed_today(user_id) if user_id else False
        type_icons = {"coding":"💻","quiz":"❓","concept":"💡"}
        type_colors = {"coding":"#667eea","quiz":"#10b981","concept":"#f59e0b"}
        ch_type = today_challenge.get('type','concept')
        ch_color = type_colors.get(ch_type,"#667eea")
        ch_icon = type_icons.get(ch_type,"💡")
        status_badge = '<span style="background:#10b981;color:white;padding:3px 10px;border-radius:6px;font-size:0.8em;">✅ Done</span>' if completed_today else '<span style="background:#f59e0b;color:white;padding:3px 10px;border-radius:6px;font-size:0.8em;">⏳ Pending</span>'
        st.markdown(f"""
            <div class="glass-card" style="border-top:4px solid {ch_color};">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                    <span style="color:{ch_color};font-weight:600;">{ch_icon} {ch_type.title()} Challenge</span>
                    {status_badge}
                </div>
                <h4 style="color:#ffffff;margin:0 0 8px 0;">{today_challenge.get('title','Daily Challenge')}</h4>
                <p style="color:rgba(255,255,255,0.7);margin:0;font-size:0.9em;">{today_challenge.get('description','')[:120]}...</p>
                <p style="color:rgba(255,255,255,0.5);margin:10px 0 0 0;font-size:0.85em;">🔥 Current streak: {streak_info.get('current',0)} days</p>
            </div>
        """, unsafe_allow_html=True)
        if not completed_today:
            if st.button("🔥 Take Today's Challenge", use_container_width=True, type="primary", key="dash_daily"):
                st.switch_page("pages/13_DailyChallenge.py")
    except Exception:
        st.info("🔥 Daily challenges available! Visit the Daily Challenge page.")


def main():
    if not check_authentication():
        st.warning("Please login to access the dashboard")
        st.switch_page("Home.py")
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
