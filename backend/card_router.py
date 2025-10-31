from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from llm_filter import get_db

router = APIRouter(
    prefix="/api/v1/cards",
    tags=["Cards"],
)

@router.post("/{card_id}/review", response_model=schemas.AnkiCardResponse)
async def review_card(card_id: int, review: schemas.CardReviewRequest, db: AsyncSession = Depends(get_db)):
    db_card = await crud.update_anki_card_schedule(db, card_id=card_id, quality=review.quality)
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    return db_card
