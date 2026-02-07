#!/bin/bash
# Automated Docker build, tag, and push script for Linux/macOS

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Read version
VERSION=$(cat VERSION | tr -d '\n\r')
IMAGE_NAME="z0r3f/wallbot-docker"

echo -e "${CYAN}🐳 Building Docker image...${NC}"
docker build --tag ${IMAGE_NAME}:latest --tag ${IMAGE_NAME}:${VERSION} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build complete!${NC}"
    echo "   - ${IMAGE_NAME}:latest"
    echo "   - ${IMAGE_NAME}:${VERSION}"
    echo ""
    
    # Optional: Ask before pushing
    read -p "📤 Push to Docker Hub? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}Pushing images...${NC}"
        docker push ${IMAGE_NAME}:latest
        docker push ${IMAGE_NAME}:${VERSION}
        echo -e "${GREEN}✅ Images pushed successfully!${NC}"
    else
        echo "ℹ️  Skipping push to Docker Hub"
    fi
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi
