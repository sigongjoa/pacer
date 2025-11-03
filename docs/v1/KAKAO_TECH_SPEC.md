# Pacer 카카오톡 연동 기술 사양서

## 1. 개요

본 문서는 카카오톡 채널 메시지 API를 사용하여 주간 리포트를 발송하는 기능 구현에 필요한 구체적인 기술 사양을 정의합니다. `KAKAO_SETUP_GUIDE.md`의 사용자 설정이 완료된 후, 본 사양서에 따라 개발을 진행합니다.

---

## 2. 데이터베이스 스키마 (`models.py`)

### 2.1. `student_parent_association` 테이블

- 학생과 학부모의 다대다(many-to-many) 관계를 정의하기 위한 연관 테이블입니다.

```python
from sqlalchemy import Table, Column, String, Integer, ForeignKey

student_parent_association = Table(
    'student_parent_association',
    Base.metadata,
    Column('student_id', String, ForeignKey('students.student_id'), primary_key=True),
    Column('parent_id', Integer, ForeignKey('parents.parent_id'), primary_key=True)
)
```

### 2.2. `Parent` 모델

- 학부모 정보를 저장하는 새로운 모델입니다.

```python
from sqlalchemy.orm import relationship

class Parent(Base):
    __tablename__ = "parents"

    parent_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # 카카오 메시지 발송을 위한 식별자. 카카오 로그인 연동 시 확보.
    kakao_user_id = Column(String, unique=True, index=True, nullable=True)

    students = relationship(
        "Student",
        secondary=student_parent_association,
        back_populates="parents"
    )
```

### 2.3. `Student` 모델 수정

- `Parent`와의 다대다 관계를 설정합니다.

```python
# Student 모델 내부에 추가
parents = relationship(
    "Parent",
    secondary=student_parent_association,
    back_populates="students"
)
```

---

## 3. API 스키마 (`schemas.py`)

- 학부모 생성 및 조회를 위한 Pydantic 스키마를 추가합니다.

```python
# Parent Schemas
class ParentBase(BaseModel):
    name: str
    kakao_user_id: Optional[str] = None

class ParentCreate(ParentBase):
    pass

class ParentResponse(ParentBase):
    parent_id: int

    model_config = ConfigDict(from_attributes=True)

# Student 스키마에 Parent 정보 추가
class StudentResponse(BaseModel):
    student_id: str
    name: str
    settings: Dict[str, Any]
    parents: List[ParentResponse] = [] # 추가

    model_config = ConfigDict(from_attributes=True)
```

---

## 4. CRUD 함수 (`crud.py`)

- `Parent` 모델에 대한 데이터베이스 처리 함수를 추가합니다.

```python
# 추가될 함수 시그니처
async def create_parent(db: AsyncSession, parent: schemas.ParentCreate) -> models.Parent:
    # ... 구현 ...

async def get_parent(db: AsyncSession, parent_id: int) -> Optional[models.Parent]:
    # ... 구현 ...

async def get_parents_by_student(db: AsyncSession, student_id: str) -> List[models.Parent]:
    # ... 구현 ...

async def assign_parent_to_student(db: AsyncSession, student_id: str, parent_id: int) -> Optional[models.Student]:
    # ... 구현 ...
```

---

## 5. 카카오 메시지 발송 모듈 (`kakao_sender.py`)

- 메시지 발송 로직을 담당할 `backend/kakao_sender.py` 파일을 생성합니다.

```python
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
                "link": { "web_url": f".../{report.report_id}" }
            },
            {
                "title": "코치 최종 코멘트",
                "description": report.coach_comment or "코멘트가 없습니다.",
                "link": { "web_url": f".../{report.report_id}" }
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
```

---

## 6. API 엔드포인트 수정 (`report_router.py`)

- 리포트 발송을 위한 `POST /send` 엔드포인트를 추가합니다.

```python
from . import kakao_sender # kakao_sender 임포트

@router.post("/{report_id}/send", status_code=200)
async def send_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_report = await crud.get_weekly_report(db, report_id=report_id)
    if not db_report or db_report.status != 'finalized':
        raise HTTPException(status_code=400, detail="리포트가 최종 승인 상태가 아닙니다.")

    db_student = await crud.get_student(db, student_id=db_report.student_id)
    if not db_student.parents:
        raise HTTPException(status_code=404, detail="리포트를 수신할 학부모가 등록되지 않았습니다.")

    # 모든 연결된 학부모에게 발송
    sent_count = 0
    for parent in db_student.parents:
        if parent.kakao_user_id:
            try:
                await kakao_sender.send_report_via_kakao(parent.kakao_user_id, db_report)
                sent_count += 1
            except Exception as e:
                # 특정 학부모에게 발송 실패 시 로깅 (추후 구현)
                print(f"카카오 메시지 발송 실패: {e}")
    
    # 발송 완료 후 리포트 상태 변경
    db_report.status = 'sent'
    await db.commit()

    return {"message": f"총 {len(db_student.parents)}명의 학부모 중 {sent_count}명에게 리포트가 발송되었습니다."}
```
