# Project Architecture — End-to-End Text Summarisation API

> A visual and structural breakdown of every layer in this system, from client request to model inference and back.

---

## High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT / CONSUMER                                  │
│                  (Browser, cURL, Postman, Frontend App)                     │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     KUBERNETES INGRESS (TLS Termination)                    │
│                          ingress.yaml · NGINX                              │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     KUBERNETES SERVICE (Load Balancer)                      │
│                 service.yaml · ClusterIP · Port 8080                       │
│              Distributes traffic across 2–10 pod replicas                  │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
     ┌────────────┐    ┌────────────┐    ┌────────────┐
     │  Pod (1)   │    │  Pod (2)   │    │  Pod (3)   │
     │  FastAPI   │    │  FastAPI   │    │  FastAPI   │
     │  Uvicorn   │    │  Uvicorn   │    │  Uvicorn   │
     └────────────┘    └────────────┘    └────────────┘
            │                                  │
            └──────────────┬───────────────────┘
                           │
            ┌──────────────┼──────────────────┐
            ▼              ▼                  ▼
      ┌──────────┐  ┌────────────┐   ┌──────────────┐
      │ MongoDB  │  │ Prometheus │   │   Grafana    │
      │ (Audit)  │  │ (Metrics)  │   │ (Dashboard)  │
      └──────────┘  └────────────┘   └──────────────┘
```

---

## Request Lifecycle (Inside Each Pod)

Every single API request passes through the following layers in this exact order. I designed it as a pipeline so each concern is isolated and testable independently.

```
  Incoming HTTP Request
         │
         ▼
  ┌──────────────────┐
  │   CORS Middleware │  ← Allows configured origins only
  └────────┬─────────┘
           ▼
  ┌──────────────────────────┐
  │ Request Tracking         │  ← Assigns unique request_id (correlation ID)
  │ Middleware                │    Starts timer for latency measurement
  └────────┬─────────────────┘
           ▼
  ┌──────────────────────────┐
  │ Rate Limiter             │  ← Token bucket algorithm (100 req / 60s per IP)
  │ (Token Bucket)           │    Returns 429 if exceeded
  └────────┬─────────────────┘
           ▼
  ┌──────────────────────────┐
  │ JWT Authentication       │  ← Decodes Bearer token (HS256)
  │ (FastAPI Depends)        │    Rejects with 401 if invalid/expired
  └────────┬─────────────────┘
           ▼
  ┌──────────────────────────┐
  │ Pydantic Validation      │  ← Validates request body (types, lengths, ranges)
  │ (Schema Layer)           │    Returns 422 with field-level errors
  └────────┬─────────────────┘
           ▼
  ┌──────────────────────────┐
  │ Input Sanitization       │  ← Checks for SQL injection, XSS, path traversal,
  │ (Security Layer)         │    command injection, LDAP injection
  └────────┬─────────────────┘
           ▼
  ┌──────────────────────────┐
  │ PEGASUS Model Inference  │  ← Tokenize → Generate → Decode
  │ (Prediction Pipeline)    │    Beam search with configurable parameters
  └────────┬─────────────────┘
           ▼
  ┌──────────────────────────┐
  │ Async MongoDB Logging    │  ← Fire-and-forget audit log (non-blocking)
  │ (Audit Trail)            │    Records: input, output, duration, user, timestamp
  └────────┬─────────────────┘
           ▼
  ┌──────────────────────────┐
  │ Prometheus Metrics       │  ← Records: latency histogram, status counter,
  │ (Observability)          │    input/output length, prediction duration
  └────────┬─────────────────┘
           ▼
     JSON Response
```

---

## Source Code Architecture

```
src/textSummarizer/
│
├── config/
│   ├── settings.py            ← Pydantic BaseSettings (53 env vars, singleton)
│   └── configuration.py       ← YAML-based ML pipeline config manager
│
├── security/
│   ├── auth.py                ← JWT creation & verification (HS256)
│   ├── rate_limiter.py        ← Token bucket per-IP rate limiting
│   └── sanitizer.py           ← Pattern-based threat detection
│
├── monitoring/
│   ├── metrics.py             ← 10+ Prometheus metric types (singleton)
│   ├── middleware.py          ← Request tracking & correlation IDs
│   └── structured_logging.py  ← JSON-formatted audit logging
│
├── database/
│   └── mongodb.py             ← Async Motor driver, connection pooling (10-50)
│
├── schemas/
│   ├── requests.py            ← PredictRequest, TokenRequest (Pydantic v2)
│   └── responses.py           ← PredictResponse, HealthResponse, ErrorResponse
│
├── pipeline/
│   ├── prediction.py          ← PEGASUS inference pipeline (HuggingFace)
│   ├── stage_01_data_ingestion.py
│   ├── stage_02_data_validation.py
│   ├── stage_03_data_transformation.py
│   ├── stage_04_model_trainer.py
│   └── stage_05_model_evaluation.py
│
├── conponents/                ← ML training components (called by pipeline stages)
│   ├── data_ingestion.py
│   ├── data_validation.py
│   ├── data_transformation.py
│   ├── model_trainer.py
│   └── model_evaluation.py
│
├── exceptions.py              ← Custom exception hierarchy
├── logging/                   ← Logger initialisation
└── utils/
    └── common.py              ← Shared file/directory helpers
```

---

## Infrastructure Layer

```
┌─────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS CI/CD                  │
│                                                         │
│  ┌──────┐    ┌──────┐    ┌───────────┐    ┌─────────┐  │
│  │ LINT │───▶│ TEST │───▶│ BUILD &   │───▶│ DEPLOY  │  │
│  │      │    │      │    │ PUSH ECR  │    │ (K8s)   │  │
│  └──────┘    └──────┘    └───────────┘    └─────────┘  │
│   black       pytest      docker build     pull image   │
│   flake8      coverage    tag: SHA+latest  health check │
│   isort                   push to ECR                   │
│   mypy                                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               DOCKER COMPOSE (Local Stack)              │
│                                                         │
│   ┌─────────┐  ┌─────────┐  ┌────────────┐  ┌───────┐ │
│   │ FastAPI │  │ MongoDB │  │ Prometheus │  │Grafana│ │
│   │  :8080  │  │  :27017 │  │   :9090    │  │ :3000 │ │
│   └─────────┘  └─────────┘  └────────────┘  └───────┘ │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│             KUBERNETES PRODUCTION CLUSTER                │
│                                                         │
│  Namespace: text-summarizer                             │
│  ┌────────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │ Deployment │  │ Service  │  │ HPA (2-10 replicas)│  │
│  │ 3 replicas │  │ ClusterIP│  │ CPU target: 70%    │  │
│  └────────────┘  └──────────┘  └────────────────────┘  │
│  ┌────────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │ Ingress    │  │ Network  │  │ Pod Disruption     │  │
│  │ TLS/NGINX  │  │ Policy   │  │ Budget (minAvail:2)│  │
│  └────────────┘  └──────────┘  └────────────────────┘  │
│  ┌────────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │ ConfigMap  │  │ Secrets  │  │ ServiceAccount     │  │
│  └────────────┘  └──────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## ML Training Pipeline

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  STAGE 1         │     │  STAGE 2         │     │  STAGE 3             │
│  Data Ingestion  │────▶│  Data Validation │────▶│  Data Transformation │
│                  │     │                  │     │                      │
│  • Download ZIP  │     │  • Check schema  │     │  • PEGASUS tokenizer │
│    from GitHub   │     │  • Verify files: │     │  • Encode dialogues  │
│  • Extract to    │     │    train, test,  │     │  • Prepare dataset   │
│    artifacts/    │     │    validation    │     │    splits            │
└──────────────────┘     └──────────────────┘     └──────────────────────┘
                                                            │
                                                            ▼
                         ┌──────────────────┐     ┌──────────────────────┐
                         │  STAGE 5         │     │  STAGE 4             │
                         │  Model Eval      │◀────│  Model Training      │
                         │                  │     │                      │
                         │  • BLEU score    │     │  • Fine-tune PEGASUS │
                         │  • ROUGE metrics │     │    on SAMSum dataset │
                         │  • Save report   │     │  • Save model +      │
                         │                  │     │    tokenizer         │
                         └──────────────────┘     └──────────────────────┘
```

---

## Configuration Sources

```
                    ┌─────────────────────────┐
                    │    Application Code     │
                    └────────────┬────────────┘
                                 │ reads from
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
     ┌────────────────┐  ┌─────────────┐  ┌────────────────┐
     │  .env file     │  │ config.yaml │  │  K8s ConfigMap │
     │  (53 vars)     │  │ (ML params) │  │  + Secrets     │
     │                │  │             │  │                │
     │  Loaded via    │  │  Pipeline   │  │  Injected as   │
     │  Pydantic      │  │  stages,    │  │  env vars in   │
     │  BaseSettings  │  │  model path,│  │  production    │
     │                │  │  data URLs  │  │  pods          │
     └────────────────┘  └─────────────┘  └────────────────┘
```

---

## Security Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                         │
│                                                              │
│  LAYER 1: Network                                            │
│  ├── Kubernetes NetworkPolicy (pod-to-pod restrictions)      │
│  ├── TLS termination at Ingress                              │
│  └── CORS origin whitelist                                   │
│                                                              │
│  LAYER 2: Authentication                                     │
│  ├── JWT Bearer tokens (HS256, 30-min expiry)                │
│  └── Optional API key header                                 │
│                                                              │
│  LAYER 3: Rate Limiting                                      │
│  ├── Token bucket algorithm (100 req / 60s per IP)           │
│  └── Returns HTTP 429 when exceeded                          │
│                                                              │
│  LAYER 4: Input Validation                                   │
│  ├── Pydantic v2 schema enforcement                          │
│  ├── Text length bounds (10–10,000 chars)                    │
│  └── Numeric range constraints                               │
│                                                              │
│  LAYER 5: Threat Detection                                   │
│  ├── SQL injection patterns (UNION, SELECT, DROP …)          │
│  ├── XSS patterns (<script>, javascript:, onerror= …)       │
│  ├── Path traversal (../ , ..\\ )                            │
│  ├── Command injection (; | && || ` $())                     │
│  └── LDAP / XML entity expansion                             │
│                                                              │
│  LAYER 6: Container Hardening                                │
│  ├── Non-root user (appuser) inside container                │
│  ├── Multi-stage Docker build (minimal attack surface)       │
│  └── Read-only volume mounts for model artifacts             │
│                                                              │
│  LAYER 7: Audit                                              │
│  ├── Every prediction logged to MongoDB                      │
│  ├── Request correlation IDs for tracing                     │
│  └── Structured JSON logs with user context                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Monitoring & Observability Stack

```
┌────────────────┐         ┌─────────────────┐         ┌──────────────┐
│   FastAPI App  │ /metrics│   Prometheus     │  query  │   Grafana    │
│                │────────▶│                  │────────▶│              │
│  Records:      │  scrape │  Stores:         │         │  Displays:   │
│  • Counters    │  every  │  • Time series   │         │  • RPS chart │
│  • Histograms  │  15s    │  • 30-day        │         │  • Latency   │
│  • Gauges      │         │    retention     │         │    P50/P95   │
│  • Summaries   │         │                  │         │  • Errors    │
│  • Info        │         │                  │         │  • DB stats  │
└────────────────┘         └─────────────────┘         └──────────────┘
```

**Metrics Tracked:**

| Category       | Metric                          | Type      |
|----------------|--------------------------------|-----------|
| Requests       | `requests_total`               | Counter   |
| Requests       | `requests_in_progress`         | Gauge     |
| Requests       | `request_duration_seconds`     | Histogram |
| Predictions    | `predictions_total`            | Counter   |
| Predictions    | `prediction_duration_seconds`  | Histogram |
| Predictions    | `prediction_input_length`      | Histogram |
| Predictions    | `prediction_output_length`     | Histogram |
| Auth           | `auth_attempts_total`          | Counter   |
| Rate Limiting  | `rate_limit_hits_total`        | Counter   |
| Database       | `db_operations_total`          | Counter   |
| Database       | `db_operation_duration_seconds`| Summary   |
| System         | `model_loaded`                 | Gauge     |
| System         | `app_info`                     | Info      |

---

## API Endpoints

```
┌────────┬─────────────┬──────────────────────────────────────┬───────────┐
│ Method │ Path        │ Description                          │ Auth?     │
├────────┼─────────────┼──────────────────────────────────────┼───────────┤
│ GET    │ /           │ Redirect to API docs (Swagger)       │ No        │
│ GET    │ /status     │ App version, environment, model flag │ No        │
│ GET    │ /health     │ Liveness: API + DB + model checks    │ No        │
│ POST   │ /auth/token │ Generate JWT access token            │ No        │
│ POST   │ /predict    │ Summarise text using PEGASUS         │ Yes (JWT) │
│ GET    │ /train      │ Trigger ML training pipeline         │ No        │
│ GET    │ /metrics    │ Prometheus scrape endpoint           │ No        │
└────────┴─────────────┴──────────────────────────────────────┴───────────┘
```

---

## Design Patterns Summary

| Pattern                  | Where Used                              | Why                                          |
|--------------------------|-----------------------------------------|----------------------------------------------|
| Singleton                | Settings, MongoDBManager, AppMetrics    | One instance shared across all requests       |
| Factory                  | `create_app()` in app.py                | Testable app creation, clean initialisation   |
| Dependency Injection     | FastAPI `Depends()` for settings, auth  | Loose coupling, easy mocking in tests         |
| Middleware Pipeline      | CORS → Tracking → Rate Limit → Handler  | Separation of cross-cutting concerns          |
| Lifespan Context Manager | Model loading, DB connection            | Guaranteed setup and teardown                 |
| Pipeline (ML)            | 5-stage training pipeline               | Each stage independent and rerunnable         |
| Token Bucket             | Rate limiter                            | Smooth, burst-friendly rate control           |
