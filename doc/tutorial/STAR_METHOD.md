# Project Description — STAR Method

> End-to-End Text Summarisation API with GitHub Actions CI/CD

---

## Situation

I needed to build a production-grade machine learning API that could take raw text input and return concise, abstractive summaries. The project was not just about getting a model to work — it was about demonstrating the full lifecycle of an ML application, from research and experimentation through to automated deployment with enterprise-level security, monitoring, and reliability. The target audience included both end users consuming the API and engineering teams who would maintain, scale, and extend it in production environments. There was no existing infrastructure, no pre-built pipeline, and no deployment automation — everything had to be designed and implemented from scratch on a modern Python stack.

---

## Task

My responsibility was to design, implement, and deploy the entire system end to end. Specifically, I needed to:

- Research and select an appropriate transformer model for abstractive text summarisation, then fine-tune it on a dialogue-specific dataset.
- Build a reproducible, multi-stage ML training pipeline that could be rerun independently at any stage without starting from scratch.
- Wrap the trained model in a production-ready REST API with proper request validation, error handling, and documentation.
- Implement a multi-layered security architecture covering authentication, rate limiting, input sanitisation, and container hardening.
- Integrate async database logging for audit trails and prediction tracking without blocking API response times.
- Set up a full observability stack with Prometheus metrics collection, Grafana dashboards, and structured JSON logging with request correlation.
- Containerise the application using Docker with multi-stage builds and orchestrate production deployment on Kubernetes with auto-scaling, health checks, and network policies.
- Automate the entire lint, test, build, and deploy cycle using GitHub Actions with separate stages and quality gates.
- Write a comprehensive test suite covering unit tests for each layer and integration tests for the full API flow, enforcing a minimum 80% code coverage threshold.

---

## Action

### ML Model Selection and Training

- Evaluated multiple transformer architectures including BART, T5, and GPT-2 for the summarisation task, and selected Google's PEGASUS because its pre-training objective (predicting masked gap sentences) is specifically aligned with abstractive summarisation, giving it a structural advantage over general-purpose models.
- Fine-tuned PEGASUS on the SAMSum dialogue summarisation dataset, which contains 14,732 training examples of human conversations paired with human-written summaries, making it directly relevant to the conversational text domain I was targeting.
- Designed the training pipeline as five independent stages — data ingestion, data validation, data transformation, model training, and model evaluation — so that any single stage can be rerun without repeating the entire pipeline, which saved significant time during iterative development.
- Implemented configurable hyperparameters through a separate `params.yaml` file (learning rate, batch size, beam count, gradient accumulation steps) to decouple training configuration from code, allowing experimentation without code changes.
- Computed both ROUGE scores (measuring overlap between generated and reference summaries) and BLEU scores (measuring n-gram precision) during evaluation to get a multi-dimensional view of model quality rather than relying on a single metric.
- Created Jupyter notebooks under `research/` for each pipeline stage to prototype and validate the approach before writing production code, ensuring that every component was proven to work before being formalised.
- Used the HuggingFace `datasets` and `transformers` libraries as the ML backbone because they provide standardised APIs for data loading, tokenisation, training, and inference, reducing the amount of custom code I needed to maintain.
- Stored all pipeline artifacts (downloaded data, tokenised datasets, trained model weights, evaluation metrics) under a versioned `artifacts/` directory structure defined in `config/config.yaml`, making the pipeline outputs traceable and reproducible.

### API Design and Implementation

- Built the REST API using FastAPI because it is async-native (critical for non-blocking database writes and model inference), has built-in dependency injection (which I use for settings, authentication, and rate limiting), and automatically generates OpenAPI/Swagger documentation from the Pydantic schemas.
- Defined strict request and response schemas using Pydantic v2, which is 5-17x faster than v1 and provides field-level validation errors that are returned directly to the client as structured JSON, eliminating the need for manual validation code.
- Implemented the application using the factory pattern (`create_app()`) to make the app testable — test fixtures can create isolated app instances without shared state leaking between tests.
- Used FastAPI's lifespan context manager to handle model loading at startup and database connection cleanup at shutdown, guaranteeing that resources are properly initialised before serving traffic and properly released when the process exits.
- Exposed six endpoints: root redirect to docs, system status, health check, JWT token generation, text prediction, and ML training trigger — each with clearly defined responsibilities and appropriate authentication requirements.
- Designed the prediction endpoint to accept configurable inference parameters (max length, beam count, length penalty) so that consumers can tune the summarisation quality-speed tradeoff per request without requiring server-side changes.
- Implemented comprehensive exception handling with a custom exception hierarchy that maps specific error types to appropriate HTTP status codes, ensuring that every error response includes a machine-readable error type, human-readable message, and the correlation request ID for debugging.
- Used Uvicorn as the ASGI server with 2 worker processes in production, balancing concurrency against memory usage since each worker loads a separate copy of the PEGASUS model into memory.

### Security Implementation

- Implemented JWT-based authentication using the HS256 algorithm with configurable expiry (default 30 minutes), chosen over session-based auth because JWTs are stateless and do not require a database lookup on every request, which is important for keeping prediction latency low.
- Built a token bucket rate limiter from scratch rather than using an external library because the implementation is straightforward (under 110 lines), runs entirely in-memory with O(1) per-request overhead, and avoids adding a Redis dependency for what is currently a single-service deployment.
- Implemented input sanitisation that scans for SQL injection patterns (UNION, SELECT, DROP, OR 1=1), XSS patterns (script tags, javascript: URIs, event handlers), path traversal sequences (../ and ..\), command injection operators (semicolons, pipes, backticks, $()), LDAP injection, and XML entity expansion — covering the OWASP Top 10 attack vectors relevant to a text input API.
- Configured CORS middleware with a whitelist of allowed origins loaded from environment variables, defaulting to restrictive settings in production and permissive settings only in development.
- Enforced non-root container execution by creating a dedicated `appuser` in the Dockerfile and running the application process under that user, limiting the blast radius if the container is compromised.
- Used Kubernetes NetworkPolicy resources to restrict pod-to-pod communication, allowing inbound traffic only from the Ingress controller and Prometheus scraper, blocking all other network access to the application pods.
- Stored all sensitive configuration (JWT secret key, MongoDB connection string, AWS credentials) in Kubernetes Secrets and Docker environment variables, with a `.env.example` template documenting every required variable without exposing actual values.
- Added TLS termination at the Kubernetes Ingress layer using NGINX, ensuring that all traffic between clients and the cluster is encrypted without requiring the application to manage certificates.

### Database and Audit Trail

- Selected MongoDB as the database because the audit records are JSON-shaped prediction logs with varying fields, which fits a document store more naturally than a relational schema, and because the Motor async driver integrates cleanly with FastAPI's async request handlers.
- Implemented connection pooling with configurable minimum (10) and maximum (50) pool sizes to avoid the overhead of establishing a new connection per request while preventing connection exhaustion under load.
- Designed prediction logging as a fire-and-forget async operation so that database latency does not add to the API response time — if the database write fails, the prediction still returns successfully to the user.
- Recorded comprehensive audit fields for each prediction: request ID, input text, output summary, input and output lengths, processing duration in milliseconds, authenticated user ID, and ISO 8601 timestamp.
- Implemented the MongoDBManager as a singleton using `__new__()` to ensure that all request handlers share a single connection pool rather than creating separate pools.
- Added a health check method that measures database round-trip latency using the `ping` admin command, which is exposed through the `/health` endpoint and used by Kubernetes liveness probes.
- Configured server selection and connection timeouts via environment variables so that the application fails fast in development (short timeouts) but is more tolerant of transient network issues in production (longer timeouts).
- Used Docker Compose to run MongoDB alongside the application with a persistent volume mount (`mongodb-data:/data/db`) so that audit data survives container restarts during local development.

### Monitoring and Observability

- Defined 10+ Prometheus metric types covering request throughput (counters), latency distribution (histograms with configurable buckets), active request count (gauge), model inference performance (histogram), authentication attempts (counter), rate limit violations (counter), database operation counts and latency (counter and summary), and system metadata (info metric with version and environment).
- Built a custom request tracking middleware that assigns a unique correlation ID to every request, records the start time, increments the active requests gauge, and after the response completes, records the duration and status code to the appropriate Prometheus metrics.
- Implemented structured JSON logging with fields for timestamp (ISO 8601), log level, message, request ID, HTTP method, endpoint path, response status code, processing duration, and authenticated user — making logs machine-parseable and filterable by any field.
- Created a pre-built Grafana dashboard JSON file (`text-summarizer.json`) that is auto-provisioned when Grafana starts, eliminating manual dashboard setup and ensuring every environment has consistent monitoring from the first deployment.
- Configured Prometheus to scrape the application's `/metrics` endpoint every 15 seconds with a 30-day data retention policy, balancing monitoring granularity against storage costs.
- Set up Grafana datasource provisioning so that Prometheus is automatically configured as the default datasource, requiring zero manual configuration after `docker compose up`.
- Exposed the `/health` endpoint without authentication so that Kubernetes probes, Docker health checks, and external monitoring systems can verify the application status without needing credentials.
- Tracked model availability as a Prometheus gauge (1 = loaded, 0 = not loaded) so that operators can set alerts for the scenario where the model fails to load or crashes during inference.

### Containerisation and Orchestration

- Used multi-stage Docker builds to separate the dependency installation phase (which requires pip and potentially compilation tools) from the production runtime phase (which only needs the Python interpreter and installed packages), reducing image size and attack surface.
- Configured Docker health checks that call the `/health` endpoint every 30 seconds with a 10-second timeout and 3 retries, allowing Docker to automatically detect and restart unhealthy containers.
- Designed the Kubernetes deployment with 3 replicas and a rolling update strategy (maxSurge: 1, maxUnavailable: 0) to achieve zero-downtime deployments — new pods are started and pass readiness checks before old pods are terminated.
- Implemented a Horizontal Pod Autoscaler that scales between 2 and 10 replicas based on CPU utilisation, with a 70% target threshold chosen because ML inference is CPU-bound and response times degrade significantly above this level.
- Created a PodDisruptionBudget requiring a minimum of 2 pods to be available at all times, ensuring that voluntary disruptions (node drains, cluster upgrades) cannot take the service offline.
- Set up Kustomize with base resources and environment-specific overlays for staging and production, allowing environment differences (replica count, resource limits, log level) to be managed declaratively without duplicating manifests.
- Created a ServiceMonitor resource for Prometheus Operator integration, enabling automatic metric scraping discovery in Kubernetes clusters that use the Prometheus Operator pattern.
- Defined resource requests and limits (CPU and memory) on the Deployment pods to ensure the Kubernetes scheduler places pods on nodes with sufficient capacity and prevents a single pod from consuming all node resources.

### CI/CD Pipeline

- Structured the GitHub Actions pipeline into four sequential stages (lint, test, build-and-push, deploy) with explicit dependency gates, so that a formatting error stops the pipeline immediately rather than wasting compute on tests and Docker builds that will ultimately be discarded.
- Configured the lint stage to run Black (formatting), isort (import ordering), flake8 (PEP 8 compliance), and mypy (type checking) in sequence, catching code quality issues before any tests execute.
- Set up pytest with coverage reporting that generates both terminal output (for CI logs) and XML reports (for artifact upload), with an 80% minimum coverage threshold that fails the pipeline if not met.
- Restricted the Docker build-and-push stage to only run on the main branch, preventing every feature branch push from creating unnecessary Docker images in the container registry.
- Tagged Docker images with both the git commit SHA (for traceability — you can always map an image back to the exact code that produced it) and `latest` (for convenience in deployment scripts that always want the newest version).
- Implemented the deploy stage on a self-hosted runner because it needs network access to the production environment, and included a post-deployment health check that verifies the `/health` endpoint returns HTTP 200 within 30 seconds.
- Created a separate `tests.yml` workflow that runs only lint and test stages on pull requests, giving PR reviewers fast feedback without triggering builds or deployments.
- Configured workflow triggers for push to main/develop branches, pull requests to main, and manual workflow dispatch, covering automated deployment, PR validation, and on-demand deployment scenarios respectively.

### Testing Strategy

- Built the test suite using pytest with the `pytest-asyncio` plugin because the application is async-native, and synchronous test wrappers can mask concurrency bugs that only appear under real async execution.
- Used `httpx.AsyncClient` with FastAPI's app instance for integration tests, which sends real HTTP requests through the full middleware stack without starting a network server, giving true end-to-end coverage with the speed of in-process testing.
- Wrote dedicated test files for each architectural layer (settings, schemas, auth, rate limiter, sanitiser, exceptions, API) so that test failures immediately indicate which layer has a regression, without needing to debug through unrelated test code.
- Tested JWT authentication with cases for valid tokens, expired tokens, tampered tokens, and missing tokens, ensuring that every authentication failure mode returns the correct HTTP status code and error message.
- Verified rate limiting behaviour including normal requests, burst requests, bucket exhaustion, token refill after the time window, and per-IP isolation, confirming that the token bucket algorithm works correctly at boundary conditions.
- Tested input sanitisation against specific attack payloads for SQL injection, XSS, path traversal, and command injection, as well as clean inputs that superficially resemble attacks but are legitimate text, reducing false positive risk.
- Configured pytest coverage to exclude research notebooks and ML pipeline stages from the coverage calculation, because those components are tested through the notebook execution and training pipeline runs rather than through unit tests.
- Set up test fixtures in `conftest.py` that provide isolated app instances, mock settings, and test clients, ensuring that tests do not share state and can run in any order without affecting each other.

---

## Result

### Technical Outcomes

- Delivered a fully functional text summarisation API that accepts raw text (10 to 10,000 characters) and returns abstractive summaries using a fine-tuned PEGASUS model, with configurable inference parameters (beam search width, length penalty, maximum output length) exposed per request.
- Achieved a complete 5-stage ML training pipeline that runs end to end from raw data download through model evaluation, with each stage independently rerunnable and all artifacts stored in a structured, traceable directory layout under `artifacts/`.
- Implemented seven distinct security layers (network policy, TLS, CORS, JWT authentication, rate limiting, input sanitisation, container hardening) providing defence in depth against the OWASP Top 10 attack categories relevant to a text input API.
- Built a rate limiting system that handles 100 requests per 60 seconds per client IP with O(1) per-request overhead and no external dependencies, using the token bucket algorithm to allow legitimate burst traffic while preventing sustained abuse.
- Established a monitoring stack with 10+ Prometheus metrics, a pre-built Grafana dashboard, and structured JSON logging with correlation IDs, giving operators real-time visibility into request throughput, latency percentiles (P50, P95, P99), error rates, model performance, and database health.
- Created a zero-downtime deployment system using Kubernetes rolling updates with readiness probes, a Horizontal Pod Autoscaler (2 to 10 replicas at 70% CPU target), and a PodDisruptionBudget (minimum 2 pods available), ensuring the service remains responsive during deployments and cluster maintenance.
- Automated the full delivery pipeline through GitHub Actions with four quality gates (lint, test, build, deploy), where code quality issues block the pipeline before tests run, test failures block before Docker images are built, and a post-deployment health check verifies the new version is actually serving traffic.
- Achieved a comprehensive test suite covering authentication, rate limiting, input sanitisation, schema validation, configuration management, exception handling, and full API integration, with an enforced 80% minimum code coverage threshold in CI.

### Architecture and Design Outcomes

- Produced a codebase organised by responsibility (config, security, monitoring, database, schemas, pipeline) where every piece of functionality has a single predictable location, reducing the cognitive load for developers navigating the project for the first time.
- Implemented the singleton pattern for Settings, MongoDBManager, and AppMetrics to ensure that expensive resources (environment parsing, connection pools, metric registries) are initialised once and shared across all requests without per-request overhead.
- Used FastAPI's dependency injection system for settings, authentication, and rate limiting, making each dependency mockable in tests and replaceable without modifying the route handlers.
- Designed the Docker containerisation with multi-stage builds that separate build-time dependencies from runtime dependencies, producing a minimal production image with no compilers, no pip, and no build tools — only the Python runtime, curl for health checks, and the application code running as a non-root user.
- Created a configuration system that loads from three sources (environment variables via Pydantic BaseSettings, YAML files for ML pipeline config, Kubernetes ConfigMaps and Secrets for production) with type-safe validation and sensible defaults, so the application works out of the box in development and is fully configurable in production.
- Built the monitoring integration so that Prometheus, Grafana datasources, and Grafana dashboards are all auto-provisioned from configuration files, meaning a fresh `docker compose up` or Kubernetes deployment gets full observability without any manual setup steps.
- Structured the CI/CD pipeline so that pull requests get fast feedback (lint and test only) while main branch pushes get the full pipeline (lint, test, build, deploy), optimising developer experience without sacrificing deployment automation.
- Documented every architectural decision, tool selection, and workflow in dedicated files (PROJECT_ARCHITECTURE.md, WORKFLOW_DIAGRAMS.md, COMPLETE_BUILD_GUIDE.md) with ASCII diagrams, decision rationale tables, and reading guides for different audiences (new developers, debuggers, DevOps engineers, ML engineers).
