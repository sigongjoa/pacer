from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from llm_filter import router as llm_router
from student_router import router as student_router
from card_router import router as card_router
from submission_router import router as submission_router
from coach_router import router as coach_router
from report_router import router as report_router
from parent_router import router as parent_router

from database import engine, Base
import models # 모든 모델을 임포트하여 Base.metadata에 등록

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 DB 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 애플리케이션 종료 시 정리 작업 (필요하다면)

app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

app.include_router(llm_router)
app.include_router(student_router)
app.include_router(card_router)
app.include_router(submission_router)
app.include_router(coach_router)
app.include_router(report_router)
app.include_router(parent_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pacer API"}
