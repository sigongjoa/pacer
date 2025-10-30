from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# AI Module Schemas
class ErrorContext(BaseModel):
    question_type: str
    concept_name: str
    student_mistake_summary: str

class AnalysisReport(BaseModel):
    score: float
    error_contexts: List[ErrorContext]

class AnalyzeRequest(BaseModel):
    submission_id: str
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

    class Config:
        orm_mode = True
