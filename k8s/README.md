# Kubernetes Deployment for Text Summarization API

This directory contains production-ready Kubernetes manifests for deploying the Text Summarization API.

## Architecture

The deployment includes:

- **Deployment**: 2 replicas with rolling updates, resource limits, health probes, and non-root security context
- **Service**: ClusterIP service exposing port 80, routing to container port 8080
- **HPA**: Horizontal Pod Autoscaler with CPU-based scaling (2-10 replicas, 70% CPU target)
- **NetworkPolicy**: Restricts ingress to port 8080 and egress to MongoDB and DNS
- **Ingress**: NGINX ingress with TLS termination and rate limiting
- **ConfigMap**: Application configuration (environment, logging, MongoDB, etc.)
- **Secret**: Sensitive data (JWT secret, API keys, MongoDB credentials)
- **ServiceAccount**: Dedicated service account with minimal permissions
- **PodDisruptionBudget**: Ensures at least 1 pod remains available during disruptions

## Prerequisites

1. Kubernetes cluster (v1.24+)
2. kubectl configured
3. NGINX Ingress Controller installed
4. cert-manager installed (for TLS certificates)
5. Metrics Server installed (for HPA)
6. MongoDB instance (in-cluster or external)

## Quick Start

### 1. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 2. Update Configuration

Edit the following files before deployment:

**configmap.yaml**:
- Update `MONGODB_URL` with your MongoDB connection string
- Update `ALLOWED_ORIGINS` with your domain(s)
- Adjust `MAX_INPUT_LENGTH` and rate limits as needed

**secret.yaml**:
- Replace placeholder secrets with actual base64-encoded values:
  ```bash
  echo -n "your-actual-jwt-secret" | base64
  echo -n "your-actual-api-key" | base64
  ```
- For production, use external secret management (Sealed Secrets, External Secrets Operator, or HashiCorp Vault)

**ingress.yaml**:
- Update `text-summarizer.example.com` with your actual domain
- Update `cert-manager.io/cluster-issuer` if using a different issuer

**deployment.yaml**:
- Update `image: text-summarizer:latest` with your actual container registry and tag

### 3. Deploy All Resources

Using kubectl:
```bash
kubectl apply -f .
```

Using kustomize:
```bash
kubectl apply -k .
```

### 4. Verify Deployment

```bash
# Check all resources
kubectl get all -n text-summarizer

# Check pods
kubectl get pods -n text-summarizer

# Check HPA
kubectl get hpa -n text-summarizer

# Check ingress
kubectl get ingress -n text-summarizer

# View logs
kubectl logs -n text-summarizer -l app=text-summarizer --tail=100
```

### 5. Test the Service

```bash
# Port-forward for local testing
kubectl port-forward -n text-summarizer svc/text-summarizer 8080:80

# Test health endpoint
curl http://localhost:8080/health

# Test via ingress (after DNS is configured)
curl https://text-summarizer.example.com/health
```

## Configuration

### Environment Variables (ConfigMap)

| Variable | Description | Default |
|----------|-------------|---------|
| APP_ENV | Environment (production/staging/development) | production |
| LOG_LEVEL | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO |
| MONGODB_URL | MongoDB connection string | mongodb://mongodb... |
| MONGODB_DATABASE | Database name | text_summarizer |
| MAX_INPUT_LENGTH | Maximum input text length | 1000 |
| JWT_EXPIRATION_MINUTES | JWT token expiration | 60 |
| RATE_LIMIT_REQUESTS | Rate limit per window | 100 |
| ALLOWED_ORIGINS | CORS allowed origins | https://... |

### Secrets

| Secret | Description |
|--------|-------------|
| JWT_SECRET_KEY | Secret key for JWT signing |
| API_KEY | API authentication key |
| MONGODB_USERNAME | MongoDB username (optional) |
| MONGODB_PASSWORD | MongoDB password (optional) |

### Resource Limits

**Requests**:
- CPU: 500m
- Memory: 1Gi

**Limits**:
- CPU: 2000m
- Memory: 4Gi

Adjust based on your workload requirements.

## Security Features

1. **Non-root user**: Containers run as UID 1000
2. **Read-only root filesystem**: Disabled only where necessary
3. **Capability dropping**: All Linux capabilities dropped
4. **Security context**: seccomp profile applied
5. **Network policies**: Restrict ingress/egress traffic
6. **Service account**: Minimal permissions, token auto-mount disabled
7. **Pod disruption budget**: Ensures availability during updates

## Scaling

### Manual Scaling

```bash
kubectl scale deployment text-summarizer -n text-summarizer --replicas=5
```

### Auto-scaling

The HPA automatically scales based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 80%)
- Min replicas: 2
- Max replicas: 10

## Monitoring

### Prometheus Metrics

Metrics are exposed at `/metrics` endpoint:

```bash
kubectl port-forward -n text-summarizer svc/text-summarizer 8080:80
curl http://localhost:8080/metrics
```

### Health Checks

- **Liveness probe**: `/health` every 30s
- **Readiness probe**: `/health` every 10s
- **Startup probe**: `/health` every 10s (max 300s)

## Troubleshooting

### Pod not starting

```bash
# Check pod status
kubectl describe pod -n text-summarizer -l app=text-summarizer

# Check logs
kubectl logs -n text-summarizer -l app=text-summarizer --tail=100

# Check events
kubectl get events -n text-summarizer --sort-by='.lastTimestamp'
```

### Health check failures

```bash
# Exec into pod
kubectl exec -it -n text-summarizer deployment/text-summarizer -- /bin/bash

# Test health endpoint from inside pod
curl http://localhost:8080/health
```

### Network policy issues

```bash
# Temporarily disable network policy
kubectl delete networkpolicy text-summarizer -n text-summarizer

# Re-enable after testing
kubectl apply -f networkpolicy.yaml
```

## Production Checklist

- [ ] Update all placeholder secrets with actual values
- [ ] Configure proper MongoDB connection (credentials, SSL/TLS)
- [ ] Update ingress hostname and TLS certificate
- [ ] Set up monitoring and alerting (Prometheus, Grafana)
- [ ] Configure log aggregation (ELK, Loki, etc.)
- [ ] Set resource limits based on load testing
- [ ] Enable Pod Security Standards
- [ ] Configure backup strategy for MongoDB
- [ ] Set up CI/CD pipeline for automated deployments
- [ ] Configure image pull secrets for private registry
- [ ] Review and adjust network policies
- [ ] Set up disaster recovery procedures

## Cleanup

```bash
# Delete all resources
kubectl delete -f .

# Or using kustomize
kubectl delete -k .

# Delete namespace (will delete all resources)
kubectl delete namespace text-summarizer
```

## Support

For issues or questions:
1. Check application logs: `kubectl logs -n text-summarizer -l app=text-summarizer`
2. Check pod status: `kubectl get pods -n text-summarizer`
3. Review events: `kubectl get events -n text-summarizer`
