import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import crud
import schemas
import models

@pytest.mark.asyncio
async def test_submit_assignment_and_create_card(client_with_db: TestClient, async_session: AsyncSession):
    # 1. Setup: Create a student
    student_id = "student-submit-001"
    await crud.create_student(async_session, schemas.StudentCreate(student_id=student_id, name="Submit Test Student"))

    # 2. Action: Submit an assignment that triggers card creation
    submission_data = schemas.SubmissionRequest(
        student_id=student_id,
        assignment_id="history-01",
        answer="임진왜란은 1592년에 일어났지만, 어떤 사람들은 1692년이라고 착각하기도 합니다."
    )
    response = client_with_db.post("/api/v1/submission/", json=submission_data.model_dump())

    # 3. Assertions for the API response
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "Submission analyzed, Anki card creation process initiated."
    assert response_json["judge_decision"] == "APPROVE"

    # 4. Verify database changes: LLMLog and AnkiCard created
    # Check LLMLog
    llm_log_result = await async_session.execute(
        select(models.LLMLog).where(models.LLMLog.submission_id == submission_data.assignment_id)
    )
    llm_log = llm_log_result.scalars().first()
    assert llm_log is not None
    assert llm_log.decision == "APPROVE"

    # Check AnkiCard
    anki_card_result = await async_session.execute(
        select(models.AnkiCard).where(models.AnkiCard.llm_log_id == llm_log.log_id)
    )
    anki_card = anki_card_result.scalars().first()
    assert anki_card is not None
    assert anki_card.student_id == student_id
    assert anki_card.question # Assert that the question is not empty

@pytest.mark.asyncio
async def test_submit_assignment_no_card_creation(client_with_db: TestClient, async_session: AsyncSession):
    # 1. Setup: Create a student
    student_id = "student-no-card-001"
    await crud.create_student(async_session, schemas.StudentCreate(student_id=student_id, name="No Card Test Student"))

    # 2. Action: Submit an assignment that does NOT trigger card creation
    submission_data = schemas.SubmissionRequest(
        student_id=student_id,
        assignment_id="math-01",
        answer="1 + 1 = 2"
    )
    response = client_with_db.post("/api/v1/submission/", json=submission_data.model_dump())

    # 3. Assertions for the API response
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["message"] == "Submission analyzed, no critical mistake found for Anki card creation."

    # 4. Verify database changes: No LLMLog or AnkiCard created for this submission_id
    llm_log_result = await async_session.execute(
        select(models.LLMLog).where(models.LLMLog.submission_id == submission_data.assignment_id)
    )
    llm_log = llm_log_result.scalars().first()
    assert llm_log is None
