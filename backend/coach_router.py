from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, timedelta
import json

import schemas
import crud
from llm_filter import get_db, call_ollama_api # Import call_ollama_api

router = APIRouter(
    prefix="/api/v1/coach",
    tags=["Coach"],
)

@router.post("/memo", response_model=schemas.CoachMemoResponse)
async def create_memo(memo: schemas.CoachMemoCreate, db: AsyncSession = Depends(get_db)):
    # Optionally, check if student_id and coach_id exist in the system
    # For now, we assume they are valid.
    db_memo = await crud.create_coach_memo(db, memo=memo)
    return db_memo

@router.get("/student/{student_id}/memos", response_model=List[schemas.CoachMemoResponse])
async def get_memos_for_student(
    student_id: str,
    coach_id: Optional[str] = Query(None, description="Filter memos by coach ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    memos = await crud.get_coach_memos(db, student_id=student_id, coach_id=coach_id, skip=skip, limit=limit)
    return memos

@router.get("/student/{student_id}/coaching-suggestions", response_model=schemas.CoachingSuggestionsResponse)
async def get_coaching_suggestions(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    days_back: int = Query(7, description="Number of days back to fetch student data for analysis.")
):
    student = await crud.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    end_date = date.today()
    start_date = end_date - timedelta(days=days_back - 1)

    # Fetch relevant student data
    llm_logs = await crud.get_llm_logs(db, student_id=student_id, start_date=start_date, end_date=end_date)
    anki_cards = await crud.get_anki_cards_by_student_id(db, student_id=student_id) # Fetch all for context
    coach_memos = await crud.get_coach_memos(db, student_id=student_id, start_date=start_date, end_date=end_date)

    # Prepare data for LLM prompt
    llm_logs_data = [{
        "concept_name": log.concept_name,
        "decision": log.decision,
        "reason": log.reason,
        "coach_feedback": log.coach_feedback,
        "model_version": log.model_version,
        "created_at": log.created_at.isoformat()
    } for log in llm_logs]

    anki_cards_data = [{
        "question": card.question,
        "answer": card.answer,
        "repetitions": card.repetitions,
        "ease_factor": card.ease_factor,
        "next_review_date": card.next_review_date.isoformat() if card.next_review_date else None,
        "last_reviewed_at": card.last_reviewed_at.isoformat() if card.last_reviewed_at else None
    } for card in anki_cards]

    coach_memos_data = [{
        "memo_text": memo.memo_text,
        "created_at": memo.created_at.isoformat()
    } for memo in coach_memos]

    student_data_context = {
        "student_name": student.name,
        "analysis_period": f"{start_date} to {end_date}",
        "llm_judgments": llm_logs_data,
        "anki_card_progress": anki_cards_data,
        "coach_memos": coach_memos_data
    }

    llm_prompt = f"""[SYSTEM]
You are an AI assistant that analyzes student learning data and generates proactive coaching suggestions. Your output must be in JSON format with two keys: "overall_assessment" (string) and "suggestions" (array of objects).

[INSTRUCTIONS]
- Analyze the provided student learning data, including LLM judgments, Anki card progress, and coach memos.
- The "overall_assessment" should be a concise summary of the student's current learning status, strengths, and areas needing attention.
- Each suggestion object in the "suggestions" array must have "category" (string), "suggestion" (string), and "priority" (string: High, Medium, Low) keys.
- Suggestions should be actionable, personalized, and cover areas like concept reinforcement, study habits, motivation, or specific topic focus.
- All outputs should be in Korean.

[STUDENT LEARNING DATA]
{json.dumps(student_data_context, ensure_ascii=False, indent=2)}

Your JSON Response:"""

    llm_response_data = {"overall_assessment": "LLM 분석 실패", "suggestions": []}
    try:
        llm_raw_response = await call_ollama_api(llm_prompt)
        llm_response_data = llm_raw_response # Assuming call_ollama_api returns parsed JSON
    except Exception as e:
        print(f"Warning: Failed to generate coaching suggestions with LLM: {e}. Using fallback.")

    return schemas.CoachingSuggestionsResponse(
        student_id=student_id,
        overall_assessment=llm_response_data.get("overall_assessment", "LLM 분석 실패"),
        suggestions=llm_response_data.get("suggestions", [])
    )