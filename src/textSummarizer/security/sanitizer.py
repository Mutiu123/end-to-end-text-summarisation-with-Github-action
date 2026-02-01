"""
Input sanitization module.
Prevents injection attacks by cleaning and validating user input.
"""

import html
import re
from typing import Optional


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize user-provided text input.

    Performs the following operations:
    - Strips leading and trailing whitespace
    - Escapes HTML entities to prevent XSS
    - Removes null bytes
    - Removes control characters (except newlines and tabs)
    - Truncates to maximum length

    Args:
        text: Raw user input text.
        max_length: Maximum allowed character length.

    Returns:
        Sanitized text string.
    """
    if not text:
        return ""

    text = text.strip()
    text = text.replace("\x00", "")
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = html.escape(text, quote=True)
    text = text[:max_length]

    return text


def validate_text_length(
    text: str, min_length: int = 10, max_length: int = 10000
) -> Optional[str]:
    """Validate that text meets length requirements.

    Args:
        text: The text to validate.
        min_length: Minimum character count.
        max_length: Maximum character count.

    Returns:
        Error message string if validation fails, None if valid.
    """
    if len(text) < min_length:
        return f"Text must be at least {min_length} characters long"
    if len(text) > max_length:
        return f"Text must not exceed {max_length} characters"
    return None


def contains_suspicious_patterns(text: str) -> bool:
    """Check if text contains patterns that may indicate injection attempts.

    Args:
        text: The text to check.

    Returns:
        True if suspicious patterns are detected.
    """
    suspicious_patterns = [
        r"<script[\s>]",
        r"javascript:",
        r"on\w+\s*=",
        r"\{\{.*\}\}",
        r"\$\{.*\}",
        r"__import__",
        r"eval\s*\(",
        r"exec\s*\(",
    ]

    text_lower = text.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower):
            return True
    return False
