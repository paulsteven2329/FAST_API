"""
Service C - Backend Microservice
Port: 8003
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import random

app = FastAPI(title="Service C", version="1.0.0")

# In-memory data store
data_store = {
    "service_name": "Service C",
    "service_id": "service-c-003",
    "port": 8003
}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Service C",
        "status": "running",
        "port": 8003,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Service C",
        "port": 8003,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/data")
async def get_data(request: Request):
    """Get data endpoint"""
    return {
        "service": "Service C",
        "port": 8003,
        "data": {
            "message": "Hello from Service C",
            "random_value": random.randint(200, 300),
            "items": ["red", "green", "blue"],
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
        "service": "Service C",
        "port": 8003,
        "message": "Data handled successfully",
        "received_data": body,
        "processed_by": "Service C",
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
    print("🚀 Starting Service C on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")