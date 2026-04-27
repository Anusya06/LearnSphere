"""
Analytics Page - Real-time Learning Progress Dashboard
Displays actual user data from database
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))

from components.ui_components import stat_card, animated_progress_bar
from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.learning_progress import get_learning_db

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
apply_theme()
load_theme_css()
apply_sidebar_fix()


def render_empty_state():
    """Show empty state when no data exists"""
    st.markdown("""
        <div style="
            text-align: center;
            padding: 80px 20px;
            background: linear-gradient(135deg, #667eea22 0%, #764ba244 100%);
            border-radius: 20px;
            margin: 40px 0;
        ">
            <div style="font-size: 5em; margin-bottom: 20px;">📊</div>
            <h2 style="color: #667eea; margin-bottom: 15px;">No Analytics Data Yet</h2>
            <p style="color: #b0b0b0; font-size: 1.2em; margin-bottom: 30px;">
                Start learning, take quizzes, and complete topics to see your analytics here!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Start Learning", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Learn.py")
    with col2:
        if st.button("📝 Take a Quiz", use_container_width=True):
            st.switch_page("pages/3_Quiz.py")


def render_learning_summary(summary):
    """Render learning summary cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:25px;border-radius:15px;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.1)">
                <div style="font-size:2.5em;margin-bottom:10px">📚</div>
                <h2 style="margin:0;color:white;font-size:2.5em">{summary['topics_learned']}</h2>
                <p style="margin:5px 0 0 0;color:rgba(255,255,255,0.9);font-size:1.1em">Topics Learned</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);padding:25px;border-radius:15px;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.1)">
                <div style="font-size:2.5em;margin-bottom:10px">📝</div>
                <h2 style="margin:0;color:white;font-size:2.5em">{summary['quizzes_attempted']}</h2>
                <p style="margin:5px 0 0 0;color:rgba(255,255,255,0.9);font-size:1.1em">Quizzes Attempted</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);padding:25px;border-radius:15px;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.1)">
                <div style="font-size:2.5em;margin-bottom:10px">🎯</div>
                <h2 style="margin:0;color:white;font-size:2.5em">{summary['average_score']:.0f}%</h2>
                <p style="margin:5px 0 0 0;color:rgba(255,255,255,0.9);font-size:1.1em">Average Score</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        latest_topic = summary['latest_topic']
        if len(latest_topic) > 20:
            latest_topic = latest_topic[:17] + "..."
        
        st.markdown(f"""
            <div style="background:linear-gradient(135deg,#ef4444 0%,#dc2626 100%);padding:25px;border-radius:15px;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.1)">
                <div style="font-size:2.5em;margin-bottom:10px">🔥</div>
                <h2 style="margin:0;color:white;font-size:1.3em">{latest_topic}</h2>
                <p style="margin:5px 0 0 0;color:rgba(255,255,255,0.9);font-size:1.1em">Latest Topic</p>
            </div>
        """, unsafe_allow_html=True)


def render_topics_learned(topics):
    """Render topics learned table"""
    st.markdown("### 📚 Topics Learned")
    
    if not topics:
        st.info("No topics learned yet. Start generating content on the Learn page!")
        return
    
    # Create DataFrame
    df_data = []
    for topic in topics:
        try:
            date_obj = datetime.fromisoformat(topic['created_at'])
            date_str = date_obj.strftime("%Y-%m-%d %H:%M")
        except:
            date_str = topic['created_at']
        
        df_data.append({
            "Topic Name": topic['topic_name'],
            "Difficulty": topic['difficulty'],
            "Date Learned": date_str
        })
    
    df = pd.DataFrame(df_data)
    
    # Display as styled table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Topic Name": st.column_config.TextColumn("Topic Name", width="large"),
            "Difficulty": st.column_config.TextColumn("Difficulty", width="small"),
            "Date Learned": st.column_config.TextColumn("Date Learned", width="medium")
        }
    )


def render_quiz_performance(quiz_results):
    """Render quiz performance table"""
    st.markdown("### 📝 Quiz Performance")
    
    if not quiz_results:
        st.info("No quiz attempts yet. Take a quiz to see your performance!")
        return
    
    # Create DataFrame
    df_data = []
    for quiz in quiz_results:
        try:
            date_obj = datetime.fromisoformat(quiz['attempted_at'])
            date_str = date_obj.strftime("%Y-%m-%d %H:%M")
        except:
            date_str = quiz['attempted_at']
        
        df_data.append({
            "Topic": quiz['topic'],
            "Score": f"{quiz['score']}/{quiz['total_questions']}",
            "Percentage": f"{quiz['percentage']:.0f}%",
            "Time Taken": f"{quiz['time_taken']}s" if quiz['time_taken'] else "N/A",
            "Date": date_str
        })
    
    df = pd.DataFrame(df_data)
    
    # Display as styled table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Topic": st.column_config.TextColumn("Topic", width="large"),
            "Score": st.column_config.TextColumn("Score", width="small"),
            "Percentage": st.column_config.TextColumn("Percentage", width="small"),
            "Time Taken": st.column_config.TextColumn("Time", width="small"),
            "Date": st.column_config.TextColumn("Date", width="medium")
        }
    )


def render_progress_chart(quiz_trend):
    """Render quiz score progress chart"""
    st.markdown("### 📈 Quiz Score Progress")
    
    if not quiz_trend or len(quiz_trend) < 2:
        st.info("Take at least 2 quizzes to see your progress trend!")
        return
    
    # Prepare data
    dates = []
    scores = []
    topics = []
    
    for i, quiz in enumerate(quiz_trend, 1):
        try:
            date_obj = datetime.fromisoformat(quiz['attempted_at'])
            dates.append(date_obj.strftime("%m/%d"))
        except:
            dates.append(f"Quiz {i}")
        
        scores.append(quiz['percentage'])
        topics.append(quiz['topic'])
    
    # Create chart
    fig = go.Figure()
    
    # Add score line
    fig.add_trace(go.Scatter(
        x=dates,
        y=scores,
        mode='lines+markers',
        name='Quiz Score',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10, color='#667eea'),
        text=topics,
        hovertemplate='<b>%{text}</b><br>Score: %{y:.1f}%<extra></extra>'
    ))
    
    # Add trend line if enough data
    if len(scores) >= 3:
        z = np.polyfit(range(len(scores)), scores, 1)
        p = np.poly1d(z)
        trend_scores = p(range(len(scores)))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=trend_scores,
            mode='lines',
            name='Trend',
            line=dict(color='#10b981', width=2, dash='dash'),
            hovertemplate='Trend: %{y:.1f}%<extra></extra>'
        ))
    
    # Add average line
    avg_score = sum(scores) / len(scores)
    fig.add_hline(
        y=avg_score,
        line_dash="dot",
        line_color="#f59e0b",
        annotation_text=f"Average: {avg_score:.1f}%",
        annotation_position="right"
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            title="Quiz Attempts"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            title="Score (%)",
            range=[0, 105]
        ),
        font=dict(family="Inter", size=12),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_recent_activity(activities):
    """Render recent activity feed"""
    st.markdown("### 🕐 Recent Activity")
    
    if not activities:
        st.info("No recent activity. Start learning to see your activity here!")
        return
    
    for activity in activities:
        try:
            date_obj = datetime.fromisoformat(activity['timestamp'])
            time_str = date_obj.strftime("%b %d, %Y at %H:%M")
        except:
            time_str = activity['timestamp']
        
        # Choose icon and color based on type
        if activity['type'] == 'topic':
            icon = "📚"
            color = "#667eea"
        else:
            icon = "📝"
            color = "#10b981"
        
        st.markdown(f"""
            <div style="background:#1e1e1e;padding:15px;border-radius:10px;margin:10px 0;border-left:4px solid {color}">
                <div style="display:flex;align-items:center;gap:10px">
                    <span style="font-size:1.5em">{icon}</span>
                    <div style="flex:1">
                        <p style="margin:0;color:#fafafa;font-weight:500">{activity['description']}</p>
                        <p style="margin:5px 0 0 0;color:#888;font-size:0.9em">{time_str}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_analytics():
    """Main analytics rendering function"""
    st.markdown("# 📊 Learning Analytics")
    st.markdown("Track your progress and identify areas for improvement")
    st.markdown("---")
    
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("User ID not found. Please login again.")
        return
    
    # Get database instance
    db = get_learning_db()
    
    # Get analytics data
    summary = db.get_analytics_summary(user_id)
    
    # Check if user has any data
    if summary['topics_learned'] == 0 and summary['quizzes_attempted'] == 0:
        render_empty_state()
        return
    
    # Section 1: Learning Summary
    render_learning_summary(summary)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create two columns for main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Section 4: Progress Chart
        quiz_trend = db.get_quiz_performance_trend(user_id, limit=15)
        render_progress_chart(quiz_trend)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Section 2: Topics Learned
        topics = db.get_learning_topics(user_id, limit=20)
        render_topics_learned(topics)
    
    with col2:
        # Section 5: Recent Activity
        activities = db.get_recent_activity(user_id, limit=10)
        render_recent_activity(activities)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 3: Quiz Performance (full width)
    quiz_results = db.get_quiz_results(user_id, limit=20)
    render_quiz_performance(quiz_results)


def main():
    if not check_authentication():
        st.warning("Please login to view analytics")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()
    
    render_analytics()


if __name__ == "__main__":
    main()
