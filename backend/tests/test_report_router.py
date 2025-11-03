import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

import crud
import schemas
import models

@pytest.mark.asyncio
async def test_generate_weekly_report(client_with_db: TestClient, async_session: AsyncSession):
    # 1. Setup: Create student and relevant data
    student_id = "student-report-001"
    coach_id = "coach-report-001"
    report_start_date = date.today() - timedelta(days=7)
    report_end_date = date.today()

    await crud.create_student(async_session, schemas.StudentCreate(student_id=student_id, name="Report Test Student"))

    # Create LLM Logs
    await crud.create_llm_log(async_session, submission_id="sub-001", decision="APPROVE", reason="Concept error", concept_name="Test Concept 1", model_version="test_v1.0")
    await crud.create_llm_log(async_session, submission_id="sub-002", decision="REJECT", reason="Typo", concept_name="Test Concept 2", model_version="test_v1.0")

    # Create Anki Cards and simulate review
    card1 = await crud.create_anki_card(async_session, schemas.AnkiCardCreate(student_id=student_id, llm_log_id=1, question="Q1", answer="A1"))
    card2 = await crud.create_anki_card(async_session, schemas.AnkiCardCreate(student_id=student_id, llm_log_id=2, question="Q2", answer="A2"))
    
    # Simulate review for card1 within the period
    await crud.update_anki_card_schedule(async_session, card_id=card1.card_id, quality=5)

    # Create Coach Memos
    await crud.create_coach_memo(async_session, schemas.CoachMemoCreate(coach_id=coach_id, student_id=student_id, memo_text="Good progress this week"))

    # 2. Action: Request the weekly report
    response = client_with_db.get(
        f"/api/v1/report/student/{student_id}/period",
        params={
            "start_date": report_start_date.isoformat(),
            "end_date": report_end_date.isoformat()
        }
    )

    # 3. Assertions
    assert response.status_code == 200
    report = response.json()

    assert report["student_id"] == student_id
    assert report["student_name"] == "Report Test Student"
    assert report["report_period_start"] == report_start_date.isoformat()
    assert report["report_period_end"] == report_end_date.isoformat()
    assert report["llm_judgments_count"] == 2 # Two LLM logs created
    assert report["anki_cards_reviewed_count"] == 1 # One card reviewed
    assert report["new_anki_cards_created_count"] == 2 # Two cards created
    assert len(report["coach_memo_summaries"]) == 1
    assert "주간 학습 리포트입니다." in report["overall_summary"]

@pytest.mark.asyncio
async def test_generate_weekly_report_student_not_found(client_with_db: TestClient):
    non_existent_student_id = "non-existent-student"
    report_start_date = date.today() - timedelta(days=7)
    report_end_date = date.today()

    response = client_with_db.get(
        f"/api/v1/report/student/{non_existent_student_id}/period",
        params={
            "start_date": report_start_date.isoformat(),
            "end_date": report_end_date.isoformat()
        }
    )

    assert response.status_code == 404
    assert "Student not found" in response.json()["detail"]
