# Documentation Guide — Why I Structured It This Way

> This file explains what is in `PROJECT_ARCHITECTURE.md` and `WORKFLOW_DIAGRAMS.md`, why I included each section, and the reasoning behind the tools and approaches I chose for this project.

---

## What Is in PROJECT_ARCHITECTURE.md

I wrote `PROJECT_ARCHITECTURE.md` as a single reference that someone can open and immediately understand how every piece of this system fits together — without reading a single line of code.

### High-Level System Overview

I start with the big picture: client, ingress, service, pods, and backing services. I included this because when someone new joins a project, the first question is always "what talks to what?" This diagram answers that in seconds. I chose to show the Kubernetes layer here because that is the production target — Docker Compose is for local development only.

### Request Lifecycle

This is probably the most important diagram in the entire documentation. It shows the exact order in which every middleware, security check, and processing step happens for a single API request. I included it because debugging production issues becomes dramatically easier when you know exactly which layer rejected a request. The layers are:

- **CORS Middleware** — I use FastAPI's built-in CORS middleware because it handles preflight requests correctly and is configurable via environment variables. No need for a custom solution.
- **Request Tracking Middleware** — I built this as a custom middleware that attaches a unique `request_id` to every request. I chose correlation IDs over distributed tracing (like OpenTelemetry) because the system is a single service, not a microservice mesh. Correlation IDs give me 90% of the debugging value at 10% of the complexity.
- **Token Bucket Rate Limiter** — I chose the token bucket algorithm over fixed window or sliding window because it handles bursts gracefully. A user can send 10 requests in one second as long as they have tokens, but they cannot sustain high throughput indefinitely. I implemented it in-memory rather than using Redis because this is a single-service deployment — distributed rate limiting would be over-engineering.
- **JWT Authentication** — I chose JWT over session-based auth because the API is stateless by design. JWTs are self-contained, so I do not need a database lookup on every request. I use HS256 (symmetric) because there is only one service verifying tokens. If I had multiple services, I would switch to RS256 (asymmetric) so only the auth service holds the private key.
- **Input Sanitization** — I built pattern-based detection for SQL injection, XSS, command injection, and path traversal. I chose pattern matching over a WAF (Web Application Firewall) because it gives me application-level control and the patterns are specific to my input domain (text for summarisation).

### Source Code Architecture

I laid out the full directory tree with one-line descriptions because navigating unfamiliar code is the second biggest time sink after understanding the overall architecture. Each directory maps to a single responsibility — `security/` handles security, `monitoring/` handles observability, `database/` handles persistence. I follow this structure because it means you can find any piece of functionality in one predictable location.

### Infrastructure Layer

I included three infrastructure diagrams (CI/CD, Docker Compose, Kubernetes) because this project runs in three different modes and each has a distinct topology. The CI/CD diagram shows the four-stage pipeline. The Docker Compose diagram shows the local development stack. The Kubernetes diagram shows the production deployment with all its supporting resources (HPA, NetworkPolicy, PDB, etc.).

### ML Training Pipeline

I documented the five-stage pipeline because the ML workflow is completely separate from the API serving workflow. Someone working on model training should not need to understand the FastAPI codebase, and vice versa. Each stage reads from and writes to the `artifacts/` directory, making them independently rerunnable.

### Security Architecture

I organised security into seven layers because defence in depth is not just a buzzword — it is the only approach that works. If the rate limiter fails, JWT still blocks unauthenticated requests. If JWT is compromised, input sanitisation still catches injection attempts. If sanitisation misses something, the non-root container user limits the blast radius. I listed all seven layers explicitly so that during security reviews, you can verify each one independently.

### Monitoring & Observability

I documented every Prometheus metric with its type (Counter, Gauge, Histogram, Summary) because when you are building Grafana dashboards or writing alerting rules, you need to know exactly what is available and what type it is. Counters are for rates (use `rate()`), histograms are for percentiles (use `histogram_quantile()`), gauges are for current values (use as-is).

### API Endpoints Table

I included a simple table with method, path, description, and auth requirement because this is the contract that every API consumer needs. It is more useful than Swagger for a quick overview because it fits on one screen.

### Design Patterns

I listed every design pattern with where it is used and why I chose it. I included this section because patterns are decisions, and decisions should be documented. If someone asks "why is Settings a singleton?", the answer is in the table: one instance shared across all requests to avoid re-parsing environment variables on every call.

---

## What Is in WORKFLOW_DIAGRAMS.md

I wrote `WORKFLOW_DIAGRAMS.md` to capture how things move through time — processes, sequences, and state transitions. While the architecture document is a snapshot of structure, the workflow document shows how the system behaves.

### CI/CD Pipeline

I diagrammed all four stages with their tools, success/failure paths, and conditions (e.g., build only runs on main branch). I included this because CI/CD pipelines are notoriously opaque — the YAML is hard to read, and the GitHub Actions UI does not show the full picture. This diagram is what I wish every project had.

**Why these four stages:**
- **Lint first** — Formatting and style issues are the cheapest to catch. Running tests before linting wastes compute on code that will need to be reformatted anyway.
- **Test second** — I use pytest with coverage because it is the Python standard. The 80% coverage threshold is a pragmatic target: high enough to catch regressions, low enough to not force meaningless tests.
- **Build third** — Multi-stage Docker builds because single-stage builds produce unnecessarily large images with build tools included. I tag with both the git SHA (for traceability) and `latest` (for convenience).
- **Deploy last** — Health check verification after deployment because a container that starts is not necessarily a container that works. The 30-second wait gives the model time to load into memory.

### Docker Build Workflow

I diagrammed the multi-stage build because it is a non-obvious optimisation. The builder stage has all the compilation tools. The production stage has none of them — just the Python runtime, `curl` for health checks, and the application code running as a non-root user. This reduces the attack surface and the image size simultaneously.

### Docker Compose Stack

I showed the dependency chain between services because startup order matters. If the app starts before MongoDB is healthy, the first requests will fail. Docker Compose's `depends_on` with health checks solves this, but only if you understand the dependency graph.

### ML Training Pipeline

I diagrammed each stage with its inputs, actions, and outputs because ML pipelines are notoriously hard to debug when something goes wrong in the middle. With this diagram, you can look at any stage's output directory and verify whether it completed correctly.

**Why PEGASUS:** I chose PEGASUS (Pre-training with Extracted Gap-sentences for Abstractive Summarisation) because it was specifically designed for abstractive summarisation. Unlike BART or T5 which are general-purpose, PEGASUS's pre-training objective (predicting masked sentences) aligns directly with the summarisation task. I fine-tune on SAMSum (dialogue summarisation dataset) because the target use case is summarising conversational text.

### Kubernetes Deployment

I listed the 11 Kubernetes resources in application order because applying them out of order causes temporary failures (e.g., the Deployment references a Secret that does not exist yet). The rolling update diagram shows exactly how zero-downtime deployment works — one pod at a time, with readiness probes gating traffic.

**Why these K8s resources:**
- **HPA (Horizontal Pod Autoscaler)** — I set the CPU target at 70% because ML inference is CPU-bound. Scaling at 70% gives headroom before response times degrade.
- **PodDisruptionBudget** — Minimum 2 pods available ensures the service survives node drains during cluster upgrades.
- **NetworkPolicy** — I restrict ingress to only the Ingress controller and Prometheus because the principle of least privilege applies to network access, not just IAM.

### Authentication Flow

I drew the sequence diagram because auth flows have two phases (get token, use token) and it is easy to confuse which headers go where. The diagram makes it clear: POST to `/auth/token` with credentials, GET back a JWT, then use that JWT as a Bearer token on `/predict`.

### Monitoring Flow

I showed the pull-based monitoring architecture because it is different from push-based systems that people may be familiar with. Prometheus pulls metrics from the app every 15 seconds. Grafana queries Prometheus using PromQL. This pull model is more reliable than push because the monitoring system controls the collection rate.

### Testing Workflow

I listed each test file with what it covers because test suites grow organically and it quickly becomes unclear which tests cover which functionality. This map ensures that when someone changes the rate limiter, they know to run `test_rate_limiter.py`.

### Pre-Commit Hooks

I documented the hook chain because developers hit pre-commit failures and do not know why their commit was blocked. This diagram shows exactly what runs and in what order.

### Error Handling Flow

I drew the decision tree because error responses are the most common thing developers debug during integration. This flowchart tells you: "if you got a 429, it was the rate limiter; if you got a 401, your JWT is invalid or expired; if you got a 422, your request body failed Pydantic validation." No guessing required.

---

## Why I Chose These Tools

| Tool | Why I Chose It | What I Considered Instead |
|------|---------------|--------------------------|
| **FastAPI** | Async-native, automatic OpenAPI docs, Pydantic integration, dependency injection built in | Flask (no async), Django REST (too heavy for a single-endpoint API) |
| **PEGASUS** | Purpose-built for abstractive summarisation; pre-training aligns with the task | BART (general purpose), T5 (general purpose), GPT-2 (generative, not summarisation-specific) |
| **Pydantic v2** | 5-17x faster than v1, built-in with FastAPI, excellent validation errors | Marshmallow (no FastAPI integration), attrs (no serialisation) |
| **MongoDB** | Schema-flexible for audit logs, async driver (Motor), natural fit for JSON-shaped prediction records | PostgreSQL (rigid schema for evolving audit data), SQLite (no async, no replication) |
| **JWT (HS256)** | Stateless auth, no database lookup per request, self-contained claims | Session cookies (stateful, needs Redis/DB), OAuth2 (overkill for a single service) |
| **Token Bucket** | Burst-friendly, simple to implement, O(1) per check | Fixed window (burst at boundary), sliding window (more complex, marginal benefit) |
| **Prometheus + Grafana** | Pull-based (reliable), industry standard, pre-built dashboard support | DataDog (paid), ELK stack (heavier, better for logs than metrics) |
| **GitHub Actions** | Native GitHub integration, free for public repos, YAML-based, good marketplace | Jenkins (self-hosted overhead), CircleCI (separate service), GitLab CI (requires GitLab) |
| **Docker multi-stage** | Smaller images, no build tools in production, clear separation | Single-stage (larger, less secure), distroless (harder to debug, no shell) |
| **Kubernetes** | Industry standard orchestration, HPA for auto-scaling, built-in health checks | Docker Swarm (limited features), ECS (AWS lock-in), Nomad (smaller ecosystem) |
| **pytest** | Fixture system, async support, plugins ecosystem, coverage integration | unittest (verbose, no fixtures), nose2 (smaller community) |
| **Black + isort + flake8** | Zero-config formatting, deterministic output, no style debates | Prettier (JS-focused), autopep8 (less opinionated, allows style drift) |

---

## How to Read These Documents

If you are **new to the project**, start with:
1. `PROJECT_ARCHITECTURE.md` → High-Level System Overview (understand what exists)
2. `WORKFLOW_DIAGRAMS.md` → Authentication Flow (understand how to use the API)
3. `PROJECT_ARCHITECTURE.md` → Request Lifecycle (understand how requests are processed)

If you are **debugging an issue**, go to:
1. `WORKFLOW_DIAGRAMS.md` → Error Handling Flow (match your error code to the layer)
2. `PROJECT_ARCHITECTURE.md` → Request Lifecycle (find which layer caused the error)
3. `WORKFLOW_DIAGRAMS.md` → Monitoring Flow (check Grafana for patterns)

If you are **deploying or doing DevOps**, go to:
1. `WORKFLOW_DIAGRAMS.md` → CI/CD Pipeline (understand the automation)
2. `WORKFLOW_DIAGRAMS.md` → Kubernetes Deployment (understand the resources)
3. `WORKFLOW_DIAGRAMS.md` → Docker Build (understand the image)

If you are **working on the ML pipeline**, go to:
1. `WORKFLOW_DIAGRAMS.md` → ML Training Pipeline (understand the stages)
2. `PROJECT_ARCHITECTURE.md` → ML Training Pipeline (see the config sources)
3. `PROJECT_ARCHITECTURE.md` → Configuration Sources (find where params live)
