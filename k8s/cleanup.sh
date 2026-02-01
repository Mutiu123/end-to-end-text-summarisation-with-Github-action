#!/bin/bash

# Text Summarization API - Cleanup Script
# This script removes all Kubernetes resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

NAMESPACE="text-summarizer"

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

confirm_deletion() {
    echo ""
    print_warn "This will delete ALL resources in namespace: $NAMESPACE"
    print_warn "This action cannot be undone!"
    echo ""
    read -p "Are you sure you want to continue? (yes/no) " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Cleanup cancelled."
        exit 0
    fi
}

delete_resources() {
    print_info "Deleting Kubernetes resources..."

    # Delete in reverse order of dependencies
    kubectl delete -f ingress.yaml --ignore-not-found=true
    kubectl delete -f networkpolicy.yaml --ignore-not-found=true
    kubectl delete -f hpa.yaml --ignore-not-found=true
    kubectl delete -f poddisruptionbudget.yaml --ignore-not-found=true
    kubectl delete -f service.yaml --ignore-not-found=true
    kubectl delete -f deployment.yaml --ignore-not-found=true
    kubectl delete -f configmap.yaml --ignore-not-found=true
    kubectl delete -f secret.yaml --ignore-not-found=true
    kubectl delete -f serviceaccount.yaml --ignore-not-found=true

    print_info "Resources deleted."
}

delete_namespace() {
    read -p "Delete namespace '$NAMESPACE'? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deleting namespace: $NAMESPACE"
        kubectl delete -f namespace.yaml --ignore-not-found=true
        print_info "Namespace deleted."
    else
        print_info "Namespace preserved."
    fi
}

verify_cleanup() {
    print_info "Verifying cleanup..."

    if kubectl get namespace $NAMESPACE &> /dev/null; then
        REMAINING=$(kubectl get all -n $NAMESPACE --no-headers 2>/dev/null | wc -l)
        if [ "$REMAINING" -eq 0 ]; then
            print_info "All resources cleaned up successfully."
        else
            print_warn "$REMAINING resources still remaining in namespace."
            kubectl get all -n $NAMESPACE
        fi
    else
        print_info "Namespace deleted. Cleanup complete."
    fi
}

main() {
    print_info "Text Summarization API - Cleanup Script"
    confirm_deletion
    delete_resources
    delete_namespace
    verify_cleanup
    print_info "Cleanup completed!"
}

main
