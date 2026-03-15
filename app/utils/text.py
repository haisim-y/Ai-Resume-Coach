"""Text cleaning and keyword extraction utilities."""

import re
import unicodedata


STOPWORDS: set[str] = {
    "the", "and", "for", "with", "this", "that", "from", "have",
    "will", "your", "they", "been", "their", "which", "when", "into",
    "about", "more", "also",
}


def clean_text(text: str) -> str:
    """Strip excessive whitespace and normalise unicode."""
    normalised = unicodedata.normalize("NFKC", text)
    collapsed = re.sub(r"\s+", " ", normalised)
    return collapsed.strip()


def extract_keywords(text: str) -> set[str]:
    """
    Lowercase, remove stopwords, tokenise on word boundaries.

    Returns unique words that are at least 4 characters long and are not
    in the hardcoded stopwords list.
    """
    lowered = text.lower()
    tokens = re.findall(r"\b[a-z]+\b", lowered)
    return {
        token for token in tokens
        if len(token) >= 4 and token not in STOPWORDS
    }
