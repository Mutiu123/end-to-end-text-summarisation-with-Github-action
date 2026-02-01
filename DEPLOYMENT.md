# Deployment Guide

This document provides comprehensive deployment instructions for the Text Summarizer API across various environments and platforms.

## Table of Contents

- [Local Development Setup](#local-development-setup)
- [Docker Deployment](#docker-deployment)
- [Docker Compose Full Stack](#docker-compose-full-stack)
- [AWS ECR/ECS Deployment](#aws-ecrecs-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Environment Configuration](#environment-configuration)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring Setup](#monitoring-setup)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedures](#rollback-procedures)

## Local Development Setup

### Prerequisites

- Python 3.10 or higher
- MongoDB (local or cloud instance)
- Git
- Virtual environment tool (venv or virtualenv)

### Step-by-Step Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/end-to-end-text-summarisation-with-Github-action.git
   cd end-to-end-text-summarisation-with-Github-action
   ```

2. **Create Virtual Environment**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env with your local configuration
   # Required variables:
   # MONGODB_URL=mongodb://localhost:27017/text_summarizer
   # AWS_ACCESS_KEY_ID=your_access_key
   # AWS_SECRET_ACCESS_KEY=your_secret_key
   # AWS_DEFAULT_REGION=us-east-1
   ```

5. **Start MongoDB Locally** (if not using cloud MongoDB)

   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest

   # Or use installed MongoDB service
   # Windows: net start MongoDB
   # macOS: brew services start mongodb-community
   # Linux: sudo systemctl start mongod
   ```

6. **Run the Application**

   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:8080`

7. **Verify the Deployment**

   ```bash
   curl http://localhost:8080/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "timestamp": "2026-02-01T12:00:00Z"
   }
   ```

## Docker Deployment

### Building the Docker Image

1. **Build the Image**

   ```bash
   docker build -t text-summarizer-api:latest .
   ```

   For a specific version:
   ```bash
   docker build -t text-summarizer-api:v1.0.0 .
   ```

2. **Verify the Build**

   ```bash
   docker images | grep text-summarizer-api
   ```

### Running the Container

1. **Run with Environment Variables**

   ```bash
   docker run -d \
     --name text-summarizer \
     -p 8080:8080 \
     -e MONGODB_URL="mongodb://host.docker.internal:27017/text_summarizer" \
     -e AWS_ACCESS_KEY_ID="your_access_key" \
     -e AWS_SECRET_ACCESS_KEY="your_secret_key" \
     -e AWS_DEFAULT_REGION="us-east-1" \
     text-summarizer-api:latest
   ```

2. **Run with Environment File**

   ```bash
   docker run -d \
     --name text-summarizer \
     -p 8080:8080 \
     --env-file .env \
     text-summarizer-api:latest
   ```

3. **View Logs**

   ```bash
   docker logs -f text-summarizer
   ```

4. **Stop and Remove Container**

   ```bash
   docker stop text-summarizer
   docker rm text-summarizer
   ```

### Docker Image Optimization

The Dockerfile uses multi-stage builds for optimization:

- **Stage 1**: Builder stage installs dependencies
- **Stage 2**: Runtime stage copies only necessary files
- **Result**: Smaller image size, improved security, faster deployments

## Docker Compose Full Stack

Deploy the complete application stack with MongoDB, Prometheus, and Grafana.

### Prerequisites

- Docker
- Docker Compose

### Deployment Steps

1. **Review docker-compose.yml**

   The compose file includes:
   - Text Summarizer API
   - MongoDB database
   - Prometheus for metrics
   - Grafana for visualization

2. **Create Environment File**

   Create a `.env` file with required variables:
   ```env
   MONGODB_URL=mongodb://mongodb:27017/text_summarizer
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   ```

3. **Start the Stack**

   ```bash
   docker-compose up -d
   ```

4. **Verify All Services**

   ```bash
   docker-compose ps
   ```

   Expected output shows all services running:
   - text-summarizer-api (port 8080)
   - mongodb (port 27017)
   - prometheus (port 9090)
   - grafana (port 3000)

5. **Access Services**

   - API: `http://localhost:8080`
   - Prometheus: `http://localhost:9090`
   - Grafana: `http://localhost:3000` (default: admin/admin)

6. **View Logs**

   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f text-summarizer-api
   ```

7. **Stop the Stack**

   ```bash
   docker-compose down
   ```

8. **Stop and Remove Volumes**

   ```bash
   docker-compose down -v
   ```

## AWS ECR/ECS Deployment

Deploy the application to AWS Elastic Container Service using Elastic Container Registry.

### Step 1: Configure AWS CLI

```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json
```

### Step 2: Create ECR Repository

```bash
# Create repository
aws ecr create-repository \
  --repository-name text-summarizer-api \
  --region us-east-1

# Note the repositoryUri from the output
```

### Step 3: Authenticate Docker to ECR

```bash
# Get login password and authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### Step 4: Build and Push Image

```bash
# Build image
docker build -t text-summarizer-api:latest .

# Tag image for ECR
docker tag text-summarizer-api:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-summarizer-api:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-summarizer-api:latest
```

### Step 5: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster \
  --cluster-name text-summarizer-cluster \
  --region us-east-1
```

### Step 6: Create Task Definition

Create a file named `task-definition.json`:

```json
{
  "family": "text-summarizer-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "text-summarizer-api",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/text-summarizer-api:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "us-east-1"
        }
      ],
      "secrets": [
        {
          "name": "MONGODB_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mongodb-url"
        },
        {
          "name": "AWS_ACCESS_KEY_ID",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:aws-access-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/text-summarizer",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register the task definition:

```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json
```

### Step 7: Create ECS Service

```bash
aws ecs create-service \
  --cluster text-summarizer-cluster \
  --service-name text-summarizer-service \
  --task-definition text-summarizer-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

### Step 8: Configure Application Load Balancer

```bash
# Create load balancer
aws elbv2 create-load-balancer \
  --name text-summarizer-alb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups sg-xxxxx

# Create target group
aws elbv2 create-target-group \
  --name text-summarizer-tg \
  --protocol HTTP \
  --port 8080 \
  --vpc-id vpc-xxxxx \
  --target-type ip

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn <alb-arn> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=<target-group-arn>
```

### Step 9: Update Service with Load Balancer

```bash
aws ecs update-service \
  --cluster text-summarizer-cluster \
  --service text-summarizer-service \
  --load-balancers targetGroupArn=<target-group-arn>,containerName=text-summarizer-api,containerPort=8080
```

## Kubernetes Deployment

Deploy the application to a Kubernetes cluster.

### Prerequisites

- Kubernetes cluster (minikube, EKS, GKE, or AKS)
- kubectl configured
- Docker image pushed to registry

### Step 1: Create Namespace

```bash
kubectl create namespace text-summarizer
```

### Step 2: Create Secrets

```bash
# Create secret for MongoDB URL
kubectl create secret generic mongodb-secret \
  --from-literal=mongodb-url='mongodb://mongodb:27017/text_summarizer' \
  -n text-summarizer

# Create secret for AWS credentials
kubectl create secret generic aws-credentials \
  --from-literal=aws-access-key-id='your_access_key' \
  --from-literal=aws-secret-access-key='your_secret_key' \
  -n text-summarizer
```

### Step 3: Apply Kubernetes Manifests

Assuming you have manifests in a `k8s/` directory:

```bash
# Apply all manifests
kubectl apply -f k8s/ -n text-summarizer

# Or apply individually
kubectl apply -f k8s/deployment.yaml -n text-summarizer
kubectl apply -f k8s/service.yaml -n text-summarizer
kubectl apply -f k8s/ingress.yaml -n text-summarizer
kubectl apply -f k8s/hpa.yaml -n text-summarizer
```

### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods -n text-summarizer

# Check services
kubectl get services -n text-summarizer

# Check deployments
kubectl get deployments -n text-summarizer

# View pod logs
kubectl logs -f <pod-name> -n text-summarizer
```

### Step 5: Access the Application

```bash
# If using LoadBalancer service
kubectl get service text-summarizer-service -n text-summarizer

# If using NodePort
kubectl get nodes -o wide
# Access via http://<node-ip>:<node-port>

# If using Ingress
kubectl get ingress -n text-summarizer
```

### Step 6: Scale the Deployment

```bash
# Manual scaling
kubectl scale deployment text-summarizer-deployment \
  --replicas=5 \
  -n text-summarizer

# Auto-scaling with HPA (if configured)
kubectl autoscale deployment text-summarizer-deployment \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n text-summarizer
```

### Step 7: Update Deployment

```bash
# Update image
kubectl set image deployment/text-summarizer-deployment \
  text-summarizer-api=YOUR_REGISTRY/text-summarizer-api:v2.0.0 \
  -n text-summarizer

# Check rollout status
kubectl rollout status deployment/text-summarizer-deployment -n text-summarizer
```

## Environment Configuration

### Development Environment

```env
# .env.dev
ENVIRONMENT=development
LOG_LEVEL=DEBUG
MONGODB_URL=mongodb://localhost:27017/text_summarizer_dev
AWS_ACCESS_KEY_ID=dev_access_key
AWS_SECRET_ACCESS_KEY=dev_secret_key
AWS_DEFAULT_REGION=us-east-1
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
RATE_LIMIT_ENABLED=false
```

### Staging Environment

```env
# .env.staging
ENVIRONMENT=staging
LOG_LEVEL=INFO
MONGODB_URL=mongodb://staging-mongodb:27017/text_summarizer_staging
AWS_ACCESS_KEY_ID=staging_access_key
AWS_SECRET_ACCESS_KEY=staging_secret_key
AWS_DEFAULT_REGION=us-east-1
CORS_ORIGINS=https://staging.example.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Production Environment

```env
# .env.prod
ENVIRONMENT=production
LOG_LEVEL=WARNING
MONGODB_URL=mongodb://prod-mongodb-cluster:27017/text_summarizer_prod?replicaSet=rs0
AWS_ACCESS_KEY_ID=prod_access_key
AWS_SECRET_ACCESS_KEY=prod_secret_key
AWS_DEFAULT_REGION=us-east-1
CORS_ORIGINS=https://api.example.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_PERIOD=60
SSL_ENABLED=true
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem
```

### Environment-Specific Configuration Best Practices

- Use AWS Secrets Manager or HashiCorp Vault for production secrets
- Never commit `.env` files to version control
- Use different MongoDB databases for each environment
- Configure appropriate rate limits for each tier
- Enable SSL/TLS in staging and production
- Set appropriate log levels (DEBUG for dev, WARNING for prod)

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot

1. **Install Certbot**

   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx

   # CentOS/RHEL
   sudo yum install certbot python3-certbot-nginx
   ```

2. **Obtain Certificate**

   ```bash
   sudo certbot certonly --standalone -d api.example.com
   ```

3. **Configure Application**

   Update your environment variables:
   ```env
   SSL_ENABLED=true
   SSL_CERT_PATH=/etc/letsencrypt/live/api.example.com/fullchain.pem
   SSL_KEY_PATH=/etc/letsencrypt/live/api.example.com/privkey.pem
   ```

4. **Auto-Renewal**

   ```bash
   # Test renewal
   sudo certbot renew --dry-run

   # Add cron job for auto-renewal
   sudo crontab -e
   # Add: 0 0 * * * /usr/bin/certbot renew --quiet
   ```

### Using AWS Certificate Manager (ACM)

1. **Request Certificate**

   ```bash
   aws acm request-certificate \
     --domain-name api.example.com \
     --validation-method DNS \
     --region us-east-1
   ```

2. **Validate Domain**

   Add the provided CNAME record to your DNS configuration

3. **Attach to Load Balancer**

   ```bash
   aws elbv2 create-listener \
     --load-balancer-arn <alb-arn> \
     --protocol HTTPS \
     --port 443 \
     --certificates CertificateArn=<certificate-arn> \
     --default-actions Type=forward,TargetGroupArn=<target-group-arn>
   ```

### Kubernetes Ingress with TLS

Create a TLS secret:

```bash
kubectl create secret tls tls-secret \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem \
  -n text-summarizer
```

Update ingress manifest:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: text-summarizer-ingress
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: tls-secret
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: text-summarizer-service
            port:
              number: 8080
```

## Monitoring Setup

### Prometheus Configuration

1. **Configure Prometheus to Scrape Metrics**

   Create `prometheus.yml`:

   ```yaml
   global:
     scrape_interval: 15s

   scrape_configs:
     - job_name: 'text-summarizer-api'
       static_configs:
         - targets: ['text-summarizer-api:8080']
   ```

2. **Deploy Prometheus**

   ```bash
   docker run -d \
     --name prometheus \
     -p 9090:9090 \
     -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
     prom/prometheus
   ```

3. **Access Prometheus UI**

   Navigate to `http://localhost:9090`

### Grafana Setup

1. **Deploy Grafana**

   ```bash
   docker run -d \
     --name grafana \
     -p 3000:3000 \
     grafana/grafana
   ```

2. **Configure Data Source**

   - Login to Grafana (default: admin/admin)
   - Add Prometheus data source
   - URL: `http://prometheus:9090`

3. **Import Dashboard**

   - Create dashboard for Text Summarizer API
   - Add panels for:
     - Request rate
     - Error rate
     - Response time
     - Database connection status
     - Model inference time

4. **Set Up Alerts**

   Configure alerts for:
   - High error rate (>5%)
   - High response time (>2s)
   - Database connection failures
   - High CPU/memory usage

### CloudWatch Monitoring (AWS)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/linux/amd64/latest/AmazonCloudWatchAgent.zip

# Configure agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json \
  -s
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Container Fails to Start

**Symptoms**: Container exits immediately after starting

**Diagnosis**:
```bash
docker logs <container-id>
```

**Solutions**:
- Check environment variables are set correctly
- Verify MongoDB connection string
- Ensure AWS credentials are valid
- Check for port conflicts

#### Issue 2: Database Connection Failures

**Symptoms**: Application logs show MongoDB connection errors

**Diagnosis**:
```bash
# Test MongoDB connection
mongosh "mongodb://localhost:27017/text_summarizer"
```

**Solutions**:
- Verify MongoDB is running
- Check MONGODB_URL in environment variables
- For Docker: Use `host.docker.internal` instead of `localhost`
- Check firewall rules and security groups

#### Issue 3: High Memory Usage

**Symptoms**: Container or pod gets killed due to OOM

**Diagnosis**:
```bash
# Docker
docker stats <container-id>

# Kubernetes
kubectl top pods -n text-summarizer
```

**Solutions**:
- Increase memory limits in deployment configuration
- Implement request batching to reduce concurrent model loads
- Add memory limits to prevent resource exhaustion
- Monitor and optimize model loading

#### Issue 4: Slow Response Times

**Symptoms**: API responses taking longer than expected

**Diagnosis**:
- Check Prometheus metrics
- Review application logs
- Monitor database query performance

**Solutions**:
- Implement caching for frequent requests
- Optimize database queries with indexes
- Scale horizontally with more replicas
- Use connection pooling
- Enable async processing for long-running tasks

#### Issue 5: SSL Certificate Errors

**Symptoms**: HTTPS connections fail with certificate errors

**Diagnosis**:
```bash
openssl s_client -connect api.example.com:443
```

**Solutions**:
- Verify certificate files are in correct location
- Check certificate expiration date
- Ensure certificate matches domain name
- Verify certificate chain is complete

## Rollback Procedures

### Docker Rollback

```bash
# Stop current container
docker stop text-summarizer

# Remove current container
docker rm text-summarizer

# Run previous version
docker run -d \
  --name text-summarizer \
  -p 8080:8080 \
  --env-file .env \
  text-summarizer-api:previous-version
```

### ECS Rollback

```bash
# List task definition revisions
aws ecs list-task-definitions \
  --family-prefix text-summarizer-task

# Update service to previous revision
aws ecs update-service \
  --cluster text-summarizer-cluster \
  --service text-summarizer-service \
  --task-definition text-summarizer-task:5
```

### Kubernetes Rollback

```bash
# View rollout history
kubectl rollout history deployment/text-summarizer-deployment -n text-summarizer

# Rollback to previous revision
kubectl rollout undo deployment/text-summarizer-deployment -n text-summarizer

# Rollback to specific revision
kubectl rollout undo deployment/text-summarizer-deployment \
  --to-revision=3 \
  -n text-summarizer

# Monitor rollback
kubectl rollout status deployment/text-summarizer-deployment -n text-summarizer
```

### Database Rollback

Always backup before migrations:

```bash
# Create backup
mongodump --uri="mongodb://localhost:27017/text_summarizer" --out=/backup/$(date +%Y%m%d)

# Restore from backup
mongorestore --uri="mongodb://localhost:27017/text_summarizer" /backup/20260201
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

For additional support, please open an issue on GitHub or contact the DevOps team.
