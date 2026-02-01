# Quick Start Guide

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- NGINX Ingress Controller
- cert-manager (for TLS)
- Metrics Server (for HPA)

## 5-Minute Deployment

### Step 1: Update Configuration

Before deploying, update these critical values:

1. **secret.yaml** - Replace placeholder secrets:
   ```bash
   # Generate secure secrets
   echo -n "your-jwt-secret-key-change-this" | base64
   echo -n "your-api-key-change-this" | base64
   ```

2. **ingress.yaml** - Update domain:
   ```yaml
   spec:
     tls:
       - hosts:
         - your-domain.com  # Change this
   ```

3. **configmap.yaml** - Update MongoDB URL:
   ```yaml
   data:
     MONGODB_URL: "mongodb://your-mongodb-host:27017"
   ```

4. **deployment.yaml** - Update container image:
   ```yaml
   spec:
     containers:
     - image: your-registry/text-summarizer:latest  # Change this
   ```

### Step 2: Deploy Using Script

```bash
# Make scripts executable
chmod +x deploy.sh cleanup.sh

# Deploy everything
./deploy.sh
```

### Step 3: Verify Deployment

```bash
# Check all resources
kubectl get all -n text-summarizer

# Check pods are running
kubectl get pods -n text-summarizer

# View logs
kubectl logs -n text-summarizer -l app=text-summarizer --tail=50
```

### Step 4: Test the API

```bash
# Port-forward for local testing
kubectl port-forward -n text-summarizer svc/text-summarizer 8080:80

# Test health endpoint
curl http://localhost:8080/health

# Test summarization (get token first)
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'

# Use the token to make prediction
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"text": "Your long text to summarize goes here..."}'
```

## Manual Deployment (Alternative)

If you prefer manual deployment:

```bash
# 1. Create namespace
kubectl apply -f namespace.yaml

# 2. Deploy secrets and config
kubectl apply -f secret.yaml
kubectl apply -f configmap.yaml
kubectl apply -f serviceaccount.yaml

# 3. Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# 4. Deploy scaling and policies
kubectl apply -f hpa.yaml
kubectl apply -f networkpolicy.yaml
kubectl apply -f poddisruptionbudget.yaml

# 5. Deploy ingress
kubectl apply -f ingress.yaml

# 6. Wait for rollout
kubectl rollout status deployment/text-summarizer -n text-summarizer
```

## Using Kustomize

```bash
# Deploy with kustomize
kubectl apply -k .

# Deploy to staging
kubectl apply -k overlays/staging

# Deploy to production
kubectl apply -k overlays/production
```

## Common Issues

### Pods not starting
```bash
# Check pod status
kubectl describe pod -n text-summarizer -l app=text-summarizer

# Check logs
kubectl logs -n text-summarizer -l app=text-summarizer
```

### HPA not working
```bash
# Check metrics-server is running
kubectl get deployment metrics-server -n kube-system

# Check HPA status
kubectl get hpa -n text-summarizer
kubectl describe hpa text-summarizer -n text-summarizer
```

### Ingress not working
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress text-summarizer -n text-summarizer

# Check cert-manager (if using TLS)
kubectl get certificate -n text-summarizer
```

## Scaling

### Manual scaling
```bash
kubectl scale deployment text-summarizer -n text-summarizer --replicas=5
```

### Check auto-scaling
```bash
kubectl get hpa -n text-summarizer -w
```

## Monitoring

### View metrics
```bash
kubectl port-forward -n text-summarizer svc/text-summarizer 8080:80
curl http://localhost:8080/metrics
```

### View logs in real-time
```bash
kubectl logs -n text-summarizer -l app=text-summarizer -f
```

## Cleanup

```bash
# Using script
./cleanup.sh

# Or manually
kubectl delete -f .

# Or delete entire namespace
kubectl delete namespace text-summarizer
```

## Next Steps

1. Set up monitoring with Prometheus/Grafana
2. Configure log aggregation (ELK, Loki)
3. Set up alerts for critical metrics
4. Configure backup for MongoDB
5. Set up CI/CD pipeline
6. Enable Pod Security Standards
7. Configure external secret management

## Useful Commands

```bash
# Get all resources
kubectl get all -n text-summarizer

# Describe deployment
kubectl describe deployment text-summarizer -n text-summarizer

# Get events
kubectl get events -n text-summarizer --sort-by='.lastTimestamp'

# Exec into pod
kubectl exec -it -n text-summarizer deployment/text-summarizer -- /bin/bash

# Check resource usage
kubectl top pods -n text-summarizer

# View all environment variables
kubectl exec -n text-summarizer deployment/text-summarizer -- env

# Force rollout restart
kubectl rollout restart deployment/text-summarizer -n text-summarizer
```
