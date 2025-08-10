from fastapi import APIRouter, HTTPException
from app.models.container import SystemStats, PortInfo
from app.services.docker_service import DockerService

router = APIRouter(tags=["Monitoring"])


@router.get("/ports", response_model=PortInfo)
async def get_port_info():
    """Get port usage information"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        port_info = docker_service.get_port_info()
        return PortInfo(**port_info)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get port information: {str(e)}"
        )


@router.get("/system/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system-wide statistics"""
    docker_service = DockerService()

    if not docker_service.is_available():
        raise HTTPException(status_code=500, detail="Docker service not available")

    try:
        stats = docker_service.get_system_stats()
        if stats is None:
            raise HTTPException(status_code=500, detail="Failed to get system stats")
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get system stats: {str(e)}"
        )
