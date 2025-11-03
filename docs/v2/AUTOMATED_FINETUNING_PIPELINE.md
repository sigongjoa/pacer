# Automated Fine-tuning Pipeline

## 1. Overview
This document details the design and implementation of the automated fine-tuning pipeline for PACER V2. The goal is to leverage the feedback data collected in V1 to continuously improve the performance of the LLM used in the `LLMFilter`.

## 2. Data Preparation
*   **Source Data:** `LLM_LOGS` table, specifically entries with `coach_feedback` (GOOD/BAD).
*   **Data Transformation:** Convert raw log entries into a format suitable for LLM fine-tuning (e.g., JSONL).
    *   **Input:** `error_context` (concept_name, student_mistake_summary) and the original prompt used for the LLM call.
    *   **Output (Completion):** The ideal `decision` (APPROVE/REJECT) and `reason` based on coach feedback.
        *   For `GOOD` feedback, the original LLM decision is considered correct.
        *   For `BAD` feedback, the `reason_code` will be used to infer the correct decision (e.g., `SIMPLE_MISTAKE` implies `REJECT`).
*   **Script:** `scripts/export_finetuning_data.py` will be developed to perform this extraction and transformation.

## 3. Fine-tuning Process
*   **Base Model:** The same base LLM (e.g., `llama2:latest` or a more suitable open-source model) used in V1.
*   **Framework:** Utilize a fine-tuning framework (e.g., Hugging Face Transformers, LoRA) to adapt the base model.
*   **Automation:** The fine-tuning job will be triggered periodically (e.g., weekly) via a CI/CD pipeline or a dedicated MLOps orchestrator.

## 4. Model Evaluation
*   **Metrics:** Evaluate the fine-tuned model's performance using metrics relevant to the `LLMFilter`'s task (e.g., accuracy, precision, recall on a held-out validation set).
*   **Comparison:** Compare the new model's performance against the currently deployed model to determine if it offers significant improvements.

## 5. Versioning
*   Each fine-tuned model will be versioned and stored in a model registry.