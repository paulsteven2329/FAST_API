"""
Service B - Backend Microservice
Port: 8002
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import random

app = FastAPI(title="Service B", version="1.0.0")

# In-memory data store
data_store = {
    "service_name": "Service B",
    "service_id": "service-b-002",
    "port": 8002
}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Service B",
        "status": "running",
        "port": 8002,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Service B",
        "port": 8002,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/data")
async def get_data(request: Request):
    """Get data endpoint"""
    return {
        "service": "Service B",
        "port": 8002,
        "data": {
            "message": "Hello from Service B",
            "random_value": random.randint(100, 200),
            "items": ["dog", "cat", "bird"],
            "count": 3
        },
        "client_ip": request.client.host,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/data")
async def post_data(request: Request):
    """Post data endpoint"""
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}

    return {
        "service": "Service B",
        "port": 8002,
        "message": "Data processed successfully",
        "received_data": body,
        "processed_by": "Service B",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/info")
async def service_info():
    """Service information endpoint"""
    return {
        "service_name": data_store["service_name"],
        "service_id": data_store["service_id"],
        "port": data_store["port"],
        "version": "1.0.0",
        "capabilities": ["data-retrieval", "data-processing"],
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🚀 Starting Service B on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")