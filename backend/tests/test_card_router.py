import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from datetime import date, timedelta

import crud
import schemas

@pytest.mark.asyncio
async def test_review_card(client_with_db: TestClient, async_session: AsyncSession):
    # 1. Setup: Create a student and a card
    student = await crud.create_student(async_session, schemas.StudentCreate(student_id="test-student", name="Test Student"))
    card_create = schemas.AnkiCardCreate(student_id=student.student_id, llm_log_id=1, question="Q", answer="A")
    card = await crud.create_anki_card(async_session, card_create)

    original_interval = card.interval_days
    original_repetitions = card.repetitions
    original_ease_factor = card.ease_factor

    # 2. Action: Review the card with a "perfect" quality score
    review_quality = 5
    response = client_with_db.post(
        f"/api/v1/cards/{card.card_id}/review",
        json={"quality": review_quality}
    )

    # 3. Assertions
    assert response.status_code == 200
    updated_card_data = response.json()

    # Check if the schedule was updated
    assert updated_card_data["card_id"] == card.card_id
    assert updated_card_data["repetitions"] > original_repetitions
    assert updated_card_data["interval_days"] > original_interval
    assert updated_card_data["ease_factor"] > original_ease_factor

    # Check the next review date
    expected_next_review_date = date.today() + timedelta(days=updated_card_data["interval_days"])
    assert date.fromisoformat(updated_card_data["next_review_date"]) == expected_next_review_date
