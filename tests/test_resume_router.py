"""Integration tests for the resume analysis router."""

from unittest.mock import patch

import fitz
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app

_MOCK_LLM_RESULT = {
    "bullet_rewrites": [
        {
            "original": "Did tasks",
            "improved": "Led cross-functional tasks",
            "reason": "More impactful",
        },
        {
            "original": "Helped team",
            "improved": "Collaborated with 5-member team",
            "reason": "Quantified",
        },
        {
            "original": "Used Python",
            "improved": "Engineered Python solutions",
            "reason": "Stronger verb",
        },
    ],
    "overall_suggestions": [
        "Add measurable achievements",
        "Include relevant certifications",
        "Tailor summary to role",
        "Add LinkedIn URL",
    ],
}

_MOCK_RESUME_TEXT = (
    "Experienced software engineer with skills in Python, machine learning, "
    "cloud infrastructure, data analysis, and agile development. "
    "Led multiple projects and collaborated with cross-functional teams."
)

_VALID_JD = (
    "We are seeking a skilled software engineer with experience in Python, "
    "machine learning, cloud platforms, data pipelines, and agile methodologies. "
    "Strong communication and collaboration skills required for this role."
)


def _make_pdf_bytes() -> bytes:
    """Create a minimal in-memory PDF for testing."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), _MOCK_RESUME_TEXT)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    """GET /health should return 200 with status: ok."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_missing_file_returns_422() -> None:
    """POST /analyze with no file should return 422 Unprocessable Entity."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/resume/analyze",
            data={"job_description": _VALID_JD},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_file_extension() -> None:
    """POST with a .txt file should return 400 Bad Request."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/v1/resume/analyze",
            files={"resume_file": ("resume.txt", b"plain text content", "text/plain")},
            data={"job_description": _VALID_JD},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_successful_analysis() -> None:
    """POST with a valid PDF and JD should return a full analysis response."""
    pdf_bytes = _make_pdf_bytes()

    with (
        patch("app.routers.resume.parse_resume", return_value=_MOCK_RESUME_TEXT),
        patch("app.routers.resume.get_resume_feedback", return_value=_MOCK_LLM_RESULT),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/resume/analyze",
                files={"resume_file": ("resume.pdf", pdf_bytes, "application/pdf")},
                data={"job_description": _VALID_JD},
            )

    assert response.status_code == 200
    data = response.json()

    assert "match_score" in data
    assert "score_label" in data
    assert "keyword_gap" in data
    assert "bullet_rewrites" in data
    assert "overall_suggestions" in data
    assert len(data["bullet_rewrites"]) == 3
    assert len(data["overall_suggestions"]) == 4
    assert 0 <= data["match_score"] <= 100
    assert data["score_label"] in {"Weak", "Fair", "Good", "Strong"}
