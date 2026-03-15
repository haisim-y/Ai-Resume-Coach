"""Keyword matching and scoring logic for resume vs. job description analysis."""

import logging

from app.models.schemas import KeywordGap
from app.utils.text import extract_keywords

logger = logging.getLogger(__name__)


def calculate_match_score(resume_text: str, job_description: str) -> KeywordGap:
    """
    Extract keywords from both texts and calculate keyword overlap.

    match_percentage = len(intersection) / len(jd_keywords) * 100

    Returns a KeywordGap containing present_keywords, missing_keywords,
    and match_percentage. If jd_keywords is empty, match_percentage is 0.0.
    """
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    if not jd_keywords:
        logger.warning("Job description produced no extractable keywords.")
        return KeywordGap(
            missing_keywords=[],
            present_keywords=[],
            match_percentage=0.0,
        )

    present = resume_keywords & jd_keywords
    missing = jd_keywords - resume_keywords
    match_percentage = len(present) / len(jd_keywords) * 100

    logger.debug(
        "Keyword match: %d present / %d total JD keywords (%.1f%%)",
        len(present),
        len(jd_keywords),
        match_percentage,
    )

    return KeywordGap(
        missing_keywords=sorted(missing),
        present_keywords=sorted(present),
        match_percentage=round(match_percentage, 2),
    )


def get_score_label(score: int) -> str:
    """
    Return a human-readable label for the given match score.

    Ranges:
        0–40   → "Weak"
        41–60  → "Fair"
        61–80  → "Good"
        81–100 → "Strong"
    """
    if score <= 40:
        return "Weak"
    if score <= 60:
        return "Fair"
    if score <= 80:
        return "Good"
    return "Strong"
