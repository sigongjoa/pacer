# 📜 PACER API 명세서 (V1 - 비용 최적화)

## 1. 개요

본 문서는 PACER 시스템 V1의 서비스 간 RESTful API 통신 규약을 정의합니다. V1의 핵심 목표는 **LLM 호출 비용 최소화**와 **명확한 역할 분리**입니다.

**Base URL:** `/api/v1`

---

## 2. LLMFilter Service API

### `POST /filter/judge`

*   **Description:** 학생 오답에 대해 Anki 카드 등록 필요성을 **최소한의 정보로** 판단합니다.
*   **V1 변경점:** 요청 본문에서 방대한 `analysis_report` 객체를 제거하고, LLM 프롬프트에 직접 사용될 **경량화된 핵심 정보**만 전달하여 토큰 비용을 획기적으로 절감합니다.
*   **Request Body:**
    ```json
    {
      "student_id": "user-123",
      "submission_id": "sub-abc-456",
      "error_context": {
        "question_type": "MATH_FORMULA",
        "concept_name": "근의 공식",
        "student_mistake_summary": "학생이 판별식의 부호를 반대로 적용함."
      }
    }
    ```
*   **Response Body (200 OK):**
    ```json
    {
      "log_id": "log-xyz-789",
      "decision": "APPROVE",
      "reason": "핵심 개념 오류로 판단됨."
    }
    ```

### `POST /filter/feedback`

*   **Description:** LLM의 판단에 대한 코치의 피드백을 **데이터베이스에 기록**합니다.
*   **V1 변경점:** 이 API는 **자동 파인튜닝을 트리거하지 않습니다.** 수집된 데이터는 프롬프트 엔지니어링 개선을 위해 수동으로 분석됩니다.
*   **Request Body:**
    ```json
    {
      "log_id": "log-xyz-789",
      "coach_id": "coach-007",
      "feedback": "BAD",
      "reason_code": "SIMPLE_MISTAKE"
    }
    ```
*   **Response Body (200 OK):**
    ```json
    {
      "status": "feedback_logged_for_manual_review",
      "log_id": "log-xyz-789"
    }
    ```

---

## 3. AIModule Service API

### `POST /ai/analyze`

*   **Description:** 학생의 제출물을 **규칙 기반(Rule-Based)으로** 분석합니다.
*   **V1 변경점:** 이 API는 **LLM을 호출하지 않으므로** 비용이 발생하지 않습니다. 정답 비교, 키워드 매칭 등의 빠른 로직을 수행합니다.
*   **Request Body:**
    ```json
    {
      "submission_id": "sub-abc-456",
      "raw_answers": { ... }
    }
    ```
*   **Response Body (200 OK):**
    ```json
    {
      "analysis_report": {
        "score": 85.5,
        "error_contexts": [
          {
            "question_type": "MATH_FORMULA",
            "concept_name": "근의 공식",
            "student_mistake_summary": "학생이 판별식의 부호를 반대로 적용함."
          }
        ]
      }
    }
    ```