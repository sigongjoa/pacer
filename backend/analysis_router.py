from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

import crud
from llm_filter import get_db

router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)

@router.get("/feedback-summary")
async def get_feedback_summary(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Analyzes the LLM logs and provides a summary of feedback, 
    focusing on logs marked as 'BAD'.
    """
    summary = await crud.get_bad_feedback_summary(db)
    return summary

@router.get("/ab-test-summary", response_model=List[Dict[str, Any]])
async def get_ab_test_summary(db: AsyncSession = Depends(get_db)):
    """
    Provides a summary of coach feedback grouped by model version, 
    useful for A/B testing analysis.
    """
    summary = await crud.get_feedback_summary_by_model_version(db)
    return summary
