from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, timedelta, datetime
from typing import List, Optional
import json

import schemas
import models
import crud
from llm_filter import call_ollama_api # Import the LLM call function

async def generate_weekly_report_draft(
    db: AsyncSession,
    student_id: str,
    start_date: date,
    end_date: date
) -> models.WeeklyReport:
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

    # --- LLM-powered Overall Summary and Coach Comment Suggestion ---
    report_context = {
        "student_name": student.name,
        "report_period": f"{start_date} ~ {end_date}",
        "llm_judgments": [{
            "concept_name": log.concept_name,
            "decision": log.decision,
            "reason": log.reason,
            "coach_feedback": log.coach_feedback
        } for log in llm_logs],
        "anki_card_reviews": [{
            "question": card.question,
            "repetitions": card.repetitions,
            "next_review_date": card.next_review_date.isoformat() if card.next_review_date else None
        } for card in anki_cards if card.last_reviewed_at and card.last_reviewed_at.date() >= start_date and card.last_reviewed_at.date() <= end_date],
        "new_anki_cards": [{
            "question": card.question,
            "concept_name": llm_log.concept_name if (llm_log := next((l for l in llm_logs if l.log_id == card.llm_log_id), None)) else "N/A"
        } for card in anki_cards if card.created_at and card.created_at.date() >= start_date and card.created_at.date() <= end_date],
        "coach_memos": [{
            "memo_text": memo.memo_text,
            "created_at": memo.created_at.isoformat()
        } for memo in coach_memos]
    }

    llm_report_prompt = f"""[SYSTEM]
You are an AI assistant that generates insightful weekly learning reports for students and suggests coach comments. Your output must be in JSON format with two keys: "overall_summary" (string) and "coach_comment_suggestion" (string). Do not add any other text.

[INSTRUCTIONS]
- Analyze the provided student learning data for the week.
- The "overall_summary" should be a concise, encouraging summary of the student's progress, highlighting key achievements and areas for improvement based on LLM judgments, Anki reviews, and new cards.
- The "coach_comment_suggestion" should be a professional and actionable comment for the coach to review and potentially use, focusing on personalized advice.
- Both outputs should be in Korean.

[STUDENT LEARNING DATA]
{json.dumps(report_context, ensure_ascii=False, indent=2)}

Your JSON Response:"""

    llm_report_response = {"overall_summary": "LLM 요약 생성 실패", "coach_comment_suggestion": "LLM 코멘트 생성 실패"}
    try:
        llm_report_response = await call_ollama_api(llm_report_prompt)
    except Exception as e:
        print(f"Warning: Failed to generate LLM report summary: {e}. Using fallback.")

    overall_summary = llm_report_response.get("overall_summary", "LLM 요약 생성 실패")
    coach_comment_suggestion = llm_report_response.get("coach_comment_suggestion", "LLM 코멘트 생성 실패")

    report_data = schemas.WeeklyReportResponse(
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
        overall_summary=overall_summary,
        coach_comment=coach_comment_suggestion, # Use LLM suggestion here
        # Fields below are not part of the draft generation, will be populated upon creation
        report_id=0, # Placeholder, will be assigned by DB
        status='draft',
        created_at=datetime.now(),
        finalized_at=None
    )

    # Create the report in the database
    created_report = await crud.create_weekly_report(db, report_data=report_data)
    return created_report