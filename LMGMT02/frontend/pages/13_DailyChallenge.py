"""
Daily Challenges Page
Daily coding, quiz, and concept challenges with streak tracking
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import date

sys.path.append(str(Path(__file__).parent.parent))

from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.daily_challenges import get_daily_challenge_system

st.set_page_config(
    page_title="Daily Challenge",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
load_theme_css()
apply_sidebar_fix()


def render_streak_banner(streak_info: dict, completed_today: bool):
    """Render streak banner"""
    current = streak_info.get('current', 0)
    longest = streak_info.get('longest', 0)
    total = streak_info.get('total', 0)

    if completed_today:
        bg = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
        msg = "✅ Challenge completed today! Come back tomorrow to keep your streak!"
        icon = "🏆"
    elif current > 0:
        bg = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
        msg = "Complete today's challenge to maintain your streak!"
        icon = "🔥"
    else:
        bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        msg = "Start your daily challenge streak today!"
        icon = "🚀"

    st.markdown(f"""
        <div style="
            background: {bg};
            padding: 25px 30px;
            border-radius: 15px;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div>
                <h2 style="color: white; margin: 0; font-size: 1.8em;">{icon} {current}-Day Streak</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">{msg}</p>
            </div>
            <div style="text-align: right;">
                <div style="color: white; font-size: 0.9em; opacity: 0.9;">
                    🏆 Best: {longest} days &nbsp;|&nbsp; ✅ Total: {total} completed
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_coding_challenge(challenge: dict, completed: bool, user_id: int, system):
    """Render coding challenge"""
    data = challenge.get('data', {})

    st.markdown(f"""
        <div style="
            background: rgba(102, 126, 234, 0.1);
            border: 2px solid #667eea;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        ">
            <p style="color: rgba(255,255,255,0.9); line-height: 1.7; margin: 0;">
                {challenge.get('description', '')}
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Example Input:** `{data.get('example_input', 'N/A')}`")
    with col_b:
        st.markdown(f"**Expected Output:** `{data.get('example_output', 'N/A')}`")

    st.markdown("<br>", unsafe_allow_html=True)

    if not completed:
        user_code = st.text_area(
            "Your Solution",
            value=data.get('starter_code', ''),
            height=200,
            key="daily_code"
        )

        col_hint, col_submit = st.columns(2)
        with col_hint:
            if st.button("💡 Show Hint", use_container_width=True):
                hints = data.get('hints', [])
                if hints:
                    st.info(hints[0])

        with col_submit:
            if st.button("✅ Submit Solution", use_container_width=True, type="primary"):
                if user_code.strip():
                    system.mark_completed(user_id, challenge['id'], user_code, 100)
                    st.success("🎉 Challenge completed! +100 XP")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Please write your solution first")
    else:
        st.success("✅ You completed this challenge today!")
        with st.expander("👁️ View Solution"):
            st.code(data.get('solution', ''), language='python')


def render_quiz_challenge(challenge: dict, completed: bool, user_id: int, system):
    """Render quiz challenge"""
    data = challenge.get('data', {})

    st.markdown(f"""
        <div style="
            background: rgba(16, 185, 129, 0.1);
            border: 2px solid #10b981;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        ">
            <h3 style="color: #10b981; margin: 0 0 10px 0;">❓ {data.get('question', '')}</h3>
        </div>
    """, unsafe_allow_html=True)

    if not completed:
        answer = st.radio(
            "Select your answer",
            data.get('options', []),
            key="daily_quiz_answer",
            index=None,
            label_visibility="collapsed"
        )

        if st.button("✅ Submit Answer", use_container_width=True, type="primary", disabled=answer is None):
            correct = answer == data.get('correct_answer')
            score = 100 if correct else 50
            system.mark_completed(user_id, challenge['id'], answer, score)

            if correct:
                st.success(f"🎉 Correct! {data.get('explanation', '')}")
                st.balloons()
            else:
                st.error(f"❌ Incorrect. Correct answer: **{data.get('correct_answer')}**")
                st.info(data.get('explanation', ''))

            st.rerun()
    else:
        st.success("✅ You completed this challenge today!")
        st.info(f"**Correct Answer:** {data.get('correct_answer', 'N/A')}")
        st.markdown(data.get('explanation', ''))


def render_concept_challenge(challenge: dict, completed: bool, user_id: int, system):
    """Render concept challenge"""
    data = challenge.get('data', {})

    st.markdown(f"""
        <div style="
            background: rgba(245, 158, 11, 0.1);
            border: 2px solid #f59e0b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        ">
            <h3 style="color: #f59e0b; margin: 0 0 15px 0;">💡 {data.get('concept', '')}</h3>
            <p style="color: rgba(255,255,255,0.9); line-height: 1.7; margin: 0;">
                {data.get('explanation', '')}
            </p>
        </div>
    """, unsafe_allow_html=True)

    if data.get('example'):
        st.markdown("**Example:**")
        st.code(data['example'])

    key_points = data.get('key_points', [])
    if key_points:
        st.markdown("**Key Points:**")
        for point in key_points:
            st.markdown(f"""
                <div style="
                    background: rgba(245, 158, 11, 0.1);
                    border-left: 3px solid #f59e0b;
                    padding: 8px 12px;
                    border-radius: 6px;
                    margin: 5px 0;
                    color: rgba(255,255,255,0.9);
                ">• {point}</div>
            """, unsafe_allow_html=True)

    if data.get('question'):
        st.markdown(f"<br>**🤔 Reflection:** {data['question']}", unsafe_allow_html=True)

    if not completed:
        reflection = st.text_area("Your thoughts (optional)", height=100, key="daily_reflection")
        if st.button("✅ Mark as Learned", use_container_width=True, type="primary"):
            system.mark_completed(user_id, challenge['id'], reflection, 100)
            st.success("🎉 Great learning! +100 XP")
            st.balloons()
            st.rerun()
    else:
        st.success("✅ You completed this challenge today!")


def main():
    if not check_authentication():
        st.warning("Please login to access Daily Challenges")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()

    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <h1 style="color: white; margin: 0;">🔥 Daily Challenge</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;">
                A new challenge every day — build your streak and level up!
            </p>
        </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("user_id")
    system = get_daily_challenge_system()

    # Get today's challenge and user stats
    challenge = system.get_today_challenge()
    streak_info = system.get_streak_info(user_id) if user_id else {"current": 0, "longest": 0, "total": 0}
    completed_today = system.is_completed_today(user_id) if user_id else False

    # Streak banner
    render_streak_banner(streak_info, completed_today)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        if not challenge:
            st.error("Could not load today's challenge. Please refresh.")
            return

        # Challenge header
        type_config = {
            "coding": {"color": "#667eea", "icon": "💻", "label": "Coding Challenge"},
            "quiz": {"color": "#10b981", "icon": "❓", "label": "Quiz Challenge"},
            "concept": {"color": "#f59e0b", "icon": "💡", "label": "Concept of the Day"},
        }
        cfg = type_config.get(challenge.get('type', 'concept'), type_config['concept'])

        st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 20px;
            ">
                <div style="
                    background: {cfg['color']}22;
                    border: 2px solid {cfg['color']};
                    padding: 10px 20px;
                    border-radius: 10px;
                    color: {cfg['color']};
                    font-weight: 600;
                ">{cfg['icon']} {cfg['label']}</div>
                <div style="color: rgba(255,255,255,0.5); font-size: 0.9em;">
                    📅 {date.today().strftime('%B %d, %Y')}
                </div>
                {'<div style="background: #10b981; color: white; padding: 6px 14px; border-radius: 8px; font-size: 0.85em;">✅ Completed</div>' if completed_today else ''}
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"## {challenge.get('title', 'Daily Challenge')}")

        challenge_type = challenge.get('type', 'concept')

        if challenge_type == "coding":
            render_coding_challenge(challenge, completed_today, user_id, system)
        elif challenge_type == "quiz":
            render_quiz_challenge(challenge, completed_today, user_id, system)
        else:
            render_concept_challenge(challenge, completed_today, user_id, system)

    with col_right:
        # Stats card
        st.markdown("""
            <div style="
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            ">
                <h3 style="color: #ffffff; margin: 0 0 15px 0;">📊 Your Stats</h3>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("🔥 Streak", streak_info.get('current', 0))
        with col_b:
            st.metric("🏆 Best", streak_info.get('longest', 0))

        st.metric("✅ Total Done", streak_info.get('total', 0))
        st.markdown("</div>", unsafe_allow_html=True)

        # Completion history
        if user_id:
            history = system.get_completion_history(user_id, limit=7)
            if history:
                st.markdown("### 📅 Recent Activity")
                for item in history:
                    type_icons = {"coding": "💻", "quiz": "❓", "concept": "💡"}
                    icon = type_icons.get(item['type'], "✅")
                    st.markdown(f"""
                        <div style="
                            background: rgba(16, 185, 129, 0.1);
                            border-left: 3px solid #10b981;
                            padding: 8px 12px;
                            border-radius: 6px;
                            margin: 5px 0;
                        ">
                            <span style="color: #10b981;">{icon}</span>
                            <span style="color: rgba(255,255,255,0.8); font-size: 0.85em; margin-left: 8px;">
                                {item['date']}
                            </span><br>
                            <span style="color: rgba(255,255,255,0.6); font-size: 0.8em;">
                                {item['title'][:30]}...
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

        # Challenge type info
        st.markdown("""
            <div style="
                background: rgba(102, 126, 234, 0.1);
                border: 1px solid #667eea;
                border-radius: 12px;
                padding: 15px;
                margin-top: 15px;
            ">
                <h4 style="color: #667eea; margin: 0 0 10px 0;">📅 Challenge Schedule</h4>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.85em; margin: 0;">
                    💻 Mon/Thu: Coding<br>
                    ❓ Tue/Fri: Quiz<br>
                    💡 Wed/Sat/Sun: Concept
                </p>
            </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
