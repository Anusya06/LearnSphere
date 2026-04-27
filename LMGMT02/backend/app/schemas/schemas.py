"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============ User Schemas ============
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: str
    total_time_spent: float
    streak_count: int
    theme: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ============ Topic Schemas ============
class TopicCreate(BaseModel):
    title: str
    difficulty: str
    depth: str


class TopicResponse(BaseModel):
    id: int
    title: str
    difficulty: str
    depth: str
    text_content: Optional[str]
    roadmap_json: Optional[Dict]
    code_example: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProgressUpdate(BaseModel):
    topic_id: int
    completion_percentage: Optional[float] = None
    time_spent: Optional[float] = None
    is_completed: Optional[bool] = None
    milestones_completed: Optional[List[str]] = None


# ============ Quiz Schemas ============
class QuizCreate(BaseModel):
    topic_id: int
    title: str
    difficulty: str
    time_limit: Optional[int] = None
    questions_json: Dict


class QuizAttemptCreate(BaseModel):
    quiz_id: int
    answers_json: Dict
    time_taken: int


class QuizAttemptResponse(BaseModel):
    id: int
    score: float
    max_score: float
    percentage: float
    time_taken: int
    feedback_json: Dict
    completed_at: datetime

    class Config:
        from_attributes = True


# ============ Analytics Schemas ============
class AnalyticsResponse(BaseModel):
    total_topics: int
    completed_topics: int
    total_time_spent: float
    quiz_average: float
    streak_count: int
    weekly_activity: List[Dict[str, Any]]
    topic_performance: List[Dict[str, Any]]
