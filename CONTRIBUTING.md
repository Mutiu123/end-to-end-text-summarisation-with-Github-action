# Contributing to Text Summarizer API

Thank you for your interest in contributing to the Text Summarizer API project! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting Up the Development Environment](#setting-up-the-development-environment)
- [Code Style Guidelines](#code-style-guidelines)
- [Running Tests](#running-tests)
- [Branch Naming Convention](#branch-naming-convention)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Code Review Checklist](#code-review-checklist)

## Prerequisites

Before you begin contributing, ensure you have the following installed on your system:

### Required Software

- **Python 3.10 or higher**: The project requires Python 3.10+ for compatibility with all dependencies
  ```bash
  python --version  # Should show 3.10.x or higher
  ```

- **Docker**: Required for containerized development and testing
  ```bash
  docker --version
  docker-compose --version
  ```

- **Git**: For version control
  ```bash
  git --version
  ```

- **pre-commit**: For running automated checks before commits
  ```bash
  pip install pre-commit
  ```

### Recommended Tools

- **VS Code** or **PyCharm** with Python extensions
- **Postman** or **Insomnia** for API testing
- **MongoDB Compass** for database inspection (optional)

## Setting Up the Development Environment

Follow these steps to set up your local development environment:

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub first, then clone your fork
git clone https://github.com/YOUR_USERNAME/end-to-end-text-summarisation-with-Github-action.git
cd end-to-end-text-summarisation-with-Github-action
```

### 2. Add Upstream Remote

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/end-to-end-text-summarisation-with-Github-action.git
git fetch upstream
```

### 3. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements_dev.txt

# Alternatively, install all at once
pip install -r requirements.txt -r requirements_dev.txt
```

### 5. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# Set the following variables:
# - MONGODB_URL (your local MongoDB connection string)
# - AWS_ACCESS_KEY_ID (for model access)
# - AWS_SECRET_ACCESS_KEY (for model access)
# - AWS_DEFAULT_REGION (default: us-east-1)
```

### 6. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Test the installation (optional)
pre-commit run --all-files
```

### 7. Verify Setup

```bash
# Run tests to verify everything works
pytest

# Start the application locally
python app.py
```

The API should now be running at `http://localhost:8080`.

## Code Style Guidelines

We follow strict code style guidelines to maintain code quality and consistency across the project.

### Python Code Formatting

#### Black

We use **Black** as our primary code formatter with a line length of 100 characters.

```bash
# Format all Python files
black --line-length 100 .

# Check formatting without making changes
black --line-length 100 --check .
```

**Configuration**: Black settings are defined in `pyproject.toml`:
```toml
[tool.black]
line-length = 100
target-version = ['py310']
```

#### isort

We use **isort** to automatically sort and organize imports.

```bash
# Sort imports
isort .

# Check imports without making changes
isort --check-only .
```

**Configuration**: isort is configured to work with Black:
```toml
[tool.isort]
profile = "black"
line_length = 100
```

#### flake8

We use **flake8** for linting and style checking.

```bash
# Run flake8 checks
flake8 .
```

**Configuration**: flake8 settings in `.flake8` or `setup.cfg`:
```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,build,dist
```

#### mypy

We use **mypy** for static type checking.

```bash
# Run type checks
mypy .
```

**Type Hints**: All functions should include type hints:
```python
def summarize_text(text: str, max_length: int = 150) -> str:
    """Summarize the given text."""
    pass
```

### Code Style Best Practices

- Write clear, self-documenting code with meaningful variable names
- Add docstrings to all functions, classes, and modules
- Keep functions small and focused (single responsibility principle)
- Use type hints for all function parameters and return values
- Avoid complex nested logic; refactor into smaller functions
- Follow PEP 8 conventions for naming:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

## Running Tests

We use **pytest** for testing with a coverage target of 80% or higher.

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term
```

### Running Specific Tests

```bash
# Run tests in a specific file
pytest tests/test_api.py

# Run a specific test function
pytest tests/test_api.py::test_health_endpoint

# Run tests matching a pattern
pytest -k "test_summarization"
```

### Coverage Requirements

- **Minimum coverage**: 80% overall
- **Critical modules**: 90%+ coverage required for core functionality
- View coverage reports in `htmlcov/index.html` after running with `--cov-report=html`

### Writing Tests

- Place all tests in the `tests/` directory
- Name test files with the `test_` prefix
- Name test functions with the `test_` prefix
- Use fixtures for common setup/teardown
- Mock external dependencies (API calls, database connections)

Example test structure:
```python
import pytest
from src.api import app

def test_health_endpoint():
    """Test the health check endpoint."""
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

## Branch Naming Convention

Use descriptive branch names that follow this pattern:

### Format

```
<type>/<short-description>
```

### Types

- **feature/**: New features or enhancements
  - Example: `feature/add-batch-summarization`
  - Example: `feature/implement-caching`

- **bugfix/**: Bug fixes
  - Example: `bugfix/fix-memory-leak`
  - Example: `bugfix/correct-token-count`

- **hotfix/**: Urgent fixes for production
  - Example: `hotfix/security-patch`
  - Example: `hotfix/api-timeout`

- **docs/**: Documentation updates
  - Example: `docs/update-api-reference`

- **refactor/**: Code refactoring
  - Example: `refactor/improve-error-handling`

- **test/**: Adding or updating tests
  - Example: `test/add-integration-tests`

### Best Practices

- Use lowercase letters
- Use hyphens to separate words
- Keep branch names short but descriptive
- Delete branches after merging

## Commit Message Format

We follow the **Conventional Commits** specification for all commit messages.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring without changing functionality
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates
- **ci**: CI/CD pipeline changes

### Examples

```
feat(api): add batch summarization endpoint

Implement new /summarize/batch endpoint that accepts multiple
texts and returns summarized versions in a single request.

Closes #123
```

```
fix(database): resolve connection pool exhaustion

Fixed issue where database connections were not being properly
released, causing pool exhaustion under high load.

Fixes #456
```

```
docs(readme): update installation instructions

Added detailed steps for Windows users and troubleshooting section.
```

### Rules

- Use imperative mood ("add" not "added" or "adds")
- Keep the subject line under 50 characters
- Capitalize the subject line
- Do not end the subject line with a period
- Separate subject from body with a blank line
- Wrap the body at 72 characters
- Use the body to explain what and why, not how

## Pull Request Process

Follow these steps when submitting a pull request:

### 1. Before Creating a PR

- Ensure your branch is up to date with the main branch:
  ```bash
  git fetch upstream
  git rebase upstream/main
  ```

- Run all tests and ensure they pass:
  ```bash
  pytest --cov=src --cov-report=term
  ```

- Run code quality checks:
  ```bash
  black --line-length 100 --check .
  isort --check-only .
  flake8 .
  mypy .
  ```

### 2. Create the Pull Request

- Push your branch to your fork
- Go to the GitHub repository and create a new pull request
- Use a clear, descriptive title following the commit message format
- Fill out the PR template completely

### 3. PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe the tests you ran and how to reproduce

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Coverage meets requirements
```

### 4. After Submission

- Respond to review comments promptly
- Make requested changes in new commits (don't force push)
- Request re-review after making changes
- Ensure CI/CD checks pass

## Code Review Checklist

Use this checklist when reviewing pull requests:

### Functionality

- [ ] Code accomplishes the intended purpose
- [ ] No obvious bugs or logic errors
- [ ] Edge cases are handled appropriately
- [ ] Error handling is comprehensive

### Code Quality

- [ ] Code is readable and well-organized
- [ ] Functions are small and focused
- [ ] No code duplication
- [ ] Variable and function names are clear
- [ ] Complex logic is commented

### Style and Standards

- [ ] Code follows Black formatting (line-length 100)
- [ ] Imports are sorted with isort
- [ ] No flake8 violations
- [ ] Type hints are present and correct
- [ ] Docstrings are complete and accurate

### Testing

- [ ] New code is covered by tests
- [ ] All tests pass
- [ ] Coverage meets 80%+ requirement
- [ ] Tests are meaningful and test behavior, not implementation

### Documentation

- [ ] README updated if needed
- [ ] API documentation updated
- [ ] Inline comments explain complex logic
- [ ] CHANGELOG updated

### Security

- [ ] No hardcoded secrets or credentials
- [ ] Input validation is present
- [ ] No SQL injection vulnerabilities
- [ ] Dependencies are secure and up-to-date

### Performance

- [ ] No obvious performance issues
- [ ] Database queries are optimized
- [ ] No memory leaks

---

## Getting Help

If you have questions or need help:

- Open an issue on GitHub
- Check existing issues and pull requests
- Review the project documentation
- Contact the maintainers

Thank you for contributing to the Text Summarizer API project!
