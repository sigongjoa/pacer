# Anki 카드 자동화 및 코치 피드백 워크플로우 (V1)

## 1. 개요

본 문서는 Pacer 시스템의 V1 아키텍처에 기반하여, **저비용으로 운영 가능한** Anki 카드 자동 생성 및 코치 피드백 워크플로우를 정의합니다. V1의 핵심은 **자동 재학습(Fine-tuning) 대신, 피드백을 기록(Logging)하여 수동 개선(Prompt Engineering)의 기반을 마련**하는 것입니다.

## 2. 워크플로우 (V1)

### 1단계: 실시간 자동화 루프 (코치 개입 없음)

1.  **오답 발생 및 규칙 기반 분석:** 학생이 과제를 제출하면, **규칙 기반(Rule-Based) AIModule**이 오답에 대한 구조화된 **[1차 분석 리포트]**를 생성합니다. (LLM 미사용)
2.  **LLM 필터 판단 요청:** 플랫폼은 `error_context`와 같이 **경량화된 정보**만을 `LLMFilter`에 보내 Anki 카드 등록 필요성 판단을 요청합니다. (LLM 1회 호출)
3.  **판단 및 결과 기록:** `LLMFilter`는 판단 결과를 플랫폼에 반환하고, 모든 판단 과정과 결과는 `LLM_LOGS` 데이터베이스 테이블에 기록됩니다.

### 2단계: 코치의 비동기 피드백 루프 (주기적)

1.  **피드백 요청:** 플랫폼은 주기적으로 코치에게 "이번 주 LLM이 N건의 카드를 자동 등록했습니다. 피드백해주세요." 와 같은 알림을 보냅니다.
2.  **피드백 수행:** 코치는 대시보드에서 `LLM_LOGS` 이력을 검토하고, 각 판단에 대해 "좋음 👍" 또는 "나쁨 👎" 피드백을 남깁니다.
3.  **피드백 기록 (V1 핵심 변경점):** 코치의 모든 피드백은 `LLM_LOGS` 테이블의 해당 레코드에 **업데이트(기록)됩니다.** 이 피드백은 **자동으로 LLM 모델을 개선하지 않습니다.**
    *   **목적:** 이 기록들은 향후 V2 모델 개발이나, 개발자가 **수동으로 프롬프트를 개선(Prompt Engineering)**하는 데 사용될 '황금 데이터셋'이 됩니다.

## 3. 시퀀스 다이어그램 (V1)

```mermaid
sequenceDiagram
    participant Student as 학생
    participant Coach as 코치 (본인)
    participant Platform as 플랫폼
    participant AIModule as <<Rule-Based>> AI 분석 모듈
    participant LLMFilter as <<V1: Judge Only>> LLM 필터
    participant DB as 데이터베이스

    %% --- 1. 실시간 자동화 루프 (V1) ---
    loop (실시간) 학생 학습 및 자동 필터링
        Student->>Platform: 과제 제출 (오답 발생)
        Platform->>AIModule: '학생A' 오답 분석 요청
        AIModule-->>Platform: [1차 분석 리포트] (규칙 기반)
        
        Platform->>LLMFilter: [판단 요청] "error_context: {...}"
        LLMFilter-->>Platform: [판단 결과] "decision: APPROVE"
        
        Platform->>DB: LLM의 [판단 결과] 로그 저장
        alt decision is APPROVE
            Platform->>AIModule: Anki 카드 생성 지시
            AIModule->>DB: [Anki 카드] 저장
        end
    end

    %% --- 2. 코치의 비동기 피드백 루프 (V1) ---
    loop (주 1회) 코치의 LLM 피드백
        Platform->>Coach: [주간 알림] "LLM 판단 N건에 대해 피드백해주세요."
        
        Coach->>Platform: (대시보드) LLM의 '자동 승인' 이력(Log) 검토
        
        opt LLM의 결정이 '나쁜' 경우
            Coach->>Platform: (클릭) **"판단 나쁨 👎"** + (사유 선택)
            Platform->>DB: **[피드백 로그 업데이트]** "log_id: ..., feedback: 'BAD'"
            note right of DB: 자동 재학습(X), 수동 분석용 데이터 축적(O)
            
            Coach->>Platform: "해당 Anki 카드 즉시 삭제" 요청
            Platform->>AIModule: Anki 카드 삭제 지시
            AIModule->>DB: [Anki 카드] 삭제
        else LLM의 결정이 '좋은' 경우
            Coach->>Platform: (클릭) "판단 좋음 👍"
            Platform->>DB: **[피드백 로그 업데이트]** "log_id: ..., feedback: 'GOOD'"
        end
    end
```