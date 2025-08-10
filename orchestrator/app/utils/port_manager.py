import socket
from typing import List


class PortManager:
    def __init__(self, start_port: int = 8000, end_port: int = 9000):
        self.start_port = start_port
        self.end_port = end_port
        self.used_ports = set()

    def find_available_port(self) -> int:
        """Find an available port in the configured range"""
        for port in range(self.start_port, self.end_port):
            if port not in self.used_ports and self._is_port_available(port):
                self.used_ports.add(port)
                return port
        raise RuntimeError("No available ports in the configured range")

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available on the system"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return True
        except OSError:
            return False

    def release_port(self, port: int):
        """Release a port back to the pool"""
        self.used_ports.discard(port)

    def get_used_ports(self) -> List[int]:
        """Get list of currently used ports"""
        return list(self.used_ports)
