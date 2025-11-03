 # Pacer 카카오톡 API 연동 계획서

## 1. 개요

본 문서는 Pacer 시스템의 주간 리포트를 학부모에게 카카오톡 메시지로 발송하기 위한 API 연동 계획을 기술합니다.

- **사용 API:** [카카오톡 채널 메시지 보내기 API](https://developers.kakao.com/docs/latest/ko/message/channel)
- **발송 대상:** Pacer 서비스의 카카오톡 채널을 추가한 학부모 사용자
- **주요 내용:** 최종 승인된 리포트의 요약 정보를 포함하는 메시지 템플릿을 구성하여 발송

---

## 2. 사전 준비사항 (사용자 직접 수행)

코드 구현에 앞서, 카카오 개발자 센터에서 다음 준비가 반드시 필요합니다.

1.  **카카오 개발자 계정 생성 및 애플리케이션 등록**
    - [카카오 개발자 사이트](https://developers.kakao.com/)에서 애플리케이션을 생성합니다.
2.  **REST API 키 확인**
    - 생성한 애플리케이션의 [내 애플리케이션] > [앱 설정] > [요약 정보]에서 **REST API 키**를 확인하여 안전한 곳에 보관합니다.
3.  **카카오톡 채널 생성 및 연결**
    - Pacer 서비스를 위한 카카오톡 채널을 개설합니다.
    - [내 애플리케이션] > [플랫폼] > [카카오톡 채널]에서 생성한 채널을 앱과 연결합니다.
4.  **메시지 API 권한 활성화**
    - [내 애플리케이션] > [제품 설정] > [카카오톡 채널]에서 '메시지 보내기' 기능의 상태를 ON으로 변경합니다.
5.  **사용자(학부모) 채널 추가**
    - 메시지를 수신할 학부모는 Pacer의 카카오톡 채널을 친구로 추가해야 합니다.

---

## 3. 구현 계획

### 3.1. 데이터베이스 모델 수정

- **`Parent` 모델 생성:** 학부모 정보를 저장할 `Parent` 모델을 `models.py`에 추가합니다. 이 모델에는 카카오톡 메시지 발송에 필요한 `kakao_user_id` 컬럼이 포함되어야 합니다.
    - `kakao_user_id`는 향후 카카오 로그인을 통해 얻어오는 것을 목표로 하되, 초기 개발 단계에서는 수동으로 입력합니다.
- **학생-학부모 관계 설정:** 학생과 학부모를 연결하는 관계(예: `students_parents` 연관 테이블)를 설정합니다.

### 3.2. 백엔드 구현

1.  **보안: API 키 관리**
    - 프로젝트 루트에 `.env` 파일을 생성하고 `KAKAO_API_KEY=your_rest_api_key` 형식으로 키를 저장합니다.
    - `.gitignore` 파일에 `.env`를 추가하여 키가 Git 저장소에 포함되지 않도록 합니다.
    - 파이썬 코드에서는 `os.getenv('KAKAO_API_KEY')`를 사용하여 키를 안전하게 불러옵니다.

2.  **카카오 메시지 발송 모듈 생성 (`kakao_sender.py`)**
    - `backend/kakao_sender.py` 파일을 새로 생성합니다.
    - `send_report_to_kakao(target_user_id: str, report: schemas.WeeklyReportResponse)` 함수를 구현합니다.
    - 이 함수는 `httpx` 또는 `requests` 라이브러리를 사용하여 카카오 메시지 API를 호출합니다.
        - **API Endpoint:** `POST https://kapi.kakao.com/v1/api/talk/friends/message/default/send`
        - **Header:** `Authorization: KakaoAK ${KAKAO_API_KEY}`
        - **Body:** `receiver_uuids` 와 `template_object` 를 포함합니다.

3.  **메시지 템플릿 구성**
    - 보고서 내용을 효과적으로 전달하기 위해 '리스트 템플릿'을 사용합니다.
    - **템플릿 예시 (`template_object`):**
      ```json
      {
          "object_type": "list",
          "header_title": "Pacer 주간 학습 리포트",
          "header_link": {
              "web_url": "https://pacer.example.com/report/{report_id}",
              "mobile_web_url": "https://pacer.example.com/report/{report_id}"
          },
          "contents": [
              {
                  "title": "학생: {student_name}",
                  "description": "기간: {start_date} ~ {end_date}",
                  "link": { "web_url": "...", "mobile_web_url": "..." }
              },
              {
                  "title": "코치 최종 코멘트",
                  "description": "{coach_comment}",
                  "link": { "web_url": "...", "mobile_web_url": "..." }
              }
          ],
          "buttons": [
              {
                  "title": "전체 리포트 보기",
                  "link": {
                      "web_url": "https://pacer.example.com/report/{report_id}",
                      "mobile_web_url": "https://pacer.example.com/report/{report_id}"
                  }
              }
          ]
      }
      ```

4.  **기존 리포트 발송 API 수정**
    - 이전에 제안했던 `POST /api/v1/report/{report_id}/send` 엔드포인트의 로직을 `kakao_sender.py`의 함수를 호출하도록 수정합니다.

---

## 4. 다음 단계

1.  `Parent` 모델 및 학생-학부모 관계를 `models.py`에 정의합니다.
2.  `.env` 파일을 설정하고, API 키를 안전하게 관리하는 로직을 추가합니다.
3.  `kakao_sender.py` 모듈과 메시지 발송 함수를 구현합니다.
4.  리포트 발송 API 엔드포인트와 `kakao_sender`를 연동합니다.
