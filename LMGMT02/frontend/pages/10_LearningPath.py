"""
Learning Path Generator Page
AI-powered personalized learning roadmap
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.learning_path_generator import get_path_generator

st.set_page_config(
    page_title="Learning Path Generator",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
load_theme_css()
apply_sidebar_fix()


def render_week_card(week: dict, week_progress: set, path_id: int, user_id: int, generator):
    """Render a single week card with progress tracking"""
    week_num = week['week']
    topics = week.get('topics', [])
    total_topics = len(topics)
    completed_topics = sum(1 for i in range(total_topics) if (week_num, i) in week_progress)
    week_done = completed_topics == total_topics and total_topics > 0

    color = "#10b981" if week_done else "#667eea"
    bg = "rgba(16, 185, 129, 0.1)" if week_done else "rgba(102, 126, 234, 0.1)"

    st.markdown(f"""
        <div style="
            background: {bg};
            border: 2px solid {color};
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="margin: 0; color: {color};">
                    {'✅' if week_done else f'📅'} Week {week_num}: {week.get('theme', '')}
                </h4>
                <span style="
                    background: {color}33;
                    color: {color};
                    padding: 4px 10px;
                    border-radius: 8px;
                    font-size: 0.85em;
                ">{completed_topics}/{total_topics} done</span>
            </div>
            <p style="color: rgba(255,255,255,0.7); margin: 0 0 10px 0; font-size: 0.9em;">
                🎯 {week.get('milestone', '')}
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Topics as checkboxes
    for i, topic in enumerate(topics):
        is_done = (week_num, i) in week_progress
        col_check, col_label = st.columns([0.08, 0.92])
        with col_check:
            checked = st.checkbox("", value=is_done, key=f"topic_{path_id}_{week_num}_{i}", label_visibility="collapsed")
        with col_label:
            style = "text-decoration: line-through; color: rgba(255,255,255,0.4);" if is_done else "color: rgba(255,255,255,0.9);"
            st.markdown(f"<span style='{style}'>{topic}</span>", unsafe_allow_html=True)

        if checked and not is_done and user_id and path_id:
            generator.mark_topic_complete(user_id, path_id, week_num, i)
            st.rerun()

    # Projects
    projects = week.get('projects', [])
    if projects:
        st.markdown(f"<small style='color: #f59e0b;'>🛠️ Project: {projects[0]}</small>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


def main():
    if not check_authentication():
        st.warning("Please login to use the Learning Path Generator")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()

    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <h1 style="color: white; margin: 0;">🗺️ Learning Path Generator</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;">
                Get a personalized AI-generated roadmap to achieve your learning goals
            </p>
        </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("user_id")
    generator = get_path_generator()

    tab1, tab2 = st.tabs(["🚀 Generate New Path", "📚 My Learning Paths"])

    with tab1:
        st.markdown("### 🎯 Define Your Learning Goal")

        col1, col2 = st.columns(2)

        with col1:
            # Apply preset from quick goal buttons before widget renders
            if "_path_goal_preset" in st.session_state:
                preset = st.session_state.pop("_path_goal_preset")
            else:
                preset = st.session_state.get("path_goal", "")

            goal = st.text_input(
                "What do you want to learn?",
                value=preset,
                placeholder="e.g., Become a Data Scientist, Learn Machine Learning, Master Python",
                key="path_goal"
            )
            skill_level = st.selectbox(
                "Your current skill level",
                ["Complete Beginner", "Beginner", "Intermediate", "Advanced"],
                key="path_skill"
            )

        with col2:
            hours_per_week = st.slider(
                "Hours available per week",
                min_value=2, max_value=40, value=10, step=2,
                key="path_hours"
            )
            duration_weeks = st.slider(
                "Duration (weeks)",
                min_value=4, max_value=24, value=8, step=2,
                key="path_duration"
            )

        # Quick goal suggestions
        st.markdown("**Quick Goals:**")
        quick_goals = [
            "🤖 Machine Learning Engineer",
            "🐍 Python Developer",
            "📊 Data Scientist",
            "🌐 Full Stack Developer",
            "☁️ Cloud Engineer",
            "🔒 Cybersecurity Analyst"
        ]
        cols = st.columns(3)
        for i, qg in enumerate(quick_goals):
            with cols[i % 3]:
                if st.button(qg, key=f"qg_{i}", use_container_width=True):
                    # Use a staging key — can't write to widget key directly
                    st.session_state._path_goal_preset = qg.split(" ", 1)[1]
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Generate My Learning Path", use_container_width=True, type="primary"):
            if not goal:
                st.error("Please enter your learning goal")
            else:
                with st.spinner("🤖 AI is creating your personalized roadmap..."):
                    path = generator.generate_path(
                        goal, skill_level, hours_per_week, duration_weeks, user_id
                    )
                    st.session_state.current_path = path
                    st.rerun()

        # Display generated path
        path = st.session_state.get("current_path")
        if path:
            st.markdown("---")
            st.markdown(f"## 🗺️ {path.get('title', 'Your Learning Path')}")

            # Overview
            st.markdown(f"""
                <div style="
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid #10b981;
                    border-radius: 12px;
                    padding: 20px;
                    margin: 15px 0;
                ">
                    <p style="color: rgba(255,255,255,0.9); margin: 0; line-height: 1.7;">
                        {path.get('overview', '')}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Stats row
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("📅 Duration", f"{path.get('total_weeks', 0)} weeks")
            with col_b:
                st.metric("⏱️ Hours/Week", f"{hours_per_week}h")
            with col_c:
                total_topics = sum(len(w.get('topics', [])) for w in path.get('weeks', []))
                st.metric("📚 Topics", total_topics)
            with col_d:
                st.metric("🎯 Skill Level", skill_level)

            st.markdown("<br>", unsafe_allow_html=True)

            # Get progress if path has an ID
            path_id = path.get('id')
            progress_data = {"completed": set(), "total_completed": 0}
            if user_id and path_id:
                progress_data = generator.get_progress(user_id, path_id)

            # Overall progress bar
            if total_topics > 0:
                pct = (progress_data['total_completed'] / total_topics) * 100
                st.markdown(f"**Overall Progress: {pct:.0f}% ({progress_data['total_completed']}/{total_topics} topics)**")
                st.progress(pct / 100)
                st.markdown("<br>", unsafe_allow_html=True)

            # Weekly roadmap
            st.markdown("### 📅 Weekly Roadmap")
            weeks = path.get('weeks', [])
            for week in weeks:
                render_week_card(week, progress_data['completed'], path_id, user_id, generator)

            # Final project & career outcomes
            col_x, col_y = st.columns(2)
            with col_x:
                if path.get('final_project'):
                    st.markdown(f"""
                        <div style="
                            background: rgba(245, 158, 11, 0.1);
                            border: 2px solid #f59e0b;
                            border-radius: 12px;
                            padding: 20px;
                        ">
                            <h4 style="color: #f59e0b; margin: 0 0 10px 0;">🏆 Final Project</h4>
                            <p style="color: rgba(255,255,255,0.9); margin: 0;">{path['final_project']}</p>
                        </div>
                    """, unsafe_allow_html=True)

            with col_y:
                outcomes = path.get('career_outcomes', [])
                if outcomes:
                    st.markdown(f"""
                        <div style="
                            background: rgba(102, 126, 234, 0.1);
                            border: 2px solid #667eea;
                            border-radius: 12px;
                            padding: 20px;
                        ">
                            <h4 style="color: #667eea; margin: 0 0 10px 0;">💼 Career Outcomes</h4>
                            {''.join(f'<p style="color: rgba(255,255,255,0.9); margin: 5px 0;">✅ {o}</p>' for o in outcomes)}
                        </div>
                    """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 📚 Your Saved Learning Paths")

        if not user_id:
            st.info("Login to see your saved paths")
        else:
            paths = generator.get_user_paths(user_id)
            if not paths:
                st.info("No learning paths yet. Generate one in the first tab!")
            else:
                for p in paths:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"""
                            <div style="
                                background: rgba(255,255,255,0.05);
                                border: 1px solid rgba(255,255,255,0.1);
                                border-radius: 10px;
                                padding: 15px;
                                margin: 8px 0;
                            ">
                                <strong style="color: #ffffff;">{p['goal']}</strong><br>
                                <span style="color: rgba(255,255,255,0.6); font-size: 0.85em;">
                                    {p['skill_level']} • {p['weeks']} weeks • Created {p['created_at'][:10]}
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        if st.button("Load", key=f"load_path_{p['id']}", use_container_width=True):
                            full_path = generator.get_path_by_id(p['id'])
                            if full_path:
                                full_path['id'] = p['id']
                                st.session_state.current_path = full_path
                                st.rerun()


if __name__ == "__main__":
    main()
