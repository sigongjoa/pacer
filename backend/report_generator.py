from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, timedelta, datetime
from typing import List, Optional

import schemas
import models
import crud

async def generate_weekly_report_draft(
    db: AsyncSession,
    student_id: str,
    start_date: date,
    end_date: date
) -> schemas.WeeklyReportResponse:
    student = await crud.get_student(db, student_id=student_id)
    if not student:
        raise ValueError("Student not found")

    # Fetch LLM Logs for the period
    llm_logs_query = select(models.LLMLog).where(
        models.LLMLog.created_at.between(start_date, end_date + timedelta(days=1)) # +1 day to include end_date
    ).order_by(models.LLMLog.created_at.desc())
    llm_logs_result = await db.execute(llm_logs_query)
    llm_logs = llm_logs_result.scalars().all()

    # Fetch Anki Cards reviewed or created in the period
    anki_cards_query = select(models.AnkiCard).where(
        models.AnkiCard.student_id == student_id,
        (models.AnkiCard.created_at.between(start_date, end_date + timedelta(days=1))) | 
        (models.AnkiCard.last_reviewed_at.between(start_date, end_date + timedelta(days=1)))
    ).order_by(models.AnkiCard.created_at.desc())
    anki_cards_result = await db.execute(anki_cards_query)
    anki_cards = anki_cards_result.scalars().all()

    # Fetch Coach Memos for the period
    coach_memos_query = select(models.CoachMemo).where(
        models.CoachMemo.student_id == student_id,
        models.CoachMemo.created_at.between(start_date, end_date + timedelta(days=1))
    ).order_by(models.CoachMemo.created_at.desc())
    coach_memos_result = await db.execute(coach_memos_query)
    coach_memos = coach_memos_result.scalars().all()

    # Aggregate data
    total_submissions = 0 # We don't have a Submission model yet, so this is a placeholder
    llm_judgments_count = len(llm_logs)
    anki_cards_reviewed_count = sum(1 for card in anki_cards if card.last_reviewed_at and card.last_reviewed_at.date() >= start_date and card.last_reviewed_at.date() <= end_date)
    new_anki_cards_created_count = sum(1 for card in anki_cards if card.created_at and card.created_at.date() >= start_date and card.created_at.date() <= end_date)

    anki_card_summaries = [schemas.ReportAnkiCardSummary.model_validate(card) for card in anki_cards]
    llm_log_summaries = [schemas.ReportLLMLogSummary.model_validate(log) for log in llm_logs]
    coach_memo_summaries = [schemas.ReportCoachMemoSummary.model_validate(memo) for memo in coach_memos]

    # Generate a simple overall summary
    overall_summary = f"{student.name} 학생의 {start_date}부터 {end_date}까지의 주간 학습 리포트입니다.\n"
    overall_summary += f"총 {llm_judgments_count}건의 AI 판단이 있었고, 이 중 {new_anki_cards_created_count}개의 새로운 Anki 카드가 생성되었습니다.\n"
    overall_summary += f"총 {anki_cards_reviewed_count}개의 Anki 카드를 복습했습니다.\n"
    if coach_memos:
        overall_summary += f"{len(coach_memos)}건의 코치 메모가 기록되었습니다.\n"

    return schemas.WeeklyReportResponse(
        student_id=student_id,
        student_name=student.name,
        report_period_start=start_date,
        report_period_end=end_date,
        total_submissions=total_submissions,
        llm_judgments_count=llm_judgments_count,
        anki_cards_reviewed_count=anki_cards_reviewed_count,
        new_anki_cards_created_count=new_anki_cards_created_count,
        anki_card_summaries=anki_card_summaries,
        llm_log_summaries=llm_log_summaries,
        coach_memo_summaries=coach_memo_summaries,
        overall_summary=overall_summary
    )
