"""
Analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database.database import get_db
from ..models.user import User
from ..models.topic import TopicProgress
from ..models.quiz import QuizAttempt
from ..schemas.schemas import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard/{user_id}", response_model=AnalyticsResponse)
def get_analytics_dashboard(user_id: int, db: Session = Depends(get_db)):
    """Get comprehensive analytics for user dashboard"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Total and completed topics
    total_topics = db.query(TopicProgress).filter(TopicProgress.user_id == user_id).count()
    completed_topics = db.query(TopicProgress).filter(
        TopicProgress.user_id == user_id,
        TopicProgress.is_completed == True
    ).count()
    
    # Quiz average
    quiz_avg = db.query(func.avg(QuizAttempt.percentage)).filter(
        QuizAttempt.user_id == user_id
    ).scalar() or 0.0
    
    # Weekly activity (last 7 days)
    weekly_activity = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        time_spent = db.query(func.sum(TopicProgress.time_spent)).filter(
            TopicProgress.user_id == user_id,
            TopicProgress.last_accessed >= day_start,
            TopicProgress.last_accessed < day_end
        ).scalar() or 0.0
        
        weekly_activity.append({
            "date": date.strftime("%Y-%m-%d"),
            "time_spent": time_spent
        })
    
    # Topic performance
    topic_performance = db.query(
        TopicProgress.topic_id,
        TopicProgress.completion_percentage,
        TopicProgress.time_spent
    ).filter(TopicProgress.user_id == user_id).all()
    
    topic_perf_list = [
        {
            "topic_id": tp.topic_id,
            "completion": tp.completion_percentage,
            "time_spent": tp.time_spent
        }
        for tp in topic_performance
    ]
    
    return AnalyticsResponse(
        total_topics=total_topics,
        completed_topics=completed_topics,
        total_time_spent=user.total_time_spent,
        quiz_average=quiz_avg,
        streak_count=user.streak_count,
        weekly_activity=weekly_activity,
        topic_performance=topic_perf_list
    )


@router.get("/quiz-history/{user_id}")
def get_quiz_history(user_id: int, db: Session = Depends(get_db)):
    """Get quiz performance history"""
    
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == user_id
    ).order_by(QuizAttempt.completed_at.desc()).all()
    
    return {
        "attempts": [
            {
                "quiz_id": a.quiz_id,
                "score": a.score,
                "percentage": a.percentage,
                "time_taken": a.time_taken,
                "completed_at": a.completed_at
            }
            for a in attempts
        ]
    }
