from pydantic import BaseModel, Field, ConfigDict # ConfigDict 추가
from typing import List, Dict, Any, Optional
from datetime import datetime, date

# AI Module Schemas
class ErrorContext(BaseModel):
    question_type: str
    concept_name: str
    student_mistake_summary: str

class AnalysisReport(BaseModel):
    score: float
    error_contexts: List[ErrorContext]

class AnalyzeRequest(BaseModel):
    submission_id: int
    raw_answers: Dict[str, Any]

# LLMFilter Schemas
class JudgeRequest(BaseModel):
    student_id: str
    submission_id: int
    error_context: ErrorContext

class JudgeResponse(BaseModel):
    log_id: str
    decision: str
    reason: str

class FeedbackRequest(BaseModel):
    log_id: str
    coach_id: str
    feedback: str # "GOOD" or "BAD"
    reason_code: Optional[str] = None # e.g., "SIMPLE_MISTAKE"
    memo: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str
    log_id: str

class LLMLogResponse(BaseModel):
    log_id: int
    submission_id: int
    decision: str
    reason: Optional[str]
    coach_feedback: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) # 추가

# Anki Card Schemas
class AnkiCardCreate(BaseModel):
    student_id: str
    llm_log_id: int
    question: str
    answer: str

class AnkiCardResponse(BaseModel):
    card_id: int
    student_id: str
    llm_log_id: int
    question: str
    answer: str
    next_review_date: date
    interval_days: int
    ease_factor: int
    repetitions: int
    last_reviewed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True) # 추가

class CardReviewRequest(BaseModel):
    quality: int = Field(..., ge=0, le=5, description="Student\'s self-assessed quality of recall (0-5). 5: perfect recall, 0: complete blackout.")

# Student Schemas
class StudentCreate(BaseModel):
    student_id: str
    name: str
    settings: Dict[str, Any] = {}

class StudentResponse(BaseModel):
    student_id: str
    name: str
    settings: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True) # 추가

class StudentUpdate(BaseModel):
    settings: Dict[str, Any]

# Pacer Brain Schemas
class DailyReviewDeckResponse(BaseModel):
    student_id: str
    due_cards: List[AnkiCardResponse]
    budget_applied: bool
    total_due: int
    cards_in_deck: int
