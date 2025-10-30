from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas

async def get_llm_logs(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(models.LLMLog).order_by(models.LLMLog.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

async def create_llm_log(db: AsyncSession, submission_id: int, decision: str, reason: str) -> models.LLMLog:
    db_log = models.LLMLog(submission_id=submission_id, decision=decision, reason=reason)
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def update_llm_log_feedback(db: AsyncSession, feedback: schemas.FeedbackRequest) -> models.LLMLog:
    result = await db.execute(select(models.LLMLog).where(models.LLMLog.log_id == int(feedback.log_id)))
    db_log = result.scalars().first()
    if db_log:
        db_log.coach_id = feedback.coach_id
        db_log.coach_feedback = feedback.feedback
        db_log.reason_code = feedback.reason_code
        db_log.memo = feedback.memo
        await db.commit()
        await db.refresh(db_log)
    return db_log
