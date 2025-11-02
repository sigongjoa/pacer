from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

import schemas
import crud
import report_generator
from llm_filter import get_db

router = APIRouter(
    prefix="/api/v1/report",
    tags=["Report"],
)

@router.get("/student/{student_id}/period", response_model=schemas.WeeklyReportResponse)
async def get_weekly_report(
    student_id: str,
    start_date: date = Query(..., description="Start date of the report period (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date of the report period (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    try:
        report = await report_generator.generate_weekly_report_draft(db, student_id, start_date, end_date)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{report_id}/finalize", response_model=schemas.WeeklyReportResponse)
async def finalize_report(
    report_id: int,
    final_data: schemas.WeeklyReportFinalize,
    db: AsyncSession = Depends(get_db)
):
    report = await crud.get_weekly_report(db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.status != 'draft':
        raise HTTPException(status_code=400, detail=f"Report is already in '{report.status}' status and cannot be finalized.")

    updated_report = await crud.finalize_weekly_report(db, report_id=report_id, final_data=final_data)
    return updated_report
