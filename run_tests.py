"""
Test runner script for the Text Summarizer API test suite.
"""

import subprocess
import sys


def main():
    """Run pytest with common configurations."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=src/textSummarizer",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]

    print("Running Text Summarizer API Test Suite...")
    print("=" * 70)

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("All tests passed successfully!")
        print("Coverage report generated in htmlcov/index.html")
    else:
        print("\n" + "=" * 70)
        print("Some tests failed. Please check the output above.")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
