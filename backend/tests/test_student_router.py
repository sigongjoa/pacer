import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas


@pytest.mark.asyncio
async def test_create_and_read_students(client_with_db: TestClient, async_session: AsyncSession):
    # 1. Create a couple of students
    student1_data = {"student_id": "s1", "name": "Student One", "settings": {"budget": 10}}
    student2_data = {"student_id": "s2", "name": "Student Two", "settings": {"budget": 20}}

    response1 = client_with_db.post("/api/v1/student/", json=student1_data)
    assert response1.status_code == 200
    response2 = client_with_db.post("/api/v1/student/", json=student2_data)
    assert response2.status_code == 200

    # 2. Read the list of students
    response = client_with_db.get("/api/v1/student/")
    assert response.status_code == 200
    students_list = response.json()

    # 3. Assertions
    assert isinstance(students_list, list)
    # We might have other students from other tests, so check for length >= 2
    assert len(students_list) >= 2 
    
    student_ids_in_response = [s['student_id'] for s in students_list]
    assert student1_data["student_id"] in student_ids_in_response
    assert student2_data["student_id"] in student_ids_in_response

@pytest.mark.asyncio
async def test_update_student_settings(client_with_db: TestClient, async_session: AsyncSession):
    # 1. Create a student
    student_id = "student-to-update"
    initial_settings = {"anki_budget_per_day": 15}
    student_data = {"student_id": student_id, "name": "Update Me", "settings": initial_settings}
    
    create_response = client_with_db.post("/api/v1/student/", json=student_data)
    assert create_response.status_code == 200

    # 2. Update the student's settings
    new_settings = {"anki_budget_per_day": 99, "new_setting": True}
    update_payload = {"settings": new_settings}

    update_response = client_with_db.put(f"/api/v1/student/{student_id}", json=update_payload)
    
    # 3. Assertions for the PUT response
    assert update_response.status_code == 200
    updated_student = update_response.json()
    assert updated_student["student_id"] == student_id
    assert updated_student["settings"] == new_settings

    # 4. Verify the update by fetching the student again
    get_response = client_with_db.get(f"/api/v1/student/{student_id}/daily_review_deck") # Use an existing endpoint to get student data indirectly
    assert get_response.status_code == 200
    # The daily_review_deck response doesn't include settings, so let's check crud
    db_student = await crud.get_student(async_session, student_id=student_id)
    assert db_student is not None
    assert db_student.settings == new_settings
