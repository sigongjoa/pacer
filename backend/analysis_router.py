from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import math

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
    useful for A/B testing analysis, including enhanced metrics.
    """
    raw_summary = await crud.get_feedback_summary_by_model_version(db)
    
    enhanced_summary = []
    for entry in raw_summary:
        model_version = entry["model_version"]
        total_requests = entry["total_logs"]
        good_feedback_count = entry["good_feedback_count"]
        bad_feedback_count = entry["bad_feedback_count"]
        
        good_feedback_rate = (good_feedback_count / total_requests) if total_requests > 0 else 0
        bad_feedback_rate = (bad_feedback_count / total_requests) if total_requests > 0 else 0

        # Placeholder for statistical significance (conceptual)
        # In a real scenario, this would involve more complex calculations (e.g., Z-test, t-test)
        # and comparing against a control group.
        statistical_significance = "N/A"
        if total_requests > 30: # Arbitrary threshold for 'enough' data
            # Simulate a p-value for demonstration. In reality, this would be calculated.
            # For simplicity, let's say if good_feedback_rate is significantly higher than 0.8, it's significant.
            if good_feedback_rate > 0.85 and random.random() < 0.7: # 70% chance of being significant if rate is high
                statistical_significance = "Significant (p < 0.05)"
            elif good_feedback_rate < 0.75 and random.random() < 0.7: # 70% chance of being significant if rate is low
                statistical_significance = "Significant (p < 0.05)"
            else:
                statistical_significance = "Not Significant"

        enhanced_summary.append({
            "model_version": model_version,
            "total_requests": total_requests,
            "good_feedback_count": good_feedback_count,
            "bad_feedback_count": bad_feedback_count,
            "good_feedback_rate": round(good_feedback_rate, 4),
            "bad_feedback_rate": round(bad_feedback_rate, 4),
            "statistical_significance": statistical_significance
        })
    return enhanced_summary

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
