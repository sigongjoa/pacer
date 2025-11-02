from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from datetime import date, timedelta
from typing import List, Optional # Optional 추가

import models
import schemas
import anki_engine

async def get_llm_logs(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(models.LLMLog).order_by(models.LLMLog.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

async def create_llm_log(db: AsyncSession, submission_id: int, decision: str, reason: str) -> models.LLMLog:
    db_log = models.LLMLog(submission_id=submission_id, decision=decision, reason=reason)
    db.add(db_log)
    await db.flush()
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
        await db.flush()
        await db.refresh(db_log)
    return db_log

async def create_anki_card(db: AsyncSession, card: schemas.AnkiCardCreate) -> models.AnkiCard:
    next_review_date, interval_days, ease_factor, repetitions = anki_engine.get_initial_anki_schedule()
    db_card = models.AnkiCard(
        student_id=card.student_id,
        llm_log_id=card.llm_log_id,
        question=card.question,
        answer=card.answer,
        next_review_date=next_review_date,
        interval_days=interval_days,
        ease_factor=int(ease_factor * 100), # Convert float to int for storage
        repetitions=repetitions
    )
    db.add(db_card)
    await db.flush()
    await db.refresh(db_card)
    return db_card

async def update_anki_card_schedule(db: AsyncSession, card_id: int, quality: int) -> models.AnkiCard:
    result = await db.execute(select(models.AnkiCard).where(models.AnkiCard.card_id == card_id))
    db_card = result.scalars().first()
    if db_card:
        repetitions, interval, ease_factor = anki_engine.calculate_sm2_schedule(
            db_card.repetitions, db_card.interval_days, db_card.ease_factor / 100, quality
        )
        db_card.repetitions = repetitions
        db_card.interval_days = interval
        db_card.ease_factor = int(ease_factor * 100)
        db_card.next_review_date = date.today() + timedelta(days=interval)
        db_card.last_reviewed_at = func.now()
        await db.flush()
        await db.refresh(db_card)
    return db_card

async def create_student(db: AsyncSession, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(
        student_id=student.student_id,
        name=student.name,
        settings=student.settings
    )
    db.add(db_student)
    await db.flush()
    await db.refresh(db_student)
    return db_student

async def get_student(db: AsyncSession, student_id: str) -> Optional[models.Student]:
    result = await db.execute(select(models.Student).where(models.Student.student_id == student_id))
    return result.scalars().first()

async def get_students(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Student]:
    result = await db.execute(select(models.Student).offset(skip).limit(limit))
    return result.scalars().all()

async def update_student(db: AsyncSession, student_id: str, student: schemas.StudentUpdate) -> Optional[models.Student]:
    db_student = await get_student(db, student_id=student_id)
    if db_student:
        db_student.settings = student.settings
        await db.flush()
        await db.refresh(db_student)
    return db_student

async def get_due_anki_cards(db: AsyncSession, student_id: str, today: date) -> List[models.AnkiCard]:
    result = await db.execute(
        select(models.AnkiCard)
        .where(models.AnkiCard.student_id == student_id)
        .where(models.AnkiCard.next_review_date <= today)
        .order_by(models.AnkiCard.next_review_date, models.AnkiCard.ease_factor.asc())
    )
    return result.scalars().all()

async def create_coach_memo(db: AsyncSession, memo: schemas.CoachMemoCreate) -> models.CoachMemo:
    db_memo = models.CoachMemo(
        coach_id=memo.coach_id,
        student_id=memo.student_id,
        memo_text=memo.memo_text
    )
    db.add(db_memo)
    await db.flush()
    await db.refresh(db_memo)
    return db_memo

async def get_coach_memos(db: AsyncSession, student_id: str, coach_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[models.CoachMemo]:
    query = select(models.CoachMemo).where(models.CoachMemo.student_id == student_id)
    if coach_id:
        query = query.where(models.CoachMemo.coach_id == coach_id)
    query = query.order_by(models.CoachMemo.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_weekly_report(db: AsyncSession, report_data: schemas.WeeklyReportResponse) -> models.WeeklyReport:
    # Convert Pydantic models to dictionaries for JSON serialization
    anki_summaries = [s.model_dump() for s in report_data.anki_card_summaries]
    llm_summaries = [s.model_dump() for s in report_data.llm_log_summaries]
    coach_summaries = [s.model_dump() for s in report_data.coach_memo_summaries]

    db_report = models.WeeklyReport(
        student_id=report_data.student_id,
        report_period_start=report_data.report_period_start,
        report_period_end=report_data.report_period_end,
        total_submissions=report_data.total_submissions,
        llm_judgments_count=report_data.llm_judgments_count,
        anki_cards_reviewed_count=report_data.anki_cards_reviewed_count,
        new_anki_cards_created_count=report_data.new_anki_cards_created_count,
        anki_card_summaries=anki_summaries,
        llm_log_summaries=llm_summaries,
        coach_memo_summaries=coach_summaries,
        overall_summary=report_data.overall_summary,
        status='draft'
    )
    db.add(db_report)
    await db.flush()
    await db.refresh(db_report)
    return db_report

async def get_weekly_report(db: AsyncSession, report_id: int) -> Optional[models.WeeklyReport]:
    result = await db.execute(select(models.WeeklyReport).where(models.WeeklyReport.report_id == report_id))
    return result.scalars().first()

async def finalize_weekly_report(db: AsyncSession, report_id: int, final_data: schemas.WeeklyReportFinalize) -> Optional[models.WeeklyReport]:
    db_report = await get_weekly_report(db, report_id)
    if db_report and db_report.status == 'draft':
        db_report.coach_comment = final_data.coach_comment
        db_report.status = 'finalized'
        db_report.finalized_at = func.now()
        await db.flush()
        await db.refresh(db_report)
    return db_report
