import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from main import app
from llm_filter import get_db
import models

# This is the overridden dependency for testing
async def override_get_db():
    from tests.conftest import SessionLocalTest
    db = SessionLocalTest()
    try:
        yield db
    finally:
        await db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.mark.asyncio
async def test_judge_and_feedback_e2e(db_session: AsyncSession):
    # 1. Judge API를 호출하여 로그를 생성합니다.
    judge_request_data = {
        "student_id": "user-e2e-001",
        "submission_id": 101,
        "error_context": {
            "question_type": "SCIENCE",
            "concept_name": "광합성",
            "student_mistake_summary": "밤에 일어난다고 답변함."
        }
    }
    response = client.post("/api/v1/filter/judge", json=judge_request_data)
    assert response.status_code == 200
    judge_data = response.json()
    log_id = judge_data["log_id"]

    # 2. DB에 로그가 실제로 생성되었는지 확인합니다.
    result = await db_session.execute(select(models.LLMLog).where(models.LLMLog.log_id == int(log_id)))
    log_in_db = result.scalars().first()
    assert log_in_db is not None
    assert log_in_db.decision == judge_data["decision"]

    # 3. Feedback API를 호출하여 위 로그를 업데이트합니다.
    feedback_data = {
        "log_id": log_id,
        "coach_id": "coach-e2e-001",
        "feedback": "BAD",
        "reason_code": "WRONG_JUDGEMENT"
    }
    response = client.post("/api/v1/filter/feedback", json=feedback_data)
    assert response.status_code == 200

    # 4. DB의 로그가 실제로 업데이트되었는지 확인합니다.
    await db_session.refresh(log_in_db)
    assert log_in_db.coach_feedback == "BAD"
    assert log_in_db.reason_code == "WRONG_JUDGEMENT"
