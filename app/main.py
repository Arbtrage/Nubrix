from fastapi import FastAPI
from app.api import base, containers, monitoring

# Create FastAPI app
app = FastAPI(
    title="Docker Orchestration API",
    description="A comprehensive API for managing Docker containers with automatic port allocation and monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(base.router)
app.include_router(containers.router)
app.include_router(monitoring.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
