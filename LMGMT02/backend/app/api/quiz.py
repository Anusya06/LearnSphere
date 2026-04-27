"""
Quiz API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database.database import get_db
from ..models.quiz import Quiz, QuizAttempt
from ..models.user import User
from ..schemas.schemas import QuizCreate, QuizAttemptCreate, QuizAttemptResponse
from ..services.ai_service import AIService

router = APIRouter(prefix="/quiz", tags=["Quiz"])
ai_service = AIService()


@router.post("/create")
def create_quiz(quiz_data: QuizCreate, db: Session = Depends(get_db)):
    """Create a new quiz"""
    
    new_quiz = Quiz(
        topic_id=quiz_data.topic_id,
        title=quiz_data.title,
        difficulty=quiz_data.difficulty,
        time_limit=quiz_data.time_limit,
        questions_json=quiz_data.questions_json
    )
    
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    return new_quiz


@router.post("/generate/{topic_id}")
def generate_quiz(topic_id: int, difficulty: str, db: Session = Depends(get_db)):
    """Generate quiz using AI"""
    from ..models.topic import Topic
    
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Generate quiz questions
    quiz_data = ai_service.generate_quiz(topic.title, difficulty, topic.depth)
    
    new_quiz = Quiz(
        topic_id=topic_id,
        title=f"{topic.title} Quiz",
        difficulty=difficulty,
        time_limit=600,  # 10 minutes default
        questions_json=quiz_data
    )
    
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    return new_quiz


@router.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get quiz details"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/submit", response_model=QuizAttemptResponse)
def submit_quiz(attempt_data: QuizAttemptCreate, user_id: int, db: Session = Depends(get_db)):
    """Submit quiz attempt and get score"""
    
    quiz = db.query(Quiz).filter(Quiz.id == attempt_data.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Score the quiz
    score, max_score, feedback = score_quiz_attempt(
        quiz.questions_json,
        attempt_data.answers_json
    )
    
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    # Create attempt record
    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=attempt_data.quiz_id,
        answers_json=attempt_data.answers_json,
        score=score,
        max_score=max_score,
        percentage=percentage,
        time_taken=attempt_data.time_taken,
        feedback_json={"feedback": feedback},
        completed_at=datetime.utcnow()
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt


@router.get("/attempts/{user_id}", response_model=List[QuizAttemptResponse])
def get_user_attempts(user_id: int, db: Session = Depends(get_db)):
    """Get all quiz attempts for a user"""
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all()
    return attempts


def score_quiz_attempt(questions: dict, answers: dict):
    """Score quiz and provide feedback"""
    questions_list = questions.get("questions", [])
    total_score = 0.0
    max_score = 0.0
    feedback = []
    
    difficulty_weights = {"easy": 1.0, "medium": 1.5, "hard": 2.0}
    
    for q in questions_list:
        qid = q["id"]
        correct_answer = str(q["answer"]).strip()
        user_answer = str(answers.get(qid, "")).strip()
        weight = difficulty_weights.get(q.get("difficulty", "easy"), 1.0)
        max_score += weight
        
        is_correct = False
        if q["type"] == "true_false":
            is_correct = user_answer.lower() == correct_answer.lower()
        elif q["type"] == "mcq":
            is_correct = user_answer == correct_answer
        else:
            is_correct = correct_answer.lower() in user_answer.lower()
        
        if is_correct:
            total_score += weight
        
        feedback.append({
            "id": qid,
            "question": q["question"],
            "correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "explanation": q.get("explanation", "")
        })
    
    return total_score, max_score, feedback
