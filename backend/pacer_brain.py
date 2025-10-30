from typing import List
from datetime import date

import models
import schemas

async def get_daily_review_deck(
    student: models.Student,
    due_cards: List[models.AnkiCard],
    today: date = date.today()
) -> schemas.DailyReviewDeckResponse:
    """
    학생의 일일 복습 예산에 맞춰 Anki 카드 덱을 생성합니다.
    """
    budget_per_day = student.settings.get("anki_budget_per_day", 20) # 기본값 20개

    # 1. 우선순위 정렬 (가장 오래된 복습일, 낮은 난이도 계수 순)
    # SM2 알고리즘에 따라, ease_factor가 낮을수록 어려운 카드이므로 우선순위가 높음
    # next_review_date가 오래될수록 우선순위 높음
    sorted_cards = sorted(due_cards, key=lambda card: (card.next_review_date, card.ease_factor))

    # 2. 예산 필터링
    deck_cards = sorted_cards[:budget_per_day]

    return schemas.DailyReviewDeckResponse(
        student_id=student.student_id,
        due_cards=[schemas.AnkiCardResponse.from_orm(card) for card in deck_cards],
        budget_applied=len(due_cards) > budget_per_day,
        total_due=len(due_cards),
        cards_in_deck=len(deck_cards)
    )
