from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Date, JSON
from sqlalchemy.sql import func
from database import Base

class LLMLog(Base):
    __tablename__ = "llm_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, nullable=False)
    coach_id = Column(String, nullable=True)
    decision = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    coach_feedback = Column(String, nullable=True)
    reason_code = Column(String, nullable=True)
    memo = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class AnkiCard(Base):
    __tablename__ = "anki_cards"

    card_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, nullable=False)
    llm_log_id = Column(Integer, ForeignKey("llm_logs.log_id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    next_review_date = Column(Date, nullable=False)
    interval_days = Column(Integer, default=0, nullable=False)
    ease_factor = Column(Integer, default=250, nullable=False) # SM2 ease factor (250 = 2.5)
    repetitions = Column(Integer, default=0, nullable=False) # SM2 repetitions
    last_reviewed_at = Column(TIMESTAMP, nullable=True)

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    settings = Column(JSON, nullable=False, default={})
