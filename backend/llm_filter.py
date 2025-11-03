import httpx
import json
from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import SessionLocal

# Dependency to get DB session
async def get_db():
    db = SessionLocal()
    try:
        yield db
        await db.commit()
    finally:
        await db.close()

router = APIRouter(
    prefix="/api/v1/filter",
    tags=["LLM Filter"],
)

async def call_ollama_api(prompt: str) -> dict:
    # ... (Ollama API 호출 로직은 이전과 동일, 생략)
    payload = {
        "model": "llama2:latest",
        "prompt": prompt,
        "format": "json",
        "stream": False
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://localhost:11434/api/generate", json=payload)
            response.raise_for_status()
            response_text = response.json()['response']
            return json.loads(response_text)
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Ollama service is unavailable: {e}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse LLM response as JSON.")

@router.get("/logs", response_model=List[schemas.LLMLogResponse])
async def get_logs(
    skip: int = 0,
    limit: int = 20,
    start_date: Optional[date] = Query(None, description="Filter logs from this date (inclusive). Defaults to 7 days ago."),
    end_date: Optional[date] = Query(None, description="Filter logs up to this date (inclusive). Defaults to today."),
    student_id: Optional[str] = Query(None, description="Filter logs by student ID."),
    db: AsyncSession = Depends(get_db)
):
    # 기본값 설정 (7일 전부터 오늘까지)
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=6) # 7일간의 데이터를 포함하도록 6일 전으로 설정

    logs = await crud.get_llm_logs(db, skip=skip, limit=limit, start_date=start_date, end_date=end_date, student_id=student_id)
    return logs

@router.post("/judge", response_model=schemas.JudgeResponse)
async def judge_anki_necessity(request: schemas.JudgeRequest, db: AsyncSession = Depends(get_db)):
    # V1 경량화 원칙에 따라, LLM에 전달할 간결한 프롬프트를 생성합니다.
    prompt = f"""[SYSTEM]
You are a helpful AI assistant that functions as a JSON API. You must only answer in JSON format. Do not add any other text. Your task is to decide if a student's mistake is worth creating a review card (Anki card).

[INSTRUCTIONS]
- Analyze the user's mistake based on the provided context.
- The JSON output must contain two keys: "decision" (string) and "reason" (string).
- The value for "decision" must be either "APPROVE" or "REJECT".
- "APPROVE" if the mistake is a core concept error, a misunderstanding of a definition, or a critical factual error.
- "REJECT" if the mistake is a simple calculation error, a typo, or not educationally significant.
- The "reason" must be a short explanation in Korean.

[EXAMPLE 1]
User Mistake Context: {{ "concept": "Pythagorean theorem", "mistake": "Student used a+b=c instead of a^2+b^2=c^2" }}
Your JSON Response: {{"decision": "APPROVE", "reason": "핵심적인 개념인 피타고라스의 정리를 잘못 이해하고 있습니다."}}

[EXAMPLE 2]
User Mistake Context: {{ "concept": "Addition", "mistake": "Student calculated 123 + 456 as 578" }}
Your JSON Response: {{"decision": "REJECT", "reason": "개념 이해보다는 단순 계산 실수에 가깝습니다."}}

[CURRENT TASK]
User Mistake Context: {{ "concept": "{request.error_context.concept_name}", "mistake": "{request.error_context.student_mistake_summary}" }}
Your JSON Response:"""
    llm_response = await call_ollama_api(prompt)
    
    # LLM 판단 결과를 실제 DB에 저장
    new_log = await crud.create_llm_log(
        db=db, 
        submission_id=request.submission_id, 
        decision=llm_response.get("decision", "REJECT"), 
        reason=llm_response.get("reason", "LLM response format error.")
    )

    # LLM이 APPROVE 결정을 내리면 Anki 카드를 생성합니다.
    if new_log.decision == "APPROVE":
        # 임시로 질문과 답변을 생성 (실제로는 더 정교한 로직 필요)
        question = f"'''{request.error_context.concept_name}'''에 대해 설명하세요."
        answer = f"'''{request.error_context.concept_name}'''은 ... 입니다. (LLM 응답 기반)"
        
        anki_card_data = schemas.AnkiCardCreate(
            student_id=request.student_id,
            llm_log_id=new_log.log_id,
            question=question,
            answer=answer
        )
        await crud.create_anki_card(db=db, card=anki_card_data)

    return schemas.JudgeResponse(
        log_id=str(new_log.log_id), 
        decision=new_log.decision,
        reason=new_log.reason
    )

@router.post("/feedback", response_model=schemas.FeedbackResponse)
async def submit_feedback(request: schemas.FeedbackRequest, db: AsyncSession = Depends(get_db)):
    updated_log = await crud.update_llm_log_feedback(db=db, feedback=request)
    if not updated_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return schemas.FeedbackResponse(
        status="feedback_logged_for_manual_review",
        log_id=request.log_id
    )
