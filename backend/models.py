from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Date, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

student_parent_association = Table(
    'student_parent_association',
    Base.metadata,
    Column('student_id', String, ForeignKey('students.student_id'), primary_key=True),
    Column('parent_id', Integer, ForeignKey('parents.parent_id'), primary_key=True)
)

class Parent(Base):
    __tablename__ = "parents"

    parent_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    kakao_user_id = Column(String, unique=True, index=True, nullable=True)

    students = relationship(
        "Student",
        secondary=student_parent_association,
        back_populates="parents"
    )

class LLMLog(Base):
    __tablename__ = "llm_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(String, nullable=False)
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
    created_at = Column(TIMESTAMP, server_default=func.now())

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    settings = Column(JSON, nullable=False, default={})
    parents = relationship(
        "Parent",
        secondary=student_parent_association,
        back_populates="students"
    )

class CoachMemo(Base):
    __tablename__ = "coach_memos"

    memo_id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(String, nullable=False)
    student_id = Column(String, nullable=False)
    memo_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    report_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    student_name = Column(String, nullable=False)
    report_period_start = Column(Date, nullable=False)
    report_period_end = Column(Date, nullable=False)
    
    # Data Snapshots
    total_submissions = Column(Integer, nullable=False)
    llm_judgments_count = Column(Integer, nullable=False)
    anki_cards_reviewed_count = Column(Integer, nullable=False)
    new_anki_cards_created_count = Column(Integer, nullable=False)
    anki_card_summaries = Column(JSON, nullable=False)
    llm_log_summaries = Column(JSON, nullable=False)
    coach_memo_summaries = Column(JSON, nullable=False)
    
    # Summaries & Comments
    overall_summary = Column(Text, nullable=False)
    coach_comment = Column(Text, nullable=True)
    
    # Status
    status = Column(String, nullable=False, default='draft') # e.g., 'draft', 'finalized'
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    finalized_at = Column(TIMESTAMP, nullable=True)
