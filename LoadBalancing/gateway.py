"""
API Gateway with Load Balancing and Rate Limiting
Port: 8000

Features:
- Round-robin load balancing
- IP-based rate limiting (5 requests per minute)
- Service health checks
- Request forwarding to backend services
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import uvicorn
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
from collections import defaultdict
import time

app = FastAPI(
    title="API Gateway",
    version="1.0.0",
    description="API Gateway with Load Balancing and Rate Limiting"
)

# Backend service configuration
BACKEND_SERVICES = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003",
]


# Load balancer state
class LoadBalancer:
    def __init__(self, services: List[str]):
        self.services = services
        self.current_index = 0
        self.healthy_services = services.copy()

    def get_next_service(self) -> str:
        """Round-robin load balancing"""
        if not self.healthy_services:
            raise HTTPException(status_code=503, detail="No healthy backend services available")

        service = self.healthy_services[self.current_index % len(self.healthy_services)]
        self.current_index += 1
        return service

    def mark_unhealthy(self, service: str):
        """Mark a service as unhealthy"""
        if service in self.healthy_services:
            self.healthy_services.remove(service)

    def mark_healthy(self, service: str):
        """Mark a service as healthy"""
        if service not in self.healthy_services and service in self.services:
            self.healthy_services.append(service)

    def get_service_status(self) -> Dict:
        """Get status of all services"""
        return {
            "total_services": len(self.services),
            "healthy_services": len(self.healthy_services),
            "services": [
                {
                    "url": service,
                    "status": "healthy" if service in self.healthy_services else "unhealthy"
                }
                for service in self.services
            ]
        }


# Initialize load balancer
load_balancer = LoadBalancer(BACKEND_SERVICES)


# Rate limiter state (in-memory)
class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limit"""
        current_time = time.time()

        # Clean up old requests outside the time window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]

        # Check if under limit
        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        # Add current request
        self.requests[client_ip].append(current_time)
        return True

    def get_remaining_requests(self, client_ip: str) -> int:
        """Get remaining requests for client"""
        current_time = time.time()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        return max(0, self.max_requests - len(self.requests[client_ip]))

    def get_reset_time(self, client_ip: str) -> float:
        """Get time until rate limit resets"""
        if not self.requests[client_ip]:
            return 0

        oldest_request = min(self.requests[client_ip])
        reset_time = oldest_request + self.window_seconds
        return max(0, reset_time - time.time())


# Initialize rate limiter (5 requests per minute)
rate_limiter = RateLimiter(max_requests=5, window_seconds=60)


# Middleware for rate limiting
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host

    # Skip rate limiting for health and info endpoints
    if request.url.path in ["/", "/health", "/services"]:
        return await call_next(request)

    if not rate_limiter.is_allowed(client_ip):
        remaining = rate_limiter.get_remaining_requests(client_ip)
        reset_time = rate_limiter.get_reset_time(client_ip)

        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Maximum {rate_limiter.max_requests} requests per {rate_limiter.window_seconds} seconds.",
                "client_ip": client_ip,
                "retry_after": int(reset_time),
                "limit": rate_limiter.max_requests,
                "remaining": remaining,
                "timestamp": datetime.now().isoformat()
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time() + reset_time)),
                "Retry-After": str(int(reset_time))
            }
        )

    response = await call_next(request)

    # Add rate limit headers to response
    remaining = rate_limiter.get_remaining_requests(client_ip)
    reset_time = rate_limiter.get_reset_time(client_ip)

    response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + reset_time))

    return response


# Background task for health checks
async def health_check_task():
    """Periodically check health of backend services"""
    while True:
        async with httpx.AsyncClient(timeout=5.0) as client:
            for service in BACKEND_SERVICES:
                try:
                    response = await client.get(f"{service}/health")
                    if response.status_code == 200:
                        load_balancer.mark_healthy(service)
                    else:
                        load_balancer.mark_unhealthy(service)
                except Exception:
                    load_balancer.mark_unhealthy(service)

        await asyncio.sleep(10)  # Check every 10 seconds


@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    asyncio.create_task(health_check_task())


@app.get("/")
async def root():
    """Gateway root endpoint"""
    return {
        "service": "API Gateway",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Load Balancing (Round Robin)",
            "Rate Limiting (5 req/min per IP)",
            "Health Checks",
            "Request Forwarding"
        ],
        "backend_services": len(BACKEND_SERVICES),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    """Gateway health check"""
    return {
        "status": "healthy",
        "service": "API Gateway",
        "backend_services": load_balancer.get_service_status(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/services")
async def list_services():
    """List all backend services and their status"""
    return {
        "gateway": "API Gateway",
        "load_balancing": "Round Robin",
        "rate_limiting": f"{rate_limiter.max_requests} requests per {rate_limiter.window_seconds} seconds",
        "backend_services": load_balancer.get_service_status(),
        "timestamp": datetime.now().isoformat()
    }


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request):
    """
    Proxy requests to backend services with load balancing
    """
    # Get next service using load balancer
    service_url = load_balancer.get_next_service()
    target_url = f"{service_url}/{path}"

    # Prepare request
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header

    # Get request body
    body = await request.body()

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Forward request to backend service
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )

            # Return response from backend service
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers={
                    "X-Gateway": "API Gateway",
                    "X-Backend-Service": service_url,
                    "X-Load-Balancer": "Round Robin"
                }
            )

        except httpx.RequestError as e:
            # Mark service as unhealthy and retry
            load_balancer.mark_unhealthy(service_url)

            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Service unavailable",
                    "message": f"Failed to connect to backend service: {service_url}",
                    "details": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Internal server error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )


@app.get("/stats")
async def get_stats(request: Request):
    """Get gateway statistics"""
    client_ip = request.client.host

    return {
        "gateway": "API Gateway",
        "rate_limiting": {
            "max_requests": rate_limiter.max_requests,
            "window_seconds": rate_limiter.window_seconds,
            "your_ip": client_ip,
            "remaining_requests": rate_limiter.get_remaining_requests(client_ip),
            "reset_in_seconds": int(rate_limiter.get_reset_time(client_ip))
        },
        "load_balancing": {
            "algorithm": "Round Robin",
            "current_index": load_balancer.current_index,
            "services": load_balancer.get_service_status()
        },
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🚀 Starting API Gateway on port 8000...")
    print("📊 Features: Load Balancing (Round Robin) + Rate Limiting (5 req/min)")
    print("🔧 Backend Services:", BACKEND_SERVICES)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")