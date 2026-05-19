"""
AI Security Analyst for Small Businesses
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import logs, chat, reports
from .config import settings

app = FastAPI(
    title="AI Security Analyst",
    description="AI-powered cybersecurity assistant for small businesses",
    version="1.0.0",
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(logs.router)
app.include_router(chat.router)
app.include_router(reports.router)


@app.get("/")
async def root():
    return {
        "name": "AI Security Analyst",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    # Check Ollama connectivity
    ollama_status = "unknown"
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                ollama_status = "connected"
                models = resp.json().get("models", [])
                ollama_status = f"connected ({len(models)} models)"
            else:
                ollama_status = "error"
    except Exception:
        ollama_status = "not_running"

    return {
        "status": "healthy",
        "ollama": ollama_status,
        "model": settings.OLLAMA_MODEL,
    }


@app.get("/api/samples")
async def list_samples():
    """List available sample log files."""
    return {
        "samples": [
            {
                "id": "auth",
                "name": "SSH Auth Log",
                "description": "Linux authentication log with brute-force attacks, failed/successful logins, and sudo commands",
                "format": "auth.log",
            },
            {
                "id": "syslog",
                "name": "System Log",
                "description": "Linux syslog with kernel messages, firewall blocks, and service events",
                "format": "syslog",
            },
            {
                "id": "access",
                "name": "Apache Access Log",
                "description": "Web server access log with SQL injection attempts, directory traversal, and 404 scanning",
                "format": "apache_access",
            },
            {
                "id": "nginx",
                "name": "Nginx Web Log",
                "description": "Nginx access log with XSS attacks, SQL injection, directory traversal, and web scanning",
                "format": "apache_access",
            },
            {
                "id": "ssh_heavy",
                "name": "Heavy Brute Force",
                "description": "Intense multi-source SSH brute force from 4 IPs with privilege escalation attempts",
                "format": "auth.log",
            },
            {
                "id": "mixed",
                "name": "Mixed Attack Log",
                "description": "Realistic combined scenario: SSH brute force + SQL injection + directory traversal + XSS + privilege escalation",
                "format": "mixed",
            },
        ]
    }
