from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

import crud
import schemas
from llm_filter import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["Parent"],
)

@router.post("/parents/", response_model=schemas.ParentResponse)
async def create_parent(parent: schemas.ParentCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_parent(db=db, parent=parent)

@router.get("/parents/{parent_id}", response_model=schemas.ParentResponse)
async def read_parent(parent_id: int, db: AsyncSession = Depends(get_db)):
    db_parent = await crud.get_parent(db, parent_id=parent_id)
    if db_parent is None:
        raise HTTPException(status_code=404, detail="Parent not found")
    return db_parent

@router.post("/students/{student_id}/assign-parent/{parent_id}", response_model=schemas.StudentResponse)
async def assign_parent_to_student(
    student_id: str,
    parent_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_student = await crud.assign_parent_to_student(db, student_id=student_id, parent_id=parent_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student or Parent not found")
    return db_student
