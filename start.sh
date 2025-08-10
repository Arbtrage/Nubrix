#!/bin/bash

echo "🚀 Starting Docker Orchestration System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Build the base API server image
echo "🔨 Building base API server image..."
if docker build -f Dockerfile.base -t base-api-server:latest .; then
    echo "✅ Base image built successfully"
else
    echo "❌ Failed to build base image"
    exit 1
fi

# Check if orchestration API is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Orchestration API is already running on port 8000"
else
    echo "🚀 Starting orchestration API..."
    
    # Install dependencies if needed
    if ! python -c "import fastapi" 2>/dev/null; then
        echo "📦 Installing dependencies..."
        pip install -e .
    fi
    
    # Start the orchestration API
    echo "🌐 Starting API on http://localhost:8000"
    echo "📖 API documentation: http://localhost:8000/docs"
    echo "🔍 Health check: http://localhost:8000/health"
    echo ""
    echo "Press Ctrl+C to stop the API"
    echo ""
    
    python main.py
fi 