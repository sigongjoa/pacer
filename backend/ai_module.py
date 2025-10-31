from typing import Optional
import schemas

async def analyze_submission(submission: schemas.SubmissionRequest) -> Optional[schemas.ErrorContext]:
    """
    규칙 기반으로 학생의 과제 제출물을 분석하여 오답 컨텍스트를 생성합니다.
    V1에서는 LLM을 사용하지 않는 간단한 규칙 기반 분석을 수행합니다.
    """
    if submission.assignment_id == "history-01":
        # 임진왜란 발발 연도 문제 시뮬레이션
        # 1592년이 정답인데, 1692년과 1592년이 모두 언급되면 혼동으로 판단
        if "1592" in submission.answer and "1692" in submission.answer:
            return schemas.ErrorContext(
                question_type="HISTORY",
                concept_name="임진왜란 발발 연도",
                student_mistake_summary="1592년을 1692년으로 잘못 기재함." # 실제로는 1592년이 정답
            )
        # 1592년이 언급되지 않고 임진왜란만 언급되면 연도를 모르는 것으로 판단
        elif "1592" not in submission.answer and "임진왜란" in submission.answer:
             return schemas.ErrorContext(
                question_type="HISTORY",
                concept_name="임진왜란 발발 연도",
                student_mistake_summary="임진왜란 연도를 정확히 알지 못함."
            )
    
    # 다른 과제 유형이나 규칙은 여기에 추가

    return None # 오답 컨텍스트를 찾지 못함
