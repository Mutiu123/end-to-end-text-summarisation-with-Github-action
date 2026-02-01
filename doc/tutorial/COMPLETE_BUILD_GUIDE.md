# Complete Build Guide — From Zero to Production

> A detailed journal of how to build this entire project from scratch. I wrote this as if I am walking you through every decision, every file, and every command — in the order I would build it if starting from an empty directory.

---

## Table of Contents

1. [Phase 1: Project Scaffolding](#phase-1-project-scaffolding)
2. [Phase 2: ML Research & Experimentation](#phase-2-ml-research--experimentation)
3. [Phase 3: ML Training Pipeline](#phase-3-ml-training-pipeline)
4. [Phase 4: FastAPI Application](#phase-4-fastapi-application)
5. [Phase 5: Security Layer](#phase-5-security-layer)
6. [Phase 6: Database Integration](#phase-6-database-integration)
7. [Phase 7: Monitoring & Observability](#phase-7-monitoring--observability)
8. [Phase 8: Testing](#phase-8-testing)
9. [Phase 9: Containerisation](#phase-9-containerisation)
10. [Phase 10: Kubernetes Deployment](#phase-10-kubernetes-deployment)
11. [Phase 11: CI/CD Pipeline](#phase-11-cicd-pipeline)
12. [Phase 12: Production Hardening](#phase-12-production-hardening)

---

## Phase 1: Project Scaffolding

### Step 1: Create the project directory and initialise Git

```bash
mkdir end-to-end-text-summarisation-with-Github-action
cd end-to-end-text-summarisation-with-Github-action
git init
```

### Step 2: Create the project template

I wrote a `template.py` script that generates the entire directory structure automatically. This is a common pattern in ML projects — you define your folder layout once and generate it programmatically so you never forget a directory or an `__init__.py` file.

The template creates:

```
src/textSummarizer/
├── __init__.py
├── config/
├── conponents/         # ML pipeline components
├── pipeline/           # Pipeline orchestration
├── logging/
├── utils/
├── database/
├── security/
├── monitoring/
├── schemas/
└── exceptions.py
config/
research/
```

Run it with:

```bash
python template.py
```

### Step 3: Set up the Python package

Create `setup.py`:

```python
import setuptools

setuptools.setup(
    name="textSummarizer",
    version="0.0.1",
    author="Your Name",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
)
```

And `pyproject.toml` for modern Python tooling configuration (Black line length, isort profile, mypy settings, pytest paths).

### Step 4: Create requirements files

I split dependencies into two files:

- **`requirements.txt`** — Production dependencies (FastAPI, transformers, torch, motor, etc.)
- **`requirements-test.txt`** — Test-only dependencies (pytest, httpx, coverage)

This separation matters because the production Docker image should not include pytest.

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -e .   # Install the package in editable mode
```

### Step 5: Set up code quality tools

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
```

Install and activate:

```bash
pip install pre-commit
pre-commit install
```

From this point on, every commit is automatically checked for formatting, import order, and PEP 8 compliance.

### Step 6: Create `.env.example`

I list every environment variable the application needs with sensible defaults. This serves as living documentation — new developers copy it to `.env` and fill in their values.

```bash
cp .env.example .env
# Edit .env with your values
```

### Step 7: Create `.gitignore`

Include: `__pycache__`, `*.pyc`, `.env`, `artifacts/`, `model/`, `*.egg-info`, `.mypy_cache`, `htmlcov/`, `.coverage`, `venv/`.

---

## Phase 2: ML Research & Experimentation

### Step 8: Research in Jupyter notebooks

Before writing any production code, I experiment in notebooks under `research/`. This is where I figure out what works before committing to an architecture.

**Notebook 01 — Data Ingestion (`01_data_ingestion.ipynb`):**

I download the SAMSum dataset (a dialogue summarisation dataset) and explore its structure. The dataset has three splits: train, test, and validation. Each record has a `dialogue` field and a `summary` field.

```python
from datasets import load_dataset
dataset = load_dataset("samsum")
print(dataset)
# DatasetDict({
#     train: Dataset({features: ['id', 'dialogue', 'summary'], num_rows: 14732}),
#     test: Dataset({features: ['id', 'dialogue', 'summary'], num_rows: 819}),
#     validation: Dataset({features: ['id', 'dialogue', 'summary'], num_rows: 818})
# })
```

**Notebook 02 — Data Validation (`02_data_validation.ipynb`):**

I check that all required files exist, there are no null values, and the text lengths are within expected ranges.

**Notebook 03 — Data Transformation (`03_data_transformation.ipynb`):**

I tokenise the dialogues and summaries using the PEGASUS tokenizer. This converts text into token IDs that the model can process.

```python
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("google/pegasus-cnn_dailymail")
```

**Notebook 04 — Model Training (`04_model_trainer.ipynb`):**

I fine-tune PEGASUS on the SAMSum dataset. Key hyperparameters I experimented with:

- `num_train_epochs`: 1 (for demonstration; production would use 3-5)
- `per_device_train_batch_size`: 1 (limited by GPU memory)
- `weight_decay`: 0.01
- `learning_rate`: 2e-5
- `evaluation_strategy`: "steps"

**Notebook 05 — Model Evaluation (`05_Model_evaluation.ipynb`):**

I generate summaries on the test set and compute ROUGE and BLEU scores to measure quality.

### Step 9: Document findings

After the notebooks, I know:
- PEGASUS works well for dialogue summarisation
- The SAMSum dataset is clean and well-structured
- Fine-tuning takes 2-4GB of GPU memory
- Inference takes 50-500ms depending on input length

Now I can convert this research into production code.

---

## Phase 3: ML Training Pipeline

### Step 10: Define the configuration schema

Create `config/config.yaml`:

```yaml
artifacts_root: artifacts/

data_ingestion:
  root_dir: artifacts/data_ingestion
  source_URL: https://github.com/...dataset.zip
  local_data_file: artifacts/data_ingestion/data.zip
  unzip_dir: artifacts/data_ingestion

data_validation:
  root_dir: artifacts/data_validation
  STATUS_FILE: artifacts/data_validation/status.txt
  ALL_REQUIRED_FILES:
    - train
    - test
    - validation

data_transformation:
  root_dir: artifacts/data_transformation

model_trainer:
  root_dir: artifacts/model_trainer
  model_ckpt: google/pegasus-cnn_dailymail

model_evaluation:
  root_dir: artifacts/model_evaluation
  model_path: artifacts/model_trainer/pegasus-samsum-model
  tokenizer_path: artifacts/model_trainer/tokenizer
```

And `params.yaml` for hyperparameters:

```yaml
TrainingArguments:
  num_train_epochs: 1
  warmup_steps: 500
  per_device_train_batch_size: 1
  weight_decay: 0.01
  logging_steps: 10
  evaluation_strategy: steps
  eval_steps: 500
  save_steps: 1e6
  gradient_accumulation_steps: 16
```

### Step 11: Build the configuration manager

Create `src/textSummarizer/config/configuration.py`. This reads `config.yaml` and `params.yaml` and returns typed configuration objects for each pipeline stage. I use `@dataclass` for the config entities and a `ConfigurationManager` class to create them.

### Step 12: Build each pipeline component

For each of the five stages, I create two files:

1. **Component** (`src/textSummarizer/conponents/`) — The actual logic (download, validate, tokenise, train, evaluate)
2. **Pipeline stage** (`src/textSummarizer/pipeline/`) — Orchestration that creates the config and calls the component

Example for data ingestion:

```python
# conponents/data_ingestion.py
class DataIngestion:
    def __init__(self, config):
        self.config = config

    def download_file(self):
        urllib.request.urlretrieve(
            self.config.source_URL,
            self.config.local_data_file
        )

    def extract_zip_file(self):
        with zipfile.ZipFile(self.config.local_data_file) as zip_ref:
            zip_ref.extractall(self.config.unzip_dir)
```

```python
# pipeline/stage_01_data_ingestion.py
class DataIngestionTrainingPipeline:
    def main(self):
        config = ConfigurationManager()
        data_ingestion_config = config.get_data_ingestion_config()
        data_ingestion = DataIngestion(config=data_ingestion_config)
        data_ingestion.download_file()
        data_ingestion.extract_zip_file()
```

### Step 13: Create the main training entry point

`main.py` runs all five stages in sequence:

```python
from textSummarizer.pipeline.stage_01_data_ingestion import DataIngestionTrainingPipeline
# ... import other stages

if __name__ == "__main__":
    stage1 = DataIngestionTrainingPipeline()
    stage1.main()

    stage2 = DataValidationTrainingPipeline()
    stage2.main()

    # ... stages 3, 4, 5
```

### Step 14: Run the training pipeline

```bash
python main.py
```

This downloads the dataset, validates it, tokenises it, fine-tunes PEGASUS, and evaluates the result. The trained model is saved to `artifacts/model_trainer/`.

---

## Phase 4: FastAPI Application

### Step 15: Create the prediction pipeline

`src/textSummarizer/pipeline/prediction.py`:

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

class PredictionPipeline:
    def __init__(self, model_path, tokenizer_path):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        self.pipe = pipeline("summarization", model=self.model, tokenizer=self.tokenizer)

    def predict(self, text):
        result = self.pipe(text, max_length=128, num_beams=8, length_penalty=0.8)
        return result[0]["summary_text"]
```

### Step 16: Create Pydantic schemas

I define request and response models with strict validation:

**`src/textSummarizer/schemas/requests.py`:**

```python
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=10000)
    max_length: int | None = Field(None, ge=10, le=512)
    num_beams: int | None = Field(None, ge=1, le=16)
    length_penalty: float | None = Field(None, ge=0.1, le=2.0)
```

I use Pydantic v2 because it integrates natively with FastAPI and gives automatic 422 error responses with field-level detail.

**`src/textSummarizer/schemas/responses.py`:**

```python
class PredictResponse(BaseModel):
    summary: str
    input_length: int
    output_length: int
    processing_time_ms: float
    request_id: str
    model: str
```

### Step 17: Create the application settings

`src/textSummarizer/config/settings.py`:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Text Summarizer API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    # ... 46 more variables

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

I use `@lru_cache()` to create a singleton — the settings are parsed once and reused for every request.

### Step 18: Build the FastAPI app

`app.py`:

```python
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load model, connect to DB
    settings = get_settings()
    model = _load_model(settings)
    app.state.model = model
    await mongodb_manager.connect()
    yield
    # Shutdown: close DB connection
    await mongodb_manager.close()

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )
    # Add routes, middleware, exception handlers
    return app

app = create_app()
```

I use the lifespan context manager (introduced in FastAPI 0.95) instead of the deprecated `@app.on_event("startup")` pattern. This guarantees that startup and shutdown logic are paired — if model loading succeeds, the DB connection closure is guaranteed on shutdown.

### Step 19: Define the API routes

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "api": True, "database": db_ok, "model": model_ok}

@app.post("/auth/token")
async def create_token(request: TokenRequest):
    token = create_access_token({"sub": request.username})
    return {"access_token": token, "token_type": "bearer", "expires_in": 1800}

@app.post("/predict")
async def predict(
    request: PredictRequest,
    user: str = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    # Sanitize → Infer → Log → Return
    ...
```

### Step 20: Test the API locally

```bash
uvicorn app:app --reload --port 8080
```

Visit `http://localhost:8080/docs` for the interactive Swagger UI.

---

## Phase 5: Security Layer

### Step 21: Implement JWT authentication

`src/textSummarizer/security/auth.py`:

I implement three functions:
- `create_access_token(data, settings)` — Encodes a JWT with an expiry claim
- `verify_token(token, settings)` — Decodes and validates the JWT
- `get_current_user(credentials)` — A FastAPI dependency that extracts the user from the Authorization header

I chose HS256 because there is only one service. The secret key comes from the `SECRET_KEY` environment variable — never hardcoded.

### Step 22: Implement rate limiting

`src/textSummarizer/security/rate_limiter.py`:

The token bucket algorithm works like this:
1. Each client IP gets a bucket with 100 tokens
2. Each request consumes one token
3. Tokens refill at a rate of 100 per 60 seconds
4. If the bucket is empty, return HTTP 429

```python
class TokenBucketRateLimiter:
    def __init__(self, max_tokens=100, window_seconds=60):
        self.max_tokens = max_tokens
        self.refill_rate = max_tokens / window_seconds
        self.buckets = {}  # IP -> (tokens, last_check_time)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        tokens, last_check = self.buckets.get(client_ip, (self.max_tokens, now))
        elapsed = now - last_check
        tokens = min(self.max_tokens, tokens + elapsed * self.refill_rate)
        if tokens >= 1:
            self.buckets[client_ip] = (tokens - 1, now)
            return True
        return False
```

### Step 23: Implement input sanitisation

`src/textSummarizer/security/sanitizer.py`:

I check for common attack patterns:
- **SQL injection**: `UNION SELECT`, `DROP TABLE`, `OR 1=1`
- **XSS**: `<script>`, `javascript:`, `onerror=`
- **Path traversal**: `../`, `..\\`
- **Command injection**: `;`, `|`, `&&`, `` ` ``, `$()`

If any pattern matches, the request is rejected with a 400 error. I chose pattern matching over escaping because the input is natural language text — there is no legitimate reason for SQL keywords or script tags to appear in a summarisation request.

---

## Phase 6: Database Integration

### Step 24: Set up MongoDB with Motor

`src/textSummarizer/database/mongodb.py`:

I chose Motor (async MongoDB driver) because the FastAPI app is async — using a synchronous driver would block the event loop during database writes.

```python
class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
        )
        self.db = self.client[settings.MONGODB_DB_NAME]

    async def log_prediction(self, record: dict):
        await self.db.predictions.insert_one(record)

    async def close(self):
        if self.client:
            self.client.close()
```

I use connection pooling (10-50 connections) because creating a new connection per request is expensive. The pool size is configurable via environment variables.

Prediction logging is fire-and-forget — I do not await the database write in the request path. This means a database failure will not cause the API to return an error to the user. The audit log is important but not critical enough to block the response.

---

## Phase 7: Monitoring & Observability

### Step 25: Define Prometheus metrics

`src/textSummarizer/monitoring/metrics.py`:

I create a singleton `AppMetrics` class with 10+ metrics. Each metric type serves a purpose:

- **Counters** for things that only go up (total requests, total errors)
- **Histograms** for distributions (latency, input length) — these give you percentiles
- **Gauges** for current values (active requests, model loaded status)
- **Summaries** for database operation latency (built-in quantile calculation)

### Step 26: Build the request tracking middleware

`src/textSummarizer/monitoring/middleware.py`:

This middleware wraps every request and:
1. Generates a unique request ID
2. Records the start time
3. Increments the active requests gauge
4. After the response, records latency and status code to Prometheus
5. Decrements the active requests gauge

### Step 27: Set up structured logging

`src/textSummarizer/monitoring/structured_logging.py`:

I output logs as JSON because:
- Machine-parseable (grep, jq, log aggregators can process them)
- Structured fields enable filtering (show me all logs for request_id X)
- Correlation IDs link related log entries across the request lifecycle

### Step 28: Configure Prometheus scraping

`monitoring/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "text-summarizer"
    scrape_interval: 15s
    static_configs:
      - targets: ["app:8080"]
    metrics_path: "/metrics"
```

### Step 29: Create the Grafana dashboard

`monitoring/grafana/dashboards/text-summarizer.json`:

I pre-built a dashboard with panels for:
- Request rate (requests per second)
- Latency percentiles (P50, P95, P99)
- Error rate by status code
- Model inference duration
- Active requests gauge
- Database operation latency

This JSON file is auto-provisioned when Grafana starts — no manual setup needed.

---

## Phase 8: Testing

### Step 30: Set up the test infrastructure

`tests/conftest.py`:

```python
import pytest
from httpx import AsyncClient
from app import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

I use `httpx.AsyncClient` instead of FastAPI's `TestClient` because the app is async. `TestClient` wraps everything in a sync adapter, which can mask async bugs.

### Step 31: Write unit tests for each layer

**`test_settings.py`** — Verify that:
- Default values are correct
- Environment variable overrides work
- Validators reject invalid values
- Computed properties return expected results

**`test_schemas.py`** — Verify that:
- Valid requests pass validation
- Text too short/long is rejected
- Optional fields have correct defaults
- Type coercion works as expected

**`test_auth.py`** — Verify that:
- Token creation returns a valid JWT
- Token verification extracts the correct claims
- Expired tokens are rejected
- Tampered tokens are rejected
- Missing tokens return 401

**`test_rate_limiter.py`** — Verify that:
- Normal requests are allowed
- Requests beyond the limit are blocked
- Tokens refill after the window passes
- Different IPs have separate buckets

**`test_sanitizer.py`** — Verify that:
- Clean text passes through unchanged
- SQL injection patterns are detected
- XSS patterns are detected
- Path traversal is caught
- Command injection is caught

**`test_api.py`** — Integration tests that:
- Health check returns correct structure
- Status endpoint shows version and environment
- Predict endpoint requires authentication
- Full auth + predict flow works end to end

### Step 32: Run tests and check coverage

```bash
pytest --cov=src/ --cov-report=html --cov-report=term -v
```

The coverage threshold is 80%. If coverage drops below this, CI fails.

---

## Phase 9: Containerisation

### Step 33: Write the production Dockerfile

```dockerfile
# Stage 1: Build dependencies
FROM python:3.10-slim-bookworm AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.10-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home appuser
COPY --from=builder /install /usr/local
WORKDIR /app
COPY --chown=appuser:appuser . .
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
USER appuser
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

Key decisions:
- **Multi-stage** — Builder installs packages; production image only copies the installed packages. No pip, no compilers in production.
- **Non-root user** — If the container is compromised, the attacker does not have root access.
- **Health check** — Docker and Kubernetes can detect when the container is unhealthy and restart it.
- **2 workers** — Uvicorn runs 2 processes for concurrency. More workers need more memory for the model.

### Step 34: Write the development Dockerfile

```dockerfile
FROM python:3.10-slim-bookworm
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]
```

Simple, with `--reload` for live code changes during development.

### Step 35: Write docker-compose.yml

```yaml
services:
  app:
    build: .
    ports: ["8080:8080"]
    depends_on:
      mongodb:
        condition: service_healthy
    environment:
      - MONGODB_URL=mongodb://mongodb:27017

  mongodb:
    image: mongo:7
    ports: ["27017:27017"]
    volumes: ["mongodb-data:/data/db"]
    healthcheck:
      test: mongosh --eval "db.adminCommand('ping')"

  prometheus:
    image: prom/prometheus
    ports: ["9090:9090"]
    volumes: ["./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml"]

  grafana:
    image: grafana/grafana
    ports: ["3000:3000"]
    volumes:
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
```

### Step 36: Test the full stack locally

```bash
docker compose up -d
curl http://localhost:8080/health
# Open http://localhost:3000 for Grafana
```

---

## Phase 10: Kubernetes Deployment

### Step 37: Create the namespace and RBAC

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: text-summarizer

# serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: text-summarizer
  namespace: text-summarizer
```

### Step 38: Create ConfigMap and Secrets

```yaml
# configmap.yaml - non-sensitive config
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  ENABLE_METRICS: "true"

# secret.yaml - sensitive values (base64 encoded)
data:
  SECRET_KEY: <base64>
  MONGODB_URL: <base64>
```

### Step 39: Create the Deployment

3 replicas with rolling update strategy, liveness and readiness probes, resource limits, and environment from ConfigMap + Secret.

### Step 40: Create Service, Ingress, and HPA

- **Service**: ClusterIP on port 80, targeting port 8080
- **Ingress**: TLS termination, hostname routing
- **HPA**: Scale 2-10 replicas based on 70% CPU utilisation

### Step 41: Create NetworkPolicy and PodDisruptionBudget

- **NetworkPolicy**: Only allow traffic from Ingress controller and Prometheus
- **PDB**: Minimum 2 pods always available during voluntary disruptions

### Step 42: Set up Kustomize

`kustomization.yaml` ties all resources together and supports overlays for staging and production.

### Step 43: Deploy

```bash
kubectl apply -k k8s/
kubectl get pods -n text-summarizer
kubectl logs -f deployment/text-summarizer -n text-summarizer
```

---

## Phase 11: CI/CD Pipeline

### Step 44: Create the GitHub Actions workflow

`.github/workflows/main.yaml`:

I define four jobs that run sequentially:

1. **lint** — Black, isort, flake8, mypy
2. **test** (needs: lint) — pytest with coverage
3. **build-and-push** (needs: test, only on main) — Docker build, tag, push to ECR
4. **deploy** (needs: build-and-push, self-hosted runner) — Pull image, run container, verify health

### Step 45: Configure GitHub repository secrets

Go to Settings → Secrets and variables → Actions:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_ECR_LOGIN_URI`
- `ECR_REPOSITORY_NAME`
- `SECRET_KEY`
- `MONGODB_URL`

### Step 46: Create a test-only workflow

`.github/workflows/tests.yml` runs on every pull request and only executes the lint and test stages. This gives fast feedback without building Docker images for every PR.

### Step 47: Test the pipeline

```bash
git add .
git commit -m "feat: complete project setup"
git push origin main
```

Watch the Actions tab in GitHub to see the pipeline run.

---

## Phase 12: Production Hardening

### Step 48: Create comprehensive documentation

- **`README.md`** — Project overview, quick start, API usage, deployment instructions
- **`CONTRIBUTING.md`** — How to contribute, code standards, PR process
- **`DEPLOYMENT.md`** — Step-by-step deployment guide for each environment
- **`TESTING.md`** — How to run tests, add tests, interpret coverage reports
- **`PRODUCTION_READY.md`** — Checklist of production requirements and their status

### Step 49: Security review checklist

Go through each security layer and verify:
- [ ] Secret key is randomly generated (not a default value)
- [ ] JWT expiry is set (not infinite)
- [ ] Rate limiting is enabled
- [ ] CORS origins are restricted (not `*` in production)
- [ ] Input sanitisation catches OWASP Top 10 patterns
- [ ] Container runs as non-root
- [ ] Network policies restrict pod-to-pod communication
- [ ] Secrets are not hardcoded anywhere in the codebase

### Step 50: Performance baseline

Run a load test to establish baseline performance:

```bash
# Install a load testing tool
pip install locust

# Or use Apache Bench
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" \
   -p payload.json -T "application/json" \
   http://localhost:8080/predict
```

Document the results: requests per second, P50/P95/P99 latency, error rate.

### Step 51: Set up Grafana alerts (optional)

In Grafana, create alert rules for:
- Error rate > 5% for 5 minutes
- P95 latency > 2 seconds for 5 minutes
- Model loaded gauge drops to 0
- Database operation errors > 0

### Step 52: Final verification

```bash
# Run all tests
pytest --cov=src/ -v

# Run linting
black --check src/ app.py
flake8 src/ app.py
mypy src/

# Build and run Docker
docker compose up -d
curl http://localhost:8080/health

# Verify monitoring
# Open http://localhost:3000 (Grafana)
# Open http://localhost:9090 (Prometheus)

# Test the full flow
TOKEN=$(curl -s -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r .access_token)

curl -X POST http://localhost:8080/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Alice: Hey Bob, can we meet tomorrow at 3pm? Bob: Sure, works for me. Alice: Great, see you at the office."}'
```

---

## Summary of Build Order

| Phase | What You Build | Key Files Created |
|-------|---------------|-------------------|
| 1 | Project scaffolding | `template.py`, `setup.py`, `requirements.txt`, `.pre-commit-config.yaml` |
| 2 | ML research | `research/*.ipynb` |
| 3 | ML training pipeline | `config/config.yaml`, `params.yaml`, `main.py`, `src/.../conponents/`, `src/.../pipeline/` |
| 4 | FastAPI application | `app.py`, `src/.../schemas/`, `src/.../config/settings.py`, `src/.../pipeline/prediction.py` |
| 5 | Security layer | `src/.../security/auth.py`, `rate_limiter.py`, `sanitizer.py` |
| 6 | Database integration | `src/.../database/mongodb.py` |
| 7 | Monitoring | `src/.../monitoring/`, `monitoring/prometheus.yml`, `monitoring/grafana/` |
| 8 | Testing | `tests/conftest.py`, `tests/test_*.py` |
| 9 | Containerisation | `Dockerfile`, `Dockerfile.dev`, `docker-compose.yml` |
| 10 | Kubernetes | `k8s/*.yaml` |
| 11 | CI/CD | `.github/workflows/main.yaml`, `.github/workflows/tests.yml` |
| 12 | Production hardening | Documentation, security review, performance baseline |

Each phase builds on the previous one. You can stop at any phase and have a working system — Phase 4 gives you a working API, Phase 9 gives you a containerised app, Phase 11 gives you automated deployment. The later phases add production readiness, not functionality.
