#!/bin/bash

# Text Summarization API - Kubernetes Deployment Script
# This script deploys the application to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="text-summarizer"
DEPLOYMENT_NAME="text-summarizer"

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found. Please install kubectl."
        exit 1
    fi

    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Check your kubeconfig."
        exit 1
    fi

    # Check if metrics-server is available (for HPA)
    if ! kubectl get deployment metrics-server -n kube-system &> /dev/null; then
        print_warn "metrics-server not found. HPA may not work correctly."
    fi

    print_info "Prerequisites check completed."
}

create_namespace() {
    print_info "Creating namespace: $NAMESPACE"
    kubectl apply -f namespace.yaml
}

deploy_secrets() {
    print_info "Deploying secrets..."
    print_warn "Using placeholder secrets. Update secret.yaml with actual values for production!"
    kubectl apply -f secret.yaml
}

deploy_config() {
    print_info "Deploying configuration..."
    kubectl apply -f configmap.yaml
}

deploy_serviceaccount() {
    print_info "Deploying service account..."
    kubectl apply -f serviceaccount.yaml
}

deploy_application() {
    print_info "Deploying application..."
    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml
}

deploy_autoscaling() {
    print_info "Deploying HPA..."
    kubectl apply -f hpa.yaml
}

deploy_network_policy() {
    print_info "Deploying network policies..."
    kubectl apply -f networkpolicy.yaml
}

deploy_ingress() {
    print_info "Deploying ingress..."
    kubectl apply -f ingress.yaml
}

deploy_pdb() {
    print_info "Deploying pod disruption budget..."
    kubectl apply -f poddisruptionbudget.yaml
}

wait_for_deployment() {
    print_info "Waiting for deployment to be ready..."
    kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=300s
}

verify_deployment() {
    print_info "Verifying deployment..."

    # Check pods
    POD_COUNT=$(kubectl get pods -n $NAMESPACE -l app=text-summarizer --field-selector=status.phase=Running --no-headers | wc -l)
    print_info "Running pods: $POD_COUNT"

    # Check service
    SVC_IP=$(kubectl get svc $DEPLOYMENT_NAME -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
    print_info "Service ClusterIP: $SVC_IP"

    # Check HPA
    kubectl get hpa -n $NAMESPACE

    # Check ingress
    kubectl get ingress -n $NAMESPACE
}

show_access_info() {
    echo ""
    print_info "======================================"
    print_info "Deployment completed successfully!"
    print_info "======================================"
    echo ""
    print_info "Access the application:"
    echo ""
    echo "  1. Via port-forward (local testing):"
    echo "     kubectl port-forward -n $NAMESPACE svc/$DEPLOYMENT_NAME 8080:80"
    echo "     curl http://localhost:8080/health"
    echo ""
    echo "  2. Via ingress (after DNS configuration):"
    INGRESS_HOST=$(kubectl get ingress -n $NAMESPACE text-summarizer -o jsonpath='{.spec.rules[0].host}')
    echo "     curl https://$INGRESS_HOST/health"
    echo ""
    print_info "Useful commands:"
    echo "  View pods:    kubectl get pods -n $NAMESPACE"
    echo "  View logs:    kubectl logs -n $NAMESPACE -l app=text-summarizer --tail=100"
    echo "  View HPA:     kubectl get hpa -n $NAMESPACE"
    echo "  Scale manual: kubectl scale deployment $DEPLOYMENT_NAME -n $NAMESPACE --replicas=3"
    echo ""
}

show_logs() {
    print_info "Recent logs from application:"
    kubectl logs -n $NAMESPACE -l app=text-summarizer --tail=20
}

# Main deployment flow
main() {
    print_info "Starting deployment of Text Summarization API..."
    echo ""

    check_prerequisites
    create_namespace
    deploy_serviceaccount
    deploy_secrets
    deploy_config
    deploy_application
    deploy_autoscaling
    deploy_network_policy
    deploy_ingress
    deploy_pdb
    wait_for_deployment
    verify_deployment
    show_access_info

    # Ask if user wants to see logs
    read -p "Show application logs? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_logs
    fi
}

# Run main function
main
