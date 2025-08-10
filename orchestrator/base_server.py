from fastapi import FastAPI
import time

app = FastAPI(title="Base API Server", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Base API Server is running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time(), "server": "base-api-server"}


@app.get("/info")
async def info():
    return {
        "name": "Base API Server",
        "version": "1.0.0",
        "port": 5000,
        "endpoints": ["/", "/health", "/info"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
