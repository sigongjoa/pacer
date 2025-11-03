import os
import httpx
import json
from dotenv import load_dotenv

from schemas import WeeklyReportResponse

load_dotenv() # .env 파일에서 환경 변수 로드

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
KAKAO_MESSAGE_URL = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"

async def send_report_via_kakao(target_kakao_id: str, report: WeeklyReportResponse):
    if not KAKAO_API_KEY:
        raise ValueError("KAKAO_API_KEY가 설정되지 않았습니다.")

    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }

    template = {
        "object_type": "list",
        "header_title": f"{report.student_name} 주간 학습 리포트",
        "header_link": {
            "web_url": f"https://pacer.example.com/report/{report.report_id}",
            "mobile_web_url": f"https://pacer.example.com/report/{report.report_id}"
        },
        "contents": [
            {
                "title": f"기간: {report.report_period_start} ~ {report.report_period_end}",
                "description": f"총 {report.llm_judgments_count}건의 AI 분석과 {report.anki_cards_reviewed_count}건의 복습이 진행되었습니다.",
                "link": { "web_url": f"https://pacer.example.com/report/{report.report_id}" }
            },
            {
                "title": "코치 최종 코멘트",
                "description": report.coach_comment or "코멘트가 없습니다.",
                "link": { "web_url": f"https://pacer.example.com/report/{report.report_id}" }
            }
        ],
        "buttons": [
            {
                "title": "상세 리포트 확인하기",
                "link": { "web_url": f"https://pacer.example.com/report/{report.report_id}" }
            }
        ]
    }

    data = {
        "receiver_uuids": json.dumps([target_kakao_id]),
        "template_object": json.dumps(template)
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(KAKAO_MESSAGE_URL, headers=headers, data=data)
        response.raise_for_status() # 오류 발생 시 예외 처리
        return response.json()
