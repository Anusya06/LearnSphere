"""
Learning content API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..models.topic import Topic, TopicProgress, Bookmark, Note
from ..models.user import User
from ..schemas.schemas import TopicCreate, TopicResponse, ProgressUpdate
from ..services.ai_service import AIService

router = APIRouter(prefix="/learning", tags=["Learning"])
ai_service = AIService()


@router.post("/topics", response_model=TopicResponse)
def create_topic(topic_data: TopicCreate, db: Session = Depends(get_db)):
    """Create a new learning topic with AI-generated content"""
    
    # Generate AI content
    text_content = ai_service.generate_content(
        topic_data.title,
        topic_data.difficulty,
        topic_data.depth
    )
    
    roadmap = ai_service.generate_roadmap(
        topic_data.title,
        topic_data.difficulty,
        topic_data.depth
    )
    
    code_example = ai_service.generate_code(
        topic_data.title,
        topic_data.difficulty,
        topic_data.depth
    )
    
    # Create topic
    new_topic = Topic(
        title=topic_data.title,
        difficulty=topic_data.difficulty,
        depth=topic_data.depth,
        text_content=text_content,
        roadmap_json=roadmap,
        code_example=code_example
    )
    
    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)
    
    return new_topic


@router.get("/topics", response_model=List[TopicResponse])
def get_topics(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Get all topics"""
    topics = db.query(Topic).offset(skip).limit(limit).all()
    return topics


@router.get("/topics/{topic_id}", response_model=TopicResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """Get a specific topic"""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.post("/progress")
def update_progress(progress_data: ProgressUpdate, user_id: int, db: Session = Depends(get_db)):
    """Update user's learning progress"""
    
    # Get or create progress record
    progress = db.query(TopicProgress).filter(
        TopicProgress.user_id == user_id,
        TopicProgress.topic_id == progress_data.topic_id
    ).first()
    
    if not progress:
        progress = TopicProgress(
            user_id=user_id,
            topic_id=progress_data.topic_id
        )
        db.add(progress)
    
    # Update fields
    if progress_data.completion_percentage is not None:
        progress.completion_percentage = progress_data.completion_percentage
    if progress_data.time_spent is not None:
        progress.time_spent += progress_data.time_spent
    if progress_data.is_completed is not None:
        progress.is_completed = progress_data.is_completed
    if progress_data.milestones_completed is not None:
        progress.milestones_completed = progress_data.milestones_completed
    
    # Update user's total time
    user = db.query(User).filter(User.id == user_id).first()
    if user and progress_data.time_spent:
        user.total_time_spent += progress_data.time_spent / 60  # Convert to hours
    
    db.commit()
    
    return {"message": "Progress updated successfully"}


@router.post("/bookmarks/{topic_id}")
def add_bookmark(topic_id: int, user_id: int, db: Session = Depends(get_db)):
    """Bookmark a topic"""
    
    # Check if already bookmarked
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == user_id,
        Bookmark.topic_id == topic_id
    ).first()
    
    if existing:
        return {"message": "Already bookmarked"}
    
    bookmark = Bookmark(user_id=user_id, topic_id=topic_id)
    db.add(bookmark)
    db.commit()
    
    return {"message": "Bookmark added"}


@router.delete("/bookmarks/{topic_id}")
def remove_bookmark(topic_id: int, user_id: int, db: Session = Depends(get_db)):
    """Remove bookmark"""
    
    bookmark = db.query(Bookmark).filter(
        Bookmark.user_id == user_id,
        Bookmark.topic_id == topic_id
    ).first()
    
    if bookmark:
        db.delete(bookmark)
        db.commit()
    
    return {"message": "Bookmark removed"}


@router.post("/chat")
def chat_with_tutor(question: str, context: str = "", db: Session = Depends(get_db)):
    """Chat with AI tutor"""
    response = ai_service.chat_tutor(question, context)
    return {"response": response}
