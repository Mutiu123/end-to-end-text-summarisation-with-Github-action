# Test Suite for Text Summarizer API

This directory contains a comprehensive test suite for the Text Summarizer API project, covering unit tests, integration tests, and API endpoint tests.

## Test Structure

The test suite is organized into the following files:

- `conftest.py` - Pytest fixtures and test configuration
- `test_settings.py` - Tests for Settings configuration module (9 tests)
- `test_auth.py` - Tests for JWT authentication module (10 tests)
- `test_rate_limiter.py` - Tests for token bucket rate limiter (8 tests)
- `test_sanitizer.py` - Tests for input sanitization module (21 tests)
- `test_exceptions.py` - Tests for custom exception classes (10 tests)
- `test_schemas.py` - Tests for Pydantic request/response schemas (18 tests)
- `test_api.py` - Integration tests for API endpoints (16 tests)

**Total: 92+ test cases**

## Installation

Install the test dependencies:

```bash
pip install -r requirements-test.txt
```

Or if you have the main requirements installed, just add the test-specific packages:

```bash
pip install pytest pytest-asyncio pytest-cov httpx pytest-mock
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=src/textSummarizer --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run specific test class
```bash
pytest tests/test_auth.py::TestAuthModule
```

### Run specific test
```bash
pytest tests/test_auth.py::TestAuthModule::test_create_access_token_success
```

### Run tests with verbose output
```bash
pytest -v
```

### Run tests with print statements visible
```bash
pytest -s
```

### Run only async tests
```bash
pytest -m asyncio
```

## Test Coverage

### Settings Module (test_settings.py)
- Default configuration values
- Environment variable loading
- Properties: allowed_origins_list, api_keys_list, is_production, is_development
- Environment validation
- Singleton caching behavior

### Authentication Module (test_auth.py)
- JWT token creation with correct payload
- Token expiration time validation
- Token verification success and failure cases
- Expired token handling
- Invalid token rejection
- Wrong secret key detection
- API key validation (valid, invalid, no keys configured)

### Rate Limiter (test_rate_limiter.py)
- Request allowance within limit
- Request blocking when limit exceeded
- Token refill over time
- Bucket reset functionality
- Separate buckets for different clients
- X-Forwarded-For header priority
- Missing client info handling

### Input Sanitizer (test_sanitizer.py)
- Basic text sanitization
- Null byte removal
- Control character removal
- HTML entity escaping
- Text truncation to max length
- Text length validation (too short, too long, valid)
- Suspicious pattern detection:
  - Script tags
  - JavaScript protocol
  - Event handlers
  - Template injection patterns
  - Python code execution patterns
- Safe text false positive prevention

### Exception Classes (test_exceptions.py)
- AppException base class behavior
- All custom exception classes (ModelNotFoundError, ModelInferenceError, etc.)
- Correct HTTP status codes
- Error message and detail formatting
- Exception inheritance hierarchy

### Request/Response Schemas (test_schemas.py)
- PredictRequest validation (text, max_length, num_beams, length_penalty)
- TokenRequest validation (username, password)
- Field constraints (min/max values)
- Default values
- Response schema creation (PredictResponse, StatusResponse, HealthResponse, etc.)

### API Endpoints (test_api.py)
- GET /status - API status information
- GET /health - Health check with database and model status
- POST /auth/token - JWT token generation
- POST /predict - Text summarization with various scenarios:
  - Success case with valid input
  - Model not loaded (503)
  - Input validation errors
  - Suspicious pattern detection
  - Rate limiting enforcement
  - Model inference errors
  - Custom generation parameters
  - Database logging
- GET /train - Training pipeline trigger
- Root redirect to documentation

## Test Fixtures

### test_settings
Provides a Settings instance configured for testing with:
- APP_ENV=testing
- Test SECRET_KEY
- Test MongoDB URL
- Test rate limits
- Test API keys
- Clears lru_cache before and after tests

### test_app
Provides an httpx.AsyncClient configured with the FastAPI app for integration testing.

### mock_prediction_pipeline
Mock PredictionPipeline that returns a predefined summary.

### mock_db_manager
Mock MongoDBManager with health check and prediction logging methods.

### reset_singletons
Auto-use fixture that resets singleton instances between tests.

## Key Testing Patterns

### Async Tests
Tests for async endpoints use `pytest.mark.asyncio` and `httpx.AsyncClient`:

```python
@pytest.mark.asyncio
async def test_get_status_success(self, test_app: AsyncClient):
    response = await test_app.get("/status")
    assert response.status_code == 200
```

### Mocking
The test suite uses unittest.mock for patching dependencies:

```python
with patch("app._prediction_pipeline", mock_prediction_pipeline):
    response = await test_app.post("/predict", json=payload)
```

### Environment Variables
Tests modify environment variables temporarily using fixtures that restore original values after tests.

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=src/textSummarizer --cov-report=xml
```

## Coverage Goals

Target coverage: 85%+

Current coverage areas:
- Configuration and settings
- Authentication and authorization
- Rate limiting
- Input validation and sanitization
- Exception handling
- API endpoints
- Schema validation

## Contributing

When adding new features, please:

1. Add corresponding tests in the appropriate test file
2. Maintain or improve overall test coverage
3. Follow existing test naming conventions
4. Use fixtures for common test setup
5. Mock external dependencies (database, ML models)

## Troubleshooting

### Import Errors
If you encounter import errors, ensure the src directory is in the Python path:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
```

### Async Test Issues
Ensure pytest-asyncio is installed and `asyncio_mode = auto` is set in pytest.ini.

### Cache Issues
If settings changes aren't reflected, the lru_cache may need clearing:
```python
get_settings.cache_clear()
```
