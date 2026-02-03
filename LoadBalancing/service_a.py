"""
Service A - Backend Microservice
Port: 8001
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import random

app = FastAPI(title="Service A", version="1.0.0")

# In-memory data store
data_store = {
    "service_name": "Service A",
    "service_id": "service-a-001",
    "port": 8001
}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Service A",
        "status": "running",
        "port": 8001,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Service A",
        "port": 8001,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/data")
async def get_data(request: Request):
    """Get data endpoint"""
    return {
        "service": "Service A",
        "port": 8001,
        "data": {
            "message": "Hello from Service A",
            "random_value": random.randint(1, 100),
            "items": ["apple", "banana", "cherry"],
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
        "service": "Service A",
        "port": 8001,
        "message": "Data received successfully",
        "received_data": body,
        "processed_by": "Service A",
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
    print("🚀 Starting Service A on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")