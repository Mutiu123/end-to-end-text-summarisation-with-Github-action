"""
Tests for the input sanitization module.
"""

import pytest

from textSummarizer.security.sanitizer import (
    contains_suspicious_patterns,
    sanitize_text,
    validate_text_length,
)


class TestSanitizer:
    """Test suite for input sanitization functions."""

    def test_sanitize_text_basic(self):
        """Test basic text sanitization with normal input."""
        text = "  Hello, world!  "
        result = sanitize_text(text)
        assert result == "Hello, world!"

    def test_sanitize_text_removes_null_bytes(self):
        """Test that null bytes are removed from text."""
        text = "Hello\x00World"
        result = sanitize_text(text)
        assert "\x00" not in result
        assert result == "HelloWorld"

    def test_sanitize_text_removes_control_characters(self):
        """Test that control characters are removed (except newlines/tabs)."""
        text = "Hello\x01\x02\x03World\x1f"
        result = sanitize_text(text)
        assert result == "HelloWorld"

        # Newlines and tabs should be preserved
        text_with_whitespace = "Hello\nWorld\tTest"
        result = sanitize_text(text_with_whitespace)
        assert "\n" in result
        assert "\t" in result

    def test_sanitize_text_escapes_html(self):
        """Test that HTML entities are escaped."""
        text = '<script>alert("XSS")</script>'
        result = sanitize_text(text)
        assert "&lt;script&gt;" in result
        assert "<script>" not in result
        assert "&quot;" in result

    def test_sanitize_text_truncates_to_max_length(self):
        """Test that text is truncated to maximum length."""
        text = "a" * 1000
        result = sanitize_text(text, max_length=100)
        assert len(result) == 100

    def test_sanitize_text_empty_input(self):
        """Test sanitize_text with empty input."""
        assert sanitize_text("") == ""
        assert sanitize_text("   ") == ""

    def test_validate_text_length_valid(self):
        """Test text length validation with valid input."""
        text = "This is a valid text with sufficient length."
        result = validate_text_length(text, min_length=10, max_length=100)
        assert result is None

    def test_validate_text_length_too_short(self):
        """Test validation fails when text is too short."""
        text = "Short"
        result = validate_text_length(text, min_length=10, max_length=100)
        assert result is not None
        assert "at least 10 characters" in result

    def test_validate_text_length_too_long(self):
        """Test validation fails when text is too long."""
        text = "a" * 200
        result = validate_text_length(text, min_length=10, max_length=100)
        assert result is not None
        assert "not exceed 100 characters" in result

    def test_validate_text_length_exact_boundaries(self):
        """Test validation at exact min and max boundaries."""
        # Exactly at minimum
        text_min = "a" * 10
        assert validate_text_length(text_min, min_length=10, max_length=100) is None

        # Exactly at maximum
        text_max = "a" * 100
        assert validate_text_length(text_max, min_length=10, max_length=100) is None

    def test_contains_suspicious_patterns_script_tags(self):
        """Test detection of script tags."""
        assert contains_suspicious_patterns("<script>alert('XSS')</script>") is True
        assert contains_suspicious_patterns("<SCRIPT>alert('XSS')</SCRIPT>") is True
        assert contains_suspicious_patterns("normal text") is False

    def test_contains_suspicious_patterns_javascript_protocol(self):
        """Test detection of javascript: protocol."""
        assert contains_suspicious_patterns('javascript:alert("XSS")') is True
        assert contains_suspicious_patterns('JAVASCRIPT:void(0)') is True

    def test_contains_suspicious_patterns_event_handlers(self):
        """Test detection of HTML event handlers."""
        assert contains_suspicious_patterns('onerror=alert("XSS")') is True
        assert contains_suspicious_patterns('onclick=malicious()') is True
        assert contains_suspicious_patterns('onload=steal()') is True

    def test_contains_suspicious_patterns_template_injection(self):
        """Test detection of template injection patterns."""
        assert contains_suspicious_patterns('{{7*7}}') is True
        assert contains_suspicious_patterns('${process.env}') is True

    def test_contains_suspicious_patterns_python_code(self):
        """Test detection of Python code execution patterns."""
        assert contains_suspicious_patterns('__import__("os")') is True
        assert contains_suspicious_patterns('eval(malicious_code)') is True
        assert contains_suspicious_patterns('exec(payload)') is True

    def test_contains_suspicious_patterns_safe_text(self):
        """Test that normal text doesn't trigger false positives."""
        safe_texts = [
            "This is a normal conversation about scripting.",
            "I need to evaluate the results.",
            "The executive summary is important.",
            "Import this file into the system.",
        ]
        for text in safe_texts:
            assert contains_suspicious_patterns(text) is False

    def test_sanitize_text_combined_operations(self):
        """Test sanitize_text with multiple operations combined."""
        text = '  <script>alert("XSS")</script>\x00\x01  '
        result = sanitize_text(text, max_length=100)

        # Should be trimmed, HTML-escaped, and cleaned
        assert result.startswith("&lt;script&gt;")
        assert "\x00" not in result
        assert "\x01" not in result
        assert not result.startswith(" ")
