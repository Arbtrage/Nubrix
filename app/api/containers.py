from fastapi import APIRouter, HTTPException
from typing import List
from app.models.container import ContainerCreateRequest, ContainerInfo, ContainerStats
from app.services.docker_service import DockerService

router = APIRouter(prefix="/containers", tags=["Container Management"])


@router.post("/create", response_model=ContainerInfo)
async def create_container(request: ContainerCreateRequest):
    """Create a new container from the base image"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        return docker_service.create_container(request.image, request.name)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create container: {str(e)}"
        )


@router.get("/", response_model=List[ContainerInfo])
async def list_containers():
    """List all containers (running, stopped, and created)"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        return docker_service.list_containers(all_containers=True)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list containers: {str(e)}"
        )


@router.get("/running", response_model=List[ContainerInfo])
async def list_running_containers():
    """List only running containers"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        return docker_service.list_containers(all_containers=False)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list running containers: {str(e)}"
        )


@router.get("/{container_id}", response_model=ContainerInfo)
async def get_container(container_id: str):
    """Get information about a specific container"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        return docker_service.get_container(container_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        raise HTTPException(
            status_code=500, detail=f"Failed to get container: {str(e)}"
        )


@router.get("/{container_id}/stats", response_model=ContainerStats)
async def get_container_stats(container_id: str):
    """Get real-time statistics for a specific container"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        container = docker_service.client.containers.get(container_id)
        stats = docker_service.get_container_stats(container)
        if stats is None:
            raise HTTPException(status_code=500, detail="Failed to get container stats")
        return stats
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        raise HTTPException(
            status_code=500, detail=f"Failed to get container stats: {str(e)}"
        )


@router.post("/{container_id}/stop")
async def stop_container(container_id: str):
    """Stop a running container"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        success = docker_service.stop_container(container_id)
        if success:
            return {"message": f"Container {container_id} stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop container")
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        raise HTTPException(
            status_code=500, detail=f"Failed to stop container: {str(e)}"
        )


@router.post("/{container_id}/start")
async def start_container(container_id: str):
    """Start a stopped container"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        success = docker_service.start_container(container_id)
        if success:
            return {"message": f"Container {container_id} started successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start container")
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        raise HTTPException(
            status_code=500, detail=f"Failed to start container: {str(e)}"
        )


@router.delete("/{container_id}")
async def remove_container(container_id: str):
    """Remove a container"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        success = docker_service.remove_container(container_id)
        if success:
            return {"message": f"Container {container_id} removed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to remove container")
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Container not found")
        raise HTTPException(
            status_code=500, detail=f"Failed to remove container: {str(e)}"
        )
