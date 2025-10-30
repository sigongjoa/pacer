from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

import crud
import schemas
import pacer_brain
from llm_filter import get_db # DB 세션 재사용

router = APIRouter(
    prefix="/api/v1/student",
    tags=["Student"],
)

@router.post("/", response_model=schemas.StudentResponse)
async def create_student(student: schemas.StudentCreate, db: AsyncSession = Depends(get_db)):
    db_student = await crud.get_student(db, student_id=student.student_id)
    if db_student:
        raise HTTPException(status_code=400, detail="Student already registered")
    return await crud.create_student(db=db, student=student)

@router.get("/{student_id}/daily_review_deck", response_model=schemas.DailyReviewDeckResponse)
async def get_daily_review_deck(student_id: str, db: AsyncSession = Depends(get_db)):
    student = await crud.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    due_cards = await crud.get_due_anki_cards(db, student_id=student_id, today=date.today())
    
    deck = await pacer_brain.get_daily_review_deck(student, due_cards)
    return deck
