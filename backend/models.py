from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
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
