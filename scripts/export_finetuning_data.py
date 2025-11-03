import asyncio
import json
import argparse
import logging
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from backend.database import SessionLocal, engine, Base
from backend.models import LLMLog

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mapping for inferring ideal decisions from BAD feedback reason codes
BAD_FEEDBACK_INFERENCE_MAP = {
    "SIMPLE_MISTAKE": {"decision": "REJECT", "reason": "코치 피드백: 단순 실수로 Anki 카드 생성 불필요."},
    "NOT_A_MISTAKE": {"decision": "REJECT", "reason": "코치 피드백: 학생의 실수가 아니므로 Anki 카드 생성 불필요."},
    "CONCEPT_KNOWN": {"decision": "REJECT", "reason": "코치 피드백: 이미 아는 개념이므로 Anki 카드 생성 불필요."},
    "LLM_MISINTERPRETATION": {"decision": "REJECT", "reason": "코치 피드백: LLM이 학생의 실수를 잘못 해석함."},
    # Add more reason codes and their inferred ideal decisions/reasons
}

async def export_finetuning_data(
    output_file: str = "finetuning_data.jsonl",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    logging.info(f"Starting data export to {output_file}")
    
    # Ensure database tables are created
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        query = select(LLMLog).where(LLMLog.coach_feedback.isnot(None))

        conditions = []
        if start_date:
            conditions.append(LLMLog.created_at >= start_date)
        if end_date:
            conditions.append(LLMLog.created_at < (end_date + timedelta(days=1)))
        
        if conditions:
            query = query.where(and_(*conditions))

        result = await db.execute(query)
        logs = result.scalars().all()

        finetuning_entries = []
        for log in logs:
            # Placeholder for student_mistake_summary as it's not stored in LLMLog directly
            # In a real V2, this would be extracted from the original submission or analysis report
            student_mistake_summary_placeholder = "[학생 실수 요약 정보 - LLMLog에 직접 저장되지 않음]"

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
User Mistake Context: {{ "concept": "{log.concept_name}", "mistake": "{student_mistake_summary_placeholder}" }}
Your JSON Response:"""
            
            ideal_decision = log.decision
            ideal_reason = log.reason

            if log.coach_feedback == "BAD":
                inferred_data = BAD_FEEDBACK_INFERENCE_MAP.get(log.reason_code)
                if inferred_data:
                    ideal_decision = inferred_data["decision"]
                    ideal_reason = inferred_data["reason"]
                else:
                    logging.warning(f"Could not infer ideal decision for log {log.log_id} with reason_code '{log.reason_code}'. Skipping entry.")
                    continue # Skip entries where inference is not possible
            
            completion_json = {"decision": ideal_decision, "reason": ideal_reason}

            finetuning_entries.append({
                "prompt": prompt_text,
                "completion": json.dumps(completion_json, ensure_ascii=False)
            })

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for entry in finetuning_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            logging.info(f"Exported {len(finetuning_entries)} entries to {output_file}")
        except IOError as e:
            logging.error(f"Failed to write to output file {output_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export LLM feedback data for fine-tuning.")
    parser.add_argument("--output_file", type=str, default="finetuning_data.jsonl",
                        help="Path to the output JSONL file.")
    parser.add_argument("--start_date", type=date.fromisoformat,
                        help="Start date for filtering logs (YYYY-MM-DD).")
    parser.add_argument("--end_date", type=date.fromisoformat,
                        help="End date for filtering logs (YYYY-MM-DD).")
    args = parser.parse_args()

    asyncio.run(export_finetuning_data(args.output_file, args.start_date, args.end_date))