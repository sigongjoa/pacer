from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

import schemas
import crud
import report_generator
import kakao_sender
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

@router.post("/{report_id}/send", status_code=200)
async def send_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_report = await crud.get_weekly_report(db, report_id=report_id)
    if not db_report or db_report.status != 'finalized':
        raise HTTPException(status_code=400, detail="리포트가 최종 승인 상태가 아닙니다.")

    db_student = await crud.get_student(db, student_id=db_report.student_id)
    if not db_student.parents:
        raise HTTPException(status_code=404, detail="리포트를 수신할 학부모가 등록되지 않았습니다.")

    # 모든 연결된 학부모에게 발송
    sent_count = 0
    for parent in db_student.parents:
        if parent.kakao_user_id:
            try:
                await kakao_sender.send_report_via_kakao(parent.kakao_user_id, db_report)
                sent_count += 1
            except Exception as e:
                # 특정 학부모에게 발송 실패 시 로깅 (추후 구현)
                print(f"카카오 메시지 발송 실패: {e}")
    
    # 발송 완료 후 리포트 상태 변경
    db_report.status = 'sent'
    await db.commit()

    return {"message": f"총 {len(db_student.parents)}명의 학부모 중 {sent_count}명에게 리포트가 발송되었습니다."}
