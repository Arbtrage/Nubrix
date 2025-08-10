#!/usr/bin/env python3
"""
Docker Orchestration API - Main Entry Point
This file serves as the entry point for the modularized application.
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
