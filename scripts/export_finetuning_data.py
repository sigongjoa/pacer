import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, timedelta

from backend.database import SessionLocal, engine, Base
from backend.models import LLMLog

async def export_finetuning_data(output_file: str = "finetuning_data.jsonl"):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        # Fetch all LLMLogs that have coach feedback
        result = await db.execute(
            select(LLMLog).where(LLMLog.coach_feedback.isnot(None))
        )
        logs = result.scalars().all()

        finetuning_entries = []
        for log in logs:
            prompt_text = f"""[SYSTEM]
You are a helpful AI assistant that functions as a JSON API. You must only answer in JSON format. Do not add any other text. Your task is to decide if a student's mistake is worth creating a review card (Anki card).

[INSTRUCTIONS]
- Analyze the user's mistake based on the provided context.
- The JSON output must contain two keys: "decision" (string) and "reason" (string).
- The value for "decision" must be either "APPROVE" or "REJECT".
- "APPROVE" if the mistake is a core concept error, a misunderstanding of a definition, or a critical factual error.
- "REJECT" if the mistake is a simple calculation error, a typo, or not educationally significant.
- The "reason" must be a short explanation in Korean.

[CURRENT TASK]
User Mistake Context: {{ "concept": "{log.concept_name}", "mistake": "Student mistake summary here (not stored in log, placeholder)" }}
Your JSON Response:"""
            
            # Determine the ideal completion based on coach feedback
            ideal_decision = log.decision
            ideal_reason = log.reason

            if log.coach_feedback == "BAD":
                # If feedback is BAD, we need to infer the *correct* decision
                # This is a simplified logic and might need more sophistication
                if log.reason_code == "SIMPLE_MISTAKE": # Example reason code
                    ideal_decision = "REJECT"
                    ideal_reason = "코치 피드백: 단순 실수로 Anki 카드 생성 불필요." # Example
                elif log.reason_code == "NOT_A_MISTAKE":
                    ideal_decision = "REJECT"
                    ideal_reason = "코치 피드백: 학생의 실수가 아니므로 Anki 카드 생성 불필요."
                # Add more logic here for other BAD reason_codes
                else:
                    # If we can't infer, we might skip or use a default
                    print(f"Warning: Could not infer ideal decision for log {log.log_id} with reason_code {log.reason_code}. Skipping.")
                    continue
            
            completion_json = {"decision": ideal_decision, "reason": ideal_reason}

            finetuning_entries.append({
                "prompt": prompt_text,
                "completion": json.dumps(completion_json, ensure_ascii=False)
            })

        with open(output_file, "w", encoding="utf-8") as f:
            for entry in finetuning_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Exported {len(finetuning_entries)} entries to {output_file}")

if __name__ == "__main__":
    asyncio.run(export_finetuning_data())
