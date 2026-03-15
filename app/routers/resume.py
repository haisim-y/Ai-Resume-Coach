"""Router for resume analysis endpoints."""

import logging
import time
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.config import settings
from app.models.schemas import BulletRewrite, KeywordGap, ResumeAnalysisResponse
from app.services.llm import get_resume_feedback
from app.services.parser import parse_resume
from app.services.scorer import calculate_match_score, get_score_label

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    resume_file: UploadFile,
    job_description: str = Form(..., min_length=50, max_length=5000),
) -> ResumeAnalysisResponse:
    """
    Analyse a resume against a job description and return AI-powered feedback.

    Steps:
    1. Validate the uploaded file extension.
    2. Read the file bytes.
    3. Parse text from PDF or DOCX.
    4. Calculate keyword match score between resume and job description.
    5. Generate AI bullet point rewrites and improvement suggestions via OpenRouter.
    6. Return a structured analysis response with all results and processing time.

    Args:
        resume_file: The uploaded resume file (PDF or DOCX, max 5 MB).
        job_description: The target job description text (50–5000 characters).

    Returns:
        ResumeAnalysisResponse containing match score, keyword gap analysis,
        bullet rewrites, suggestions, and processing time.
    """
    extension = Path(resume_file.filename or "").suffix.lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        logger.warning("Rejected upload with unsupported extension: %s", extension)
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{extension}'. "
                f"Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            ),
        )

    file_bytes = await resume_file.read()
    start_time = time.time()

    try:
        resume_text = parse_resume(file_bytes, resume_file.filename or "resume")
    except ValueError as exc:
        logger.warning("Resume parsing failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    keyword_gap: KeywordGap = calculate_match_score(resume_text, job_description)
    match_score = int(keyword_gap.match_percentage)
    score_label = get_score_label(match_score)

    try:
        llm_result = get_resume_feedback(resume_text, job_description, keyword_gap)
    except RuntimeError as exc:
        logger.error("LLM feedback generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    bullet_rewrites = [
        BulletRewrite(**item) for item in llm_result.get("bullet_rewrites", [])
    ]
    overall_suggestions: list[str] = llm_result.get("overall_suggestions", [])

    processing_time_ms = int((time.time() - start_time) * 1000)

    logger.info(
        "Analysis complete: score=%d label=%s time=%dms",
        match_score,
        score_label,
        processing_time_ms,
    )

    return ResumeAnalysisResponse(
        match_score=match_score,
        score_label=score_label,
        keyword_gap=keyword_gap,
        bullet_rewrites=bullet_rewrites,
        overall_suggestions=overall_suggestions,
        processing_time_ms=processing_time_ms,
    )
