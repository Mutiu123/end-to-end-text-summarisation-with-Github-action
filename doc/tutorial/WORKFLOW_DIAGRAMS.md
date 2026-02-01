# Workflow Diagrams — End-to-End Text Summarisation API

> Every operational workflow in this project, visualised step by step.

---

## 1. CI/CD Pipeline (GitHub Actions)

This is the automated pipeline that runs on every push to `main` or `develop`. I split it into four stages because each serves a distinct quality gate — if linting fails, there is no point running tests, and if tests fail, there is no point building a Docker image.

```
  ┌──────────────────────────────────────────────────────┐
  │              TRIGGER                                  │
  │  push: main, develop  │  pull_request: main  │ manual│
  └────────────────────────┬─────────────────────────────┘
                           │
                           ▼
  ┌─────────────────────────────────────────┐
  │           STAGE 1: LINT                  │
  │                                         │
  │   black --check        (formatting)     │
  │   isort --check-only   (import order)   │
  │   flake8 src/ app.py   (PEP 8)         │
  │   mypy src/            (type safety)    │
  │                                         │
  │   ✗ Fail → Pipeline stops               │
  │   ✓ Pass → Continue                     │
  └──────────────────┬──────────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────────┐
  │           STAGE 2: TEST                  │
  │                                         │
  │   pip install -r requirements.txt       │
  │   pip install -r requirements-test.txt  │
  │   pytest --cov=src/ --cov-report=xml    │
  │                                         │
  │   Coverage threshold: 80%               │
  │   Upload: coverage.xml artifact         │
  │                                         │
  │   ✗ Fail → Pipeline stops               │
  │   ✓ Pass → Continue                     │
  └──────────────────┬──────────────────────┘
                     │
                     ▼ (only on main branch)
  ┌─────────────────────────────────────────┐
  │      STAGE 3: BUILD & PUSH TO ECR       │
  │                                         │
  │   Configure AWS credentials             │
  │   Login to Amazon ECR                   │
  │   docker build -t app .                 │
  │   Tag: $ECR_REGISTRY/$REPO:$GIT_SHA    │
  │   Tag: $ECR_REGISTRY/$REPO:latest      │
  │   docker push (both tags)              │
  │                                         │
  │   ✗ Fail → Pipeline stops               │
  │   ✓ Pass → Continue                     │
  └──────────────────┬──────────────────────┘
                     │
                     ▼ (self-hosted runner)
  ┌─────────────────────────────────────────┐
  │        STAGE 4: DEPLOY                   │
  │                                         │
  │   Pull latest image from ECR            │
  │   Stop existing container               │
  │   Run new container with env secrets    │
  │   Wait 30 seconds                       │
  │   Verify /health returns 200            │
  │   Clean up old Docker images            │
  │                                         │
  │   ✗ Fail → Alert / rollback needed      │
  │   ✓ Pass → Deployment complete          │
  └─────────────────────────────────────────┘
```

---

## 2. Docker Build Workflow (Multi-Stage)

I use a multi-stage build to keep the production image small and secure. The builder stage installs all dependencies into a clean directory, and the production stage copies only what is needed — no compilers, no build tools, no pip cache.

```
  ┌─────────────────────────────────────────────────┐
  │         STAGE 1: BUILDER                         │
  │         FROM python:3.10-slim-bookworm           │
  │                                                  │
  │   COPY requirements.txt                          │
  │   pip install --prefix=/install                  │
  │       (dependencies compiled here)               │
  │                                                  │
  │   Result: /install/ contains all packages        │
  └──────────────────────┬──────────────────────────┘
                         │ COPY --from=builder
                         ▼
  ┌─────────────────────────────────────────────────┐
  │         STAGE 2: PRODUCTION                      │
  │         FROM python:3.10-slim-bookworm           │
  │                                                  │
  │   Install: curl (health checks only)             │
  │   Create: non-root user "appuser"                │
  │   COPY --from=builder /install → /usr/local      │
  │   COPY application source code                   │
  │   chown everything to appuser                    │
  │                                                  │
  │   EXPOSE 8080                                    │
  │   HEALTHCHECK: curl /health every 30s            │
  │   USER appuser                                   │
  │   CMD: uvicorn app:app --host 0.0.0.0            │
  │        --port 8080 --workers 2                   │
  └─────────────────────────────────────────────────┘
```

---

## 3. Docker Compose Full Stack

When running locally with `docker compose up`, four services spin up together. MongoDB starts first (the app depends on it), and then Prometheus begins scraping the app's `/metrics` endpoint every 15 seconds.

```
  docker compose up -d
         │
         ├──▶ mongodb (:27017)
         │      │  healthcheck: mongosh --eval "db.adminCommand('ping')"
         │      │
         │      ▼ (depends_on: healthy)
         ├──▶ app (:8080)
         │      │  healthcheck: curl http://localhost:8080/health
         │      │  volumes: model-artifacts
         │      │
         │      │ /metrics endpoint
         │      ▼
         ├──▶ prometheus (:9090)
         │      │  scrape_interval: 15s
         │      │  retention: 30 days
         │      │
         │      │ datasource
         │      ▼
         └──▶ grafana (:3000)
                 │  pre-configured dashboard
                 │  default login: admin/admin
                 └──▶ text-summarizer.json dashboard
```

---

## 4. ML Training Pipeline Workflow

The training pipeline runs through five sequential stages. I made each stage independent so I can rerun any single stage without starting from scratch. The pipeline reads from `config/config.yaml` for paths and from `params.yaml` for hyperparameters.

```
  python main.py
         │
         ▼
  ┌─────────────────────────────────────────┐
  │  Read config/config.yaml                │
  │  Read params.yaml                       │
  └──────────────────┬──────────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────────┐
  │  STAGE 1: Data Ingestion                │
  │                                         │
  │  Input:  GitHub URL (ZIP archive)       │
  │  Action: Download → Extract             │
  │  Output: artifacts/data_ingestion/      │
  │          └── samsum_dataset/            │
  │              ├── train.csv              │
  │              ├── test.csv               │
  │              └── validation.csv         │
  └──────────────────┬──────────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────────┐
  │  STAGE 2: Data Validation               │
  │                                         │
  │  Input:  artifacts/data_ingestion/      │
  │  Action: Verify required files exist    │
  │          Check schema consistency       │
  │  Output: Validation status (pass/fail)  │
  └──────────────────┬──────────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────────┐
  │  STAGE 3: Data Transformation           │
  │                                         │
  │  Input:  Raw CSV datasets               │
  │  Action: Load PEGASUS tokenizer         │
  │          Tokenize dialogues + summaries │
  │          Convert to HuggingFace Dataset │
  │  Output: artifacts/data_transformation/ │
  │          └── tokenized dataset          │
  └──────────────────┬──────────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────────┐
  │  STAGE 4: Model Training                │
  │                                         │
  │  Input:  Tokenized dataset              │
  │  Model:  google/pegasus-cnn_dailymail   │
  │  Action: Fine-tune on SAMSum dataset    │
  │          (dialogue summarisation)       │
  │  Output: artifacts/model_trainer/       │
  │          ├── model/                     │
  │          └── tokenizer/                 │
  └──────────────────┬──────────────────────┘
                     │
                     ▼
  ┌─────────────────────────────────────────┐
  │  STAGE 5: Model Evaluation              │
  │                                         │
  │  Input:  Trained model + test set       │
  │  Action: Generate summaries on test set │
  │          Calculate ROUGE scores         │
  │          Calculate BLEU score           │
  │  Output: artifacts/model_evaluation/    │
  │          └── metrics.csv                │
  └─────────────────────────────────────────┘
```

---

## 5. Kubernetes Deployment Workflow

Deploying to Kubernetes involves applying a set of manifests in the right order. I use Kustomize to manage environment-specific overlays (staging vs production).

```
  kubectl apply -k k8s/
         │
         ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  1. Namespace         →  text-summarizer (isolation)         │
  │  2. ServiceAccount    →  RBAC identity for pods              │
  │  3. ConfigMap         →  Non-sensitive app config            │
  │  4. Secret            →  JWT key, MongoDB URL (base64)       │
  │  5. NetworkPolicy     →  Allow only: ingress, prometheus     │
  │  6. Deployment        →  3 replicas, rolling update strategy │
  │     ├── Liveness probe:  GET /health every 30s               │
  │     ├── Readiness probe: GET /health every 10s               │
  │     ├── Resource limits: CPU + memory caps                   │
  │     └── Environment: from ConfigMap + Secret                 │
  │  7. Service           →  ClusterIP, port 80 → target 8080   │
  │  8. Ingress           →  TLS, hostname routing               │
  │  9. HPA               →  Scale 2–10 replicas at 70% CPU     │
  │ 10. PodDisruptionBudget → Min 2 pods always available        │
  │ 11. ServiceMonitor    →  Prometheus auto-discovery           │
  └──────────────────────────────────────────────────────────────┘
```

**Rolling Update Strategy:**

```
  Current State: [Pod v1] [Pod v1] [Pod v1]

  Update begins:
  Step 1:  [Pod v1] [Pod v1] [Pod v1] [Pod v2 starting...]
  Step 2:  [Pod v1] [Pod v1] [Pod v2 ✓]  [Pod v1 terminating]
  Step 3:  [Pod v1] [Pod v2 ✓] [Pod v2 starting...]
  Step 4:  [Pod v2 ✓] [Pod v2 ✓] [Pod v2 starting...]
  Step 5:  [Pod v2 ✓] [Pod v2 ✓] [Pod v2 ✓]

  Zero downtime achieved.
```

---

## 6. Authentication Flow

```
  ┌────────┐                              ┌──────────┐
  │ Client │                              │ FastAPI  │
  └───┬────┘                              └────┬─────┘
      │                                        │
      │  POST /auth/token                      │
      │  { username, password }                │
      │───────────────────────────────────────▶│
      │                                        │ Validate credentials
      │                                        │ Generate JWT (HS256)
      │         { access_token, expires_in }   │ Set 30-min expiry
      │◀───────────────────────────────────────│
      │                                        │
      │  POST /predict                         │
      │  Authorization: Bearer <token>         │
      │  { text: "..." }                       │
      │───────────────────────────────────────▶│
      │                                        │ Decode JWT
      │                                        │ Check expiry
      │                                        │ Rate limit check
      │                                        │ Sanitize input
      │                                        │ Run PEGASUS
      │                                        │ Log to MongoDB
      │         { summary, processing_time }   │
      │◀───────────────────────────────────────│
      │                                        │
```

---

## 7. Monitoring & Alerting Flow

```
  ┌──────────┐     ┌────────────┐     ┌─────────────┐     ┌──────────┐
  │ FastAPI  │     │ Prometheus │     │   Grafana   │     │ Operator │
  │ App      │     │            │     │             │     │ (Human)  │
  └────┬─────┘     └─────┬──────┘     └──────┬──────┘     └────┬─────┘
       │                 │                   │                  │
       │  Every request: │                   │                  │
       │  Record metrics │                   │                  │
       │  (counters,     │                   │                  │
       │   histograms,   │                   │                  │
       │   gauges)       │                   │                  │
       │                 │                   │                  │
       │◀── GET /metrics │                   │                  │
       │    (every 15s)  │                   │                  │
       │────────────────▶│                   │                  │
       │                 │  Store time series │                  │
       │                 │                   │                  │
       │                 │◀── PromQL query ──│                  │
       │                 │──── results ─────▶│                  │
       │                 │                   │                  │
       │                 │                   │  Dashboard panels │
       │                 │                   │  • Request rate   │
       │                 │                   │  • P95 latency    │
       │                 │                   │  • Error rate     │
       │                 │                   │  • Model status   │
       │                 │                   │─────────────────▶│
       │                 │                   │   Visual alerts   │
       │                 │                   │                  │
```

---

## 8. Testing Workflow

I structured the test suite to cover each layer independently. Integration tests use `httpx.AsyncClient` with FastAPI's test client so no real server is needed.

```
  pytest --cov=src/ --cov-report=html
         │
         ├── test_settings.py      → Configuration loading & validation
         │     └── Pydantic field validators, defaults, computed props
         │
         ├── test_schemas.py       → Request/response model validation
         │     └── Valid inputs, boundary values, type enforcement
         │
         ├── test_auth.py          → JWT token lifecycle
         │     └── Create token, verify token, expired token, invalid token
         │
         ├── test_rate_limiter.py  → Token bucket algorithm
         │     └── Normal usage, burst, exhaustion, refill
         │
         ├── test_sanitizer.py     → Threat pattern detection
         │     └── SQL injection, XSS, path traversal, clean inputs
         │
         ├── test_exceptions.py    → Custom exception hierarchy
         │     └── Error codes, messages, HTTP status mapping
         │
         └── test_api.py           → Full API integration
               └── Health check, status, predict, auth flow, error handling

  Coverage report → htmlcov/index.html
  Threshold: 80% minimum
```

---

## 9. Pre-Commit Hook Workflow

Before any commit lands in the repository, pre-commit hooks run these checks locally. This catches issues before they reach CI.

```
  git commit -m "feature: add new endpoint"
         │
         ▼
  ┌─────────────────────────┐
  │  .pre-commit-config.yaml│
  └────────────┬────────────┘
               │
               ├──▶ trailing-whitespace    (remove trailing spaces)
               ├──▶ end-of-file-fixer      (ensure newline at EOF)
               ├──▶ check-yaml             (valid YAML syntax)
               ├──▶ check-added-large-files (block files > 500KB)
               ├──▶ black                  (auto-format Python)
               ├──▶ isort                  (sort imports)
               ├──▶ flake8                 (PEP 8 compliance)
               └──▶ mypy                   (type checking)
                    │
                    ├── All pass → Commit proceeds
                    └── Any fail → Commit blocked, fix and retry
```

---

## 10. Error Handling Flow

```
  Request arrives
       │
       ▼
  ┌─── Is route valid? ──── No ──▶ 404 NotFoundError
  │    Yes
  │    ▼
  ├─── Rate limit OK? ──── No ──▶ 429 RateLimitExceeded
  │    Yes
  │    ▼
  ├─── JWT valid? ───────── No ──▶ 401 AuthenticationError
  │    Yes
  │    ▼
  ├─── Schema valid? ────── No ──▶ 422 ValidationError (field-level details)
  │    Yes
  │    ▼
  ├─── Input safe? ──────── No ──▶ 400 SanitisationError (threat detected)
  │    Yes
  │    ▼
  ├─── Model loaded? ────── No ──▶ 503 ServiceUnavailable
  │    Yes
  │    ▼
  ├─── Inference OK? ────── No ──▶ 500 PredictionError
  │    Yes
  │    ▼
  └──▶ 200 PredictResponse { summary, processing_time, request_id }

  All errors return:
  {
    "error": "ErrorType",
    "status_code": 4xx/5xx,
    "message": "Human-readable explanation",
    "request_id": "req_abc123",
    "detail": { ... }   // optional field-level info
  }
```
