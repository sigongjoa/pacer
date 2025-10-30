from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_submission_with_basic_math_error():
    # 1. 테스트용 요청 데이터 준비
    request_data = {
        "submission_id": 1,
        "raw_answers": {
            "q1": {
                "question": "1+1=?",
                "answer": "3" # 오답
            }
        }
    }

    # 2. API 엔드포인트 호출
    response = client.post("/api/v1/ai/analyze", json=request_data)

    # 3. 결과 검증
    assert response.status_code == 200
    response_data = response.json()
    
    # 점수는 0점이어야 함
    assert response_data["score"] == 0.0
    
    # 에러 컨텍스트가 정확히 1개 있어야 함
    assert len(response_data["error_contexts"]) == 1
    
    # 에러 컨텍스트의 내용이 예상과 일치해야 함
    error_context = response_data["error_contexts"][0]
    assert error_context["question_type"] == "BASIC_ARITHMETIC"
    assert error_context["concept_name"] == "덧셈"
    assert error_context["student_mistake_summary"] == "1+1의 답을 3으로 계산함."
