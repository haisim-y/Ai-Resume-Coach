"""OpenRouter LLM service for generating resume feedback via the OpenAI-compatible API."""

import json
import logging

from openai import APIConnectionError, APIError, OpenAI

from app.config import settings
from app.models.schemas import KeywordGap

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.LLM_BASE_URL,
)

_SYSTEM_MESSAGE = (
    "You are an expert resume coach. Always respond with valid JSON only. "
    "No markdown, no explanation outside the JSON."
)

_USER_TEMPLATE = """\
You are reviewing a resume against a job description.

### Resume (truncated)
{resume_text}

### Job Description (truncated)
{job_description}

### Missing Keywords
{missing_keywords}

Return EXACTLY the following JSON structure (no other text):
{{
  "bullet_rewrites": [
    {{"original": "...", "improved": "...", "reason": "..."}},
    {{"original": "...", "improved": "...", "reason": "..."}},
    {{"original": "...", "improved": "...", "reason": "..."}}
  ],
  "overall_suggestions": [
    "...", "...", "...", "..."
  ]
}}

Rules:
- Provide exactly 3 bullet_rewrites using real bullet points from the resume.
- Provide exactly 4 overall_suggestions as concise, actionable strings.
- Do not include any text outside the JSON object.
"""


def get_resume_feedback(
    resume_text: str,
    job_description: str,
    keyword_gap: KeywordGap,
) -> dict:
    """
    Call OpenRouter with a structured prompt and return parsed feedback.

    The prompt includes the resume (truncated to 3000 chars), the job description
    (truncated to 1500 chars), and the list of missing keywords. The LLM is
    instructed to return a JSON object with bullet_rewrites and overall_suggestions.

    Raises:
        RuntimeError: If the API call fails or returns invalid JSON.
    """
    missing_kw_str = ", ".join(keyword_gap.missing_keywords) or "none"

    user_message = _USER_TEMPLATE.format(
        resume_text=resume_text[:3000],
        job_description=job_description[:1500],
        missing_keywords=missing_kw_str,
    )

    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            max_tokens=settings.MAX_TOKENS,
            messages=[
                {"role": "system", "content": _SYSTEM_MESSAGE},
                {"role": "user", "content": user_message},
            ],
            extra_headers={
                "HTTP-Referer": settings.SITE_URL,
                "X-Title": settings.SITE_NAME,
            },
        )
    except (APIError, APIConnectionError) as exc:
        logger.error("LLM API error: %s", exc)
        raise RuntimeError(f"LLM service error: {exc}") from exc

    raw_content = response.choices[0].message.content

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned invalid JSON: %s", raw_content)
        raise RuntimeError("LLM returned invalid JSON") from exc
