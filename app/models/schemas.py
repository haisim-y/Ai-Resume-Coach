"""Pydantic v2 request and response models for the AI Resume Coach API."""

from pydantic import BaseModel, Field


class ResumeAnalysisRequest(BaseModel):
    """Request model for resume analysis (used for documentation; actual input via Form)."""

    job_description: str = Field(..., min_length=50, max_length=5000)


class KeywordGap(BaseModel):
    """Keyword gap analysis between resume and job description."""

    missing_keywords: list[str]
    present_keywords: list[str]
    match_percentage: float


class BulletRewrite(BaseModel):
    """A single bullet point rewrite suggestion."""

    original: str
    improved: str
    reason: str


class ResumeAnalysisResponse(BaseModel):
    """Full analysis response returned to the client."""

    match_score: int  # 0–100
    score_label: str  # "Weak" / "Fair" / "Good" / "Strong"
    keyword_gap: KeywordGap
    bullet_rewrites: list[BulletRewrite]  # top 3 rewrites
    overall_suggestions: list[str]  # 3–5 actionable tips
    processing_time_ms: int


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    detail: str | None = None
