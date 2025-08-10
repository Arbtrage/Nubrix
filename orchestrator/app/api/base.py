from fastapi import APIRouter, HTTPException
from app.services.docker_service import DockerService
import time

router = APIRouter(tags=["System"])


@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Docker Orchestration API",
        "version": "1.0.0",
        "endpoints": [
            "/containers",
            "/containers/running",
            "/containers/create",
            "/containers/{container_id}",
            "/containers/{container_id}/stats",
            "/containers/{container_id}/stop",
            "/containers/{container_id}/start",
            "/containers/{container_id}/remove",
            "/ports",
        ],
    }


@router.get("/health")
async def health():
    """Health check endpoint"""
    docker_service = DockerService()
    docker_status = "healthy" if docker_service.is_available() else "unhealthy"
    return {"status": "healthy", "docker": docker_status, "timestamp": time.time()}
