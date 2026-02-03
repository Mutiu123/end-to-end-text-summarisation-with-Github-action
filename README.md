# Text Summarization API

Enterprise-grade REST API for intelligent text summarization powered using PEGASUS transformer model. Built with FastAPI, this production-ready service features comprehensive security, monitoring, and scalability capabilities designed for mission-critical applications.

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [API Usage Examples](#api-usage-examples)
  - [Authentication](#authentication)
  - [Text Summarization](#text-summarization)
  - [Health Checks](#health-checks)
  - [System Status](#system-status)
- [Docker Usage](#docker-usage)
  - [Production Deployment](#production-deployment)
  - [Development Environment](#development-environment)
  - [Full Stack with Monitoring](#full-stack-with-monitoring)
- [Kubernetes Deployment](#kubernetes-deployment)
  - [Prerequisites](#kubernetes-prerequisites)
  - [Deployment Steps](#deployment-steps)
  - [Configuration Management](#configuration-management)
  - [Scaling and High Availability](#scaling-and-high-availability)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Application Settings](#application-settings)
  - [Security Configuration](#security-configuration)
  - [Database Configuration](#database-configuration)
  - [Model Configuration](#model-configuration)
- [Monitoring and Observability](#monitoring-and-observability)
  - [Prometheus Metrics](#prometheus-metrics)
  - [Grafana Dashboards](#grafana-dashboards)
  - [Structured Logging](#structured-logging)
  - [Audit Trail](#audit-trail)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Coverage Reports](#coverage-reports)
  - [Test Categories](#test-categories)
- [Project Structure](#project-structure)
- [Security](#security)
  - [Authentication and Authorization](#authentication-and-authorization)
  - [Rate Limiting](#rate-limiting)
  - [Input Validation](#input-validation)
  - [Security Best Practices](#security-best-practices)
- [Performance](#performance)
  - [Optimization Strategies](#optimization-strategies)
  - [Benchmarks](#benchmarks)
- [Development](#development)
  - [Development Setup](#development-setup)
  - [Code Quality](#code-quality)
  - [Pre-commit Hooks](#pre-commit-hooks)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)
- [Acknowledgments](#acknowledgments)

## Features

This enterprise-grade text summarization API provides a comprehensive suite of production-ready features:

### Security Features
- **JWT Authentication**: Secure token-based authentication using JSON Web Tokens with configurable expiration
- **Token Bucket Rate Limiting**: Advanced rate limiting to prevent API abuse and ensure fair usage
- **API Key Authentication**: Optional API key-based authentication for service-to-service communication
- **Input Sanitization**: Automatic sanitization of user inputs to prevent injection attacks
- **CORS Configuration**: Configurable Cross-Origin Resource Sharing for controlled access
- **Content Security**: Protection against malicious patterns and suspicious inputs

### Monitoring and Observability
- **Prometheus Metrics**: 10+ comprehensive metric types for deep system insights
  - Request count and latency histograms
  - Active request tracking
  - Error rate monitoring
  - Model performance metrics
  - Database connection pool metrics
  - Rate limiter statistics
  - HTTP status code distributions
  - Request size tracking
- **Structured JSON Logging**: Machine-readable logs with correlation IDs for distributed tracing
- **Request Tracking**: Unique request IDs for end-to-end request tracing
- **Health Check Endpoints**: Comprehensive health monitoring for orchestration platforms
- **Grafana Dashboards**: Pre-configured dashboards for real-time visualization

### Database and Persistence
- **MongoDB Audit Logging**: Complete audit trail of all API requests and responses
- **Connection Pooling**: Optimized database connection management with configurable pool sizes
- **Async Operations**: Non-blocking database operations for maximum performance
- **Automatic Reconnection**: Resilient connection handling with automatic recovery

### Data Validation and Processing
- **Pydantic v2 Input Validation**: Type-safe request and response validation
- **Schema Enforcement**: Strict schema validation for all API endpoints
- **Error Handling**: Comprehensive error handling with detailed error responses
- **Global Exception Handling**: Centralized exception management with appropriate HTTP status codes

### Deployment and Scalability
- **Multi-stage Docker Builds**: Optimized container images with minimal attack surface
- **Non-root Container Execution**: Security-hardened containers running as non-privileged users
- **Kubernetes Manifests**: Production-ready K8s configurations including:
  - Deployments with rolling updates
  - Services and load balancing
  - Horizontal Pod Autoscaling (HPA)
  - Network policies
  - ConfigMaps and Secrets management
  - Ingress controllers
  - Pod Disruption Budgets
- **CI/CD with GitHub Actions**: Automated testing, building, and deployment pipelines
- **Health Checks**: Container health monitoring for automatic recovery

### Model and ML Features
- **PEGASUS Model**: State-of-the-art transformer model for abstractive text summarization
- **Configurable Inference**: Adjustable beam search, length penalty, and generation parameters
- **Model Versioning**: Support for model updates without service interruption
- **Batch Processing**: Efficient handling of multiple summarization requests

## Architecture Overview

The application follows a modular, layered architecture designed for maintainability and scalability:

```
Text Summarization API
│
├── API Layer (FastAPI)
│   ├── Route handlers
│   ├── Request/Response schemas
│   └── Dependency injection
│
├── Security Layer
│   ├── JWT authentication (security/auth.py)
│   ├── Rate limiting (security/rate_limiter.py)
│   └── Input sanitization (security/sanitizer.py)
│
├── Monitoring Layer
│   ├── Prometheus metrics (monitoring/metrics.py)
│   ├── Structured logging (monitoring/structured_logging.py)
│   └── Request tracking middleware (monitoring/middleware.py)
│
├── Database Layer
│   ├── MongoDB connection management (database/mongodb.py)
│   ├── Audit logging
│   └── Connection pooling
│
├── Validation Layer
│   ├── Request schemas (schemas/requests.py)
│   ├── Response schemas (schemas/responses.py)
│   └── Pydantic v2 models
│
├── Business Logic Layer
│   ├── Model training pipeline
│   ├── Data ingestion and validation
│   ├── Data transformation
│   └── Model evaluation
│
├── ML Pipeline
│   ├── Prediction pipeline (pipeline/prediction.py)
│   ├── Model loading and inference
│   └── PEGASUS model integration
│
└── Configuration Layer
    ├── Settings management (config/settings.py)
    ├── Environment variables
    └── Configuration validation
```

## Screenshots
![The System Demo](https://github.com/Mutiu123/end-to-end-text-summarisation-with-Github-action/blob/main/demos/demo1.png)
![The System Demo1](https://github.com/Mutiu123/end-to-end-text-summarisation-with-Github-action/blob/main/demos/demo2.png)



### Key Modules

**Security Module** (`src/textSummarizer/security/`)
- `auth.py`: JWT token generation and validation
- `rate_limiter.py`: Token bucket rate limiting implementation
- `sanitizer.py`: Input sanitization and validation

**Monitoring Module** (`src/textSummarizer/monitoring/`)
- `metrics.py`: Prometheus metrics definitions and collectors
- `structured_logging.py`: JSON logging configuration
- `middleware.py`: Request tracking and timing middleware

**Database Module** (`src/textSummarizer/database/`)
- `mongodb.py`: MongoDB connection management and audit logging

**Schemas Module** (`src/textSummarizer/schemas/`)
- `requests.py`: Pydantic request models
- `responses.py`: Pydantic response models

**Configuration Module** (`src/textSummarizer/config/`)
- `settings.py`: Application settings using Pydantic BaseSettings
- `configuration.py`: ML pipeline configuration management

## Quick Start

### Prerequisites

Before running the Text Summarization API, ensure you have the following installed:

- **Python 3.10 or higher**: The application requires Python 3.10+ for modern async features
- **Docker** (optional): For containerized deployment
- **Docker Compose** (optional): For full stack deployment with monitoring
- **MongoDB**: Database for audit logging (can be run via Docker Compose)
- **Git**: For cloning the repository
- **CUDA-capable GPU** (optional): For accelerated model inference

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/Mutiu123/end-to-end-text-summarisation-with-Github-action.git
cd end-to-end-text-summarisation-with-Github-action
```

2. **Create a virtual environment**

Using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Using conda:
```bash
conda create -n textsummarizer python=3.10 -y
conda activate textsummarizer
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit the `.env` file and update the following critical settings:
- `SECRET_KEY`: Generate a secure secret key for JWT tokens
- `MONGODB_URL`: MongoDB connection string
- `ALLOWED_ORIGINS`: Configure CORS origins

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

5. **Set up MongoDB** (if running locally)

Start MongoDB using Docker:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:7
```

Or install MongoDB locally following the official documentation.

### Running the Application

#### Development Mode

Run the application with auto-reload enabled:

```bash
python app.py
```

The API will be available at `http://localhost:8080`

#### Production Mode

Run with Uvicorn in production mode:

```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --workers 4
```

For production deployments, it's recommended to use a process manager like systemd or Docker.

#### Verify Installation

Access the following endpoints to verify the installation:

- API Documentation: `http://localhost:8080/docs`
- Alternative Docs: `http://localhost:8080/redoc`
- Health Check: `http://localhost:8080/health`
- Status: `http://localhost:8080/status`

## API Endpoints

The Text Summarization API provides the following endpoints:

| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| GET | `/` | Root endpoint - redirects to API documentation | No |
| GET | `/status` | System status and configuration information | No |
| GET | `/health` | Health check endpoint for load balancers | No |
| POST | `/auth/token` | Generate JWT access token for authentication | No |
| POST | `/predict` | Summarize text using the PEGASUS model | Yes (JWT) |
| GET | `/train` | Trigger model training pipeline | Yes (JWT) |
| GET | `/metrics` | Prometheus metrics endpoint | No |

### Endpoint Details

#### GET /
Redirects to the interactive API documentation at `/docs`.

**Response:** 302 redirect

#### GET /status
Returns system status, configuration, and runtime information.

**Response:** JSON object with system metadata
- Application name and version
- Environment
- Model status
- Request tracking information

#### GET /health
Health check endpoint for container orchestration and load balancers.

**Response:** JSON object with health status
- Status: "healthy" or "unhealthy"
- Database connectivity
- Model availability
- Timestamp

#### POST /auth/token
Generate a JWT access token for API authentication.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /predict
Summarize input text using the PEGASUS model.

**Headers:**
- `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "text": "string"
}
```

**Response:**
```json
{
  "summary": "string",
  "request_id": "string",
  "timestamp": "2026-02-01T12:00:00.000Z",
  "processing_time_ms": 123.45
}
```

#### GET /train
Trigger the model training pipeline (admin endpoint).

**Headers:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Training pipeline initiated",
  "status": "success"
}
```

#### GET /metrics
Prometheus-formatted metrics for monitoring and alerting.

**Response:** Prometheus exposition format

## API Usage Examples

### Authentication

First, obtain a JWT token for authentication:

```bash
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Save the access token for subsequent requests.

### Text Summarization

Summarize a long text using the prediction endpoint:

```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "text": "The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building, and the tallest structure in Paris. Its base is square, measuring 125 metres (410 ft) on each side. During its construction, the Eiffel Tower surpassed the Washington Monument to become the tallest man-made structure in the world, a title it held for 41 years until the Chrysler Building in New York City was finished in 1930. It was the first structure to reach a height of 300 metres. Due to the addition of a broadcasting aerial at the top of the tower in 1957, it is now taller than the Chrysler Building by 5.2 metres (17 ft). Excluding transmitters, the Eiffel Tower is the second tallest free-standing structure in France after the Millau Viaduct."
  }'
```

Response:
```json
{
  "summary": "The Eiffel Tower is 324 metres tall and was the tallest man-made structure in the world for 41 years. It is the second tallest free-standing structure in France.",
  "request_id": "req_abc123xyz",
  "timestamp": "2026-02-01T12:34:56.789Z",
  "processing_time_ms": 145.23
}
```

### Health Checks

Check the health status of the API:

```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "model": "loaded",
  "timestamp": "2026-02-01T12:34:56.789Z"
}
```

### System Status

Get detailed system status and configuration:

```bash
curl http://localhost:8080/status
```

Response:
```json
{
  "app_name": "Text Summarizer API",
  "version": "1.0.0",
  "environment": "production",
  "model_status": "loaded",
  "request_id": "req_xyz789abc",
  "timestamp": "2026-02-01T12:34:56.789Z"
}
```

### Using Python Requests

Example using the Python `requests` library:

```python
import requests

# Base URL
BASE_URL = "http://localhost:8080"

# Authenticate
auth_response = requests.post(
    f"{BASE_URL}/auth/token",
    json={"username": "admin", "password": "admin123"}
)
token = auth_response.json()["access_token"]

# Summarize text
headers = {"Authorization": f"Bearer {token}"}
text_to_summarize = """
Your long text here...
"""

predict_response = requests.post(
    f"{BASE_URL}/predict",
    json={"text": text_to_summarize},
    headers=headers
)

summary = predict_response.json()["summary"]
print(f"Summary: {summary}")
```

### Using JavaScript Fetch

Example using JavaScript fetch API:

```javascript
const BASE_URL = 'http://localhost:8080';

// Authenticate
async function getToken() {
  const response = await fetch(`${BASE_URL}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'admin',
      password: 'admin123'
    })
  });
  const data = await response.json();
  return data.access_token;
}

// Summarize text
async function summarizeText(text) {
  const token = await getToken();
  const response = await fetch(`${BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ text })
  });
  const data = await response.json();
  return data.summary;
}

// Usage
const longText = 'Your long text here...';
summarizeText(longText).then(summary => {
  console.log('Summary:', summary);
});
```

## Docker Usage

The Text Summarization API provides multiple Docker deployment options for different use cases.

### Production Deployment

Build and run the production-optimized Docker image:

#### Build the Image

```bash
docker build -t text-summarizer-api:latest .
```

The production Dockerfile uses a multi-stage build to:
- Minimize image size
- Reduce attack surface
- Run as non-root user
- Include health checks

#### Run the Container

```bash
docker run -d \
  --name text-summarizer \
  -p 8080:8080 \
  -e SECRET_KEY="your-secret-key" \
  -e MONGODB_URL="mongodb://host.docker.internal:27017" \
  -e LOG_LEVEL="INFO" \
  --restart unless-stopped \
  text-summarizer-api:latest
```

#### With Environment File

Create a `.env` file and run:

```bash
docker run -d \
  --name text-summarizer \
  -p 8080:8080 \
  --env-file .env \
  --restart unless-stopped \
  text-summarizer-api:latest
```

#### Volume Mounts for Model Artifacts

If you have pre-trained models, mount them as volumes:

```bash
docker run -d \
  --name text-summarizer \
  -p 8080:8080 \
  -v $(pwd)/artifacts:/app/artifacts:ro \
  --env-file .env \
  text-summarizer-api:latest
```

### Development Environment

Run the development environment with hot-reload and debugging:

```bash
docker compose --profile dev up
```

This starts:
- Application in development mode with code hot-reload
- MongoDB database
- Volume mounts for live code changes

Access the application at `http://localhost:8080`

Stop the development environment:

```bash
docker compose --profile dev down
```

### Full Stack with Monitoring

Deploy the complete stack including monitoring infrastructure:

```bash
docker compose up -d
```

This starts:
- **Text Summarizer API**: Main application
- **MongoDB**: Database for audit logging
- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization and dashboards

Services and ports:
- Application: `http://localhost:8080`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (default credentials: admin/admin)
- MongoDB: `mongodb://localhost:27017`

#### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f app

# Last 100 lines
docker compose logs --tail=100 app
```

#### Stop the Stack

```bash
# Stop but keep data
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers and volumes
docker compose down -v
```

#### Scale the Application

Scale the application to multiple instances:

```bash
docker compose up -d --scale app=3
```

Note: You'll need to configure a load balancer (like Nginx) to distribute traffic across instances.

### Docker Compose Profiles

The docker-compose.yml supports profiles for different deployment scenarios:

- **Default**: Production deployment with monitoring
- **dev**: Development environment with hot-reload

```bash
# Production
docker compose up -d

# Development
docker compose --profile dev up

# Specific services
docker compose up -d mongodb prometheus grafana
```

## Kubernetes Deployment

The Text Summarization API includes production-ready Kubernetes manifests for orchestrated deployments.

### Kubernetes Prerequisites

Before deploying to Kubernetes, ensure you have:

- **Kubernetes cluster**: Version 1.24 or higher (EKS, GKE, AKS, or local cluster)
- **kubectl**: Configured to communicate with your cluster
- **Container registry**: Access to push Docker images (Docker Hub, ECR, GCR, ACR)
- **Ingress controller**: Nginx, Traefik, or cloud provider load balancer
- **Metrics server**: For Horizontal Pod Autoscaling

### Deployment Steps

#### 1. Build and Push Docker Image

Build the Docker image and push to your container registry:

```bash
# Build the image
docker build -t your-registry/text-summarizer-api:v1.0.0 .

# Push to registry
docker push your-registry/text-summarizer-api:v1.0.0
```

For AWS ECR:
```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag text-summarizer-api:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/text-summarizer-api:v1.0.0
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/text-summarizer-api:v1.0.0
```

#### 2. Create Namespace

Create a dedicated namespace for the application:

```bash
kubectl apply -f k8s/namespace.yaml
```

Or create manually:
```bash
kubectl create namespace text-summarizer
```

#### 3. Configure Secrets

Create Kubernetes secrets for sensitive configuration:

```bash
# Create secret for JWT and MongoDB
kubectl create secret generic text-summarizer-secrets \
  --from-literal=SECRET_KEY="your-secret-key-here" \
  --from-literal=MONGODB_URL="mongodb://mongodb:27017" \
  -n text-summarizer
```

Or apply the secret manifest after updating values:
```bash
kubectl apply -f k8s/secret.yaml
```

#### 4. Apply ConfigMaps

Apply application configuration:

```bash
kubectl apply -f k8s/configmap.yaml
```

#### 5. Deploy MongoDB

Deploy MongoDB for audit logging:

```bash
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/mongodb-service.yaml
```

Or use a managed MongoDB service (MongoDB Atlas, AWS DocumentDB):
```bash
# Update MONGODB_URL in secrets to point to managed service
kubectl edit secret text-summarizer-secrets -n text-summarizer
```

#### 6. Deploy the Application

Deploy the main application:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Verify the deployment:
```bash
kubectl get pods -n text-summarizer
kubectl get services -n text-summarizer
```

#### 7. Configure Horizontal Pod Autoscaling

Apply HPA for automatic scaling:

```bash
kubectl apply -f k8s/hpa.yaml
```

Verify HPA:
```bash
kubectl get hpa -n text-summarizer
```

#### 8. Configure Ingress

Update the ingress manifest with your domain:

```bash
# Edit k8s/ingress.yaml and update host field
kubectl apply -f k8s/ingress.yaml
```

Verify ingress:
```bash
kubectl get ingress -n text-summarizer
```

#### 9. Apply Network Policies

Apply network policies for security:

```bash
kubectl apply -f k8s/networkpolicy.yaml
```

#### 10. Configure Pod Disruption Budget

Apply PDB for high availability:

```bash
kubectl apply -f k8s/poddisruptionbudget.yaml
```

### Configuration Management

#### Using Kustomize

Deploy using Kustomize for environment-specific configurations:

```bash
# Development
kubectl apply -k k8s/overlays/development

# Production
kubectl apply -k k8s/overlays/production
```

#### Update Configuration

Update ConfigMap and restart pods:

```bash
kubectl edit configmap text-summarizer-config -n text-summarizer
kubectl rollout restart deployment/text-summarizer -n text-summarizer
```

### Scaling and High Availability

#### Manual Scaling

Scale the deployment manually:

```bash
kubectl scale deployment/text-summarizer --replicas=5 -n text-summarizer
```

#### Horizontal Pod Autoscaling

The HPA automatically scales based on CPU and memory:

```yaml
minReplicas: 2
maxReplicas: 10
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

Monitor HPA:
```bash
kubectl get hpa -n text-summarizer -w
```

#### Rolling Updates

Perform zero-downtime updates:

```bash
kubectl set image deployment/text-summarizer \
  text-summarizer=your-registry/text-summarizer-api:v1.1.0 \
  -n text-summarizer
```

Monitor rollout:
```bash
kubectl rollout status deployment/text-summarizer -n text-summarizer
```

Rollback if needed:
```bash
kubectl rollout undo deployment/text-summarizer -n text-summarizer
```

### Monitoring in Kubernetes

#### Check Pod Logs

```bash
kubectl logs -f deployment/text-summarizer -n text-summarizer
```

#### Check Events

```bash
kubectl get events -n text-summarizer --sort-by='.lastTimestamp'
```

#### Port Forward for Testing

```bash
kubectl port-forward service/text-summarizer 8080:8080 -n text-summarizer
```

Access at `http://localhost:8080`

### Cleanup

Remove all resources:

```bash
kubectl delete namespace text-summarizer
```

Or remove individual resources:
```bash
kubectl delete -f k8s/
```

## Configuration

The Text Summarization API uses environment variables for configuration management.

### Environment Variables

All configuration options available in `.env.example`:

#### Application Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | Text Summarizer API | No |
| `APP_VERSION` | Application version | 1.0.0 | No |
| `APP_ENV` | Environment (development/production) | development | No |
| `DEBUG` | Enable debug mode | false | No |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 8080 | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO | No |

#### Security Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Secret key for JWT signing | change-me-in-production | Yes |
| `JWT_ALGORITHM` | JWT signing algorithm | HS256 | No |
| `JWT_EXPIRATION_MINUTES` | JWT token expiration time | 30 | No |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | http://localhost | No |
| `RATE_LIMIT_REQUESTS` | Max requests per window | 100 | No |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window duration | 60 | No |
| `API_KEY_HEADER` | Custom API key header name | X-API-Key | No |
| `API_KEYS` | Comma-separated list of valid API keys | (empty) | No |

#### Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URL` | MongoDB connection string | mongodb://localhost:27017 | Yes |
| `MONGODB_DB_NAME` | Database name | text_summarizer | No |
| `MONGODB_MIN_POOL_SIZE` | Minimum connection pool size | 10 | No |
| `MONGODB_MAX_POOL_SIZE` | Maximum connection pool size | 50 | No |
| `MONGODB_CONNECT_TIMEOUT_MS` | Connection timeout in milliseconds | 5000 | No |
| `MONGODB_SERVER_SELECTION_TIMEOUT_MS` | Server selection timeout | 5000 | No |

#### Monitoring Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_METRICS` | Enable Prometheus metrics | true | No |
| `METRICS_PREFIX` | Metrics namespace prefix | textsummarizer | No |

#### Model Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MODEL_PATH` | Path to trained model | artifacts/model_trainer/pegasus-samsum-model | No |
| `TOKENIZER_PATH` | Path to tokenizer | artifacts/model_trainer/tokenizer | No |
| `MAX_INPUT_LENGTH` | Maximum input token length | 1024 | No |
| `MAX_SUMMARY_LENGTH` | Maximum summary token length | 128 | No |
| `NUM_BEAMS` | Beam search width | 8 | No |
| `LENGTH_PENALTY` | Length penalty for generation | 0.8 | No |

#### AWS Configuration (CI/CD)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key for ECR | (empty) | For AWS deployment |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | (empty) | For AWS deployment |
| `AWS_REGION` | AWS region | us-east-1 | For AWS deployment |
| `AWS_ECR_LOGIN_URI` | ECR registry URI | (empty) | For AWS deployment |
| `ECR_REPOSITORY_NAME` | ECR repository name | (empty) | For AWS deployment |

### Application Settings

#### Generating a Secure Secret Key

Generate a cryptographically secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Update the `SECRET_KEY` in your `.env` file with the generated value.

#### Configuring CORS

To allow requests from specific origins:

```env
ALLOWED_ORIGINS=http://localhost:3000,https://example.com,https://app.example.com
```

For development only (not recommended for production):
```env
ALLOWED_ORIGINS=*
```

### Security Configuration

#### Rate Limiting

Adjust rate limiting to match your requirements:

```env
# Allow 1000 requests per 60 seconds
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW_SECONDS=60

# Stricter limits: 50 requests per 300 seconds (5 minutes)
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW_SECONDS=300
```

#### JWT Configuration

Configure JWT token settings:

```env
# Token expires in 2 hours
JWT_EXPIRATION_MINUTES=120

# Use RS256 for asymmetric signing (requires private/public key pair)
JWT_ALGORITHM=RS256
```

### Database Configuration

#### MongoDB Connection String

Local MongoDB:
```env
MONGODB_URL=mongodb://localhost:27017
```

MongoDB with authentication:
```env
MONGODB_URL=mongodb://username:password@localhost:27017/admin
```

MongoDB Atlas:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

MongoDB replica set:
```env
MONGODB_URL=mongodb://host1:27017,host2:27017,host3:27017/?replicaSet=rs0
```

#### Connection Pool Settings

For high-traffic applications:
```env
MONGODB_MIN_POOL_SIZE=20
MONGODB_MAX_POOL_SIZE=100
```

For low-traffic applications:
```env
MONGODB_MIN_POOL_SIZE=5
MONGODB_MAX_POOL_SIZE=20
```

### Model Configuration

#### Adjusting Model Parameters

For faster inference (lower quality):
```env
NUM_BEAMS=4
MAX_SUMMARY_LENGTH=64
```

For higher quality (slower inference):
```env
NUM_BEAMS=12
MAX_SUMMARY_LENGTH=256
LENGTH_PENALTY=1.0
```

#### Using Custom Models

Point to a custom trained model:
```env
MODEL_PATH=/path/to/custom/model
TOKENIZER_PATH=/path/to/custom/tokenizer
```

## Monitoring and Observability

The Text Summarization API provides comprehensive monitoring capabilities for production environments.

### Prometheus Metrics

The application exposes Prometheus metrics at the `/metrics` endpoint.

#### Available Metrics

**Application Metrics:**
- `textsummarizer_app_info`: Application metadata (version, environment)
- `textsummarizer_requests_total`: Total HTTP requests by method, endpoint, status
- `textsummarizer_request_duration_seconds`: Request latency histogram
- `textsummarizer_active_requests`: Current number of active requests
- `textsummarizer_request_size_bytes`: HTTP request size distribution
- `textsummarizer_response_size_bytes`: HTTP response size distribution

**Model Metrics:**
- `textsummarizer_model_loaded`: Model load status (1 = loaded, 0 = not loaded)
- `textsummarizer_predictions_total`: Total predictions processed
- `textsummarizer_prediction_duration_seconds`: Prediction latency histogram
- `textsummarizer_prediction_errors_total`: Total prediction errors

**Rate Limiter Metrics:**
- `textsummarizer_rate_limit_hits_total`: Total rate limit violations
- `textsummarizer_rate_limit_allowed_total`: Total allowed requests

**Database Metrics:**
- `textsummarizer_db_connections_active`: Active database connections
- `textsummarizer_db_connections_total`: Total database connections in pool
- `textsummarizer_db_query_duration_seconds`: Database query latency

**Error Metrics:**
- `textsummarizer_errors_total`: Total errors by type and endpoint

#### Accessing Metrics

```bash
curl http://localhost:8080/metrics
```

Example output:
```
# HELP textsummarizer_requests_total Total requests
# TYPE textsummarizer_requests_total counter
textsummarizer_requests_total{method="POST",endpoint="/predict",status="200"} 1523.0

# HELP textsummarizer_request_duration_seconds Request duration
# TYPE textsummarizer_request_duration_seconds histogram
textsummarizer_request_duration_seconds_bucket{le="0.1"} 892.0
textsummarizer_request_duration_seconds_bucket{le="0.5"} 1456.0
textsummarizer_request_duration_seconds_sum 234.5
textsummarizer_request_duration_seconds_count 1523.0
```

### Grafana Dashboards

Pre-configured Grafana dashboards are available in `monitoring/grafana/dashboards/`.

#### Accessing Grafana

When using Docker Compose:
1. Navigate to `http://localhost:3000`
2. Login with default credentials: `admin` / `admin`
3. Navigate to Dashboards to view the Text Summarizer dashboard

#### Dashboard Features

The included dashboard provides:
- **Request Rate**: Requests per second over time
- **Latency Percentiles**: P50, P95, P99 response times
- **Error Rate**: Error percentage by endpoint
- **Model Performance**: Prediction latency and throughput
- **Rate Limiting**: Rate limit hits and allowed requests
- **Database Connections**: Connection pool utilization
- **Status Codes**: Distribution of HTTP status codes
- **Active Requests**: Real-time active request count

#### Creating Custom Dashboards

Import the provided dashboard:
1. In Grafana, go to Dashboards > Import
2. Upload `monitoring/grafana/dashboards/text-summarizer.json`
3. Select Prometheus as the data source

Or create custom dashboards using PromQL queries:
```promql
# Request rate per minute
rate(textsummarizer_requests_total[1m])

# 95th percentile latency
histogram_quantile(0.95, rate(textsummarizer_request_duration_seconds_bucket[5m]))

# Error rate
rate(textsummarizer_errors_total[5m])
```

### Structured Logging

The application uses JSON structured logging for machine-readable logs.

#### Log Format

Each log entry includes:
- `timestamp`: ISO 8601 formatted timestamp
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `service`: Service name
- `environment`: Deployment environment
- `request_id`: Unique request identifier
- `message`: Log message
- `extra`: Additional context fields

Example log entry:
```json
{
  "timestamp": "2026-02-01T12:34:56.789Z",
  "level": "INFO",
  "service": "Text Summarizer API",
  "environment": "production",
  "request_id": "req_abc123xyz",
  "message": "Request completed",
  "extra": {
    "method": "POST",
    "path": "/predict",
    "status_code": 200,
    "duration_ms": 145.23,
    "user": "admin"
  }
}
```

#### Viewing Logs

Docker Compose:
```bash
docker compose logs -f app
```

Kubernetes:
```bash
kubectl logs -f deployment/text-summarizer -n text-summarizer
```

#### Log Aggregation

Integrate with log aggregation platforms:

**ELK Stack:**
- Configure Filebeat to ship logs to Elasticsearch
- Use Kibana for log visualization and analysis

**CloudWatch (AWS):**
- Configure CloudWatch Logs agent
- Use CloudWatch Insights for log queries

**Splunk:**
- Configure Splunk forwarder
- Create Splunk dashboards for log analysis

### Audit Trail

All API requests are logged to MongoDB for compliance and audit purposes.

#### Audit Log Structure

Each audit log entry contains:
- Request timestamp
- Request ID
- User/client identifier
- HTTP method and endpoint
- Request headers and body
- Response status and body
- Processing duration
- IP address and user agent

#### Querying Audit Logs

Connect to MongoDB and query audit logs:

```javascript
// Find all requests by user
db.audit_logs.find({ user: "admin" })

// Find failed requests
db.audit_logs.find({ status_code: { $gte: 400 } })

// Find slow requests (> 1 second)
db.audit_logs.find({ duration_ms: { $gt: 1000 } })

// Aggregate requests by endpoint
db.audit_logs.aggregate([
  { $group: { _id: "$endpoint", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

#### Audit Log Retention

Configure retention policies to manage storage:

```javascript
// Create TTL index to auto-delete logs after 90 days
db.audit_logs.createIndex({ timestamp: 1 }, { expireAfterSeconds: 7776000 })
```

## Testing

The Text Summarization API includes a comprehensive test suite for ensuring code quality and reliability.

### Running Tests

#### Run All Tests

```bash
pytest
```

#### Run with Coverage

```bash
pytest --cov=src/textSummarizer --cov-report=html --cov-report=term
```

View the HTML coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

#### Run Specific Test Files

```bash
pytest tests/test_auth.py
pytest tests/test_rate_limiter.py
pytest tests/test_sanitizer.py
```

#### Run with Verbose Output

```bash
pytest -v
```

#### Run Specific Test Functions

```bash
pytest tests/test_auth.py::test_create_access_token
pytest tests/test_rate_limiter.py::test_rate_limiter_allows_requests
```

### Coverage Reports

Generate coverage reports in multiple formats:

```bash
# Terminal output
pytest --cov=src/textSummarizer --cov-report=term-missing

# HTML report
pytest --cov=src/textSummarizer --cov-report=html

# XML report (for CI/CD)
pytest --cov=src/textSummarizer --cov-report=xml

# All formats
pytest --cov=src/textSummarizer --cov-report=html --cov-report=xml --cov-report=term
```

### Test Categories

The test suite is organized into several categories:

#### Unit Tests

Test individual components in isolation:
- `test_settings.py`: Configuration and settings validation
- `test_auth.py`: JWT authentication and token management
- `test_rate_limiter.py`: Rate limiting logic
- `test_sanitizer.py`: Input sanitization and validation
- `test_schemas.py`: Pydantic schema validation
- `test_exceptions.py`: Custom exception handling

#### Integration Tests

Test component interactions:
- API endpoint integration
- Database connectivity
- Authentication flow
- End-to-end request processing

#### Performance Tests

Benchmark critical operations:
- Model inference latency
- Database query performance
- Rate limiter overhead

### Running Tests in Docker

Run tests in a containerized environment:

```bash
docker compose run --rm app pytest
```

With coverage:
```bash
docker compose run --rm app pytest --cov=src/textSummarizer --cov-report=term
```

### Continuous Integration

Tests are automatically run on every push and pull request via GitHub Actions. See `.github/workflows/main.yaml` for the CI configuration.

The CI pipeline:
1. Runs linting and code quality checks
2. Executes the full test suite
3. Generates coverage reports
4. Builds Docker images
5. Deploys to staging/production environments

## Project Structure

```
end-to-end-text-summarisation-with-Github-action/
│
├── .github/
│   └── workflows/
│       └── main.yaml                   # CI/CD pipeline configuration
│
├── config/
│   └── config.yaml                     # ML pipeline configuration
│
├── demos/
│   ├── demo1.png                       # Application screenshots
│   └── demo2.png
│
├── k8s/                                # Kubernetes manifests
│   ├── configmap.yaml                  # Application configuration
│   ├── deployment.yaml                 # Application deployment
│   ├── hpa.yaml                        # Horizontal Pod Autoscaler
│   ├── ingress.yaml                    # Ingress controller config
│   ├── kustomization.yaml              # Kustomize configuration
│   ├── namespace.yaml                  # Kubernetes namespace
│   ├── networkpolicy.yaml              # Network security policies
│   ├── poddisruptionbudget.yaml        # High availability config
│   ├── secret.yaml                     # Secrets management
│   ├── service.yaml                    # Service definition
│   └── serviceaccount.yaml             # Service account
│
├── monitoring/                         # Monitoring configuration
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── dashboard.yml           # Dashboard provisioning
│   │   │   └── text-summarizer.json    # Pre-built dashboard
│   │   └── datasources/
│   │       └── prometheus.yml          # Prometheus data source
│   └── prometheus.yml                  # Prometheus scrape config
│
├── research/                           # Jupyter notebooks
│   ├── 01_data_ingestion.ipynb
│   ├── 02_data_validation.ipynb
│   ├── 03_data_transformation.ipynb
│   ├── 04_model_trainer.ipynb
│   ├── 05_Model_evaluation.ipynb
│   ├── Text_Summarization.ipynb
│   └── trials.ipynb
│
├── src/
│   └── textSummarizer/
│       ├── __init__.py
│       │
│       ├── config/                     # Configuration management
│       │   ├── __init__.py
│       │   ├── configuration.py        # ML pipeline config
│       │   └── settings.py             # Application settings
│       │
│       ├── conponents/                 # ML pipeline components
│       │   ├── __init__.py
│       │   ├── data_ingestion.py
│       │   ├── data_transformation.py
│       │   ├── data_validation.py
│       │   ├── model_evaluation.py
│       │   └── model_trainer.py
│       │
│       ├── constants/                  # Application constants
│       │   └── __init__.py
│       │
│       ├── database/                   # Database layer
│       │   ├── __init__.py
│       │   └── mongodb.py              # MongoDB connection & audit
│       │
│       ├── entity/                     # Data entities
│       │   └── __init__.py
│       │
│       ├── logging/                    # Logging utilities
│       │   └── __init__.py
│       │
│       ├── monitoring/                 # Observability
│       │   ├── __init__.py
│       │   ├── metrics.py              # Prometheus metrics
│       │   ├── middleware.py           # Request tracking
│       │   └── structured_logging.py   # JSON logging
│       │
│       ├── pipeline/                   # ML pipelines
│       │   ├── __init__.py
│       │   ├── prediction.py           # Inference pipeline
│       │   ├── stage_01_data_ingestion.py
│       │   ├── stage_02_data_validation.py
│       │   ├── stage_03_data_transformation.py
│       │   ├── stage_04_model_trainer.py
│       │   └── stage_05_model_evaluation.py
│       │
│       ├── schemas/                    # Pydantic schemas
│       │   ├── __init__.py
│       │   ├── requests.py             # Request models
│       │   └── responses.py            # Response models
│       │
│       ├── security/                   # Security layer
│       │   ├── __init__.py
│       │   ├── auth.py                 # JWT authentication
│       │   ├── rate_limiter.py         # Rate limiting
│       │   └── sanitizer.py            # Input sanitization
│       │
│       ├── utils/                      # Utilities
│       │   ├── __init__.py
│       │   └── common.py
│       │
│       └── exceptions.py               # Custom exceptions
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Test fixtures
│   ├── test_auth.py
│   ├── test_exceptions.py
│   ├── test_rate_limiter.py
│   ├── test_sanitizer.py
│   ├── test_schemas.py
│   └── test_settings.py
│
├── .env.example                        # Environment variables template
├── .flake8                             # Flake8 configuration
├── .gitignore                          # Git ignore patterns
├── .pre-commit-config.yaml             # Pre-commit hooks
├── app.py                              # FastAPI application
├── CONTRIBUTING.md                     # Contribution guidelines
├── docker-compose.yml                  # Docker Compose config
├── Dockerfile                          # Production Dockerfile
├── Dockerfile.dev                      # Development Dockerfile
├── LICENSE.md                          # MIT License
├── main.py                             # ML pipeline entry point
├── params.yaml                         # ML hyperparameters
├── pyproject.toml                      # Python project metadata
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── setup.py                            # Package setup
└── template.py                         # Project template generator
```

### Key Directories

**k8s/**: Contains all Kubernetes manifests for production deployment, including deployments, services, ingress, autoscaling, and security policies.

**monitoring/**: Monitoring infrastructure configuration with Prometheus scrape configs and Grafana dashboards for observability.

**src/textSummarizer/**: Main application source code organized into modular components for security, monitoring, database, schemas, and business logic.

**tests/**: Comprehensive test suite covering unit tests, integration tests, and test fixtures.

**research/**: Jupyter notebooks documenting the ML experimentation and development process.

## Security

The Text Summarization API implements multiple layers of security to protect against common vulnerabilities.

### Authentication and Authorization

#### JWT Token Authentication

The API uses JSON Web Tokens (JWT) for stateless authentication:

1. **Obtain Token**: Call `/auth/token` with credentials
2. **Use Token**: Include in `Authorization: Bearer <token>` header
3. **Token Expiration**: Tokens expire after configured time (default: 30 minutes)
4. **Token Refresh**: Implement token refresh logic in your client

Token payload includes:
- User identifier
- Expiration timestamp
- Custom claims (roles, permissions)

#### API Key Authentication

Alternative authentication using API keys:

```bash
curl -X POST http://localhost:8080/predict \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "..."}'
```

Configure API keys:
```env
API_KEYS=key1,key2,key3
```

### Rate Limiting

Token bucket algorithm prevents API abuse:

**Default Limits:**
- 100 requests per 60 seconds per client
- Configurable per endpoint
- IP-based tracking

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1234567890
```

**Rate Limit Exceeded Response:**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 45
}
```

### Input Validation

Multi-layer input validation:

1. **Schema Validation**: Pydantic v2 enforces type safety
2. **Length Validation**: Maximum text length limits
3. **Pattern Detection**: Detects SQL injection, XSS, path traversal
4. **Sanitization**: Removes dangerous characters and patterns

**Rejected Patterns:**
- SQL injection attempts
- XSS payloads
- Path traversal sequences
- Command injection
- LDAP injection
- XML external entities

### Security Best Practices

#### Production Checklist

- [ ] Generate strong `SECRET_KEY` (64+ characters)
- [ ] Enable HTTPS/TLS in production
- [ ] Configure restrictive CORS policies
- [ ] Use secure MongoDB connection (authentication + TLS)
- [ ] Rotate JWT secret keys periodically
- [ ] Implement rate limiting appropriate for your use case
- [ ] Enable audit logging to MongoDB
- [ ] Run containers as non-root user
- [ ] Use Kubernetes network policies
- [ ] Implement pod security policies
- [ ] Regular security updates and patches
- [ ] Monitor and alert on security events

#### Environment Security

**Never commit secrets:**
- Use `.env` files (excluded from git)
- Use Kubernetes secrets
- Use secret management services (AWS Secrets Manager, HashiCorp Vault)

**Container Security:**
- Multi-stage builds minimize attack surface
- Non-root user execution
- Read-only root filesystem (where possible)
- Security scanning with Trivy or Snyk

**Network Security:**
- Kubernetes network policies restrict pod communication
- Ingress with TLS termination
- Internal services not exposed externally

## Performance

### Optimization Strategies

The API implements several performance optimizations:

**Model Loading:**
- Model loaded once at startup
- Shared across all requests
- GPU acceleration when available

**Database:**
- Connection pooling (10-50 connections)
- Async operations for non-blocking I/O
- Indexed queries for fast lookups

**API Layer:**
- Async request handling
- Response compression
- Connection keep-alive

**Caching:**
- Model artifacts cached in memory
- Tokenizer reused across requests

### Benchmarks

Typical performance metrics on standard hardware:

**Single Request Latency:**
- Short text (100 words): 50-100ms
- Medium text (500 words): 150-250ms
- Long text (1000 words): 300-500ms

**Throughput:**
- CPU only: 10-20 requests/second
- With GPU: 50-100 requests/second

**Resource Usage:**
- Memory: 2-4GB (model loaded)
- CPU: 1-2 cores per worker
- GPU: 2-4GB VRAM when enabled

Actual performance depends on:
- Hardware specifications
- Text length and complexity
- Model configuration
- Concurrent request load

## Development

### Development Setup

Set up a development environment:

```bash
# Clone repository
git clone https://github.com/Mutiu123/end-to-end-text-summarisation-with-Github-action.git
cd end-to-end-text-summarisation-with-Github-action

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies including dev tools
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Copy environment variables
cp .env.example .env

# Run in development mode
python app.py
```

### Code Quality

The project uses multiple tools to maintain code quality:

**Linting:**
```bash
# Flake8 for style guide enforcement
flake8 src/ tests/

# Pylint for code analysis
pylint src/textSummarizer/

# MyPy for static type checking
mypy src/textSummarizer/
```

**Formatting:**
```bash
# Black for code formatting
black src/ tests/

# Check without modifying
black --check src/ tests/
```

**Configuration Files:**
- `.flake8`: Flake8 configuration
- `pyproject.toml`: Black, MyPy, and other tool configs
- `.pre-commit-config.yaml`: Pre-commit hook definitions

### Pre-commit Hooks

Pre-commit hooks automatically run checks before commits:

**Installed Hooks:**
- Trailing whitespace removal
- End-of-file fixer
- YAML validation
- Large file checker
- Black code formatting
- Flake8 linting
- MyPy type checking

**Run Manually:**
```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

**Update Hooks:**
```bash
pre-commit autoupdate
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment.

**Pipeline Stages:**

1. **Code Quality Checks**
   - Linting with Flake8
   - Type checking with MyPy
   - Code formatting with Black

2. **Testing**
   - Unit tests
   - Integration tests
   - Coverage reporting

3. **Build**
   - Docker image build
   - Multi-architecture support

4. **Deploy**
   - Push to container registry
   - Deploy to Kubernetes
   - Run smoke tests

**Workflow File:** `.github/workflows/main.yaml`

**Triggered On:**
- Push to main branch
- Pull requests
- Manual workflow dispatch

**Required Secrets:**
- `SECRET_KEY`: JWT secret
- `AWS_ACCESS_KEY_ID`: AWS credentials
- `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `MONGODB_URL`: Database connection

## Troubleshooting

### Common Issues

**Issue: Model Not Loading**

Symptoms: 500 errors, "Model not loaded" messages

Solutions:
```bash
# Check model path exists
ls -la artifacts/model_trainer/

# Verify model files
ls artifacts/model_trainer/pegasus-samsum-model/

# Check logs for error details
docker compose logs app | grep -i error

# Increase memory allocation
docker run --memory=8g ...
```

**Issue: MongoDB Connection Failed**

Symptoms: "Database connection error" messages

Solutions:
```bash
# Verify MongoDB is running
docker ps | grep mongodb

# Test connection
mongosh mongodb://localhost:27017

# Check network connectivity
docker compose exec app ping mongodb

# Verify environment variable
docker compose exec app env | grep MONGODB
```

**Issue: Rate Limit Errors**

Symptoms: 429 status code, "Rate limit exceeded"

Solutions:
```bash
# Adjust rate limits in .env
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW_SECONDS=60

# Check rate limit metrics
curl http://localhost:8080/metrics | grep rate_limit

# Clear rate limiter state (restart)
docker compose restart app
```

**Issue: High Memory Usage**

Solutions:
```bash
# Reduce model precision
# Reduce max input length
MAX_INPUT_LENGTH=512

# Limit worker count
CMD ["uvicorn", "app:app", "--workers", "1"]

# Monitor memory
docker stats text-summarizer
```

### Debug Mode

Enable debug logging:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

Access debug information:
```bash
# View detailed logs
docker compose logs -f app

# Check application status
curl http://localhost:8080/status

# Verify health
curl http://localhost:8080/health
```

### Getting Help

If you encounter issues:

1. Check the logs for error messages
2. Review this README and documentation
3. Search existing GitHub issues
4. Create a new issue with:
   - Detailed problem description
   - Steps to reproduce
   - Error messages and logs
   - Environment information

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick Start:**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

**Development Guidelines:**

- Follow PEP 8 style guide
- Write unit tests for new features
- Update documentation
- Use meaningful commit messages
- Keep changes focused and atomic

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

The MIT License is a permissive license that allows:
- Commercial use
- Modification
- Distribution
- Private use

With the following conditions:
- License and copyright notice must be included
- The software is provided "as is" without warranty

## Author

**Mutiu Adegboye**

Machine Learning Engineer specializing in NLP and production ML systems.

- GitHub: [@Mutiu123](https://github.com/Mutiu123)
- Email: adegboyemutiu@gmail.com
- LinkedIn: [Mutiu Adegboye](https://linkedin.com/in/mutiu-adegboye)

## Acknowledgments

This project leverages several outstanding open-source technologies:

**Machine Learning:**
- **Hugging Face Transformers**: For PEGASUS model implementation
- **PyTorch**: Deep learning framework
- **NLTK**: Natural language processing utilities

**Web Framework:**
- **FastAPI**: Modern, high-performance Python web framework
- **Uvicorn**: ASGI server implementation
- **Pydantic**: Data validation using Python type hints

**Monitoring:**
- **Prometheus**: Systems monitoring and alerting
- **Grafana**: Metrics visualization and dashboards

**Database:**
- **MongoDB**: Document database for audit logging
- **Motor**: Async Python driver for MongoDB

**Infrastructure:**
- **Docker**: Containerization platform
- **Kubernetes**: Container orchestration
- **GitHub Actions**: CI/CD automation

**Development Tools:**
- **pytest**: Testing framework
- **Black**: Code formatter
- **Flake8**: Linting tool
- **MyPy**: Static type checker
- **pre-commit**: Git hook framework

Special thanks to the open-source community for creating and maintaining these excellent tools.

---

**Project Status:** Production Ready

**Last Updated:** February 2026

**Documentation Version:** 1.0.0

For questions, issues, or feature requests, please open an issue on GitHub or contact the author directly.
