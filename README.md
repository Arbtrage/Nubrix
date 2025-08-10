# Docker Orchestration API

A FastAPI-based Docker orchestration system that automatically manages containers with intelligent port allocation and real-time monitoring.

## Features

- **Base API Server**: A sample FastAPI server running on port 5000 with health endpoints
- **Container Orchestration**: Create, manage, and monitor Docker containers
- **Automatic Port Management**: Intelligent port allocation (8000-9000 range)
- **Real-time Statistics**: CPU, memory, and network usage monitoring
- **Container Lifecycle Management**: Start, stop, and remove containers
- **System Monitoring**: Host system resource usage

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Orchestration     │    │   Base API Server   │    │   Docker Engine     │
│   API (Port 8000)   │◄──►│   (Port 5000)      │◄──►│   (via socket)     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Docker daemon running

## Quick Start

### 1. Build and Run with Docker Compose

```bash
# Clone the repository
git clone <your-repo>
cd nubrixai

# Build and start all services
docker-compose up --build

# The services will be available at:
# - Orchestration API: http://localhost:8000
# - Base API Server: http://localhost:5000
```

### 2. Manual Setup

```bash
# Install dependencies
pip install -e .

# Build the base image
docker build -f Dockerfile.base -t base-api-server:latest .

# Run the orchestration API
python main.py
```

## API Endpoints

### Core Endpoints

| Method | Endpoint  | Description                             |
| ------ | --------- | --------------------------------------- |
| `GET`  | `/`       | API information and available endpoints |
| `GET`  | `/health` | Health check and Docker status          |

### Container Management

| Method   | Endpoint                 | Description                                     |
| -------- | ------------------------ | ----------------------------------------------- |
| `POST`   | `/containers/create`     | Create a new container                          |
| `GET`    | `/containers`            | List all containers (running, stopped, created) |
| `GET`    | `/containers/running`    | List only running containers                    |
| `GET`    | `/containers/{id}`       | Get container information                       |
| `POST`   | `/containers/{id}/start` | Start a container                               |
| `POST`   | `/containers/{id}/stop`  | Stop a container                                |
| `DELETE` | `/containers/{id}`       | Remove a container                              |

### Monitoring

| Method | Endpoint                 | Description                |
| ------ | ------------------------ | -------------------------- |
| `GET`  | `/containers/{id}/stats` | Get container statistics   |
| `GET`  | `/system/stats`          | Get system-wide statistics |
| `GET`  | `/ports`                 | Get port usage information |

## Usage Examples

### 1. Create a New Container

```bash
curl -X POST "http://localhost:9000/containers/create" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-api-server", "image": "base-api-server:latest"}'
```

Response:

```json
{
  "id": "abc123",
  "name": "my-api-server",
  "status": "running",
  "image": "base-api-server:latest",
  "ports": { "5000/tcp": "0.0.0.0:8001" },
  "created": "2024-01-01T00:00:00.000000000Z",
  "state": "running"
}
```

### 2. List All Containers

```bash
# List all containers (including stopped ones)
curl "http://localhost:9000/containers"

# List only running containers
curl "http://localhost:9000/containers/running"
```

### 3. Get Container Statistics

```bash
curl "http://localhost:9000/containers/abc123/stats"
```

Response:

```json
{
  "container_id": "abc123",
  "name": "my-api-server",
  "cpu_percent": 2.5,
  "memory_usage": "45.23 MB",
  "memory_limit": "512.00 MB",
  "memory_percent": 8.8,
  "network_rx": "1.25 MB",
  "network_tx": "0.75 MB",
  "timestamp": 1704067200.0
}
```

### 4. Stop a Container

```bash
curl -X POST "http://localhost:9000/containers/abc123/stop"
```

### 5. Check Port Usage

```bash
curl "http://localhost:8000/ports"
```

## Port Management

The system automatically manages ports in the range 8000-9000:

- **8000**: Orchestration API
- **8001-8999**: Dynamically allocated to containers
- Ports are automatically released when containers are stopped/removed
- Port conflicts are automatically resolved

## Container Lifecycle

1. **Create**: Container is created with automatic port allocation
2. **Start**: Container starts and becomes accessible
3. **Monitor**: Real-time statistics available via API
4. **Stop**: Container stops and port is released
5. **Remove**: Container is completely removed

## Development

### Project Structure

```
nubrixai/
├── main.py                 # Main orchestration API
├── base_server.py          # Sample base API server
├── Dockerfile.base         # Base server Dockerfile
├── Dockerfile.orchestration # Orchestration API Dockerfile
├── docker-compose.yml      # Development environment
├── pyproject.toml          # Project dependencies
└── README.md              # This file
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black .

# Linting
flake8
```

### Adding New Features

1. **New Endpoints**: Add routes to `main.py`
2. **New Models**: Extend Pydantic models
3. **New Images**: Create additional Dockerfiles
4. **Monitoring**: Extend statistics collection

## Troubleshooting

### Common Issues

1. **Docker Connection Error**

   - Ensure Docker daemon is running
   - Check Docker socket permissions

2. **Port Already in Use**

   - The system automatically finds available ports
   - Check `/ports` endpoint for current usage

3. **Container Won't Start**
   - Verify base image exists: `docker images base-api-server:latest`
   - Check Docker logs: `docker logs <container_id>`

### Debug Mode

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python main.py

# Check Docker client status
curl "http://localhost:8000/health"
```

## Security Considerations

- The API exposes Docker socket access
- Consider implementing authentication for production use
- Limit port range to prevent port scanning
- Monitor container resource usage

## Performance

- Port allocation is O(n) where n is port range size
- Container statistics are real-time
- Memory usage scales with number of containers
- Consider connection pooling for high-traffic scenarios

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review Docker and FastAPI documentation
