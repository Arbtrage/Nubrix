import docker
import psutil
import time
import logging
from typing import List, Optional, Union
from app.models.container import ContainerInfo, ContainerStats, SystemStats
from app.utils.port_manager import PortManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DockerService:
    def __init__(self):
        self.client = None
        self.port_manager = PortManager()
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if Docker service is available"""
        return self.client is not None

    def get_container_info(self, container) -> ContainerInfo:
        """Extract container information into ContainerInfo model"""
        try:
            ports = {}
            if container.attrs.get("NetworkSettings", {}).get("Ports"):
                for internal_port, port_bindings in container.attrs["NetworkSettings"][
                    "Ports"
                ].items():
                    if port_bindings:
                        for binding in port_bindings:
                            ports[internal_port] = (
                                f"{binding['HostIp']}:{binding['HostPort']}"
                            )

            return ContainerInfo(
                id=container.short_id,
                name=container.name,
                status=container.status,
                image=(
                    container.image.tags[0]
                    if container.image.tags
                    else container.image.id
                ),
                ports=ports,
                created=container.attrs["Created"],
                state=container.attrs["State"]["Status"],
            )
        except Exception as e:
            logger.error(f"Error extracting container info: {e}")
            return None

    def get_container_stats(self, container) -> ContainerStats:
        """Get real-time statistics for a container"""
        try:
            stats = container.stats(stream=False)

            # Calculate CPU percentage
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )
            cpu_percent = (cpu_delta / system_delta) * 100 if system_delta > 0 else 0

            # Memory calculations
            memory_usage = stats["memory_stats"]["usage"]
            memory_limit = stats["memory_stats"]["limit"]
            memory_percent = (
                (memory_usage / memory_limit) * 100 if memory_limit > 0 else 0
            )

            # Network calculations
            network_rx = (
                stats["networks"]["eth0"]["rx_bytes"]
                if "networks" in stats and "eth0" in stats["networks"]
                else 0
            )
            network_tx = (
                stats["networks"]["eth0"]["tx_bytes"]
                if "networks" in stats and "eth0" in stats["networks"]
                else 0
            )

            return ContainerStats(
                container_id=container.short_id,
                name=container.name,
                cpu_percent=round(cpu_percent, 2),
                memory_usage=f"{memory_usage / (1024*1024):.2f} MB",
                memory_limit=f"{memory_limit / (1024*1024):.2f} MB",
                memory_percent=round(memory_percent, 2),
                network_rx=f"{network_rx / (1024*1024):.2f} MB",
                network_tx=f"{network_tx / (1024*1024):.2f} MB",
                timestamp=time.time(),
            )
        except Exception as e:
            logger.error(f"Error getting stats for container {container.short_id}: {e}")
            return None

    def get_system_stats(self) -> SystemStats:
        """Get system-wide statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return SystemStats(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=f"{memory.used / (1024**3):.2f} GB",
                memory_total=f"{memory.total / (1024**3):.2f} GB",
                disk_usage_percent=disk.percent,
                timestamp=time.time(),
            )
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return None

    def create_container(self, image: str, name: Optional[str] = None) -> ContainerInfo:
        """Create a new container"""
        if not self.is_available():
            raise RuntimeError("Docker service not available")

        # Find available port
        host_port = self.port_manager.find_available_port()

        # Generate container name if not provided
        container_name = name or f"api-server-{int(time.time())}"

        # Create and start container
        container = self.client.containers.run(
            image=image,
            name=container_name,
            detach=True,
            ports={"5000/tcp": host_port},
            environment={"HOST_PORT": str(host_port)},
        )

        logger.info(f"Created container {container.short_id} on port {host_port}")

        # Wait a moment for container to start
        time.sleep(2)

        # Refresh container object to get updated info
        container.reload()
        return self.get_container_info(container)

    def list_containers(self, all_containers: bool = True) -> List[ContainerInfo]:
        """List containers"""
        if not self.is_available():
            raise RuntimeError("Docker service not available")

        containers = self.client.containers.list(all=all_containers)
        return [self.get_container_info(container) for container in containers]

    def get_container(self, container_id: str) -> ContainerInfo:
        """Get specific container"""
        if not self.is_available():
            raise RuntimeError("Docker service not available")

        container = self.client.containers.get(container_id)
        return self.get_container_info(container)

    def stop_container(self, container_id: str) -> Union[bool, None]:
        """Stop a container"""
        if not self.is_available():
            raise RuntimeError("Docker service not available")

        try:
            container = self.client.containers.get(container_id)
            container.stop()

            # Release the port
            container.reload()
            if container.attrs.get("NetworkSettings", {}).get("Ports"):
                for internal_port, port_bindings in container.attrs["NetworkSettings"][
                    "Ports"
                ].items():
                    if port_bindings:
                        for binding in port_bindings:
                            host_port = int(binding["HostPort"])
                            self.port_manager.release_port(host_port)

            logger.info(f"Stopped container {container_id}")
            return True
        except Exception as e:
            logger.error(f"Error stopping container {container_id}: {e}")
            return None

    def start_container(self, container_id: str) -> Union[bool, None]:
        """Start a stopped container"""
        if not self.is_available():
            raise RuntimeError("Docker service not available")

        try:
            container = self.client.containers.get(container_id)
            container.start()
            logger.info(f"Started container {container_id}")
            return True
        except Exception as e:
            logger.error(f"Error starting container {container_id}: {e}")
            return None

    def remove_container(self, container_id: str) -> Union[bool, None]:
        """Remove a container"""
        if not self.is_available():
            raise RuntimeError("Docker service not available")

        try:
            container = self.client.containers.get(container_id)

            # Release the port if container was running
            if container.status == "running":
                if container.attrs.get("NetworkSettings", {}).get("Ports"):
                    for internal_port, port_bindings in container.attrs[
                        "NetworkSettings"
                    ]["Ports"].items():
                        if port_bindings:
                            for binding in port_bindings:
                                host_port = int(binding["HostPort"])
                                self.port_manager.release_port(host_port)

            container.remove()
            logger.info(f"Removed container {container_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing container {container_id}: {e}")
            return None

    def get_port_info(self):
        """Get port usage information"""
        used_ports = self.port_manager.get_used_ports()
        return {
            "used_ports": used_ports,
            "available_range": f"{self.port_manager.start_port}-{self.port_manager.end_port}",
            "total_ports": self.port_manager.end_port - self.port_manager.start_port,
        }
