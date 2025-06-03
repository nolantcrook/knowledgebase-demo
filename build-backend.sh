#!/bin/bash

# Build and push backend Docker image to ECR

set -e

echo "Building and pushing demo-knowledgebase backend to ECR..."

# AWS ECR configuration
AWS_REGION="us-west-2"
AWS_ACCOUNT_ID="891377073036"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
BACKEND_REPO="demo-knowledgebase-backend"

# Login to ECR
echo "=== Logging into ECR ==="
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Create repository if it doesn't exist
echo "=== Creating ECR repository if needed ==="
aws ecr describe-repositories --repository-names ${BACKEND_REPO} --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name ${BACKEND_REPO} --region ${AWS_REGION}

# Build and push backend
echo "=== Building Backend ==="
docker build -f backend/Dockerfile -t ${BACKEND_REPO}:latest .
docker tag ${BACKEND_REPO}:latest ${ECR_REGISTRY}/${BACKEND_REPO}:latest
echo "Pushing backend image..."
docker push ${ECR_REGISTRY}/${BACKEND_REPO}:latest

echo "=== Backend image built and pushed successfully! ==="
echo ""
echo "Backend: ${ECR_REGISTRY}/${BACKEND_REPO}:latest" 