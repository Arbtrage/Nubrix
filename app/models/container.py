from pydantic import BaseModel
from typing import Dict, Optional


class ContainerCreateRequest(BaseModel):
    name: Optional[str] = None
    image: str = "base-api-server:latest"


class ContainerInfo(BaseModel):
    id: str
    name: str
    status: str
    image: str
    ports: Dict[str, str]
    created: str
    state: str


class ContainerStats(BaseModel):
    container_id: str
    name: str
    cpu_percent: float
    memory_usage: str
    memory_limit: str
    memory_percent: float
    network_rx: str
    network_tx: str
    timestamp: float


class SystemStats(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used: str
    memory_total: str
    disk_usage_percent: float
    timestamp: float


class PortInfo(BaseModel):
    used_ports: list[int]
    available_range: str
    total_ports: int
