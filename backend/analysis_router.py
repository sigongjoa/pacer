from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

import crud
from llm_filter import get_db
from backend.model_registry import ModelRegistry # Import ModelRegistry

router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)

model_registry = ModelRegistry()

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

@router.post("/model-status/{version}")
async def set_model_status(version: str, status: str):
    """
    Sets the production status of a model version in the registry.
    Valid statuses: 'inactive', 'staging', 'production'.
    """
    if status not in ["inactive", "staging", "production"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be inactive, staging, or production.")
    
    success = model_registry.set_model_production_status(version, status)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model version {version} not found.")
    
    return {"message": f"Model {version} status set to {status}."}

@router.get("/models", response_model=Dict[str, Dict[str, Any]])
async def list_registered_models():
    """
    Lists all registered models and their details.
    """
    return model_registry.list_models()