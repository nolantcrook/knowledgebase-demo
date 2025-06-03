#!/bin/bash

# Build and push both backend and frontend Docker images to ECR

set -e

echo "Building and pushing demo-knowledgebase images to ECR..."

# AWS ECR configuration
AWS_REGION="us-west-2"
AWS_ACCOUNT_ID="891377073036"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
BACKEND_REPO="demo-knowledgebase-backend"
FRONTEND_REPO="demo-knowledgebase-frontend"

# Login to ECR
echo "=== Logging into ECR ==="
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Create repositories if they don't exist
echo "=== Creating ECR repositories if needed ==="
aws ecr describe-repositories --repository-names ${BACKEND_REPO} --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name ${BACKEND_REPO} --region ${AWS_REGION}

aws ecr describe-repositories --repository-names ${FRONTEND_REPO} --region ${AWS_REGION} 2>/dev/null || \
    aws ecr create-repository --repository-name ${FRONTEND_REPO} --region ${AWS_REGION}

# Build and push backend
echo "=== Building Backend ==="
docker build -f backend/Dockerfile -t ${BACKEND_REPO}:latest .
docker tag ${BACKEND_REPO}:latest ${ECR_REGISTRY}/${BACKEND_REPO}:latest
echo "Pushing backend image..."
docker push ${ECR_REGISTRY}/${BACKEND_REPO}:latest

# Build and push frontend
echo "=== Building Frontend ==="
docker build -f frontend/Dockerfile -t ${FRONTEND_REPO}:latest ./frontend
docker tag ${FRONTEND_REPO}:latest ${ECR_REGISTRY}/${FRONTEND_REPO}:latest
echo "Pushing frontend image..."
docker push ${ECR_REGISTRY}/${FRONTEND_REPO}:latest

echo "=== All images built and pushed successfully! ==="
echo ""
echo "Backend: ${ECR_REGISTRY}/${BACKEND_REPO}:latest"
echo "Frontend: ${ECR_REGISTRY}/${FRONTEND_REPO}:latest"
echo ""
echo "You can now deploy the Kubernetes application or update your docker-compose.yml to use these images."
echo ""
echo "To use in docker-compose, update the image references to:"
echo "  backend: ${ECR_REGISTRY}/${BACKEND_REPO}:latest"
echo "  frontend: ${ECR_REGISTRY}/${FRONTEND_REPO}:latest" 