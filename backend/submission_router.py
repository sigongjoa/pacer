from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import ai_module
import llm_filter
from llm_filter import get_db # DB 세션 재사용

router = APIRouter(
    prefix="/api/v1/submission",
    tags=["Submission"],
)

@router.post("/", response_model=dict)
async def submit_assignment(submission: schemas.SubmissionRequest, db: AsyncSession = Depends(get_db)):
    # 1. AI Module을 사용하여 제출물 분석 (규칙 기반)
    error_context = await ai_module.analyze_submission(submission)

    if error_context:
        # 2. LLMFilter에 Anki 카드 생성 필요성 판단 요청
        judge_request = schemas.JudgeRequest(
            student_id=submission.student_id,
            submission_id=submission.assignment_id, # submission_id는 int여야 하지만, 여기서는 assignment_id를 사용
            error_context=error_context
        )
        # llm_filter.judge_anki_necessity는 이미 db 세션을 Depends로 받으므로, 직접 호출
        judge_response = await llm_filter.judge_anki_necessity(request=judge_request, db=db)
        
        return {"message": "Submission analyzed, Anki card creation process initiated.", "judge_decision": judge_response.decision}
    else:
        return {"message": "Submission analyzed, no critical mistake found for Anki card creation."}
