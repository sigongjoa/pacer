from fastapi import APIRouter
from schemas import AnalyzeRequest, AnalysisReport, ErrorContext

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["AI Module"],
)

def run_rule_based_analysis(request: AnalyzeRequest) -> AnalysisReport:
    """
    V1의 규칙 기반 분석을 수행합니다.
    현재는 "1+1=3"이라는 특정 케이스만 처리하는 간단한 예시입니다.
    """
    error_contexts = []
    score = 100.0

    # "1+1=3" 케이스를 하드코딩하여 확인
    q1_answer = request.raw_answers.get("q1", {}).get("answer")
    if q1_answer == "3":
        score = 0.0
        error_contexts.append(
            ErrorContext(
                question_type="BASIC_ARITHMETIC",
                concept_name="덧셈",
                student_mistake_summary="1+1의 답을 3으로 계산함."
            )
        )

    return AnalysisReport(score=score, error_contexts=error_contexts)


@router.post("/analyze", response_model=AnalysisReport)
def analyze_submission(request: AnalyzeRequest):
    """
    규칙 기반으로 학생의 제출물을 분석하는 API 엔드포인트입니다.
    V1에서는 LLM을 호출하지 않습니다.
    """
    report = run_rule_based_analysis(request)
    return report
