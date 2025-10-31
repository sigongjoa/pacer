import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import crud
import schemas
import models

@pytest.mark.asyncio
async def test_create_coach_memo(client_with_db: TestClient, async_session: AsyncSession):
    # 1. Setup: Create a student
    student_id = "student-memo-001"
    await crud.create_student(async_session, schemas.StudentCreate(student_id=student_id, name="Memo Test Student"))

    # 2. Action: Create a memo
    memo_data = schemas.CoachMemoCreate(
        coach_id="coach-001",
        student_id=student_id,
        memo_text="학생이 오늘 수업에 집중을 잘 했습니다."
    )
    response = client_with_db.post("/api/v1/coach/memo", json=memo_data.model_dump())

    # 3. Assertions
    assert response.status_code == 200
    created_memo = response.json()
    assert created_memo["coach_id"] == memo_data.coach_id
    assert created_memo["student_id"] == memo_data.student_id
    assert created_memo["memo_text"] == memo_data.memo_text
    assert "memo_id" in created_memo
    assert "created_at" in created_memo

    # 4. Verify in DB
    db_memo = await async_session.execute(select(models.CoachMemo).where(models.CoachMemo.memo_id == created_memo["memo_id"]))
    memo_in_db = db_memo.scalars().first()
    assert memo_in_db is not None
    assert memo_in_db.memo_text == memo_data.memo_text

@pytest.mark.asyncio
async def test_get_memos_for_student(client_with_db: TestClient, async_session: AsyncSession):
    # 1. Setup: Create a student and multiple memos
    student_id = "student-memo-002"
    coach1_id = "coach-001"
    coach2_id = "coach-002"
    await crud.create_student(async_session, schemas.StudentCreate(student_id=student_id, name="Memo Test Student 2"))

    memo1_data = schemas.CoachMemoCreate(coach_id=coach1_id, student_id=student_id, memo_text="Memo by coach 1")
    memo2_data = schemas.CoachMemoCreate(coach_id=coach2_id, student_id=student_id, memo_text="Memo by coach 2")
    memo3_data = schemas.CoachMemoCreate(coach_id=coach1_id, student_id=student_id, memo_text="Another memo by coach 1")

    await crud.create_coach_memo(async_session, memo=memo1_data)
    await crud.create_coach_memo(async_session, memo=memo2_data)
    await crud.create_coach_memo(async_session, memo=memo3_data)

    # 2. Action: Get all memos for the student
    response = client_with_db.get(f"/api/v1/coach/student/{student_id}/memos")

    # 3. Assertions
    assert response.status_code == 200
    memos = response.json()
    assert len(memos) == 3
    assert any(m["memo_text"] == memo1_data.memo_text for m in memos)
    assert any(m["memo_text"] == memo2_data.memo_text for m in memos)
    assert any(m["memo_text"] == memo3_data.memo_text for m in memos)

@pytest.mark.asyncio
async def test_get_memos_for_student_filtered_by_coach(client_with_db: TestClient, async_session: AsyncSession):
    # 1. Setup: Create a student and multiple memos (reusing setup from previous test)
    student_id = "student-memo-003"
    coach1_id = "coach-001"
    coach2_id = "coach-002"
    await crud.create_student(async_session, schemas.StudentCreate(student_id=student_id, name="Memo Test Student 3"))

    memo1_data = schemas.CoachMemoCreate(coach_id=coach1_id, student_id=student_id, memo_text="Memo by coach 1 for filter")
    memo2_data = schemas.CoachMemoCreate(coach_id=coach2_id, student_id=student_id, memo_text="Memo by coach 2 for filter")
    memo3_data = schemas.CoachMemoCreate(coach_id=coach1_id, student_id=student_id, memo_text="Another memo by coach 1 for filter")

    await crud.create_coach_memo(async_session, memo=memo1_data)
    await crud.create_coach_memo(async_session, memo=memo2_data)
    await crud.create_coach_memo(async_session, memo=memo3_data)

    # 2. Action: Get memos filtered by coach1_id
    response = client_with_db.get(f"/api/v1/coach/student/{student_id}/memos?coach_id={coach1_id}")

    # 3. Assertions
    assert response.status_code == 200
    memos = response.json()
    assert len(memos) == 2
    assert all(m["coach_id"] == coach1_id for m in memos)
    assert any(m["memo_text"] == memo1_data.memo_text for m in memos)
    assert any(m["memo_text"] == memo3_data.memo_text for m in memos)
