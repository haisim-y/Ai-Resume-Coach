"""Tests for the keyword scoring service."""

import pytest

from app.services.scorer import calculate_match_score, get_score_label


_RESUME_TEXT = (
    "Experienced software engineer skilled in Python, machine learning, "
    "data analysis, cloud infrastructure, and agile development methodologies."
)

_JD_TEXT = (
    "We are looking for a software engineer proficient in Python, machine learning, "
    "deep learning, cloud infrastructure, communication skills, and agile practices."
)


def test_match_percentage_in_range() -> None:
    """match_percentage should always be between 0.0 and 100.0."""
    gap = calculate_match_score(_RESUME_TEXT, _JD_TEXT)
    assert 0.0 <= gap.match_percentage <= 100.0


def test_full_match() -> None:
    """Identical resume and JD text should yield 100% match."""
    text = (
        "Python developer with experience in machine learning, data analysis, "
        "cloud infrastructure, agile development, communication, testing, deployment."
    )
    gap = calculate_match_score(text, text)
    assert gap.match_percentage == 100.0


def test_no_match() -> None:
    """Resume with no JD keywords should yield 0% match."""
    resume = "cooking baking gardening painting singing dancing"
    jd = "Python machine learning cloud infrastructure agile development deployment"
    gap = calculate_match_score(resume, jd)
    assert gap.match_percentage == 0.0


def test_score_label_weak() -> None:
    """Score of 30 should be labelled 'Weak'."""
    assert get_score_label(30) == "Weak"


def test_score_label_fair() -> None:
    """Score of 50 should be labelled 'Fair'."""
    assert get_score_label(50) == "Fair"


def test_score_label_good() -> None:
    """Score of 70 should be labelled 'Good'."""
    assert get_score_label(70) == "Good"


def test_score_label_strong() -> None:
    """Score of 90 should be labelled 'Strong'."""
    assert get_score_label(90) == "Strong"
