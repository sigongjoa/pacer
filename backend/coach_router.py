from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import schemas
import crud
from llm_filter import get_db

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
