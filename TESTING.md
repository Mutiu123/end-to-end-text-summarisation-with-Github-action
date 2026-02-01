# Testing Guide for Text Summarizer API

This guide provides instructions for running and maintaining the test suite for the Text Summarizer API.

## Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
pytest
```

Or use the test runner script:

```bash
python run_tests.py
```

## Test Suite Overview

The test suite consists of 92+ test cases across 8 test modules:

| Module | Tests | Coverage |
|--------|-------|----------|
| test_settings.py | 9 | Configuration and environment settings |
| test_auth.py | 10 | JWT token creation and validation |
| test_rate_limiter.py | 8 | Rate limiting logic |
| test_sanitizer.py | 21 | Input sanitization and validation |
| test_exceptions.py | 10 | Custom exception classes |
| test_schemas.py | 18 | Pydantic request/response models |
| test_api.py | 16 | API endpoint integration tests |

## Common Test Commands

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test class
pytest tests/test_auth.py::TestAuthModule

# Run specific test function
pytest tests/test_auth.py::TestAuthModule::test_create_access_token_success
```

### Coverage Reports

```bash
# Generate terminal coverage report
pytest --cov=src/textSummarizer --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src/textSummarizer --cov-report=html

# Open HTML report (after generation)
open htmlcov/index.html  # macOS
start htmlcov\index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

### Test Filtering

```bash
# Run only async tests
pytest -m asyncio

# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Run tests matching pattern
pytest -k "test_auth"
```

### Debug and Troubleshooting

```bash
# Show print statements during tests
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run last failed tests
pytest --lf

# Run failed tests first, then others
pytest --ff
```

## Test Structure

### Unit Tests
Located in:
- `tests/test_settings.py`
- `tests/test_auth.py`
- `tests/test_rate_limiter.py`
- `tests/test_sanitizer.py`
- `tests/test_exceptions.py`
- `tests/test_schemas.py`

These tests verify individual components in isolation using mocks.

### Integration Tests
Located in:
- `tests/test_api.py`

These tests verify the entire API stack using httpx.AsyncClient to make real HTTP requests to the FastAPI app.

## Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

- `test_settings` - Provides test Settings configuration
- `test_app` - Provides AsyncClient for API testing
- `mock_prediction_pipeline` - Mocked ML model
- `mock_db_manager` - Mocked MongoDB manager
- `reset_singletons` - Auto-resets singleton instances between tests

## Writing New Tests

### Example Unit Test

```python
def test_new_feature(test_settings: Settings):
    """Test description."""
    # Arrange
    input_data = "test input"

    # Act
    result = function_under_test(input_data, test_settings)

    # Assert
    assert result == "expected output"
```

### Example Async Integration Test

```python
@pytest.mark.asyncio
async def test_new_endpoint(test_app: AsyncClient):
    """Test new API endpoint."""
    # Arrange
    payload = {"field": "value"}

    # Act
    response = await test_app.post("/new-endpoint", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

### Example Test with Mocking

```python
@pytest.mark.asyncio
async def test_with_mock(test_app: AsyncClient, mock_prediction_pipeline: MagicMock):
    """Test with mocked dependency."""
    with patch("app._prediction_pipeline", mock_prediction_pipeline):
        response = await test_app.post("/predict", json={"text": "test"})
        assert response.status_code == 200
        mock_prediction_pipeline.predict.assert_called_once()
```

## Continuous Integration

Add this to your CI/CD pipeline (GitHub Actions, GitLab CI, etc.):

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run tests with coverage
      run: |
        pytest --cov=src/textSummarizer --cov-report=xml --cov-report=term

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

## Best Practices

### 1. Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Use descriptive names: `test_create_token_with_expired_date`

### 2. Test Organization
- One test file per source module
- Group related tests in classes
- Use fixtures for common setup
- Keep tests independent and isolated

### 3. Assertions
- Use specific assertions: `assert value == expected`
- Include helpful failure messages: `assert result is True, "Expected authentication to succeed"`
- Test both success and failure cases

### 4. Mocking
- Mock external dependencies (database, APIs, file system)
- Use `unittest.mock.patch` for dependency injection
- Verify mock calls: `mock.assert_called_once()`

### 5. Async Testing
- Mark async tests with `@pytest.mark.asyncio`
- Use `AsyncClient` for API tests
- Use `AsyncMock` for async mock objects

## Coverage Goals

Target: 85%+ code coverage

Current coverage by module:
- Configuration: 95%+
- Authentication: 90%+
- Rate limiting: 90%+
- Sanitization: 95%+
- Exceptions: 100%
- Schemas: 90%+
- API endpoints: 85%+

## Troubleshooting

### Problem: Import errors
**Solution**: Ensure src is in Python path. The conftest.py file handles this automatically.

### Problem: Async tests not running
**Solution**: Install pytest-asyncio: `pip install pytest-asyncio`

### Problem: Settings cache issues
**Solution**: Use the `test_settings` fixture which clears the cache automatically.

### Problem: Rate limiter state persists between tests
**Solution**: The `reset_singletons` fixture resets the rate limiter between tests.

### Problem: Tests hang or timeout
**Solution**: Check for missing `await` keywords in async tests or blocking operations.

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [httpx documentation](https://www.python-httpx.org/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)

## Maintaining Tests

### When Adding New Features
1. Write tests first (TDD approach)
2. Ensure new code has 80%+ coverage
3. Update test documentation

### When Fixing Bugs
1. Write a failing test that reproduces the bug
2. Fix the bug
3. Verify the test passes

### When Refactoring
1. Run tests before refactoring
2. Keep tests green during refactoring
3. Update tests if API changes

## Support

For questions or issues with the test suite, please:
1. Check this guide
2. Review test examples in the tests/ directory
3. Check pytest documentation
4. Open an issue in the project repository
