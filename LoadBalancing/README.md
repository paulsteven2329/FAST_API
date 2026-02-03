# FastAPI API Gateway with Load Balancing & Rate Limiting

A microservices architecture demonstration featuring an API Gateway, multiple backend services, load balancing, and rate limiting.

## 🏗️ Architecture

```
Client Request
     ↓
API Gateway (Port 8000)
     ├── Rate Limiter (5 req/min per IP)
     └── Load Balancer (Round Robin)
          ├── Service A (Port 8001)
          ├── Service B (Port 8002)
          └── Service C (Port 8003)
```

## 📋 Features

- **API Gateway**: Single entry point for all client requests
- **Load Balancing**: Round-robin distribution across backend services
- **Rate Limiting**: IP-based request limiting (5 requests/minute)
- **Health Checks**: Monitor backend service availability
- **Service Discovery**: Dynamic service registration

## 🚀 Quick Start

### Prerequisites

```bash
pip install fastapi uvicorn httpx redis slowapi
```

### Running the Services

1. **Start Backend Services** (in separate terminals):
```bash
python service_a.py
python service_b.py
python service_c.py
```

2. **Start API Gateway**:
```bash
python gateway.py
```

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Get data (load balanced)
curl http://localhost:8000/api/data

# Test rate limiting (run multiple times)
for i in {1..10}; do curl http://localhost:8000/api/data; echo ""; done
```

## 📁 Project Structure

```
api-gateway-project/
├── gateway.py           # API Gateway with load balancing & rate limiting
├── service_a.py         # Backend Service A
├── service_b.py         # Backend Service B
├── service_c.py         # Backend Service C
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

- **Gateway Port**: 8000
- **Service A Port**: 8001
- **Service B Port**: 8002
- **Service C Port**: 8003
- **Rate Limit**: 5 requests per minute per IP
- **Load Balancing**: Round Robin algorithm

## 🎯 API Endpoints

### Gateway Endpoints

- `GET /` - Welcome message
- `GET /health` - Gateway health status
- `GET /api/data` - Proxied to backend services (load balanced)
- `POST /api/data` - Proxied to backend services (load balanced)
- `GET /services` - List registered backend services

### Backend Service Endpoints

- `GET /health` - Service health check
- `GET /data` - Returns service-specific data
- `POST /data` - Accepts and processes data