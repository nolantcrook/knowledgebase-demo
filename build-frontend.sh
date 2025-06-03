#!/bin/bash

# Build and push frontend Docker image to ECR

set -e

echo "Building and pushing demo-knowledgebase frontend to ECR..."

# AWS ECR configuration
AWS_REGION="us-west-2"
AWS_ACCOUNT_ID="891377073036"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FRONTEND_REPO="demo-knowledgebase-frontend"

# Login to ECR
echo "=== Logging into ECR ==="
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Create repository if it doesn't exist
echo "=== Creating ECR repository if needed ==="
aws ecr describe-repositories --repository-names ${FRONTEND_REPO} --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name ${FRONTEND_REPO} --region ${AWS_REGION}

# Build and push frontend
echo "=== Building Frontend ==="
docker build -f frontend/Dockerfile -t ${FRONTEND_REPO}:latest ./frontend
docker tag ${FRONTEND_REPO}:latest ${ECR_REGISTRY}/${FRONTEND_REPO}:latest
echo "Pushing frontend image..."
docker push ${ECR_REGISTRY}/${FRONTEND_REPO}:latest

echo "=== Frontend image built and pushed successfully! ==="
echo ""
echo "Frontend: ${ECR_REGISTRY}/${FRONTEND_REPO}:latest" 