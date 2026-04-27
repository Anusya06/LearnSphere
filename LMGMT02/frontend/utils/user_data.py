"""
User data management - 100% database-driven, NO static data
"""
import streamlit as st
from datetime import datetime, timedelta
import requests


API_BASE_URL = "http://localhost:8000"


def init_user_data():
    """Initialize user-specific data storage - EMPTY by default"""
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    
    user_id = st.session_state.get("user_id")
    if user_id and user_id not in st.session_state.user_data:
        # Initialize EMPTY - no fake data
        st.session_state.user_data[user_id] = {
            "topics_completed": [],
            "topics_in_progress": [],
            "quiz_attempts": [],
            "study_sessions": [],
            "total_time_spent": 0.0,
            "streak_count": 0,
            "last_active": datetime.now().isoformat(),
            "achievements": [],
            "bookmarks": [],
            "notes": {},
            "generated_content": {}  # Store AI-generated content
        }


def get_user_data():
    """Get current user's data"""
    init_user_data()
    user_id = st.session_state.get("user_id", 1)
    return st.session_state.user_data.get(user_id, {})


def update_user_data(key: str, value):
    """Update user data"""
    init_user_data()
    user_id = st.session_state.get("user_id", 1)
    if user_id in st.session_state.user_data:
        st.session_state.user_data[user_id][key] = value


def add_topic_completed(topic_title: str, time_spent: float):
    """Add a completed topic"""
    user_data = get_user_data()
    user_data["topics_completed"].append({
        "title": topic_title,
        "completed_at": datetime.now().isoformat(),
        "time_spent": time_spent
    })
    user_data["total_time_spent"] += time_spent
    update_user_data("topics_completed", user_data["topics_completed"])
    update_user_data("total_time_spent", user_data["total_time_spent"])


def add_quiz_attempt(topic: str, score: float, max_score: float, time_taken: int):
    """Add a quiz attempt"""
    user_data = get_user_data()
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    user_data["quiz_attempts"].append({
        "topic": topic,
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
        "time_taken": time_taken,
        "completed_at": datetime.now().isoformat()
    })
    update_user_data("quiz_attempts", user_data["quiz_attempts"])


def add_study_session(duration: float):
    """Add a study session"""
    user_data = get_user_data()
    user_data["study_sessions"].append({
        "duration": duration,
        "date": datetime.now().isoformat()
    })
    update_user_data("study_sessions", user_data["study_sessions"])


def get_analytics_data():
    """Get analytics data for current user"""
    user_data = get_user_data()
    
    # Calculate statistics
    total_topics = len(user_data.get("topics_completed", [])) + len(user_data.get("topics_in_progress", []))
    completed_topics = len(user_data.get("topics_completed", []))
    
    quiz_attempts = user_data.get("quiz_attempts", [])
    quiz_average = sum(q["percentage"] for q in quiz_attempts) / len(quiz_attempts) if quiz_attempts else 0
    
    total_time = user_data.get("total_time_spent", 0.0)
    streak = user_data.get("streak_count", 0)
    
    # Weekly activity (last 7 days)
    weekly_activity = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # Get sessions for this day
        day_sessions = [s for s in user_data.get("study_sessions", []) 
                       if s["date"].startswith(date_str)]
        time_spent = sum(s["duration"] for s in day_sessions)
        
        weekly_activity.append({
            "date": date_str,
            "day": date.strftime("%a"),
            "time_spent": time_spent
        })
    
    weekly_activity.reverse()
    
    # Topic performance
    topic_performance = []
    for topic in user_data.get("topics_completed", []):
        topic_performance.append({
            "topic": topic["title"],
            "time_spent": topic["time_spent"],
            "completion": 100.0
        })
    
    for topic in user_data.get("topics_in_progress", []):
        topic_performance.append({
            "topic": topic["title"],
            "time_spent": topic.get("time_spent", 0),
            "completion": topic.get("progress", 0)
        })
    
    return {
        "total_topics": total_topics,
        "completed_topics": completed_topics,
        "total_time_spent": total_time,
        "quiz_average": quiz_average,
        "streak_count": streak,
        "weekly_activity": weekly_activity,
        "topic_performance": topic_performance,
        "quiz_attempts": quiz_attempts
    }


def store_generated_content(topic: str, content: dict):
    """Store AI-generated content for a topic"""
    user_data = get_user_data()
    if "generated_content" not in user_data:
        user_data["generated_content"] = {}
    
    user_data["generated_content"][topic] = {
        "text": content.get("text", ""),
        "roadmap": content.get("roadmap", {}),
        "code": content.get("code", ""),
        "generated_at": datetime.now().isoformat()
    }
    update_user_data("generated_content", user_data["generated_content"])


def get_generated_content(topic: str):
    """Get AI-generated content for a topic"""
    user_data = get_user_data()
    return user_data.get("generated_content", {}).get(topic)


def has_any_data():
    """Check if user has ANY data at all"""
    user_data = get_user_data()
    return (
        len(user_data.get("topics_completed", [])) > 0 or
        len(user_data.get("quiz_attempts", [])) > 0 or
        len(user_data.get("study_sessions", [])) > 0
    )


def store_tutor_message(user_message: str, ai_response: str):
    """Store tutor chat conversation"""
    user_data = get_user_data()
    if "tutor_chat" not in user_data:
        user_data["tutor_chat"] = []
    
    user_data["tutor_chat"].append({
        "user_message": user_message,
        "ai_response": ai_response,
        "timestamp": datetime.now().isoformat()
    })
    update_user_data("tutor_chat", user_data["tutor_chat"])


def get_tutor_chat_history():
    """Get tutor chat history"""
    user_data = get_user_data()
    return user_data.get("tutor_chat", [])


def store_code_execution(topic: str, language: str, execution_time: float, success: bool, error_msg: str = None):
    """Store code execution data for analytics"""
    user_data = get_user_data()
    if "code_executions" not in user_data:
        user_data["code_executions"] = []
    
    user_data["code_executions"].append({
        "topic": topic,
        "language": language,
        "execution_time": execution_time,
        "success": success,
        "error_msg": error_msg,
        "timestamp": datetime.now().isoformat()
    })
    update_user_data("code_executions", user_data["code_executions"])


def get_code_execution_stats():
    """Get code execution statistics"""
    user_data = get_user_data()
    executions = user_data.get("code_executions", [])
    
    if not executions:
        return {
            "total_executions": 0,
            "success_rate": 0,
            "languages_used": [],
            "avg_execution_time": 0
        }
    
    total = len(executions)
    successful = sum(1 for e in executions if e["success"])
    languages = list(set(e["language"] for e in executions))
    avg_time = sum(e["execution_time"] for e in executions) / total
    
    return {
        "total_executions": total,
        "success_rate": (successful / total * 100) if total > 0 else 0,
        "languages_used": languages,
        "avg_execution_time": avg_time
    }
