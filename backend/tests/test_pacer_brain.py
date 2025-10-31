import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from fastapi.testclient import TestClient # 추가

from main import app
from llm_filter import get_db
import crud
import schemas
import models

# Test DB override (reusing from conftest)

client = TestClient(app)

@pytest.mark.asyncio
async def test_get_daily_review_deck_with_budget(client_with_db: TestClient, async_session: AsyncSession):
    student_id = "student-budget-001"
    # 1. 학생 생성 (예산 설정)
    student_create_data = schemas.StudentCreate(
        student_id=student_id,
        name="예산 학생",
        settings={"anki_budget_per_day": 2}
    )
    await crud.create_student(async_session, student=student_create_data)

    # 2. Anki 카드 여러 개 생성 (일부는 오늘 기한, 일부는 아님)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # 기한이 된 카드 3개 (예산 2개 초과)
    card1_data = schemas.AnkiCardCreate(student_id=student_id, llm_log_id=1, question="Q1", answer="A1")
    card2_data = schemas.AnkiCardCreate(student_id=student_id, llm_log_id=2, question="Q2", answer="A2")
    card3_data = schemas.AnkiCardCreate(student_id=student_id, llm_log_id=3, question="Q3", answer="A3")
    
    card1 = await crud.create_anki_card(async_session, card=card1_data)
    card2 = await crud.create_anki_card(async_session, card=card2_data)
    card3 = await crud.create_anki_card(async_session, card=card3_data)

    # next_review_date를 오늘로 강제 설정 (테스트용)
    card1.next_review_date = today
    card2.next_review_date = today
    card3.next_review_date = today
    async_session.add_all([card1, card2, card3])

    # 기한이 아닌 카드 1개
    card4_data = schemas.AnkiCardCreate(student_id=student_id, llm_log_id=4, question="Q4", answer="A4")
    card4 = await crud.create_anki_card(async_session, card=card4_data)
    card4.next_review_date = tomorrow # 내일 기한
    async_session.add(card4)

    # 3. API 엔드포인트 호출
    response = client_with_db.get(f"/api/v1/student/{student_id}/daily_review_deck")

    # 4. 결과 검증
    assert response.status_code == 200
    deck_data = response.json()

    assert deck_data["student_id"] == student_id
    assert deck_data["total_due"] == 3 # 기한이 된 카드는 3개
    assert deck_data["budget_applied"] == True # 예산이 적용되어야 함
    assert deck_data["cards_in_deck"] == 2 # 예산 2개에 맞춰 2개만 반환되어야 함
    assert len(deck_data["due_cards"]) == 2
    
    # 우선순위가 높은 카드 2개가 반환되었는지 확인 (next_review_date, ease_factor 순)
    # SM2 초기값은 모두 같으므로, card_id 순서대로 반환될 것
    assert deck_data["due_cards"][0]["card_id"] == card1.card_id
    assert deck_data["due_cards"][1]["card_id"] == card2.card_id